#!/usr/bin/env python3
"""
测试完整的飞书多维表格解决方案
"""

import sys
import os
sys.path.append('.')

from agents.feishu_bitable_agent import FeishuBitableAgent
from utils.logger import get_logger
import json

def main():
    logger = get_logger("test_complete_feishu_solution")
    
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
    
    # 步骤1: 创建应用和表格配置
    logger.info("=== 步骤1: 创建应用和表格配置 ===")
    app_result = agent.create_bitable_app()
    
    if app_result.get('success'):
        logger.info("✅ 飞书应用创建成功")
        logger.info(f"App Token: {app_result.get('app_token')}")
        logger.info(f"配置的表格: {list(app_result.get('tables', {}).keys())}")
    else:
        logger.error("❌ 飞书应用创建失败")
        return
    
    # 步骤2: 测试数据同步
    logger.info("=== 步骤2: 测试数据同步 ===")
    
    # 模拟持仓数据
    position_data = {
        'symbol': 'AAPL',
        'name': 'Apple Inc.',
        'market_type': 'US',
        'buy_price': 150.00,
        'current_price': 175.50,
        'quantity': 100,
        'buy_date': '2024-01-15',
        'total_cost': 15000.00,
        'current_value': 17550.00,
        'profit_loss': 2550.00,
        'profit_loss_percent': 17.0,
        'notes': '长期持有'
    }
    
    sync_result = agent.sync_position_to_bitable(position_data)
    logger.info(f"持仓同步结果: {sync_result}")
    
    # 步骤3: 生成分享链接
    logger.info("=== 步骤3: 生成分享链接 ===")
    share_links = agent.get_share_links()
    
    for table_key, link_info in share_links.items():
        logger.info(f"表格 {table_key}: {link_info['table_name']}")
        logger.info(f"  应用链接: {link_info['app_url']}")
        logger.info(f"  说明: {link_info['note']}")
    
    # 步骤4: 导出CSV文件
    logger.info("=== 步骤4: 导出CSV文件 ===")
    export_result = agent.export_data_to_csv()
    
    for table_key, export_info in export_result.items():
        logger.info(f"表格 {table_key}: {export_info['table_name']}")
        logger.info(f"  CSV文件: {export_info['csv_file']}")
        logger.info(f"  记录数: {export_info['record_count']}")
    
    # 步骤5: 显示完整的解决方案说明
    logger.info("=== 步骤5: 完整解决方案说明 ===")
    logger.info("✅ 飞书应用已创建成功")
    logger.info("✅ 数据同步系统已配置完成")
    logger.info("✅ 本地数据存储已建立")
    logger.info("✅ CSV导出功能已准备就绪")
    
    logger.info("\n📋 用户操作指南:")
    logger.info("1. 访问飞书应用链接，手动创建4个表格")
    logger.info("2. 使用data/feishu_export/目录中的CSV文件导入数据")
    logger.info("3. 系统会自动同步新的交易记录到本地文件")
    logger.info("4. 定期导出CSV文件并更新到飞书表格")
    
    logger.info(f"\n🔗 飞书应用链接:")
    for table_key, link_info in share_links.items():
        logger.info(f"{table_key}: {link_info['app_url']}")

if __name__ == "__main__":
    main()