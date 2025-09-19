#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重置数据库并重新初始化数据
"""

import os
import sys
import shutil
import time
from pathlib import Path

# 设置控制台编码为UTF-8
import codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

# 添加项目根目录到路径
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from database.database import StockDatabase
from api.app import _initialize_default_data

def reset_database():
    """重置数据库"""
    db_path = 'stock_portfolio.db'

    print("=" * 50)
    print("重置股票投资组合数据库")
    print("=" * 50)

    # 备份现有数据库
    if os.path.exists(db_path):
        backup_path = f"stock_portfolio_backup_{int(time.time())}.db"
        shutil.copy2(db_path, backup_path)
        print(f"✅ 已备份数据库: {backup_path}")

    # 删除现有数据库
    if os.path.exists(db_path):
        os.remove(db_path)
        print("✅ 已删除现有数据库")

    # 重新创建数据库并初始化
    try:
        print("正在创建新数据库...")
        db = StockDatabase(db_path)

        print("正在初始化新数据...")
        _initialize_default_data()

        # 验证数据
        positions = db.get_positions()
        print(f"\n✅ 数据库重置完成!")
        print(f"📊 总持仓数量: {len(positions)}")

        # 按市场统计
        market_counts = {}
        for pos in positions:
            market = pos['market']
            market_counts[market] = market_counts.get(market, 0) + 1

        print("\n📈 各市场持仓统计:")
        for market, count in market_counts.items():
            print(f"  {market}: {count}只")

        print(f"\n💰 现金余额: {db.get_total_cash():,.2f}")
        print(f"\n📁 数据库文件: {db_path}")
        print("🔄 系统已准备就绪，可以启动服务器")

    except Exception as e:
        print(f"❌ 重置数据库失败: {e}")
        return False

    return True

if __name__ == "__main__":
    import time
    reset_database()