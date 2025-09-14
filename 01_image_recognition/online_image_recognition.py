#!/usr/bin/env python3
"""
在线图片识别工具 - 使用免费的OCR API
不需要本地安装Tesseract
"""

import os
import sys
import json
import requests
import base64
from typing import Dict, Any, Optional
from PIL import Image
import io
import re

class OnlineImageRecognitionTool:
    def __init__(self):
        self.ocr_space_api_key = "K89144843288957"  # 免费API密钥（有使用限制）
        self.ocr_space_url = "https://api.ocr.space/parse/image"
    
    def encode_image_to_base64(self, image_path: str) -> str:
        """将图片编码为base64"""
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            raise Exception(f"无法读取图片文件: {e}")
    
    def recognize_with_ocr_space(self, image_path: str, language: str = 'chi_sim+eng') -> Dict[str, Any]:
        """使用OCR.space API进行文字识别"""
        result = {
            "image_path": image_path,
            "success": False,
            "text_content": "",
            "confidence": 0,
            "error": None,
            "api_used": "OCR.space"
        }
        
        try:
            # 准备请求数据
            base64_image = self.encode_image_to_base64(image_path)
            
            payload = {
                'base64Image': f'data:image/jpeg;base64,{base64_image}',
                'language': language,
                'isOverlayRequired': False,
                'scale': True,
                'detectOrientation': True,
                'isTable': False
            }
            
            headers = {
                'apikey': self.ocr_space_api_key,
                'Content-Type': 'application/json'
            }
            
            print("  正在调用OCR.space API...")
            response = requests.post(self.ocr_space_url, 
                                   headers=headers, 
                                   json=payload, 
                                   timeout=30)
            
            if response.status_code == 200:
                response_data = response.json()
                
                if response_data.get('OCRExitCode') == 1:
                    # 识别成功
                    parsed_results = response_data.get('ParsedResults', [])
                    if parsed_results:
                        text_content = parsed_results[0].get('ParsedText', '')
                        text_overlay = parsed_results[0].get('TextOverlay', {})
                        confidence = text_overlay.get('MeanConfidence', 0)
                        
                        result["text_content"] = text_content.strip()
                        result["confidence"] = confidence
                        result["success"] = True
                    else:
                        result["error"] = "API返回空结果"
                else:
                    error_info = response_data.get('ErrorMessage', '未知错误')
                    result["error"] = f"OCR API错误: {error_info}"
            else:
                result["error"] = f"HTTP错误: {response.status_code}"
                
        except requests.exceptions.RequestException as e:
            result["error"] = f"网络请求失败: {e}"
        except Exception as e:
            result["error"] = f"处理失败: {e}"
        
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
    
    def extract_weather_info(self, text_content: str) -> Dict[str, Any]:
        """从文字中提取天气相关信息"""
        weather_patterns = {
            "temperature": [
                r'(\d+)°[CF]',  # 25°C
                r'温度[：:]\s*(\d+)',  # 温度:25
                r'气温[：:]\s*(\d+)',  # 气温:25
                r'(\d+)\s*度',  # 25度
            ],
            "humidity": [
                r'湿度[：:]\s*(\d+)%',  # 湿度:60%
                r'相对湿度[：:]\s*(\d+)%',  # 相对湿度:60%
                r'(\d+)%',  # 60%
            ],
            "wind": [
                r'风[力速]?[：:]\s*(\d+)\s*(km/h|m/s|级)',  # 风力:3级
                r'(\d+)\s*(km/h|m/s|级)',  # 10km/h
                r'(东风|西风|南风|北风|东南风|西北风|东北风|西南风)',  # 风向
            ],
            "pressure": [
                r'气压[：:]\s*(\d+)\s*(hPa|mbar)',  # 气压:1013hPa
                r'(\d+)\s*(hPa|mbar)',  # 1013hPa
            ],
            "weather_condition": [
                r'(晴|阴|雨|雪|雾|多云|局部|雷|暴雨|小雪|大雨)',
            ],
            "location": [
                r'(北京|上海|广州|深圳|天津|重庆|杭州|南京|武汉|成都)',
                r'(城市|地区)[：:]\s*([^\s]+)',
            ],
            "time": [
                r'(今天|明天|后天|上午|下午|晚上|凌晨|半夜)',
                r'(\d{1,2})[月时](\d{1,2})[日号]',  # 9月10日
                r'(\d{4})[-年](\d{1,2})[-月](\d{1,2})',  # 2025-09-10
            ]
        }
        
        extracted_info = {}
        
        for category, patterns in weather_patterns.items():
            matches = []
            for pattern in patterns:
                found = re.findall(pattern, text_content)
                if found:
                    matches.extend(found)
            
            if matches:
                extracted_info[category] = list(set(matches))  # 去重
        
        return extracted_info
    
    def generate_analysis_report(self, image_info: Dict, text_result: Dict, weather_info: Dict) -> str:
        """生成分析报告"""
        report_parts = []
        
        # 图片信息
        if image_info["success"]:
            img_info = image_info["image_info"]
            report_parts.append(f"📸 图片信息:")
            report_parts.append(f"   尺寸: {img_info['width']} × {img_info['height']} 像素")
            report_parts.append(f"   格式: {img_info['format']}")
            report_parts.append(f"   宽高比: {img_info['aspect_ratio']:.2f}")
        
        # 文字识别结果
        if text_result["success"]:
            text = text_result["text_content"]
            confidence = text_result["confidence"]
            
            report_parts.append(f"\n🔤 文字识别:")
            report_parts.append(f"   置信度: {confidence:.1f}%")
            report_parts.append(f"   文字长度: {len(text)} 字符")
            
            if text:
                # 内容类型判断
                content_types = []
                if any(word in text for word in ["天气", "温度", "湿度", "风", "气压"]):
                    content_types.append("天气信息")
                if any(word in text for word in ["时间", "日期", "今天", "明天"]):
                    content_types.append("时间信息")
                if any(word in text for word in ["北京", "上海", "广州", "城市"]):
                    content_types.append("地点信息")
                
                if content_types:
                    report_parts.append(f"   内容类型: {', '.join(content_types)}")
                else:
                    report_parts.append(f"   内容类型: 通用文本")
                
                # 显示前100个字符
                preview = text[:100].replace('\n', ' ').strip()
                if len(text) > 100:
                    preview += "..."
                report_parts.append(f"   内容预览: {preview}")
        
        # 天气信息
        if weather_info:
            report_parts.append(f"\n🌤️  天气信息分析:")
            for category, items in weather_info.items():
                if items:
                    category_name = {
                        "temperature": "温度",
                        "humidity": "湿度", 
                        "wind": "风力",
                        "pressure": "气压",
                        "weather_condition": "天气状况",
                        "location": "地点",
                        "time": "时间"
                    }.get(category, category)
                    
                    report_parts.append(f"   {category_name}: {', '.join(str(item) for item in items)}")
        
        # 总结
        report_parts.append(f"\n📋 总结:")
        if text_result["success"] and text_result["text_content"]:
            if weather_info:
                report_parts.append("   ✓ 确认为天气相关图片")
                report_parts.append("   ✓ 成功提取天气信息")
            else:
                report_parts.append("   ⚠ 可能不是天气图片，或文字识别不完整")
        else:
            report_parts.append("   ✗ 文字识别失败，无法分析内容")
        
        return "\n".join(report_parts)
    
    def comprehensive_analysis(self, image_path: str) -> Dict[str, Any]:
        """综合分析图片"""
        print(f"🔍 开始分析图片: {image_path}")
        
        # 1. 分析图片基本信息
        print("   📊 分析图片结构...")
        image_info = self.analyze_image_structure(image_path)
        
        # 2. 文字识别
        print("   🔤 进行文字识别...")
        text_result = self.recognize_with_ocr_space(image_path)
        
        # 3. 天气信息提取
        weather_info = {}
        if text_result["success"] and text_result["text_content"]:
            print("   🌤️  提取天气信息...")
            weather_info = self.extract_weather_info(text_result["text_content"])
        
        # 4. 生成分析报告
        print("   📋 生成分析报告...")
        analysis_report = self.generate_analysis_report(image_info, text_result, weather_info)
        
        # 组装结果
        result = {
            "image_path": image_path,
            "timestamp": str(__import__('datetime').datetime.now()),
            "image_info": image_info,
            "text_recognition": text_result,
            "weather_info": weather_info,
            "analysis_report": analysis_report
        }
        
        return result

def main():
    """主函数"""
    print("🚀 在线图片识别工具")
    print("=" * 50)
    
    # 初始化工具
    recognizer = OnlineImageRecognitionTool()
    
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
    result = recognizer.comprehensive_analysis(selected_image)
    
    # 显示结果
    print("\n" + "=" * 50)
    print("📊 分析结果")
    print("=" * 50)
    
    print(result["analysis_report"])
    
    # 保存结果
    output_file = f"analysis_result_{selected_image.split('.')[0]}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 分析结果已保存到: {output_file}")
    
    # 如果有天气信息，显示天气总结
    if result["weather_info"]:
        print("\n🌤️  天气信息总结:")
        for category, items in result["weather_info"].items():
            if items:
                category_name = {
                    "temperature": "🌡️ 温度",
                    "humidity": "💧 湿度", 
                    "wind": "💨 风力",
                    "pressure": "🔽 气压",
                    "weather_condition": "☀️ 天气状况",
                    "location": "📍 地点",
                    "time": "⏰ 时间"
                }.get(category, category)
                
                print(f"   {category_name}: {', '.join(str(item) for item in items)}")

if __name__ == "__main__":
    main()