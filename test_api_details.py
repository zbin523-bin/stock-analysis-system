#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API源信息测试
"""

import requests
import json

# API配置
API_BASE_URL = "https://stock-portfolio-api-nd2p.onrender.com/api"

def test_stock_with_details():
    """测试股票数据详细信息"""
    print("=== 测试股票数据详细信息 ===")
    
    test_cases = [
        ("a", "000001", "平安银行"),
        ("us", "AAPL", "苹果"),
        ("hk", "700", "腾讯控股")
    ]
    
    for market, code, name in test_cases:
        print(f"\n测试 {market} {name} ({code}):")
        
        try:
            if market == "a":
                response = requests.get(f"{API_BASE_URL}/stock/a/{code}", timeout=15)
            elif market == "us":
                response = requests.get(f"{API_BASE_URL}/stock/us/{code}", timeout=15)
            elif market == "hk":
                response = requests.get(f"{API_BASE_URL}/stock/hk/{code}", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                print(f"  响应状态: {data.get('success')}")
                print(f"  错误信息: {data.get('error', 'None')}")
                
                if data.get('success'):
                    stock_info = data.get('data', {})
                    print(f"  股票名称: {stock_info.get('name', 'N/A')}")
                    print(f"  股票价格: {stock_info.get('price', 'N/A')}")
                    print(f"  数据来源: {stock_info.get('source', 'N/A')}")
                    print(f"  货币: {stock_info.get('currency', 'N/A')}")
                    print(f"  涨跌幅: {stock_info.get('changePercent', 'N/A')}%")
                    print(f"  时间戳: {stock_info.get('timestamp', 'N/A')}")
                else:
                    print(f"  获取失败: {data.get('error')}")
            else:
                print(f"  HTTP错误: {response.status_code}")
                print(f"  响应内容: {response.text[:200]}")
                
        except Exception as e:
            print(f"  连接失败: {e}")

def test_cache_behavior():
    """测试缓存行为"""
    print("\n=== 测试缓存行为 ===")
    
    # 连续请求同一个股票，观察缓存效果
    code = "000001"
    
    for i in range(3):
        print(f"\n第 {i+1} 次请求 A股 {code}:")
        
        try:
            response = requests.get(f"{API_BASE_URL}/stock/a/{code}", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    stock_info = data.get('data', {})
                    print(f"  价格: {stock_info.get('price', 'N/A')}")
                    print(f"  来源: {stock_info.get('source', 'N/A')}")
                    print(f"  时间戳: {stock_info.get('timestamp', 'N/A')}")
                else:
                    print(f"  获取失败: {data.get('error')}")
                    
        except Exception as e:
            print(f"  连接失败: {e}")
        
        # 等待1秒
        import time
        time.sleep(1)

def main():
    """主测试函数"""
    print("开始测试API源信息...")
    print(f"API地址: {API_BASE_URL}")
    
    # 测试详细信息
    test_stock_with_details()
    
    # 测试缓存行为
    test_cache_behavior()
    
    print("\n测试完成！")

if __name__ == "__main__":
    main()