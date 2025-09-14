"""
主Agent控制器
统筹管理所有子Agent，提供统一的接口和协调机制
"""

import json
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

from utils.logger import get_logger
from utils.date_utils import DateUtils
from utils.auto_scheduler import scheduler
from agents.data_fetching_agent import DataFetchingAgent
from agents.portfolio_analyzer import PortfolioAnalyzer
from agents.feishu_integration import FeishuIntegrationAgent
from agents.feishu_bitable_agent import FeishuBitableAgent
from agents.notification_agent import NotificationAgent
from agents.ai_analysis_agent import AIAnalysisAgent


class MainAgent:
    """主Agent控制器"""
    
    def __init__(self, config_dir: str = "config"):
        self.logger = get_logger("main_agent")
        self.date_utils = DateUtils()
        self.config_dir = Path(config_dir)
        
        # 加载配置
        self.settings = self._load_config("settings.json")
        self.api_keys = self._load_config("api_keys.json")
        self.stock_symbols = self._load_config("stock_symbols.json")
        
        # 初始化子Agent
        self.agents = {}
        self._initialize_agents()
        
        # 运行状态
        self.running = False
        self.start_time = None
        
    def _load_config(self, filename: str) -> Dict:
        """加载配置文件"""
        try:
            config_path = self.config_dir / filename
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"加载配置文件失败 {filename}: {e}")
            return {}
    
    def _initialize_agents(self):
        """初始化所有子Agent"""
        try:
            self.logger.info("开始初始化子Agent...")
            
            # 数据抓取Agent
            self.agents['data_fetching'] = DataFetchingAgent(
                api_keys=self.api_keys,
                stock_symbols=self.stock_symbols
            )
            
            # 投资组合分析Agent
            self.agents['portfolio_analyzer'] = PortfolioAnalyzer(
                settings=self.settings,
                data_fetching_agent=self.agents['data_fetching']
            )
            
            # 飞书集成Agent
            self.agents['feishu_integration'] = FeishuIntegrationAgent(
                api_keys=self.api_keys,
                settings=self.settings
            )
            
            # 飞书多维表格Agent
            self.agents['feishu_bitable'] = FeishuBitableAgent(
                api_keys=self.api_keys,
                settings=self.settings
            )
            
            # 通知Agent
            self.agents['notification'] = NotificationAgent(
                api_keys=self.api_keys,
                settings=self.settings
            )
            
            # AI分析Agent
            self.agents['ai_analyzer'] = AIAnalysisAgent(
                api_keys=self.api_keys,
                settings=self.settings
            )
            
            self.logger.info("所有子Agent初始化完成")
            
        except Exception as e:
            self.logger.error(f"初始化子Agent失败: {e}")
            raise
    
    def start(self):
        """启动系统"""
        try:
            if self.running:
                self.logger.warning("系统已经在运行中")
                return
            
            self.logger.info("正在启动股票投资分析系统...")
            self.start_time = self.date_utils.get_current_time()
            
            # 启动子Agent
            for agent_name, agent in self.agents.items():
                if hasattr(agent, 'start'):
                    agent.start()
            
            # 设置定时任务
            scheduler.setup_default_tasks(self.agents)
            
            # 启动调度器
            scheduler.start()
            
            self.running = True
            self.logger.info("股票投资分析系统启动成功")
            
            # 启动后立即执行一次数据更新
            self.run_initial_update()
            
        except Exception as e:
            self.logger.error(f"启动系统失败: {e}")
            raise
    
    def stop(self):
        """停止系统"""
        try:
            if not self.running:
                self.logger.warning("系统未在运行")
                return
            
            self.logger.info("正在停止股票投资分析系统...")
            
            # 停止调度器
            scheduler.stop()
            
            # 停止子Agent
            for agent_name, agent in self.agents.items():
                if hasattr(agent, 'stop'):
                    agent.stop()
            
            self.running = False
            self.logger.info("股票投资分析系统停止成功")
            
        except Exception as e:
            self.logger.error(f"停止系统失败: {e}")
    
    def run_initial_update(self):
        """启动后立即执行初始更新"""
        try:
            self.logger.info("执行启动后初始更新...")
            
            # 更新所有价格数据
            self.agents['data_fetching'].update_all_prices()
            
            # 分析投资组合
            self.agents['portfolio_analyzer'].analyze_portfolio()
            
            # 同步数据到飞书
            self.agents['feishu_integration'].sync_data()
            
            # 发送启动报告
            self.agents['notification'].send_startup_report()
            
            self.logger.info("初始更新完成")
            
        except Exception as e:
            self.logger.error(f"初始更新失败: {e}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        try:
            status = {
                'system_running': self.running,
                'start_time': self.start_time.isoformat() if self.start_time else None,
                'current_time': self.date_utils.get_current_time().isoformat(),
                'uptime': self._get_uptime(),
                'agents_status': {},
                'scheduler_status': scheduler.get_task_status(),
                'system_info': {
                    'name': self.settings.get('system', {}).get('name', '股票投资分析管理系统'),
                    'version': self.settings.get('system', {}).get('version', '1.0.0'),
                    'timezone': self.settings.get('system', {}).get('timezone', 'Asia/Shanghai')
                }
            }
            
            # 获取各Agent状态
            for agent_name, agent in self.agents.items():
                if hasattr(agent, 'get_status'):
                    status['agents_status'][agent_name] = agent.get_status()
                else:
                    status['agents_status'][agent_name] = {'status': 'active'}
            
            return status
            
        except Exception as e:
            self.logger.error(f"获取系统状态失败: {e}")
            return {}
    
    def _get_uptime(self) -> str:
        """获取系统运行时间"""
        if not self.start_time:
            return "N/A"
        
        uptime = self.date_utils.get_current_time() - self.start_time
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        
        if days > 0:
            return f"{days}天 {hours}小时 {minutes}分钟"
        elif hours > 0:
            return f"{hours}小时 {minutes}分钟"
        else:
            return f"{minutes}分钟"
    
    def add_buy_record(self, stock_data: Dict) -> Dict:
        """添加买入记录"""
        try:
            self.logger.info(f"添加买入记录: {stock_data.get('symbol', 'Unknown')}")
            
            # 验证数据
            required_fields = ['symbol', 'name', 'market_type', 'buy_price', 'quantity']
            for field in required_fields:
                if field not in stock_data:
                    raise ValueError(f"缺少必需字段: {field}")
            
            # 调用投资组合分析Agent添加记录
            result = self.agents['portfolio_analyzer'].add_buy_record(stock_data)
            
            # 同步到飞书
            self.agents['feishu_integration'].sync_buy_record(stock_data)
            
            # 发送通知
            self.agents['notification'].send_trade_notification('buy', stock_data, result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"添加买入记录失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def add_sell_record(self, stock_data: Dict) -> Dict:
        """添加卖出记录"""
        try:
            self.logger.info(f"添加卖出记录: {stock_data.get('symbol', 'Unknown')}")
            
            # 验证数据
            required_fields = ['symbol', 'sell_price', 'quantity']
            for field in required_fields:
                if field not in stock_data:
                    raise ValueError(f"缺少必需字段: {field}")
            
            # 调用投资组合分析Agent添加记录
            result = self.agents['portfolio_analyzer'].add_sell_record(stock_data)
            
            # 同步到飞书
            self.agents['feishu_integration'].sync_sell_record(stock_data)
            
            # 发送通知
            self.agents['notification'].send_trade_notification('sell', stock_data, result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"添加卖出记录失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_portfolio_summary(self) -> Dict:
        """获取投资组合摘要"""
        try:
            return self.agents['portfolio_analyzer'].get_portfolio_summary()
        except Exception as e:
            self.logger.error(f"获取投资组合摘要失败: {e}")
            return {}
    
    def get_stock_analysis(self, symbol: str, market_type: str) -> Dict:
        """获取个股分析"""
        try:
            return self.agents['ai_analyzer'].analyze_stock(symbol, market_type)
        except Exception as e:
            self.logger.error(f"获取个股分析失败: {e}")
            return {}
    
    def run_manual_analysis(self) -> Dict:
        """手动运行分析"""
        try:
            self.logger.info("开始手动运行分析...")
            
            # 更新价格
            self.agents['data_fetching'].update_all_prices()
            
            # 分析投资组合
            portfolio_result = self.agents['portfolio_analyzer'].analyze_portfolio()
            
            # AI分析
            ai_result = self.agents['ai_analyzer'].run_analysis()
            
            # 同步数据
            self.agents['feishu_integration'].sync_data()
            
            # 发送报告
            self.agents['notification'].send_manual_analysis_report(portfolio_result, ai_result)
            
            return {
                'success': True,
                'portfolio_analysis': portfolio_result,
                'ai_analysis': ai_result,
                'timestamp': self.date_utils.get_current_time().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"手动运行分析失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def send_test_notification(self) -> Dict:
        """发送测试通知"""
        try:
            return self.agents['notification'].send_test_notification()
        except Exception as e:
            self.logger.error(f"发送测试通知失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def reload_config(self):
        """重新加载配置"""
        try:
            self.logger.info("重新加载配置...")
            
            self.settings = self._load_config("settings.json")
            self.api_keys = self._load_config("api_keys.json")
            self.stock_symbols = self._load_config("stock_symbols.json")
            
            # 重新初始化Agent
            for agent_name, agent in self.agents.items():
                if hasattr(agent, 'reload_config'):
                    agent.reload_config(self.settings, self.api_keys, self.stock_symbols)
            
            self.logger.info("配置重新加载完成")
            
        except Exception as e:
            self.logger.error(f"重新加载配置失败: {e}")


def main():
    """主函数 - 命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='股票投资分析管理系统')
    parser.add_argument('--config', default='config', help='配置文件目录')
    parser.add_argument('--action', choices=['start', 'stop', 'status', 'test'], 
                       default='start', help='执行动作')
    
    args = parser.parse_args()
    
    agent = MainAgent(config_dir=args.config)
    
    if args.action == 'start':
        agent.start()
        print("系统已启动，按 Ctrl+C 停止...")
        try:
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            agent.stop()
            print("系统已停止")
    
    elif args.action == 'status':
        status = agent.get_system_status()
        print(json.dumps(status, indent=2, ensure_ascii=False))
    
    elif args.action == 'test':
        result = agent.send_test_notification()
        print(f"测试通知结果: {result}")
    
    elif args.action == 'stop':
        print("停止功能需要通过运行中的系统来执行")


if __name__ == "__main__":
    main()