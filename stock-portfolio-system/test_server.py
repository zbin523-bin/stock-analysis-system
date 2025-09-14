#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import time
from flask import Flask, jsonify

app = Flask(__name__)

def get_hk_stock_data(code):
    """获取港股数据"""
    try:
        # 腾讯财经港股API
        hk_code = f"hk{code}"
        url = f"https://qt.gtimg.cn/q={hk_code}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 Safari/604.1',
            'Referer': 'https://stockapp.finance.qq.com/',
            'Accept': 'text/plain, */*; q=0.01',
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            content = response.text
            if '=' in content and '~' in content:
                data_part = content.split('=')[1].strip('";\n')
                fields = data_part.split('~')
                
                if len(fields) >= 10:
                    name = fields[1] if fields[1] else f"HK{code}"
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
                            'timestamp': int(time.time() * 1000),
                            'currency': 'HKD'
                        }
        
        return None
        
    except Exception as e:
        print(f"获取港股 {code} 失败: {e}")
        return None

@app.route('/api/test/hk/<code>')
def test_hk_stock(code):
    """测试港股数据"""
    data = get_hk_stock_data(code)
    if data:
        return jsonify({
            'success': True,
            'data': data,
            'message': f"成功获取 {data['name']}: {data['price']}"
        })
    else:
        return jsonify({
            'success': False,
            'error': f'无法获取港股 {code} 的数据'
        })

@app.route('/api/test/all')
def test_all():
    """测试所有股票"""
    results = {
        'A': {},
        'HK': {},
        'US': {}
    }
    
    # 测试A股
    a_stocks = ['600036', '000858', '300059']
    for code in a_stocks:
        results['A'][code] = f"测试中..."
        time.sleep(1)
    
    # 测试港股
    hk_stocks = ['0700', '0941', '0005']
    for code in hk_stocks:
        data = get_hk_stock_data(code)
        if data:
            results['HK'][code] = f"成功: {data['name']} - {data['price']}"
        else:
            results['HK'][code] = "失败"
        time.sleep(1)
    
    # 测试美股（暂时失败）
    us_stocks = ['AAPL', 'GOOGL', 'TSLA']
    for symbol in us_stocks:
        results['US'][symbol] = "网络限制"
    
    return jsonify(results)

if __name__ == '__main__':
    print("股票数据测试服务器启动中...")
    print("测试港股: http://localhost:5001/api/test/hk/0700")
    print("测试所有: http://localhost:5001/api/test/all")
    
    app.run(host='0.0.0.0', port=5001, debug=False)