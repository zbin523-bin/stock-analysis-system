#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试TuShare API
"""

import requests
import json

def debug_tushare_api():
    """调试TuShare API"""
    print("调试TuShare API...")

    # TuShare API配置
    token = "91cb00a3a0021ce5faa4244f491a6669b926b3d50b381b1680bace81"
    url = "http://api.tushare.pro"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    # 测试获取股票基本信息
    basic_data = {
        "api_name": "stock_basic",
        "token": token,
        "params": {
            "ts_code": "600036.SH",
            "limit": "1"
        }
    }

    print("测试stock_basic接口...")
    try:
        response = requests.post(url, json=basic_data, headers=headers, timeout=10)
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")

        if response.status_code == 200:
            result = response.json()
            print(f"解析结果: {result}")
    except Exception as e:
        print(f"请求异常: {e}")

    # 测试获取日线行情数据
    daily_data = {
        "api_name": "daily",
        "token": token,
        "params": {
            "ts_code": "600036.SH",
            "trade_date": "",
            "start_date": "",
            "end_date": "",
            "limit": "1",
            "offset": ""
        }
    }

    print("\n测试daily接口...")
    try:
        response = requests.post(url, json=daily_data, headers=headers, timeout=10)
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")

        if response.status_code == 200:
            result = response.json()
            print(f"解析结果: {result}")
    except Exception as e:
        print(f"请求异常: {e}")

if __name__ == "__main__":
    debug_tushare_api()