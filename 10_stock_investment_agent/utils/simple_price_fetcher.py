"""
简化的股票价格获取模块
使用Yahoo Finance作为数据源
"""

import yfinance as yf
from datetime import datetime
from typing import Dict, Optional
from utils.logger import get_logger

class SimplePriceFetcher:
    """简化的股票价格获取器"""
    
    def __init__(self):
        self.logger = get_logger("price_fetcher")
    
    def get_stock_price(self, symbol: str, market_type: str) -> Dict:
        """
        获取股票价格
        
        Args:
            symbol: 股票代码
            market_type: 市场类型
            
        Returns:
            价格信息字典
        """
        try:
            # 根据市场类型调整股票代码
            yf_symbol = self._convert_to_yfinance_symbol(symbol, market_type)
            
            # 获取ticker对象
            ticker = yf.Ticker(yf_symbol)
            
            # 获取历史数据
            hist = ticker.history(period='1d', interval='1m')
            
            if hist.empty:
                # 尝试获取日线数据
                hist = ticker.history(period='2d')
                
                if hist.empty:
                    return {'error': '无法获取价格数据'}
            
            # 获取最新价格
            latest_data = hist.iloc[-1]
            current_price = float(latest_data['Close'])
            
            # 计算涨跌幅
            if len(hist) > 1:
                prev_close = float(hist.iloc[-2]['Close'])
                change = current_price - prev_close
                change_percent = (change / prev_close) * 100 if prev_close != 0 else 0
            else:
                change = 0
                change_percent = 0
            
            # 获取交易量
            volume = int(latest_data['Volume']) if 'Volume' in latest_data else 0
            
            # 获取货币类型
            info = ticker.info
            currency = info.get('currency', 'USD')
            
            return {
                'symbol': symbol,
                'price': current_price,
                'timestamp': datetime.now().isoformat(),
                'currency': currency,
                'change': change,
                'change_percent': change_percent,
                'volume': volume,
                'market_type': market_type
            }
            
        except Exception as e:
            self.logger.error(f"获取股票价格失败 {symbol} ({market_type}): {e}")
            return {'error': str(e)}
    
    def _convert_to_yfinance_symbol(self, symbol: str, market_type: str) -> str:
        """将股票代码转换为Yahoo Finance格式"""
        
        if market_type == 'us_stocks':
            # 美股直接使用
            return symbol
        elif market_type == 'a_stocks':
            # A股需要添加.SS或.SZ后缀
            if symbol.startswith('6'):
                return f"{symbol}.SS"  # 上海交易所
            else:
                return f"{symbol}.SZ"  # 深圳交易所
        elif market_type == 'hk_stocks':
            # 港股添加.HK后缀
            return f"{symbol}.HK"
        else:
            # 默认直接返回
            return symbol
    
    def get_batch_prices(self, symbols: list) -> Dict:
        """
        批量获取股票价格
        
        Args:
            symbols: 股票代码列表，每个元素为 (symbol, market_type) 元组
            
        Returns:
            批量价格结果
        """
        results = {}
        
        for symbol, market_type in symbols:
            try:
                price_data = self.get_stock_price(symbol, market_type)
                results[symbol] = price_data
                
            except Exception as e:
                self.logger.error(f"批量获取价格失败 {symbol}: {e}")
                results[symbol] = {'error': str(e)}
        
        return results
    
    def get_market_status(self, symbol: str, market_type: str) -> Dict:
        """
        获取市场状态信息
        
        Args:
            symbol: 股票代码
            market_type: 市场类型
            
        Returns:
            市场状态信息
        """
        try:
            yf_symbol = self._convert_to_yfinance_symbol(symbol, market_type)
            ticker = yf.Ticker(yf_symbol)
            
            # 获取基本信息
            info = ticker.info
            
            return {
                'symbol': symbol,
                'market_type': market_type,
                'name': info.get('longName', info.get('shortName', 'N/A')),
                'exchange': info.get('exchange', 'N/A'),
                'currency': info.get('currency', 'USD'),
                'market_cap': info.get('marketCap', 0),
                'regular_market_price': info.get('regularMarketPrice', 0),
                'previous_close': info.get('previousClose', 0),
                'open': info.get('regularMarketOpen', 0),
                'day_high': info.get('regularMarketDayHigh', 0),
                'day_low': info.get('regularMarketDayLow', 0),
                'volume': info.get('regularMarketVolume', 0),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"获取市场状态失败 {symbol}: {e}")
            return {'error': str(e)}

# 单例实例
price_fetcher = SimplePriceFetcher()

# 便捷函数
def get_stock_price(symbol: str, market_type: str) -> Dict:
    """获取股票价格的便捷函数"""
    return price_fetcher.get_stock_price(symbol, market_type)

def get_batch_prices(symbols: list) -> Dict:
    """批量获取股票价格的便捷函数"""
    return price_fetcher.get_batch_prices(symbols)

def get_market_status(symbol: str, market_type: str) -> Dict:
    """获取市场状态的便捷函数"""
    return price_fetcher.get_market_status(symbol, market_type)