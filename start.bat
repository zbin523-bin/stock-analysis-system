@echo off
chcp 65001 >nul
title 股票投资组合管理系统

echo 正在启动股票投资组合管理系统...

REM 检查Python是否可用
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到Python，请先安装Python
    pause
    exit /b 1
)

REM 进入项目目录
cd /d "%~dp0"

REM 检查依赖是否安装
echo 检查依赖...
if not exist "api\requirements.txt" (
    echo 错误: 未找到requirements.txt文件
    pause
    exit /b 1
)

REM 安装Python依赖
echo 安装Python依赖...
cd api
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo 错误: 依赖安装失败
    pause
    exit /b 1
)

cd ..

REM 启动API服务器
echo 启动API服务器...
start "Stock API Server" /min cmd /c "cd api && python app.py"

REM 等待API服务器启动
timeout /t 3 /nobreak >nul

REM 测试API服务器
echo 测试API服务器...
curl -s http://localhost:5000/api/health >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ API服务器启动失败
    taskkill /f /im python.exe >nul 2>&1
    pause
    exit /b 1
)

echo ✅ API服务器启动成功

REM 启动Web服务器
echo 启动Web服务器...
cd web
start "Stock Web Server" /min cmd /c "python -m http.server 8080"

REM 等待Web服务器启动
timeout /t 2 /nobreak >nul

echo.
echo ✅ 系统启动完成！
echo.
echo 访问地址:
echo - 前端界面: http://localhost:8080
echo - API接口: http://localhost:5000
echo - 健康检查: http://localhost:5000/api/health
echo.
echo 按任意键停止服务...
pause >nul

REM 停止服务
echo.
echo 正在停止服务...
taskkill /f /im python.exe >nul 2>&1
echo 服务已停止
pause