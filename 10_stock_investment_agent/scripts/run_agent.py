#!/usr/bin/env python3
"""
股票投资分析管理系统启动脚本
提供简单易用的启动和管理界面
"""

import sys
import os
import json
import argparse
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from main_agent import MainAgent
from utils.logger import get_logger

logger = get_logger("startup")


def print_banner():
    """打印启动横幅"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                    股票投资分析管理系统                        ║
    ║                      Stock Investment Agent                   ║
    ║                                                              ║
    ║  功能:                                                       ║
    ║  ✅ 实时股价监控                                              ║
    ║  ✅ 投资组合分析                                              ║
    ║  ✅ AI智能分析                                                ║
    ║  ✅ 自动报告生成                                              ║
    ║  ✅ 飞书表格同步                                              ║
    ║  ✅ 邮件通知预警                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def check_dependencies():
    """检查依赖包"""
    required_packages = [
        'pandas', 'numpy', 'requests', 'schedule', 
        'pytz', 'loguru', 'tushare', 'alpha_vantage'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ 缺少依赖包: {', '.join(missing_packages)}")
        print("请运行: pip install -r requirements.txt")
        return False
    
    print("✅ 依赖包检查通过")
    return True


def check_config_files():
    """检查配置文件"""
    config_dir = Path("config")
    required_files = ['settings.json', 'api_keys.json', 'stock_symbols.json']
    
    missing_files = []
    for file_name in required_files:
        file_path = config_dir / file_name
        if not file_path.exists():
            missing_files.append(file_name)
    
    if missing_files:
        print(f"❌ 缺少配置文件: {', '.join(missing_files)}")
        return False
    
    print("✅ 配置文件检查通过")
    return True


def create_directories():
    """创建必要的目录"""
    directories = ['data', 'data/logs', 'logs']
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ 目录结构检查通过")


def install_requirements():
    """安装依赖包"""
    print("正在安装依赖包...")
    os.system("pip install -r requirements.txt")
    print("✅ 依赖包安装完成")


def setup_environment():
    """设置环境"""
    print("正在设置环境...")
    
    # 检查和安装依赖
    if not check_dependencies():
        install_requirements()
    
    # 检查配置文件
    if not check_config_files():
        print("❌ 配置文件检查失败，请检查config目录")
        return False
    
    # 创建目录
    create_directories()
    
    print("✅ 环境设置完成")
    return True


def start_agent():
    """启动Agent"""
    try:
        print("\n🚀 启动股票投资分析系统...")
        
        agent = MainAgent()
        agent.start()
        
        print("✅ 系统启动成功！")
        print("\n💡 使用说明:")
        print("  • 按 Ctrl+C 停止系统")
        print("  • 系统将自动更新价格并发送报告")
        print("  • 查看日志文件了解运行状态")
        
        # 保持运行
        import time
        try:
            while True:
                time.sleep(60)
                # 定期显示系统状态
                status = agent.get_system_status()
                uptime = status.get('uptime', 'N/A')
                print(f"\r⏱️  运行时间: {uptime}", end="", flush=True)
        except KeyboardInterrupt:
            print("\n\n🛑 正在停止系统...")
            agent.stop()
            print("✅ 系统已安全停止")
            
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        logger.error(f"启动Agent失败: {e}")


def show_system_status():
    """显示系统状态"""
    try:
        agent = MainAgent()
        status = agent.get_system_status()
        
        print("\n📊 系统状态:")
        print(f"  运行状态: {'✅ 运行中' if status.get('system_running') else '❌ 未运行'}")
        print(f"  启动时间: {status.get('start_time', 'N/A')}")
        print(f"  运行时间: {status.get('uptime', 'N/A')}")
        print(f"  系统版本: {status.get('system_info', {}).get('version', 'N/A')}")
        
        # 显示Agent状态
        agents_status = status.get('agents_status', {})
        if agents_status:
            print("\n🤖 Agent状态:")
            for agent_name, agent_status in agents_status.items():
                print(f"  {agent_name}: {agent_status.get('status', 'Unknown')}")
        
        # 显示定时任务状态
        scheduler_status = status.get('scheduler_status', {})
        if scheduler_status:
            print(f"\n⏰ 定时任务: {scheduler_status.get('total_tasks', 0)} 个任务")
            tasks = scheduler_status.get('tasks', {})
            for task_name, task_info in tasks.items():
                print(f"  {task_name}: {task_info.get('description', 'N/A')}")
        
    except Exception as e:
        print(f"❌ 获取状态失败: {e}")


def send_test_notification():
    """发送测试通知"""
    try:
        print("📧 发送测试通知...")
        
        agent = MainAgent()
        result = agent.send_test_notification()
        
        if result.get('success'):
            print("✅ 测试通知发送成功")
        else:
            print(f"❌ 测试通知发送失败: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ 发送测试通知失败: {e}")


def interactive_menu():
    """交互式菜单"""
    while True:
        print("\n" + "="*50)
        print("📈 股票投资分析管理系统")
        print("="*50)
        print("1. 启动系统")
        print("2. 查看系统状态")
        print("3. 发送测试通知")
        print("4. 安装依赖包")
        print("5. 查看使用说明")
        print("0. 退出")
        print("="*50)
        
        choice = input("\n请选择操作 (0-5): ").strip()
        
        if choice == '1':
            start_agent()
            break
        elif choice == '2':
            show_system_status()
        elif choice == '3':
            send_test_notification()
        elif choice == '4':
            install_requirements()
        elif choice == '5':
            show_help()
        elif choice == '0':
            print("👋 再见！")
            break
        else:
            print("❌ 无效选择，请重新输入")
        
        input("\n按回车键继续...")


def show_help():
    """显示帮助信息"""
    help_text = """
    📚 使用说明
    
    🚀 启动系统:
      • 选择菜单选项1或运行: python scripts/run_agent.py start
      • 系统将自动开始监控和分析
    
    📊 主要功能:
      • 实时股价更新 (每5分钟)
      • 投资组合分析 (每小时)
      • AI智能分析 (每2小时)
      • 每日报告 (18:00)
      • 每周报告 (周日18:00)
    
    📁 目录结构:
      • config/ - 配置文件
      • agents/ - Agent模块
      • utils/ - 工具模块
      • data/ - 数据存储
      • logs/ - 日志文件
    
    🔧 配置文件:
      • settings.json - 系统设置
      • api_keys.json - API密钥
      • stock_symbols.json - 股票代码映射
    
    📧 通知设置:
      • 每日18:00发送投资报告
      • 价格异常变动预警
      • 风险提醒和建议
    
    📗 飞书集成:
      • 自动同步到飞书多维表格
      • 实时更新持仓数据
      • 生成分析报告
    
    ⚠️  注意事项:
      • 确保API密钥正确配置
      • 保持网络连接稳定
      • 定期检查日志文件
    """
    print(help_text)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='股票投资分析管理系统启动器')
    parser.add_argument('--setup', action='store_true', help='设置环境')
    parser.add_argument('--start', action='store_true', help='启动系统')
    parser.add_argument('--status', action='store_true', help='查看状态')
    parser.add_argument('--test', action='store_true', help='发送测试通知')
    parser.add_argument('--interactive', action='store_true', help='交互式菜单')
    parser.add_argument('--help', action='store_true', help='显示帮助')
    
    args = parser.parse_args()
    
    # 显示横幅
    print_banner()
    
    if args.setup:
        setup_environment()
    elif args.start:
        if setup_environment():
            start_agent()
    elif args.status:
        show_system_status()
    elif args.test:
        send_test_notification()
    elif args.help:
        show_help()
    elif args.interactive:
        interactive_menu()
    else:
        # 默认进入交互式菜单
        interactive_menu()


if __name__ == "__main__":
    main()