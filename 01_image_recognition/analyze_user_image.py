#!/usr/bin/env python3
"""
专门分析刚保存的用户图片
"""

import os
import json
from datetime import datetime

def analyze_user_saved_image():
    """分析用户保存的图片"""
    
    # 查找pic目录中最新的图片文件
    pic_dir = "pic"
    if not os.path.exists(pic_dir):
        print("❌ pic目录不存在")
        return
    
    # 查找图片文件
    image_files = []
    for file in os.listdir(pic_dir):
        if file.endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')) and not file.startswith('._'):
            image_files.append(os.path.join(pic_dir, file))
    
    if not image_files:
        print("❌ pic目录中没有找到图片文件")
        return
    
    # 选择最新的图片文件
    latest_image = max(image_files, key=os.path.getctime)
    print(f"🎯 分析图片: {latest_image}")
    
    # 使用硅基流动API进行分析
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
            return
        
        recognizer = SiliconFlowImageRecognitionTool(api_key)
        
        # 使用专门的分析提示词
        analysis_prompt = """
请详细分析这张图片，重点关注以下方面：

1. 图片的整体内容和结构描述
2. 如果包含表格，请提取表格数据并整理成结构化格式
3. 如果包含图表，请描述图表类型和数据趋势
4. 识别所有的文字信息和数字数据
5. 提取关键信息和核心数据点

请按以下JSON格式返回分析结果：
{
  "description": "图片整体描述",
  "content_type": "数据报告/表格/图表等",
  "tables": [
    {
      "title": "表格标题",
      "headers": ["列1", "列2", "列3"],
      "rows": [
        ["数据1", "数据2", "数据3"],
        ["数据4", "数据5", "数据6"]
      ]
    }
  ],
  "charts": [
    {
      "type": "图表类型",
      "description": "图表描述",
      "data_points": ["数据点1", "数据点2"]
    }
  ],
  "text_content": ["文字1", "文字2"],
  "numerical_data": ["数字1", "数字2"],
  "key_insights": ["洞察1", "洞察2"],
  "summary": "内容总结"
}
"""
        
        print("🤖 正在进行AI分析...")
        result = recognizer.recognize_with_siliconflow(
            latest_image, 
            analysis_prompt,
            "Qwen/Qwen2.5-VL-72B-Instruct"
        )
        
        if result['success']:
            print("✅ AI分析成功！")
            
            # 尝试解析JSON结果
            try:
                import json
                analysis_data = json.loads(result['content'])
                
                # 生成核心信息报告
                print("\n" + "=" * 60)
                print("📊 图片核心信息分析报告")
                print("=" * 60)
                
                print(f"📸 图片文件: {latest_image}")
                print(f"🕐 分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"🤖 使用模型: {result['model_used']}")
                print()
                
                # 基本描述
                if 'description' in analysis_data:
                    print("📝 图片描述:")
                    print(f"   {analysis_data['description']}")
                    print()
                
                # 内容类型
                if 'content_type' in analysis_data:
                    print("🎯 内容类型:")
                    print(f"   {analysis_data['content_type']}")
                    print()
                
                # 表格数据
                if 'tables' in analysis_data and analysis_data['tables']:
                    print("📋 表格数据:")
                    for i, table in enumerate(analysis_data['tables'], 1):
                        print(f"   表格 {i}: {table.get('title', '无标题')}")
                        if 'headers' in table and 'rows' in table:
                            print(f"     表头: {' | '.join(table['headers'])}")
                            print(f"     数据行数: {len(table['rows'])}")
                            # 显示前几行数据
                            for j, row in enumerate(table['rows'][:2]):
                                print(f"     行{j+1}: {' | '.join(str(cell) for cell in row)}")
                            if len(table['rows']) > 2:
                                print(f"     ... (还有{len(table['rows'])-2}行数据)")
                        print()
                
                # 图表信息
                if 'charts' in analysis_data and analysis_data['charts']:
                    print("📈 图表信息:")
                    for i, chart in enumerate(analysis_data['charts'], 1):
                        print(f"   图表 {i}: {chart.get('type', '未知类型')}")
                        print(f"     描述: {chart.get('description', '无描述')}")
                        if 'data_points' in chart:
                            print(f"     数据点: {', '.join(chart['data_points'][:3])}...")
                        print()
                
                # 文字内容
                if 'text_content' in analysis_data and analysis_data['text_content']:
                    print("📝 文字内容:")
                    for i, text in enumerate(analysis_data['text_content'][:5], 1):
                        print(f"   {i}. {text}")
                    print()
                
                # 数值数据
                if 'numerical_data' in analysis_data and analysis_data['numerical_data']:
                    print("🔢 数值数据:")
                    for i, num in enumerate(analysis_data['numerical_data'][:5], 1):
                        print(f"   {i}. {num}")
                    print()
                
                # 关键洞察
                if 'key_insights' in analysis_data and analysis_data['key_insights']:
                    print("💡 关键洞察:")
                    for i, insight in enumerate(analysis_data['key_insights'], 1):
                        print(f"   {i}. {insight}")
                    print()
                
                # 总结
                if 'summary' in analysis_data:
                    print("📋 总结:")
                    print(f"   {analysis_data['summary']}")
                    print()
                
                # 保存分析结果
                output_file = f"pic/detailed_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        "image_path": latest_image,
                        "analysis_time": datetime.now().isoformat(),
                        "model_used": result['model_used'],
                        "analysis_data": analysis_data,
                        "raw_response": result['content']
                    }, f, ensure_ascii=False, indent=2)
                
                print(f"💾 详细分析结果已保存到: {output_file}")
                
                return analysis_data
                
            except json.JSONDecodeError:
                print("⚠️ AI返回了非JSON格式的响应")
                print("📝 原始响应内容:")
                print(result['content'])
                return None
                
        else:
            print(f"❌ AI分析失败: {result['error']}")
            return None
            
    except Exception as e:
        print(f"❌ 分析过程中出错: {e}")
        return None

def main():
    """主函数"""
    print("🚀 用户图片分析工具")
    print("=" * 50)
    print("🎯 分析保存在pic目录中的用户图片")
    print("=" * 50)
    
    # 分析用户保存的图片
    analysis_result = analyze_user_saved_image()
    
    if analysis_result:
        print("\n🎉 图片分析完成！")
        print("📊 核心信息已提取并显示在上方")
        print("💾 详细分析结果已保存到pic目录")
    else:
        print("\n❌ 图片分析失败")

if __name__ == "__main__":
    main()