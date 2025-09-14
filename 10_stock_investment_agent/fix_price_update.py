#!/usr/bin/env python3
"""
股票价格更新问题诊断和修复工具
"""

import sys
import subprocess
import json
from datetime import datetime

def check_package_installation():
    """检查并安装必要的Python包"""
    print("=" * 60)
    print("🔍 检查Python包安装状态")
    print("=" * 60)
    
    required_packages = [
        ('tushare', 'tushare'),
        ('alpha_vantage', 'alpha-vantage'),
        ('pandas', 'pandas'),
        ('requests', 'requests'),
        ('yfinance', 'yfinance'),
        ('loguru', 'loguru')
    ]
    
    missing_packages = []
    
    for package_name, pip_name in required_packages:
        try:
            __import__(package_name)
            print(f"✅ {package_name}: 已安装")
        except ImportError:
            print(f"❌ {package_name}: 未安装")
            missing_packages.append(pip_name)
    
    if missing_packages:
        print(f"\n📦 需要安装的包: {', '.join(missing_packages)}")
        return missing_packages
    else:
        print("\n✅ 所有依赖包已安装")
        return []

def install_packages(packages):
    """安装缺失的包"""
    if not packages:
        return True
    
    print("\n🔧 开始安装Python包...")
    for package in packages:
        try:
            print(f"⬇️  安装 {package}...")
            result = subprocess.run([sys.executable, '-m', 'pip', 'install', package], 
                                  capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print(f"✅ {package} 安装成功")
            else:
                print(f"❌ {package} 安装失败: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"❌ {package} 安装超时")
            return False
        except Exception as e:
            print(f"❌ {package} 安装异常: {e}")
            return False
    
    return True

def test_api_connections():
    """测试API连接"""
    print("\n" + "=" * 60)
    print("🌐 测试API连接")
    print("=" * 60)
    
    try:
        # 测试Alpha Vantage
        from alpha_vantage.timeseries import TimeSeries
        print("✅ Alpha Vantage导入成功")
    except ImportError:
        print("❌ Alpha Vantage导入失败")
    
    try:
        import tushare as ts
        print("✅ TuShare导入成功")
    except ImportError:
        print("❌ TuShare导入失败")
    
    try:
        import yfinance as yf
        print("✅ Yahoo Finance导入成功")
    except ImportError:
        print("❌ Yahoo Finance导入失败")

def test_price_fetching():
    """测试价格获取功能"""
    print("\n" + "=" * 60)
    print("💰 测试股票价格获取")
    print("=" * 60)
    
    try:
        import yfinance as yf
        
        # 测试股票
        test_symbols = ['AAPL', '000001.SZ', '0700.HK']
        
        for symbol in test_symbols:
            try:
                ticker = yf.Ticker(symbol)
                data = ticker.history(period='1d')
                
                if not data.empty:
                    price = data['Close'].iloc[-1]
                    print(f"✅ {symbol}: ¥{price:.2f}")
                else:
                    print(f"❌ {symbol}: 无数据")
                    
            except Exception as e:
                print(f"❌ {symbol}: 获取失败 - {e}")
                
    except ImportError:
        print("❌ yfinance未安装，无法测试")

def check_portfolio_data():
    """检查投资组合数据"""
    print("\n" + "=" * 60)
    print("📊 检查投资组合数据")
    print("=" * 60)
    
    try:
        with open('data/portfolio.json', 'r', encoding='utf-8') as f:
            portfolio = json.load(f)
        
        positions = portfolio.get('positions', [])
        print(f"📈 持仓数量: {len(positions)}")
        
        for position in positions:
            symbol = position.get('symbol', 'N/A')
            market_type = position.get('market_type', 'N/A')
            quantity = position.get('quantity', 0)
            print(f"   {symbol} ({market_type}): {quantity}股")
            
        return True
        
    except FileNotFoundError:
        print("❌ 投资组合文件不存在")
        return False
    except Exception as e:
        print(f"❌ 读取投资组合数据失败: {e}")
        return False

def main():
    print("🎯 股票价格更新问题诊断工具")
    print(f"📅 运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 检查包安装
    missing_packages = check_package_installation()
    
    # 2. 安装缺失的包
    if missing_packages:
        print(f"\n⚠️  发现缺失的包，开始安装...")
        if not install_packages(missing_packages):
            print("❌ 包安装失败，请手动安装")
            return
    
    # 3. 重新检查
    print("\n🔍 重新检查包安装状态...")
    missing_packages = check_package_installation()
    
    if missing_packages:
        print("❌ 仍有包未安装，价格更新可能失败")
        return
    
    # 4. 测试API连接
    test_api_connections()
    
    # 5. 测试价格获取
    test_price_fetching()
    
    # 6. 检查投资组合数据
    check_portfolio_data()
    
    print("\n" + "=" * 60)
    print("✅ 诊断完成")
    print("=" * 60)
    print("\n💡 如果问题仍然存在，请检查:")
    print("1. 网络连接是否正常")
    print("2. API密钥是否有效")
    print("3. 股票代码格式是否正确")

if __name__ == "__main__":
    main()