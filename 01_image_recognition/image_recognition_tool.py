#!/usr/bin/env python3
"""
图片识别和理解工具
支持多种OCR和图像识别服务
"""

import base64
import requests
import json
from typing import Dict, Any, Optional
import os

class ImageRecognitionTool:
    def __init__(self):
        self.api_keys = {
            'openai': os.getenv('OPENAI_API_KEY'),
            'baidu_ocr': os.getenv('BAIDU_OCR_API_KEY'),
            'tencent_ocr': os.getenv('TENCENT_OCR_API_KEY')
        }
    
    def encode_image(self, image_path: str) -> str:
        """将图片编码为base64"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def recognize_with_openai(self, image_path: str, prompt: str = "请描述这张图片的内容") -> str:
        """使用GPT-4V进行图像识别"""
        if not self.api_keys['openai']:
            return "未配置OpenAI API密钥"
        
        base64_image = self.encode_image(image_path)
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_keys['openai']}"
        }
        
        payload = {
            "model": "gpt-4-vision-preview",
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
            "max_tokens": 500
        }
        
        try:
            response = requests.post("https://api.openai.com/v1/chat/completions", 
                                  headers=headers, json=payload)
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            return f"OpenAI API调用失败: {str(e)}"
    
    def recognize_with_baidu_ocr(self, image_path: str) -> str:
        """使用百度OCR进行文字识别"""
        if not self.api_keys['baidu_ocr']:
            return "未配置百度OCR API密钥"
        
        # 这里实现百度OCR调用逻辑
        # 需要先获取access_token，然后调用OCR API
        return "百度OCR功能待实现"
    
    def extract_text_from_image(self, image_path: str, method: str = "openai") -> Dict[str, Any]:
        """从图片中提取文字和信息"""
        result = {
            "image_path": image_path,
            "method": method,
            "success": False,
            "content": "",
            "error": None
        }
        
        try:
            if method == "openai":
                content = self.recognize_with_openai(image_path, "请提取图片中的所有文字内容")
            elif method == "baidu":
                content = self.recognize_with_baidu_ocr(image_path)
            else:
                content = f"不支持的识别方法: {method}"
            
            result["content"] = content
            result["success"] = True
            
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def understand_image(self, image_path: str, question: str = "") -> Dict[str, Any]:
        """理解图片内容并回答问题"""
        prompt = f"请分析这张图片并回答：{question}" if question else "请详细描述这张图片的内容"
        
        result = {
            "image_path": image_path,
            "question": question,
            "success": False,
            "answer": "",
            "error": None
        }
        
        try:
            answer = self.recognize_with_openai(image_path, prompt)
            result["answer"] = answer
            result["success"] = True
            
        except Exception as e:
            result["error"] = str(e)
        
        return result

# 使用示例
if __name__ == "__main__":
    recognizer = ImageRecognitionTool()
    
    # 测试图片识别
    image_path = "test_image.jpg"
    
    # 提取文字
    text_result = recognizer.extract_text_from_image(image_path)
    print("文字提取结果:", json.dumps(text_result, ensure_ascii=False, indent=2))
    
    # 理解图片
    understanding_result = recognizer.understand_image(image_path, "这张图片中有什么天气信息？")
    print("图片理解结果:", json.dumps(understanding_result, ensure_ascii=False, indent=2))