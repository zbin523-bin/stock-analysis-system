#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票数据API服务 - 增强版（支持qos.hk API）
支持A股、港股、美股实时数据抓取
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

class EnhancedStockScraper:
    """增强的股票数据抓取器 - 支持多种数据源"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        })
        
        # qos.hk API配置
        self.qos_api_key = "708435e33614a53a9abde3f835024144"
        self.qos_base_url = "https://qos.hk"
    
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
                if '=' in content and '"' in content:
                    data_part = content.split('=')[1].strip('";\n')
                    fields = data_part.split(',')
                    
                    if len(fields) >= 10 and fields[3] != '0.000':
                        name = fields[0] if fields[0] else code
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
                                'currency': 'CNY'
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
                        name = fields[1] if fields[1] else code
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
                                'currency': 'CNY'
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
    
    def _scrape_qos_hk(self, code):
        """使用qos.hk API获取港股数据"""
        try:
            # 港股代码格式: HK:700
            hk_code = f"HK:{code}"
            
            # 获取实时行情
            url = f"{self.qos_base_url}/snapshot"
            payload = {"codes": [hk_code]}
            params = {"key": self.qos_api_key}
            
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            }
            
            response = self.session.post(url, json=payload, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("msg") == "OK" and data.get("data"):
                    stock_data = data["data"][0]
                    
                    # 计算涨跌额和涨跌幅
                    current_price = float(stock_data.get("lp", 0))
                    yesterday_price = float(stock_data.get("yp", 0))
                    
                    if current_price > 0 and yesterday_price > 0:
                        change = current_price - yesterday_price
                        change_percent = (change / yesterday_price) * 100
                    else:
                        change = 0
                        change_percent = 0
                    
                    return {
                        'code': code,
                        'name': f"HK{code}",  # 可以通过instrument-info接口获取真实名称
                        'price': current_price,
                        'change': change,
                        'changePercent': change_percent,
                        'volume': int(stock_data.get("v", 0)),
                        'high': float(stock_data.get("h", 0)),
                        'low': float(stock_data.get("l", 0)),
                        'open': float(stock_data.get("o", 0)),
                        'timestamp': int(stock_data.get("ts", time.time())) * 1000,
                        'currency': 'HKD',
                        'source': 'qos.hk'
                    }
        except Exception as e:
            logger.error(f"qos.hk港股 {code} 失败: {e}")
        
        return None
    
    def _scrape_qos_us(self, symbol):
        """使用qos.hk API获取美股数据"""
        try:
            # 美股代码格式: US:AAPL
            us_code = f"US:{symbol}"
            
            # 获取实时行情
            url = f"{self.qos_base_url}/snapshot"
            payload = {"codes": [us_code]}
            params = {"key": self.qos_api_key}
            
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            }
            
            response = self.session.post(url, json=payload, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("msg") == "OK" and data.get("data"):
                    stock_data = data["data"][0]
                    
                    # 计算涨跌额和涨跌幅
                    current_price = float(stock_data.get("lp", 0))
                    yesterday_price = float(stock_data.get("yp", 0))
                    
                    if current_price > 0 and yesterday_price > 0:
                        change = current_price - yesterday_price
                        change_percent = (change / yesterday_price) * 100
                    else:
                        change = 0
                        change_percent = 0
                    
                    return {
                        'code': symbol,
                        'name': symbol,  # 可以通过instrument-info接口获取真实名称
                        'price': current_price,
                        'change': change,
                        'changePercent': change_percent,
                        'volume': int(stock_data.get("v", 0)),
                        'high': float(stock_data.get("h", 0)),
                        'low': float(stock_data.get("l", 0)),
                        'open': float(stock_data.get("o", 0)),
                        'timestamp': int(stock_data.get("ts", time.time())) * 1000,
                        'currency': 'USD',
                        'source': 'qos.hk'
                    }
        except Exception as e:
            logger.error(f"qos.hk美股 {symbol} 失败: {e}")
        
        return None

# 初始化抓取器
scraper = EnhancedStockScraper()

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
            "industry": "电信",
            "quantity": 200,
            "costPrice": 55.00,
            "currency": "HKD"
        }
    ],
    "totalCash": 50000
}

# API路由
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
            code = position["code"]
            market = position["market"]
            
            # 根据市场获取股票数据
            stock_data = None
            has_real_time_data = False
            
            if market == "A股":
                stock_data = scraper.get_a_stock_data(code)
            elif market == "美股":
                stock_data = scraper.get_us_stock_data(code)
            elif market == "港股":
                stock_data = scraper.get_hk_stock_data(code)
            
            # 计算持仓信息
            quantity = position["quantity"]
            cost_price = position["costPrice"]
            
            if stock_data and stock_data.get("price", 0) > 0:
                current_price = stock_data["price"]
                has_real_time_data = True
            else:
                current_price = cost_price
                has_real_time_data = False
            
            market_value = quantity * current_price
            profit = market_value - (quantity * cost_price)
            profit_rate = (profit / (quantity * cost_price) * 100) if (quantity * cost_price) > 0 else 0
            
            enriched_position = {
                "id": position["id"],
                "code": code,
                "name": position["name"],
                "market": market,
                "industry": position["industry"],
                "quantity": quantity,
                "costPrice": cost_price,
                "currentPrice": current_price,
                "currency": position["currency"],
                "marketValue": market_value,
                "profit": profit,
                "profitRate": profit_rate,
                "hasRealTimeData": has_real_time_data
            }
            
            # 添加实时数据字段
            if stock_data:
                enriched_position.update({
                    "change": stock_data.get("change", 0),
                    "changePercent": stock_data.get("changePercent", 0),
                    "volume": stock_data.get("volume", 0),
                    "high": stock_data.get("high", 0),
                    "low": stock_data.get("low", 0),
                    "open": stock_data.get("open", 0),
                    "lastUpdate": stock_data.get("timestamp", int(time.time() * 1000))
                })
            
            enriched_positions.append(enriched_position)
            total_value += market_value
            total_profit += profit
        
        total_assets = total_value + portfolio_data["totalCash"]
        total_profit_percent = (total_profit / (total_value - total_profit) * 100) if (total_value - total_profit) > 0 else 0
        
        return jsonify({
            "success": True,
            "lastUpdate": int(time.time() * 1000),
            "positions": enriched_positions,
            "summary": {
                "totalAssets": total_assets,
                "totalValue": total_value,
                "totalProfit": total_profit,
                "totalProfitPercent": total_profit_percent,
                "cashBalance": portfolio_data["totalCash"]
            }
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