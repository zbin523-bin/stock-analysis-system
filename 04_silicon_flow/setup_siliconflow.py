#!/usr/bin/env python3
"""
硅基流动图片识别工具 - 配置和使用指南
"""

import os
import sys
import subprocess

def setup_environment():
    """设置环境变量和依赖"""
    print("🚀 硅基流动图片识别工具 - 环境配置")
    print("=" * 50)
    
    # 检查Python依赖
    print("📦 检查Python依赖...")
    required_packages = ['requests', 'PIL']
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'PIL':
                import PIL
            else:
                __import__(package)
            print(f"   ✓ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"   ✗ {package}")
    
    if missing_packages:
        print(f"\n⚠️  缺少依赖包，正在安装...")
        for package in missing_packages:
            package_name = 'pillow' if package == 'PIL' else package
            subprocess.run([sys.executable, '-m', 'pip', 'install', package_name])
    
    # 检查API密钥配置
    print(f"\n🔑 检查API密钥配置...")
    api_key = os.getenv('SILICONFLOW_API_KEY')
    
    if api_key:
        print(f"   ✓ 已配置API密钥: {api_key[:10]}...")
    else:
        print("   ✗ 未配置API密钥")
        print("\n请按以下步骤配置:")
        print("1. 访问 https://cloud.siliconflow.cn/")
        print("2. 注册并登录您的账户")
        print("3. 在控制台中获取API密钥")
        print("4. 运行以下命令设置环境变量:")
        print("   export SILICONFLOW_API_KEY=your_api_key_here")
        print("   或者创建 .env 文件")
        
        # 询问是否要创建.env文件
        create_env = input("\n是否要创建 .env 配置文件? (y/n): ").lower().strip()
        if create_env == 'y':
            create_env_file()
    
    return api_key is not None

def create_env_file():
    """创建.env配置文件"""
    api_key = input("请输入您的硅基流动API密钥: ").strip()
    
    if not api_key:
        print("❌ API密钥不能为空")
        return
    
    env_content = f"""# 硅基流动API配置文件
SILICONFLOW_API_KEY={api_key}

# 默认模型选择
DEFAULT_MODEL=qwen-vl-max

# API基础URL
SILICONFLOW_BASE_URL=https://api.siliconflow.cn/v1

# 请求超时时间（秒）
REQUEST_TIMEOUT=60
"""
    
    try:
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        print("✅ .env 文件创建成功")
        print("💡 请重新运行脚本以加载配置")
    except Exception as e:
        print(f"❌ 创建 .env 文件失败: {e}")

def show_supported_models():
    """显示支持的模型"""
    print("\n🤖 硅基流动支持的图片识别模型:")
    print("-" * 40)
    
    models = {
        "qwen-vl-max": {
            "name": "通义千问VL Max",
            "description": "阿里云最新多模态大模型，图片理解能力最强",
            "features": ["高精度图片识别", "复杂场景理解", "多语言支持"]
        },
        "qwen-vl-plus": {
            "name": "通义千问VL Plus", 
            "description": "阿里云多模态大模型，性能均衡",
            "features": ["快速响应", "良好的图片理解", "成本较低"]
        },
        "deepseek-vl": {
            "name": "DeepSeek VL",
            "description": "深度求索多模态模型",
            "features": ["优秀的推理能力", "中文理解优秀", "性价比高"]
        },
        "yi-vl": {
            "name": "Yi VL",
            "description": "零一万物多模态模型",
            "features": ["强大的视觉理解", "多场景适应", "稳定性能"]
        },
        "glm-4v": {
            "name": "GLM-4V",
            "description": "智谱AI多模态模型",
            "features": ["优秀的中文理解", "多模态融合", "快速响应"]
        },
        "minicpm-v": {
            "name": "MiniCPM-V",
            "description": "面壁智能轻量多模态模型",
            "features": ["轻量高效", "本地部署友好", "成本最低"]
        }
    }
    
    for model_id, info in models.items():
        print(f"\n📍 {model_id}")
        print(f"   名称: {info['name']}")
        print(f"   描述: {info['description']}")
        print(f"   特点: {', '.join(info['features'])}")

def test_api_connection():
    """测试API连接"""
    print("\n🔧 测试API连接...")
    
    try:
        from siliconflow_image_recognition import SiliconFlowImageRecognitionTool
        
        # 加载环境变量
        if os.path.exists('.env'):
            from dotenv import load_dotenv
            load_dotenv()
        
        api_key = os.getenv('SILICONFLOW_API_KEY')
        if not api_key:
            print("❌ 未找到API密钥")
            return False
        
        recognizer = SiliconFlowImageRecognitionTool(api_key)
        
        # 创建测试图片
        from PIL import Image, ImageDraw, ImageFont
        import io
        
        # 创建一个简单的测试图片
        img = Image.new('RGB', (200, 100), color='white')
        draw = ImageDraw.Draw(img)
        draw.text((10, 10), "Test Image", fill='black')
        draw.text((10, 40), "测试图片", fill='black')
        draw.text((10, 70), "2025-09-10", fill='black')
        
        # 保存测试图片
        test_image_path = "test_image.png"
        img.save(test_image_path)
        
        # 测试识别
        result = recognizer.recognize_with_siliconflow(
            test_image_path, 
            "请描述这张测试图片的内容"
        )
        
        # 清理测试图片
        if os.path.exists(test_image_path):
            os.remove(test_image_path)
        
        if result["success"]:
            print("✅ API连接测试成功")
            print(f"   使用的模型: {result['model_used']}")
            print(f"   识别结果: {result['content'][:100]}...")
            return True
        else:
            print(f"❌ API连接测试失败: {result['error']}")
            return False
            
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        return False

def main():
    """主函数"""
    print("🛠️  硅基流动图片识别工具 - 配置向导")
    print("=" * 60)
    
    # 1. 设置环境
    env_ok = setup_environment()
    
    # 2. 显示支持的模型
    show_supported_models()
    
    # 3. 如果环境配置成功，测试API连接
    if env_ok:
        print("\n" + "=" * 60)
        test_api_connection()
        
        print("\n🎉 配置完成！")
        print("\n使用方法:")
        print("1. 将图片文件放在当前目录")
        print("2. 运行: python3 siliconflow_image_recognition.py")
        print("3. 选择要分析的图片和模型")
        
        print("\n📚 更多信息请查看 README_siliconflow.md")
    else:
        print("\n⚠️  环境配置未完成，请先配置API密钥")

if __name__ == "__main__":
    main()