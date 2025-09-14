#!/usr/bin/env python3
"""
测试修复后的价格获取功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.simple_price_fetcher import get_stock_price, get_batch_prices
from datetime import datetime

def test_price_fetching():
    """测试价格获取功能"""
    print("=" * 60)
    print("🧪 测试修复后的股票价格获取功能")
    print("=" * 60)
    
    # 测试股票列表
    test_stocks = [
        ('AAPL', 'us_stocks'),
        ('000001', 'a_stocks'),
        ('0700', 'hk_stocks'),
        ('510300', 'a_stocks')  # 基金
    ]
    
    print(f"📅 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    for symbol, market_type in test_stocks:
        print(f"🔍 正在获取 {symbol} ({market_type})...")
        
        try:
            result = get_stock_price(symbol, market_type)
            
            if 'error' in result:
                print(f"   ❌ 失败: {result['error']}")
            else:
                print(f"   ✅ 成功:")
                print(f"      💰 价格: ¥{result['price']:.2f}")
                print(f"      📈 涨跌: {result['change_percent']:.2f}%")
                print(f"      💱 货币: {result['currency']}")
                print(f"      📊 交易量: {result['volume']:,}")
                
        except Exception as e:
            print(f"   ❌ 异常: {e}")
        
        print()
    
    # 测试批量获取
    print("🔍 测试批量获取...")
    try:
        batch_result = get_batch_prices(test_stocks)
        
        success_count = 0
        failed_count = 0
        
        for symbol, result in batch_result.items():
            if 'error' in result:
                failed_count += 1
            else:
                success_count += 1
        
        print(f"   📊 批量获取结果: 成功 {success_count}, 失败 {failed_count}")
        
    except Exception as e:
        print(f"   ❌ 批量获取异常: {e}")

def main():
    try:
        test_price_fetching()
        
        print("\n" + "=" * 60)
        print("✅ 价格获取测试完成")
        print("=" * 60)
        
    except ImportError as e:
        print("❌ 导入错误，请确保已安装yfinance包")
        print(f"   错误: {e}")
        print("   安装命令: pip3 install yfinance")
        
    except Exception as e:
        print(f"❌ 测试过程中发生异常: {e}")

if __name__ == "__main__":
    main()