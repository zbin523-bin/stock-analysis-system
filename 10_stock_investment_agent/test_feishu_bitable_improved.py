#!/usr/bin/env python3
"""
测试改进的飞书多维表格创建功能
"""

import sys
import os
sys.path.append('.')

from agents.feishu_bitable_agent import FeishuBitableAgent
from utils.logger import get_logger
import json

def main():
    logger = get_logger("test_feishu_bitable")
    
    # 加载配置
    try:
        with open('config/api_keys.json', 'r', encoding='utf-8') as f:
            api_keys = json.load(f)
        
        with open('config/settings.json', 'r', encoding='utf-8') as f:
            settings = json.load(f)
            
    except FileNotFoundError as e:
        logger.error(f"配置文件不存在: {e}")
        return
    
    # 初始化飞书多维表格Agent
    agent = FeishuBitableAgent(api_keys, settings)
    
    if not agent.bitable_manager:
        logger.error("多维表格管理器初始化失败")
        return
    
    # 测试创建应用和表格
    logger.info("开始测试创建应用和表格...")
    
    result = agent.create_bitable_app()
    
    if result.get('success'):
        logger.info("✅ 多维表格应用和表格创建成功")
        logger.info(f"App Token: {result.get('app_token')}")
        logger.info(f"创建的表格: {list(result.get('tables', {}).keys())}")
        
        # 显示表格详情
        for table_key, table_info in result.get('tables', {}).items():
            logger.info(f"  表格 {table_key}: {table_info.get('table_name')} ({table_info.get('table_id')})")
    else:
        logger.error("❌ 多维表格应用或表格创建失败")
        logger.error(f"错误信息: {result.get('error')}")

if __name__ == "__main__":
    main()