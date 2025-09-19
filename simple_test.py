#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的股票数据测试
"""

import requests
import time
import json

def test_a_stock(code):
    """测试A股数据"""
    print(f"测试A股 {code}...")
    
    try:
        prefix = 'sh' if code.startswith('6') else 'sz'
        full_code = f"{prefix}{code}"
        url = f"https://hq.sinajs.cn/list={full_code}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 Safari/604.1',
            'Referer': f'https://finance.sina.com.cn/realstock/company/{full_code}/nc.shtml',
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            content = response.text
            if '=' in content and ',' in content:
                data_part = content.split('=')[1].strip('";\n')
                fields = data_part.split(',')
                
                if len(fields) >= 10:
                    name = fields[0] if fields[0] else f"股票{code}"
                    price = float(fields[3]) if fields[3] and fields[3] != '0.000' else 0
                    change = float(fields[4]) if fields[4] and fields[4] != '0.000' else 0
                    change_percent = float(fields[5]) if fields[5] and fields[5] != '0.000' else 0
                    
                    if price > 0:
                        print(f"成功: {name} - 价格: {price} - 涨跌: {change} ({change_percent}%)")
                        return {
                            'code': code,
                            'name': name,
                            'price': price,
                            'change': change,
                            'changePercent': change_percent,
                            'timestamp': int(time.time() * 1000)
                        }
        
        print(f"失败: 无法获取 {code} 的数据")
        return None
        
    except Exception as e:
        print(f"错误: {e}")
        return None

def test_us_stock(symbol):
    """测试美股数据"""
    print(f"测试美股 {symbol}...")
    
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
            'Referer': f'https://finance.yahoo.com/quote/{symbol}',
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
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
                        name = meta.get('longName', meta.get('shortName', symbol))
                        print(f"成功: {name} - 价格: {current_price} - 涨跌: {change} ({change_percent}%)")
                        return {
                            'symbol': symbol,
                            'name': name,
                            'price': current_price,
                            'change': change,
                            'changePercent': change_percent,
                            'timestamp': int(time.time() * 1000)
                        }
        
        print(f"失败: 无法获取 {symbol} 的数据")
        return None
        
    except Exception as e:
        print(f"错误: {e}")
        return None

def main():
    print("=== 股票数据抓取测试 ===\n")
    
    # 测试A股
    print("1. A股测试:")
    a_stocks = ['600036', '000858', '300059']
    for code in a_stocks:
        test_a_stock(code)
        time.sleep(2)
    
    print("\n2. 美股测试:")
    us_stocks = ['AAPL', 'TSLA', 'GOOGL']
    for symbol in us_stocks:
        test_us_stock(symbol)
        time.sleep(2)
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    main()