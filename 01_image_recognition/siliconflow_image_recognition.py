#!/usr/bin/env python3
"""
硅基流动图片识别工具
支持国产多模态大模型进行图片识别和理解
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

class SiliconFlowImageRecognitionTool:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('SILICONFLOW_API_KEY')
        self.base_url = "https://api.siliconflow.cn/v1"
        
        # 支持的模型列表（根据硅基流动实际支持的模型）
        self.supported_models = {
            "Qwen/Qwen2-VL-72B-Instruct": "通义千问VL 72B",
            "Qwen/Qwen2-VL-7B-Instruct": "通义千问VL 7B",
            "deepseek-ai/deepseek-vl": "DeepSeek VL",
            "01-ai/Yi-VL-6B": "Yi VL 6B",
            "THUDM/glm-4v": "GLM-4V",
            "MiniCPM-V/MiniCPM-V-6B": "MiniCPM-V 6B"
        }
        
        self.default_model = "Qwen/Qwen2-VL-72B-Instruct"
        
        if not self.api_key:
            print("⚠️ 未配置SiliconFlow API密钥")
            print("请设置环境变量: export SILICONFLOW_API_KEY=your_key_here")
    
    def encode_image_to_base64(self, image_path: str) -> str:
        """将图片编码为base64"""
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            raise Exception(f"无法读取图片文件: {e}")
    
    def recognize_with_siliconflow(self, image_path: str, prompt: str = "请详细描述这张图片的内容", 
                                 model: str = None) -> Dict[str, Any]:
        """使用硅基流动API进行图片识别"""
        result = {
            "image_path": image_path,
            "success": False,
            "content": "",
            "model_used": model or self.default_model,
            "error": None,
            "api_used": "SiliconFlow"
        }
        
        if not self.api_key:
            result["error"] = "未配置SiliconFlow API密钥"
            return result
        
        try:
            # 准备图片数据
            base64_image = self.encode_image_to_base64(image_path)
            
            # 构建请求
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # 根据不同模型构建请求格式
            model_name = model or self.default_model
            
            if "qwen" in model_name.lower():
                # 通义千问VL格式
                payload = {
                    "model": model_name,
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{base64_image}"
                                    }
                                }
                            ]
                        }
                    ],
                    "max_tokens": 2000,
                    "temperature": 0.1
                }
            else:
                # 其他模型的通用格式
                payload = {
                    "model": model_name,
                    "messages": [
                        {
                            "role": "user",
                            "content": f"{prompt}\n\n图片数据: data:image/jpeg;base64,{base64_image}"
                        }
                    ],
                    "max_tokens": 2000,
                    "temperature": 0.1
                }
            
            print(f"  🤖 正在调用 {self.supported_models.get(model_name, model_name)} 模型...")
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                response_data = response.json()
                
                if "choices" in response_data and len(response_data["choices"]) > 0:
                    content = response_data["choices"][0]["message"]["content"]
                    result["content"] = content.strip()
                    result["success"] = True
                    
                    # 提取使用信息
                    if "usage" in response_data:
                        result["usage"] = response_data["usage"]
                else:
                    result["error"] = "API返回格式异常"
            else:
                error_msg = response.text
                result["error"] = f"API调用失败 ({response.status_code}): {error_msg}"
                
        except requests.exceptions.RequestException as e:
            result["error"] = f"网络请求失败: {e}"
        except Exception as e:
            result["error"] = f"处理失败: {e}"
        
        return result
    
    def extract_weather_info(self, text_content: str) -> Dict[str, Any]:
        """从文字中提取天气相关信息"""
        weather_patterns = {
            "temperature": [
                r'(\d+)°[CF]',  # 25°C
                r'温度[：:]\s*(\d+)',  # 温度:25
                r'气温[：:]\s*(\d+)',  # 气温:25
                r'(\d+)\s*度',  # 25度
                r'最高温度[：:]\s*(\d+)',  # 最高温度:30
                r'最低温度[：:]\s*(\d+)',  # 最低温度:15
            ],
            "humidity": [
                r'湿度[：:]\s*(\d+)%',  # 湿度:60%
                r'相对湿度[：:]\s*(\d+)%',  # 相对湿度:60%
                r'(\d+)%',  # 60%
            ],
            "wind": [
                r'风[力速]?[：:]\s*(\d+)\s*(km/h|m/s|级)',  # 风力:3级
                r'(\d+)\s*(km/h|m/s|级)',  # 10km/h
                r'(东风|西风|南风|北风|东南风|西北风|东北风|西南风)',
                r'无风|微风|轻风|中风|强风',
            ],
            "pressure": [
                r'气压[：:]\s*(\d+)\s*(hPa|mbar)',  # 气压:1013hPa
                r'(\d+)\s*(hPa|mbar)',  # 1013hPa
            ],
            "weather_condition": [
                r'(晴|阴|雨|雪|雾|多云|局部|雷|暴雨|小雪|大雨|中雨|晴朗)',
            ],
            "location": [
                r'(北京|上海|广州|深圳|天津|重庆|杭州|南京|武汉|成都|西安|苏州)',
                r'(城市|地区)[：:]\s*([^\s]+)',
            ],
            "time": [
                r'(今天|明天|后天|上午|下午|晚上|凌晨|半夜|清晨)',
                r'(\d{1,2})[月时](\d{1,2})[日号]',  # 9月10日
                r'(\d{4})[-年](\d{1,2})[-月](\d{1,2})',  # 2025-09-10
                r'周[一二三四五六七日]',  # 周一
            ],
            "air_quality": [
                r'空气质量[：:]\s*([^\n]+)',
                r'(优|良|轻度污染|中度污染|重度污染)',
                r'PM2\.5[：:]\s*(\d+)',
                r'PM10[：:]\s*(\d+)',
            ],
            "uv_index": [
                r'紫外线[：:]\s*([^\n]+)',
                r'UV指数[：:]\s*(\d+)',
                r'(弱|中等|强|很强|极强)',
            ]
        }
        
        extracted_info = {}
        
        for category, patterns in weather_patterns.items():
            matches = []
            for pattern in patterns:
                found = re.findall(pattern, text_content, re.IGNORECASE)
                if found:
                    matches.extend(found)
            
            if matches:
                extracted_info[category] = list(set(matches))  # 去重
        
        return extracted_info
    
    def comprehensive_weather_analysis(self, image_path: str, model: str = None) -> Dict[str, Any]:
        """综合天气图片分析"""
        print(f"🔍 开始分析天气图片: {image_path}")
        
        # 1. 基本图片信息
        print("  📊 分析图片基本信息...")
        image_info = self.analyze_image_structure(image_path)
        
        # 2. 天气专业分析
        weather_prompt = """请详细分析这张天气相关图片，提取以下信息：

1. 地点信息：图片显示的是哪个城市或地区的天气？
2. 时间信息：显示的是什么时间的天气？（今天、明天、具体日期等）
3. 温度信息：当前温度、最高温度、最低温度
4. 天气状况：晴天、阴天、雨天、雪天、多云等
5. 湿度信息：相对湿度百分比
6. 风力信息：风速、风向、风力等级
7. 气压信息：大气压数值
8. 其他指标：空气质量、紫外线指数、能见度等
9. 特殊提醒：是否有恶劣天气预警、特殊天气现象等

请以结构化的方式回答，如果有不确定的信息请说明。"""
        
        print("  🌤️  进行AI天气分析...")
        ai_result = self.recognize_with_siliconflow(image_path, weather_prompt, model)
        
        # 3. 提取结构化天气数据
        weather_data = {}
        if ai_result["success"]:
            print("  📋 提取结构化天气数据...")
            weather_data = self.extract_weather_info(ai_result["content"])
        
        # 4. 生成综合报告
        print("  📝 生成综合分析报告...")
        analysis_report = self.generate_weather_report(image_info, ai_result, weather_data)
        
        result = {
            "image_path": image_path,
            "timestamp": str(__import__('datetime').datetime.now()),
            "image_info": image_info,
            "ai_analysis": ai_result,
            "extracted_weather_data": weather_data,
            "analysis_report": analysis_report
        }
        
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
    
    def generate_weather_report(self, image_info: Dict, ai_result: Dict, weather_data: Dict) -> str:
        """生成天气分析报告"""
        report_parts = []
        
        # 图片信息
        if image_info["success"]:
            img_info = image_info["image_info"]
            report_parts.append(f"📸 图片信息:")
            report_parts.append(f"   尺寸: {img_info['width']} × {img_info['height']} 像素")
            report_parts.append(f"   格式: {img_info['format']}")
        
        # AI分析结果
        if ai_result["success"]:
            model_name = self.supported_models.get(ai_result["model_used"], ai_result["model_used"])
            report_parts.append(f"\n🤖 AI分析结果 ({model_name}):")
            report_parts.append(f"   {ai_result['content']}")
        else:
            report_parts.append(f"\n❌ AI分析失败: {ai_result['error']}")
        
        # 结构化天气数据
        if weather_data:
            report_parts.append(f"\n🌤️  结构化天气数据:")
            
            category_names = {
                "location": "📍 地点",
                "time": "⏰ 时间", 
                "temperature": "🌡️ 温度",
                "weather_condition": "☀️ 天气状况",
                "humidity": "💧 湿度",
                "wind": "💨 风力",
                "pressure": "🔽 气压",
                "air_quality": "🌬️ 空气质量",
                "uv_index": "☀️ 紫外线"
            }
            
            for category, items in weather_data.items():
                category_name = category_names.get(category, category)
                report_parts.append(f"   {category_name}: {', '.join(str(item) for item in items)}")
        
        return "\n".join(report_parts)

def main():
    """主函数"""
    print("🚀 硅基流动图片识别工具")
    print("=" * 50)
    
    # 检查API密钥
    api_key = os.getenv('SILICONFLOW_API_KEY')
    if not api_key:
        print("❌ 未找到SiliconFlow API密钥")
        print("请设置环境变量: export SILICONFLOW_API_KEY=your_key_here")
        return
    
    print("✅ API密钥已配置")
    
    # 初始化工具
    recognizer = SiliconFlowImageRecognitionTool(api_key)
    
    # 显示支持的模型
    print(f"\n🤖 支持的模型:")
    for model_id, model_name in recognizer.supported_models.items():
        marker = "📍" if model_id == recognizer.default_model else "  "
        print(f"   {marker} {model_name} ({model_id})")
    
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
    
    print(f"\n📁 找到 {len(image_files)} 个图片文件:")
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
    
    # 选择模型
    print(f"\n🤖 选择分析模型 (默认: {recognizer.default_model})")
    print("直接回车使用默认模型，或输入模型编号:")
    model_list = list(recognizer.supported_models.keys())
    for i, model in enumerate(model_list, 1):
        print(f"   {i}. {recognizer.supported_models[model]}")
    
    model_choice = input("请选择: ").strip()
    if model_choice:
        try:
            selected_model = model_list[int(model_choice) - 1]
        except (ValueError, IndexError):
            print("⚠️  无效选择，使用默认模型")
            selected_model = recognizer.default_model
    else:
        selected_model = recognizer.default_model
    
    print(f"\n🎯 开始分析图片: {selected_image}")
    print(f"🤖 使用模型: {recognizer.supported_models.get(selected_model, selected_model)}")
    print("=" * 50)
    
    # 执行分析
    result = recognizer.comprehensive_weather_analysis(selected_image, selected_model)
    
    # 显示结果
    print("\n" + "=" * 50)
    print("📊 分析结果")
    print("=" * 50)
    
    print(result["analysis_report"])
    
    # 保存结果
    output_file = f"siliconflow_analysis_{selected_image.split('.')[0]}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 分析结果已保存到: {output_file}")

if __name__ == "__main__":
    main()