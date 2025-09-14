@echo off
chcp 65001 >nul
echo.
echo ========================================
echo    股票投资组合管理系统 - 快速启动
echo ========================================
echo.

REM 检查Python是否可用
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到Python，请先安装Python
    pause
    exit /b 1
)

echo [信息] Python环境检查通过

REM 进入项目目录
cd /d "%~dp0"

REM 检查API服务是否运行
echo [信息] 检查API服务状态...
curl -s http://localhost:5000/api/health >nul 2>&1
if %errorlevel% equ 0 (
    echo [成功] API服务正在运行
) else (
    echo [信息] 启动API服务...
    start "Stock API Server" /min cmd /c "cd api && python app.py"
    timeout /t 5 /nobreak >nul
)

REM 检查Web服务是否运行
echo [信息] 检查Web服务状态...
curl -s http://localhost:8080 >nul 2>&1
if %errorlevel% equ 0 (
    echo [成功] Web服务正在运行
) else (
    echo [信息] 启动Web服务...
    start "Stock Web Server" /min cmd /c "cd web && python -m http.server 8080"
    timeout /t 3 /nobreak >nul
)

REM 最终检查
echo [信息] 最终检查服务状态...
curl -s http://localhost:5000/api/health >nul 2>&1
if %errorlevel% neq 0 (
    echo [警告] API服务启动失败
)

curl -s http://localhost:8080 >nul 2>&1
if %errorlevel% neq 0 (
    echo [警告] Web服务启动失败
)

echo.
echo ========================================
echo    系统启动完成！
echo ========================================
echo.
echo 访问地址：
echo - 主页面: http://localhost:8080
echo - 简化测试: http://localhost:8080/simple.html
echo - API测试: http://localhost:8080/test.html
echo - API接口: http://localhost:5000
echo.
echo 注意：如果页面显示无数据，请点击"刷新数据"按钮
echo.
echo 按任意键打开浏览器...
pause >nul

start http://localhost:8080/simple.html

echo.
echo 系统正在运行中，按任意键停止服务...
pause >nul

echo.
echo [信息] 正在停止服务...
taskkill /f /im python.exe >nul 2>&1
echo [成功] 服务已停止
pause