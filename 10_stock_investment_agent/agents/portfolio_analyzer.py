"""
投资组合分析Agent
负责计算盈亏、分析持仓、风险评估等功能
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from loguru import logger

from utils.logger import get_logger
from utils.calculation_utils import CalculationUtils
from utils.date_utils import DateUtils


class PortfolioAnalyzer:
    """投资组合分析器"""
    
    def __init__(self, settings: Dict, data_fetching_agent):
        self.logger = get_logger("portfolio_analysis")
        self.settings = settings
        self.data_fetching_agent = data_fetching_agent
        self.calc_utils = CalculationUtils()
        self.date_utils = DateUtils()
        
    def add_buy_record(self, trade_data: Dict) -> Dict:
        """添加买入记录"""
        try:
            # 计算买入成本
            buy_price = trade_data['buy_price']
            quantity = trade_data['quantity']
            fees = trade_data.get('fees', 0)
            total_cost = buy_price * quantity + fees
            
            # 创建交易记录
            record = {
                'symbol': trade_data['symbol'],
                'name': trade_data['name'],
                'market_type': trade_data['market_type'],
                'trade_type': 'buy',
                'price': buy_price,
                'quantity': quantity,
                'total_cost': total_cost,
                'fees': fees,
                'timestamp': datetime.now().isoformat(),
                'notes': trade_data.get('notes', '')
            }
            
            # 保存到交易记录
            self._save_trade_record(record)
            
            # 更新持仓
            self._update_position(record)
            
            return {
                'success': True,
                'record_id': record.get('id'),
                'message': '买入记录添加成功'
            }
            
        except Exception as e:
            self.logger.error(f"添加买入记录失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def add_sell_record(self, trade_data: Dict) -> Dict:
        """添加卖出记录"""
        try:
            # 计算卖出金额
            sell_price = trade_data['sell_price']
            quantity = trade_data['quantity']
            fees = trade_data.get('fees', 0)
            total_amount = sell_price * quantity - fees
            
            # 创建交易记录
            record = {
                'symbol': trade_data['symbol'],
                'trade_type': 'sell',
                'price': sell_price,
                'quantity': quantity,
                'total_amount': total_amount,
                'fees': fees,
                'timestamp': datetime.now().isoformat(),
                'notes': trade_data.get('notes', '')
            }
            
            # 保存到交易记录
            self._save_trade_record(record)
            
            # 更新持仓
            self._update_position(record)
            
            return {
                'success': True,
                'record_id': record.get('id'),
                'message': '卖出记录添加成功'
            }
            
        except Exception as e:
            self.logger.error(f"添加卖出记录失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def analyze_portfolio(self) -> Dict:
        """分析投资组合"""
        try:
            # 加载持仓数据
            portfolio_data = self._load_portfolio_data()
            positions = portfolio_data.get('positions', [])
            
            if not positions:
                return {
                    'success': True,
                    'summary': self._get_empty_summary(),
                    'positions': [],
                    'analysis': {}
                }
            
            # 更新价格
            for position in positions:
                price_data = self.data_fetching_agent.get_stock_price(
                    position['symbol'], position['market_type']
                )
                
                if 'error' not in price_data:
                    position['current_price'] = price_data['price']
                    position['last_update'] = price_data['timestamp']
            
            # 计算每个持仓的盈亏
            for position in positions:
                if 'current_price' in position:
                    pnl = self.calc_utils.calculate_profit_loss(
                        position['avg_cost'],
                        position['current_price'],
                        position['quantity']
                    )
                    position.update(pnl)
            
            # 计算投资组合摘要
            summary = self.calc_utils.calculate_portfolio_summary(positions)
            
            # 计算资产配置
            allocation = self.calc_utils.calculate_asset_allocation(positions)
            
            # 计算风险指标
            risk_metrics = self.calc_utils.calculate_risk_metrics(positions, {})
            
            # 计算业绩指标
            performance = self.calc_utils.calculate_performance_metrics(positions)
            
            # 保存更新后的数据
            portfolio_data['last_update'] = datetime.now().isoformat()
            self._save_portfolio_data(portfolio_data)
            
            return {
                'success': True,
                'summary': summary,
                'positions': positions,
                'allocation': allocation,
                'risk_metrics': risk_metrics,
                'performance': performance,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"分析投资组合失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_portfolio_summary(self) -> Dict:
        """获取投资组合摘要"""
        try:
            analysis = self.analyze_portfolio()
            if analysis.get('success'):
                return {
                    'summary': analysis.get('summary', {}),
                    'total_value': analysis.get('summary', {}).get('total_value', 0),
                    'total_profit_loss': analysis.get('summary', {}).get('total_profit_loss', 0),
                    'positions_count': analysis.get('summary', {}).get('positions_count', 0),
                    'last_update': datetime.now().isoformat()
                }
            else:
                return self._get_empty_summary()
                
        except Exception as e:
            self.logger.error(f"获取投资组合摘要失败: {e}")
            return self._get_empty_summary()
    
    def _get_empty_summary(self) -> Dict:
        """获取空摘要"""
        return {
            'total_value': 0,
            'total_cost': 0,
            'total_profit_loss': 0,
            'total_profit_loss_percent': 0,
            'positions_count': 0
        }
    
    def _save_trade_record(self, record: Dict):
        """保存交易记录"""
        try:
            trade_records = self._load_trade_records()
            record['id'] = len(trade_records) + 1
            trade_records.append(record)
            
            with open('data/trade_records.json', 'w', encoding='utf-8') as f:
                json.dump(trade_records, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"保存交易记录失败: {e}")
    
    def _load_trade_records(self) -> List[Dict]:
        """加载交易记录"""
        try:
            with open('data/trade_records.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
        except Exception as e:
            self.logger.error(f"加载交易记录失败: {e}")
            return []
    
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
    
    def _save_portfolio_data(self, data: Dict):
        """保存投资组合数据"""
        try:
            with open('data/portfolio_data.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"保存投资组合数据失败: {e}")
    
    def _update_position(self, trade_record: Dict):
        """更新持仓"""
        try:
            portfolio_data = self._load_portfolio_data()
            positions = portfolio_data.get('positions', [])
            
            symbol = trade_record['symbol']
            market_type = trade_record.get('market_type', 'us_stocks')
            
            # 查找现有持仓
            position = None
            for pos in positions:
                if pos['symbol'] == symbol and pos['market_type'] == market_type:
                    position = pos
                    break
            
            if trade_record['trade_type'] == 'buy':
                # 买入操作
                if position is None:
                    # 新建持仓
                    position = {
                        'symbol': symbol,
                        'name': trade_record.get('name', symbol),
                        'market_type': market_type,
                        'quantity': trade_record['quantity'],
                        'avg_cost': trade_record['price'],
                        'total_cost': trade_record['total_cost'],
                        'buy_date': trade_record['timestamp'],
                        'currency': self._get_currency_by_market(market_type)
                    }
                    positions.append(position)
                else:
                    # 增加持仓
                    total_quantity = position['quantity'] + trade_record['quantity']
                    total_cost = position['total_cost'] + trade_record['total_cost']
                    position['quantity'] = total_quantity
                    position['avg_cost'] = total_cost / total_quantity
                    position['total_cost'] = total_cost
                    
            elif trade_record['trade_type'] == 'sell':
                # 卖出操作
                if position is not None:
                    position['quantity'] -= trade_record['quantity']
                    position['total_cost'] *= (position['quantity'] / (position['quantity'] + trade_record['quantity']))
                    
                    # 如果持仓为0，移除该持仓
                    if position['quantity'] <= 0:
                        positions.remove(position)
            
            portfolio_data['positions'] = positions
            portfolio_data['last_update'] = datetime.now().isoformat()
            self._save_portfolio_data(portfolio_data)
            
        except Exception as e:
            self.logger.error(f"更新持仓失败: {e}")
    
    def _get_currency_by_market(self, market_type: str) -> str:
        """根据市场类型获取货币"""
        currency_map = {
            'us_stocks': 'USD',
            'a_stocks': 'CNY',
            'hk_stocks': 'HKD',
            'funds': 'CNY'
        }
        return currency_map.get(market_type, 'USD')
    
    def get_status(self) -> Dict:
        """获取Agent状态"""
        return {
            'status': 'active',
            'last_analysis': None,
            'positions_count': len(self._load_portfolio_data().get('positions', []))
        }
    
    def start(self):
        """启动Agent"""
        self.logger.info("投资组合分析Agent启动")
    
    def stop(self):
        """停止Agent"""
        self.logger.info("投资组合分析Agent停止")