#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票分析启动器 - 使用现有Gmail配置
Stock Analysis Launcher - Using existing Gmail configuration
"""

import os
import sys
import subprocess
import logging
from datetime import datetime

def load_env_config():
    """加载环境变量配置"""
    config = {}
    try:
        with open('.env', 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    config[key] = value.strip()
    except Exception as e:
        print(f"警告：无法读取配置文件: {e}")
    
    return config

def setup_directories():
    """创建必要的目录"""
    directories = ['reports', 'logs', 'output']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ 创建目录: {directory}")

def check_dependencies():
    """检查依赖包"""
    required_packages = ['pandas', 'requests', 'schedule']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ 缺少依赖包: {', '.join(missing_packages)}")
        print("正在安装依赖包...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
            print("✅ 依赖包安装完成")
        except Exception as e:
            print(f"❌ 依赖包安装失败: {e}")
            return False
    
    return True

def create_launcher_script():
    """创建启动脚本"""
    launcher_content = '''#!/bin/bash
# 股票分析系统启动器

# 设置环境变量
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到Python3，请先安装Python3"
    exit 1
fi

# 创建必要目录
mkdir -p reports logs output

echo "🚀 启动自动化股票分析系统..."
echo "⏰ 定时任务：每天10:00和16:00"
echo "📧 邮件发送至：zhangbin19850523@163.com"
echo "按 Ctrl+C 停止程序"
echo ""

# 启动分析系统
python3 automated_stock_analyzer.py
'''
    
    with open('start_stock_analysis.sh', 'w') as f:
        f.write(launcher_content)
    
    # 使脚本可执行
    os.chmod('start_stock_analysis.sh', 0o755)
    print("✅ 创建启动脚本: start_stock_analysis.sh")

def create_systemd_service():
    """创建systemd服务文件（可选）"""
    service_content = f'''[Unit]
Description=Automated Stock Analysis System
After=network.target

[Service]
Type=simple
User={os.getenv('USER', 'user')}
WorkingDirectory={os.getcwd()}
ExecStart={sys.executable} automated_stock_analyzer.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
'''
    
    with open('stock-analysis.service', 'w') as f:
        f.write(service_content)
    
    print("✅ 创建systemd服务文件: stock-analysis.service")
    print("要启用服务，请运行:")
    print("  sudo cp stock-analysis.service /etc/systemd/system/")
    print("  sudo systemctl daemon-reload")
    print("  sudo systemctl enable stock-analysis")
    print("  sudo systemctl start stock-analysis")

def main():
    """主函数"""
    print("🔧 股票分析系统部署工具")
    print("=" * 50)
    
    # 加载配置
    config = load_env_config()
    
    # 检查Gmail配置
    if 'EMAIL_SENDER' in config and 'EMAIL_PASSWORD' in config:
        print(f"✅ Gmail配置: {config['EMAIL_SENDER']}")
    else:
        print("❌ Gmail配置不完整，请检查.env文件")
        return
    
    # 检查依赖
    if not check_dependencies():
        return
    
    # 创建目录
    setup_directories()
    
    # 创建启动脚本
    create_launcher_script()
    
    # 创建systemd服务
    create_systemd_service()
    
    print("\n🎉 部署完成！")
    print("\n📋 使用说明:")
    print("1. 直接运行: python3 automated_stock_analyzer.py")
    print("2. 使用脚本: ./start_stock_analysis.sh")
    print("3. 系统服务: sudo systemctl start stock-analysis")
    
    print(f"\n📧 邮件将发送至: {config.get('EMAIL_RECEIVER', 'zhangbin19850523@163.com')}")
    print("⏰ 定时任务: 每天10:00和16:00")
    
    # 询问是否立即测试
    test_now = input("\n是否立即测试系统？(y/n): ").lower().strip()
    if test_now == 'y':
        print("\n🧪 运行测试...")
        try:
            # 修改analyzer使用现有配置
            with open('automated_stock_analyzer.py', 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 更新Gmail配置
            content = content.replace(
                'self.gmail_config = {\n            "smtp_server": "smtp.gmail.com",\n            "smtp_port": 587,\n            "sender_email": "your_email@gmail.com",  # 您的Gmail地址\n            "sender_password": "your_app_password",  # Gmail应用密码\n            "recipient_email": "zhangbin19850523@163.com"\n        }',
                f'''self.gmail_config = {{
                    "smtp_server": "smtp.gmail.com",
                    "smtp_port": 587,
                    "sender_email": "{config['EMAIL_SENDER']}",
                    "sender_password": "{config['EMAIL_PASSWORD']}",
                    "recipient_email": "{config.get('EMAIL_RECEIVER', 'zhangbin19850523@163.com')}"
                }}'''
            )
            
            with open('automated_stock_analyzer.py', 'w', encoding='utf-8') as f:
                f.write(content)
            
            # 运行测试
            subprocess.run([sys.executable, 'automated_stock_analyzer.py'], input='1\n'.encode())
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    main()