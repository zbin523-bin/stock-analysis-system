"""
数据抓取Agent
负责从各种数据源获取股票价格、新闻等信息
"""

import json
import time
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import pandas as pd
import requests
from loguru import logger

try:
    import tushare as ts
    from alpha_vantage.timeseries import TimeSeries
    TUSHARE_AVAILABLE = True
except ImportError:
    TUSHARE_AVAILABLE = False
    logger.warning("TuShare或Alpha Vantage未安装，某些功能可能不可用")

from utils.logger import get_logger
from utils.date_utils import DateUtils
from utils.simple_price_fetcher import get_stock_price, get_batch_prices


class DataFetchingAgent:
    """数据抓取Agent"""
    
    def __init__(self, api_keys: Dict, stock_symbols: Dict):
        self.logger = get_logger("data_fetching")
        self.api_keys = api_keys
        self.stock_symbols = stock_symbols
        self.date_utils = DateUtils()
        
        # 初始化API客户端
        self._initialize_apis()
        
        # 数据缓存
        self.price_cache = {}
        self.news_cache = {}
        self.last_update = {}
        
        # 速率限制
        self.rate_limits = {
            'alpha_vantage': {'calls': 0, 'last_reset': datetime.now()},
            'tushare': {'calls': 0, 'last_reset': datetime.now()}
        }
        
    def _initialize_apis(self):
        """初始化API客户端"""
        try:
            # 初始化Alpha Vantage
            if 'alpha_vantage' in self.api_keys:
                av_key = self.api_keys['alpha_vantage']['api_key']
                self.ts = TimeSeries(key=av_key, output_format='pandas')
                self.logger.info("Alpha Vantage API初始化成功")
            
            # 初始化TuShare
            if 'tushare' in self.api_keys and TUSHARE_AVAILABLE:
                ts_key = self.api_keys['tushare']['api_key']
                ts.set_token(ts_key)
                self.pro = ts.pro_api()
                self.logger.info("TuShare Pro API初始化成功")
            elif not TUSHARE_AVAILABLE:
                self.logger.warning("TuShare未安装，A股数据获取功能不可用")
                
        except Exception as e:
            self.logger.error(f"API初始化失败: {e}")
    
    def get_stock_price(self, symbol: str, market_type: str) -> Dict:
        """
        获取股票价格
        
        Args:
            symbol: 股票代码
            market_type: 市场类型 ('us_stocks', 'a_stocks', 'hk_stocks')
            
        Returns:
            价格信息字典
        """
        try:
            cache_key = f"{symbol}_{market_type}"
            
            # 检查缓存
            if cache_key in self.price_cache:
                cached_data = self.price_cache[cache_key]
                if (datetime.now() - cached_data['timestamp']).seconds < 300:  # 5分钟缓存
                    return cached_data['data']
            
            # 使用简化的价格获取器
            price_data = get_stock_price(symbol, market_type)
            
            # 缓存结果
            if price_data and 'error' not in price_data:
                self.price_cache[cache_key] = {
                    'data': price_data,
                    'timestamp': datetime.now()
                }
            
            return price_data
            
        except Exception as e:
            self.logger.error(f"获取股票价格失败 {symbol} ({market_type}): {e}")
            return {'error': str(e)}
    
    def _get_us_stock_price(self, symbol: str) -> Dict:
        """获取美股价格"""
        try:
            if not hasattr(self, 'ts'):
                return {'error': 'Alpha Vantage API未初始化'}
            
            # 使用Alpha Vantage获取价格
            data, meta_data = self.ts.get_intraday(symbol=symbol, interval='1min', outputsize='compact')
            
            if data.empty:
                return {'error': '无数据'}
            
            # 获取最新价格
            latest_data = data.iloc[0]
            current_price = float(latest_data['4. close'])
            
            return {
                'symbol': symbol,
                'price': current_price,
                'timestamp': datetime.now().isoformat(),
                'currency': 'USD',
                'change': 0.0,  # 需要计算
                'change_percent': 0.0,
                'volume': int(latest_data['5. volume']) if '5. volume' in latest_data else 0
            }
            
        except Exception as e:
            self.logger.error(f"获取美股价格失败 {symbol}: {e}")
            return {'error': str(e)}
    
    def _get_a_stock_price(self, symbol: str) -> Dict:
        """获取A股价格"""
        try:
            if not hasattr(self, 'pro'):
                return {'error': 'TuShare API未初始化'}
            
            # 使用TuShare获取A股价格
            df = self.pro.daily(ts_code=symbol, start_date=(datetime.now() - timedelta(days=7)).strftime('%Y%m%d'))
            
            if df.empty:
                return {'error': '无数据'}
            
            # 获取最新价格
            latest_data = df.iloc[0]
            current_price = float(latest_data['close'])
            
            return {
                'symbol': symbol,
                'price': current_price,
                'timestamp': datetime.now().isoformat(),
                'currency': 'CNY',
                'change': float(latest_data['change']) if 'change' in latest_data else 0.0,
                'change_percent': float(latest_data['pct_chg']) if 'pct_chg' in latest_data else 0.0,
                'volume': int(latest_data['vol']) if 'vol' in latest_data else 0
            }
            
        except Exception as e:
            self.logger.error(f"获取A股价格失败 {symbol}: {e}")
            return {'error': str(e)}
    
    def _get_hk_stock_price(self, symbol: str) -> Dict:
        """获取港股价格"""
        try:
            # 使用Alpha Vantage获取港股价格
            if hasattr(self, 'ts'):
                data, meta_data = self.ts.get_intraday(symbol=symbol, interval='1min', outputsize='compact')
                
                if not data.empty:
                    latest_data = data.iloc[0]
                    current_price = float(latest_data['4. close'])
                    
                    return {
                        'symbol': symbol,
                        'price': current_price,
                        'timestamp': datetime.now().isoformat(),
                        'currency': 'HKD',
                        'change': 0.0,
                        'change_percent': 0.0,
                        'volume': int(latest_data['5. volume']) if '5. volume' in latest_data else 0
                    }
            
            # 备选方案：使用Yahoo Finance API
            return self._get_yahoo_finance_price(symbol)
            
        except Exception as e:
            self.logger.error(f"获取港股价格失败 {symbol}: {e}")
            return {'error': str(e)}
    
    def _get_yahoo_finance_price(self, symbol: str) -> Dict:
        """使用Yahoo Finance API获取价格"""
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                chart = data['chart']['result'][0]
                
                if chart and 'meta' in chart:
                    meta = chart['meta']
                    current_price = meta.get('regularMarketPrice', 0)
                    
                    return {
                        'symbol': symbol,
                        'price': current_price,
                        'timestamp': datetime.now().isoformat(),
                        'currency': meta.get('currency', 'USD'),
                        'change': meta.get('regularMarketPrice', 0) - meta.get('previousClose', 0),
                        'change_percent': 0.0,
                        'volume': meta.get('regularMarketVolume', 0)
                    }
            
            return {'error': '无法获取价格数据'}
            
        except Exception as e:
            self.logger.error(f"Yahoo Finance API调用失败 {symbol}: {e}")
            return {'error': str(e)}
    
    def update_all_prices(self) -> Dict:
        """更新所有持仓股票价格"""
        try:
            self.logger.info("开始更新所有股票价格...")
            
            results = {
                'success': 0,
                'failed': 0,
                'errors': [],
                'timestamp': datetime.now().isoformat()
            }
            
            # 从投资组合数据中获取需要更新的股票
            portfolio_data = self._load_portfolio_data()
            
            if not portfolio_data:
                self.logger.warning("没有找到投资组合数据")
                return results
            
            # 更新每个持仓的价格
            for position in portfolio_data.get('positions', []):
                symbol = position.get('symbol')
                market_type = position.get('market_type')
                
                if symbol and market_type:
                    price_data = self.get_stock_price(symbol, market_type)
                    
                    if 'error' not in price_data:
                        results['success'] += 1
                        # 更新持仓价格
                        position['current_price'] = price_data['price']
                        position['last_update'] = price_data['timestamp']
                    else:
                        results['failed'] += 1
                        results['errors'].append(f"{symbol}: {price_data['error']}")
            
            # 保存更新后的数据
            self._save_portfolio_data(portfolio_data)
            
            self.logger.info(f"价格更新完成: 成功 {results['success']}, 失败 {results['failed']}")
            return results
            
        except Exception as e:
            self.logger.error(f"更新所有价格失败: {e}")
            return {'success': 0, 'failed': 0, 'error': str(e)}
    
    def get_stock_news(self, symbol: str, market_type: str) -> List[Dict]:
        """获取股票相关新闻"""
        try:
            # 使用Composio搜索API获取新闻
            news_results = []
            
            # 搜索股票新闻
            search_query = f"{symbol} stock news"
            if market_type == 'a_stocks':
                search_query = f"{symbol} 股票新闻"
            
            # 这里可以集成Composio的搜索API
            # 目前返回模拟数据
            news_results = [
                {
                    'title': f'{symbol} 最新动态',
                    'summary': '公司发布重要公告',
                    'source': '财经媒体',
                    'timestamp': datetime.now().isoformat(),
                    'sentiment': 'neutral'
                }
            ]
            
            return news_results
            
        except Exception as e:
            self.logger.error(f"获取股票新闻失败 {symbol}: {e}")
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
    
    def get_status(self) -> Dict:
        """获取Agent状态"""
        return {
            'status': 'active',
            'api_status': {
                'alpha_vantage': hasattr(self, 'ts'),
                'tushare': hasattr(self, 'pro'),
                'yahoo_finance': True
            },
            'cache_size': len(self.price_cache),
            'last_update': self.last_update
        }
    
    def start(self):
        """启动Agent"""
        self.logger.info("数据抓取Agent启动")
    
    def stop(self):
        """停止Agent"""
        self.logger.info("数据抓取Agent停止")