"""
日志系统模块
提供统一的日志记录和管理功能
"""

import sys
import os
from datetime import datetime
from pathlib import Path
from loguru import logger
from typing import Optional


class LoggerManager:
    """日志管理器"""
    
    def __init__(self, log_dir: str = "data/logs", log_level: str = "INFO"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_level = log_level
        self.setup_logger()
    
    def setup_logger(self):
        """设置日志器"""
        # 移除默认的日志处理器
        logger.remove()
        
        # 控制台日志格式
        console_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )
        
        # 文件日志格式
        file_format = (
            "{time:YYYY-MM-DD HH:mm:ss} | "
            "{level: <8} | "
            "{name}:{function}:{line} | "
            "{message}"
        )
        
        # 添加控制台处理器
        logger.add(
            sys.stdout,
            format=console_format,
            level=self.log_level,
            colorize=True
        )
        
        # 添加文件处理器
        log_file = self.log_dir / f"stock_agent_{datetime.now().strftime('%Y%m%d')}.log"
        logger.add(
            log_file,
            format=file_format,
            level=self.log_level,
            rotation="10 MB",
            retention="7 days",
            compression="zip",
            encoding="utf-8"
        )
        
        # 添加错误日志文件
        error_log_file = self.log_dir / f"stock_agent_error_{datetime.now().strftime('%Y%m%d')}.log"
        logger.add(
            error_log_file,
            format=file_format,
            level="ERROR",
            rotation="10 MB",
            retention="30 days",
            compression="zip",
            encoding="utf-8"
        )
    
    def get_logger(self, name: str):
        """获取指定名称的日志器"""
        return logger.bind(name=name)
    
    def set_level(self, level: str):
        """设置日志级别"""
        self.log_level = level
        self.setup_logger()


# 全局日志管理器实例
log_manager = LoggerManager()


def get_logger(name: str):
    """获取日志器的便捷函数"""
    return log_manager.get_logger(name)


# 为不同模块创建日志器
main_logger = get_logger("main_agent")
data_logger = get_logger("data_fetching")
portfolio_logger = get_logger("portfolio_analysis")
feishu_logger = get_logger("feishu_integration")
notification_logger = get_logger("notification")
ai_logger = get_logger("ai_analysis")