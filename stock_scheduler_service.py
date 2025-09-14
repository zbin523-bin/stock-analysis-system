#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票分析定时服务
Stock Analysis Scheduled Service
功能：作为系统服务运行定时股票分析任务
"""

import os
import sys
import time
import signal
import logging
import argparse
from datetime import datetime, timedelta
import schedule
import threading
import daemon
from daemon import pidfile

# 添加项目路径
project_path = '/Volumes/Work/SynologyDrive/claude'
sys.path.insert(0, project_path)

from stock_notification_agent_enhanced import StockNotificationAgent

class StockSchedulerService:
    """股票定时调度服务"""
    
    def __init__(self, config_file=None):
        self.setup_logging()
        self.agent = StockNotificationAgent()
        self.running = False
        self.config = self.load_config(config_file)
        
        # 设置定时任务
        self.setup_schedule()
        
        self.logger.info("股票分析定时服务初始化完成")
    
    def setup_logging(self):
        """设置日志"""
        log_dir = '/var/log/stock_analyzer'
        os.makedirs(log_dir, exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'{log_dir}/scheduler.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('StockScheduler')
    
    def load_config(self, config_file):
        """加载配置"""
        default_config = {
            'schedule_times': ['10:00', '16:00'],
            'timezone': 'Asia/Shanghai',
            'retry_attempts': 3,
            'health_check_interval': 300  # 5分钟
        }
        
        # 这里可以加载配置文件
        return default_config
    
    def setup_schedule(self):
        """设置定时任务"""
        times = self.config.get('schedule_times', ['10:00', '16:00'])
        
        for time_str in times:
            schedule.every().day.at(time_str).do(self.run_scheduled_analysis)
            self.logger.info(f"已设置定时任务: 每天 {time_str}")
        
        # 健康检查
        schedule.every(self.config['health_check_interval']).seconds.do(self.health_check)
    
    def run_scheduled_analysis(self):
        """运行定时分析"""
        self.logger.info(f"开始定时分析 - {datetime.now()}")
        
        retry_count = 0
        max_retries = self.config.get('retry_attempts', 3)
        
        while retry_count < max_retries:
            try:
                result = self.agent.run_analysis_and_send_email()
                if result:
                    self.logger.info("定时分析完成，邮件已发送")
                    break
                else:
                    raise Exception("邮件发送失败")
                    
            except Exception as e:
                retry_count += 1
                self.logger.error(f"定时分析失败 (尝试 {retry_count}/{max_retries}): {e}")
                
                if retry_count < max_retries:
                    wait_time = 300 * retry_count  # 递增等待时间
                    self.logger.info(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                else:
                    self.logger.error("定时分析最终失败")
    
    def health_check(self):
        """健康检查"""
        try:
            # 检查网络连接
            import requests
            response = requests.get('https://www.baidu.com', timeout=10)
            
            # 检查Gmail连接
            gmail_ok = self.agent.test_gmail_connection()
            
            self.logger.info(f"健康检查 - 网络: {'OK' if response.status_code == 200 else 'FAIL'}, Gmail: {'OK' if gmail_ok else 'FAIL'}")
            
        except Exception as e:
            self.logger.error(f"健康检查失败: {e}")
    
    def start(self):
        """启动服务"""
        self.running = True
        self.logger.info("股票分析定时服务启动")
        
        try:
            # 注册信号处理
            signal.signal(signal.SIGTERM, self.signal_handler)
            signal.signal(signal.SIGINT, self.signal_handler)
            
            # 立即运行一次
            self.logger.info("运行初始分析...")
            self.run_scheduled_analysis()
            
            # 主循环
            while self.running:
                schedule.run_pending()
                time.sleep(60)  # 每分钟检查一次
                
        except KeyboardInterrupt:
            self.logger.info("收到中断信号")
        except Exception as e:
            self.logger.error(f"服务运行异常: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """停止服务"""
        self.running = False
        self.logger.info("股票分析定时服务停止")
    
    def signal_handler(self, signum, frame):
        """信号处理器"""
        self.logger.info(f"收到信号 {signum}，准备停止服务...")
        self.stop()
        sys.exit(0)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='股票分析定时服务')
    parser.add_argument('--daemon', action='store_true', help='以守护进程方式运行')
    parser.add_argument('--pid-file', default='/tmp/stock_scheduler.pid', help='PID文件路径')
    parser.add_argument('--config', help='配置文件路径')
    
    args = parser.parse_args()
    
    if args.daemon:
        # 以守护进程方式运行
        with daemon.DaemonContext(
            pidfile=pidfile.TimeoutPIDLockFile(args.pid_file),
            working_directory='/Volumes/Work/SynologyDrive/claude'
        ):
            service = StockSchedulerService(args.config)
            service.start()
    else:
        # 前台运行
        service = StockSchedulerService(args.config)
        service.start()

if __name__ == "__main__":
    main()