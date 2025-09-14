#!/usr/bin/env python3
"""
全局记忆和上下文管理器
配置图片分析功能作为后续全局记忆
"""

import os
import json
import pickle
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from pathlib import Path

class GlobalMemoryManager:
    """全局记忆管理器"""
    
    def __init__(self, memory_dir: str = ".memory"):
        """
        初始化全局记忆管理器
        
        Args:
            memory_dir: 记忆存储目录
        """
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(exist_ok=True)
        
        # 记忆文件
        self.config_file = self.memory_dir / "config.json"
        self.context_file = self.memory_dir / "context.pkl"
        self.history_file = self.memory_dir / "history.json"
        self.preferences_file = self.memory_dir / "preferences.json"
        
        # 初始化记忆数据
        self.config = self._load_config()
        self.context = self._load_context()
        self.history = self._load_history()
        self.preferences = self._load_preferences()
        
        # 图片分析相关的记忆
        self.image_analysis_memory = {
            "enabled": True,
            "last_analysis_time": None,
            "analysis_count": 0,
            "successful_analyses": 0,
            "failed_analyses": 0,
            "favorite_model": "Qwen/Qwen2.5-VL-72B-Instruct",
            "analysis_types_used": [],
            "recent_results": [],
            "learned_patterns": {},
            "user_feedback": {}
        }
        
        print("🧠 全局记忆管理器初始化完成")
    
    def _load_config(self) -> Dict:
        """加载配置"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"❌ 加载配置失败: {e}")
        
        return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """获取默认配置"""
        return {
            "version": "1.0.0",
            "created_time": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "image_analysis": {
                "auto_analyze": True,
                "auto_monitor": True,
                "default_model": "Qwen/Qwen2.5-VL-72B-Instruct",
                "watch_directories": ["pic", "uploads", "images"],
                "max_history_size": 1000,
                "save_results": True
            },
            "memory_settings": {
                "max_memory_size": 10000,  # KB
                "auto_cleanup": True,
                "cleanup_threshold": 0.8,  # 80%时触发清理
                "backup_enabled": True,
                "backup_interval": 86400  # 24小时
            }
        }
    
    def _load_context(self) -> Dict:
        """加载上下文"""
        if self.context_file.exists():
            try:
                with open(self.context_file, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                print(f"❌ 加载上下文失败: {e}")
        
        return {
            "current_session": {
                "start_time": datetime.now().isoformat(),
                "session_id": self._generate_session_id(),
                "commands_executed": [],
                "analysis_results": []
            },
            "persistent_context": {
                "user_preferences": {},
                "system_knowledge": {},
                "learned_behaviors": {}
            }
        }
    
    def _load_history(self) -> List[Dict]:
        """加载历史记录"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"❌ 加载历史记录失败: {e}")
        
        return []
    
    def _load_preferences(self) -> Dict:
        """加载用户偏好"""
        if self.preferences_file.exists():
            try:
                with open(self.preferences_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"❌ 加载用户偏好失败: {e}")
        
        return {
            "language": "zh-CN",
            "output_format": "text",
            "verbosity": "normal",
            "auto_save": True,
            "analysis_preferences": {
                "preferred_model": "Qwen/Qwen2.5-VL-72B-Instruct",
                "default_analysis_type": "auto",
                "enable_auto_monitor": True,
                "save_results_to_file": True
            }
        }
    
    def _generate_session_id(self) -> str:
        """生成会话ID"""
        import uuid
        return str(uuid.uuid4())
    
    def save_config(self):
        """保存配置"""
        try:
            self.config["last_updated"] = datetime.now().isoformat()
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ 保存配置失败: {e}")
    
    def save_context(self):
        """保存上下文"""
        try:
            with open(self.context_file, 'wb') as f:
                pickle.dump(self.context, f)
        except Exception as e:
            print(f"❌ 保存上下文失败: {e}")
    
    def save_history(self):
        """保存历史记录"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ 保存历史记录失败: {e}")
    
    def save_preferences(self):
        """保存用户偏好"""
        try:
            with open(self.preferences_file, 'w', encoding='utf-8') as f:
                json.dump(self.preferences, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ 保存用户偏好失败: {e}")
    
    def save_all(self):
        """保存所有记忆数据"""
        self.save_config()
        self.save_context()
        self.save_history()
        self.save_preferences()
        print("💾 所有记忆数据已保存")
    
    def add_analysis_result(self, result: Dict):
        """添加图片分析结果到记忆"""
        timestamp = datetime.now().isoformat()
        
        # 更新图片分析记忆
        self.image_analysis_memory["last_analysis_time"] = timestamp
        self.image_analysis_memory["analysis_count"] += 1
        
        if result.get("success", False):
            self.image_analysis_memory["successful_analyses"] += 1
        else:
            self.image_analysis_memory["failed_analyses"] += 1
        
        # 记录分析类型
        analysis_type = result.get("analysis_type", "unknown")
        if analysis_type not in self.image_analysis_memory["analysis_types_used"]:
            self.image_analysis_memory["analysis_types_used"].append(analysis_type)
        
        # 添加到最近结果
        self.image_analysis_memory["recent_results"].append({
            "timestamp": timestamp,
            "image_path": result.get("image_path", ""),
            "analysis_type": analysis_type,
            "success": result.get("success", False),
            "model_used": result.get("model_used", "")
        })
        
        # 限制最近结果数量
        max_recent = 50
        if len(self.image_analysis_memory["recent_results"]) > max_recent:
            self.image_analysis_memory["recent_results"] = self.image_analysis_memory["recent_results"][-max_recent:]
        
        # 学习模式
        self._learn_from_analysis(result)
        
        # 添加到历史记录
        history_entry = {
            "timestamp": timestamp,
            "type": "image_analysis",
            "result": result,
            "session_id": self.context["current_session"]["session_id"]
        }
        
        self.history.append(history_entry)
        
        # 限制历史记录大小
        max_history = self.config["image_analysis"]["max_history_size"]
        if len(self.history) > max_history:
            self.history = self.history[-max_history:]
        
        # 添加到当前会话
        self.context["current_session"]["analysis_results"].append(history_entry)
        
        # 保存记忆
        self.save_all()
        
        print(f"🧠 分析结果已添加到全局记忆")
    
    def _learn_from_analysis(self, result: Dict):
        """从分析结果中学习"""
        if result.get("success", False):
            model_used = result.get("model_used", "")
            if model_used:
                # 学习用户偏好的模型
                if model_used not in self.image_analysis_memory["learned_patterns"]:
                    self.image_analysis_memory["learned_patterns"][model_used] = 0
                self.image_analysis_memory["learned_patterns"][model_used] += 1
                
                # 更新最喜欢的模型
                max_usage = max(self.image_analysis_memory["learned_patterns"].values())
                if self.image_analysis_memory["learned_patterns"][model_used] == max_usage:
                    self.image_analysis_memory["favorite_model"] = model_used
            
            # 学习分析类型偏好
            analysis_type = result.get("analysis_type", "")
            if analysis_type:
                type_key = f"type_{analysis_type}"
                if type_key not in self.image_analysis_memory["learned_patterns"]:
                    self.image_analysis_memory["learned_patterns"][type_key] = 0
                self.image_analysis_memory["learned_patterns"][type_key] += 1
    
    def get_analysis_insights(self) -> Dict:
        """获取分析洞察"""
        insights = {
            "total_analyses": self.image_analysis_memory["analysis_count"],
            "success_rate": 0,
            "favorite_model": self.image_analysis_memory["favorite_model"],
            "most_used_analysis_type": None,
            "recent_trends": {},
            "recommendations": []
        }
        
        if self.image_analysis_memory["analysis_count"] > 0:
            insights["success_rate"] = (
                self.image_analysis_memory["successful_analyses"] / 
                self.image_analysis_memory["analysis_count"]
            ) * 100
        
        # 找出最常用的分析类型
        type_counts = {}
        for key, count in self.image_analysis_memory["learned_patterns"].items():
            if key.startswith("type_"):
                analysis_type = key[5:]  # 去掉"type_"前缀
                type_counts[analysis_type] = count
        
        if type_counts:
            insights["most_used_analysis_type"] = max(type_counts, key=type_counts.get)
        
        # 生成建议
        if insights["success_rate"] < 80:
            insights["recommendations"].append("考虑检查API配置或网络连接")
        
        if self.image_analysis_memory["analysis_count"] > 10:
            insights["recommendations"].append("定期清理历史记录以保持系统性能")
        
        return insights
    
    def get_user_preferences(self) -> Dict:
        """获取用户偏好"""
        return {
            "general": self.preferences,
            "analysis": {
                "favorite_model": self.image_analysis_memory["favorite_model"],
                "auto_analyze": self.config["image_analysis"]["auto_analyze"],
                "auto_monitor": self.config["image_analysis"]["auto_monitor"],
                "watch_directories": self.config["image_analysis"]["watch_directories"]
            }
        }
    
    def update_user_preferences(self, new_preferences: Dict):
        """更新用户偏好"""
        # 更新一般偏好
        if "general" in new_preferences:
            self.preferences.update(new_preferences["general"])
        
        # 更新分析偏好
        if "analysis" in new_preferences:
            analysis_prefs = new_preferences["analysis"]
            
            # 更新配置
            if "auto_analyze" in analysis_prefs:
                self.config["image_analysis"]["auto_analyze"] = analysis_prefs["auto_analyze"]
            
            if "auto_monitor" in analysis_prefs:
                self.config["image_analysis"]["auto_monitor"] = analysis_prefs["auto_monitor"]
            
            if "watch_directories" in analysis_prefs:
                self.config["image_analysis"]["watch_directories"] = analysis_prefs["watch_directories"]
            
            if "favorite_model" in analysis_prefs:
                self.image_analysis_memory["favorite_model"] = analysis_prefs["favorite_model"]
        
        self.save_all()
        print("✅ 用户偏好已更新")
    
    def get_memory_summary(self) -> Dict:
        """获取记忆摘要"""
        return {
            "config": {
                "version": self.config["version"],
                "created_time": self.config["created_time"],
                "last_updated": self.config["last_updated"],
                "image_analysis_enabled": self.config["image_analysis"]["auto_analyze"]
            },
            "image_analysis_memory": {
                "total_analyses": self.image_analysis_memory["analysis_count"],
                "successful_analyses": self.image_analysis_memory["successful_analyses"],
                "failed_analyses": self.image_analysis_memory["failed_analyses"],
                "last_analysis_time": self.image_analysis_memory["last_analysis_time"],
                "favorite_model": self.image_analysis_memory["favorite_model"],
                "analysis_types_used": self.image_analysis_memory["analysis_types_used"]
            },
            "context": {
                "current_session_id": self.context["current_session"]["session_id"],
                "session_start_time": self.context["current_session"]["start_time"],
                "session_analyses": len(self.context["current_session"]["analysis_results"])
            },
            "history": {
                "total_entries": len(self.history),
                "analysis_entries": len([h for h in self.history if h["type"] == "image_analysis"])
            }
        }
    
    def cleanup_memory(self):
        """清理记忆数据"""
        print("🧹 清理记忆数据...")
        
        # 清理最近结果
        max_recent = 20
        if len(self.image_analysis_memory["recent_results"]) > max_recent:
            self.image_analysis_memory["recent_results"] = self.image_analysis_memory["recent_results"][-max_recent:]
        
        # 清理历史记录
        max_history = self.config["image_analysis"]["max_history_size"] // 2
        if len(self.history) > max_history:
            self.history = self.history[-max_history:]
        
        # 清理学习模式（保留最常用的）
        if len(self.image_analysis_memory["learned_patterns"]) > 10:
            # 按使用频率排序，保留前10个
            sorted_patterns = sorted(
                self.image_analysis_memory["learned_patterns"].items(),
                key=lambda x: x[1],
                reverse=True
            )
            self.image_analysis_memory["learned_patterns"] = dict(sorted_patterns[:10])
        
        self.save_all()
        print("✅ 记忆数据清理完成")
    
    def backup_memory(self):
        """备份记忆数据"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = self.memory_dir / f"backup_{timestamp}"
        backup_dir.mkdir(exist_ok=True)
        
        # 复制所有记忆文件
        import shutil
        
        files_to_backup = [
            self.config_file,
            self.context_file,
            self.history_file,
            self.preferences_file
        ]
        
        for file_path in files_to_backup:
            if file_path.exists():
                shutil.copy2(file_path, backup_dir)
        
        print(f"💾 记忆数据已备份到: {backup_dir}")
    
    def reset_memory(self):
        """重置记忆数据"""
        print("🔄 重置记忆数据...")
        
        # 保留配置文件，重置其他数据
        self.context = self._load_context()
        self.history = []
        self.image_analysis_memory = {
            "enabled": True,
            "last_analysis_time": None,
            "analysis_count": 0,
            "successful_analyses": 0,
            "failed_analyses": 0,
            "favorite_model": "Qwen/Qwen2.5-VL-72B-Instruct",
            "analysis_types_used": [],
            "recent_results": [],
            "learned_patterns": {},
            "user_feedback": {}
        }
        
        self.save_all()
        print("✅ 记忆数据已重置")


def main():
    """主函数 - 演示全局记忆管理器的使用"""
    print("🧠 全局记忆管理器演示")
    print("=" * 50)
    
    # 创建记忆管理器
    memory_manager = GlobalMemoryManager()
    
    # 显示记忆摘要
    print("\n📊 记忆摘要:")
    summary = memory_manager.get_memory_summary()
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    
    # 显示用户偏好
    print("\n⚙️  用户偏好:")
    preferences = memory_manager.get_user_preferences()
    print(json.dumps(preferences, ensure_ascii=False, indent=2))
    
    # 显示分析洞察
    print("\n🔍 分析洞察:")
    insights = memory_manager.get_analysis_insights()
    print(json.dumps(insights, ensure_ascii=False, indent=2))
    
    print("\n💡 全局记忆管理器已准备就绪！")
    print("   - 图片分析功能已配置为全局记忆")
    print("   - 系统将自动学习和适应用户偏好")
    print("   - 所有分析结果都将被记录和学习")


if __name__ == "__main__":
    main()