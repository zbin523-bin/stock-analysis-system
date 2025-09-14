#!/usr/bin/env python3
"""
专门用于分析用户图片并生成表格的工具
"""

import os
import requests
import json
import base64
from datetime import datetime
from PIL import Image
import io

class ImageTableAnalyzer:
    def __init__(self):
        # 从.env文件加载API密钥
        self.api_key = None
        if os.path.exists('.env'):
            with open('.env', 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith('SILICONFLOW_API_KEY='):
                        self.api_key = line.split('=', 1)[1].strip()
                        break
        
        if not self.api_key:
            print("❌ 未找到API密钥")
            return
        
        self.base_url = "https://api.siliconflow.cn/v1"
        self.model = "Qwen/Qwen2.5-VL-72B-Instruct"
        
    def encode_image_to_base64(self, image_path: str) -> str:
        """将图片编码为base64"""
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            raise Exception(f"无法读取图片文件: {e}")
    
    def analyze_image_and_generate_table(self, image_path: str) -> dict:
        """分析图片并生成表格"""
        result = {
            "success": False,
            "analysis": {},
            "table_data": [],
            "error": None,
            "timestamp": datetime.now().isoformat()
        }
        
        if not self.api_key:
            result["error"] = "未配置API密钥"
            return result
        
        try:
            # 检查图片文件是否存在
            if not os.path.exists(image_path):
                result["error"] = f"图片文件不存在: {image_path}"
                return result
            
            print(f"🔍 分析图片: {image_path}")
            
            # 获取图片基本信息
            with Image.open(image_path) as img:
                image_info = {
                    "format": img.format,
                    "size": img.size,
                    "width": img.width,
                    "height": img.height,
                    "mode": img.mode
                }
            
            result["image_info"] = image_info
            
            # 准备API请求
            base64_image = self.encode_image_to_base64(image_path)
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # 分析提示词 - 专门用于表格提取
            analysis_prompt = """
请详细分析这张图片，并完成以下任务：

1. 首先描述图片的整体内容和结构

2. 如果图片中包含表格、列表或结构化数据，请提取并整理成markdown表格格式

3. 如果图片中包含数字、文字或其他可量化的信息，请按类别整理成表格

4. 如果图片不是表格类型，请将主要信息点整理成结构化的表格形式

5. 请确保提取的信息准确完整，表格格式清晰易读

请按以下JSON格式返回结果：
{
  "description": "图片整体描述",
  "table_type": "表格类型描述",
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
  "key_points": ["关键点1", "关键点2"],
  "summary": "内容总结"
}
"""
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": analysis_prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 3000,
                "temperature": 0.1
            }
            
            print("🤖 正在调用AI分析...")
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=120
            )
            
            if response.status_code == 200:
                response_data = response.json()
                
                if "choices" in response_data and len(response_data["choices"]) > 0:
                    content = response_data["choices"][0]["message"]["content"]
                    
                    # 尝试解析JSON响应
                    try:
                        analysis_json = json.loads(content)
                        result["analysis"] = analysis_json
                        result["raw_response"] = content
                        result["success"] = True
                        
                        # 提取表格数据
                        if "tables" in analysis_json:
                            result["table_data"] = analysis_json["tables"]
                        
                    except json.JSONDecodeError:
                        # 如果不是JSON格式，保存原始响应
                        result["analysis"] = {
                            "description": content,
                            "table_type": "非结构化响应",
                            "tables": [],
                            "key_points": [],
                            "summary": "AI返回了非结构化响应"
                        }
                        result["raw_response"] = content
                        result["success"] = True
                    
                else:
                    result["error"] = "API返回格式异常"
            else:
                result["error"] = f"API调用失败 ({response.status_code}): {response.text}"
                
        except Exception as e:
            result["error"] = f"分析过程中出错: {e}"
        
        return result
    
    def generate_markdown_report(self, result: dict) -> str:
        """生成markdown格式的报告"""
        report = []
        
        report.append("# 图片分析报告")
        report.append(f"**分析时间**: {result['timestamp']}")
        report.append(f"**使用模型**: {self.model}")
        report.append("")
        
        if "image_info" in result:
            info = result["image_info"]
            report.append("## 图片信息")
            report.append(f"- **格式**: {info['format']}")
            report.append(f"- **尺寸**: {info['width']} × {info['height']} 像素")
            report.append(f"- **模式**: {info['mode']}")
            report.append("")
        
        if result["success"]:
            analysis = result["analysis"]
            
            if "description" in analysis:
                report.append("## 图片描述")
                report.append(analysis["description"])
                report.append("")
            
            if "table_type" in analysis:
                report.append("## 表格类型")
                report.append(analysis["table_type"])
                report.append("")
            
            if "tables" in analysis and analysis["tables"]:
                report.append("## 提取的表格")
                report.append("")
                
                for i, table in enumerate(analysis["tables"], 1):
                    if "title" in table:
                        report.append(f"### 表格 {i}: {table['title']}")
                    else:
                        report.append(f"### 表格 {i}")
                    
                    if "headers" in table and "rows" in table:
                        # 生成markdown表格
                        headers = table["headers"]
                        rows = table["rows"]
                        
                        # 表头
                        report.append("| " + " | ".join(str(h) for h in headers) + " |")
                        report.append("| " + " | ".join(["---"] * len(headers)) + " |")
                        
                        # 数据行
                        for row in rows:
                            report.append("| " + " | ".join(str(cell) for cell in row) + " |")
                    
                    report.append("")
            
            if "key_points" in analysis and analysis["key_points"]:
                report.append("## 关键信息")
                for point in analysis["key_points"]:
                    report.append(f"- {point}")
                report.append("")
            
            if "summary" in analysis:
                report.append("## 总结")
                report.append(analysis["summary"])
                report.append("")
            
        else:
            report.append("## 分析失败")
            report.append(f"错误信息: {result['error']}")
            report.append("")
        
        return "\n".join(report)

def main():
    """主函数"""
    print("🚀 图片表格分析工具")
    print("=" * 50)
    
    # 初始化分析器
    analyzer = ImageTableAnalyzer()
    
    if not analyzer.api_key:
        print("❌ API密钥未配置")
        print("请确保 .env 文件中包含正确的 SILICONFLOW_API_KEY")
        return
    
    print("✅ API密钥已配置")
    
    # 查找图片文件
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']
    image_files = []
    
    for file in os.listdir('.'):
        if any(file.lower().endswith(ext) for ext in image_extensions):
            image_files.append(file)
    
    if not image_files:
        print("❌ 当前目录中没有找到图片文件")
        print("💡 请将图片文件放在当前目录中，然后重新运行此脚本")
        return
    
    print(f"📁 找到 {len(image_files)} 个图片文件:")
    for i, img in enumerate(image_files, 1):
        print(f"   {i}. {img}")
    
    # 选择图片
    if len(image_files) == 1:
        selected_image = image_files[0]
    else:
        try:
            choice = int(input("\n👉 请选择要分析的图片编号: "))
            selected_image = image_files[choice - 1]
        except (ValueError, IndexError):
            print("⚠️  无效选择，使用第一个图片")
            selected_image = image_files[0]
    
    print(f"\n🎯 开始分析图片: {selected_image}")
    print("=" * 50)
    
    # 执行分析
    result = analyzer.analyze_image_and_generate_table(selected_image)
    
    # 生成报告
    if result["success"]:
        print("✅ 分析成功!")
        
        # 生成markdown报告
        markdown_report = analyzer.generate_markdown_report(result)
        
        # 保存结果
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_files = [
            f"image_analysis_{timestamp}.json",
            f"image_analysis_{timestamp}.md"
        ]
        
        # 保存JSON结果
        with open(output_files[0], 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        # 保存markdown报告
        with open(output_files[1], 'w', encoding='utf-8') as f:
            f.write(markdown_report)
        
        print(f"\n📊 分析结果:")
        print("=" * 50)
        print(markdown_report)
        
        print(f"\n💾 结果已保存到:")
        for file in output_files:
            print(f"   • {file}")
        
    else:
        print("❌ 分析失败")
        print(f"错误: {result['error']}")

if __name__ == "__main__":
    main()