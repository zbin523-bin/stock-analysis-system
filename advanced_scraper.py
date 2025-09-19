#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
高级港股美股数据抓取系统
包含多种协议和方法的数据获取解决方案
"""

import requests
import re
import json
import time
from datetime import datetime
from typing import Dict, Optional, List, Any
from urllib.parse import quote, urlencode
import hashlib
import random

class AdvancedStockScraper:
    """高级股票数据抓取器 - 多协议多方法"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })
        
        # 代理服务器列表（如果需要）
        self.proxies = []
        
    def get_hk_stock_data(self, code: str) -> Optional[Dict]:
        """获取港股数据 - 高级多源方法"""
        print(f"开始获取港股 {code} 数据...")
        
        # 方法1: 东方财富港股API
        data = self._get_hk_from_eastmoney(code)
        if data:
            return data
            
        # 方法2: 同花顺港股API
        data = self._get_hk_from_10jqka(code)
        if data:
            return data
            
        # 方法3: 新浪财经港股（多种格式）
        data = self._get_hk_from_sina_advanced(code)
        if data:
            return data
            
        # 方法4: 腾讯财经港股（多种格式）
        data = self._get_hk_from_tencent_advanced(code)
        if data:
            return data
            
        # 方法5: 雪球港股API
        data = self._get_hk_from_xueqiu_advanced(code)
        if data:
            return data
            
        # 方法6: 富途港股API
        data = self._get_hk_from_futu(code)
        if data:
            return data
            
        # 方法7: 阿里云行情API
        data = self._get_hk_from_alibaba(code)
        if data:
            return data
            
        # 方法8: 金融界港股API
        data = self._get_hk_from_jrj(code)
        if data:
            return data
            
        print(f"港股 {code} 所有数据源都失败")
        return None
    
    def _get_hk_from_eastmoney(self, code: str) -> Optional[Dict]:
        """东方财富港股API"""
        try:
            # 东方财富港股API
            url = f'https://push2.eastmoney.com/api/qt/stock/kline/get'
            params = {
                'cb': 'jQuery' + str(int(time.time() * 1000)),
                'secid': '116.' + code,  # 116表示港股
                'ut': 'fa5fd1943c7b386f172d6893dbfba10b',
                'fields1': 'f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13',
                'fields2': 'f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61',
                'klt': '101',  # 日线
                'lmt': '1',    # 最新1条
            }
            
            headers = {
                'Referer': 'https://quote.eastmoney.com/hk/' + code + '.html',
                'Accept': '*/*',
            }
            
            response = self.session.get(url, params=params, headers=headers, timeout=10)
            if response.status_code == 200:
                content = response.text
                # 提取JSON数据
                json_match = re.search(r'\((.*)\)', content)
                if json_match:
                    data = json.loads(json_match.group(1))
                    if data.get('data') and data['data'].get('klines'):
                        kline = data['data']['klines'][0]
                        fields = kline.split(',')
                        
                        if len(fields) >= 10:
                            return {
                                'code': code,
                                'name': f'H股{code}',
                                'price': float(fields[2]),  # 收盘价
                                'open': float(fields[1]),   # 开盘价
                                'high': float(fields[3]),   # 最高价
                                'low': float(fields[4]),    # 最低价
                                'volume': int(fields[5]),   # 成交量
                                'change': float(fields[6]) if fields[6] else 0,
                                'changePercent': float(fields[7]) if fields[7] else 0,
                                'timestamp': int(time.time() * 1000),
                                'currency': 'HKD',
                                'source': 'eastmoney'
                            }
        except Exception as e:
            print(f"东方财富港股 {code} 失败: {e}")
        
        return None
    
    def _get_hk_from_10jqka(self, code: str) -> Optional[Dict]:
        """同花顺港股API"""
        try:
            # 同花顺港股API
            url = f'https://d.10jqka.com.cn/v6/realhead/hk/{code}.js'
            
            headers = {
                'Referer': 'https://stockpage.10jqka.com.cn/hk/' + code + '/',
                'Accept': '*/*',
            }
            
            response = self.session.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                content = response.text
                # 提取JSON数据
                json_match = re.search(r'\((.*)\)', content)
                if json_match:
                    data = json.loads(json_match.group(1))
                    if data.get('items'):
                        item = data['items'][0]
                        return {
                            'code': code,
                            'name': item.get('name', f'H股{code}'),
                            'price': float(item.get('price', 0)),
                            'open': float(item.get('open', 0)),
                            'high': float(item.get('high', 0)),
                            'low': float(item.get('low', 0)),
                            'volume': int(item.get('volume', 0)),
                            'change': float(item.get('updown', 0)),
                            'changePercent': float(item.get('percent', 0)),
                            'timestamp': int(time.time() * 1000),
                            'currency': 'HKD',
                            'source': '10jqka'
                        }
        except Exception as e:
            print(f"同花顺港股 {code} 失败: {e}")
        
        return None
    
    def _get_hk_from_sina_advanced(self, code: str) -> Optional[Dict]:
        """新浪财经港股API - 高级版"""
        try:
            # 尝试多种新浪API格式
            urls = [
                f'https://hq.sinajs.cn/?list=rt_hk{code}',
                f'https://hq.sinajs.cn/?list=hk{code}',
                f'https://hq.sinajs.cn/?list=gb_hk{code}',
                f'https://hq.sinajs.cn/?list=hf_{code}',
            ]
            
            headers = {
                'Referer': 'https://finance.sina.com.cn/',
                'Accept': '*/*',
            }
            
            for url in urls:
                try:
                    response = self.session.get(url, headers=headers, timeout=5)
                    if response.status_code == 200:
                        content = response.text
                        if '=' in content and '"' in content:
                            data_part = content.split('=')[1].strip('";\n')
                            fields = data_part.split(',')
                            
                            if len(fields) >= 10 and fields[3] != '0.000':
                                name = fields[6] if fields[6] else f"HK{code}"
                                price = float(fields[3]) if fields[3] and fields[3] != '0.000' else 0
                                change = float(fields[4]) if fields[4] and fields[4] != '0.000' else 0
                                change_percent = float(fields[5]) if fields[5] and fields[5] != '0.000' else 0
                                volume = int(fields[8]) if fields[8] and fields[8].isdigit() else 0
                                
                                if price > 0:
                                    return {
                                        'code': code,
                                        'name': name,
                                        'price': price,
                                        'change': change,
                                        'changePercent': change_percent,
                                        'volume': volume,
                                        'timestamp': int(time.time() * 1000),
                                        'currency': 'HKD',
                                        'source': 'sina'
                                    }
                except:
                    continue
        except Exception as e:
            print(f"新浪港股 {code} 失败: {e}")
        
        return None
    
    def _get_hk_from_tencent_advanced(self, code: str) -> Optional[Dict]:
        """腾讯财经港股API - 高级版"""
        try:
            # 尝试多种腾讯API格式
            urls = [
                f'https://qt.gtimg.cn/q=hk{code}',
                f'https://qt.gtimg.cn/q=r_hk{code}',
                f'https://qt.gtimg.cn/q=s_hk{code}',
                f'https://qt.gtimg.cn/q=b_hk{code}',
                f'https://qt.gtimg.cn/q=ff_hk{code}',
            ]
            
            # 尝试不同的User-Agent
            user_agents = [
                'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 Safari/604.1',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/604.1',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            ]
            
            headers_base = {
                'Referer': 'https://stockapp.finance.qq.com/',
                'Accept': 'text/plain, */*; q=0.01',
            }
            
            for url in urls:
                for ua in user_agents:
                    try:
                        headers = headers_base.copy()
                        headers['User-Agent'] = ua
                        
                        response = self.session.get(url, headers=headers, timeout=5)
                        if response.status_code == 200:
                            content = response.text
                            if '=' in content and '~' in content and 'pv_none_match' not in content:
                                data_part = content.split('=')[1].strip('";\n')
                                fields = data_part.split('~')
                                
                                if len(fields) >= 10:
                                    name = fields[1] if fields[1] else f"HK{code}"
                                    price = float(fields[3]) if fields[3] and fields[3] != '0.00' else 0
                                    change = float(fields[4]) if fields[4] and fields[4] != '0.00' else 0
                                    change_percent = float(fields[5]) if fields[5] and fields[5] != '0.00' else 0
                                    volume = int(fields[6]) if fields[6] and fields[6].isdigit() else 0
                                    
                                    if price > 0:
                                        return {
                                            'code': code,
                                            'name': name,
                                            'price': price,
                                            'change': change,
                                            'changePercent': change_percent,
                                            'volume': volume,
                                            'timestamp': int(time.time() * 1000),
                                            'currency': 'HKD',
                                            'source': 'tencent'
                                        }
                    except:
                        continue
        except Exception as e:
            print(f"腾讯港股 {code} 失败: {e}")
        
        return None
    
    def _get_hk_from_xueqiu_advanced(self, code: str) -> Optional[Dict]:
        """雪球港股API - 高级版"""
        try:
            # 雪球港股API
            symbol = f'HK{code}'
            urls = [
                f'https://stock.xueqiu.com/v5/stock/quote.json?symbol={symbol}&extend=detail',
                f'https://stock.xueqiu.com/v5/stock/quote.json?symbol={symbol}',
                f'https://stock.xueqiu.com/v5/stock/chart/kline.json?symbol={symbol}&period=day&type=before&count=1&indicator=kline,pe,pb,ps,pcf,market_capital,agt,ggt,balance',
            ]
            
            # 获取雪球cookie
            self.session.get('https://xueqiu.com/', timeout=5)
            
            headers = {
                'Referer': f'https://xueqiu.com/S/{symbol}',
                'Accept': 'application/json, text/plain, */*',
                'X-Requested-With': 'XMLHttpRequest',
            }
            
            for url in urls:
                try:
                    response = self.session.get(url, headers=headers, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        
                        if data.get('data') and data['data'].get('quote'):
                            quote = data['data']['quote']
                            price = quote.get('current', 0)
                            
                            if price > 0:
                                return {
                                    'code': code,
                                    'name': quote.get('name', f'H股{code}'),
                                    'price': price,
                                    'change': quote.get('chg', 0),
                                    'changePercent': quote.get('percent', 0),
                                    'volume': quote.get('volume', 0),
                                    'high': quote.get('high', 0),
                                    'low': quote.get('low', 0),
                                    'open': quote.get('open', 0),
                                    'timestamp': int(time.time() * 1000),
                                    'currency': 'HKD',
                                    'source': 'xueqiu'
                                }
                        
                        # 处理K线数据
                        if data.get('data') and data['data'].get('item'):
                            items = data['data']['item']
                            if items:
                                item = items[-1]  # 最新数据
                                return {
                                    'code': code,
                                    'name': f'H股{code}',
                                    'price': float(item[2]),  # 收盘价
                                    'open': float(item[1]),   # 开盘价
                                    'high': float(item[3]),   # 最高价
                                    'low': float(item[4]),    # 最低价
                                    'volume': int(item[5]),   # 成交量
                                    'timestamp': int(time.time() * 1000),
                                    'currency': 'HKD',
                                    'source': 'xueqiu_kline'
                                }
                except:
                    continue
        except Exception as e:
            print(f"雪球港股 {code} 失败: {e}")
        
        return None
    
    def _get_hk_from_futu(self, code: str) -> Optional[Dict]:
        """富途港股API"""
        try:
            # 富途牛牛港股API
            url = f'https://www.futunn.com/stock/US-HK{code}'
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Referer': 'https://www.futunn.com/',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            }
            
            response = self.session.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                content = response.text
                
                # 使用正则表达式提取数据
                patterns = [
                    (r'data-price=\"([0-9.]+)\"', 'price'),
                    (r'data-name=\"([^\"]+)\"', 'name'),
                    (r'data-change=\"([0-9.-]+)\"', 'change'),
                    (r'data-change-percent=\"([0-9.-]+)\"', 'changePercent'),
                    (r'data-volume=\"([0-9]+)\"', 'volume'),
                ]
                
                data = {'code': code, 'currency': 'HKD', 'source': 'futu'}
                for pattern, key in patterns:
                    match = re.search(pattern, content)
                    if match:
                        value = match.group(1)
                        if key in ['price', 'change', 'changePercent']:
                            data[key] = float(value)
                        elif key == 'volume':
                            data[key] = int(value)
                        else:
                            data[key] = value
                
                if data.get('price', 0) > 0:
                    data['timestamp'] = int(time.time() * 1000)
                    if 'name' not in data:
                        data['name'] = f'H股{code}'
                    return data
        except Exception as e:
            print(f"富途港股 {code} 失败: {e}")
        
        return None
    
    def _get_hk_from_alibaba(self, code: str) -> Optional[Dict]:
        """阿里云行情API"""
        try:
            # 阿里云行情API
            url = f'https://www.alipay.com/hk/stock/{code}'
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Referer': 'https://www.alipay.com/',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            }
            
            response = self.session.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                content = response.text
                
                # 尝试从页面中提取数据
                price_pattern = r'\"currentPrice\"\s*:\s*([0-9.]+)'
                name_pattern = r'\"stockName\"\s*:\s*\"([^\"]+)\"'
                
                price_match = re.search(price_pattern, content)
                name_match = re.search(name_pattern, content)
                
                if price_match:
                    price = float(price_match.group(1))
                    name = name_match.group(1) if name_match else f'H股{code}'
                    
                    return {
                        'code': code,
                        'name': name,
                        'price': price,
                        'change': 0,
                        'changePercent': 0,
                        'volume': 0,
                        'timestamp': int(time.time() * 1000),
                        'currency': 'HKD',
                        'source': 'alibaba'
                    }
        except Exception as e:
            print(f"阿里云港股 {code} 失败: {e}")
        
        return None
    
    def _get_hk_from_jrj(self, code: str) -> Optional[Dict]:
        """金融界港股API"""
        try:
            # 金融界港股API
            url = f'https://hqt.jrj.com.cn/hkstock/{code}.js'
            
            headers = {
                'Referer': 'https://hk.jrj.com.cn/' + code + '.shtml',
                'Accept': '*/*',
            }
            
            response = self.session.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                content = response.text
                # 提取JSON数据
                json_match = re.search(r'\((.*)\)', content)
                if json_match:
                    data = json.loads(json_match.group(1))
                    if data.get('Data'):
                        item = data['Data']
                        return {
                            'code': code,
                            'name': item.get('Name', f'H股{code}'),
                            'price': float(item.get('Price', 0)),
                            'change': float(item.get('Change', 0)),
                            'changePercent': float(item.get('ChangePercent', 0)),
                            'volume': int(item.get('Volume', 0)),
                            'timestamp': int(time.time() * 1000),
                            'currency': 'HKD',
                            'source': 'jrj'
                        }
        except Exception as e:
            print(f"金融界港股 {code} 失败: {e}")
        
        return None
    
    def get_us_stock_data(self, symbol: str) -> Optional[Dict]:
        """获取美股数据 - 高级多源方法"""
        print(f"开始获取美股 {symbol} 数据...")
        
        # 方法1: Yahoo Finance高级API
        data = self._get_us_from_yahoo_advanced(symbol)
        if data:
            return data
            
        # 方法2: Alpha Vantage高级API
        data = self._get_us_from_alpha_vantage_advanced(symbol)
        if data:
            return data
            
        # 方法3: IEX Cloud高级API
        data = self._get_us_from_iex_advanced(symbol)
        if data:
            return data
            
        # 方法4: Finnhub高级API
        data = self._get_us_from_finnhub(symbol)
        if data:
            return data
            
        # 方法5: MarketStack高级API
        data = self._get_us_from_marketstack(symbol)
        if data:
            return data
            
        # 方法6: Polygon.io高级API
        data = self._get_us_from_polygon(symbol)
        if data:
            return data
            
        # 方法7: TradingView高级API
        data = self._get_us_from_tradingview(symbol)
        if data:
            return data
            
        print(f"美股 {symbol} 所有数据源都失败")
        return None
    
    def _get_us_from_yahoo_advanced(self, symbol: str) -> Optional[Dict]:
        """Yahoo Finance高级API"""
        try:
            # Yahoo Finance多种API格式
            urls = [
                f'https://query1.finance.yahoo.com/v8/finance/chart/{symbol}',
                f'https://query2.finance.yahoo.com/v8/finance/chart/{symbol}',
                f'https://guce.yahoo.com/consent',
                f'https://finance.yahoo.com/quote/{symbol}',
            ]
            
            # 尝试不同的cookie和header
            headers_list = [
                {
                    'Referer': f'https://finance.yahoo.com/quote/{symbol}',
                    'Accept': 'application/json',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                },
                {
                    'Referer': f'https://finance.yahoo.com/quote/{symbol}',
                    'Accept': 'application/json',
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/604.1',
                },
            ]
            
            for url in urls:
                for headers in headers_list:
                    try:
                        response = self.session.get(url, headers=headers, timeout=10)
                        if response.status_code == 200:
                            if 'chart' in url:
                                data = response.json()
                                chart = data.get('chart', {}).get('result', [])
                                if chart:
                                    result = chart[0]
                                    meta = result.get('meta', {})
                                    price = meta.get('regularMarketPrice', 0)
                                    
                                    if price > 0:
                                        return {
                                            'code': symbol,
                                            'name': meta.get('longName', meta.get('shortName', symbol)),
                                            'price': price,
                                            'change': meta.get('regularMarketPrice', 0) - meta.get('previousClose', price),
                                            'changePercent': 0,
                                            'volume': meta.get('regularMarketVolume', 0),
                                            'timestamp': int(time.time() * 1000),
                                            'currency': 'USD',
                                            'source': 'yahoo'
                                        }
                            else:
                                # 从HTML页面提取数据
                                content = response.text
                                price_pattern = r'data-field=\"regularMarketPrice\".*?value=\"([0-9.]+)\"'
                                price_match = re.search(price_pattern, content)
                                if price_match:
                                    price = float(price_match.group(1))
                                    return {
                                        'code': symbol,
                                        'name': symbol,
                                        'price': price,
                                        'change': 0,
                                        'changePercent': 0,
                                        'volume': 0,
                                        'timestamp': int(time.time() * 1000),
                                        'currency': 'USD',
                                        'source': 'yahoo_html'
                                    }
                    except:
                        continue
        except Exception as e:
            print(f"Yahoo Finance美股 {symbol} 失败: {e}")
        
        return None
    
    def _get_us_from_alpha_vantage_advanced(self, symbol: str) -> Optional[Dict]:
        """Alpha Vantage高级API"""
        try:
            # Alpha Vantage多种API
            urls = [
                f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey=demo',
                f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=1min&apikey=demo',
                f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey=demo',
            ]
            
            for url in urls:
                try:
                    response = self.session.get(url, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        
                        if 'Global Quote' in data:
                            quote = data['Global Quote']
                            price = float(quote.get('05. price', 0))
                            
                            if price > 0:
                                return {
                                    'code': symbol,
                                    'name': symbol,
                                    'price': price,
                                    'change': float(quote.get('09. change', 0)),
                                    'changePercent': float(quote.get('10. change percent', '0%').replace('%', '')),
                                    'volume': int(quote.get('06. volume', 0)),
                                    'timestamp': int(time.time() * 1000),
                                    'currency': 'USD',
                                    'source': 'alpha_vantage'
                                }
                        
                        # 处理时间序列数据
                        if 'Time Series (1min)' in data:
                            time_series = data['Time Series (1min)']
                            latest_time = sorted(time_series.keys())[-1]
                            latest_data = time_series[latest_time]
                            price = float(latest_data.get('4. close', 0))
                            
                            if price > 0:
                                return {
                                    'code': symbol,
                                    'name': symbol,
                                    'price': price,
                                    'change': 0,
                                    'changePercent': 0,
                                    'volume': int(latest_data.get('5. volume', 0)),
                                    'timestamp': int(time.time() * 1000),
                                    'currency': 'USD',
                                    'source': 'alpha_vantage_intraday'
                                }
                except:
                    continue
        except Exception as e:
            print(f"Alpha Vantage美股 {symbol} 失败: {e}")
        
        return None
    
    def _get_us_from_iex_advanced(self, symbol: str) -> Optional[Dict]:
        """IEX Cloud高级API"""
        try:
            # IEX Cloud多种API
            urls = [
                f'https://cloud.iexapis.com/stable/stock/{symbol}/quote?token=Tpk_1234567890',
                f'https://cloud.iexapis.com/stable/stock/{symbol}/intraday-prices?token=Tpk_1234567890',
                f'https://cloud.iexapis.com/stable/stock/{symbol}/chart/1d?token=Tpk_1234567890',
            ]
            
            for url in urls:
                try:
                    response = self.session.get(url, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        
                        if 'latestPrice' in data:
                            price = data.get('latestPrice', 0)
                            
                            if price > 0:
                                return {
                                    'code': symbol,
                                    'name': data.get('companyName', symbol),
                                    'price': price,
                                    'change': data.get('change', 0),
                                    'changePercent': data.get('changePercent', 0),
                                    'volume': data.get('volume', 0),
                                    'timestamp': int(time.time() * 1000),
                                    'currency': 'USD',
                                    'source': 'iex_cloud'
                                }
                        
                        # 处理数组数据
                        if isinstance(data, list) and data:
                            latest = data[-1]
                            price = latest.get('close', latest.get('price', 0))
                            
                            if price > 0:
                                return {
                                    'code': symbol,
                                    'name': symbol,
                                    'price': price,
                                    'change': 0,
                                    'changePercent': 0,
                                    'volume': latest.get('volume', 0),
                                    'timestamp': int(time.time() * 1000),
                                    'currency': 'USD',
                                    'source': 'iex_cloud_intraday'
                                }
                except:
                    continue
        except Exception as e:
            print(f"IEX Cloud美股 {symbol} 失败: {e}")
        
        return None
    
    def _get_us_from_finnhub(self, symbol: str) -> Optional[Dict]:
        """Finnhub高级API"""
        try:
            # Finnhub API
            url = f'https://finnhub.io/api/v1/quote?symbol={symbol}&token=demo'
            
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                price = data.get('c', 0)
                
                if price > 0:
                    return {
                        'code': symbol,
                        'name': symbol,
                        'price': price,
                        'change': data.get('d', 0),
                        'changePercent': data.get('dp', 0),
                        'volume': 0,
                        'timestamp': int(time.time() * 1000),
                        'currency': 'USD',
                        'source': 'finnhub'
                    }
        except Exception as e:
            print(f"Finnhub美股 {symbol} 失败: {e}")
        
        return None
    
    def _get_us_from_marketstack(self, symbol: str) -> Optional[Dict]:
        """MarketStack高级API"""
        try:
            # MarketStack API
            url = f'https://api.marketstack.com/v1/eod?access_key=demo&symbols={symbol}&limit=1'
            
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('data'):
                    item = data['data'][0]
                    price = item.get('close', 0)
                    
                    if price > 0:
                        return {
                            'code': symbol,
                            'name': symbol,
                            'price': price,
                            'change': item.get('change', 0),
                            'changePercent': item.get('change_percent', 0),
                            'volume': item.get('volume', 0),
                            'timestamp': int(time.time() * 1000),
                            'currency': 'USD',
                            'source': 'marketstack'
                        }
        except Exception as e:
            print(f"MarketStack美股 {symbol} 失败: {e}")
        
        return None
    
    def _get_us_from_polygon(self, symbol: str) -> Optional[Dict]:
        """Polygon.io高级API"""
        try:
            # Polygon.io API
            url = f'https://api.polygon.io/v2/aggs/ticker/{symbol}/prev?adjusted=true&apiKey=demo'
            
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('results'):
                    item = data['results'][0]
                    price = item.get('c', 0)
                    
                    if price > 0:
                        return {
                            'code': symbol,
                            'name': symbol,
                            'price': price,
                            'change': 0,
                            'changePercent': 0,
                            'volume': item.get('v', 0),
                            'timestamp': int(time.time() * 1000),
                            'currency': 'USD',
                            'source': 'polygon'
                        }
        except Exception as e:
            print(f"Polygon美股 {symbol} 失败: {e}")
        
        return None
    
    def _get_us_from_tradingview(self, symbol: str) -> Optional[Dict]:
        """TradingView高级API"""
        try:
            # TradingView API
            url = f'https://www.tradingview.com/symbols/{symbol}/'
            
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                content = response.text
                
                # 使用正则表达式提取数据
                price_pattern = r'\"last_price\"\s*:\s*\"([0-9.]+)\"'
                name_pattern = r'\"short_name\"\s*:\s*\"([^\"]+)\"'
                
                price_match = re.search(price_pattern, content)
                name_match = re.search(name_pattern, content)
                
                if price_match:
                    price = float(price_match.group(1))
                    name = name_match.group(1) if name_match else symbol
                    
                    return {
                        'code': symbol,
                        'name': name,
                        'price': price,
                        'change': 0,
                        'changePercent': 0,
                        'volume': 0,
                        'timestamp': int(time.time() * 1000),
                        'currency': 'USD',
                        'source': 'tradingview'
                    }
        except Exception as e:
            print(f"TradingView美股 {symbol} 失败: {e}")
        
        return None

# 测试函数
def test_advanced_scraper():
    """测试高级抓取器"""
    scraper = AdvancedStockScraper()
    
    print("=== 测试高级港股数据抓取 ===")
    hk_stocks = ['0700', '0941', '0005', '03690']  # 腾讯、中国移动、汇丰、美团
    for code in hk_stocks:
        print(f"\n测试港股 {code}:")
        data = scraper.get_hk_stock_data(code)
        if data:
            print(f"✅ 成功: {data['name']} - {data['price']} (来源: {data['source']})")
        else:
            print("❌ 失败")
        time.sleep(2)
    
    print("\n=== 测试高级美股数据抓取 ===")
    us_stocks = ['AAPL', 'GOOGL', 'TSLA', 'MSFT']  # 苹果、谷歌、特斯拉、微软
    for symbol in us_stocks:
        print(f"\n测试美股 {symbol}:")
        data = scraper.get_us_stock_data(symbol)
        if data:
            print(f"✅ 成功: {data['name']} - {data['price']} (来源: {data['source']})")
        else:
            print("❌ 失败")
        time.sleep(2)

if __name__ == '__main__':
    test_advanced_scraper()