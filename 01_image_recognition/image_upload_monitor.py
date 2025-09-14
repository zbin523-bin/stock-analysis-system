#!/usr/bin/env python3
"""
图片上传监控器
自动检测新上传的图片并触发分析
"""

import os
import time
import json
import hashlib
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Callable
from automated_image_analyzer import AutomatedImageAnalyzer

class ImageUploadMonitor:
    """图片上传监控器"""
    
    def __init__(self, watch_directories: List[str] = None, callback: Callable = None):
        """
        初始化图片上传监控器
        
        Args:
            watch_directories: 要监控的目录列表
            callback: 发现新图片时的回调函数
        """
        self.watch_directories = watch_directories or ["pic", "uploads", "images"]
        self.callback = callback
        self.is_running = False
        self.check_interval = 5  # 检查间隔（秒）
        self.file_hashes = {}  # 存储文件哈希以避免重复分析
        self.state_file = "upload_monitor_state.json"
        
        # 支持的图片格式
        self.supported_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']
        
        # 初始化分析器
        self.analyzer = AutomatedImageAnalyzer()
        
        # 确保监控目录存在
        for directory in self.watch_directories:
            os.makedirs(directory, exist_ok=True)
        
        # 加载状态
        self._load_state()
    
    def _load_state(self):
        """加载监控状态"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                    self.file_hashes = state.get('file_hashes', {})
                print("✅ 监控状态已加载")
            except Exception as e:
                print(f"❌ 加载监控状态失败: {e}")
                self.file_hashes = {}
    
    def _save_state(self):
        """保存监控状态"""
        try:
            state = {
                'file_hashes': self.file_hashes,
                'last_update': datetime.now().isoformat()
            }
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ 保存监控状态失败: {e}")
    
    def _get_file_hash(self, filepath: str) -> str:
        """计算文件的哈希值"""
        try:
            with open(filepath, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return ""
    
    def _is_image_file(self, filepath: str) -> bool:
        """检查是否为图片文件"""
        if not os.path.isfile(filepath):
            return False
        
        # 检查文件扩展名
        ext = os.path.splitext(filepath)[1].lower()
        return ext in self.supported_extensions
    
    def _get_new_images(self, directory: str) -> List[str]:
        """获取目录中的新图片文件"""
        new_images = []
        
        if not os.path.exists(directory):
            return new_images
        
        try:
            for root, dirs, files in os.walk(directory):
                # 跳过隐藏目录
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                for file in files:
                    # 跳过隐藏文件和临时文件
                    if file.startswith('.') or file.startswith('._') or file.startswith('~'):
                        continue
                    
                    filepath = os.path.join(root, file)
                    
                    if self._is_image_file(filepath):
                        file_hash = self._get_file_hash(filepath)
                        
                        # 如果文件哈希不存在，则是新文件
                        if file_hash and file_hash not in self.file_hashes:
                            new_images.append(filepath)
                            self.file_hashes[file_hash] = {
                                'filepath': filepath,
                                'first_seen': datetime.now().isoformat(),
                                'analyzed': False
                            }
        
        except Exception as e:
            print(f"❌ 扫描目录时出错 {directory}: {e}")
        
        return new_images
    
    def _handle_new_image(self, image_path: str):
        """处理新发现的图片"""
        print(f"🖼️  发现新图片: {os.path.basename(image_path)}")
        
        # 等待文件完全写入（避免文件未完成传输就进行分析）
        time.sleep(2)
        
        # 使用分析器进行分析
        try:
            result = self.analyzer.analyze_image(image_path)
            
            if result['success']:
                print(f"✅ 图片分析成功: {os.path.basename(image_path)}")
                
                # 标记为已分析
                file_hash = self._get_file_hash(image_path)
                if file_hash in self.file_hashes:
                    self.file_hashes[file_hash]['analyzed'] = True
                    self.file_hashes[file_hash]['analyzed_time'] = datetime.now().isoformat()
                
                # 调用回调函数
                if self.callback:
                    self.callback(image_path, result)
            
            else:
                print(f"❌ 图片分析失败: {os.path.basename(image_path)} - {result.get('error', '未知错误')}")
        
        except Exception as e:
            print(f"❌ 处理图片时出错 {image_path}: {e}")
    
    def start_monitoring(self):
        """开始监控"""
        if self.is_running:
            print("⚠️ 监控已在运行中")
            return
        
        self.is_running = True
        print(f"👀 开始监控图片上传...")
        print(f"📁 监控目录: {', '.join(self.watch_directories)}")
        print(f"⏱️  检查间隔: {self.check_interval} 秒")
        
        def monitor_loop():
            while self.is_running:
                try:
                    new_images = []
                    
                    # 扫描所有监控目录
                    for directory in self.watch_directories:
                        images = self._get_new_images(directory)
                        new_images.extend(images)
                    
                    if new_images:
                        print(f"🔍 发现 {len(new_images)} 张新图片")
                        
                        for image_path in new_images:
                            self._handle_new_image(image_path)
                        
                        # 保存状态
                        self._save_state()
                    
                    # 等待下一次检查
                    time.sleep(self.check_interval)
                
                except Exception as e:
                    print(f"❌ 监控过程中出错: {e}")
                    time.sleep(10)  # 出错后等待10秒再继续
        
        # 在后台线程中运行监控
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
    
    def stop_monitoring(self):
        """停止监控"""
        self.is_running = False
        print("🛑 停止图片上传监控")
        
        # 保存最终状态
        self._save_state()
    
    def scan_once(self) -> List[Dict]:
        """手动扫描一次所有目录"""
        print("🔍 手动扫描图片...")
        
        all_new_images = []
        results = []
        
        for directory in self.watch_directories:
            images = self._get_new_images(directory)
            all_new_images.extend(images)
        
        if all_new_images:
            print(f"🔍 发现 {len(all_new_images)} 张新图片")
            
            for image_path in all_new_images:
                try:
                    result = self.analyzer.analyze_image(image_path)
                    results.append(result)
                    
                    # 标记为已分析
                    file_hash = self._get_file_hash(image_path)
                    if file_hash in self.file_hashes:
                        self.file_hashes[file_hash]['analyzed'] = True
                        self.file_hashes[file_hash]['analyzed_time'] = datetime.now().isoformat()
                    
                except Exception as e:
                    print(f"❌ 分析图片失败 {image_path}: {e}")
            
            # 保存状态
            self._save_state()
        else:
            print("📝 没有发现新图片")
        
        return results
    
    def get_monitor_stats(self) -> Dict:
        """获取监控统计信息"""
        total_files = len(self.file_hashes)
        analyzed_files = sum(1 for info in self.file_hashes.values() if info.get('analyzed', False))
        
        return {
            'is_running': self.is_running,
            'watch_directories': self.watch_directories,
            'total_files_seen': total_files,
            'analyzed_files': analyzed_files,
            'pending_files': total_files - analyzed_files,
            'check_interval': self.check_interval,
            'supported_extensions': self.supported_extensions
        }
    
    def clear_state(self):
        """清除监控状态"""
        self.file_hashes = {}
        self._save_state()
        print("🔄 监控状态已清除")
    
    def add_watch_directory(self, directory: str):
        """添加监控目录"""
        if directory not in self.watch_directories:
            self.watch_directories.append(directory)
            os.makedirs(directory, exist_ok=True)
            print(f"✅ 已添加监控目录: {directory}")
    
    def remove_watch_directory(self, directory: str):
        """移除监控目录"""
        if directory in self.watch_directories:
            self.watch_directories.remove(directory)
            print(f"✅ 已移除监控目录: {directory}")


def default_callback(image_path: str, result: Dict):
    """默认回调函数"""
    print(f"📊 图片分析完成: {os.path.basename(image_path)}")
    if result.get('success'):
        print(f"   分析类型: {result.get('analysis_type', 'unknown')}")
        print(f"   使用模型: {result.get('model_used', 'unknown')}")
        
        # 显示提取的关键信息
        extracted_data = result.get('extracted_data', {})
        if extracted_data:
            print(f"   提取数据: {list(extracted_data.keys())}")


def main():
    """主函数 - 演示图片上传监控器的使用"""
    print("🚀 图片上传监控器")
    print("=" * 50)
    
    # 创建监控器
    monitor = ImageUploadMonitor(callback=default_callback)
    
    # 显示统计信息
    stats = monitor.get_monitor_stats()
    print(f"📊 监控统计:")
    print(f"   监控目录: {', '.join(stats['watch_directories'])}")
    print(f"   已发现文件: {stats['total_files_seen']}")
    print(f"   已分析文件: {stats['analyzed_files']}")
    print(f"   待分析文件: {stats['pending_files']}")
    
    # 先手动扫描一次
    print("\n🔍 执行初始扫描...")
    results = monitor.scan_once()
    
    if results:
        print(f"✅ 初始扫描完成，分析了 {len(results)} 张图片")
    else:
        print("📝 初始扫描未发现新图片")
    
    # 询问是否启动自动监控
    print("\n💡 是否启动自动监控？")
    print("   - 启动后，系统将自动检测新上传的图片并进行分析")
    print("   - 按 Ctrl+C 停止监控")
    
    try:
        response = input("启动自动监控？(y/n): ").lower().strip()
        if response == 'y' or response == 'yes':
            print("\n👀 启动自动监控...")
            monitor.start_monitoring()
            
            # 保持运行
            while True:
                time.sleep(1)
        else:
            print("📝 不启动自动监控")
    
    except KeyboardInterrupt:
        if monitor.is_running:
            monitor.stop_monitoring()
        print("\n🛑 监控已停止")


if __name__ == "__main__":
    main()