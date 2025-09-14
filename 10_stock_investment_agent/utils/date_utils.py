"""
日期和时间工具模块
提供日期处理、时间计算、时区转换等功能
"""

import pytz
from datetime import datetime, timedelta, time, date
from typing import Dict, List, Optional, Tuple
from loguru import logger


class DateUtils:
    """日期时间工具类"""
    
    def __init__(self, timezone: str = 'Asia/Shanghai'):
        self.timezone = pytz.timezone(timezone)
        self.logger = logger.bind(utils="date")
    
    def get_current_time(self) -> datetime:
        """获取当前时间"""
        return datetime.now(self.timezone)
    
    def get_current_date(self) -> date:
        """获取当前日期"""
        return self.get_current_time().date()
    
    def format_datetime(self, dt: datetime, format_str: str = '%Y-%m-%d %H:%M:%S') -> str:
        """
        格式化日期时间
        
        Args:
            dt: 日期时间对象
            format_str: 格式字符串
            
        Returns:
            格式化后的字符串
        """
        try:
            return dt.strftime(format_str)
        except Exception as e:
            self.logger.error(f"格式化日期时间失败: {e}")
            return ""
    
    def parse_datetime(self, date_str: str, format_str: str = '%Y-%m-%d %H:%M:%S') -> Optional[datetime]:
        """
        解析日期时间字符串
        
        Args:
            date_str: 日期时间字符串
            format_str: 格式字符串
            
        Returns:
            日期时间对象
        """
        try:
            return datetime.strptime(date_str, format_str)
        except Exception as e:
            self.logger.error(f"解析日期时间失败: {e}")
            return None
    
    def get_trading_day(self, dt: datetime) -> bool:
        """
        判断是否为交易日
        
        Args:
            dt: 日期时间对象
            
        Returns:
            是否为交易日
        """
        try:
            # 周末不是交易日
            if dt.weekday() >= 5:  # 5=周六, 6=周日
                return False
            
            # TODO: 可以添加节假日判断
            return True
            
        except Exception as e:
            self.logger.error(f"判断交易日失败: {e}")
            return False
    
    def get_market_open_time(self, market: str) -> Tuple[time, time]:
        """
        获取市场开盘时间
        
        Args:
            market: 市场 ('US', 'A', 'HK')
            
        Returns:
            (开盘时间, 收盘时间)
        """
        market_times = {
            'US': (time(21, 30), time(4, 0)),    # 美股夏令时
            'A': (time(9, 30), time(15, 0)),    # A股
            'HK': (time(9, 30), time(16, 0))     # 港股
        }
        return market_times.get(market, (time(9, 0), time(17, 0)))
    
    def is_market_open(self, market: str) -> bool:
        """
        判断市场是否开盘
        
        Args:
            market: 市场
            
        Returns:
            是否开盘
        """
        try:
            now = self.get_current_time()
            
            # 检查是否为交易日
            if not self.get_trading_day(now):
                return False
            
            # 检查是否在交易时间内
            open_time, close_time = self.get_market_open_time(market)
            current_time = now.time()
            
            return open_time <= current_time <= close_time
            
        except Exception as e:
            self.logger.error(f"判断市场开盘状态失败: {e}")
            return False
    
    def get_next_trading_day(self, dt: Optional[datetime] = None) -> datetime:
        """
        获取下一个交易日
        
        Args:
            dt: 参考日期，默认为当前日期
            
        Returns:
            下一个交易日
        """
        if dt is None:
            dt = self.get_current_time()
        
        next_day = dt + timedelta(days=1)
        while not self.get_trading_day(next_day):
            next_day += timedelta(days=1)
        
        return next_day
    
    def get_previous_trading_day(self, dt: Optional[datetime] = None) -> datetime:
        """
        获取上一个交易日
        
        Args:
            dt: 参考日期，默认为当前日期
            
        Returns:
            上一个交易日
        """
        if dt is None:
            dt = self.get_current_time()
        
        prev_day = dt - timedelta(days=1)
        while not self.get_trading_day(prev_day):
            prev_day -= timedelta(days=1)
        
        return prev_day
    
    def get_trading_days_in_month(self, year: int, month: int) -> List[datetime]:
        """
        获取某月的所有交易日
        
        Args:
            year: 年份
            month: 月份
            
        Returns:
            交易日列表
        """
        trading_days = []
        
        # 获取月份的第一天和最后一天
        first_day = datetime(year, month, 1)
        if month == 12:
            last_day = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = datetime(year, month + 1, 1) - timedelta(days=1)
        
        # 遍历每一天
        current_day = first_day
        while current_day <= last_day:
            if self.get_trading_day(current_day):
                trading_days.append(current_day)
            current_day += timedelta(days=1)
        
        return trading_days
    
    def get_time_ranges(self, range_type: str) -> Dict[str, datetime]:
        """
        获取时间范围
        
        Args:
            range_type: 范围类型 ('today', 'week', 'month', 'year')
            
        Returns:
            时间范围字典
        """
        now = self.get_current_time()
        
        if range_type == 'today':
            return {
                'start': now.replace(hour=0, minute=0, second=0, microsecond=0),
                'end': now.replace(hour=23, minute=59, second=59, microsecond=999999)
            }
        
        elif range_type == 'week':
            # 本周开始（周一）
            days_since_monday = now.weekday()
            week_start = now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=days_since_monday)
            week_end = week_start + timedelta(days=6, hours=23, minutes=59, seconds=59)
            
            return {
                'start': week_start,
                'end': week_end
            }
        
        elif range_type == 'month':
            # 本月开始
            month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            # 下月第一天减1秒
            if now.month == 12:
                next_month = now.replace(year=now.year + 1, month=1, day=1)
            else:
                next_month = now.replace(month=now.month + 1, day=1)
            
            month_end = next_month - timedelta(seconds=1)
            
            return {
                'start': month_start,
                'end': month_end
            }
        
        elif range_type == 'year':
            # 本年开始
            year_start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            year_end = now.replace(month=12, day=31, hour=23, minute=59, second=59, microsecond=999999)
            
            return {
                'start': year_start,
                'end': year_end
            }
        
        else:
            return {
                'start': now,
                'end': now
            }
    
    def add_business_days(self, dt: datetime, days: int) -> datetime:
        """
        添加工作日
        
        Args:
            dt: 起始日期
            days: 要添加的工作日数
            
        Returns:
            结果日期
        """
        result = dt
        remaining_days = abs(days)
        
        while remaining_days > 0:
            result += timedelta(days=1 if days > 0 else -1)
            if self.get_trading_day(result):
                remaining_days -= 1
        
        return result
    
    def get_date_range_string(self, start_date: datetime, end_date: datetime) -> str:
        """
        获取日期范围字符串
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            日期范围字符串
        """
        try:
            if start_date.date() == end_date.date():
                return self.format_datetime(start_date, '%Y-%m-%d')
            else:
                return f"{self.format_datetime(start_date, '%Y-%m-%d')} 至 {self.format_datetime(end_date, '%Y-%m-%d')}"
                
        except Exception as e:
            self.logger.error(f"获取日期范围字符串失败: {e}")
            return ""
    
    def get_relative_time_string(self, dt: datetime) -> str:
        """
        获取相对时间字符串
        
        Args:
            dt: 目标时间
            
        Returns:
            相对时间字符串
        """
        try:
            now = self.get_current_time()
            diff = now - dt
            
            if diff.days > 0:
                return f"{diff.days}天前"
            elif diff.seconds > 3600:
                hours = diff.seconds // 3600
                return f"{hours}小时前"
            elif diff.seconds > 60:
                minutes = diff.seconds // 60
                return f"{minutes}分钟前"
            else:
                return "刚刚"
                
        except Exception as e:
            self.logger.error(f"获取相对时间字符串失败: {e}")
            return ""