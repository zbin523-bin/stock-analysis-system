#!/usr/bin/env python3
"""
图片分析系统主程序
集成所有功能，提供完整的自动化图片分析解决方案
"""

import os
import sys
import json
import argparse
from datetime import datetime
from typing import Dict, List, Optional

# 导入所有模块
from automated_image_analyzer import AutomatedImageAnalyzer
from image_upload_monitor import ImageUploadMonitor
from image_analysis_api import ImageAnalysisAPI
from global_memory_manager import GlobalMemoryManager

class ImageAnalysisSystem:
    """图片分析系统主类"""
    
    def __init__(self, api_key: str = None):
        """
        初始化图片分析系统
        
        Args:
            api_key: 硅基流动API密钥
        """
        self.api_key = api_key
        self.version = "2.0.0"
        
        # 初始化各个组件
        self.memory_manager = GlobalMemoryManager()
        self.analyzer = AutomatedImageAnalyzer(api_key)
        self.monitor = ImageUploadMonitor()
        self.api = ImageAnalysisAPI(api_key)
        
        # 系统状态
        self.is_initialized = True
        self.start_time = datetime.now()
        
        print(f"🚀 图片分析系统 v{self.version} 初始化完成")
        print(f"🧠 全局记忆管理器已启用")
        print(f"🔍 分析器已就绪")
        print(f"👀 监控器已就绪")
        print(f"🌐 API接口已就绪")
    
    def analyze_image(self, image_path: str, analysis_type: str = "auto") -> Dict:
        """
        分析单张图片
        
        Args:
            image_path: 图片文件路径
            analysis_type: 分析类型
        
        Returns:
            分析结果
        """
        print(f"🔍 分析图片: {image_path}")
        
        # 执行分析
        result = self.api.analyze_image(image_path, analysis_type)
        
        # 添加到全局记忆
        self.memory_manager.add_analysis_result(result)
        
        return result
    
    def analyze_directory(self, directory: str, analysis_type: str = "auto") -> Dict:
        """
        分析目录中的所有图片
        
        Args:
            directory: 目录路径
            analysis_type: 分析类型
        
        Returns:
            分析结果
        """
        print(f"🔍 分析目录: {directory}")
        
        # 执行分析
        result = self.api.analyze_directory(directory, analysis_type)
        
        # 将每个分析结果添加到全局记忆
        if result.get("success") and "results" in result:
            for analysis_result in result["results"]:
                self.memory_manager.add_analysis_result(analysis_result)
        
        return result
    
    def start_monitoring(self, directories: List[str] = None) -> Dict:
        """
        启动自动监控
        
        Args:
            directories: 监控目录列表
        
        Returns:
            启动结果
        """
        print("👀 启动自动监控...")
        
        # 启动监控
        result = self.api.start_auto_monitor(directories)
        
        if result.get("success"):
            print("✅ 自动监控已启动")
            print(f"📁 监控目录: {', '.join(directories or self.monitor.watch_directories)}")
            print("💡 系统将自动检测新上传的图片并进行分析")
        else:
            print(f"❌ 启动监控失败: {result.get('error')}")
        
        return result
    
    def stop_monitoring(self) -> Dict:
        """
        停止自动监控
        
        Returns:
            停止结果
        """
        print("🛑 停止自动监控...")
        
        # 停止监控
        result = self.api.stop_auto_monitor()
        
        if result.get("success"):
            print("✅ 自动监控已停止")
        else:
            print(f"❌ 停止监控失败: {result.get('error')}")
        
        return result
    
    def get_system_status(self) -> Dict:
        """
        获取系统状态
        
        Returns:
            系统状态
        """
        # 获取各个组件的状态
        api_status = self.api.get_system_status()
        memory_summary = self.memory_manager.get_memory_summary()
        insights = self.memory_manager.get_analysis_insights()
        
        return {
            "system": {
                "version": self.version,
                "start_time": self.start_time.isoformat(),
                "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
                "is_initialized": self.is_initialized
            },
            "components": {
                "api": api_status,
                "memory": memory_summary,
                "insights": insights
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def get_user_guide(self) -> str:
        """
        获取用户使用指南
        
        Returns:
            使用指南字符串
        """
        guide = """
🎯 图片分析系统使用指南
═════════════════════════════════════════

📸 基本功能：
• 分析单张图片：analyze_image(图片路径, 分析类型)
• 分析整个目录：analyze_directory(目录路径, 分析类型)
• 启动自动监控：start_monitoring([目录列表])
• 停止自动监控：stop_monitoring()

🔍 分析类型：
• auto - 自动判断（默认）
• wechat - 微信图片分析
• table - 表格数据提取
• weather - 天气信息分析
• general - 通用图片分析

📁 支持的图片格式：
• .jpg, .jpeg
• .png
• .gif
• .bmp
• .tiff
• .webp

🧠 智能功能：
• 自动学习和适应用户偏好
• 持久化记忆和上下文管理
• 自动检测新上传的图片
• 智能分析类型判断

💡 使用建议：
• 将图片放入 pic/ 目录进行自动分析
• 使用命令行工具进行批量分析
• 查看系统统计了解使用情况
• 定期清理记忆数据保持性能

🛠️ 系统管理：
• 查看系统状态：get_system_status()
• 获取用户指南：get_user_guide()
• 查看分析洞察：系统状态中的insights部分
"""
        return guide
    
    def interactive_mode(self):
        """交互式模式"""
        print("🎮 进入交互式模式")
        print("输入 'help' 查看帮助，'exit' 退出")
        
        while True:
            try:
                user_input = input("\n图片分析系统> ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['exit', 'quit', '退出']:
                    print("👋 再见！")
                    break
                
                elif user_input.lower() in ['help', '帮助']:
                    print(self.get_user_guide())
                
                elif user_input.lower() in ['status', '状态']:
                    status = self.get_system_status()
                    print("📊 系统状态:")
                    print(json.dumps(status, ensure_ascii=False, indent=2))
                
                elif user_input.lower().startswith('analyze '):
                    # 分析图片
                    image_path = user_input[8:].strip()
                    if os.path.exists(image_path):
                        result = self.analyze_image(image_path)
                        print(f"✅ 分析完成: {os.path.basename(image_path)}")
                        if result.get('success'):
                            print(f"   类型: {result.get('analysis_type', 'unknown')}")
                            print(f"   模型: {result.get('model_used', 'unknown')}")
                        else:
                            print(f"   ❌ {result.get('error', '未知错误')}")
                    else:
                        print(f"❌ 文件不存在: {image_path}")
                
                elif user_input.lower().startswith('analyze-dir '):
                    # 分析目录
                    directory = user_input[13:].strip()
                    if os.path.exists(directory):
                        result = self.analyze_directory(directory)
                        if result.get('success'):
                            print(f"✅ 目录分析完成: {directory}")
                            print(f"   分析数量: {result.get('analyzed_count', 0)}")
                            print(f"   总文件数: {result.get('total_files', 0)}")
                        else:
                            print(f"   ❌ {result.get('error', '未知错误')}")
                    else:
                        print(f"❌ 目录不存在: {directory}")
                
                elif user_input.lower() == 'monitor':
                    # 启动监控
                    result = self.start_monitoring()
                    if result.get('success'):
                        print("✅ 监控已启动，按 Ctrl+C 停止")
                        try:
                            while True:
                                import time
                                time.sleep(1)
                        except KeyboardInterrupt:
                            self.stop_monitoring()
                    else:
                        print(f"❌ 启动监控失败: {result.get('error')}")
                
                elif user_input.lower() in ['memory', '记忆']:
                    # 显示记忆信息
                    summary = self.memory_manager.get_memory_summary()
                    insights = self.memory_manager.get_analysis_insights()
                    
                    print("🧠 记忆摘要:")
                    print(f"   总分析次数: {summary['image_analysis_memory']['total_analyses']}")
                    print(f"   成功分析: {summary['image_analysis_memory']['successful_analyses']}")
                    print(f"   失败分析: {summary['image_analysis_memory']['failed_analyses']}")
                    print(f"   首选模型: {summary['image_analysis_memory']['favorite_model']}")
                    
                    print("\n📊 分析洞察:")
                    print(f"   成功率: {insights['success_rate']:.1f}%")
                    print(f"   最常用类型: {insights.get('most_used_analysis_type', '无')}")
                    if insights['recommendations']:
                        print(f"   建议: {', '.join(insights['recommendations'])}")
                
                elif user_input.lower() in ['clear', '清理']:
                    # 清理记忆
                    self.memory_manager.cleanup_memory()
                    print("✅ 记忆数据已清理")
                
                elif user_input.lower() in ['backup', '备份']:
                    # 备份记忆
                    self.memory_manager.backup_memory()
                    print("✅ 记忆数据已备份")
                
                else:
                    print("❌ 未知命令，输入 'help' 查看帮助")
            
            except KeyboardInterrupt:
                print("\n👋 再见！")
                break
            except Exception as e:
                print(f"❌ 执行命令时出错: {e}")


def create_cli():
    """创建命令行接口"""
    parser = argparse.ArgumentParser(
        description='图片分析系统 - 基于硅基流动AI的智能图片分析工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  %(prog)s analyze image.jpg                    # 分析单张图片
  %(prog)s analyze-dir ./images                 # 分析目录中的所有图片
  %(prog)s monitor --dirs pic uploads           # 启动自动监控
  %(prog)s status                               # 查看系统状态
  %(prog)s interactive                          # 进入交互式模式
        """
    )
    
    # 基本参数
    parser.add_argument('--api-key', help='硅基流动API密钥')
    parser.add_argument('--version', action='version', version='%(prog)s 2.0.0')
    
    # 子命令
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 分析命令
    analyze_parser = subparsers.add_parser('analyze', help='分析单张图片')
    analyze_parser.add_argument('image_path', help='图片文件路径')
    analyze_parser.add_argument('--type', choices=['auto', 'wechat', 'table', 'weather', 'general'],
                               default='auto', help='分析类型')
    analyze_parser.add_argument('--output', '-o', help='输出文件路径')
    
    # 分析目录命令
    dir_parser = subparsers.add_parser('analyze-dir', help='分析目录中的所有图片')
    dir_parser.add_argument('directory', help='目录路径')
    dir_parser.add_argument('--type', choices=['auto', 'wechat', 'table', 'weather', 'general'],
                            default='auto', help='分析类型')
    dir_parser.add_argument('--output', '-o', help='输出文件路径')
    
    # 监控命令
    monitor_parser = subparsers.add_parser('monitor', help='启动自动监控')
    monitor_parser.add_argument('--dirs', nargs='+', help='监控目录列表')
    
    # 停止监控命令
    stop_parser = subparsers.add_parser('stop-monitor', help='停止自动监控')
    
    # 状态命令
    status_parser = subparsers.add_parser('status', help='查看系统状态')
    
    # 交互式模式
    interactive_parser = subparsers.add_parser('interactive', help='进入交互式模式')
    
    # 用户指南
    guide_parser = subparsers.add_parser('guide', help='显示用户指南')
    
    return parser


def main():
    """主函数"""
    parser = create_cli()
    args = parser.parse_args()
    
    # 创建系统实例
    system = ImageAnalysisSystem(args.api_key)
    
    # 执行命令
    if args.command == 'analyze':
        result = system.analyze_image(args.image_path, args.type)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"✅ 结果已保存到: {args.output}")
        else:
            print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif args.command == 'analyze-dir':
        result = system.analyze_directory(args.directory, args.type)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"✅ 结果已保存到: {args.output}")
        else:
            print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif args.command == 'monitor':
        result = system.start_monitoring(args.dirs)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        if result.get('success'):
            print("💡 按 Ctrl+C 停止监控")
            try:
                import time
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                system.stop_monitoring()
    
    elif args.command == 'stop-monitor':
        result = system.stop_monitoring()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif args.command == 'status':
        status = system.get_system_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))
    
    elif args.command == 'interactive':
        system.interactive_mode()
    
    elif args.command == 'guide':
        print(system.get_user_guide())
    
    else:
        parser.print_help()
        
        # 显示快速开始指南
        print("\n🚀 快速开始:")
        print("1. 分析单张图片: python image_analysis_system.py analyze image.jpg")
        print("2. 分析目录: python image_analysis_system.py analyze-dir ./images")
        print("3. 启动监控: python image_analysis_system.py monitor")
        print("4. 交互模式: python image_analysis_system.py interactive")
        print("5. 查看帮助: python image_analysis_system.py guide")


if __name__ == "__main__":
    main()