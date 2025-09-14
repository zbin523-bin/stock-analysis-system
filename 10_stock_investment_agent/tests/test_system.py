#!/usr/bin/env python3
"""
系统测试脚本
验证股票投资分析管理系统的基本功能
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_imports():
    """测试模块导入"""
    print("🔍 测试模块导入...")
    
    try:
        from main_agent import MainAgent
        print("✅ MainAgent 导入成功")
        
        from agents.data_fetching_agent import DataFetchingAgent
        print("✅ DataFetchingAgent 导入成功")
        
        from agents.portfolio_analyzer import PortfolioAnalyzer
        print("✅ PortfolioAnalyzer 导入成功")
        
        from agents.notification_agent import NotificationAgent
        print("✅ NotificationAgent 导入成功")
        
        from agents.feishu_integration import FeishuIntegrationAgent
        print("✅ FeishuIntegrationAgent 导入成功")
        
        from agents.ai_analysis_agent import AIAnalysisAgent
        print("✅ AIAnalysisAgent 导入成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 模块导入失败: {e}")
        return False

def test_config_files():
    """测试配置文件"""
    print("\n🔍 测试配置文件...")
    
    config_files = [
        'config/api_keys.json',
        'config/settings.json', 
        'config/stock_symbols.json'
    ]
    
    all_exist = True
    for config_file in config_files:
        file_path = project_root / config_file
        if file_path.exists():
            print(f"✅ {config_file} 存在")
        else:
            print(f"❌ {config_file} 不存在")
            all_exist = False
    
    return all_exist

def test_main_agent_creation():
    """测试主Agent创建"""
    print("\n🔍 测试主Agent创建...")
    
    try:
        from main_agent import MainAgent
        
        # 创建主Agent实例
        agent = MainAgent()
        print("✅ MainAgent 创建成功")
        
        # 获取系统状态
        status = agent.get_system_status()
        print(f"✅ 系统状态获取成功: {status.get('system_info', {}).get('name', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ MainAgent 创建失败: {e}")
        return False

def test_data_fetching():
    """测试数据抓取功能"""
    print("\n🔍 测试数据抓取功能...")
    
    try:
        from agents.data_fetching_agent import DataFetchingAgent
        
        # 加载配置
        import json
        with open(project_root / 'config/api_keys.json', 'r', encoding='utf-8') as f:
            api_keys = json.load(f)
        
        with open(project_root / 'config/stock_symbols.json', 'r', encoding='utf-8') as f:
            stock_symbols = json.load(f)
        
        # 创建数据抓取Agent
        agent = DataFetchingAgent(api_keys, stock_symbols)
        print("✅ DataFetchingAgent 创建成功")
        
        # 获取Agent状态
        status = agent.get_status()
        print(f"✅ Agent状态: {status.get('status', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ 数据抓取测试失败: {e}")
        return False

def test_notification_agent():
    """测试通知Agent"""
    print("\n🔍 测试通知Agent...")
    
    try:
        from agents.notification_agent import NotificationAgent
        
        # 加载配置
        import json
        with open(project_root / 'config/api_keys.json', 'r', encoding='utf-8') as f:
            api_keys = json.load(f)
        
        with open(project_root / 'config/settings.json', 'r', encoding='utf-8') as f:
            settings = json.load(f)
        
        # 创建通知Agent
        agent = NotificationAgent(api_keys, settings)
        print("✅ NotificationAgent 创建成功")
        
        # 获取Agent状态
        status = agent.get_status()
        print(f"✅ Agent状态: {status.get('status', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ 通知Agent测试失败: {e}")
        return False

def test_basic_calculation():
    """测试基础计算功能"""
    print("\n🔍 测试基础计算功能...")
    
    try:
        from utils.calculation_utils import CalculationUtils
        
        calc = CalculationUtils()
        
        # 测试盈亏计算
        result = calc.calculate_profit_loss(100, 110, 100)
        print(f"✅ 盈亏计算成功: {result.get('profit_loss', 0)}")
        
        # 测试货币格式化
        formatted = calc.format_currency(1000.50, 'CNY')
        print(f"✅ 货币格式化成功: {formatted}")
        
        return True
        
    except Exception as e:
        print(f"❌ 基础计算测试失败: {e}")
        return False

def test_date_utils():
    """测试日期工具"""
    print("\n🔍 测试日期工具...")
    
    try:
        from utils.date_utils import DateUtils
        
        date_utils = DateUtils()
        
        # 测试当前时间获取
        current_time = date_utils.get_current_time()
        print(f"✅ 当前时间获取成功: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 测试交易日判断
        is_trading = date_utils.get_trading_day(current_time)
        print(f"✅ 交易日判断成功: {is_trading}")
        
        return True
        
    except Exception as e:
        print(f"❌ 日期工具测试失败: {e}")
        return False

def run_all_tests():
    """运行所有测试"""
    print("🚀 开始系统测试...")
    print("="*50)
    
    tests = [
        test_imports,
        test_config_files,
        test_basic_calculation,
        test_date_utils,
        test_main_agent_creation,
        test_data_fetching,
        test_notification_agent
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            failed += 1
    
    print("\n" + "="*50)
    print(f"📊 测试结果:")
    print(f"✅ 通过: {passed}")
    print(f"❌ 失败: {failed}")
    print(f"📈 成功率: {passed/(passed+failed)*100:.1f}%")
    
    if failed == 0:
        print("\n🎉 所有测试通过！系统准备就绪。")
        return True
    else:
        print(f"\n⚠️  有 {failed} 个测试失败，请检查配置。")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)