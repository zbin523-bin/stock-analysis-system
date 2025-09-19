#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试新的API集成
"""

import requests
import json
import time

# API配置
API_BASE_URL = "https://stock-portfolio-api-nd2p.onrender.com/api"

def test_alpha_vantage_us():
    """测试Alpha Vantage美股API"""
    print("=== 测试Alpha Vantage美股API ===")
    
    test_stocks = ["AAPL", "MSFT", "TSLA"]
    
    for symbol in test_stocks:
        print(f"\n测试美股 {symbol}:")
        
        try:
            response = requests.get(f"{API_BASE_URL}/stock/us/{symbol}", timeout=15)
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    stock_info = data.get("data", {})
                    price = stock_info.get("price", 0)
                    source = stock_info.get("source", "unknown")
                    print(f"  OK 获取成功: 价格={price}, 来源={source}")
                else:
                    print(f"  ERROR 获取失败: {data.get('error')}")
            else:
                print(f"  ERROR 请求失败: {response.status_code}")
                
        except Exception as e:
            print(f"  ERROR 连接失败: {e}")

def test_alpha_vantage_hk():
    """测试Alpha Vantage港股API"""
    print("\n=== 测试Alpha Vantage港股API ===")
    
    test_stocks = ["700", "9988", "9618"]
    
    for code in test_stocks:
        print(f"\n测试港股 {code}:")
        
        try:
            response = requests.get(f"{API_BASE_URL}/stock/hk/{code}", timeout=15)
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    stock_info = data.get("data", {})
                    price = stock_info.get("price", 0)
                    source = stock_info.get("source", "unknown")
                    print(f"  OK 获取成功: 价格={price}, 来源={source}")
                else:
                    print(f"  ERROR 获取失败: {data.get('error')}")
            else:
                print(f"  ERROR 请求失败: {response.status_code}")
                
        except Exception as e:
            print(f"  ERROR 连接失败: {e}")

def test_tushare_a():
    """测试TuShare Pro A股API"""
    print("\n=== 测试TuShare Pro A股API ===")
    
    test_stocks = ["000001", "600036", "000858"]
    
    for code in test_stocks:
        print(f"\n测试A股 {code}:")
        
        try:
            response = requests.get(f"{API_BASE_URL}/stock/a/{code}", timeout=15)
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    stock_info = data.get("data", {})
                    price = stock_info.get("price", 0)
                    source = stock_info.get("source", "unknown")
                    print(f"  OK 获取成功: 价格={price}, 来源={source}")
                else:
                    print(f"  ERROR 获取失败: {data.get('error')}")
            else:
                print(f"  ERROR 请求失败: {response.status_code}")
                
        except Exception as e:
            print(f"  ERROR 连接失败: {e}")

def test_api_health():
    """测试API健康状态"""
    print("=== 测试API健康状态 ===")
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"OK API服务正常: {data}")
            return True
        else:
            print(f"ERROR API服务异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"ERROR API连接失败: {e}")
        return False

def main():
    """主测试函数"""
    print("开始测试新的API集成...")
    print(f"API地址: {API_BASE_URL}")
    
    # 测试API健康状态
    if not test_api_health():
        print("\n❌ API服务不可用，停止测试")
        return
    
    # 测试各个API
    test_tushare_a()
    test_alpha_vantage_us()
    test_alpha_vantage_hk()
    
    print("\n测试完成！")

if __name__ == "__main__":
    main()