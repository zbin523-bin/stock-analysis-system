#!/usr/bin/env python3
"""
飞书应用查看和检查指南
帮助用户找到和使用飞书多维表格应用
"""

import json
import webbrowser
from datetime import datetime
from agents.feishu_bitable_agent import FeishuBitableAgent

def check_feishu_app_status():
    """检查飞书应用状态"""
    print("=" * 80)
    print("🔍 飞书应用状态检查")
    print("=" * 80)
    
    try:
        # 初始化飞书代理
        with open('config/settings.json', 'r', encoding='utf-8') as f:
            settings = json.load(f)
        
        with open('config/api_keys.json', 'r', encoding='utf-8') as f:
            api_keys = json.load(f)
            
        agent = FeishuBitableAgent(api_keys, settings)
        
        # 检查访问令牌
        token = agent.bitable_manager.get_access_token()
        print(f"✅ 飞书访问令牌: {token[:20]}...")
        
        # 尝试获取应用信息
        app_info = agent.get_app_info()
        if app_info:
            print(f"✅ 应用Token: {app_info.get('app_token', 'N/A')}")
            print(f"✅ 应用名称: {app_info.get('name', 'N/A')}")
            print(f"✅ 应用URL: {app_info.get('url', 'N/A')}")
        else:
            print("⚠️  无法获取应用信息")
            
        return True
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        return False

def show_feishu_access_guide():
    """显示飞书应用访问指南"""
    print("\n" + "=" * 80)
    print("📱 飞书应用访问指南")
    print("=" * 80)
    
    print("🔗 飞书应用链接:")
    print("https://open.feishu.cn/open-apis/bitable/v1/apps/RqegbSWNZaINbOsAusQcJ7cJnif")
    print()
    
    print("📋 如何访问飞书应用:")
    print("-" * 40)
    print("1. 🌐 在浏览器中打开上述链接")
    print("2. 🔑 使用您的飞书账号登录")
    print("3. 📱 进入飞书工作台")
    print("4. 🔍 搜索'股票投资分析管理系统'")
    print("5. 📊 打开多维表格应用")
    print()
    
    print("🛠️ 如果看不到应用，请尝试:")
    print("-" * 40)
    print("1. 确认您有访问权限")
    print("2. 检查应用是否已发布")
    print("3. 联系飞书管理员")
    print("4. 尝试在飞书工作台中手动添加应用")
    print()
    
    print("📝 应用配置信息:")
    print("-" * 40)
    print(f"应用ID: cli_a84bed3e7b7a500c")
    print(f"应用Token: RqegbSWNZaINbOsAusQcJ7cJnif")
    print(f"创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    print("📊 需要创建的表格:")
    print("-" * 40)
    print("1. 持仓记录 (positions)")
    print("   - 字段: 股票代码, 股票名称, 市场类型, 买入价格, 当前价格, 数量, 买入日期, 总成本, 当前价值, 盈亏, 盈亏比例, 备注")
    print()
    print("2. 买卖记录 (trades)")
    print("   - 字段: 股票代码, 股票名称, 交易类型, 价格, 数量, 金额, 交易日期, 备注")
    print()
    print("3. 价格历史 (price_history)")
    print("   - 字段: 股票代码, 价格, 时间戳, 涨跌幅")
    print()
    print("4. 分析结果 (analysis)")
    print("   - 字段: 股票代码, 分析类型, 建议, 置信度, 分析日期, 备注")

def show_troubleshooting():
    """显示故障排除指南"""
    print("\n" + "=" * 80)
    print("🔧 故障排除指南")
    print("=" * 80)
    
    print("❌ 常见问题及解决方案:")
    print("-" * 40)
    
    print("1. 问题: 点击链接提示'无权限访问'")
    print("   解决方案:")
    print("   - 确认使用正确的飞书账号")
    print("   - 联系应用管理员分配权限")
    print("   - 检查账号是否被禁用")
    print()
    
    print("2. 问题: 应用显示'不存在'或'已删除'")
    print("   解决方案:")
    print("   - 检查应用Token是否正确")
    print("   - 重新创建应用")
    print("   - 联系飞书技术支持")
    print()
    
    print("3. 问题: 找不到多维表格功能")
    print("   解决方案:")
    print("   - 确认使用飞书企业版")
    print("   - 检查账号是否有权限使用多维表格")
    print("   - 更新飞书到最新版本")
    print()
    
    print("4. 问题: 无法导入CSV文件")
    print("   解决方案:")
    print("   - 检查CSV文件格式")
    print("   - 确认字段名称匹配")
    print("   - 尝试手动复制粘贴数据")
    print()

def show_csv_import_guide():
    """显示CSV导入指南"""
    print("\n" + "=" * 80)
    print("📊 CSV文件导入指南")
    print("=" * 80)
    
    print("📁 CSV文件位置:")
    print("data/feishu_export/ 目录")
    print()
    
    print("📋 可用的CSV文件:")
    print("-" * 40)
    
    import os
    
    csv_files = {
        '持仓记录': 'data/feishu_export/持仓记录.csv',
        '买卖记录': 'data/feishu_export/买卖记录.csv',
        '价格历史': 'data/feishu_export/价格历史.csv',
        '分析结果': 'data/feishu_export/分析结果.csv'
    }
    
    for table_name, file_path in csv_files.items():
        if os.path.exists(file_path):
            print(f"✅ {table_name}: {file_path}")
            
            # 显示文件大小和记录数
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    record_count = len(lines) - 1 if lines else 0
                    print(f"   记录数: {record_count}")
            except Exception as e:
                print(f"   读取失败: {e}")
        else:
            print(f"❌ {table_name}: 文件不存在")
        print()
    
    print("🔄 导入步骤:")
    print("-" * 40)
    print("1. 在飞书中打开对应的多维表格")
    print("2. 点击'导入'按钮")
    print("3. 选择'CSV文件'")
    print("4. 上传对应的CSV文件")
    print("5. 确认字段映射")
    print("6. 完成导入")

def main():
    print("🎯 飞书应用查看和检查工具")
    print(f"📅 运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 检查应用状态
    check_feishu_app_status()
    
    # 2. 显示访问指南
    show_feishu_access_guide()
    
    # 3. 显示故障排除
    show_troubleshooting()
    
    # 4. 显示CSV导入指南
    show_csv_import_guide()
    
    print("\n" + "=" * 80)
    print("✅ 飞书应用检查完成")
    print("📧 如有其他问题，请查看系统日志或联系技术支持")
    print("=" * 80)
    
    # 询问是否打开飞书链接
    try:
        open_link = input("\n🔗 是否现在打开飞书应用链接? (y/n): ").lower().strip()
        if open_link == 'y':
            webbrowser.open("https://open.feishu.cn/open-apis/bitable/v1/apps/RqegbSWNZaINbOsAusQcJ7cJnif")
            print("✅ 已在浏览器中打开飞书应用链接")
    except KeyboardInterrupt:
        print("\n👋 退出程序")

if __name__ == "__main__":
    main()