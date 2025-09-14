#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
基于qos.hk API的港股美股数据抓取器
API Key: 708435e33614a53a9abde3f835024144
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Optional, List, Any

class QosStockScraper:
    """基于qos.hk API的股票数据抓取器"""
    
    def __init__(self, api_key: str = "708435e33614a53a9abde3f835024144"):
        self.api_key = api_key
        self.base_url = "https://qos.hk"
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        })
    
    def get_instrument_info(self, codes: List[str]) -> Optional[Dict]:
        """获取交易品种的基础信息"""
        try:
            url = f"{self.base_url}/instrument-info"
            
            # 准备请求数据
            payload = {"codes": codes}
            
            # 添加API key到URL参数
            params = {"key": self.api_key}
            
            response = self.session.post(url, json=payload, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("msg") == "OK":
                    return data.get("data", [])
                else:
                    print(f"获取基础信息失败: {data.get('msg')}")
            else:
                print(f"HTTP错误: {response.status_code}")
                
        except Exception as e:
            print(f"获取基础信息异常: {e}")
        
        return None
    
    def get_snapshot(self, codes: List[str]) -> Optional[Dict]:
        """获取交易品种的实时行情快照"""
        try:
            url = f"{self.base_url}/snapshot"
            
            # 准备请求数据
            payload = {"codes": codes}
            
            # 添加API key到URL参数
            params = {"key": self.api_key}
            
            response = self.session.post(url, json=payload, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("msg") == "OK":
                    return data.get("data", [])
                else:
                    print(f"获取快照数据失败: {data.get('msg')}")
            else:
                print(f"HTTP错误: {response.status_code}")
                
        except Exception as e:
            print(f"获取快照数据异常: {e}")
        
        return None
    
    def get_hk_stock_data(self, code: str) -> Optional[Dict]:
        """获取港股数据"""
        try:
            # 港股代码格式: HK:700
            hk_code = f"HK:{code}"
            
            # 获取实时行情
            snapshot_data = self.get_snapshot([hk_code])
            
            if snapshot_data and len(snapshot_data) > 0:
                stock_data = snapshot_data[0]
                
                # 获取基础信息
                info_data = self.get_instrument_info([hk_code])
                name = f"HK{code}"
                if info_data and len(info_data) > 0:
                    name = info_data[0].get("nc", name)
                
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
                    'name': name,
                    'price': current_price,
                    'change': change,
                    'changePercent': change_percent,
                    'volume': int(stock_data.get("v", 0)),
                    'high': float(stock_data.get("h", 0)),
                    'low': float(stock_data.get("l", 0)),
                    'open': float(stock_data.get("o", 0)),
                    'timestamp': int(stock_data.get("ts", time.time())) * 1000,
                    'currency': 'HKD',
                    'source': 'qos.hk',
                    'yesterday_close': yesterday_price,
                    'turnover': float(stock_data.get("t", 0)),
                    'is_suspended': stock_data.get("s", 0) == 1
                }
            else:
                print(f"港股 {code} 快照数据为空")
                
        except Exception as e:
            print(f"获取港股 {code} 数据失败: {e}")
        
        return None
    
    def get_us_stock_data(self, symbol: str) -> Optional[Dict]:
        """获取美股数据"""
        try:
            # 美股代码格式: US:AAPL
            us_code = f"US:{symbol}"
            
            # 获取实时行情
            snapshot_data = self.get_snapshot([us_code])
            
            if snapshot_data and len(snapshot_data) > 0:
                stock_data = snapshot_data[0]
                
                # 获取基础信息
                info_data = self.get_instrument_info([us_code])
                name = symbol
                if info_data and len(info_data) > 0:
                    name = info_data[0].get("nc", name)
                
                # 计算涨跌额和涨跌幅
                current_price = float(stock_data.get("lp", 0))
                yesterday_price = float(stock_data.get("yp", 0))
                
                if current_price > 0 and yesterday_price > 0:
                    change = current_price - yesterday_price
                    change_percent = (change / yesterday_price) * 100
                else:
                    change = 0
                    change_percent = 0
                
                # 处理盘前盘后数据
                pre_market = None
                after_market = None
                
                if "pq" in stock_data:
                    pq = stock_data["pq"]
                    pre_market = {
                        'price': float(pq.get("lp", 0)),
                        'change': float(pq.get("lp", 0)) - float(pq.get("yp", 0)),
                        'volume': int(pq.get("v", 0)),
                        'timestamp': int(pq.get("ts", time.time())) * 1000,
                    }
                
                if "aq" in stock_data:
                    aq = stock_data["aq"]
                    after_market = {
                        'price': float(aq.get("lp", 0)),
                        'change': float(aq.get("lp", 0)) - float(aq.get("yp", 0)),
                        'volume': int(aq.get("v", 0)),
                        'timestamp': int(aq.get("ts", time.time())) * 1000,
                    }
                
                return {
                    'code': symbol,
                    'name': name,
                    'price': current_price,
                    'change': change,
                    'changePercent': change_percent,
                    'volume': int(stock_data.get("v", 0)),
                    'high': float(stock_data.get("h", 0)),
                    'low': float(stock_data.get("l", 0)),
                    'open': float(stock_data.get("o", 0)),
                    'timestamp': int(stock_data.get("ts", time.time())) * 1000,
                    'currency': 'USD',
                    'source': 'qos.hk',
                    'yesterday_close': yesterday_price,
                    'turnover': float(stock_data.get("t", 0)),
                    'is_suspended': stock_data.get("s", 0) == 1,
                    'pre_market': pre_market,
                    'after_market': after_market,
                    'trading_session': stock_data.get("tt", 0)
                }
            else:
                print(f"美股 {symbol} 快照数据为空")
                
        except Exception as e:
            print(f"获取美股 {symbol} 数据失败: {e}")
        
        return None
    
    def get_a_stock_data(self, code: str) -> Optional[Dict]:
        """获取A股数据"""
        try:
            # A股代码格式: SH:600036 或 SZ:000001
            if code.startswith('6'):
                market = 'SH'
            else:
                market = 'SZ'
            
            a_code = f"{market}:{code}"
            
            # 获取实时行情
            snapshot_data = self.get_snapshot([a_code])
            
            if snapshot_data and len(snapshot_data) > 0:
                stock_data = snapshot_data[0]
                
                # 获取基础信息
                info_data = self.get_instrument_info([a_code])
                name = f"{market}{code}"
                if info_data and len(info_data) > 0:
                    name = info_data[0].get("nc", name)
                
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
                    'name': name,
                    'price': current_price,
                    'change': change,
                    'changePercent': change_percent,
                    'volume': int(stock_data.get("v", 0)),
                    'high': float(stock_data.get("h", 0)),
                    'low': float(stock_data.get("l", 0)),
                    'open': float(stock_data.get("o", 0)),
                    'timestamp': int(stock_data.get("ts", time.time())) * 1000,
                    'currency': 'CNY',
                    'source': 'qos.hk',
                    'yesterday_close': yesterday_price,
                    'turnover': float(stock_data.get("t", 0)),
                    'is_suspended': stock_data.get("s", 0) == 1
                }
            else:
                print(f"A股 {code} 快照数据为空")
                
        except Exception as e:
            print(f"获取A股 {code} 数据失败: {e}")
        
        return None
    
    def batch_get_stocks(self, stock_requests: List[Dict]) -> Dict[str, Optional[Dict]]:
        """批量获取股票数据"""
        try:
            # 准备所有代码
            all_codes = []
            code_mapping = {}
            
            for request in stock_requests:
                market = request.get('market', 'HK')
                code = request.get('code')
                
                if market == 'HK':
                    formatted_code = f"HK:{code}"
                elif market == 'US':
                    formatted_code = f"US:{code}"
                elif market == 'A':
                    if code.startswith('6'):
                        formatted_code = f"SH:{code}"
                    else:
                        formatted_code = f"SZ:{code}"
                else:
                    continue
                
                all_codes.append(formatted_code)
                code_mapping[formatted_code] = request
            
            # 批量获取快照数据
            snapshot_data = self.get_snapshot(all_codes)
            
            # 批量获取基础信息
            info_data = self.get_instrument_info(all_codes)
            
            # 处理结果
            results = {}
            
            if snapshot_data:
                info_mapping = {}
                if info_data:
                    info_mapping = {item.get('c'): item for item in info_data}
                
                for stock_data in snapshot_data:
                    code = stock_data.get('c')
                    if code in code_mapping:
                        request = code_mapping[code]
                        original_code = request.get('code')
                        market = request.get('market', 'HK')
                        
                        # 获取名称
                        name = original_code
                        if code in info_mapping:
                            name = info_mapping[code].get('nc', name)
                        
                        # 计算涨跌
                        current_price = float(stock_data.get("lp", 0))
                        yesterday_price = float(stock_data.get("yp", 0))
                        
                        if current_price > 0 and yesterday_price > 0:
                            change = current_price - yesterday_price
                            change_percent = (change / yesterday_price) * 100
                        else:
                            change = 0
                            change_percent = 0
                        
                        # 确定货币
                        currency = 'HKD' if market == 'HK' else 'USD' if market == 'US' else 'CNY'
                        
                        results[original_code] = {
                            'code': original_code,
                            'name': name,
                            'price': current_price,
                            'change': change,
                            'changePercent': change_percent,
                            'volume': int(stock_data.get("v", 0)),
                            'high': float(stock_data.get("h", 0)),
                            'low': float(stock_data.get("l", 0)),
                            'open': float(stock_data.get("o", 0)),
                            'timestamp': int(stock_data.get("ts", time.time())) * 1000,
                            'currency': currency,
                            'source': 'qos.hk',
                            'yesterday_close': yesterday_price,
                            'turnover': float(stock_data.get("t", 0)),
                            'is_suspended': stock_data.get("s", 0) == 1
                        }
            
            return results
            
        except Exception as e:
            print(f"批量获取股票数据失败: {e}")
            return {}

# 测试函数
def test_qos_scraper():
    """测试qos.hk抓取器"""
    scraper = QosStockScraper()
    
    print("=== 测试qos.hk API ===")
    
    # 测试港股
    print("\n--- 港股测试 ---")
    hk_codes = ['700', '9988', '0005', '03690']
    for code in hk_codes:
        print(f"\n测试港股 {code}:")
        data = scraper.get_hk_stock_data(code)
        if data:
            print(f"✅ 成功: {data['name']}")
            print(f"   价格: {data['price']}")
            print(f"   涨跌: {data['change']} ({data['changePercent']:.2f}%)")
            print(f"   成交量: {data['volume']}")
            print(f"   时间戳: {data['timestamp']}")
        else:
            print("❌ 失败")
        time.sleep(1)
    
    # 测试美股
    print("\n--- 美股测试 ---")
    us_codes = ['AAPL', 'TSLA', 'MSFT', 'GOOGL']
    for code in us_codes:
        print(f"\n测试美股 {code}:")
        data = scraper.get_us_stock_data(code)
        if data:
            print(f"✅ 成功: {data['name']}")
            print(f"   价格: {data['price']}")
            print(f"   涨跌: {data['change']} ({data['changePercent']:.2f}%)")
            print(f"   成交量: {data['volume']}")
            print(f"   时间戳: {data['timestamp']}")
            if data.get('pre_market'):
                print(f"   盘前: {data['pre_market']['price']}")
            if data.get('after_market'):
                print(f"   盘后: {data['after_market']['price']}")
        else:
            print("❌ 失败")
        time.sleep(1)
    
    # 测试A股
    print("\n--- A股测试 ---")
    a_codes = ['600036', '000001', '000858', '300059']
    for code in a_codes:
        print(f"\n测试A股 {code}:")
        data = scraper.get_a_stock_data(code)
        if data:
            print(f"✅ 成功: {data['name']}")
            print(f"   价格: {data['price']}")
            print(f"   涨跌: {data['change']} ({data['changePercent']:.2f}%)")
            print(f"   成交量: {data['volume']}")
            print(f"   时间戳: {data['timestamp']}")
        else:
            print("❌ 失败")
        time.sleep(1)
    
    # 测试批量获取
    print("\n--- 批量获取测试 ---")
    batch_requests = [
        {'market': 'HK', 'code': '700'},
        {'market': 'HK', 'code': '9988'},
        {'market': 'US', 'code': 'AAPL'},
        {'market': 'US', 'code': 'TSLA'},
        {'market': 'A', 'code': '600036'},
        {'market': 'A', 'code': '000001'},
    ]
    
    results = scraper.batch_get_stocks(batch_requests)
    print(f"批量获取结果: {len(results)} 只股票")
    for code, data in results.items():
        if data:
            print(f"✅ {code}: {data['name']} - {data['price']}")
        else:
            print(f"❌ {code}: 获取失败")

if __name__ == '__main__':
    test_qos_scraper()