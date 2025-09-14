#!/bin/bash
# -*- coding: utf-8 -*-
"""
股票分析系统安装脚本
Stock Analysis System Installation Script
"""

echo "🚀 股票分析定时发送系统安装"
echo "=================================="

# 检查系统
OS=$(uname -s)
if [ "$OS" = "Darwin" ]; then
    echo "✅ 检测到 macOS 系统"
elif [ "$OS" = "Linux" ]; then
    echo "✅ 检测到 Linux 系统"
else
    echo "❌ 不支持的操作系统: $OS"
    exit 1
fi

# 检查Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✅ Python已安装: $PYTHON_VERSION"
else
    echo "❌ 请先安装 Python3"
    exit 1
fi

# 检查必要的Python包
echo "🔍 检查Python依赖包..."
python3 -c "
import sys
required_packages = ['pandas', 'requests', 'schedule', 'yfinance', 'beautifulsoup4', 'openpyxl']
missing_packages = []

for package in required_packages:
    try:
        __import__(package.replace('-', '_'))
    except ImportError:
        missing_packages.append(package)

if missing_packages:
    print('❌ 缺少以下包:', ', '.join(missing_packages))
    print('请运行: pip3 install ' + ' '.join(missing_packages))
    sys.exit(1)
else:
    print('✅ 所有依赖包已安装')
"

if [ $? -ne 0 ]; then
    echo "请安装缺少的依赖包后重新运行此脚本"
    exit 1
fi

# 创建必要的目录
echo "📁 创建目录结构..."
mkdir -p logs
mkdir -p pids
mkdir -p reports
echo "✅ 目录结构创建完成"

# 设置执行权限
echo "🔐 设置执行权限..."
chmod +x stock_control_center.sh
chmod +x stock_scheduler_service.py
echo "✅ 权限设置完成"

# 测试系统
echo "🧪 测试系统..."
python3 stock_notification_agent_enhanced.py

if [ $? -eq 0 ]; then
    echo "✅ 系统测试通过"
else
    echo "❌ 系统测试失败，请检查配置"
    exit 1
fi

echo ""
echo "🎉 安装完成！"
echo ""
echo "📖 使用说明:"
echo "1. 运行控制中心: ./stock_control_center.sh"
echo "2. 直接发送报告: python3 stock_notification_agent_enhanced.py"
echo "3. 启动定时服务: python3 stock_scheduler_service.py --daemon"
echo ""
echo "⚙️  定时任务选项:"
echo "- 系统级: 使用控制中心的选项7设置crontab"
echo "- 服务级: 使用选项3启动守护进程"
echo "- 应用级: 使用选项2前台运行"
echo ""
echo "📧 邮件将发送到: zhangbin19850523@163.com"
echo "⏰ 默认时间: 每天10:00和16:00"