#!/usr/bin/env python3
"""
飞书多维表格解决方案状态报告
显示系统状态和用户操作指南
"""

import json
import os
from datetime import datetime
from agents.feishu_bitable_agent import FeishuBitableAgent

def main():
    print("=" * 80)
    print("🎯 股票投资分析系统 - 飞书多维表格解决方案")
    print("=" * 80)
    print(f"📅 报告时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 初始化飞书多维表格Agent
    try:
        with open('config/settings.json', 'r', encoding='utf-8') as f:
            settings = json.load(f)
        
        with open('config/api_keys.json', 'r', encoding='utf-8') as f:
            api_keys = json.load(f)
            
        agent = FeishuBitableAgent(api_keys, settings)
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        agent = None
    
    # 显示系统状态
    print("🔍 系统状态检查:")
    print("-" * 40)
    
    try:
        # 检查飞书连接
        token = agent.bitable_manager.get_access_token()
        print("✅ 飞书API连接: 正常")
        print(f"   访问令牌: {token[:20]}...")
    except Exception as e:
        print(f"❌ 飞书API连接: 失败 - {e}")
        return
    
    # 显示数据状态
    print("\n📊 数据状态:")
    print("-" * 40)
    
    # 检查本地数据文件
    data_files = {
        'positions': 'data/feishu_sync/positions_data.json',
        'trades': 'data/feishu_sync/trades_data.json',
        'price_history': 'data/feishu_sync/price_history_data.json',
        'analysis': 'data/feishu_sync/analysis_data.json'
    }
    
    for table_name, file_path in data_files.items():
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    record_count = len(data) if isinstance(data, list) else 0
                print(f"✅ {table_name}: {record_count} 条记录")
            except Exception as e:
                print(f"❌ {table_name}: 读取失败 - {e}")
        else:
            print(f"⚠️  {table_name}: 无数据文件")
    
    # 显示CSV导出状态
    print("\n📁 CSV导出状态:")
    print("-" * 40)
    
    export_files = {
        '持仓记录': 'data/feishu_export/持仓记录.csv',
        '买卖记录': 'data/feishu_export/买卖记录.csv',
        '价格历史': 'data/feishu_export/价格历史.csv',
        '分析结果': 'data/feishu_export/分析结果.csv'
    }
    
    for table_name, file_path in export_files.items():
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    record_count = len(lines) - 1 if lines else 0  # 减去标题行
                print(f"✅ {table_name}: {record_count} 条记录")
                print(f"   文件路径: {file_path}")
            except Exception as e:
                print(f"❌ {table_name}: 读取失败 - {e}")
        else:
            print(f"⚠️  {table_name}: 无CSV文件")
    
    # 显示飞书应用信息
    print("\n🔗 飞书应用信息:")
    print("-" * 40)
    
    # 尝试获取最新的应用信息
    try:
        # 从配置文件中读取应用token
        config_file = 'config/feishu_app_config.json'
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                app_token = config.get('app_token')
                if app_token:
                    print(f"✅ 应用Token: {app_token}")
                    app_url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}"
                    print(f"✅ 应用链接: {app_url}")
                else:
                    print("⚠️  应用Token未找到")
        else:
            print("⚠️  配置文件不存在")
    except Exception as e:
        print(f"❌ 读取配置失败: {e}")
    
    # 显示用户操作指南
    print("\n📋 用户操作指南:")
    print("-" * 40)
    print("1. 📱 访问飞书应用链接，手动创建4个表格:")
    print("   - 持仓记录 (positions)")
    print("   - 买卖记录 (trades)")
    print("   - 价格历史 (price_history)")
    print("   - 分析结果 (analysis)")
    print()
    print("2. 📊 使用CSV文件导入数据:")
    print("   - 在 data/feishu_export/ 目录中找到导出的CSV文件")
    print("   - 在飞书表格中使用'导入CSV'功能")
    print("   - 确保字段映射正确")
    print()
    print("3. 🔄 数据同步说明:")
    print("   - 系统会自动同步交易记录到本地文件")
    print("   - 定期运行 'python3 test_complete_feishu_solution.py' 导出最新CSV")
    print("   - 手动将CSV文件导入到飞书表格")
    print()
    print("4. 📈 直接在飞书中操作:")
    print("   - 在'买卖记录'表格中直接添加交易记录")
    print("   - 在'持仓记录'表格中查看当前持仓")
    print("   - 在'分析结果'表格中查看投资分析")
    print()
    print("5. 🚀 系统功能:")
    print("   - 自动更新股票价格")
    print("   - 自动分析投资组合")
    print("   - 自动发送邮件报告")
    print("   - 自动AI智能分析")
    
    print("\n" + "=" * 80)
    print("✅ 飞书多维表格解决方案已就绪")
    print("📧 如有问题，请查看系统日志或联系技术支持")
    print("=" * 80)

if __name__ == "__main__":
    main()