#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整的股票投资组合管理系统 - 本地演示版
支持A股、港股、美股实时数据
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import time
import os
import logging
from datetime import datetime
import requests

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# 配置
CACHE_DURATION = int(os.getenv('CACHE_DURATION', '30000'))  # 30秒缓存
stock_cache = {}

class CompleteStockScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 Safari/604.1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'
        })
    
    def get_a_stock_data(self, code):
        """获取A股真实数据"""
        cache_key = f"a_{code}"
        cached = stock_cache.get(cache_key)
        
        if cached and time.time() * 1000 - cached['timestamp'] < CACHE_DURATION:
            return cached['data']
        
        try:
            # 新浪财经API (最可靠)
            data = self._scrape_sina_a(code)
            if data and data.get('price', 0) > 0:
                stock_cache[cache_key] = {'data': data, 'timestamp': int(time.time() * 1000)}
                logger.info(f"成功获取A股 {code}: {data['name']} - {data['price']}")
                return data
                
            # 腾讯财经API (备用)
            data = self._scrape_tencent_a(code)
            if data and data.get('price', 0) > 0:
                stock_cache[cache_key] = {'data': data, 'timestamp': int(time.time() * 1000)}
                logger.info(f"成功获取A股 {code}: {data['name']} - {data['price']}")
                return data
                
        except Exception as e:
            logger.error(f"获取A股 {code} 失败: {e}")
        
        return None
    
    def get_hk_stock_data(self, code):
        """获取港股数据"""
        cache_key = f"hk_{code}"
        cached = stock_cache.get(cache_key)
        
        if cached and time.time() * 1000 - cached['timestamp'] < CACHE_DURATION:
            return cached['data']
        
        try:
            # 腾讯财经港股API
            data = self._scrape_tencent_hk(code)
            if data and data.get('price', 0) > 0:
                stock_cache[cache_key] = {'data': data, 'timestamp': int(time.time() * 1000)}
                logger.info(f"成功获取港股 {code}: {data['name']} - {data['price']}")
                return data
                
        except Exception as e:
            logger.error(f"获取港股 {code} 失败: {e}")
        
        return None
    
    def get_us_stock_data(self, symbol):
        """获取美股数据"""
        cache_key = f"us_{symbol}"
        cached = stock_cache.get(cache_key)
        
        if cached and time.time() * 1000 - cached['timestamp'] < CACHE_DURATION:
            return cached['data']
        
        try:
            # Yahoo Finance API
            data = self._scrape_yahoo_finance(symbol)
            if data and data.get('price', 0) > 0:
                stock_cache[cache_key] = {'data': data, 'timestamp': int(time.time() * 1000)}
                logger.info(f"成功获取美股 {symbol}: {data['name']} - {data['price']}")
                return data
                
        except Exception as e:
            logger.error(f"获取美股 {symbol} 失败: {e}")
        
        return None
    
    def _scrape_sina_a(self, code):
        """新浪财经API - A股"""
        try:
            prefix = 'sh' if code.startswith('6') else 'sz'
            full_code = f"{prefix}{code}"
            url = f"https://hq.sinajs.cn/list={full_code}"
            
            headers = {
                'Referer': f'https://finance.sina.com.cn/realstock/company/{full_code}/nc.shtml',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            }
            
            response = self.session.get(url, headers=headers, timeout=10)
            
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
                                'timestamp': int(time.time() * 1000),
                                'currency': 'CNY'
                            }
                        
        except Exception as e:
            logger.error(f"新浪财经API失败: {e}")
        
        return None
    
    def _scrape_tencent_a(self, code):
        """腾讯财经API - A股"""
        try:
            url = f"https://qt.gtimg.cn/q={code}"
            
            headers = {
                'Referer': 'https://stockapp.finance.qq.com/',
                'Accept': 'text/plain, */*; q=0.01',
            }
            
            response = self.session.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                content = response.text
                if '=' in content and '~' in content:
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
                                'timestamp': int(time.time() * 1000),
                                'currency': 'CNY'
                            }
                        
        except Exception as e:
            logger.error(f"腾讯财经API失败: {e}")
        
        return None
    
    def _scrape_tencent_hk(self, code):
        """腾讯财经API - 港股"""
        try:
            hk_code = f"hk{code}"
            url = f"https://qt.gtimg.cn/q={hk_code}"
            
            headers = {
                'Referer': 'https://stockapp.finance.qq.com/',
                'Accept': 'text/plain, */*; q=0.01',
            }
            
            response = self.session.get(url, headers=headers, timeout=10)
            
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
                        
        except Exception as e:
            logger.error(f"腾讯财经港股API失败: {e}")
        
        return None
    
    def _scrape_yahoo_finance(self, symbol):
        """Yahoo Finance API - 美股"""
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
            
            headers = {
                'Referer': f'https://finance.yahoo.com/quote/{symbol}',
                'Accept-Language': 'en-US,en;q=0.9',
            }
            
            response = self.session.get(url, headers=headers, timeout=10)
            
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
                                'timestamp': int(time.time() * 1000),
                                'currency': 'USD'
                            }
                        
        except Exception as e:
            logger.error(f"Yahoo Finance失败: {e}")
        
        return None

# 初始化抓取器
scraper = CompleteStockScraper()

# 完整的投资组合数据
portfolio_data = {
    "positions": [
        {
            "id": 1,
            "code": "600036",
            "name": "招商银行",
            "market": "A股",
            "industry": "银行",
            "quantity": 100,
            "costPrice": 38.70,
            "currency": "CNY"
        },
        {
            "id": 2,
            "code": "000858",
            "name": "五粮液",
            "market": "A股",
            "industry": "白酒",
            "quantity": 50,
            "costPrice": 165.80,
            "currency": "CNY"
        },
        {
            "id": 3,
            "code": "300059",
            "name": "东方财富",
            "market": "A股",
            "industry": "互联网金融",
            "quantity": 200,
            "costPrice": 18.90,
            "currency": "CNY"
        },
        {
            "id": 4,
            "code": "601318",
            "name": "中国平安",
            "market": "A股",
            "industry": "保险",
            "quantity": 80,
            "costPrice": 45.00,
            "currency": "CNY"
        },
        {
            "id": 5,
            "code": "600900",
            "name": "长江电力",
            "market": "A股",
            "industry": "电力",
            "quantity": 60,
            "costPrice": 22.50,
            "currency": "CNY"
        },
        {
            "id": 6,
            "code": "601899",
            "name": "紫金矿业",
            "market": "A股",
            "industry": "矿业",
            "quantity": 150,
            "costPrice": 12.80,
            "currency": "CNY"
        },
        {
            "id": 101,
            "code": "0700",
            "name": "腾讯控股",
            "market": "港股",
            "industry": "科技",
            "quantity": 30,
            "costPrice": 320.00,
            "currency": "HKD"
        },
        {
            "id": 102,
            "code": "0941",
            "name": "中国移动",
            "market": "港股",
            "industry": "电信",
            "quantity": 50,
            "costPrice": 45.00,
            "currency": "HKD"
        },
        {
            "id": 103,
            "code": "0005",
            "name": "汇丰控股",
            "market": "港股",
            "industry": "银行",
            "quantity": 40,
            "costPrice": 55.00,
            "currency": "HKD"
        },
        {
            "id": 201,
            "code": "AAPL",
            "name": "Apple Inc.",
            "market": "美股",
            "industry": "科技",
            "quantity": 30,
            "costPrice": 150.00,
            "currency": "USD"
        },
        {
            "id": 202,
            "code": "GOOGL",
            "name": "Alphabet Inc.",
            "market": "美股",
            "industry": "科技",
            "quantity": 20,
            "costPrice": 120.00,
            "currency": "USD"
        },
        {
            "id": 203,
            "code": "TSLA",
            "name": "Tesla Inc.",
            "market": "美股",
            "industry": "汽车",
            "quantity": 15,
            "costPrice": 200.00,
            "currency": "USD"
        }
    ],
    "totalCash": 100000
}

@app.route('/api/health')
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'ok',
        'timestamp': int(time.time() * 1000),
        'cache_size': len(stock_cache),
        'version': '3.0.0'
    })

@app.route('/api/stock/a/<code>')
def get_a_stock(code):
    """获取A股数据"""
    try:
        data = scraper.get_a_stock_data(code)
        if data:
            return jsonify({
                'success': True,
                'data': data,
                'timestamp': int(time.time() * 1000)
            })
        else:
            return jsonify({
                'success': False,
                'error': '无法获取数据',
                'timestamp': int(time.time() * 1000)
            })
    except Exception as e:
        logger.error(f"获取A股 {code} 异常: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': int(time.time() * 1000)
        })

@app.route('/api/stock/hk/<code>')
def get_hk_stock(code):
    """获取港股数据"""
    try:
        data = scraper.get_hk_stock_data(code)
        if data:
            return jsonify({
                'success': True,
                'data': data,
                'timestamp': int(time.time() * 1000)
            })
        else:
            return jsonify({
                'success': False,
                'error': '无法获取数据',
                'timestamp': int(time.time() * 1000)
            })
    except Exception as e:
        logger.error(f"获取港股 {code} 异常: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': int(time.time() * 1000)
        })

@app.route('/api/stock/us/<symbol>')
def get_us_stock(symbol):
    """获取美股数据"""
    try:
        data = scraper.get_us_stock_data(symbol)
        if data:
            return jsonify({
                'success': True,
                'data': data,
                'timestamp': int(time.time() * 1000)
            })
        else:
            return jsonify({
                'success': False,
                'error': '无法获取数据',
                'timestamp': int(time.time() * 1000)
            })
    except Exception as e:
        logger.error(f"获取美股 {symbol} 异常: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': int(time.time() * 1000)
        })

@app.route('/api/portfolio')
def get_portfolio():
    """获取投资组合数据"""
    try:
        enriched_positions = []
        total_value = 0
        total_profit = 0
        
        for position in portfolio_data["positions"]:
            # 获取实时价格
            real_time_data = None
            if position["market"] == "A股":
                real_time_data = scraper.get_a_stock_data(position["code"])
            elif position["market"] == "港股":
                real_time_data = scraper.get_hk_stock_data(position["code"])
            elif position["market"] == "美股":
                real_time_data = scraper.get_us_stock_data(position["code"])
            
            if real_time_data:
                current_price = real_time_data.get('price', position["costPrice"])
                change = real_time_data.get('change', 0)
                change_percent = real_time_data.get('changePercent', 0)
                has_real_time_data = True
            else:
                current_price = position["costPrice"]
                change = 0
                change_percent = 0
                has_real_time_data = False
            
            market_value = position["quantity"] * current_price
            profit = market_value - (position["quantity"] * position["costPrice"])
            profit_rate = (profit / (position["quantity"] * position["costPrice"])) * 100 if position["costPrice"] > 0 else 0
            
            total_value += market_value
            total_profit += profit
            
            enriched_position = {
                **position,
                "currentPrice": current_price,
                "marketValue": market_value,
                "profit": profit,
                "profitRate": profit_rate,
                "change": change,
                "changePercent": change_percent,
                "hasRealTimeData": has_real_time_data
            }
            
            enriched_positions.append(enriched_position)
        
        summary = {
            "totalValue": total_value,
            "totalProfit": total_profit,
            "totalProfitPercent": (total_profit / (total_value - total_profit)) * 100 if (total_value - total_profit) > 0 else 0,
            "cashBalance": portfolio_data["totalCash"],
            "totalAssets": total_value + portfolio_data["totalCash"]
        }
        
        return jsonify({
            "success": True,
            "positions": enriched_positions,
            "summary": summary,
            "lastUpdate": int(time.time() * 1000)
        })
        
    except Exception as e:
        logger.error(f"获取投资组合数据异常: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": int(time.time() * 1000)
        })

@app.route('/api/clear-cache', methods=['POST'])
def clear_cache():
    """清除缓存"""
    try:
        stock_cache.clear()
        logger.info("缓存已清除")
        
        return jsonify({
            "success": True,
            "message": "缓存已清除",
            "timestamp": int(time.time() * 1000)
        })
    except Exception as e:
        logger.error(f"清除缓存异常: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": int(time.time() * 1000)
        })

@app.route('/')
def index():
    """主页 - 重定向到前端"""
    return """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="refresh" content="0; url=/web">
        <title>股票投资组合管理系统</title>
    </head>
    <body>
        <p>正在跳转到股票投资组合管理系统...</p>
    </body>
    </html>
    """

@app.route('/web')
def web_interface():
    """完整的前端界面"""
    return """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>股票投资组合管理系统</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            
            .container {
                max-width: 1400px;
                margin: 0 auto;
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                overflow: hidden;
            }
            
            .header {
                background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }
            
            .header h1 {
                font-size: 2.5em;
                margin-bottom: 10px;
                font-weight: 700;
            }
            
            .header p {
                font-size: 1.2em;
                opacity: 0.9;
            }
            
            .status-bar {
                background: #f8f9fa;
                padding: 15px 30px;
                border-bottom: 1px solid #e9ecef;
                display: flex;
                justify-content: space-between;
                align-items: center;
                flex-wrap: wrap;
                gap: 10px;
            }
            
            .status-indicator {
                display: flex;
                align-items: center;
                gap: 8px;
            }
            
            .status-dot {
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background: #28a745;
            }
            
            .status-dot.error {
                background: #dc3545;
            }
            
            .status-dot.warning {
                background: #ffc107;
            }
            
            .controls {
                display: flex;
                gap: 10px;
                flex-wrap: wrap;
            }
            
            .btn {
                padding: 8px 16px;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                font-size: 14px;
                transition: all 0.3s ease;
            }
            
            .btn-primary {
                background: #007bff;
                color: white;
            }
            
            .btn-primary:hover {
                background: #0056b3;
            }
            
            .btn-secondary {
                background: #6c757d;
                color: white;
            }
            
            .btn-secondary:hover {
                background: #545b62;
            }
            
            .main-content {
                padding: 30px;
            }
            
            .summary-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            
            .summary-card {
                background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                padding: 20px;
                border-radius: 12px;
                text-align: center;
                border: 1px solid #dee2e6;
            }
            
            .summary-card h3 {
                color: #495057;
                font-size: 0.9em;
                margin-bottom: 8px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            .summary-card .value {
                font-size: 1.8em;
                font-weight: 700;
                margin-bottom: 5px;
            }
            
            .summary-card .change {
                font-size: 0.9em;
            }
            
            .positive {
                color: #28a745;
            }
            
            .negative {
                color: #dc3545;
            }
            
            .table-container {
                background: white;
                border-radius: 12px;
                overflow: hidden;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            
            .table {
                width: 100%;
                border-collapse: collapse;
            }
            
            .table th,
            .table td {
                padding: 12px 15px;
                text-align: left;
                border-bottom: 1px solid #e9ecef;
            }
            
            .table th {
                background: #f8f9fa;
                font-weight: 600;
                color: #495057;
                text-transform: uppercase;
                font-size: 0.85em;
                letter-spacing: 0.5px;
            }
            
            .table tbody tr:hover {
                background: #f8f9fa;
            }
            
            .table .error-row {
                background: #fff5f5;
                color: #721c24;
            }
            
            .table .error-row td {
                border-bottom: 1px solid #f5c6cb;
            }
            
            .error-badge {
                background: #dc3545;
                color: white;
                padding: 2px 8px;
                border-radius: 12px;
                font-size: 0.8em;
                margin-left: 8px;
            }
            
            .market-badge {
                background: #17a2b8;
                color: white;
                padding: 2px 6px;
                border-radius: 8px;
                font-size: 0.75em;
                margin-left: 4px;
            }
            
            .loading {
                text-align: center;
                padding: 40px;
                color: #6c757d;
            }
            
            .loading::after {
                content: '';
                display: inline-block;
                width: 20px;
                height: 20px;
                border: 2px solid #f3f3f3;
                border-top: 2px solid #3498db;
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin-left: 10px;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            .footer {
                background: #f8f9fa;
                padding: 20px 30px;
                text-align: center;
                color: #6c757d;
                border-top: 1px solid #e9ecef;
            }
            
            @media (max-width: 768px) {
                .container {
                    margin: 10px;
                    border-radius: 15px;
                }
                
                .header {
                    padding: 20px;
                }
                
                .header h1 {
                    font-size: 2em;
                }
                
                .main-content {
                    padding: 20px;
                }
                
                .status-bar {
                    padding: 15px 20px;
                }
                
                .table th,
                .table td {
                    padding: 8px 10px;
                    font-size: 0.9em;
                }
                
                .summary-card {
                    padding: 15px;
                }
                
                .summary-card .value {
                    font-size: 1.5em;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>股票投资组合管理系统</h1>
                <p>支持A股、港股、美股实时数据监控</p>
            </div>
            
            <div class="status-bar">
                <div class="status-indicator">
                    <div id="statusDot" class="status-dot"></div>
                    <span id="statusText">数据正常</span>
                </div>
                <div class="controls">
                    <button class="btn btn-primary" onclick="refreshData()">刷新数据</button>
                    <button class="btn btn-secondary" onclick="clearCache()">清除缓存</button>
                </div>
            </div>
            
            <div class="main-content">
                <div id="summary" class="summary-grid">
                    <div class="summary-card">
                        <h3>总资产</h3>
                        <div class="value" id="totalAssets">--</div>
                        <div class="change">CNY</div>
                    </div>
                    <div class="summary-card">
                        <h3>总市值</h3>
                        <div class="value" id="totalValue">--</div>
                        <div class="change">多币种</div>
                    </div>
                    <div class="summary-card">
                        <h3>总盈亏</h3>
                        <div class="value" id="totalProfit">--</div>
                        <div class="change" id="totalProfitPercent">--</div>
                    </div>
                    <div class="summary-card">
                        <h3>现金余额</h3>
                        <div class="value" id="cashBalance">--</div>
                        <div class="change">CNY</div>
                    </div>
                </div>
                
                <div class="table-container">
                    <table class="table">
                        <thead>
                            <tr>
                                <th>股票名称</th>
                                <th>代码</th>
                                <th>市场</th>
                                <th>当前价格</th>
                                <th>涨跌额</th>
                                <th>涨跌幅</th>
                                <th>持仓数量</th>
                                <th>市值</th>
                                <th>盈亏</th>
                                <th>盈亏比例</th>
                            </tr>
                        </thead>
                        <tbody id="portfolio">
                            <tr><td colspan="10" class="loading">加载中...</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
            
            <div class="footer">
                <p>&copy; 2024 股票投资组合管理系统 | 最后更新: <span id="lastUpdate">--</span> | 数据状态: <span id="dataCount">--</span></p>
            </div>
        </div>

        <script>
            const API_BASE = '';
            
            function formatNumber(num, decimals = 2) {
                if (isNaN(num) || num === null) return '--';
                return num.toFixed(decimals);
            }
            
            function formatCurrency(num, currency = 'CNY') {
                if (isNaN(num) || num === null) return '--';
                const symbols = { CNY: '¥', HKD: 'HK$', USD: '$' };
                return symbols[currency] + num.toFixed(2);
            }
            
            function formatPercent(num) {
                if (isNaN(num) || num === null) return '--';
                return num.toFixed(2) + '%';
            }
            
            function getChangeClass(change) {
                if (change > 0) return 'positive';
                if (change < 0) return 'negative';
                return '';
            }
            
            function getMarketBadge(market) {
                const colors = { 'A股': '#28a745', '港股': '#ffc107', '美股': '#dc3545' };
                return `<span class="market-badge" style="background: ${colors[market]}">${market}</span>`;
            }
            
            async function loadPortfolio() {
                try {
                    const response = await fetch('/api/portfolio');
                    const data = await response.json();
                    
                    if (data.success) {
                        renderPortfolio(data);
                        updateStatus(data.positions);
                        updateLastUpdate(data.lastUpdate);
                    } else {
                        document.getElementById('portfolio').innerHTML = 
                            '<tr><td colspan="10" style="text-align: center; color: red;">加载失败: ' + data.error + '</td></tr>';
                    }
                } catch (error) {
                    document.getElementById('portfolio').innerHTML = 
                        '<tr><td colspan="10" style="text-align: center; color: red;">网络错误</td></tr>';
                }
            }
            
            function renderPortfolio(data) {
                // 渲染汇总
                const summary = data.summary;
                document.getElementById('totalAssets').textContent = formatCurrency(summary.totalAssets);
                document.getElementById('totalValue').textContent = formatCurrency(summary.totalValue);
                document.getElementById('totalProfit').textContent = formatCurrency(summary.totalProfit);
                document.getElementById('totalProfit').textContent = formatCurrency(summary.totalProfit);
                document.getElementById('totalProfit').className = 'value ' + getChangeClass(summary.totalProfit);
                document.getElementById('totalProfitPercent').textContent = formatPercent(summary.totalProfitPercent);
                document.getElementById('totalProfitPercent').className = 'change ' + getChangeClass(summary.totalProfit);
                document.getElementById('cashBalance').textContent = formatCurrency(summary.cashBalance);
                
                // 渲染持仓
                const portfolio = data.positions;
                const tbody = document.getElementById('portfolio');
                
                tbody.innerHTML = portfolio.map(pos => {
                    if (!pos.hasRealTimeData) {
                        return `
                            <tr class="error-row">
                                <td>${pos.name}</td>
                                <td>${pos.code}</td>
                                <td>${getMarketBadge(pos.market)}</td>
                                <td>--</td>
                                <td>--</td>
                                <td>--</td>
                                <td>${pos.quantity}</td>
                                <td>--</td>
                                <td>--</td>
                                <td>--</td>
                            </tr>
                        `;
                    }
                    
                    return `
                        <tr>
                            <td>${pos.name}</td>
                            <td>${pos.code}</td>
                            <td>${getMarketBadge(pos.market)}</td>
                            <td>${formatCurrency(pos.currentPrice, pos.currency)}</td>
                            <td class="${getChangeClass(pos.change)}">${formatCurrency(pos.change, pos.currency)}</td>
                            <td class="${getChangeClass(pos.changePercent)}">${formatPercent(pos.changePercent)}</td>
                            <td>${pos.quantity}</td>
                            <td>${formatCurrency(pos.marketValue, pos.currency)}</td>
                            <td class="${getChangeClass(pos.profit)}">${formatCurrency(pos.profit, pos.currency)}</td>
                            <td class="${getChangeClass(pos.profitRate)}">${formatPercent(pos.profitRate)}</td>
                        </tr>
                    `;
                }).join('');
            }
            
            function updateStatus(positions) {
                const statusDot = document.getElementById('statusDot');
                const statusText = document.getElementById('statusText');
                const dataCount = document.getElementById('dataCount');
                
                if (!positions || positions.length === 0) {
                    statusDot.className = 'status-dot error';
                    statusText.textContent = '数据加载失败';
                    dataCount.textContent = '0/0';
                    return;
                }
                
                const realTimeCount = positions.filter(p => p.hasRealTimeData).length;
                const totalCount = positions.length;
                
                dataCount.textContent = `${realTimeCount}/${totalCount}`;
                
                if (realTimeCount === 0) {
                    statusDot.className = 'status-dot error';
                    statusText.textContent = '数据获取失败';
                } else if (realTimeCount < totalCount) {
                    statusDot.className = 'status-dot warning';
                    statusText.textContent = '部分数据异常';
                } else {
                    statusDot.className = 'status-dot';
                    statusText.textContent = '数据正常';
                }
            }
            
            function updateLastUpdate(timestamp) {
                const lastUpdate = new Date(timestamp);
                document.getElementById('lastUpdate').textContent = lastUpdate.toLocaleString();
            }
            
            async function refreshData() {
                try {
                    await fetch('/api/clear-cache', { method: 'POST' });
                    await loadPortfolio();
                } catch (error) {
                    alert('刷新失败');
                }
            }
            
            async function clearCache() {
                try {
                    await fetch('/api/clear-cache', { method: 'POST' });
                    await loadPortfolio();
                } catch (error) {
                    alert('清除缓存失败');
                }
            }
            
            // 初始化
            loadPortfolio();
            setInterval(loadPortfolio, 30000);
        </script>
    </body>
    </html>
    """

if __name__ == '__main__':
    logger.info("完整股票投资组合管理系统启动中...")
    logger.info("访问 http://localhost:5000 查看系统")
    logger.info("支持功能:")
    logger.info("  - A股实时数据 (新浪财经 + 腾讯财经)")
    logger.info("  - 港股实时数据 (腾讯财经)")
    logger.info("  - 美股实时数据 (Yahoo Finance)")
    logger.info("  - 完整的投资组合管理")
    logger.info("  - 多币种支持 (CNY, HKD, USD)")
    
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)