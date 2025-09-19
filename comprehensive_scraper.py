#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import re
import json
import time
from datetime import datetime
from typing import Dict, Optional, List

class ComprehensiveStockScraper:
    """综合股票数据抓取器 - 支持港股、美股、A股"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        })
        
    def get_hk_stock_data(self, code: str) -> Optional[Dict]:
        """获取港股数据 - 多源尝试"""
        # 按优先级尝试不同的数据源
        sources = [
            self._get_hk_from_tencent,
            self._get_hk_from_sina,
            self._get_hk_from_yahoo,
            self._get_hk_from_google_finance,
        ]
        
        for source_func in sources:
            try:
                data = source_func(code)
                if data and data.get('price', 0) > 0:
                    print(f"OK 港股 {code} 数据获取成功: {data['name']} - {data['price']}")
                    return data
            except Exception as e:
                print(f"ERROR 港股 {code} 数据源失败: {source_func.__name__}: {e}")
                continue
        
        print(f"ERROR 港股 {code} 所有数据源都失败")
        return None
    
    def _get_hk_from_tencent(self, code: str) -> Optional[Dict]:
        """从腾讯财经获取港股数据"""
        try:
            # 多种腾讯API格式尝试
            urls = [
                f'https://qt.gtimg.cn/q=hk{code}',
                f'https://qt.gtimg.cn/q=r_hk{code}',
                f'https://qt.gtimg.cn/q=s_hk{code}',
            ]
            
            headers = {
                'Referer': 'https://finance.qq.com/',
                'Accept': '*/*',
            }
            
            for url in urls:
                try:
                    response = self.session.get(url, headers=headers, timeout=5)
                    if response.status_code == 200:
                        content = response.text
                        if '~' in content and not 'pv_none_match' in content:
                            data_part = content.split('~')
                            if len(data_part) > 6:
                                name = data_part[1] if data_part[1] else f'HK{code}'
                                price = float(data_part[3]) if data_part[3] and data_part[3] != '0.00' else 0
                                change = float(data_part[4]) if data_part[4] and data_part[4] != '0.00' else 0
                                change_percent = float(data_part[5]) if data_part[5] and data_part[5] != '0.00' else 0
                                volume = int(data_part[6]) if data_part[6] and data_part[6].isdigit() else 0
                                
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
            print(f"腾讯财经港股 {code} 失败: {e}")
        
        return None
    
    def _get_hk_from_sina(self, code: str) -> Optional[Dict]:
        """从新浪财经获取港股数据"""
        try:
            urls = [
                f'https://hq.sinajs.cn/?list=rt_hk{code}',
                f'https://hq.sinajs.cn/?list=hk{code}',
            ]
            
            headers = {
                'Referer': 'https://finance.sina.com.cn/',
                'Accept': '*/*',
            }
            
            for url in urls:
                response = self.session.get(url, headers=headers, timeout=5)
                if response.status_code == 200:
                    content = response.text
                    if '=' in content and '"' in content:
                        data_part = content.split('=')[1].strip('";\n')
                        fields = data_part.split(',')
                        
                        if len(fields) >= 10:
                            name = fields[6] if fields[6] else f'HK{code}'
                            price = float(fields[3]) if fields[3] and fields[3] != '0.00' else 0
                            change = float(fields[4]) if fields[4] and fields[4] != '0.00' else 0
                            change_percent = float(fields[5]) if fields[5] and fields[5] != '0.00' else 0
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
        except Exception as e:
            print(f"新浪财经港股 {code} 失败: {e}")
        
        return None
    
    def _get_hk_from_yahoo(self, code: str) -> Optional[Dict]:
        """从Yahoo Finance获取港股数据"""
        try:
            symbol = f'{code}.HK'
            url = f'https://query1.finance.yahoo.com/v8/finance/chart/{symbol}'
            
            headers = {
                'Referer': f'https://finance.yahoo.com/quote/{symbol}',
                'Accept': 'application/json',
            }
            
            response = self.session.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                chart = data.get('chart', {}).get('result', [])
                if chart:
                    result = chart[0]
                    meta = result.get('meta', {})
                    price = meta.get('regularMarketPrice', 0)
                    
                    if price > 0:
                        return {
                            'code': code,
                            'name': meta.get('longName', f'HK{code}'),
                            'price': price,
                            'change': meta.get('regularMarketPrice', 0) - meta.get('previousClose', price),
                            'changePercent': 0,  # 需要计算
                            'volume': meta.get('regularMarketVolume', 0),
                            'timestamp': int(time.time() * 1000),
                            'currency': 'HKD',
                            'source': 'yahoo'
                        }
        except Exception as e:
            print(f"Yahoo Finance港股 {code} 失败: {e}")
        
        return None
    
    def _get_hk_from_google_finance(self, code: str) -> Optional[Dict]:
        """从Google Finance获取港股数据"""
        try:
            symbol = f'HKG:{code}'
            url = f'https://www.google.com/finance/quote/{symbol}'
            
            response = self.session.get(url, timeout=5)
            if response.status_code == 200:
                content = response.text
                
                # 使用正则表达式提取数据
                price_pattern = r'data-last-price=\"([0-9.]+)\"'
                name_pattern = r'data-name=\"([^\"]+)\"'
                
                price_match = re.search(price_pattern, content)
                name_match = re.search(name_pattern, content)
                
                if price_match:
                    price = float(price_match.group(1))
                    name = name_match.group(1) if name_match else f'HK{code}'
                    
                    return {
                        'code': code,
                        'name': name,
                        'price': price,
                        'change': 0,
                        'changePercent': 0,
                        'volume': 0,
                        'timestamp': int(time.time() * 1000),
                        'currency': 'HKD',
                        'source': 'google'
                    }
        except Exception as e:
            print(f"Google Finance港股 {code} 失败: {e}")
        
        return None
    
    def get_us_stock_data(self, symbol: str) -> Optional[Dict]:
        """获取美股数据 - 多源尝试"""
        sources = [
            self._get_us_from_yahoo,
            self._get_us_from_alpha_vantage,
            self._get_us_from_iex_cloud,
            self._get_us_from_google_finance,
        ]
        
        for source_func in sources:
            try:
                data = source_func(symbol)
                if data and data.get('price', 0) > 0:
                    print(f"✅ 美股 {symbol} 数据获取成功: {data['name']} - {data['price']}")
                    return data
            except Exception as e:
                print(f"❌ 美股 {symbol} 数据源失败: {source_func.__name__}: {e}")
                continue
        
        print(f"❌ 美股 {symbol} 所有数据源都失败")
        return None
    
    def _get_us_from_yahoo(self, symbol: str) -> Optional[Dict]:
        """从Yahoo Finance获取美股数据"""
        try:
            url = f'https://query1.finance.yahoo.com/v8/finance/chart/{symbol}'
            
            headers = {
                'Referer': f'https://finance.yahoo.com/quote/{symbol}',
                'Accept': 'application/json',
            }
            
            response = self.session.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                chart = data.get('chart', {}).get('result', [])
                if chart:
                    result = chart[0]
                    meta = result.get('meta', {})
                    price = meta.get('regularMarketPrice', 0)
                    
                    if price > 0:
                        return {
                            'code': symbol,
                            'name': meta.get('longName', symbol),
                            'price': price,
                            'change': meta.get('regularMarketPrice', 0) - meta.get('previousClose', price),
                            'changePercent': 0,
                            'volume': meta.get('regularMarketVolume', 0),
                            'timestamp': int(time.time() * 1000),
                            'currency': 'USD',
                            'source': 'yahoo'
                        }
        except Exception as e:
            print(f"Yahoo Finance美股 {symbol} 失败: {e}")
        
        return None
    
    def _get_us_from_alpha_vantage(self, symbol: str) -> Optional[Dict]:
        """从Alpha Vantage获取美股数据"""
        try:
            # 使用免费的Alpha Vantage API
            url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey=demo'
            
            response = self.session.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                quote = data.get('Global Quote', {})
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
        except Exception as e:
            print(f"Alpha Vantage美股 {symbol} 失败: {e}")
        
        return None
    
    def _get_us_from_iex_cloud(self, symbol: str) -> Optional[Dict]:
        """从IEX Cloud获取美股数据"""
        try:
            # 使用IEX Cloud的测试API
            url = f'https://cloud.iexapis.com/stable/stock/{symbol}/quote?token=Tpk_1234567890'
            
            response = self.session.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
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
        except Exception as e:
            print(f"IEX Cloud美股 {symbol} 失败: {e}")
        
        return None
    
    def _get_us_from_google_finance(self, symbol: str) -> Optional[Dict]:
        """从Google Finance获取美股数据"""
        try:
            url = f'https://www.google.com/finance/quote/{symbol}:NASDAQ'
            
            response = self.session.get(url, timeout=5)
            if response.status_code == 200:
                content = response.text
                
                # 使用正则表达式提取数据
                price_pattern = r'data-last-price=\"([0-9.]+)\"'
                name_pattern = r'data-name=\"([^\"]+)\"'
                
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
                        'source': 'google'
                    }
        except Exception as e:
            print(f"Google Finance美股 {symbol} 失败: {e}")
        
        return None
    
    def get_fund_data(self, fund_code: str) -> Optional[Dict]:
        """获取基金数据"""
        try:
            # 从天天基金获取数据
            url = f'https://fund.eastmoney.com/{fund_code}.html'
            
            response = self.session.get(url, timeout=5)
            if response.status_code == 200:
                content = response.text
                
                # 使用正则表达式提取基金数据
                name_pattern = r'<title>([^<]+)</title>'
                price_pattern = r'\"dzjz\">([0-9.]+)</span>'
                
                name_match = re.search(name_pattern, content)
                price_match = re.search(price_pattern, content)
                
                if name_match and price_match:
                    name = name_match.group(1).replace(' - 天天基金网', '')
                    price = float(price_match.group(1))
                    
                    return {
                        'code': fund_code,
                        'name': name,
                        'price': price,
                        'change': 0,
                        'changePercent': 0,
                        'volume': 0,
                        'timestamp': int(time.time() * 1000),
                        'currency': 'CNY',
                        'source': 'eastmoney'
                    }
        except Exception as e:
            print(f"基金 {fund_code} 数据获取失败: {e}")
        
        return None

# 测试函数
def test_scraper():
    """测试抓取器"""
    scraper = ComprehensiveStockScraper()
    
    # 测试港股
    print("=== 测试港股数据 ===")
    hk_stocks = ['0700', '0941', '0005']  # 腾讯、中国移动、汇丰
    for code in hk_stocks:
        data = scraper.get_hk_stock_data(code)
        print(f"港股 {code}: {data}")
        time.sleep(1)
    
    # 测试美股
    print("\n=== 测试美股数据 ===")
    us_stocks = ['AAPL', 'GOOGL', 'TSLA']  # 苹果、谷歌、特斯拉
    for symbol in us_stocks:
        data = scraper.get_us_stock_data(symbol)
        print(f"美股 {symbol}: {data}")
        time.sleep(1)
    
    # 测试基金
    print("\n=== 测试基金数据 ===")
    funds = ['000001', '110011', '161725']  # 华夏成长、易方达中小盘、招商中证白酒
    for fund_code in funds:
        data = scraper.get_fund_data(fund_code)
        print(f"基金 {fund_code}: {data}")
        time.sleep(1)

if __name__ == '__main__':
    test_scraper()