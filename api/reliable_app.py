#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票数据API服务 - 支持A股、港股、美股
专注提供可靠的股票数据
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

class ReliableStockScraper:
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
        """获取港股真实数据"""
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
                
            # 新浪财经港股API (备用)
            data = self._scrape_sina_hk(code)
            if data and data.get('price', 0) > 0:
                stock_cache[cache_key] = {'data': data, 'timestamp': int(time.time() * 1000)}
                logger.info(f"成功获取港股 {code}: {data['name']} - {data['price']}")
                return data
                
        except Exception as e:
            logger.error(f"获取港股 {code} 失败: {e}")
        
        return None
    
    def get_us_stock_data(self, symbol):
        """获取美股真实数据"""
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
    
    def _scrape_sina_hk(self, code):
        """新浪财经API - 港股"""
        try:
            hk_code = f"rt_hk{code}"
            url = f"https://hq.sinajs.cn/list={hk_code}"
            
            headers = {
                'Referer': f'https://finance.sina.com.cn/hk/',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            }
            
            response = self.session.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                content = response.text
                if '=' in content and ',' in content:
                    data_part = content.split('=')[1].strip('";\n')
                    fields = data_part.split(',')
                    
                    if len(fields) >= 10:
                        name = fields[0] if fields[0] else f"HK{code}"
                        price = float(fields[6]) if fields[6] and fields[6] != '0.000' else 0
                        change = float(fields[7]) if fields[7] and fields[7] != '0.000' else 0
                        change_percent = float(fields[8]) if fields[8] and fields[8] != '0.000' else 0
                        volume = int(fields[10]) if fields[10] and fields[10].isdigit() else 0
                        high = float(fields[4]) if fields[4] and fields[4] != '0.000' else 0
                        low = float(fields[5]) if fields[5] and fields[5] != '0.000' else 0
                        open_price = float(fields[2]) if fields[2] and fields[2] != '0.000' else 0
                        
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
            logger.error(f"新浪财经港股API失败: {e}")
        
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
scraper = ReliableStockScraper()

# 模拟的投资组合数据 - 包含港股和美股
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
            "code": "0700",
            "name": "腾讯控股",
            "market": "港股",
            "industry": "科技",
            "quantity": 30,
            "costPrice": 320.00,
            "currency": "HKD"
        },
        {
            "id": 5,
            "code": "0941",
            "name": "中国移动",
            "market": "港股",
            "industry": "电信",
            "quantity": 50,
            "costPrice": 45.00,
            "currency": "HKD"
        },
        {
            "id": 101,
            "code": "AAPL",
            "name": "Apple Inc.",
            "market": "美股",
            "industry": "科技",
            "quantity": 30,
            "costPrice": 150.00,
            "currency": "USD"
        },
        {
            "id": 102,
            "code": "GOOGL",
            "name": "Alphabet Inc.",
            "market": "美股",
            "industry": "科技",
            "quantity": 20,
            "costPrice": 120.00,
            "currency": "USD"
        },
        {
            "id": 103,
            "code": "TSLA",
            "name": "Tesla Inc.",
            "market": "美股",
            "industry": "汽车",
            "quantity": 15,
            "costPrice": 200.00,
            "currency": "USD"
        }
    ],
    "totalCash": 50000
}

@app.route('/api/health')
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'ok',
        'timestamp': int(time.time() * 1000),
        'cache_size': len(stock_cache),
        'version': '2.0.0'
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
    """主页"""
    return """
    <html>
        <head>
            <title>股票投资组合管理系统 API</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .endpoint { margin: 10px 0; padding: 10px; background: #f5f5f5; border-radius: 5px; }
                .method { color: #007bff; font-weight: bold; }
            </style>
        </head>
        <body>
            <h1>股票投资组合管理系统 API</h1>
            <h2>可用接口：</h2>
            <div class="endpoint">
                <span class="method">GET</span> /api/health - 健康检查
            </div>
            <div class="endpoint">
                <span class="method">GET</span> /api/stock/a/&lt;code&gt; - 获取A股数据
            </div>
            <div class="endpoint">
                <span class="method">GET</span> /api/stock/hk/&lt;code&gt; - 获取港股数据
            </div>
            <div class="endpoint">
                <span class="method">GET</span> /api/stock/us/&lt;symbol&gt; - 获取美股数据
            </div>
            <div class="endpoint">
                <span class="method">GET</span> /api/portfolio - 获取投资组合数据
            </div>
            <div class="endpoint">
                <span class="method">POST</span> /api/clear-cache - 清除缓存
            </div>
            <p><a href="/web">访问前端界面</a></p>
        </body>
    </html>
    """

@app.route('/web')
def web_interface():
    """前端界面"""
    return """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>股票投资组合管理系统</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .header { text-align: center; margin-bottom: 30px; }
            .status { text-align: center; margin-bottom: 20px; }
            .summary { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 30px; }
            .card { background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; }
            .table { width: 100%; border-collapse: collapse; }
            .table th, .table td { padding: 12px; text-align: left; border-bottom: 1px solid #dee2e6; }
            .table th { background: #f8f9fa; font-weight: 600; }
            .btn { padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; margin: 5px; }
            .btn-primary { background: #007bff; color: white; }
            .btn-secondary { background: #6c757d; color: white; }
            .positive { color: #28a745; }
            .negative { color: #dc3545; }
            .error { background: #fff5f5; color: #721c24; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>股票投资组合管理系统</h1>
                <p>支持A股、港股、美股实时数据</p>
            </div>
            
            <div class="status">
                <div id="status">正在加载数据...</div>
                <div>
                    <button class="btn btn-primary" onclick="refreshData()">刷新数据</button>
                    <button class="btn btn-secondary" onclick="clearCache()">清除缓存</button>
                </div>
            </div>
            
            <div id="summary" class="summary">加载中...</div>
            
            <div class="table-container">
                <table class="table">
                    <thead>
                        <tr>
                            <th>股票名称</th>
                            <th>代码</th>
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
                        <tr><td colspan="9" style="text-align: center;">加载中...</td></tr>
                    </tbody>
                </table>
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
            
            async function loadPortfolio() {
                try {
                    const response = await fetch('/api/portfolio');
                    const data = await response.json();
                    
                    if (data.success) {
                        renderPortfolio(data);
                        updateStatus(data.positions);
                    } else {
                        document.getElementById('portfolio').innerHTML = 
                            '<tr><td colspan="9" style="text-align: center; color: red;">加载失败: ' + data.error + '</td></tr>';
                    }
                } catch (error) {
                    document.getElementById('portfolio').innerHTML = 
                        '<tr><td colspan="9" style="text-align: center; color: red;">网络错误</td></tr>';
                }
            }
            
            function renderPortfolio(data) {
                // 渲染汇总
                const summary = data.summary;
                document.getElementById('summary').innerHTML = `
                    <div class="card">
                        <h3>总资产</h3>
                        <div>${formatCurrency(summary.totalAssets)}</div>
                    </div>
                    <div class="card">
                        <h3>总市值</h3>
                        <div>${formatCurrency(summary.totalValue)}</div>
                    </div>
                    <div class="card">
                        <h3>总盈亏</h3>
                        <div class="${getChangeClass(summary.totalProfit)}">${formatCurrency(summary.totalProfit)}</div>
                        <div>${formatPercent(summary.totalProfitPercent)}</div>
                    </div>
                    <div class="card">
                        <h3>现金余额</h3>
                        <div>${formatCurrency(summary.cashBalance)}</div>
                    </div>
                `;
                
                // 渲染持仓
                const portfolio = data.positions;
                const tbody = document.getElementById('portfolio');
                
                tbody.innerHTML = portfolio.map(pos => {
                    if (!pos.hasRealTimeData) {
                        return `
                            <tr class="error">
                                <td>${pos.name}</td>
                                <td>${pos.code}</td>
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
                const statusEl = document.getElementById('status');
                const realTimeCount = positions.filter(p => p.hasRealTimeData).length;
                const totalCount = positions.length;
                
                if (realTimeCount === 0) {
                    statusEl.innerHTML = '<span style="color: red;">数据获取失败</span>';
                } else if (realTimeCount < totalCount) {
                    statusEl.innerHTML = `<span style="color: orange;">部分数据异常 (${realTimeCount}/${totalCount})</span>`;
                } else {
                    statusEl.innerHTML = '<span style="color: green;">数据正常</span>';
                }
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
    logger.info("股票数据API服务器启动中...")
    logger.info("访问 http://localhost:5000/api/health 检查服务状态")
    logger.info("访问 http://localhost:5000/web 查看前端界面")
    
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)