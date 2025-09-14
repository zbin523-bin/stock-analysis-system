#!/usr/bin/env python3
"""
专门分析用户微信图片的工具
"""

import os
import json
from datetime import datetime

def analyze_wechat_image():
    """分析微信图片"""
    
    image_path = "pic/微信图片_20250906234045_82_276.jpg"
    
    if not os.path.exists(image_path):
        print(f"❌ 图片文件不存在: {image_path}")
        return None
    
    print("🎯 分析微信图片")
    print("=" * 50)
    print(f"📸 图片文件: {image_path}")
    print(f"📏 文件大小: {os.path.getsize(image_path)} bytes")
    print("=" * 50)
    
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
        
        # 获取图片基本信息
        from PIL import Image
        with Image.open(image_path) as img:
            image_info = {
                "format": img.format,
                "size": img.size,
                "width": img.width,
                "height": img.height,
                "mode": img.mode
            }
        
        print(f"📊 图片信息: {image_info['width']}x{image_info['height']} px | {image_info['format']}")
        
        # 使用专门的分析提示词
        analysis_prompt = """
请详细分析这张微信图片，提供全面准确的信息：

1. **图片内容描述**：
   - 图片主要显示了什么内容？
   - 有哪些主要元素和对象？
   - 整体场景和氛围如何？

2. **文字信息提取**：
   - 图片中包含哪些文字内容？
   - 有标题、标签、说明文字吗？
   - 如果是聊天截图，请提取所有对话内容

3. **数据信息**：
   - 有数字、统计数据吗？
   - 有时间、日期信息吗？
   - 有表格、图表或其他结构化数据吗？

4. **图片类型和用途**：
   - 这是什么类型的图片？（聊天截图、文档、照片等）
   - 图片的用途和场景是什么？
   - 可能的来源和背景？

5. **关键信息总结**：
   - 图片的核心信息是什么？
   - 最重要的数据点或内容是什么？
   - 有什么特殊或值得注意的地方？

请提供详细、结构化的分析，重点关注提取准确的信息和数据。
"""
        
        print("🤖 正在使用硅基流动AI分析微信图片...")
        result = recognizer.recognize_with_siliconflow(
            image_path, 
            analysis_prompt,
            "Qwen/Qwen2.5-VL-72B-Instruct"
        )
        
        if result['success']:
            print("✅ AI分析成功！")
            print("\n" + "=" * 60)
            print("📊 微信图片分析报告")
            print("=" * 60)
            
            print(f"📸 图片文件: {image_path}")
            print(f"📏 图片尺寸: {image_info['width']}x{image_info['height']} px")
            print(f"📄 文件大小: {os.path.getsize(image_path)} bytes")
            print(f"🕐 分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"🤖 使用模型: {result['model_used']}")
            print()
            
            print("📝 AI分析内容:")
            print("-" * 60)
            print(result['content'])
            print("-" * 60)
            
            # 提取关键信息
            content = result['content']
            
            # 查找数字
            import re
            numbers = re.findall(r'\d+(?:\.\d+)?', content)
            if numbers:
                print(f"\n🔢 提取的数字: {', '.join(numbers)}")
            
            # 查找时间信息
            time_patterns = re.findall(r'\d{4}[-年]\d{1,2}[-月]\d{1,2}|\d{1,2}[:时]\d{1,2}|\d{1,2}月\d{1,2}日|\d{1,2}:\d{2}', content)
            if time_patterns:
                print(f"⏰ 检测到时间信息: {', '.join(time_patterns)}")
            
            # 查找可能的微信相关内容
            wechat_keywords = ['微信', '聊天', '消息', '发送', '接收', '群聊', '朋友圈']
            found_wechat_content = []
            for keyword in wechat_keywords:
                if keyword in content:
                    found_wechat_content.append(keyword)
            
            if found_wechat_content:
                print(f"💬 检测到微信相关内容: {', '.join(found_wechat_content)}")
            
            # 保存分析结果
            output_file = f"pic/wechat_image_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "image_path": image_path,
                    "image_info": image_info,
                    "file_size": os.path.getsize(image_path),
                    "analysis_time": datetime.now().isoformat(),
                    "model_used": result['model_used'],
                    "analysis_content": result['content'],
                    "extracted_numbers": numbers,
                    "detected_time_patterns": time_patterns,
                    "wechat_keywords_found": found_wechat_content
                }, f, ensure_ascii=False, indent=2)
            
            print(f"\n💾 分析结果已保存到: {output_file}")
            
            return {
                "image_path": image_path,
                "analysis_content": result['content'],
                "extracted_data": {
                    "numbers": numbers,
                    "time_patterns": time_patterns,
                    "wechat_keywords": found_wechat_content
                }
            }
            
        else:
            print(f"❌ AI分析失败: {result['error']}")
            return None
            
    except Exception as e:
        print(f"❌ 分析过程中出错: {e}")
        return None

def main():
    """主函数"""
    print("🚀 微信图片专用分析工具")
    print("=" * 50)
    print("🎯 分析微信图片: 微信图片_20250906234045_82_276.jpg")
    print("=" * 50)
    
    # 分析微信图片
    analysis_result = analyze_wechat_image()
    
    if analysis_result:
        print("\n🎉 微信图片分析完成！")
        print("📊 上述内容是基于您真实微信图片的AI分析结果")
        
        print("\n📋 总结:")
        print("✅ 图片文件: 微信图片_20250906234045_82_276.jpg")
        print("✅ AI模型: Qwen/Qwen2.5-VL-72B-Instruct")
        print("✅ 分析内容: 详细图片内容、文字、数据提取")
        print("✅ 结构化数据: 数字、时间、关键词提取")
        
    else:
        print("\n❌ 微信图片分析失败")
        print("请检查图片文件或网络连接")

if __name__ == "__main__":
    main()