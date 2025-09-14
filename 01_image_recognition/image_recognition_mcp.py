#!/usr/bin/env python3
"""
MCP服务器 - 图片识别和理解工具
为Claude Code提供图片识别能力
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from image_recognition_tool import ImageRecognitionTool

class ImageRecognitionMCPServer:
    def __init__(self):
        self.recognizer = ImageRecognitionTool()
        self.logger = logging.getLogger(__name__)
        
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """处理MCP请求"""
        method = request.get("method")
        params = request.get("params", {})
        
        try:
            if method == "tools/list":
                return await self.list_tools()
            elif method == "tools/call":
                return await self.call_tool(params)
            else:
                return {"error": f"未知方法: {method}"}
        except Exception as e:
            self.logger.error(f"处理请求时出错: {e}")
            return {"error": str(e)}
    
    async def list_tools(self) -> Dict[str, Any]:
        """列出可用工具"""
        return {
            "tools": [
                {
                    "name": "recognize_image",
                    "description": "识别图片内容并提取文字",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "image_path": {
                                "type": "string",
                                "description": "图片文件路径"
                            },
                            "method": {
                                "type": "string",
                                "enum": ["openai", "baidu"],
                                "default": "openai",
                                "description": "识别方法"
                            }
                        },
                        "required": ["image_path"]
                    }
                },
                {
                    "name": "understand_image",
                    "description": "理解图片内容并回答问题",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "image_path": {
                                "type": "string",
                                "description": "图片文件路径"
                            },
                            "question": {
                                "type": "string",
                                "description": "关于图片的问题"
                            }
                        },
                        "required": ["image_path"]
                    }
                },
                {
                    "name": "analyze_weather_image",
                    "description": "专门分析天气相关图片",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "image_path": {
                                "type": "string",
                                "description": "天气图片文件路径"
                            }
                        },
                        "required": ["image_path"]
                    }
                }
            ]
        }
    
    async def call_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """调用工具"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if tool_name == "recognize_image":
            return await self.recognize_image(arguments)
        elif tool_name == "understand_image":
            return await self.understand_image(arguments)
        elif tool_name == "analyze_weather_image":
            return await self.analyze_weather_image(arguments)
        else:
            return {"error": f"未知工具: {tool_name}"}
    
    async def recognize_image(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """识别图片"""
        image_path = args.get("image_path")
        method = args.get("method", "openai")
        
        if not image_path:
            return {"error": "缺少image_path参数"}
        
        if not os.path.exists(image_path):
            return {"error": f"图片文件不存在: {image_path}"}
        
        # 在实际实现中，这里应该异步调用识别功能
        # 为了简化，这里使用同步调用
        try:
            result = self.recognizer.extract_text_from_image(image_path, method)
            return {"content": result}
        except Exception as e:
            return {"error": str(e)}
    
    async def understand_image(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """理解图片"""
        image_path = args.get("image_path")
        question = args.get("question", "")
        
        if not image_path:
            return {"error": "缺少image_path参数"}
        
        if not os.path.exists(image_path):
            return {"error": f"图片文件不存在: {image_path}"}
        
        try:
            result = self.recognizer.understand_image(image_path, question)
            return {"content": result}
        except Exception as e:
            return {"error": str(e)}
    
    async def analyze_weather_image(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """分析天气图片"""
        image_path = args.get("image_path")
        
        if not image_path:
            return {"error": "缺少image_path参数"}
        
        if not os.path.exists(image_path):
            return {"error": f"图片文件不存在: {image_path}"}
        
        try:
            # 专门针对天气图片的分析提示
            weather_prompt = """请分析这张天气相关的图片，提取以下信息：
1. 天气状况（晴天、阴天、雨天等）
2. 温度信息
3. 湿度信息
4. 风力信息
5. 其他相关的天气数据
6. 图片中显示的地点和时间

请以JSON格式返回这些信息。"""
            
            result = self.recognizer.understand_image(image_path, weather_prompt)
            return {"content": result}
        except Exception as e:
            return {"error": str(e)}

async def main():
    """主函数"""
    logging.basicConfig(level=logging.INFO)
    server = ImageRecognitionMCPServer()
    
    # 简单的测试
    print("图片识别MCP服务器已启动")
    print("可用的工具:")
    tools = await server.list_tools()
    for tool in tools["tools"]:
        print(f"  - {tool['name']}: {tool['description']}")

if __name__ == "__main__":
    asyncio.run(main())