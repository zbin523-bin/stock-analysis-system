#!/usr/bin/env python3
"""
自动化图片分析系统
当用户上传图片或需要分析图片时自动调用
"""

import os
import json
import glob
import time
import threading
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

# 导入现有的分析工具
from siliconflow_image_recognition import SiliconFlowImageRecognitionTool
from analyze_wechat_image import analyze_wechat_image
from analyze_real_image import analyze_real_user_image
from image_table_analyzer import ImageTableAnalyzer

class AutomatedImageAnalyzer:
    """自动化图片分析系统"""
    
    def __init__(self, api_key: str = None, watch_directory: str = "pic"):
        """
        初始化自动化图片分析系统
        
        Args:
            api_key: 硅基流动API密钥
            watch_directory: 监控的图片目录
        """
        self.watch_directory = watch_directory
        self.api_key = api_key
        self.analyzer = None
        self.table_analyzer = None
        self.is_running = False
        self.analysis_history = []
        self.config_file = "image_analyzer_config.json"
        
        # 确保监控目录存在
        os.makedirs(watch_directory, exist_ok=True)
        
        # 加载配置
        self._load_config()
        
        # 初始化分析器
        self._initialize_analyzers()
        
        # 支持的图片格式
        self.supported_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']
        
        # 系统记忆文件
        self.memory_file = "image_analysis_memory.json"
        self._load_memory()
    
    def _load_config(self):
        """加载配置文件"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            except Exception as e:
                print(f"❌ 加载配置文件失败: {e}")
                self.config = self._get_default_config()
        else:
            self.config = self._get_default_config()
            self._save_config()
    
    def _get_default_config(self) -> Dict:
        """获取默认配置"""
        return {
            "auto_analyze": True,
            "auto_watch": True,
            "default_model": "Qwen/Qwen2.5-VL-72B-Instruct",
            "analysis_types": {
                "wechat": True,
                "table": True,
                "general": True,
                "weather": True
            },
            "output_formats": ["json", "txt"],
            "save_history": True,
            "max_history_size": 100
        }
    
    def _save_config(self):
        """保存配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ 保存配置文件失败: {e}")
    
    def _initialize_analyzers(self):
        """初始化分析器"""
        if not self.api_key:
            # 尝试从环境变量或.env文件加载
            if os.path.exists('.env'):
                with open('.env', 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.startswith('SILICONFLOW_API_KEY='):
                            self.api_key = line.split('=', 1)[1].strip()
                            break
        
        if not self.api_key:
            print("❌ 未找到API密钥，某些功能可能无法使用")
            return
        
        try:
            self.analyzer = SiliconFlowImageRecognitionTool(self.api_key)
            self.table_analyzer = ImageTableAnalyzer(self.api_key)
            print("✅ 图片分析器初始化成功")
        except Exception as e:
            print(f"❌ 初始化分析器失败: {e}")
    
    def _load_memory(self):
        """加载系统记忆"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    self.memory = json.load(f)
            except Exception as e:
                print(f"❌ 加载记忆文件失败: {e}")
                self.memory = self._get_default_memory()
        else:
            self.memory = self._get_default_memory()
            self._save_memory()
    
    def _get_default_memory(self) -> Dict:
        """获取默认记忆"""
        return {
            "total_analyzed": 0,
            "analysis_history": [],
            "frequent_patterns": {},
            "user_preferences": {
                "preferred_model": "Qwen/Qwen2.5-VL-72B-Instruct",
                "preferred_analysis_type": "general"
            },
            "learned_insights": []
        }
    
    def _save_memory(self):
        """保存系统记忆"""
        try:
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.memory, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ 保存记忆文件失败: {e}")
    
    def _update_memory(self, analysis_result: Dict):
        """更新系统记忆"""
        self.memory["total_analyzed"] += 1
        
        # 添加到历史记录
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "image_path": analysis_result.get("image_path", ""),
            "analysis_type": analysis_result.get("analysis_type", "general"),
            "model_used": analysis_result.get("model_used", ""),
            "success": analysis_result.get("success", False)
        }
        
        self.memory["analysis_history"].append(history_entry)
        
        # 限制历史记录大小
        if len(self.memory["analysis_history"]) > self.config["max_history_size"]:
            self.memory["analysis_history"] = self.memory["analysis_history"][-self.config["max_history_size"]:]
        
        # 更新用户偏好
        if analysis_result.get("success"):
            model_used = analysis_result.get("model_used", "")
            if model_used:
                if model_used not in self.memory["frequent_patterns"]:
                    self.memory["frequent_patterns"][model_used] = 0
                self.memory["frequent_patterns"][model_used] += 1
                
                # 更新首选模型
                most_used = max(self.memory["frequent_patterns"], key=self.memory["frequent_patterns"].get)
                self.memory["user_preferences"]["preferred_model"] = most_used
        
        self._save_memory()
    
    def _get_image_files(self) -> List[str]:
        """获取监控目录中的所有图片文件"""
        image_files = []
        
        for ext in self.supported_extensions:
            pattern = os.path.join(self.watch_directory, f"*{ext}")
            image_files.extend(glob.glob(pattern))
            pattern = os.path.join(self.watch_directory, f"*{ext.upper()}")
            image_files.extend(glob.glob(pattern))
        
        # 过滤掉系统文件和隐藏文件
        image_files = [f for f in image_files if not os.path.basename(f).startswith('._')]
        
        return sorted(image_files, key=os.path.getctime, reverse=True)
    
    def _determine_analysis_type(self, image_path: str) -> str:
        """根据文件名和内容确定分析类型"""
        filename = os.path.basename(image_path).lower()
        
        if "wechat" in filename or "微信" in filename:
            return "wechat"
        elif "table" in filename or "表格" in filename or "表" in filename:
            return "table"
        elif "weather" in filename or "天气" in filename:
            return "weather"
        else:
            return "general"
    
    def analyze_image(self, image_path: str, analysis_type: str = None) -> Dict:
        """
        分析单个图片
        
        Args:
            image_path: 图片文件路径
            analysis_type: 分析类型 (wechat, table, weather, general)
        
        Returns:
            分析结果字典
        """
        if not os.path.exists(image_path):
            return {
                "success": False,
                "error": f"图片文件不存在: {image_path}",
                "image_path": image_path,
                "timestamp": datetime.now().isoformat()
            }
        
        if not analysis_type:
            analysis_type = self._determine_analysis_type(image_path)
        
        print(f"🔍 开始分析图片: {os.path.basename(image_path)}")
        print(f"📊 分析类型: {analysis_type}")
        
        result = {
            "image_path": image_path,
            "analysis_type": analysis_type,
            "timestamp": datetime.now().isoformat(),
            "success": False
        }
        
        try:
            # 根据分析类型选择不同的分析方法
            if analysis_type == "wechat" and "微信" in image_path:
                # 使用专门的微信图片分析工具
                analysis_result = analyze_wechat_image()
                if analysis_result:
                    result.update({
                        "success": True,
                        "content": analysis_result.get("analysis_content", ""),
                        "extracted_data": analysis_result.get("extracted_data", {}),
                        "model_used": "Qwen/Qwen2.5-VL-72B-Instruct"
                    })
            
            elif analysis_type == "table" and self.table_analyzer:
                # 使用表格分析工具
                table_result = self.table_analyzer.analyze_image_table(image_path)
                if table_result.get("success"):
                    result.update({
                        "success": True,
                        "content": table_result.get("description", ""),
                        "extracted_data": {"table": table_result.get("table_data", {})},
                        "model_used": table_result.get("model_used", "")
                    })
            
            elif self.analyzer:
                # 使用通用分析工具
                prompt = self._get_analysis_prompt(analysis_type)
                model = self.config.get("default_model", "Qwen/Qwen2.5-VL-72B-Instruct")
                
                analysis_result = self.analyzer.recognize_with_siliconflow(
                    image_path, prompt, model
                )
                
                if analysis_result['success']:
                    result.update({
                        "success": True,
                        "content": analysis_result['content'],
                        "model_used": analysis_result['model_used']
                    })
                    
                    # 提取结构化数据
                    result["extracted_data"] = self._extract_structured_data(analysis_result['content'])
                else:
                    result["error"] = analysis_result.get('error', '未知错误')
            else:
                result["error"] = "分析器未初始化"
        
        except Exception as e:
            result["error"] = f"分析过程中出错: {e}"
            print(f"❌ 分析图片时出错: {e}")
        
        # 保存分析结果
        if result["success"]:
            self._save_analysis_result(result)
        
        # 更新系统记忆
        self._update_memory(result)
        
        return result
    
    def _get_analysis_prompt(self, analysis_type: str) -> str:
        """根据分析类型获取对应的提示词"""
        prompts = {
            "wechat": """
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
""",
            "table": """
请详细分析这张包含表格的图片：

1. **表格结构分析**：
   - 表格有多少行多少列？
   - 表格的标题和表头是什么？
   - 表格的整体结构如何？

2. **数据提取**：
   - 请完整提取表格中的所有数据
   - 确保数据的准确性和完整性
   - 注意数据格式和单位

3. **表格内容分析**：
   - 这个表格展示了什么信息？
   - 数据之间的关系和趋势如何？
   - 有什么重要的数据点？

4. **格式化输出**：
   - 请将表格数据整理成结构化格式
   - 保持原有的数据格式和精度
   - 提供清晰的数据组织

请确保提取的表格数据准确无误，并保持原有的格式和结构。
""",
            "weather": """
请详细分析这张天气相关图片：

1. **天气信息识别**：
   - 图片中显示的是什么天气信息？
   - 包含哪些气象参数？
   - 数据的单位和数值是什么？

2. **数据提取**：
   - 温度、湿度、压力等具体数值
   - 风速、风向信息
   - 其他气象参数

3. **图表分析**：
   - 如果有图表，请分析图表类型和内容
   - 数据趋势和变化规律
   - 重要数据点和异常值

4. **综合判断**：
   - 当前天气状况如何？
   - 是否有异常天气情况？
   - 需要特别注意的信息？

请提供准确的天气数据分析，重点关注数值信息的提取。
""",
            "general": """
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
        }
        
        return prompts.get(analysis_type, prompts["general"])
    
    def _extract_structured_data(self, content: str) -> Dict:
        """从分析内容中提取结构化数据"""
        import re
        
        data = {}
        
        # 提取数字
        numbers = re.findall(r'\d+(?:\.\d+)?', content)
        if numbers:
            data["numbers"] = numbers
        
        # 提取时间信息
        time_patterns = re.findall(r'\d{4}[-年]\d{1,2}[-月]\d{1,2}|\d{1,2}[:时]\d{1,2}|\d{1,2}月\d{1,2}日|\d{1,2}:\d{2}', content)
        if time_patterns:
            data["time_patterns"] = time_patterns
        
        # 提取可能的表格信息
        if any(keyword in content for keyword in ['表格', '表', 'table', '行', '列']):
            data["contains_table"] = True
        
        # 提取可能的天气信息
        weather_keywords = ['温度', '湿度', '压力', '风速', '天气', '晴', '雨', '雪', '阴']
        found_weather = [kw for kw in weather_keywords if kw in content]
        if found_weather:
            data["weather_keywords"] = found_weather
        
        return data
    
    def _save_analysis_result(self, result: Dict):
        """保存分析结果到文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"analysis_result_{timestamp}.json"
        filepath = os.path.join(self.watch_directory, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"💾 分析结果已保存到: {filepath}")
        except Exception as e:
            print(f"❌ 保存分析结果失败: {e}")
    
    def analyze_new_images(self) -> List[Dict]:
        """分析监控目录中的新图片"""
        if not self.config.get("auto_analyze", True):
            return []
        
        image_files = self._get_image_files()
        results = []
        
        for image_path in image_files:
            # 检查是否已经分析过
            if self._is_image_analyzed(image_path):
                continue
            
            # 分析图片
            result = self.analyze_image(image_path)
            results.append(result)
            
            # 记录已分析的图片
            self._mark_image_analyzed(image_path)
        
        return results
    
    def _is_image_analyzed(self, image_path: str) -> bool:
        """检查图片是否已经分析过"""
        analyzed_file = os.path.join(self.watch_directory, ".analyzed_images.txt")
        
        if os.path.exists(analyzed_file):
            with open(analyzed_file, 'r', encoding='utf-8') as f:
                analyzed_images = f.read().splitlines()
                return image_path in analyzed_images
        
        return False
    
    def _mark_image_analyzed(self, image_path: str):
        """标记图片为已分析"""
        analyzed_file = os.path.join(self.watch_directory, ".analyzed_images.txt")
        
        try:
            with open(analyzed_file, 'a', encoding='utf-8') as f:
                f.write(image_path + '\n')
        except Exception as e:
            print(f"❌ 标记图片分析状态失败: {e}")
    
    def start_watching(self):
        """开始监控目录"""
        if not self.config.get("auto_watch", True):
            return
        
        self.is_running = True
        print(f"👀 开始监控目录: {self.watch_directory}")
        
        def watch_loop():
            while self.is_running:
                try:
                    results = self.analyze_new_images()
                    if results:
                        print(f"🔍 自动分析了 {len(results)} 张新图片")
                    
                    # 等待一段时间后再次检查
                    time.sleep(10)  # 每10秒检查一次
                    
                except Exception as e:
                    print(f"❌ 监控过程中出错: {e}")
                    time.sleep(30)  # 出错后等待30秒再继续
        
        # 在后台线程中运行监控
        watch_thread = threading.Thread(target=watch_loop, daemon=True)
        watch_thread.start()
    
    def stop_watching(self):
        """停止监控目录"""
        self.is_running = False
        print("🛑 停止监控目录")
    
    def get_analysis_history(self, limit: int = 10) -> List[Dict]:
        """获取分析历史"""
        return self.memory["analysis_history"][-limit:]
    
    def get_system_stats(self) -> Dict:
        """获取系统统计信息"""
        return {
            "total_analyzed": self.memory["total_analyzed"],
            "config": self.config,
            "user_preferences": self.memory["user_preferences"],
            "frequent_patterns": self.memory["frequent_patterns"],
            "is_running": self.is_running,
            "watch_directory": self.watch_directory
        }
    
    def reset_memory(self):
        """重置系统记忆"""
        self.memory = self._get_default_memory()
        self._save_memory()
        print("🔄 系统记忆已重置")
    
    def configure(self, **kwargs):
        """配置系统参数"""
        for key, value in kwargs.items():
            if key in self.config:
                self.config[key] = value
                print(f"✅ 已更新配置: {key} = {value}")
            else:
                print(f"⚠️ 未知配置项: {key}")
        
        self._save_config()


def main():
    """主函数 - 演示自动化图片分析系统的使用"""
    print("🚀 自动化图片分析系统")
    print("=" * 50)
    
    # 初始化系统
    analyzer = AutomatedImageAnalyzer()
    
    # 分析现有图片
    print("\n🔍 分析现有图片...")
    results = analyzer.analyze_new_images()
    
    if results:
        print(f"✅ 成功分析了 {len(results)} 张图片")
        for result in results:
            if result["success"]:
                print(f"   📸 {os.path.basename(result['image_path'])} - {result['analysis_type']}")
            else:
                print(f"   ❌ {os.path.basename(result['image_path'])} - {result.get('error', '未知错误')}")
    else:
        print("📝 没有找到新的图片需要分析")
    
    # 显示系统统计
    stats = analyzer.get_system_stats()
    print(f"\n📊 系统统计:")
    print(f"   总分析次数: {stats['total_analyzed']}")
    print(f"   首选模型: {stats['user_preferences']['preferred_model']}")
    print(f"   监控目录: {stats['watch_directory']}")
    print(f"   自动分析: {stats['config']['auto_analyze']}")
    print(f"   自动监控: {stats['config']['auto_watch']}")
    
    # 启动监控（可选）
    if stats['config']['auto_watch']:
        print("\n👀 启动自动监控...")
        analyzer.start_watching()
        print("💡 系统将自动监控新上传的图片并进行分析")
        print("   按 Ctrl+C 停止监控")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            analyzer.stop_watching()
            print("\n🛑 监控已停止")


if __name__ == "__main__":
    main()