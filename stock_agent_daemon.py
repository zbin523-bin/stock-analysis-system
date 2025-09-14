#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票分析定时任务守护进程
功能：后台运行，定时执行股票分析并发送邮件
"""

import os
import sys
import time
import subprocess
import logging
from datetime import datetime
import schedule
import threading
import signal
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('stock_agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class StockAgentDaemon:
    def __init__(self):
        self.running = False
        self.process = None
        self.setup_signal_handlers()
    
    def setup_signal_handlers(self):
        """设置信号处理器"""
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """处理终止信号"""
        logger.info(f"收到信号 {signum}，正在停止守护进程...")
        self.stop()
    
    def check_dependencies(self):
        """检查依赖项"""
        required_files = [
            'stock_portfolio_analyzer.py',
            '.env',
            'requirements.txt'
        ]
        
        for file in required_files:
            if not os.path.exists(file):
                logger.error(f"缺少必要文件: {file}")
                return False
        
        # 检查Python包
        try:
            import pandas, requests, matplotlib, talib, schedule
            logger.info("所有依赖包已安装")
            return True
        except ImportError as e:
            logger.error(f"缺少依赖包: {e}")
            return False
    
    def install_dependencies(self):
        """安装依赖包"""
        logger.info("正在安装依赖包...")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                         check=True, capture_output=True)
            logger.info("依赖包安装完成")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"依赖包安装失败: {e}")
            return False
    
    def run_analysis(self):
        """执行单次分析"""
        logger.info("开始执行股票分析...")
        try:
            result = subprocess.run([
                sys.executable, 'stock_portfolio_analyzer.py'
            ], capture_output=True, text=True, timeout=600)  # 10分钟超时
            
            if result.returncode == 0:
                logger.info("股票分析完成")
                if result.stdout:
                    logger.info(f"输出: {result.stdout}")
            else:
                logger.error(f"股票分析失败: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            logger.error("股票分析超时")
        except Exception as e:
            logger.error(f"股票分析异常: {e}")
    
    def setup_schedule(self):
        """设置定时任务"""
        # 每天下午4点30分运行（股市收盘后）
        schedule.every().day.at("16:30").do(self.run_analysis)
        
        # 每周一上午9点运行（周策略）
        schedule.every().monday.at("09:00").do(self.run_analysis)
        
        # 每月最后一天下午3点运行（月度总结）
        schedule.every().day.at("15:00").do(self.check_month_end)
        
        logger.info("定时任务设置完成:")
        logger.info("- 每天16:30: 股市收盘分析")
        logger.info("- 每周一09:00: 周策略分析")
        logger.info("- 每月最后一天15:00: 月度总结")
    
    def check_month_end(self):
        """检查是否为月末"""
        from datetime import datetime
        today = datetime.now()
        tomorrow = today.replace(day=today.day + 1)
        
        if today.month != tomorrow.month:  # 明天是下个月，说明今天是月末
            logger.info("执行月末分析")
            self.run_analysis()
    
    def run_scheduler(self):
        """运行调度器"""
        logger.info("调度器启动")
        while self.running:
            schedule.run_pending()
            time.sleep(30)  # 每30秒检查一次
    
    def start(self):
        """启动守护进程"""
        if self.running:
            logger.warning("守护进程已在运行")
            return
        
        logger.info("启动股票分析守护进程...")
        
        # 检查依赖
        if not self.check_dependencies():
            logger.info("正在安装依赖...")
            if not self.install_dependencies():
                logger.error("依赖安装失败，无法启动")
                return
        
        # 设置定时任务
        self.setup_schedule()
        
        # 启动调度器线程
        self.running = True
        scheduler_thread = threading.Thread(target=self.run_scheduler)
        scheduler_thread.daemon = True
        scheduler_thread.start()
        
        # 立即执行一次分析
        self.run_analysis()
        
        logger.info("守护进程启动完成")
        logger.info("按 Ctrl+C 停止服务")
        
        # 主线程保持运行
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("收到中断信号")
        finally:
            self.stop()
    
    def stop(self):
        """停止守护进程"""
        if not self.running:
            return
        
        logger.info("正在停止守护进程...")
        self.running = False
        
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except:
                try:
                    self.process.kill()
                except:
                    pass
        
        logger.info("守护进程已停止")
    
    def status(self):
        """获取状态信息"""
        status = {
            "running": self.running,
            "pid": os.getpid(),
            "jobs": len(schedule.jobs),
            "next_run": None
        }
        
        if schedule.jobs:
            next_job = min(schedule.jobs, key=lambda x: x.next_run)
            status["next_run"] = next_job.next_run.strftime("%Y-%m-%d %H:%M:%S")
        
        return status

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='股票分析守护进程')
    parser.add_argument('action', choices=['start', 'stop', 'status', 'install'], 
                       help='操作类型')
    parser.add_argument('--config', default='.env', help='配置文件路径')
    
    args = parser.parse_args()
    
    daemon = StockAgentDaemon()
    
    if args.action == 'start':
        daemon.start()
    elif args.action == 'stop':
        daemon.stop()
    elif args.action == 'status':
        status = daemon.status()
        print(f"状态: {'运行中' if status['running'] else '已停止'}")
        print(f"PID: {status['pid']}")
        print(f"定时任务数: {status['jobs']}")
        if status['next_run']:
            print(f"下次运行: {status['next_run']}")
    elif args.action == 'install':
        if daemon.install_dependencies():
            print("依赖安装完成")
        else:
            print("依赖安装失败")

if __name__ == "__main__":
    main()