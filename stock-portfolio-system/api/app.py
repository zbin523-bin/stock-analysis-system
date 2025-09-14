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
    
    def get_fund_data(self, code):
        """获取基金数据"""
        cache_key = f"fund_{code}"
        cached = stock_cache.get(cache_key)
        
        if cached and time.time() * 1000 - cached['timestamp'] < CACHE_DURATION:
            return cached['data']
        
        try:
            # 天天基金网API
            data = self._scrape_ttjj_fund(code)
            if data and data.get('price', 0) > 0:
                stock_cache[cache_key] = {'data': data, 'timestamp': int(time.time() * 1000)}
                logger.info(f"成功获取基金 {code}: {data['name']} - {data['price']}")
                return data
                
        except Exception as e:
            logger.error(f"获取基金 {code} 失败: {e}")
        
        return None
    
    def _scrape_ttjj_fund(self, code):
        """天天基金网API"""
        try:
            url = f"https://fundgz.1234567.com.cn/js/{code}.js"
            
            headers = {
                'Referer': f'https://fund.eastmoney.com/{code}.html',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            }
            
            response = self.session.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                content = response.text
                if 'jsonpgz(' in content and ')' in content:
                    # 提取JSON数据
                    json_str = content.split('jsonpgz(')[1].split(')')[0]
                    data = json.loads(json_str)
                    
                    if data.get('dwjz', 0) > 0:
                        return {
                            'code': code,
                            'name': data.get('name', code),
                            'price': float(data.get('dwjz', 0)),  # 单位净值
                            'change': float(data.get('gszzl', 0)),  # 估算涨跌幅
                            'changePercent': float(data.get('gszzl', 0)),
                            'timestamp': int(time.time() * 1000),
                            'currency': 'CNY',
                            'fundType': data.get('fundtype', ''),
                            'yesterdayPrice': float(data.get('jzrq', 0))  # 昨日净值
                        }
        except Exception as e:
            logger.error(f"天天基金网API失败: {e}")
        
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
            "code": "700",
            "name": "腾讯控股",
            "market": "港股",
            "industry": "科技",
            "quantity": 100,
            "costPrice": 550.00,
            "currency": "HKD"
        },
        {
            "id": 202,
            "code": "9988",
            "name": "阿里巴巴-W",
            "market": "港股",
            "industry": "电商",
            "quantity": 50,
            "costPrice": 120.00,
            "currency": "HKD"
        },
      ],
    "totalCash": 50000
}

# 交易记录数据
transactions_data = [
    {
        "id": 1,
        "date": "2024-01-10",
        "type": "买入",
        "code": "600036",
        "name": "招商银行",
        "market": "A股",
        "price": 38.70,
        "quantity": 100,
        "amount": 3870.00,
        "commission": 5.00,
        "status": "已完成"
    },
    {
        "id": 2,
        "date": "2024-01-12",
        "type": "买入",
        "code": "000858",
        "name": "五粮液",
        "market": "A股",
        "price": 165.80,
        "quantity": 50,
        "amount": 8290.00,
        "commission": 5.00,
        "status": "已完成"
    },
    {
        "id": 3,
        "date": "2024-01-15",
        "type": "买入",
        "code": "300059",
        "name": "东方财富",
        "market": "A股",
        "price": 18.90,
        "quantity": 200,
        "amount": 3780.00,
        "commission": 5.00,
        "status": "已完成"
    },
    {
        "id": 4,
        "date": "2024-02-01",
        "type": "买入",
        "code": "AAPL",
        "name": "Apple Inc.",
        "market": "美股",
        "price": 150.00,
        "quantity": 30,
        "amount": 4500.00,
        "commission": 5.00,
        "status": "已完成"
    },
    {
        "id": 5,
        "date": "2024-02-05",
        "type": "买入",
        "code": "TSLA",
        "name": "Tesla Inc.",
        "market": "美股",
        "price": 200.00,
        "quantity": 20,
        "amount": 4000.00,
        "commission": 5.00,
        "status": "已完成"
    },
    {
        "id": 6,
        "date": "2024-02-10",
        "type": "买入",
        "code": "700",
        "name": "腾讯控股",
        "market": "港股",
        "price": 550.00,
        "quantity": 100,
        "amount": 55000.00,
        "commission": 10.00,
        "status": "已完成"
    },
    {
        "id": 7,
        "date": "2024-02-12",
        "type": "买入",
        "code": "9988",
        "name": "阿里巴巴-W",
        "market": "港股",
        "price": 120.00,
        "quantity": 50,
        "amount": 6000.00,
        "commission": 10.00,
        "status": "已完成"
    }
]

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

@app.route('/api/fund/<code>')
def get_fund(code):
    """获取基金数据"""
    try:
        data = scraper.get_fund_data(code)
        if data:
            return jsonify({
                'success': True,
                'data': data,
                'timestamp': int(time.time() * 1000)
            })
        else:
            return jsonify({
                'success': False,
                'error': '无法获取基金数据',
                'timestamp': int(time.time() * 1000)
            })
    except Exception as e:
        logger.error(f"获取基金 {code} 异常: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': int(time.time() * 1000)
        })

def _calculate_portfolio_from_transactions():
    """从交易记录计算持仓"""
    positions = {}
    total_cost = 0
    
    for transaction in transactions_data:
        code = transaction["code"]
        name = transaction["name"]
        market = transaction["market"]
        quantity = transaction["quantity"]
        price = transaction["price"]
        amount = transaction["amount"]
        commission = transaction.get("commission", 0)
        
        if code not in positions:
            positions[code] = {
                "code": code,
                "name": name,
                "market": market,
                "quantity": 0,
                "total_cost": 0,
                "currency": "CNY" if market in ["A股", "基金"] else "HKD" if market == "港股" else "USD"
            }
        
        if transaction["type"] in ["buy", "买入"]:
            positions[code]["quantity"] += quantity
            positions[code]["total_cost"] += amount + commission
            total_cost += amount + commission
        elif transaction["type"] in ["sell", "卖出"]:
            positions[code]["quantity"] -= quantity
            positions[code]["total_cost"] -= amount - commission
            total_cost -= amount - commission
    
    # 转换为列表并计算成本价
    position_list = []
    for code, pos in positions.items():
        if pos["quantity"] > 0:  # 只显示有持仓的
            cost_price = pos["total_cost"] / pos["quantity"]
            position_list.append({
                "id": len(position_list) + 1,
                "code": pos["code"],
                "name": pos["name"],
                "market": pos["market"],
                "industry": "基金" if pos["market"] == "基金" else ("股票" if pos["market"] == "A股" else "股票"),
                "quantity": pos["quantity"],
                "costPrice": cost_price,
                "currency": pos["currency"]
            })
    
    return position_list, total_cost

@app.route('/api/portfolio')
def get_portfolio():
    """获取投资组合数据"""
    try:
        # 从交易记录动态计算持仓
        calculated_positions, total_cost = _calculate_portfolio_from_transactions()
        enriched_positions = []
        total_value = 0
        total_profit = 0
        
        for position in calculated_positions:
            code = position["code"]
            market = position["market"]
            
            # 根据市场获取数据
            asset_data = None
            has_real_time_data = False
            
            if market == "A股":
                asset_data = scraper.get_a_stock_data(code)
            elif market == "美股":
                asset_data = scraper.get_us_stock_data(code)
            elif market == "港股":
                asset_data = scraper.get_hk_stock_data(code)
            elif market == "基金":
                asset_data = scraper.get_fund_data(code)
            
            # 计算持仓信息
            quantity = position["quantity"]
            cost_price = position["costPrice"]
            
            if asset_data and asset_data.get("price", 0) > 0:
                current_price = asset_data["price"]
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
            if asset_data:
                enriched_position.update({
                    "change": asset_data.get("change", 0),
                    "changePercent": asset_data.get("changePercent", 0),
                    "volume": asset_data.get("volume", 0),
                    "high": asset_data.get("high", 0),
                    "low": asset_data.get("low", 0),
                    "open": asset_data.get("open", 0),
                    "lastUpdate": asset_data.get("timestamp", int(time.time() * 1000))
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
        logger.error(f"清除缓存异常: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": int(time.time() * 1000)
        })

@app.route('/api/transactions')
def get_transactions():
    """获取交易记录"""
    try:
        return jsonify({
            "success": True,
            "data": transactions_data,
            "timestamp": int(time.time() * 1000)
        })
    except Exception as e:
        logger.error(f"获取交易记录异常: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": int(time.time() * 1000)
        })

@app.route('/api/transactions', methods=['POST'])
def add_transaction():
    """添加交易记录"""
    try:
        data = request.get_json()
        
        # 验证必要字段
        required_fields = ['type', 'code', 'name', 'market', 'price', 'quantity']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "success": False,
                    "error": f"缺少必要字段: {field}",
                    "timestamp": int(time.time() * 1000)
                }), 400
        
        # 创建新交易记录
        new_transaction = {
            "id": len(transactions_data) + 1,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "type": data["type"],
            "code": data["code"],
            "name": data["name"],
            "market": data["market"],
            "price": float(data["price"]),
            "quantity": int(data["quantity"]),
            "amount": float(data["price"]) * int(data["quantity"]),
            "commission": data.get("commission", 5.00),
            "status": "已完成"
        }
        
        # 添加到交易记录列表
        transactions_data.append(new_transaction)
        
        # 如果是买入操作，更新投资组合
        if data["type"] == "买入":
            # 检查是否已存在该股票的持仓
            existing_position = None
            for position in portfolio_data["positions"]:
                if position["code"] == data["code"] and position["market"] == data["market"]:
                    existing_position = position
                    break
            
            if existing_position:
                # 更新现有持仓的平均成本
                old_quantity = existing_position["quantity"]
                old_cost = existing_position["costPrice"] * old_quantity
                new_quantity = old_quantity + int(data["quantity"])
                new_cost = old_cost + (float(data["price"]) * int(data["quantity"]))
                existing_position["costPrice"] = new_cost / new_quantity
                existing_position["quantity"] = new_quantity
            else:
                # 添加新持仓
                currency_map = {"A股": "CNY", "美股": "USD", "港股": "HKD"}
                industry_map = {
                    "600036": "银行", "000858": "白酒", "300059": "互联网金融",
                    "AAPL": "科技", "TSLA": "汽车", "700": "科技", "9988": "电商"
                }
                
                new_position = {
                    "id": len(portfolio_data["positions"]) + 1,
                    "code": data["code"],
                    "name": data["name"],
                    "market": data["market"],
                    "industry": industry_map.get(data["code"], "其他"),
                    "quantity": int(data["quantity"]),
                    "costPrice": float(data["price"]),
                    "currency": currency_map.get(data["market"], "CNY")
                }
                portfolio_data["positions"].append(new_position)
        
        logger.info(f"添加交易记录: {data['type']} {data['code']} {data['quantity']}股")
        return jsonify({
            "success": True,
            "message": "交易记录添加成功",
            "data": new_transaction,
            "timestamp": int(time.time() * 1000)
        })
        
    except Exception as e:
        logger.error(f"添加交易记录异常: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": int(time.time() * 1000)
        })

@app.route('/api/transactions/<int:transaction_id>', methods=['PUT'])
def update_transaction(transaction_id):
    """更新交易记录"""
    try:
        data = request.get_json()
        
        # 验证必需字段
        required_fields = ['type', 'code', 'name', 'market', 'price', 'quantity']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'缺少必需字段: {field}',
                    'timestamp': int(time.time() * 1000)
                }), 400
        
        # 查找交易记录
        transaction_index = -1
        for i, trans in enumerate(transactions_data):
            if trans['id'] == transaction_id:
                transaction_index = i
                break
        
        if transaction_index == -1:
            return jsonify({
                'success': False,
                'error': '交易记录不存在',
                'timestamp': int(time.time() * 1000)
            }), 404
        
        # 更新交易记录
        updated_transaction = {
            "id": transaction_id,
            "date": data.get("date", transactions_data[transaction_index]["date"]),
            "type": data["type"],
            "code": data["code"],
            "name": data["name"],
            "market": data["market"],
            "price": float(data["price"]),
            "quantity": int(data["quantity"]),
            "amount": float(data["price"]) * int(data["quantity"]),
            "commission": data.get("commission", 5.00),
            "status": data.get("status", "已完成")
        }
        
        transactions_data[transaction_index] = updated_transaction
        logger.info(f"更新交易记录: {data['type']} {data['code']} {data['quantity']}股")
        
        return jsonify({
            "success": True,
            "message": "交易记录更新成功",
            "data": updated_transaction,
            "timestamp": int(time.time() * 1000)
        })
        
    except Exception as e:
        logger.error(f"更新交易记录异常: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": int(time.time() * 1000)
        })

@app.route('/api/transactions/<int:transaction_id>', methods=['DELETE'])
def delete_transaction(transaction_id):
    """删除交易记录"""
    try:
        # 查找交易记录
        transaction_index = -1
        for i, trans in enumerate(transactions_data):
            if trans['id'] == transaction_id:
                transaction_index = i
                break
        
        if transaction_index == -1:
            return jsonify({
                'success': False,
                'error': '交易记录不存在',
                'timestamp': int(time.time() * 1000)
            }), 404
        
        deleted_transaction = transactions_data.pop(transaction_index)
        logger.info(f"删除交易记录: {deleted_transaction['type']} {deleted_transaction['code']} {deleted_transaction['quantity']}股")
        
        return jsonify({
            "success": True,
            "message": "交易记录删除成功",
            "data": deleted_transaction,
            "timestamp": int(time.time() * 1000)
        })
        
    except Exception as e:
        logger.error(f"删除交易记录异常: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": int(time.time() * 1000)
        })

@app.route('/api/transactions/<int:transaction_id>')
def get_transaction(transaction_id):
    """获取单个交易记录"""
    try:
        # 查找交易记录
        for trans in transactions_data:
            if trans['id'] == transaction_id:
                return jsonify({
                    "success": True,
                    "data": trans,
                    "timestamp": int(time.time() * 1000)
                })
        
        return jsonify({
            'success': False,
            'error': '交易记录不存在',
            'timestamp': int(time.time() * 1000)
        }), 404
        
    except Exception as e:
        logger.error(f"获取交易记录异常: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": int(time.time() * 1000)
        })

@app.route('/')
def index():
    """主页"""
    return send_from_directory('../web', 'index.html')

@app.route('/api.js')
def serve_api_js():
    """提供api.js文件"""
    try:
        return send_from_directory('../web/static', 'api.js')
    except Exception as e:
        logger.error(f"提供api.js文件失败: {e}")
        return "File not found", 404

if __name__ == '__main__':
    logger.info("股票数据API服务器启动中...")
    logger.info("访问 http://localhost:5000/api/health 检查服务状态")
    
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)