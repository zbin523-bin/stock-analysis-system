#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票数据API服务 - 群晖部署版
支持A股、美股实时数据抓取
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import json
import time
import os
import logging
from datetime import datetime
import requests
from functools import wraps
import threading

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='../web/static')
CORS(app)

# 配置
CACHE_DURATION = int(os.getenv('CACHE_DURATION', '30000'))  # 30秒缓存
stock_cache = {}

class RealStockScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        })
    
    def get_a_stock_data(self, code):
        """获取A股真实数据"""
        cache_key = f"a_{code}"
        cached = stock_cache.get(cache_key)
        
        if cached and time.time() * 1000 - cached['timestamp'] < CACHE_DURATION:
            return cached['data']
        
        try:
            # 新浪财经API
            data = self._scrape_sina_a(code)
            if data and data.get('price', 0) > 0:
                stock_cache[cache_key] = {'data': data, 'timestamp': int(time.time() * 1000)}
                logger.info(f"成功获取A股 {code}: {data['name']} - {data['price']}")
                return data
                
            # 腾讯财经API
            data = self._scrape_tencent_a(code)
            if data and data.get('price', 0) > 0:
                stock_cache[cache_key] = {'data': data, 'timestamp': int(time.time() * 1000)}
                logger.info(f"成功获取A股 {code}: {data['name']} - {data['price']}")
                return data
                
        except Exception as e:
            logger.error(f"获取A股 {code} 失败: {e}")
        
        return None
    
    def get_us_stock_data(self, symbol):
        """获取美股真实数据"""
        cache_key = f"us_{symbol}"
        cached = stock_cache.get(cache_key)
        
        if cached and time.time() * 1000 - cached['timestamp'] < CACHE_DURATION:
            return cached['data']
        
        try:
            # 优先使用qos.hk API
            data = self._scrape_qos_us(symbol)
            if data and data.get('price', 0) > 0:
                stock_cache[cache_key] = {'data': data, 'timestamp': int(time.time() * 1000)}
                logger.info(f"成功获取美股 {symbol}: {data['name']} - {data['price']}")
                return data
            
            # 备用：Yahoo Finance API
            data = self._scrape_yahoo_finance(symbol)
            if data and data.get('price', 0) > 0:
                stock_cache[cache_key] = {'data': data, 'timestamp': int(time.time() * 1000)}
                logger.info(f"成功获取美股 {symbol}: {data['name']} - {data['price']}")
                return data
                
        except Exception as e:
            logger.error(f"获取美股 {symbol} 失败: {e}")
        
        return None
    
    def get_hk_stock_data(self, code):
        """获取港股真实数据"""
        cache_key = f"hk_{code}"
        cached = stock_cache.get(cache_key)
        
        if cached and time.time() * 1000 - cached['timestamp'] < CACHE_DURATION:
            return cached['data']
        
        try:
            # 优先使用qos.hk API
            data = self._scrape_qos_hk(code)
            if data and data.get('price', 0) > 0:
                stock_cache[cache_key] = {'data': data, 'timestamp': int(time.time() * 1000)}
                logger.info(f"成功获取港股 {code}: {data['name']} - {data['price']}")
                return data
            
            # 备用：腾讯财经港股API
            data = self._scrape_tencent_hk(code)
            if data and data.get('price', 0) > 0:
                stock_cache[cache_key] = {'data': data, 'timestamp': int(time.time() * 1000)}
                logger.info(f"成功获取港股 {code}: {data['name']} - {data['price']}")
                return data
                
        except Exception as e:
            logger.error(f"获取港股 {code} 失败: {e}")
        
        return None
    
    def _scrape_sina_a(self, code):
        """新浪财经API"""
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
                                'timestamp': int(time.time() * 1000)
                            }
        except Exception as e:
            logger.error(f"新浪财经API失败: {e}")
        
        return None
    
    def _scrape_tencent_a(self, code):
        """腾讯财经API"""
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
                                'timestamp': int(time.time() * 1000)
                            }
        except Exception as e:
            logger.error(f"腾讯财经API失败: {e}")
        
        return None
    
    def _scrape_yahoo_finance(self, symbol):
        """Yahoo Finance API"""
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
                                'timestamp': int(time.time() * 1000)
                            }
        except Exception as e:
            logger.error(f"Yahoo Finance失败: {e}")
        
        return None
    
    def _scrape_tencent_hk(self, code):
        """腾讯财经港股API"""
        try:
            hk_code = f"hk{code}"
            url = f"https://qt.gtimg.cn/q={hk_code}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 Safari/604.1',
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

# 初始化抓取器
scraper = RealStockScraper()

# 模拟的投资组合数据
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
            "code": "TSLA",
            "name": "Tesla Inc.",
            "market": "美股",
            "industry": "汽车",
            "quantity": 20,
            "costPrice": 200.00,
            "currency": "USD"
        },
        {
            "id": 201,
            "code": "0700",
            "name": "腾讯控股",
            "market": "港股",
            "industry": "科技",
            "quantity": 100,
            "costPrice": 320.00,
            "currency": "HKD"
        },
        {
            "id": 202,
            "code": "0941",
            "name": "中国移动",
            "market": "港股",
            "industry": "通信",
            "quantity": 200,
            "costPrice": 55.00,
            "currency": "HKD"
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
        'version': '1.0.0'
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
            elif position["market"] == "美股":
                real_time_data = scraper.get_us_stock_data(position["code"])
            elif position["market"] == "港股":
                real_time_data = scraper.get_hk_stock_data(position["code"])
            
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
    return send_from_directory('../web', 'index.html')

if __name__ == '__main__':
    logger.info("股票数据API服务器启动中...")
    logger.info("访问 http://localhost:5000/api/health 检查服务状态")
    
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)