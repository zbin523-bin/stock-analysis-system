"""
计算工具模块
提供投资组合计算、财务指标计算等功能
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from loguru import logger


class CalculationUtils:
    """投资组合计算工具类"""
    
    def __init__(self):
        self.logger = logger.bind(utils="calculation")
    
    def calculate_profit_loss(self, buy_price: float, current_price: float, 
                            quantity: int, fees: float = 0) -> Dict:
        """
        计算盈亏
        
        Args:
            buy_price: 买入价格
            current_price: 当前价格
            quantity: 数量
            fees: 手续费
            
        Returns:
            包含盈亏信息的字典
        """
        try:
            # 计算总成本
            total_cost = buy_price * quantity + fees
            
            # 计算当前市值
            current_value = current_price * quantity
            
            # 计算盈亏金额
            profit_loss = current_value - total_cost
            
            # 计算盈亏比例
            profit_loss_percent = (profit_loss / total_cost) * 100 if total_cost > 0 else 0
            
            return {
                'total_cost': round(total_cost, 2),
                'current_value': round(current_value, 2),
                'profit_loss': round(profit_loss, 2),
                'profit_loss_percent': round(profit_loss_percent, 2),
                'quantity': quantity,
                'buy_price': buy_price,
                'current_price': current_price
            }
            
        except Exception as e:
            self.logger.error(f"计算盈亏失败: {e}")
            return {}
    
    def calculate_portfolio_summary(self, positions: List[Dict]) -> Dict:
        """
        计算投资组合摘要
        
        Args:
            positions: 持仓列表
            
        Returns:
            投资组合摘要信息
        """
        try:
            if not positions:
                return {
                    'total_value': 0,
                    'total_cost': 0,
                    'total_profit_loss': 0,
                    'total_profit_loss_percent': 0,
                    'positions_count': 0
                }
            
            total_value = sum(pos.get('current_value', 0) for pos in positions)
            total_cost = sum(pos.get('total_cost', 0) for pos in positions)
            total_profit_loss = sum(pos.get('profit_loss', 0) for pos in positions)
            total_profit_loss_percent = (total_profit_loss / total_cost * 100) if total_cost > 0 else 0
            
            return {
                'total_value': round(total_value, 2),
                'total_cost': round(total_cost, 2),
                'total_profit_loss': round(total_profit_loss, 2),
                'total_profit_loss_percent': round(total_profit_loss_percent, 2),
                'positions_count': len(positions)
            }
            
        except Exception as e:
            self.logger.error(f"计算投资组合摘要失败: {e}")
            return {}
    
    def calculate_asset_allocation(self, positions: List[Dict]) -> Dict:
        """
        计算资产配置
        
        Args:
            positions: 持仓列表
            
        Returns:
            资产配置信息
        """
        try:
            if not positions:
                return {}
            
            total_value = sum(pos.get('current_value', 0) for pos in positions)
            if total_value == 0:
                return {}
            
            allocation = {}
            for pos in positions:
                market_type = pos.get('market_type', 'Unknown')
                value = pos.get('current_value', 0)
                allocation[market_type] = allocation.get(market_type, 0) + value
            
            # 计算百分比
            for market_type in allocation:
                allocation[market_type] = round((allocation[market_type] / total_value) * 100, 2)
            
            return allocation
            
        except Exception as e:
            self.logger.error(f"计算资产配置失败: {e}")
            return {}
    
    def calculate_risk_metrics(self, positions: List[Dict], price_history: Dict) -> Dict:
        """
        计算风险指标
        
        Args:
            positions: 持仓列表
            price_history: 价格历史数据
            
        Returns:
            风险指标
        """
        try:
            risk_metrics = {
                'portfolio_volatility': 0,
                'max_drawdown': 0,
                'sharpe_ratio': 0,
                'risk_level': 'Low'
            }
            
            # 简化的风险计算（实际应用中需要更复杂的计算）
            total_value = sum(pos.get('current_value', 0) for pos in positions)
            if total_value == 0:
                return risk_metrics
            
            # 计算最大持仓集中度
            max_position = max([pos.get('current_value', 0) for pos in positions], default=0)
            concentration = (max_position / total_value) * 100
            
            # 根据集中度判断风险等级
            if concentration > 30:
                risk_level = 'High'
            elif concentration > 20:
                risk_level = 'Medium'
            else:
                risk_level = 'Low'
            
            risk_metrics['concentration_risk'] = round(concentration, 2)
            risk_metrics['risk_level'] = risk_level
            
            return risk_metrics
            
        except Exception as e:
            self.logger.error(f"计算风险指标失败: {e}")
            return {}
    
    def calculate_performance_metrics(self, positions: List[Dict]) -> Dict:
        """
        计算业绩指标
        
        Args:
            positions: 持仓列表
            
        Returns:
            业绩指标
        """
        try:
            if not positions:
                return {}
            
            # 计算胜率
            profitable_positions = [pos for pos in positions if pos.get('profit_loss', 0) > 0]
            win_rate = len(profitable_positions) / len(positions) * 100 if positions else 0
            
            # 计算平均盈亏
            avg_profit = np.mean([pos.get('profit_loss', 0) for pos in profitable_positions]) if profitable_positions else 0
            losing_positions = [pos for pos in positions if pos.get('profit_loss', 0) < 0]
            avg_loss = np.mean([pos.get('profit_loss', 0) for pos in losing_positions]) if losing_positions else 0
            
            # 计算盈亏比
            profit_loss_ratio = abs(avg_profit / avg_loss) if avg_loss != 0 else 0
            
            return {
                'win_rate': round(win_rate, 2),
                'avg_profit': round(avg_profit, 2),
                'avg_loss': round(avg_loss, 2),
                'profit_loss_ratio': round(profit_loss_ratio, 2),
                'total_positions': len(positions),
                'profitable_positions': len(profitable_positions)
            }
            
        except Exception as e:
            self.logger.error(f"计算业绩指标失败: {e}")
            return {}
    
    def format_currency(self, amount: float, currency: str = 'CNY') -> str:
        """
        格式化货币显示
        
        Args:
            amount: 金额
            currency: 货币类型
            
        Returns:
            格式化后的货币字符串
        """
        try:
            if currency == 'CNY':
                return f"¥{amount:,.2f}"
            elif currency == 'USD':
                return f"${amount:,.2f}"
            elif currency == 'HKD':
                return f"HK${amount:,.2f}"
            else:
                return f"{amount:,.2f}"
                
        except Exception as e:
            self.logger.error(f"格式化货币失败: {e}")
            return f"{amount:,.2f}"
    
    def calculate_time_weighted_return(self, cash_flows: List[Dict], 
                                     start_value: float, end_value: float) -> float:
        """
        计算时间加权收益率
        
        Args:
            cash_flows: 现金流列表
            start_value: 期初价值
            end_value: 期末价值
            
        Returns:
            时间加权收益率
        """
        try:
            # 简化的时间加权收益率计算
            if start_value == 0:
                return 0
            
            total_return = (end_value - start_value) / start_value
            return round(total_return * 100, 2)
            
        except Exception as e:
            self.logger.error(f"计算时间加权收益率失败: {e}")
            return 0