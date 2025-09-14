#!/usr/bin/env python3
"""
图片分析API接口
提供用户友好的按需分析功能
"""

import os
import json
import argparse
from datetime import datetime
from typing import Dict, List, Optional, Any
from automated_image_analyzer import AutomatedImageAnalyzer
from image_upload_monitor import ImageUploadMonitor

class ImageAnalysisAPI:
    """图片分析API接口"""
    
    def __init__(self, api_key: str = None):
        """
        初始化图片分析API
        
        Args:
            api_key: 硅基流动API密钥
        """
        self.analyzer = AutomatedImageAnalyzer(api_key)
        self.monitor = ImageUploadMonitor()
        self.api_version = "1.0.0"
        
        print(f"🚀 图片分析API v{self.api_version} 初始化完成")
    
    def analyze_image(self, image_path: str, analysis_type: str = None, **kwargs) -> Dict:
        """
        分析单张图片
        
        Args:
            image_path: 图片文件路径
            analysis_type: 分析类型 (auto, wechat, table, weather, general)
            **kwargs: 其他参数
        
        Returns:
            分析结果字典
        """
        print(f"🔍 开始分析图片: {image_path}")
        
        if not os.path.exists(image_path):
            return {
                "success": False,
                "error": "图片文件不存在",
                "code": "FILE_NOT_FOUND",
                "timestamp": datetime.now().isoformat()
            }
        
        # 分析图片
        result = self.analyzer.analyze_image(image_path, analysis_type)
        
        # 添加API元数据
        result["api_version"] = self.api_version
        result["request_time"] = datetime.now().isoformat()
        
        return result
    
    def analyze_directory(self, directory: str, analysis_type: str = None, **kwargs) -> Dict:
        """
        分析目录中的所有图片
        
        Args:
            directory: 目录路径
            analysis_type: 分析类型
            **kwargs: 其他参数
        
        Returns:
            分析结果字典
        """
        print(f"🔍 分析目录中的图片: {directory}")
        
        if not os.path.exists(directory):
            return {
                "success": False,
                "error": "目录不存在",
                "code": "DIRECTORY_NOT_FOUND",
                "timestamp": datetime.now().isoformat()
            }
        
        # 获取目录中的所有图片
        image_files = []
        supported_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']
        
        for ext in supported_extensions:
            import glob
            pattern = os.path.join(directory, f"*{ext}")
            image_files.extend(glob.glob(pattern))
            pattern = os.path.join(directory, f"*{ext.upper()}")
            image_files.extend(glob.glob(pattern))
        
        # 过滤掉系统文件
        image_files = [f for f in image_files if not os.path.basename(f).startswith('._')]
        
        if not image_files:
            return {
                "success": True,
                "message": "目录中没有找到图片文件",
                "analyzed_count": 0,
                "total_files": 0,
                "results": [],
                "timestamp": datetime.now().isoformat()
            }
        
        # 分析每张图片
        results = []
        success_count = 0
        
        for image_path in image_files:
            try:
                result = self.analyzer.analyze_image(image_path, analysis_type)
                results.append(result)
                
                if result.get("success", False):
                    success_count += 1
                
                print(f"   {'✅' if result.get('success') else '❌'} {os.path.basename(image_path)}")
                
            except Exception as e:
                error_result = {
                    "success": False,
                    "error": str(e),
                    "image_path": image_path,
                    "timestamp": datetime.now().isoformat()
                }
                results.append(error_result)
                print(f"   ❌ {os.path.basename(image_path)} - {e}")
        
        return {
            "success": True,
            "message": f"目录分析完成",
            "analyzed_count": success_count,
            "total_files": len(image_files),
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
    
    def start_auto_monitor(self, directories: List[str] = None, **kwargs) -> Dict:
        """
        启动自动监控
        
        Args:
            directories: 要监控的目录列表
            **kwargs: 其他参数
        
        Returns:
            启动结果字典
        """
        print("👀 启动自动图片监控...")
        
        if directories:
            for directory in directories:
                self.monitor.add_watch_directory(directory)
        
        try:
            self.monitor.start_monitoring()
            
            return {
                "success": True,
                "message": "自动监控已启动",
                "watch_directories": self.monitor.watch_directories,
                "check_interval": self.monitor.check_interval,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"启动监控失败: {e}",
                "code": "MONITOR_START_FAILED",
                "timestamp": datetime.now().isoformat()
            }
    
    def stop_auto_monitor(self, **kwargs) -> Dict:
        """
        停止自动监控
        
        Returns:
            停止结果字典
        """
        print("🛑 停止自动图片监控...")
        
        try:
            self.monitor.stop_monitoring()
            
            return {
                "success": True,
                "message": "自动监控已停止",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"停止监控失败: {e}",
                "code": "MONITOR_STOP_FAILED",
                "timestamp": datetime.now().isoformat()
            }
    
    def get_system_status(self, **kwargs) -> Dict:
        """
        获取系统状态
        
        Returns:
            系统状态字典
        """
        analyzer_stats = self.analyzer.get_system_stats()
        monitor_stats = self.monitor.get_monitor_stats()
        
        return {
            "success": True,
            "api_version": self.api_version,
            "analyzer": analyzer_stats,
            "monitor": monitor_stats,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_analysis_history(self, limit: int = 10, **kwargs) -> Dict:
        """
        获取分析历史
        
        Args:
            limit: 返回记录数量限制
        
        Returns:
            分析历史字典
        """
        history = self.analyzer.get_analysis_history(limit)
        
        return {
            "success": True,
            "history": history,
            "total_count": len(history),
            "limit": limit,
            "timestamp": datetime.now().isoformat()
        }
    
    def scan_for_new_images(self, directories: List[str] = None, **kwargs) -> Dict:
        """
        扫描新图片
        
        Args:
            directories: 要扫描的目录列表
        
        Returns:
            扫描结果字典
        """
        print("🔍 扫描新图片...")
        
        if directories:
            original_dirs = self.monitor.watch_directories.copy()
            self.monitor.watch_directories = directories
        
        try:
            results = self.monitor.scan_once()
            
            return {
                "success": True,
                "message": f"扫描完成，发现 {len(results)} 张图片",
                "results": results,
                "scanned_directories": directories or self.monitor.watch_directories,
                "timestamp": datetime.now().isoformat()
            }
            
        finally:
            if directories:
                self.monitor.watch_directories = original_dirs
    
    def configure_system(self, **kwargs) -> Dict:
        """
        配置系统参数
        
        Args:
            **kwargs: 配置参数
        
        Returns:
            配置结果字典
        """
        print("⚙️  配置系统参数...")
        
        try:
            # 配置分析器
            analyzer_configs = {
                'auto_analyze', 'auto_watch', 'default_model', 'analysis_types',
                'output_formats', 'save_history', 'max_history_size'
            }
            
            analyzer_kwargs = {k: v for k, v in kwargs.items() if k in analyzer_configs}
            if analyzer_kwargs:
                self.analyzer.configure(**analyzer_kwargs)
            
            # 配置监控器
            monitor_configs = {
                'check_interval', 'watch_directories'
            }
            
            monitor_kwargs = {k: v for k, v in kwargs.items() if k in monitor_configs}
            if 'check_interval' in monitor_kwargs:
                self.monitor.check_interval = monitor_kwargs['check_interval']
            
            if 'watch_directories' in monitor_kwargs:
                self.monitor.watch_directories = monitor_kwargs['watch_directories']
            
            return {
                "success": True,
                "message": "系统配置已更新",
                "updated_configs": list(kwargs.keys()),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"配置失败: {e}",
                "code": "CONFIG_FAILED",
                "timestamp": datetime.now().isoformat()
            }
    
    def export_analysis_results(self, output_file: str = None, **kwargs) -> Dict:
        """
        导出分析结果
        
        Args:
            output_file: 输出文件路径
        
        Returns:
            导出结果字典
        """
        print("💾 导出分析结果...")
        
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"analysis_export_{timestamp}.json"
        
        try:
            # 获取系统状态和历史记录
            status = self.get_system_status()
            history = self.get_analysis_history(limit=100)
            
            export_data = {
                "export_info": {
                    "timestamp": datetime.now().isoformat(),
                    "api_version": self.api_version,
                    "export_version": "1.0"
                },
                "system_status": status,
                "analysis_history": history,
                "configuration": {
                    "analyzer_config": self.analyzer.config,
                    "monitor_config": {
                        "watch_directories": self.monitor.watch_directories,
                        "check_interval": self.monitor.check_interval
                    }
                }
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            return {
                "success": True,
                "message": f"分析结果已导出到 {output_file}",
                "output_file": output_file,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"导出失败: {e}",
                "code": "EXPORT_FAILED",
                "timestamp": datetime.now().isoformat()
            }


def create_command_line_interface():
    """创建命令行接口"""
    parser = argparse.ArgumentParser(description='图片分析API命令行工具')
    
    # 基本参数
    parser.add_argument('--api-key', help='硅基流动API密钥')
    parser.add_argument('--output', '-o', help='输出文件路径')
    parser.add_argument('--format', choices=['json', 'text'], default='text', help='输出格式')
    
    # 子命令
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 分析单张图片
    analyze_parser = subparsers.add_parser('analyze', help='分析单张图片')
    analyze_parser.add_argument('image_path', help='图片文件路径')
    analyze_parser.add_argument('--type', choices=['auto', 'wechat', 'table', 'weather', 'general'], 
                               default='auto', help='分析类型')
    
    # 分析目录
    dir_parser = subparsers.add_parser('analyze-dir', help='分析目录中的所有图片')
    dir_parser.add_argument('directory', help='目录路径')
    dir_parser.add_argument('--type', choices=['auto', 'wechat', 'table', 'weather', 'general'], 
                            default='auto', help='分析类型')
    
    # 启动监控
    monitor_parser = subparsers.add_parser('monitor', help='启动自动监控')
    monitor_parser.add_argument('--dirs', nargs='+', help='监控目录列表')
    
    # 停止监控
    stop_parser = subparsers.add_parser('stop-monitor', help='停止自动监控')
    
    # 扫描新图片
    scan_parser = subparsers.add_parser('scan', help='扫描新图片')
    scan_parser.add_argument('--dirs', nargs='+', help='扫描目录列表')
    
    # 系统状态
    status_parser = subparsers.add_parser('status', help='获取系统状态')
    
    # 分析历史
    history_parser = subparsers.add_parser('history', help='获取分析历史')
    history_parser.add_argument('--limit', type=int, default=10, help='返回记录数量限制')
    
    # 导出结果
    export_parser = subparsers.add_parser('export', help='导出分析结果')
    export_parser.add_argument('--output', help='输出文件路径')
    
    return parser


def main():
    """主函数"""
    parser = create_command_line_interface()
    args = parser.parse_args()
    
    # 创建API实例
    api = ImageAnalysisAPI(args.api_key)
    
    # 执行命令
    result = None
    
    if args.command == 'analyze':
        result = api.analyze_image(args.image_path, args.type)
    
    elif args.command == 'analyze-dir':
        result = api.analyze_directory(args.directory, args.type)
    
    elif args.command == 'monitor':
        result = api.start_auto_monitor(args.dirs)
    
    elif args.command == 'stop-monitor':
        result = api.stop_auto_monitor()
    
    elif args.command == 'scan':
        result = api.scan_for_new_images(args.dirs)
    
    elif args.command == 'status':
        result = api.get_system_status()
    
    elif args.command == 'history':
        result = api.get_analysis_history(args.limit)
    
    elif args.command == 'export':
        result = api.export_analysis_results(args.output)
    
    else:
        parser.print_help()
        return
    
    # 输出结果
    if args.format == 'json':
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        # 格式化输出
        if result.get('success'):
            print("✅ 操作成功")
            if 'message' in result:
                print(f"📝 {result['message']}")
        else:
            print("❌ 操作失败")
            if 'error' in result:
                print(f"❌ {result['error']}")
        
        # 显示详细信息
        if 'analyzed_count' in result:
            print(f"📊 分析数量: {result['analyzed_count']}")
        
        if 'total_files' in result:
            print(f"📁 总文件数: {result['total_files']}")
        
        if 'watch_directories' in result:
            print(f"👀 监控目录: {', '.join(result['watch_directories'])}")


if __name__ == "__main__":
    main()