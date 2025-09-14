#!/bin/bash

# 股票投资组合管理系统启动脚本

echo "正在启动股票投资组合管理系统..."

# 检查Python是否可用
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请先安装Python3"
    exit 1
fi

# 检查依赖是否安装
echo "检查依赖..."
cd "$(dirname "$0")"

if [ ! -f "api/requirements.txt" ]; then
    echo "错误: 未找到requirements.txt文件"
    exit 1
fi

# 安装Python依赖
echo "安装Python依赖..."
cd api
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "错误: 依赖安装失败"
    exit 1
fi

cd ..

# 启动API服务器
echo "启动API服务器..."
cd api
python3 app.py &
API_PID=$!

# 等待API服务器启动
sleep 3

# 测试API服务器
echo "测试API服务器..."
if curl -s http://localhost:5000/api/health > /dev/null; then
    echo "✅ API服务器启动成功"
else
    echo "❌ API服务器启动失败"
    kill $API_PID
    exit 1
fi

# 启动Web服务器
echo "启动Web服务器..."
cd ../web
python3 -m http.server 8080 &
WEB_PID=$!

# 等待Web服务器启动
sleep 2

echo "✅ 系统启动完成！"
echo ""
echo "访问地址:"
echo "- 前端界面: http://localhost:8080"
echo "- API接口: http://localhost:5000"
echo "- 健康检查: http://localhost:5000/api/health"
echo ""
echo "按 Ctrl+C 停止服务"

# 清理函数
cleanup() {
    echo ""
    echo "正在停止服务..."
    kill $API_PID 2>/dev/null
    kill $WEB_PID 2>/dev/null
    echo "服务已停止"
    exit 0
}

# 设置信号处理
trap cleanup SIGINT SIGTERM

# 等待用户中断
wait