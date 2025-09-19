#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试数据库API功能
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_health_check():
    """测试健康检查"""
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✓ 健康检查通过:", data)
            return True
        else:
            print("✗ 健康检查失败:", response.status_code)
            return False
    except Exception as e:
        print("✗ 健康检查异常:", e)
        return False

def test_portfolio():
    """测试投资组合数据"""
    try:
        response = requests.get(f"{BASE_URL}/api/portfolio", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                positions = data.get("positions", [])
                summary = data.get("summary", {})
                print(f"✓ 投资组合数据获取成功，共{len(positions)}个持仓")
                print(f"  总资产: {summary.get('totalAssets', 0):,.2f}")
                print(f"  总市值: {summary.get('totalValue', 0):,.2f}")
                print(f"  现金余额: {summary.get('cashBalance', 0):,.2f}")
                print(f"  总盈亏: {summary.get('totalProfit', 0):,.2f}")
                return True
            else:
                print("✗ 投资组合数据获取失败:", data.get("error"))
                return False
        else:
            print("✗ 投资组合API错误:", response.status_code)
            return False
    except Exception as e:
        print("✗ 投资组合API异常:", e)
        return False

def test_transactions():
    """测试交易记录"""
    try:
        response = requests.get(f"{BASE_URL}/api/transactions", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                transactions = data.get("data", [])
                print(f"✓ 交易记录获取成功，共{len(transactions)}条记录")
                return True
            else:
                print("✗ 交易记录获取失败:", data.get("error"))
                return False
        else:
            print("✗ 交易记录API错误:", response.status_code)
            return False
    except Exception as e:
        print("✗ 交易记录API异常:", e)
        return False

def test_add_transaction():
    """测试添加交易记录"""
    try:
        transaction_data = {
            "type": "买入",
            "code": "000001",
            "name": "平安银行",
            "market": "A股",
            "price": 12.50,
            "quantity": 100
        }

        response = requests.post(f"{BASE_URL}/api/transactions", json=transaction_data, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✓ 交易记录添加成功:", data.get("message"))
                return data.get("data", {}).get("id")
            else:
                print("✗ 交易记录添加失败:", data.get("error"))
                return None
        else:
            print("✗ 添加交易记录API错误:", response.status_code)
            return None
    except Exception as e:
        print("✗ 添加交易记录API异常:", e)
        return None

def test_delete_transaction(transaction_id):
    """测试删除交易记录"""
    if not transaction_id:
        return False

    try:
        response = requests.delete(f"{BASE_URL}/api/transactions/{transaction_id}", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✓ 交易记录删除成功:", data.get("message"))
                return True
            else:
                print("✗ 交易记录删除失败:", data.get("error"))
                return False
        else:
            print("✗ 删除交易记录API错误:", response.status_code)
            return False
    except Exception as e:
        print("✗ 删除交易记录API异常:", e)
        return False

def test_stock_data():
    """测试股票数据获取"""
    try:
        # 测试A股数据
        response = requests.get(f"{BASE_URL}/api/stock/a/000001", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✓ A股数据获取成功:", data.get("data", {}).get("name"))
            else:
                print("✗ A股数据获取失败:", data.get("error"))

        # 测试美股数据
        response = requests.get(f"{BASE_URL}/api/stock/us/AAPL", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✓ 美股数据获取成功:", data.get("data", {}).get("name"))
            else:
                print("✗ 美股数据获取失败:", data.get("error"))

        # 测试港股数据
        response = requests.get(f"{BASE_URL}/api/stock/hk/00700", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✓ 港股数据获取成功:", data.get("data", {}).get("name"))
            else:
                print("✗ 港股数据获取失败:", data.get("error"))

        return True
    except Exception as e:
        print("✗ 股票数据API异常:", e)
        return False

def main():
    """主测试函数"""
    print("=" * 50)
    print("股票投资组合系统API测试")
    print("=" * 50)

    # 等待服务器启动
    print("等待服务器启动...")
    time.sleep(3)

    tests = [
        ("健康检查", test_health_check),
        ("投资组合数据", test_portfolio),
        ("交易记录", test_transactions),
        ("股票数据", test_stock_data),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        if test_func():
            passed += 1

    print(f"\n--- 动态交易测试 ---")
    transaction_id = test_add_transaction()
    if transaction_id:
        print("测试添加交易记录后重新获取投资组合...")
        time.sleep(1)
        if test_portfolio():
            passed += 1
            total += 1

        print("测试删除交易记录后重新获取投资组合...")
        if test_delete_transaction(transaction_id):
            time.sleep(1)
            if test_portfolio():
                passed += 1
                total += 1

    print("\n" + "=" * 50)
    print(f"测试结果: {passed}/{total} 通过")
    print("=" * 50)

    if passed == total:
        print("🎉 所有测试通过！系统运行正常。")
    else:
        print("⚠️  部分测试失败，请检查系统配置。")

if __name__ == "__main__":
    main()