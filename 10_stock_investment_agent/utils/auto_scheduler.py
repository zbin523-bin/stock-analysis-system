"""
自动化调度器模块
提供定时任务、自动更新、报告生成等功能
"""

import schedule
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Callable, Optional
from loguru import logger
from utils.date_utils import DateUtils
from utils.logger import get_logger


class AutoScheduler:
    """自动化调度器"""
    
    def __init__(self):
        self.logger = get_logger("scheduler")
        self.date_utils = DateUtils()
        self.running = False
        self.scheduler_thread = None
        self.tasks = {}
        
    def add_task(self, task_name: str, task_func: Callable, 
                schedule_type: str, schedule_value: str, 
                description: str = ""):
        """
        添加定时任务
        
        Args:
            task_name: 任务名称
            task_func: 任务函数
            schedule_type: 调度类型 ('interval', 'daily', 'weekly', 'monthly')
            schedule_value: 调度值
            description: 任务描述
        """
        try:
            if schedule_type == 'interval':
                # 间隔调度
                interval = int(schedule_value)
                schedule.every(interval).minutes.do(task_func).tag(task_name)
                
            elif schedule_type == 'daily':
                # 每日调度
                hour, minute = map(int, schedule_value.split(':'))
                schedule.every().day.at(f"{hour:02d}:{minute:02d}").do(task_func).tag(task_name)
                
            elif schedule_type == 'weekly':
                # 每周调度
                parts = schedule_value.split('_')
                weekday = parts[0]
                time_str = parts[1]
                hour, minute = map(int, time_str.split(':'))
                
                getattr(schedule.every(), weekday).at(f"{hour:02d}:{minute:02d}").do(task_func).tag(task_name)
                
            elif schedule_type == 'monthly':
                # 每月调度
                day = int(schedule_value.split('_')[0])
                time_str = schedule_value.split('_')[1]
                hour, minute = map(int, time_str.split(':'))
                
                # 简化的月度调度（实际应用中可能需要更复杂的逻辑）
                schedule.every().day.at(f"{hour:02d}:{minute:02d}").do(
                    lambda: self._check_monthly_task(day, task_func)
                ).tag(task_name)
            
            self.tasks[task_name] = {
                'func': task_func,
                'type': schedule_type,
                'value': schedule_value,
                'description': description,
                'last_run': None,
                'next_run': self._get_next_run_time(schedule_type, schedule_value)
            }
            
            self.logger.info(f"添加定时任务: {task_name} - {description}")
            
        except Exception as e:
            self.logger.error(f"添加定时任务失败: {e}")
    
    def _check_monthly_task(self, day: int, task_func: Callable):
        """检查是否为每月指定日期并执行任务"""
        today = self.date_utils.get_current_date()
        if today.day == day:
            task_func()
    
    def _get_next_run_time(self, schedule_type: str, schedule_value: str) -> Optional[datetime]:
        """获取下次运行时间"""
        try:
            now = self.date_utils.get_current_time()
            
            if schedule_type == 'interval':
                interval = int(schedule_value)
                return now + timedelta(minutes=interval)
            
            elif schedule_type == 'daily':
                hour, minute = map(int, schedule_value.split(':'))
                next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                if next_run <= now:
                    next_run += timedelta(days=1)
                return next_run
            
            elif schedule_type == 'weekly':
                parts = schedule_value.split('_')
                weekday = parts[0]
                time_str = parts[1]
                hour, minute = map(int, time_str.split(':'))
                
                # 计算下次指定周几和时间
                days_ahead = self._get_days_until_weekday(weekday)
                next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                next_run += timedelta(days=days_ahead)
                
                if next_run <= now:
                    next_run += timedelta(days=7)
                
                return next_run
            
            elif schedule_type == 'monthly':
                day = int(schedule_value.split('_')[0])
                time_str = schedule_value.split('_')[1]
                hour, minute = map(int, time_str.split(':'))
                
                # 计算下次每月指定日期
                next_run = now.replace(day=day, hour=hour, minute=minute, second=0, microsecond=0)
                if next_run <= now:
                    # 如果这个月的日期已过，计算下个月
                    if now.month == 12:
                        next_run = next_run.replace(year=now.year + 1, month=1)
                    else:
                        next_run = next_run.replace(month=now.month + 1)
                
                return next_run
            
            return None
            
        except Exception as e:
            self.logger.error(f"获取下次运行时间失败: {e}")
            return None
    
    def _get_days_until_weekday(self, weekday: str) -> int:
        """获取到指定周几的天数"""
        weekdays = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
            'friday': 4, 'saturday': 5, 'sunday': 6
        }
        
        target_weekday = weekdays.get(weekday.lower(), 0)
        current_weekday = self.date_utils.get_current_time().weekday()
        
        days_ahead = target_weekday - current_weekday
        if days_ahead < 0:
            days_ahead += 7
        
        return days_ahead
    
    def remove_task(self, task_name: str):
        """移除定时任务"""
        try:
            schedule.clear(task_name)
            if task_name in self.tasks:
                del self.tasks[task_name]
            self.logger.info(f"移除定时任务: {task_name}")
            
        except Exception as e:
            self.logger.error(f"移除定时任务失败: {e}")
    
    def start(self):
        """启动调度器"""
        if self.running:
            self.logger.warning("调度器已经在运行中")
            return
        
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        self.logger.info("调度器启动成功")
    
    def stop(self):
        """停止调度器"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        self.logger.info("调度器停止成功")
    
    def _run_scheduler(self):
        """运行调度器主循环"""
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                self.logger.error(f"调度器运行错误: {e}")
                time.sleep(5)
    
    def get_task_status(self) -> Dict:
        """获取所有任务状态"""
        status = {
            'scheduler_running': self.running,
            'total_tasks': len(self.tasks),
            'tasks': {}
        }
        
        for task_name, task_info in self.tasks.items():
            status['tasks'][task_name] = {
                'description': task_info['description'],
                'type': task_info['type'],
                'value': task_info['value'],
                'last_run': task_info['last_run'],
                'next_run': task_info['next_run']
            }
        
        return status
    
    def run_task_now(self, task_name: str):
        """立即运行指定任务"""
        try:
            if task_name in self.tasks:
                task_func = self.tasks[task_name]['func']
                task_func()
                self.logger.info(f"手动执行任务: {task_name}")
            else:
                self.logger.warning(f"任务不存在: {task_name}")
                
        except Exception as e:
            self.logger.error(f"执行任务失败: {e}")
    
    def setup_default_tasks(self, agents: Dict):
        """设置默认的定时任务"""
        try:
            # 价格更新任务 - 每5分钟
            self.add_task(
                "price_update",
                agents['data_fetching'].update_all_prices,
                "interval",
                "5",
                "更新所有持仓股票价格"
            )
            
            # 投资组合分析任务 - 每1小时
            self.add_task(
                "portfolio_analysis",
                agents['portfolio_analyzer'].analyze_portfolio,
                "interval",
                "60",
                "分析投资组合状况"
            )
            
            # 每日报告任务 - 每天18:00
            self.add_task(
                "daily_report",
                agents['notification'].send_daily_report,
                "daily",
                "18:00",
                "发送每日投资报告"
            )
            
            # 每周报告任务 - 每周日18:00
            self.add_task(
                "weekly_report",
                agents['notification'].send_weekly_report,
                "weekly",
                "sunday_18:00",
                "发送每周投资报告"
            )
            
            # AI分析任务 - 每2小时
            self.add_task(
                "ai_analysis",
                agents['ai_analyzer'].run_analysis,
                "interval",
                "120",
                "运行AI智能分析"
            )
            
            # 数据同步任务 - 每30分钟
            self.add_task(
                "data_sync",
                agents['feishu_integration'].sync_data,
                "interval",
                "30",
                "同步数据到飞书表格"
            )
            
            self.logger.info("默认定时任务设置完成")
            
        except Exception as e:
            self.logger.error(f"设置默认定时任务失败: {e}")


# 全局调度器实例
scheduler = AutoScheduler()