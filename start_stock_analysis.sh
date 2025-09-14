#!/bin/bash
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
