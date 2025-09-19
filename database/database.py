#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票投资组合数据库模块
"""

import sqlite3
import json
import logging
from datetime import datetime
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class StockDatabase:
    """股票投资组合数据库管理类"""

    def __init__(self, db_path='stock_portfolio.db'):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """初始化数据库表结构"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # 设置SQLite编码为UTF-8
                cursor.execute('PRAGMA encoding = "UTF-8"')

                # 创建持仓表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS positions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        code TEXT NOT NULL,
                        name TEXT NOT NULL,
                        market TEXT NOT NULL,
                        industry TEXT,
                        quantity INTEGER NOT NULL DEFAULT 0,
                        cost_price REAL NOT NULL DEFAULT 0,
                        currency TEXT NOT NULL DEFAULT 'CNY',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                # 创建交易记录表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS transactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT NOT NULL,
                        type TEXT NOT NULL,
                        code TEXT NOT NULL,
                        name TEXT NOT NULL,
                        market TEXT NOT NULL,
                        price REAL NOT NULL,
                        quantity INTEGER NOT NULL,
                        amount REAL NOT NULL,
                        commission REAL DEFAULT 5.00,
                        status TEXT DEFAULT '已完成',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                # 创建系统设置表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS settings (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                # 创建索引
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_positions_code_market ON positions(code, market)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_code_market ON transactions(code, market)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date)')

                conn.commit()
                logger.info("数据库初始化完成")

        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")
            raise

    @contextmanager
    def get_connection(self):
        """获取数据库连接的上下文管理器"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # 返回字典格式结果
        try:
            yield conn
        except Exception as e:
            conn.rollback()
            logger.error(f"数据库操作异常: {e}")
            raise
        finally:
            conn.close()

    def get_positions(self):
        """获取所有持仓"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM positions WHERE quantity > 0 ORDER BY id
                ''')
                positions = [dict(row) for row in cursor.fetchall()]
                return positions
        except Exception as e:
            logger.error(f"获取持仓失败: {e}")
            return []

    def get_position_by_code_market(self, code, market):
        """根据股票代码和市场获取持仓"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM positions WHERE code = ? AND market = ?
                ''', (code, market))
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"获取持仓失败: {e}")
            return None

    def add_position(self, code, name, market, quantity, cost_price, industry='其他', currency='CNY'):
        """添加持仓"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO positions (code, name, market, industry, quantity, cost_price, currency)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (code, name, market, industry, quantity, cost_price, currency))
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"添加持仓失败: {e}")
            return None

    def update_position(self, position_id, **kwargs):
        """更新持仓"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                updates = []
                params = []

                for key, value in kwargs.items():
                    if key in ['quantity', 'cost_price', 'name', 'industry']:
                        updates.append(f"{key} = ?")
                        params.append(value)

                if updates:
                    updates.append("updated_at = CURRENT_TIMESTAMP")
                    params.append(position_id)

                    query = f"UPDATE positions SET {', '.join(updates)} WHERE id = ?"
                    cursor.execute(query, params)
                    conn.commit()
                    return cursor.rowcount > 0
                return False
        except Exception as e:
            logger.error(f"更新持仓失败: {e}")
            return False

    def delete_position(self, position_id):
        """删除持仓"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM positions WHERE id = ?', (position_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"删除持仓失败: {e}")
            return False

    def get_transactions(self):
        """获取所有交易记录"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM transactions ORDER BY date DESC, id DESC
                ''')
                transactions = [dict(row) for row in cursor.fetchall()]
                return transactions
        except Exception as e:
            logger.error(f"获取交易记录失败: {e}")
            return []

    def get_transaction(self, transaction_id):
        """获取单个交易记录"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM transactions WHERE id = ?', (transaction_id,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"获取交易记录失败: {e}")
            return None

    def add_transaction(self, date, type_, code, name, market, price, quantity, commission=5.00, status='已完成'):
        """添加交易记录"""
        try:
            amount = price * quantity
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO transactions (date, type, code, name, market, price, quantity, amount, commission, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (date, type_, code, name, market, price, quantity, amount, commission, status))
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"添加交易记录失败: {e}")
            return None

    def update_transaction(self, transaction_id, **kwargs):
        """更新交易记录"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                updates = []
                params = []

                for key, value in kwargs.items():
                    if key in ['date', 'type', 'code', 'name', 'market', 'price', 'quantity', 'commission', 'status']:
                        updates.append(f"{key} = ?")
                        params.append(value)

                if updates:
                    # 如果更新了价格或数量，重新计算金额
                    if 'price' in kwargs or 'quantity' in kwargs:
                        updates.append("amount = price * quantity")

                    updates.append("updated_at = CURRENT_TIMESTAMP")
                    params.append(transaction_id)

                    query = f"UPDATE transactions SET {', '.join(updates)} WHERE id = ?"
                    cursor.execute(query, params)
                    conn.commit()
                    return cursor.rowcount > 0
                return False
        except Exception as e:
            logger.error(f"更新交易记录失败: {e}")
            return False

    def delete_transaction(self, transaction_id):
        """删除交易记录"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM transactions WHERE id = ?', (transaction_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"删除交易记录失败: {e}")
            return False

    def get_setting(self, key, default=None):
        """获取设置值"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
                row = cursor.fetchone()
                return json.loads(row['value']) if row else default
        except Exception as e:
            logger.error(f"获取设置失败: {e}")
            return default

    def set_setting(self, key, value):
        """设置值"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO settings (key, value, updated_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                ''', (key, json.dumps(value)))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"设置值失败: {e}")
            return False

    def calculate_portfolio_from_transactions(self):
        """从交易记录计算持仓"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # 获取所有交易记录
                cursor.execute('SELECT * FROM transactions ORDER BY id')
                transactions = cursor.fetchall()

                positions = {}

                for trans in transactions:
                    trans = dict(trans)
                    code = trans["code"]
                    name = trans["name"]
                    market = trans["market"]
                    quantity = trans["quantity"]
                    price = trans["price"]
                    amount = trans["amount"]
                    commission = trans.get("commission", 0)

                    key = f"{code}_{market}"

                    if key not in positions:
                        positions[key] = {
                            "code": code,
                            "name": name,
                            "market": market,
                            "quantity": 0,
                            "total_cost": 0,
                            "currency": "CNY" if market in ["A股", "基金"] else "HKD" if market == "港股" else "USD"
                        }

                    if trans["type"] in ["买入", "buy"]:
                        positions[key]["quantity"] += quantity
                        positions[key]["total_cost"] += amount + commission
                    elif trans["type"] in ["卖出", "sell"]:
                        positions[key]["quantity"] -= quantity
                        positions[key]["total_cost"] -= amount - commission

                # 转换为持仓列表
                position_list = []
                for key, pos in positions.items():
                    if pos["quantity"] > 0:  # 只显示有持仓的
                        cost_price = pos["total_cost"] / pos["quantity"]
                        position_list.append({
                            "code": pos["code"],
                            "name": pos["name"],
                            "market": pos["market"],
                            "industry": "基金" if pos["market"] == "基金" else ("股票" if pos["market"] == "A股" else "股票"),
                            "quantity": pos["quantity"],
                            "cost_price": cost_price,
                            "currency": pos["currency"]
                        })

                return position_list
        except Exception as e:
            logger.error(f"计算持仓失败: {e}")
            return []

    def sync_positions_from_transactions(self):
        """从交易记录同步持仓数据"""
        try:
            calculated_positions = self.calculate_portfolio_from_transactions()

            with self.get_connection() as conn:
                cursor = conn.cursor()

                # 清空现有持仓
                cursor.execute('DELETE FROM positions')

                # 插入新的持仓
                for pos in calculated_positions:
                    cursor.execute('''
                        INSERT INTO positions (code, name, market, industry, quantity, cost_price, currency)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (pos["code"], pos["name"], pos["market"], pos["industry"],
                          pos["quantity"], pos["cost_price"], pos["currency"]))

                conn.commit()
                logger.info(f"持仓同步完成，共{len(calculated_positions)}个持仓")
                return True

        except Exception as e:
            logger.error(f"同步持仓失败: {e}")
            return False

    def get_total_cash(self):
        """获取总现金余额（人民币等价）"""
        cash_balances = self.get_cash_balances()
        total_cny = 0

        # 汇率（实际应用中应该从API获取实时汇率）
        exchange_rates = {
            'CNY': 1.0,
            'USD': 7.2,  # 1 USD = 7.2 CNY
            'HKD': 0.92  # 1 HKD = 0.92 CNY
        }

        for currency, amount in cash_balances.items():
            total_cny += amount * exchange_rates.get(currency, 1.0)

        return total_cny

    def set_total_cash(self, amount):
        """设置总现金余额（人民币）"""
        return self.set_setting('total_cash', amount)

    def get_cash_balances(self):
        """获取各币种现金余额"""
        return self.get_setting('cash_balances', {
            'CNY': 50000,   # 人民币现金
            'USD': 1000,    # 美元现金
            'HKD': 5000     # 港币现金
        })

    def set_cash_balances(self, balances):
        """设置各币种现金余额"""
        return self.set_setting('cash_balances', balances)

    def get_cash_balance(self, currency):
        """获取指定币种的现金余额"""
        balances = self.get_cash_balances()
        return balances.get(currency, 0)

    def set_cash_balance(self, currency, amount):
        """设置指定币种的现金余额"""
        balances = self.get_cash_balances()
        balances[currency] = amount
        return self.set_cash_balances(balances)

    def update_cash_balance(self, currency, amount_change):
        """更新指定币种的现金余额"""
        balances = self.get_cash_balances()
        current_balance = balances.get(currency, 0)
        balances[currency] = current_balance + amount_change
        return self.set_cash_balances(balances)