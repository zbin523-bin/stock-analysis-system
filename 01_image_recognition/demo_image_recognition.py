#!/usr/bin/env python3
"""
演示脚本：图片识别和理解功能
"""

import os
import json
from image_recognition_tool import ImageRecognitionTool

def demo_image_recognition():
    """演示图片识别功能"""
    print("=== 图片识别和理解功能演示 ===\n")
    
    # 初始化识别工具
    recognizer = ImageRecognitionTool()
    
    # 检查是否有图片文件
    demo_images = []
    for file in os.listdir('.'):
        if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
            demo_images.append(file)
    
    if not demo_images:
        print("当前目录中没有找到图片文件")
        print("请将图片文件放在当前目录中，然后重新运行此脚本")
        return
    
    print(f"找到 {len(demo_images)} 个图片文件:")
    for i, img in enumerate(demo_images, 1):
        print(f"  {i}. {img}")
    
    # 选择图片
    if len(demo_images) == 1:
        selected_image = demo_images[0]
    else:
        try:
            choice = int(input("\n请选择要识别的图片编号: "))
            selected_image = demo_images[choice - 1]
        except (ValueError, IndexError):
            print("无效选择，使用第一个图片")
            selected_image = demo_images[0]
    
    print(f"\n正在识别图片: {selected_image}")
    
    # 1. 基本文字识别
    print("\n1. 基本文字识别:")
    print("-" * 40)
    text_result = recognizer.extract_text_from_image(selected_image)
    if text_result['success']:
        print("识别成功!")
        print("内容:", text_result['content'])
    else:
        print("识别失败:", text_result.get('error', '未知错误'))
    
    # 2. 图片理解
    print("\n2. 图片理解:")
    print("-" * 40)
    question = "请详细描述这张图片的内容"
    understanding_result = recognizer.understand_image(selected_image, question)
    if understanding_result['success']:
        print("理解成功!")
        print("分析结果:", understanding_result['answer'])
    else:
        print("理解失败:", understanding_result.get('error', '未知错误'))
    
    # 3. 天气信息识别（如果是天气图片）
    print("\n3. 天气信息识别:")
    print("-" * 40)
    weather_question = """请分析这张图片，如果是天气相关图片，请提取：
- 天气状况
- 温度信息
- 湿度信息  
- 风力信息
- 其他天气数据
- 地点和时间信息

如果不是天气图片，请说明图片的主要内容。"""
    
    weather_result = recognizer.understand_image(selected_image, weather_question)
    if weather_result['success']:
        print("天气分析完成!")
        print("天气信息:", weather_result['answer'])
    else:
        print("天气分析失败:", weather_result.get('error', '未知错误'))
    
    # 保存结果
    results = {
        'image_file': selected_image,
        'text_recognition': text_result,
        'image_understanding': understanding_result,
        'weather_analysis': weather_result,
        'timestamp': str(__import__('datetime').datetime.now())
    }
    
    output_file = f"recognition_results_{selected_image.split('.')[0]}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n识别结果已保存到: {output_file}")

def main():
    """主函数"""
    print("图片识别和理解工具")
    print("=" * 50)
    
    # 检查依赖
    try:
        import requests
        import openai
        print("✓ 依赖库已安装")
    except ImportError as e:
        print(f"✗ 缺少依赖库: {e}")
        print("请运行: pip install openai requests")
        return
    
    # 检查API密钥
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        print("✓ OpenAI API密钥已配置")
    else:
        print("⚠ 未检测到OpenAI API密钥")
        print("请设置环境变量: export OPENAI_API_KEY=your_key_here")
        print("或者创建.env文件")
    
    print("\n开始演示...")
    demo_image_recognition()

if __name__ == "__main__":
    main()