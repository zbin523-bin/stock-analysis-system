#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设置每日定时分析任务
"""

import os
import subprocess
import platform
import getpass
from datetime import datetime

def create_cron_job():
    """创建Linux/Mac定时任务"""
    # 获取当前脚本路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    analyzer_path = os.path.join(current_dir, "stock_analyzer_yahoo.py")
    
    # 创建cron任务（每天下午4点30分运行）
    cron_job = f"30 16 * * * cd {current_dir} && python3 {analyzer_path}\n"
    
    print("正在设置定时任务...")
    print(f"定时任务内容: {cron_job}")
    
    # 添加到crontab
    try:
        # 获取现有crontab
        result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
        existing_cron = result.stdout if result.returncode == 0 else ""
        
        # 检查是否已存在
        if analyzer_path in existing_cron:
            print("✅ 定时任务已存在")
            return True
        
        # 添加新任务
        new_cron = existing_cron + cron_job
        process = subprocess.Popen(['crontab', '-'], stdin=subprocess.PIPE, text=True)
        process.communicate(input=new_cron)
        
        print("✅ 定时任务设置成功")
        print(f"⏰ 将在每天 16:30 自动运行股票分析")
        return True
        
    except Exception as e:
        print(f"❌ 设置定时任务失败: {e}")
        return False

def create_launchd_plist():
    """创建macOS launchd服务"""
    import plistlib
    
    # 获取当前用户信息
    username = getpass.getuser()
    current_dir = os.path.dirname(os.path.abspath(__file__))
    analyzer_path = os.path.join(current_dir, "stock_analyzer_yahoo.py")
    
    # 创建plist文件
    plist_data = {
        'Label': 'com.user.stockanalyzer',
        'ProgramArguments': [
            '/usr/bin/python3',
            analyzer_path
        ],
        'WorkingDirectory': current_dir,
        'StartCalendarInterval': {
            'Hour': 16,
            'Minute': 30
        },
        'RunAtLoad': False,
        'StandardOutPath': os.path.join(current_dir, 'stock_analyzer.log'),
        'StandardErrorPath': os.path.join(current_dir, 'stock_analyzer_error.log'),
    }
    
    plist_path = os.path.expanduser(f'~/Library/LaunchAgents/com.user.stockanalyzer.plist')
    
    try:
        # 写入plist文件
        with open(plist_path, 'wb') as f:
            plistlib.dump(plist_data, f)
        
        # 加载服务
        subprocess.run(['launchctl', 'load', plist_path])
        
        print("✅ macOS定时服务设置成功")
        print(f"⏰ 将在每天 16:30 自动运行股票分析")
        print(f"📝 日志文件: {current_dir}/stock_analyzer.log")
        return True
        
    except Exception as e:
        print(f"❌ 设置macOS服务失败: {e}")
        return False

def create_windows_task():
    """创建Windows计划任务"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    analyzer_path = os.path.join(current_dir, "stock_analyzer_yahoo.py")
    
    try:
        # 创建计划任务
        cmd = f'''
        schtasks /create /tn "股票分析" /tr "python3 {analyzer_path}" /sc daily /st 16:30 /f
        '''
        subprocess.run(cmd, shell=True, check=True)
        
        print("✅ Windows计划任务设置成功")
        print(f"⏰ 将在每天 16:30 自动运行股票分析")
        return True
        
    except Exception as e:
        print(f"❌ 设置Windows计划任务失败: {e}")
        return False

def main():
    print("=" * 60)
    print("🚀 股票分析系统 - 定时任务设置")
    print("=" * 60)
    
    system = platform.system()
    
    print(f"🖥️  检测到系统: {system}")
    
    if system == "Darwin":  # macOS
        print("🍎 使用 launchd 设置定时任务...")
        success = create_launchd_plist()
    elif system == "Linux":
        print("🐧 使用 crontab 设置定时任务...")
        success = create_cron_job()
    elif system == "Windows":
        print("🪟 使用计划任务设置定时任务...")
        success = create_windows_task()
    else:
        print(f"❌ 不支持的系统: {system}")
        success = False
    
    if success:
        print("\n🎉 定时任务设置完成！")
        print("📧 您将在每天下午4点30分收到股票分析报告")
        print("\n📋 其他运行方式:")
        print("   手动运行: python3 stock_analyzer_yahoo.py")
        print("   查看日志: tail -f stock_analyzer.log")
        
        # 立即运行一次测试
        print("\n🧪 是否立即运行一次测试？ (y/n)")
        choice = input().strip().lower()
        if choice == 'y':
            print("🔄 正在运行测试...")
            subprocess.run(['python3', 'stock_analyzer_yahoo.py'])
    else:
        print("\n❌ 定时任务设置失败")
        print("📝 您可以手动运行: python3 stock_analyzer_yahoo.py")

if __name__ == "__main__":
    main()