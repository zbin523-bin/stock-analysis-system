"""
飞书集成Agent
负责与飞书多维表格进行数据同步和操作
"""

import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from loguru import logger

from utils.logger import get_logger
from utils.date_utils import DateUtils


class FeishuIntegrationAgent:
    """飞书集成Agent"""
    
    def __init__(self, api_keys: Dict, settings: Dict):
        self.logger = get_logger("feishu_integration")
        self.api_keys = api_keys
        self.settings = settings
        self.date_utils = DateUtils()
        
        # 飞书API配置
        self.app_id = api_keys.get('feishu', {}).get('app_id')
        self.app_secret = api_keys.get('feishu', {}).get('app_secret')
        self.base_url = "https://open.feishu.cn/open-apis"
        
        # 访问令牌
        self.access_token = None
        self.token_expires = None
        
    def get_access_token(self) -> Optional[str]:
        """获取访问令牌"""
        try:
            # 检查令牌是否过期
            if self.access_token and self.token_expires:
                if datetime.now() < self.token_expires:
                    return self.access_token
            
            # 获取新的访问令牌
            url = f"{self.base_url}/auth/v3/tenant_access_token/internal"
            
            headers = {
                "Content-Type": "application/json; charset=utf-8"
            }
            
            data = {
                "app_id": self.app_id,
                "app_secret": self.app_secret
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                self.logger.info(f"飞书API响应: {result}")
                if result.get("code") == 0:
                    self.access_token = result.get("tenant_access_token")
                    expires_in = result.get("expire", 3600)
                    self.token_expires = datetime.now() + timedelta(seconds=expires_in - 300)
                    
                    self.logger.info("飞书访问令牌获取成功")
                    return self.access_token
                else:
                    self.logger.error(f"获取访问令牌失败: {result.get('msg', 'Unknown error')}")
                    self.logger.error(f"错误代码: {result.get('code')}")
                    return None
            else:
                self.logger.error(f"获取访问令牌失败: {response.status_code}")
                self.logger.error(f"响应内容: {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"获取访问令牌失败: {e}")
            return None
    
    def sync_data(self) -> Dict:
        """同步数据到飞书"""
        try:
            self.logger.info("开始同步数据到飞书...")
            
            # 获取访问令牌
            token = self.get_access_token()
            if not token:
                return {'success': False, 'error': '无法获取访问令牌'}
            
            # 加载投资组合数据
            portfolio_data = self._load_portfolio_data()
            
            # 同步到飞书表格
            result = self._sync_portfolio_to_feishu(portfolio_data, token)
            
            if result.get('success'):
                self.logger.info("数据同步到飞书成功")
                return {'success': True, 'message': '数据同步成功'}
            else:
                return {'success': False, 'error': result.get('error')}
                
        except Exception as e:
            self.logger.error(f"同步数据到飞书失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def sync_buy_record(self, trade_data: Dict) -> Dict:
        """同步买入记录到飞书"""
        try:
            self.logger.info(f"同步买入记录到飞书: {trade_data.get('symbol')}")
            
            # 这里应该调用飞书API添加记录
            # 现在返回模拟结果
            return {'success': True, 'message': '买入记录同步成功'}
            
        except Exception as e:
            self.logger.error(f"同步买入记录失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def sync_sell_record(self, trade_data: Dict) -> Dict:
        """同步卖出记录到飞书"""
        try:
            self.logger.info(f"同步卖出记录到飞书: {trade_data.get('symbol')}")
            
            # 这里应该调用飞书API添加记录
            # 现在返回模拟结果
            return {'success': True, 'message': '卖出记录同步成功'}
            
        except Exception as e:
            self.logger.error(f"同步卖出记录失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def _sync_portfolio_to_feishu(self, portfolio_data: Dict, token: str) -> Dict:
        """同步投资组合数据到飞书"""
        try:
            # 这里应该调用飞书多维表格API
            # 现在返回模拟结果
            
            positions = portfolio_data.get('positions', [])
            
            self.logger.info(f"同步 {len(positions)} 个持仓到飞书")
            
            # 模拟同步操作
            for position in positions:
                self.logger.info(f"同步持仓: {position.get('symbol')}")
            
            return {'success': True, 'synced_positions': len(positions)}
            
        except Exception as e:
            self.logger.error(f"同步投资组合到飞书失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def _load_portfolio_data(self) -> Dict:
        """加载投资组合数据"""
        try:
            with open('data/portfolio_data.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {'positions': [], 'last_update': None}
        except Exception as e:
            self.logger.error(f"加载投资组合数据失败: {e}")
            return {'positions': [], 'last_update': None}
    
    def create_feishu_table(self, table_name: str) -> Dict:
        """创建飞书表格"""
        try:
            self.logger.info(f"创建飞书表格: {table_name}")
            
            # 这里应该调用飞书API创建表格
            # 现在返回模拟结果
            return {
                'success': True,
                'table_id': 'mock_table_id',
                'table_name': table_name,
                'message': '表格创建成功'
            }
            
        except Exception as e:
            self.logger.error(f"创建飞书表格失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_feishu_tables(self) -> List[Dict]:
        """获取飞书表格列表"""
        try:
            self.logger.info("获取飞书表格列表")
            
            # 这里应该调用飞书API获取表格列表
            # 现在返回模拟结果
            return [
                {
                    'table_id': 'table1',
                    'name': '买入记录',
                    'created_time': datetime.now().isoformat()
                },
                {
                    'table_id': 'table2',
                    'name': '卖出记录',
                    'created_time': datetime.now().isoformat()
                },
                {
                    'table_id': 'table3',
                    'name': '持仓统计',
                    'created_time': datetime.now().isoformat()
                }
            ]
            
        except Exception as e:
            self.logger.error(f"获取飞书表格列表失败: {e}")
            return []
    
    def test_connection(self) -> Dict:
        """测试飞书连接"""
        try:
            token = self.get_access_token()
            if token:
                return {
                    'success': True,
                    'message': '飞书连接测试成功',
                    'token_valid': True
                }
            else:
                return {
                    'success': False,
                    'message': '无法获取访问令牌',
                    'token_valid': False
                }
                
        except Exception as e:
            self.logger.error(f"测试飞书连接失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_status(self) -> Dict:
        """获取Agent状态"""
        return {
            'status': 'active',
            'feishu_configured': bool(self.app_id and self.app_secret),
            'token_valid': bool(self.access_token),
            'last_sync': None
        }
    
    def start(self):
        """启动Agent"""
        self.logger.info("飞书集成Agent启动")
        
        # 测试连接
        test_result = self.test_connection()
        if test_result.get('success'):
            self.logger.info("飞书连接测试成功")
        else:
            self.logger.warning(f"飞书连接测试失败: {test_result.get('message')}")
    
    def stop(self):
        """停止Agent"""
        self.logger.info("飞书集成Agent停止")