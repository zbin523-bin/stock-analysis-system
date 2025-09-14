#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import time

def get_stock_price(code, name, market='A'):
    print(f"正在获取 {name} ({code})...")
    
    try:
        if market == 'A':
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
                        price = float(fields[3]) if fields[3] and fields[3] != '0.000' else 0
                        change = float(fields[4]) if fields[4] and fields[4] != '0.000' else 0
                        change_percent = float(fields[5]) if fields[5] and fields[5] != '0.000' else 0
                        
                        if price > 0:
                            print(f"成功: {name}: {price}元 ({change:+.2f}, {change_percent:+.2f}%)")
                            return price
        
        elif market == 'US':
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{code}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
                'Referer': f'https://finance.yahoo.com/quote/{code}',
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
                            print(f"成功: {name}: ${current_price:.2f} ({change:+.2f}, {change_percent:+.2f}%)")
                            return current_price
        
        print(f"失败: {name}: 获取失败")
        return None
        
    except Exception as e:
        print(f"失败: {name}: 错误 - {e}")
        return None

print("=== 最新股价查询 ===\n")

# 要查询的股票列表
stocks = [
    ('GOOGL', '谷歌', 'US'),
    ('601318', '中国平安', 'A'),
    ('600900', '长江电力', 'A'),
    ('AAPL', '苹果', 'US'),
    ('0700', '腾讯控股', 'HK'),  # 港股
    ('601899', '紫金矿业', 'A')
]

for code, name, market in stocks:
    get_stock_price(code, name, market)
    time.sleep(2)

print("\n=== 查询完成 ===")