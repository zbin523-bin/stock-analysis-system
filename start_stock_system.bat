@echo off
REM 股票分析系统启动脚本 (Windows)

REM 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到Python，请先安装Python
    pause
    exit /b 1
)

REM 创建必要目录
if not exist "logs" mkdir logs
if not exist "reports" mkdir reports

echo 🚀 启动生产环境股票分析系统...
echo ⏰ 定时任务：每天10:00和16:00
echo 📧 邮件发送至：zhangbin19850523@163.com
echo 按 Ctrl+C 停止程序
echo.

REM 启动分析系统
python production_stock_analyzer.py
pause
