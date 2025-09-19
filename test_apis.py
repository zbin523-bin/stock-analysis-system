#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试TuShare API
"""

import requests
import json
import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.app import EnhancedStockScraper

def test_tushare_api():
    """测试TuShare API"""
    print("开始测试TuShare API...")

    # 创建爬虫实例
    scraper = EnhancedStockScraper()

    # 测试A股代码
    test_codes = ['600036', '000001', '600519']

    for code in test_codes:
        print(f"\n测试A股代码: {code}")

        # 测试TuShare API
        try:
            data = scraper._scrape_tushare_a(code)
            if data:
                print(f"OK TuShare API成功: {data}")
            else:
                print("ERROR TuShare API失败")
        except Exception as e:
            print(f"ERROR TuShare API异常: {e}")

        # 测试新浪财经API
        try:
            data = scraper._scrape_sina_a(code)
            if data:
                print(f"OK 新浪财经API成功: {data['name']} - {data['price']}")
            else:
                print("ERROR 新浪财经API失败")
        except Exception as e:
            print(f"ERROR 新浪财经API异常: {e}")

def test_portfolio_api():
    """测试Portfolio API"""
    print("\n测试Portfolio API...")

    try:
        response = requests.get("http://localhost:5000/api/health")
        if response.status_code == 200:
            print("OK API服务器正常运行")

            response = requests.get("http://localhost:5000/api/portfolio")
            if response.status_code == 200:
                data = response.json()
                print(f"OK Portfolio API成功，返回 {len(data.get('positions', []))} 个持仓")

                # 检查前几个持仓的数据
                for i, pos in enumerate(data.get('positions', [])[:3]):
                    print(f"  持仓 {i+1}: {pos['name']} ({pos['code']})")
                    print(f"    当前价: {pos['currentPrice']}")
                    print(f"    成本价: {pos['costPrice']}")
                    print(f"    累计涨跌额: {pos.get('cumulativeChange', 'N/A')}")
                    print(f"    累计涨跌幅: {pos.get('cumulativeChangePercent', 'N/A')}%")
                    print(f"    实时数据: {pos.get('hasRealTimeData', False)}")
            else:
                print(f"ERROR Portfolio API失败: {response.status_code}")
        else:
            print(f"ERROR API服务器异常: {response.status_code}")
    except Exception as e:
        print(f"ERROR API测试异常: {e}")

if __name__ == "__main__":
    test_tushare_api()
    test_portfolio_api()