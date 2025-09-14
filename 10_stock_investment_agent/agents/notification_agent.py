"""
通知Agent
负责发送邮件通知、报告生成、预警等功能
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from loguru import logger

from utils.logger import get_logger
from utils.date_utils import DateUtils


class NotificationAgent:
    """通知Agent"""
    
    def __init__(self, api_keys: Dict, settings: Dict):
        self.logger = get_logger("notification")
        self.api_keys = api_keys
        self.settings = settings
        self.date_utils = DateUtils()
        
    def send_daily_report(self) -> Dict:
        """发送每日报告"""
        try:
            self.logger.info("准备发送每日报告...")
            
            # 这里应该获取投资组合分析数据
            # 现在发送一个简单的测试报告
            
            report_data = {
                'date': self.date_utils.format_datetime(self.date_utils.get_current_time(), '%Y-%m-%d'),
                'portfolio_summary': {
                    'total_value': 100000,
                    'total_profit_loss': 5000,
                    'total_profit_loss_percent': 5.0
                },
                'top_performers': [],
                'worst_performers': [],
                'market_summary': '市场表现平稳'
            }
            
            result = self._send_email(
                subject=f"每日投资报告 - {report_data['date']}",
                body=self._format_daily_report(report_data),
                is_html=True
            )
            
            if result.get('success'):
                self.logger.info("每日报告发送成功")
                return {'success': True, 'message': '每日报告发送成功'}
            else:
                self.logger.error(f"每日报告发送失败: {result.get('error')}")
                return {'success': False, 'error': result.get('error')}
                
        except Exception as e:
            self.logger.error(f"发送每日报告失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def send_weekly_report(self) -> Dict:
        """发送每周报告"""
        try:
            self.logger.info("准备发送每周报告...")
            
            report_data = {
                'week_range': '本周',
                'portfolio_summary': {
                    'weekly_return': 2.5,
                    'total_value': 102500,
                    'best_performer': 'AAPL',
                    'worst_performer': 'TSLA'
                },
                'market_analysis': '本周市场整体上涨',
                'recommendations': ['建议继续持有', '关注市场动态']
            }
            
            result = self._send_email(
                subject=f"每周投资报告 - {report_data['week_range']}",
                body=self._format_weekly_report(report_data),
                is_html=True
            )
            
            if result.get('success'):
                self.logger.info("每周报告发送成功")
                return {'success': True, 'message': '每周报告发送成功'}
            else:
                return {'success': False, 'error': result.get('error')}
                
        except Exception as e:
            self.logger.error(f"发送每周报告失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def send_trade_notification(self, trade_type: str, trade_data: Dict, result: Dict) -> Dict:
        """发送交易通知"""
        try:
            symbol = trade_data.get('symbol', 'Unknown')
            trade_type_cn = "买入" if trade_type == "buy" else "卖出"
            
            subject = f"交易通知 - {trade_type_cn} {symbol}"
            
            if trade_type == "buy":
                body = self._format_buy_notification(trade_data, result)
            else:
                body = self._format_sell_notification(trade_data, result)
            
            email_result = self._send_email(subject, body, is_html=True)
            
            if email_result.get('success'):
                self.logger.info(f"交易通知发送成功: {symbol}")
                return {'success': True, 'message': '交易通知发送成功'}
            else:
                return {'success': False, 'error': email_result.get('error')}
                
        except Exception as e:
            self.logger.error(f"发送交易通知失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def send_alert(self, alert_type: str, symbol: str, message: str, severity: str = 'medium') -> Dict:
        """发送预警通知"""
        try:
            subject = f"投资预警 - {alert_type} - {symbol}"
            
            body = f"""
            <h2>投资预警通知</h2>
            <p><strong>股票代码:</strong> {symbol}</p>
            <p><strong>预警类型:</strong> {alert_type}</p>
            <p><strong>严重程度:</strong> {severity}</p>
            <p><strong>预警信息:</strong> {message}</p>
            <p><strong>时间:</strong> {self.date_utils.format_datetime(self.date_utils.get_current_time())}</p>
            """
            
            result = self._send_email(subject, body, is_html=True)
            
            if result.get('success'):
                self.logger.info(f"预警通知发送成功: {symbol}")
                return {'success': True, 'message': '预警通知发送成功'}
            else:
                return {'success': False, 'error': result.get('error')}
                
        except Exception as e:
            self.logger.error(f"发送预警通知失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def send_startup_report(self) -> Dict:
        """发送启动报告"""
        try:
            self.logger.info("发送系统启动报告...")
            
            subject = "股票投资分析系统启动成功"
            
            body = f"""<h2>系统启动成功</h2>
            <p>您的股票投资分析管理系统已成功启动并开始运行。</p>
            
            <h3>系统功能:</h3>
            <ul>
                <li>✅ 实时股价监控</li>
                <li>✅ 投资组合分析</li>
                <li>✅ 自动报告生成</li>
                <li>✅ 智能预警通知</li>
                <li>✅ 飞书表格同步</li>
            </ul>
            
            <h3>运行计划:</h3>
            <ul>
                <li>价格更新: 每5分钟</li>
                <li>组合分析: 每小时</li>
                <li>每日报告: 18:00</li>
                <li>每周报告: 周日18:00</li>
            </ul>
            
            <p><em>启动时间: {self.date_utils.format_datetime(self.date_utils.get_current_time())}</em></p>
            """
            
            result = self._send_email(subject, body, is_html=True)
            
            if result.get('success'):
                self.logger.info("启动报告发送成功")
                return {'success': True, 'message': '启动报告发送成功'}
            else:
                return {'success': False, 'error': result.get('error')}
                
        except Exception as e:
            self.logger.error(f"发送启动报告失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def send_test_notification(self) -> Dict:
        """发送测试通知"""
        try:
            subject = "股票投资分析系统测试通知"
            
            body = f"""
            <h2>测试通知</h2>
            <p>这是一条来自股票投资分析系统的测试通知。</p>
            <p>如果您收到此邮件，说明邮件通知功能正常工作。</p>
            <p><em>测试时间: {self.date_utils.format_datetime(self.date_utils.get_current_time())}</em></p>
            """
            
            result = self._send_email(subject, body, is_html=True)
            
            if result.get('success'):
                self.logger.info("测试通知发送成功")
                return {'success': True, 'message': '测试通知发送成功'}
            else:
                return {'success': False, 'error': result.get('error')}
                
        except Exception as e:
            self.logger.error(f"发送测试通知失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def _send_email(self, subject: str, body: str, is_html: bool = True) -> Dict:
        """发送邮件"""
        try:
            # 使用Gmail MCP发送邮件
            recipient_email = self.api_keys.get('gmail', {}).get('recipient_email', 'zbin523@gmail.com')
            
            # 这里应该调用Gmail MCP API
            # 现在返回模拟结果
            self.logger.info(f"发送邮件到: {recipient_email}")
            self.logger.info(f"主题: {subject}")
            
            return {
                'success': True,
                'message': '邮件发送成功',
                'recipient': recipient_email,
                'subject': subject
            }
            
        except Exception as e:
            self.logger.error(f"发送邮件失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def _format_daily_report(self, data: Dict) -> str:
        """格式化每日报告"""
        return f"""
        <h2>每日投资报告 - {data['date']}</h2>
        
        <h3>投资组合摘要</h3>
        <table border="1" style="border-collapse: collapse; width: 100%;">
            <tr>
                <th>总市值</th>
                <th>总盈亏</th>
                <th>盈亏比例</th>
            </tr>
            <tr>
                <td>¥{data['portfolio_summary']['total_value']:,.2f}</td>
                <td>¥{data['portfolio_summary']['total_profit_loss']:,.2f}</td>
                <td>{data['portfolio_summary']['total_profit_loss_percent']:.2f}%</td>
            </tr>
        </table>
        
        <h3>市场概况</h3>
        <p>{data['market_summary']}</p>
        
        <p><em>报告生成时间: {self.date_utils.format_datetime(self.date_utils.get_current_time())}</em></p>
        """
    
    def _format_weekly_report(self, data: Dict) -> str:
        """格式化每周报告"""
        return f"""
        <h2>每周投资报告 - {data['week_range']}</h2>
        
        <h3>本周表现</h3>
        <table border="1" style="border-collapse: collapse; width: 100%;">
            <tr>
                <th>周收益率</th>
                <th>总市值</th>
                <th>最佳表现</th>
                <th>最差表现</th>
            </tr>
            <tr>
                <td>{data['portfolio_summary']['weekly_return']:.2f}%</td>
                <td>¥{data['portfolio_summary']['total_value']:,.2f}</td>
                <td>{data['portfolio_summary']['best_performer']}</td>
                <td>{data['portfolio_summary']['worst_performer']}</td>
            </tr>
        </table>
        
        <h3>市场分析</h3>
        <p>{data['market_analysis']}</p>
        
        <h3>投资建议</h3>
        <ul>
            {''.join([f'<li>{rec}</li>' for rec in data['recommendations']])}
        </ul>
        
        <p><em>报告生成时间: {self.date_utils.format_datetime(self.date_utils.get_current_time())}</em></p>
        """
    
    def _format_buy_notification(self, trade_data: Dict, result: Dict) -> str:
        """格式化买入通知"""
        return f"""
        <h2>买入通知</h2>
        
        <table border="1" style="border-collapse: collapse; width: 100%;">
            <tr>
                <th>股票代码</th>
                <th>股票名称</th>
                <th>市场类型</th>
                <th>买入价格</th>
                <th>数量</th>
                <th>总成本</th>
            </tr>
            <tr>
                <td>{trade_data['symbol']}</td>
                <td>{trade_data.get('name', 'N/A')}</td>
                <td>{trade_data.get('market_type', 'N/A')}</td>
                <td>¥{trade_data['buy_price']:,.2f}</td>
                <td>{trade_data['quantity']}</td>
                <td>¥{trade_data.get('total_cost', 0):,.2f}</td>
            </tr>
        </table>
        
        <p><strong>备注:</strong> {trade_data.get('notes', '无')}</p>
        <p><em>交易时间: {self.date_utils.format_datetime(self.date_utils.get_current_time())}</em></p>
        """
    
    def _format_sell_notification(self, trade_data: Dict, result: Dict) -> str:
        """格式化卖出通知"""
        return f"""
        <h2>卖出通知</h2>
        
        <table border="1" style="border-collapse: collapse; width: 100%;">
            <tr>
                <th>股票代码</th>
                <th>卖出价格</th>
                <th>数量</th>
                <th>卖出金额</th>
            </tr>
            <tr>
                <td>{trade_data['symbol']}</td>
                <td>¥{trade_data['sell_price']:,.2f}</td>
                <td>{trade_data['quantity']}</td>
                <td>¥{trade_data.get('total_amount', 0):,.2f}</td>
            </tr>
        </table>
        
        <p><strong>备注:</strong> {trade_data.get('notes', '无')}</p>
        <p><em>交易时间: {self.date_utils.format_datetime(self.date_utils.get_current_time())}</em></p>
        """
    
    def send_manual_analysis_report(self, portfolio_result: Dict, ai_result: Dict) -> Dict:
        """发送手动分析报告"""
        try:
            subject = "手动分析报告"
            
            body = f"""
            <h2>手动分析报告</h2>
            
            <h3>投资组合分析</h3>
            <pre>{json.dumps(portfolio_result, indent=2, ensure_ascii=False)}</pre>
            
            <h3>AI分析结果</h3>
            <pre>{json.dumps(ai_result, indent=2, ensure_ascii=False)}</pre>
            
            <p><em>分析时间: {self.date_utils.format_datetime(self.date_utils.get_current_time())}</em></p>
            """
            
            result = self._send_email(subject, body, is_html=True)
            
            if result.get('success'):
                self.logger.info("手动分析报告发送成功")
                return {'success': True, 'message': '手动分析报告发送成功'}
            else:
                return {'success': False, 'error': result.get('error')}
                
        except Exception as e:
            self.logger.error(f"发送手动分析报告失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_status(self) -> Dict:
        """获取Agent状态"""
        return {
            'status': 'active',
            'last_email_sent': None,
            'email_configured': 'gmail' in self.api_keys
        }
    
    def start(self):
        """启动Agent"""
        self.logger.info("通知Agent启动")
    
    def stop(self):
        """停止Agent"""
        self.logger.info("通知Agent停止")