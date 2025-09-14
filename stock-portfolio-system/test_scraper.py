#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试股票数据抓取功能
"""

import requests
import time
import re
from datetime import datetime
from typing import Dict, Optional, Union
from urllib.parse import quote
import random

class RealStockScraper:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        self.session.headers.update(self.headers)
        
    def get_a_stock_data(self, code: str) -> Optional[Dict]:
        """获取A股真实数据"""
        print(f"开始获取A股 {code} 的真实数据...")
        
        try:
            # 方法1: 新浪财经API (最可靠)
            data = self._scrape_sina_a(code)
            if data and data['price'] > 0:
                print(f"新浪财经API成功获取 {code}: {data['name']} - {data['price']}")
                return data
                
            # 方法2: 腾讯财经API
            data = self._scrape_tencent_a(code)
            if data and data['price'] > 0:
                print(f"腾讯财经API成功获取 {code}: {data['name']} - {data['price']}")
                return data
                
        except Exception as e:
            print(f"抓取A股 {code} 数据失败: {e}")
            
        print(f"所有方法都无法获取 {code} 的有效数据")
        return None
    
    def get_us_stock_data(self, symbol: str) -> Optional[Dict]:
        """获取美股真实数据"""
        print(f"开始获取美股 {symbol} 的真实数据...")
        
        try:
            # 方法1: Yahoo Finance API
            data = self._scrape_yahoo_finance(symbol)
            if data and data['price'] > 0:
                print(f"Yahoo Finance成功获取 {symbol}: {data['name']} - {data['price']}")
                return data
                
        except Exception as e:
            print(f"抓取美股 {symbol} 数据失败: {e}")
            
        print(f"所有方法都无法获取 {symbol} 的有效数据")
        return None
    
    def _scrape_sina_a(self, code: str) -> Optional[Dict]:
        """新浪财经API - A股数据抓取"""
        try:
            prefix = 'sh' if code.startswith('6') else 'sz'
            full_code = f"{prefix}{code}"
            url = f"https://hq.sinajs.cn/list={full_code}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 Safari/604.1',
                'Referer': f'https://finance.sina.com.cn/realstock/company/{full_code}/nc.shtml',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive'
            }
            
            response = self.session.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                content = response.text
                if '=' in content and ',' in content:
                    # 解析新浪数据格式
                    data_part = content.split('=')[1].strip('";\n')
                    fields = data_part.split(',')
                    
                    if len(fields) >= 10:
                        name = fields[0] if fields[0] else f"股票{code}"
                        price = float(fields[3]) if fields[3] and fields[3] != '0.000' else 0
                        change = float(fields[4]) if fields[4] and fields[4] != '0.000' else 0
                        change_percent = float(fields[5]) if fields[5] and fields[5] != '0.000' else 0
                        volume = int(fields[8]) if fields[8] and fields[8].isdigit() else 0
                        high = float(fields[6]) if fields[6] and fields[6] != '0.000' else 0
                        low = float(fields[7]) if fields[7] and fields[7] != '0.000' else 0
                        open_price = float(fields[1]) if fields[1] and fields[1] != '0.000' else 0
                        
                        if price > 0:
                            return {
                                'code': code,
                                'name': name,
                                'price': price,
                                'change': change,
                                'changePercent': change_percent,
                                'volume': volume,
                                'high': high,
                                'low': low,
                                'open': open_price,
                                'timestamp': int(time.time() * 1000)
                            }
                        
        except Exception as e:
            print(f"新浪财经API抓取失败: {e}")
            
        return None
    
    def _scrape_tencent_a(self, code: str) -> Optional[Dict]:
        """腾讯财经API - A股数据抓取"""
        try:
            url = f"https://qt.gtimg.cn/q={code}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Referer': 'https://stockapp.finance.qq.com/',
                'Accept': 'text/plain, */*; q=0.01',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
            }
            
            response = self.session.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                content = response.text
                if '=' in content and '~' in content:
                    # 解析腾讯数据格式
                    data_part = content.split('=')[1].strip('";\n')
                    fields = data_part.split('~')
                    
                    if len(fields) >= 10:
                        name = fields[1] if fields[1] else f"股票{code}"
                        price = float(fields[3]) if fields[3] and fields[3] != '0.00' else 0
                        change = float(fields[4]) if fields[4] and fields[4] != '0.00' else 0
                        change_percent = float(fields[5]) if fields[5] and fields[5] != '0.00' else 0
                        volume = int(fields[6]) if fields[6] and fields[6].isdigit() else 0
                        high = float(fields[8]) if fields[8] and fields[8] != '0.00' else 0
                        low = float(fields[9]) if fields[9] and fields[9] != '0.00' else 0
                        open_price = float(fields[2]) if fields[2] and fields[2] != '0.00' else 0
                        
                        if price > 0:
                            return {
                                'code': code,
                                'name': name,
                                'price': price,
                                'change': change,
                                'changePercent': change_percent,
                                'volume': volume,
                                'high': high,
                                'low': low,
                                'open': open_price,
                                'timestamp': int(time.time() * 1000)
                            }
                        
        except Exception as e:
            print(f"腾讯财经API抓取失败: {e}")
            
        return None
    
    def _scrape_yahoo_finance(self, symbol: str) -> Optional[Dict]:
        """Yahoo Finance API - 美股数据抓取"""
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': f'https://finance.yahoo.com/quote/{symbol}',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            response = self.session.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('chart') and data['chart'].get('result') and len(data['chart']['result']) > 0:
                    result = data['chart']['result'][0]
                    meta = result.get('meta')
                    
                    if meta and meta.get('regularMarketPrice'):
                        current_price = meta.get('regularMarketPrice', 0)
                        previous_close = meta.get('previousClose', current_price)
                        change = current_price - previous_close
                        change_percent = (change / previous_close * 100) if previous_close > 0 else 0
                        
                        if current_price > 0:
                            return {
                                'symbol': symbol,
                                'name': meta.get('longName', meta.get('shortName', symbol)),
                                'price': current_price,
                                'change': change,
                                'changePercent': change_percent,
                                'volume': meta.get('regularMarketVolume', 0),
                                'high': meta.get('high', 0),
                                'low': meta.get('low', 0),
                                'open': meta.get('open', 0),
                                'timestamp': int(time.time() * 1000)
                            }
                        
        except Exception as e:
            print(f"Yahoo Finance抓取失败: {e}")
            
        return None

def test_stock_data():
    print("=== 测试股票数据抓取功能 ===\n")
    
    scraper = RealStockScraper()
    
    # 测试A股数据
    print("1. 测试A股数据抓取")
    a_stocks = ['600036', '000858', '300059']
    
    for code in a_stocks:
        print(f"\n正在获取 {code}...")
        data = scraper.get_a_stock_data(code)
        if data:
            print(f"✅ 成功: {data['name']} - 价格: {data['price']} - 涨跌: {data['change']} ({data['changePercent']}%)")
        else:
            print(f"❌ 失败: 无法获取 {code} 的数据")
        time.sleep(2)
    
    print("\n" + "="*50)
    
    # 测试美股数据
    print("2. 测试美股数据抓取")
    us_stocks = ['AAPL', 'TSLA', 'GOOGL']
    
    for symbol in us_stocks:
        print(f"\n正在获取 {symbol}...")
        data = scraper.get_us_stock_data(symbol)
        if data:
            print(f"✅ 成功: {data['name']} - 价格: {data['price']} - 涨跌: {data['change']} ({data['changePercent']}%)")
        else:
            print(f"❌ 失败: 无法获取 {symbol} 的数据")
        time.sleep(2)
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_stock_data()