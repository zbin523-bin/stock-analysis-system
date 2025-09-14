#!/bin/bash
# 硅基流动图片识别工具 - 快速设置脚本

echo "🚀 硅基流动图片识别工具 - 快速设置"
echo "========================================"

# 检查Python
echo "📦 检查Python环境..."
python3 --version

# 安装依赖
echo "📦 安装依赖包..."
pip3 install requests pillow python-dotenv

# 创建配置文件
echo "🔑 创建配置文件..."
cat > .env << EOF
# 硅基流动API配置
# 请访问 https://cloud.siliconflow.cn/ 获取API密钥

SILICONFLOW_API_KEY=your_api_key_here
DEFAULT_MODEL=qwen-vl-max
SILICONFLOW_BASE_URL=https://api.siliconflow.cn/v1
REQUEST_TIMEOUT=60
EOF

echo "✅ 已创建 .env 配置文件"
echo ""
echo "📋 下一步操作："
echo "1. 编辑 .env 文件，填入您的硅基流动API密钥"
echo "2. 运行: python3 siliconflow_image_recognition.py"
echo "3. 按提示选择图片进行识别"
echo ""
echo "🔑 获取API密钥："
echo "   访问: https://cloud.siliconflow.cn/"
echo "   注册账户后，在控制台获取API密钥"
echo ""
echo "🤖 支持的模型："
echo "   - qwen-vl-max (推荐)"
echo "   - qwen-vl-plus"
echo "   - deepseek-vl"
echo "   - yi-vl"
echo "   - glm-4v"
echo "   - minicpm-v"