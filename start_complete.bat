@echo off
chcp 65001 >nul
echo.
echo ========================================
echo    🚀 股票投资组合管理系统 - 完整版
echo ========================================
echo.

REM 检查Python是否可用
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [❌] 未找到Python，请先安装Python
    pause
    exit /b 1
)

echo [✅] Python环境检查通过

REM 进入项目目录
cd /d "%~dp0"

REM 清理旧的Python进程
echo [🔄] 清理旧的服务进程...
taskkill /f /im python.exe >nul 2>&1
timeout /t 2 /nobreak >nul

REM 启动新的API服务
echo [🚀] 启动API服务器 (端口5001)...
start "Stock API Server" /min cmd /c "cd api && python app.py"
timeout /t 3 /nobreak >nul

REM 检查Web服务是否运行
echo [🔄] 检查Web服务状态...
curl -s http://localhost:8080 >nul 2>&1
if %errorlevel% equ 0 (
    echo [✅] Web服务正在运行
) else (
    echo [🚀] 启动Web服务...
    start "Stock Web Server" /min cmd /c "cd web && python -m http.server 8080"
    timeout /t 3 /nobreak >nul
)

REM 最终检查
echo [🔍] 最终检查服务状态...
curl -s http://localhost:5001/api/health >nul 2>&1
if %errorlevel% neq 0 (
    echo [⚠️]  API服务启动失败 - 请手动检查
)

curl -s http://localhost:8080 >nul 2>&1
if %errorlevel% neq 0 (
    echo [⚠️]  Web服务启动失败 - 请手动检查
)

echo.
echo ========================================
echo    🎉 系统启动完成！
echo ========================================
echo.
echo 📱 访问地址：
echo    📊 完整测试页面: http://localhost:8080/complete.html
echo    📈 简化页面: http://localhost:8080/simple.html
echo    🧪 API测试: http://localhost:8080/test.html
echo    🔗 API接口: http://localhost:5001
echo.
echo 💡 功能特性：
echo    ✅ A股实时数据 (新浪财经 + 腾讯财经)
echo    ✅ 港股实时数据 (腾讯财经港股)
echo    ✅ 美股实时数据 (Yahoo Finance - 可能受网络限制)
echo    ✅ 投资组合管理
echo    ✅ 多市场数据展示
echo    ✅ 数据状态监控
echo.
echo 📋 测试建议：
echo    1. 首先访问完整测试页面
echo    2. 点击"测试所有市场"按钮
echo    3. 查看各市场股票数据状态
echo    4. 使用"刷新数据"更新最新价格
echo.
echo 按任意键打开完整测试页面...
pause >nul

start http://localhost:8080/complete.html

echo.
echo 🔄 系统正在运行中，按任意键停止服务...
pause >nul

echo.
echo [🛑] 正在停止服务...
taskkill /f /im python.exe >nul 2>&1
echo [✅] 服务已停止
echo.
echo 📁 项目位置：%cd%
echo 📖 部署指南：README.md
pause