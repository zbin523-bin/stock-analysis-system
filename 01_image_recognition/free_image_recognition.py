#!/usr/bin/env python3
"""
免费图片识别工具 - 使用Tesseract OCR
不需要API密钥，本地运行
"""

import os
import sys
import json
import subprocess
import tempfile
import base64
from typing import Dict, Any, Optional
from PIL import Image
import io

class FreeImageRecognitionTool:
    def __init__(self):
        self.check_dependencies()
    
    def check_dependencies(self):
        """检查依赖项"""
        try:
            import pytesseract
            from PIL import Image
            print("✓ Python依赖库已安装")
        except ImportError as e:
            print(f"✗ 缺少依赖库: {e}")
            print("请运行: pip install pytesseract pillow")
            sys.exit(1)
        
        # 检查tesseract是否安装
        try:
            result = subprocess.run(['tesseract', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✓ Tesseract OCR已安装")
            else:
                print("⚠ Tesseract OCR可能未正确安装")
        except FileNotFoundError:
            print("✗ 未找到Tesseract OCR")
            print("请安装Tesseract OCR:")
            print("  macOS: brew install tesseract")
            print("  Ubuntu: sudo apt-get install tesseract-ocr")
            print("  Windows: 下载安装tesseract from https://github.com/UB-Mannheim/tesseract/wiki")
    
    def recognize_text(self, image_path: str) -> Dict[str, Any]:
        """使用Tesseract识别图片中的文字"""
        result = {
            "image_path": image_path,
            "success": False,
            "text_content": "",
            "confidence": 0,
            "error": None
        }
        
        try:
            import pytesseract
            from PIL import Image
            
            # 打开图片
            image = Image.open(image_path)
            
            # 使用Tesseract进行OCR
            text = pytesseract.image_to_string(image, lang='chi_sim+eng')
            
            # 获取详细数据包括置信度
            data = pytesseract.image_to_data(image, lang='chi_sim+eng', output_type=pytesseract.Output.DICT)
            
            # 计算平均置信度
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            result["text_content"] = text.strip()
            result["confidence"] = avg_confidence
            result["success"] = True
            
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def analyze_image_structure(self, image_path: str) -> Dict[str, Any]:
        """分析图片的基本结构"""
        result = {
            "image_path": image_path,
            "success": False,
            "image_info": {},
            "error": None
        }
        
        try:
            from PIL import Image
            
            with Image.open(image_path) as img:
                result["image_info"] = {
                    "format": img.format,
                    "size": img.size,
                    "mode": img.mode,
                    "width": img.width,
                    "height": img.height,
                    "aspect_ratio": img.width / img.height,
                    "has_transparency": img.mode in ('RGBA', 'LA') or 'transparency' in img.info
                }
                result["success"] = True
            
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def detect_weather_info(self, text_content: str) -> Dict[str, Any]:
        """从文字中检测天气相关信息"""
        weather_keywords = {
            "temperature": ["温度", "气温", "°C", "°F", "度"],
            "humidity": ["湿度", "相对湿度", "%"],
            "wind": ["风", "风速", "风力", "km/h", "m/s"],
            "pressure": ["气压", "hPa", "mbar"],
            "weather_condition": ["晴", "阴", "雨", "雪", "雾", "多云", "局部"],
            "location": ["北京", "上海", "广州", "深圳", "城市", "地区"],
            "time": ["今天", "明天", "上午", "下午", "晚上", "日期"]
        }
        
        detected_info = {}
        
        for category, keywords in weather_keywords.items():
            found_items = []
            for keyword in keywords:
                if keyword in text_content:
                    # 找到关键词周围的文本
                    start_idx = text_content.find(keyword)
                    # 获取关键词前后的文本（各30个字符）
                    start = max(0, start_idx - 30)
                    end = min(len(text_content), start_idx + len(keyword) + 30)
                    context = text_content[start:end].strip()
                    found_items.append(context)
            
            if found_items:
                detected_info[category] = found_items
        
        return detected_info
    
    def comprehensive_analysis(self, image_path: str) -> Dict[str, Any]:
        """综合分析图片"""
        print(f"正在分析图片: {image_path}")
        
        # 1. 基本图片信息
        print("  - 分析图片基本信息...")
        image_info = self.analyze_image_structure(image_path)
        
        # 2. 文字识别
        print("  - 识别文字内容...")
        text_result = self.recognize_text(image_path)
        
        analysis_result = {
            "image_path": image_path,
            "timestamp": str(__import__('datetime').datetime.now()),
            "image_info": image_info,
            "text_recognition": text_result,
            "weather_info": {},
            "ai_analysis": ""
        }
        
        # 3. 如果文字识别成功，进行天气信息检测
        if text_result["success"] and text_result["text_content"]:
            print("  - 检测天气信息...")
            weather_info = self.detect_weather_info(text_result["text_content"])
            analysis_result["weather_info"] = weather_info
            
            # 4. 生成AI分析
            print("  - 生成智能分析...")
            analysis_result["ai_analysis"] = self.generate_analysis(
                image_info, text_result, weather_info
            )
        
        return analysis_result
    
    def generate_analysis(self, image_info: Dict, text_result: Dict, weather_info: Dict) -> str:
        """生成智能分析报告"""
        analysis_parts = []
        
        # 图片信息分析
        if image_info["success"]:
            img_info = image_info["image_info"]
            analysis_parts.append(f"图片尺寸: {img_info['width']}x{img_info['height']}")
            analysis_parts.append(f"图片格式: {img_info['format']}")
        
        # 文字识别分析
        if text_result["success"]:
            text = text_result["text_content"]
            confidence = text_result["confidence"]
            
            analysis_parts.append(f"文字识别置信度: {confidence:.1f}%")
            
            if text:
                analysis_parts.append(f"识别到文字内容: {len(text)} 字符")
                
                # 简单的内容分析
                if any(word in text for word in ["天气", "温度", "湿度", "风"]):
                    analysis_parts.append("✓ 确认为天气相关图片")
                else:
                    analysis_parts.append("⚠ 可能不是天气图片")
        
        # 天气信息分析
        if weather_info:
            analysis_parts.append("检测到的天气信息:")
            for category, items in weather_info.items():
                if items:
                    analysis_parts.append(f"  - {category}: {', '.join(items)}")
        
        return "\n".join(analysis_parts)

def main():
    """主函数"""
    print("=== 免费图片识别工具 ===\n")
    
    # 初始化工具
    recognizer = FreeImageRecognitionTool()
    
    # 查找图片文件
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']
    image_files = []
    
    for file in os.listdir('.'):
        if any(file.lower().endswith(ext) for ext in image_extensions):
            image_files.append(file)
    
    if not image_files:
        print("当前目录中没有找到图片文件")
        print("请将图片文件放在当前目录中，然后重新运行此脚本")
        return
    
    print(f"找到 {len(image_files)} 个图片文件:")
    for i, img in enumerate(image_files, 1):
        print(f"  {i}. {img}")
    
    # 选择图片
    if len(image_files) == 1:
        selected_image = image_files[0]
    else:
        try:
            choice = int(input("\n请选择要分析的图片编号: "))
            selected_image = image_files[choice - 1]
        except (ValueError, IndexError):
            print("无效选择，使用第一个图片")
            selected_image = image_files[0]
    
    print(f"\n开始分析图片: {selected_image}")
    print("=" * 50)
    
    # 执行分析
    result = recognizer.comprehensive_analysis(selected_image)
    
    # 显示结果
    print("\n=== 分析结果 ===")
    print(f"图片路径: {result['image_path']}")
    print(f"分析时间: {result['timestamp']}")
    
    if result['image_info']['success']:
        print(f"\n图片信息:")
        img_info = result['image_info']['image_info']
        for key, value in img_info.items():
            print(f"  {key}: {value}")
    
    if result['text_recognition']['success']:
        print(f"\n文字识别:")
        text_result = result['text_recognition']
        print(f"  置信度: {text_result['confidence']:.1f}%")
        print(f"  识别内容:")
        print(f"    {text_result['text_content'][:200]}...")
    
    if result['weather_info']:
        print(f"\n天气信息:")
        for category, items in result['weather_info'].items():
            if items:
                print(f"  {category}: {', '.join(items)}")
    
    print(f"\n智能分析:")
    print(result['ai_analysis'])
    
    # 保存结果
    output_file = f"analysis_result_{selected_image.split('.')[0]}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n分析结果已保存到: {output_file}")

if __name__ == "__main__":
    main()