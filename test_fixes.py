#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试股票投资组合系统修复
"""

import requests
import json
import time

# API配置
API_BASE_URL = "https://stock-portfolio-api-nd2p.onrender.com/api"

def test_api_health():
    """测试API健康状态"""
    print("=== 测试API健康状态 ===")
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API服务正常: {data}")
            return True
        else:
            print(f"❌ API服务异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API连接失败: {e}")
        return False

def test_stock_data():
    """测试股票数据获取"""
    print("\n=== 测试股票数据获取 ===")
    
    test_stocks = [
        ("600036", "A股", "招商银行"),
        ("AAPL", "美股", "苹果"),
        ("700", "港股", "腾讯控股"),
        ("160633", "基金", "华夏行业")
    ]
    
    for code, market, name in test_stocks:
        print(f"\n测试 {market} {name} ({code}):")
        
        try:
            if market == "A股":
                response = requests.get(f"{API_BASE_URL}/stock/a/{code}", timeout=10)
            elif market == "美股":
                response = requests.get(f"{API_BASE_URL}/stock/us/{code}", timeout=10)
            elif market == "港股":
                response = requests.get(f"{API_BASE_URL}/stock/hk/{code}", timeout=10)
            elif market == "基金":
                response = requests.get(f"{API_BASE_URL}/fund/{code}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    stock_info = data.get("data", {})
                    price = stock_info.get("price", 0)
                    print(f"  ✅ 获取成功: 价格={price}")
                else:
                    print(f"  ❌ 获取失败: {data.get('error')}")
            else:
                print(f"  ❌ 请求失败: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ 连接失败: {e}")

def test_portfolio():
    """测试投资组合数据"""
    print("\n=== 测试投资组合数据 ===")
    try:
        response = requests.get(f"{API_BASE_URL}/portfolio", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                portfolio = data.get("data", {})
                positions = portfolio.get("positions", [])
                summary = portfolio.get("summary", {})
                
                print(f"✅ 投资组合数据获取成功")
                print(f"  持仓数量: {len(positions)}")
                print(f"  总资产: {summary.get('totalAssets', 0):.2f}")
                print(f"  总盈亏: {summary.get('totalProfit', 0):.2f}")
                
                # 显示前3个持仓
                for i, pos in enumerate(positions[:3]):
                    print(f"  {i+1}. {pos['name']} ({pos['code']}): {pos['quantity']}股, 成本价:{pos['costPrice']:.2f}")
            else:
                print(f"❌ 获取失败: {data.get('error')}")
        else:
            print(f"❌ 请求失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 连接失败: {e}")

def test_transactions():
    """测试交易记录"""
    print("\n=== 测试交易记录 ===")
    try:
        response = requests.get(f"{API_BASE_URL}/transactions", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                transactions = data.get("data", [])
                print(f"✅ 交易记录获取成功")
                print(f"  交易记录数量: {len(transactions)}")
                
                # 显示最近3条交易
                for i, trans in enumerate(transactions[:3]):
                    print(f"  {i+1}. {trans['date']} {trans['type']} {trans['name']} {trans['quantity']}股")
            else:
                print(f"❌ 获取失败: {data.get('error')}")
        else:
            print(f"❌ 请求失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 连接失败: {e}")

def test_add_transaction():
    """测试添加交易记录"""
    print("\n=== 测试添加交易记录 ===")
    
    # 测试数据
    test_transaction = {
        "type": "买入",
        "code": "000001",
        "name": "平安银行",
        "market": "A股",
        "price": 10.50,
        "quantity": 100,
        "commission": 5.00
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/transactions",
            json=test_transaction,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print(f"✅ 交易记录添加成功")
                new_trans = data.get("data", {})
                print(f"  新交易ID: {new_trans.get('id')}")
                return new_trans.get('id')
            else:
                print(f"❌ 添加失败: {data.get('error')}")
        else:
            print(f"❌ 请求失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 连接失败: {e}")
    
    return None

def test_delete_transaction(transaction_id):
    """测试删除交易记录"""
    if not transaction_id:
        print("⚠️  跳过删除测试（没有交易ID）")
        return
        
    print(f"\n=== 测试删除交易记录 (ID: {transaction_id}) ===")
    
    try:
        response = requests.delete(f"{API_BASE_URL}/transactions/{transaction_id}", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print(f"✅ 交易记录删除成功")
                deleted_trans = data.get("data", {})
                print(f"  删除的交易: {deleted_trans.get('name')} {deleted_trans.get('quantity')}股")
            else:
                print(f"❌ 删除失败: {data.get('error')}")
        else:
            print(f"❌ 请求失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 连接失败: {e}")

def main():
    """主测试函数"""
    print("开始测试股票投资组合系统修复...")
    print(f"API地址: {API_BASE_URL}")
    
    # 测试API健康状态
    if not test_api_health():
        print("\n❌ API服务不可用，停止测试")
        return
    
    # 测试股票数据获取
    test_stock_data()
    
    # 测试投资组合
    test_portfolio()
    
    # 测试交易记录
    test_transactions()
    
    # 测试添加和删除交易记录
    new_transaction_id = test_add_transaction()
    time.sleep(2)  # 等待2秒
    
    # 获取最新的投资组合和交易记录
    test_portfolio()
    test_transactions()
    
    # 测试删除交易记录
    test_delete_transaction(new_transaction_id)
    time.sleep(2)  # 等待2秒
    
    # 最终验证
    print("\n=== 最终验证 ===")
    test_portfolio()
    test_transactions()
    
    print("\n测试完成！")

if __name__ == "__main__":
    main()