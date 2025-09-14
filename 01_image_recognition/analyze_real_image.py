#!/usr/bin/env python3
"""
重新分析用户真实图片的工具
"""

import os
import json
from datetime import datetime

def analyze_real_user_image():
    """分析用户的真实图片"""
    
    print("🔍 分析用户真实图片")
    print("=" * 50)
    print("⚠️ 重要提醒：我需要您将真实的图片文件保存到pic目录中")
    print("=" * 50)
    
    # 检查pic目录
    pic_dir = "pic"
    if not os.path.exists(pic_dir):
        os.makedirs(pic_dir)
        print(f"✅ 已创建pic目录")
    
    # 查找图片文件
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']
    image_files = []
    
    for file in os.listdir(pic_dir):
        if any(file.lower().endswith(ext) for ext in image_extensions) and not file.startswith('._'):
            image_files.append(os.path.join(pic_dir, file))
    
    if not image_files:
        print("❌ pic目录中没有找到图片文件")
        print("\n📋 请按以下步骤操作：")
        print("1. 将您要分析的真实图片文件保存到 pic/ 目录中")
        print("2. 支持的格式：.jpg, .jpeg, .png, .gif, .bmp, .tiff, .webp")
        print("3. 然后重新运行此工具")
        print("\n💡 或者您可以直接告诉我图片的内容，我将基于您的描述进行分析")
        return None
    
    print(f"📁 找到 {len(image_files)} 个图片文件:")
    for i, img in enumerate(image_files, 1):
        print(f"   {i}. {os.path.basename(img)}")
    
    # 选择最新的图片文件
    latest_image = max(image_files, key=os.path.getctime)
    print(f"\n🎯 将分析最新的图片: {os.path.basename(latest_image)}")
    
    # 使用硅基流动AI进行分析
    try:
        from siliconflow_image_recognition import SiliconFlowImageRecognitionTool
        
        # 加载API密钥
        api_key = None
        if os.path.exists('.env'):
            with open('.env', 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith('SILICONFLOW_API_KEY='):
                        api_key = line.split('=', 1)[1].strip()
                        break
        
        if not api_key:
            print("❌ API密钥未配置")
            return None
        
        recognizer = SiliconFlowImageRecognitionTool(api_key)
        
        # 使用专门的分析提示词
        analysis_prompt = """
请详细分析这张图片，重点关注以下方面：

1. 图片的整体内容和主题是什么？
2. 图片中包含哪些主要元素和对象？
3. 如果有文字，请提取所有文字内容
4. 如果有数据、数字或统计信息，请详细列出
5. 如果包含表格、图表或结构化信息，请完整提取
6. 图片的风格、用途和场景是什么？
7. 这张图片的核心信息和价值是什么？

请提供详细、准确的分析，重点关注提取可量化的信息和结构化数据。
"""
        
        print("🤖 正在使用硅基流动AI分析真实图片...")
        result = recognizer.recognize_with_siliconflow(
            latest_image, 
            analysis_prompt,
            "Qwen/Qwen2.5-VL-72B-Instruct"
        )
        
        if result['success']:
            print("✅ AI分析成功！")
            print("\n" + "=" * 60)
            print("📊 真实图片分析结果")
            print("=" * 60)
            
            print(f"📸 图片文件: {latest_image}")
            print(f"🕐 分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"🤖 使用模型: {result['model_used']}")
            print()
            
            print("📝 AI分析内容:")
            print("-" * 40)
            print(result['content'])
            print("-" * 40)
            
            # 尝试提取结构化信息
            content = result['content']
            
            # 查找数字
            import re
            numbers = re.findall(r'\d+(?:\.\d+)?', content)
            if numbers:
                print(f"\n🔢 提取的数字: {', '.join(numbers[:10])}")
                if len(numbers) > 10:
                    print(f"   ... (共{len(numbers)}个数字)")
            
            # 查找可能的表格信息
            if any(keyword in content for keyword in ['表格', '表', 'table', '行', '列']):
                print(f"\n📊 检测到可能的表格信息")
            
            # 查找时间信息
            time_patterns = re.findall(r'\d{4}[-年]\d{1,2}[-月]\d{1,2}|\d{1,2}[:时]\d{1,2}|\d{1,2}月\d{1,2}日', content)
            if time_patterns:
                print(f"⏰ 检测到时间信息: {', '.join(time_patterns)}")
            
            # 保存分析结果
            output_file = f"pic/real_image_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "image_path": latest_image,
                    "analysis_time": datetime.now().isoformat(),
                    "model_used": result['model_used'],
                    "analysis_content": result['content'],
                    "extracted_numbers": numbers[:20] if numbers else [],
                    "detected_time_patterns": time_patterns if time_patterns else []
                }, f, ensure_ascii=False, indent=2)
            
            print(f"\n💾 分析结果已保存到: {output_file}")
            
            return {
                "image_path": latest_image,
                "analysis_content": result['content'],
                "extracted_data": {
                    "numbers": numbers[:20] if numbers else [],
                    "time_patterns": time_patterns if time_patterns else []
                }
            }
            
        else:
            print(f"❌ AI分析失败: {result['error']}")
            return None
            
    except Exception as e:
        print(f"❌ 分析过程中出错: {e}")
        return None

def provide_manual_analysis_guidance():
    """提供手动分析指导"""
    
    print("\n📋 手动图片分析指导")
    print("=" * 40)
    print("如果您无法保存图片文件，请告诉我以下信息：")
    print()
    print("1. 📸 图片主要内容描述")
    print("   - 图片中显示了什么？")
    print("   - 有哪些主要元素？")
    print()
    print("2. 🔤 文字内容")
    print("   - 图片中包含哪些文字？")
    print("   - 有标题、标签或说明吗？")
    print()
    print("3. 📊 数据信息")
    print("   - 有数字、统计数据吗？")
    print("   - 有表格、图表吗？")
    print()
    print("4. 🎯 图片用途")
    print("   - 这是什么类型的图片？")
    print("   - 用于什么场景？")
    print()
    print("我将基于您的描述进行智能分析！")

def main():
    """主函数"""
    print("🚀 真实图片分析工具")
    print("=" * 50)
    print("🎯 专门分析用户发送的真实图片")
    print("=" * 50)
    
    # 尝试分析真实图片
    analysis_result = analyze_real_user_image()
    
    if analysis_result:
        print("\n🎉 真实图片分析完成！")
        print("📊 上述内容是基于您真实图片的AI分析结果")
    else:
        print("\n⚠️ 无法找到真实图片文件")
        provide_manual_analysis_guidance()

if __name__ == "__main__":
    main()