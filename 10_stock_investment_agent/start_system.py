#!/usr/bin/env python3
"""
股票投资分析系统启动脚本
提供简单的命令行界面来运行系统
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from main_agent import MainAgent
from loguru import logger


def show_menu():
    """显示主菜单"""
    print("\n" + "="*50)
    print("🚀 股票投资分析管理系统")
    print("="*50)
    print("1. 启动系统")
    print("2. 查看系统状态")
    print("3. 添加买入记录")
    print("4. 添加卖出记录")
    print("5. 获取投资组合摘要")
    print("6. 发送测试通知")
    print("7. 运行AI分析")
    print("8. 退出系统")
    print("="*50)


def start_system():
    """启动系统"""
    try:
        agent = MainAgent()
        agent.start()
        print("✅ 系统启动成功！")
        return agent
    except Exception as e:
        print(f"❌ 系统启动失败: {e}")
        return None


def show_status(agent):
    """显示系统状态"""
    try:
        status = agent.get_system_status()
        print(f"\n📊 系统状态: {status.get('status', 'unknown')}")
        print(f"🏢 运行时间: {status.get('uptime', 'N/A')}")
        print(f"📈 Agent状态: {len(status.get('agents', {}))} 个Agent运行中")
        
        for agent_name, agent_status in status.get('agents', {}).items():
            print(f"  - {agent_name}: {agent_status.get('status', 'unknown')}")
    except Exception as e:
        print(f"❌ 获取状态失败: {e}")


def add_buy_record(agent):
    """添加买入记录"""
    try:
        print("\n📝 添加买入记录")
        symbol = input("股票代码: ")
        name = input("股票名称: ")
        market_type = input("市场类型 (us_stocks/a_stocks/hk_stocks/funds): ")
        buy_price = float(input("买入价格: "))
        quantity = int(input("买入数量: "))
        notes = input("备注 (可选): ")
        
        record = {
            'symbol': symbol,
            'name': name,
            'market_type': market_type,
            'buy_price': buy_price,
            'quantity': quantity,
            'notes': notes
        }
        
        result = agent.add_buy_record(record)
        if result.get('success'):
            print("✅ 买入记录添加成功")
        else:
            print(f"❌ 添加失败: {result.get('error')}")
    except Exception as e:
        print(f"❌ 输入错误: {e}")


def add_sell_record(agent):
    """添加卖出记录"""
    try:
        print("\n📝 添加卖出记录")
        symbol = input("股票代码: ")
        sell_price = float(input("卖出价格: "))
        quantity = int(input("卖出数量: "))
        notes = input("备注 (可选): ")
        
        record = {
            'symbol': symbol,
            'sell_price': sell_price,
            'quantity': quantity,
            'notes': notes
        }
        
        result = agent.add_sell_record(record)
        if result.get('success'):
            print("✅ 卖出记录添加成功")
        else:
            print(f"❌ 添加失败: {result.get('error')}")
    except Exception as e:
        print(f"❌ 输入错误: {e}")


def get_portfolio_summary(agent):
    """获取投资组合摘要"""
    try:
        result = agent.get_portfolio_summary()
        if result.get('success'):
            summary = result.get('summary', {})
            print(f"\n📊 投资组合摘要")
            print(f"总市值: ¥{summary.get('total_value', 0):,.2f}")
            print(f"总成本: ¥{summary.get('total_cost', 0):,.2f}")
            print(f"总盈亏: ¥{summary.get('total_profit_loss', 0):,.2f}")
            print(f"盈亏比例: {summary.get('total_profit_loss_percent', 0):.2f}%")
            print(f"持仓数量: {summary.get('positions_count', 0)}")
        else:
            print(f"❌ 获取失败: {result.get('error')}")
    except Exception as e:
        print(f"❌ 获取失败: {e}")


def send_test_notification(agent):
    """发送测试通知"""
    try:
        result = agent.agents['notification'].send_test_notification()
        if result.get('success'):
            print("✅ 测试通知发送成功")
        else:
            print(f"❌ 发送失败: {result.get('error')}")
    except Exception as e:
        print(f"❌ 发送失败: {e}")


def run_ai_analysis(agent):
    """运行AI分析"""
    try:
        print("\n🧠 正在运行AI分析...")
        result = agent.agents['ai_analyzer'].run_analysis()
        if result.get('success'):
            print("✅ AI分析完成")
            print(f"分析了 {result.get('analyzed_positions', 0)} 个持仓")
            print(f"生成了 {len(result.get('alerts', []))} 个预警")
        else:
            print(f"❌ 分析失败: {result.get('error')}")
    except Exception as e:
        print(f"❌ 分析失败: {e}")


def main():
    """主函数"""
    agent = None
    
    while True:
        show_menu()
        choice = input("\n请选择操作 (1-8): ")
        
        if choice == '1':
            agent = start_system()
        elif choice == '2':
            if agent:
                show_status(agent)
            else:
                print("❌ 请先启动系统")
        elif choice == '3':
            if agent:
                add_buy_record(agent)
            else:
                print("❌ 请先启动系统")
        elif choice == '4':
            if agent:
                add_sell_record(agent)
            else:
                print("❌ 请先启动系统")
        elif choice == '5':
            if agent:
                get_portfolio_summary(agent)
            else:
                print("❌ 请先启动系统")
        elif choice == '6':
            if agent:
                send_test_notification(agent)
            else:
                print("❌ 请先启动系统")
        elif choice == '7':
            if agent:
                run_ai_analysis(agent)
            else:
                print("❌ 请先启动系统")
        elif choice == '8':
            print("👋 感谢使用股票投资分析管理系统！")
            if agent:
                agent.stop()
            break
        else:
            print("❌ 无效选择，请重新输入")
        
        input("\n按回车键继续...")


if __name__ == "__main__":
    main()