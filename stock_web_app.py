#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版股票分析系统 - 包含交易功能和详细盈亏统计
Enhanced Stock Analysis System with Trading Functions and Detailed P&L Statistics
"""

import os
import json
import sqlite3
from datetime import datetime, timedelta, date
from flask import Flask, render_template_string, request, jsonify
from stock_notification_agent_enhanced import StockNotificationAgent
from config import *

app = Flask(__name__)

# 数据库初始化
def init_db():
    conn = sqlite3.connect('trading_data.db')
    cursor = conn.cursor()
    
    # 交易记录表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stock_name TEXT NOT NULL,
            stock_code TEXT NOT NULL,
            trade_type TEXT NOT NULL,  -- 'buy' or 'sell'
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            total_amount REAL NOT NULL,
            currency TEXT NOT NULL,
            trade_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            notes TEXT
        )
    ''')
    
    # 持仓表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS positions (
            stock_name TEXT PRIMARY KEY,
            stock_code TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            avg_cost REAL NOT NULL,
            total_cost REAL NOT NULL,
            currency TEXT NOT NULL,
            last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 价格历史表（用于计算盈亏）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stock_name TEXT NOT NULL,
            stock_code TEXT NOT NULL,
            price REAL NOT NULL,
            currency TEXT NOT NULL,
            record_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

class EnhancedStockSystem:
    def __init__(self):
        self.agent = StockNotificationAgent()
        init_db()
    
    def add_trade(self, stock_name, stock_code, trade_type, quantity, price, currency='HKD', notes=''):
        """添加交易记录"""
        total_amount = quantity * price
        
        conn = sqlite3.connect('trading_data.db')
        cursor = conn.cursor()
        
        # 添加交易记录
        cursor.execute('''
            INSERT INTO trades (stock_name, stock_code, trade_type, quantity, price, total_amount, currency, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (stock_name, stock_code, trade_type, quantity, price, total_amount, currency, notes))
        
        # 更新持仓
        if trade_type == 'buy':
            cursor.execute('''
                INSERT OR REPLACE INTO positions (stock_name, stock_code, quantity, avg_cost, total_cost, currency)
                VALUES (?, ?, 
                    COALESCE((SELECT quantity FROM positions WHERE stock_name = ?), 0) + ?,
                    (COALESCE((SELECT total_cost FROM positions WHERE stock_name = ?), 0) + ?) / 
                    (COALESCE((SELECT quantity FROM positions WHERE stock_name = ?), 0) + ?),
                    COALESCE((SELECT total_cost FROM positions WHERE stock_name = ?), 0) + ?, ?
                )
            ''', (stock_name, stock_code, stock_name, quantity, stock_name, total_amount, stock_name, quantity, stock_name, total_amount, currency))
        else:  # sell
            current_pos = cursor.execute('SELECT quantity, avg_cost FROM positions WHERE stock_name = ?', (stock_name,)).fetchone()
            if current_pos and current_pos[0] >= quantity:
                # 更新持仓数量和成本
                remaining_qty = current_pos[0] - quantity
                if remaining_qty > 0:
                    cursor.execute('''
                        UPDATE positions SET quantity = ?, total_cost = ? WHERE stock_name = ?
                    ''', (remaining_qty, current_pos[1] * remaining_qty, stock_name))
                else:
                    cursor.execute('DELETE FROM positions WHERE stock_name = ?', (stock_name,))
        
        conn.commit()
        conn.close()
        
        return True
    
    def get_positions(self):
        """获取当前持仓"""
        conn = sqlite3.connect('trading_data.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM positions ORDER BY stock_name')
        positions = cursor.fetchall()
        conn.close()
        
        return [
            {
                'stock_name': pos[0],
                'stock_code': pos[1], 
                'quantity': pos[2],
                'avg_cost': pos[3],
                'total_cost': pos[4],
                'currency': pos[5]
            }
            for pos in positions
        ]
    
    def get_trades(self, days=30):
        """获取交易记录"""
        conn = sqlite3.connect('trading_data.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM trades 
            WHERE trade_date >= date('now', '-{} days')
            ORDER BY trade_date DESC
        '''.format(days))
        trades = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': trade[0],
                'stock_name': trade[1],
                'stock_code': trade[2],
                'trade_type': trade[3],
                'quantity': trade[4],
                'price': trade[5],
                'total_amount': trade[6],
                'currency': trade[7],
                'trade_date': trade[8],
                'notes': trade[9]
            }
            for trade in trades
        ]
    
    def calculate_pnl(self):
        """计算详细盈亏统计"""
        positions = self.get_positions()
        
        # 获取当前价格
        current_prices = {}
        for pos in positions:
            try:
                ticker = yf.Ticker(pos['stock_code'])
                hist = ticker.history(period='1d')
                if not hist.empty:
                    current_prices[pos['stock_name']] = hist.iloc[-1]['Close']
                else:
                    current_prices[pos['stock_name']] = pos['avg_cost']
            except:
                current_prices[pos['stock_name']] = pos['avg_cost']
        
        total_pnl = 0
        daily_pnl = 0
        weekly_pnl = 0
        monthly_pnl = 0
        
        position_details = []
        
        for pos in positions:
            current_price = current_prices.get(pos['stock_name'], pos['avg_cost'])
            current_value = pos['quantity'] * current_price
            cost_basis = pos['total_cost']
            
            unrealized_pnl = current_value - cost_basis
            pnl_percent = (unrealized_pnl / cost_basis * 100) if cost_basis > 0 else 0
            
            total_pnl += unrealized_pnl
            
            position_details.append({
                'stock_name': pos['stock_name'],
                'quantity': pos['quantity'],
                'avg_cost': pos['avg_cost'],
                'current_price': current_price,
                'current_value': current_value,
                'cost_basis': cost_basis,
                'unrealized_pnl': unrealized_pnl,
                'pnl_percent': pnl_percent,
                'currency': pos['currency']
            })
        
        # 计算已实现盈亏（从交易记录）
        conn = sqlite3.connect('trading_data.db')
        cursor = conn.cursor()
        
        # 当日已实现盈亏
        cursor.execute('''
            SELECT trade_type, SUM(total_amount) 
            FROM trades 
            WHERE date(trade_date) = date('now')
            GROUP BY trade_type
        ''')
        daily_trades = dict(cursor.fetchall())
        
        # 本周已实现盈亏
        cursor.execute('''
            SELECT trade_type, SUM(total_amount) 
            FROM trades 
            WHERE date(trade_date) >= date('now', 'weekday 0')
            GROUP BY trade_type
        ''')
        weekly_trades = dict(cursor.fetchall())
        
        # 本月已实现盈亏
        cursor.execute('''
            SELECT trade_type, SUM(total_amount) 
            FROM trades 
            WHERE date(trade_date) >= date('now', 'start of month')
            GROUP BY trade_type
        ''')
        monthly_trades = dict(cursor.fetchall())
        
        conn.close()
        
        realized_daily = (daily_trades.get('sell', 0) - daily_trades.get('buy', 0))
        realized_weekly = (weekly_trades.get('sell', 0) - weekly_trades.get('buy', 0))
        realized_monthly = (monthly_trades.get('sell', 0) - monthly_trades.get('buy', 0))
        
        return {
            'total_unrealized_pnl': total_pnl,
            'daily_realized_pnl': realized_daily,
            'weekly_realized_pnl': realized_weekly,
            'monthly_realized_pnl': realized_monthly,
            'daily_total_pnl': total_pnl + realized_daily,
            'weekly_total_pnl': total_pnl + realized_weekly,
            'monthly_total_pnl': total_pnl + realized_monthly,
            'positions': position_details
        }

# 创建系统实例
stock_system = EnhancedStockSystem()

# Flask路由
@app.route('/')
def index():
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>股票交易系统</title>
            <meta charset="utf-8">
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .container { max-width: 1200px; margin: 0 auto; }
                .section { margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }
                .form-group { margin: 10px 0; }
                label { display: inline-block; width: 120px; font-weight: bold; }
                input, select { padding: 5px; margin: 0 10px; }
                button { padding: 10px 20px; margin: 5px; background: #007cba; color: white; border: none; border-radius: 3px; cursor: pointer; }
                button:hover { background: #005a87; }
                table { width: 100%; border-collapse: collapse; margin: 10px 0; }
                th, td { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }
                .profit { color: green; }
                .loss { color: red; }
                .pnl-summary { font-size: 18px; font-weight: bold; margin: 10px 0; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📈 股票交易管理系统</h1>
                
                <!-- 交易表单 -->
                <div class="section">
                    <h2>💼 交易操作</h2>
                    <form id="tradeForm">
                        <div class="form-group">
                            <label>股票名称:</label>
                            <input type="text" id="stockName" required>
                        </div>
                        <div class="form-group">
                            <label>股票代码:</label>
                            <input type="text" id="stockCode" required>
                        </div>
                        <div class="form-group">
                            <label>交易类型:</label>
                            <select id="tradeType" required>
                                <option value="buy">买入</option>
                                <option value="sell">卖出</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>数量:</label>
                            <input type="number" id="quantity" required>
                        </div>
                        <div class="form-group">
                            <label>价格:</label>
                            <input type="number" step="0.01" id="price" required>
                        </div>
                        <div class="form-group">
                            <label>货币:</label>
                            <select id="currency">
                                <option value="HKD">港币</option>
                                <option value="CNY">人民币</option>
                                <option value="USD">美元</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>备注:</label>
                            <input type="text" id="notes">
                        </div>
                        <button type="submit">提交交易</button>
                    </form>
                </div>
                
                <!-- 盈亏统计 -->
                <div class="section">
                    <h2>📊 盈亏统计</h2>
                    <div id="pnlStats">加载中...</div>
                    <button onclick="refreshPnl()">刷新数据</button>
                </div>
                
                <!-- 当前持仓 -->
                <div class="section">
                    <h2>📋 当前持仓</h2>
                    <div id="positions">加载中...</div>
                    <button onclick="refreshPositions()">刷新持仓</button>
                </div>
                
                <!-- 交易记录 -->
                <div class="section">
                    <h2>📝 交易记录</h2>
                    <div id="trades">加载中...</div>
                    <button onclick="refreshTrades()">刷新记录</button>
                </div>
                
                <!-- 快速操作 -->
                <div class="section">
                    <h2>⚡ 快速操作</h2>
                    <button onclick="sendReport()">📧 发送分析报告</button>
                    <button onclick="loadCurrentPrices()">🔄 更新股价</button>
                </div>
            </div>

            <script>
                // 页面加载时初始化数据
                document.addEventListener('DOMContentLoaded', function() {
                    refreshPnl();
                    refreshPositions();
                    refreshTrades();
                });

                // 提交交易表单
                document.getElementById('tradeForm').addEventListener('submit', function(e) {
                    e.preventDefault();
                    
                    const data = {
                        stock_name: document.getElementById('stockName').value,
                        stock_code: document.getElementById('stockCode').value,
                        trade_type: document.getElementById('tradeType').value,
                        quantity: parseInt(document.getElementById('quantity').value),
                        price: parseFloat(document.getElementById('price').value),
                        currency: document.getElementById('currency').value,
                        notes: document.getElementById('notes').value
                    };
                    
                    fetch('/api/trade', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify(data)
                    })
                    .then(response => response.json())
                    .then(data => {
                        alert(data.message);
                        if (data.success) {
                            document.getElementById('tradeForm').reset();
                            refreshPnl();
                            refreshPositions();
                            refreshTrades();
                        }
                    })
                    .catch(error => {
                        alert('交易失败: ' + error);
                    });
                });

                function refreshPnl() {
                    fetch('/api/pnl')
                        .then(response => response.json())
                        .then(data => {
                            const pnlDiv = document.getElementById('pnlStats');
                            pnlDiv.innerHTML = `
                                <div class="pnl-summary">
                                    <div>📅 当日盈亏: <span class="${data.daily_total_pnl >= 0 ? 'profit' : 'loss'}">
                                        ${data.daily_total_pnl.toFixed(2)} CNY
                                    </span></div>
                                    <div>📆 本周盈亏: <span class="${data.weekly_total_pnl >= 0 ? 'profit' : 'loss'}">
                                        ${data.weekly_total_pnl.toFixed(2)} CNY
                                    </span></div>
                                    <div>📅 本月盈亏: <span class="${data.monthly_total_pnl >= 0 ? 'profit' : 'loss'}">
                                        ${data.monthly_total_pnl.toFixed(2)} CNY
                                    </span></div>
                                    <div>💰 总未实现盈亏: <span class="${data.total_unrealized_pnl >= 0 ? 'profit' : 'loss'}">
                                        ${data.total_unrealized_pnl.toFixed(2)} CNY
                                    </span></div>
                                </div>
                                <h3>持仓明细:</h3>
                                <table>
                                    <tr><th>股票</th><th>数量</th><th>成本价</th><th>现价</th><th>盈亏</th><th>盈亏%</th></tr>
                                    ${data.positions.map(pos => `
                                        <tr>
                                            <td>${pos.stock_name}</td>
                                            <td>${pos.quantity}</td>
                                            <td>${pos.avg_cost.toFixed(2)}</td>
                                            <td>${pos.current_price.toFixed(2)}</td>
                                            <td class="${pos.unrealized_pnl >= 0 ? 'profit' : 'loss'}">
                                                ${pos.unrealized_pnl.toFixed(2)}
                                            </td>
                                            <td class="${pos.pnl_percent >= 0 ? 'profit' : 'loss'}">
                                                ${pos.pnl_percent.toFixed(2)}%
                                            </td>
                                        </tr>
                                    `).join('')}
                                </table>
                            `;
                        });
                }

                function refreshPositions() {
                    fetch('/api/positions')
                        .then(response => response.json())
                        .then(data => {
                            const posDiv = document.getElementById('positions');
                            posDiv.innerHTML = `
                                <table>
                                    <tr><th>股票名称</th><th>代码</th><th>数量</th><th>平均成本</th><th>总成本</th><th>货币</th></tr>
                                    ${data.map(pos => `
                                        <tr>
                                            <td>${pos.stock_name}</td>
                                            <td>${pos.stock_code}</td>
                                            <td>${pos.quantity}</td>
                                            <td>${pos.avg_cost.toFixed(2)}</td>
                                            <td>${pos.total_cost.toFixed(2)}</td>
                                            <td>${pos.currency}</td>
                                        </tr>
                                    `).join('')}
                                </table>
                            `;
                        });
                }

                function refreshTrades() {
                    fetch('/api/trades')
                        .then(response => response.json())
                        .then(data => {
                            const tradesDiv = document.getElementById('trades');
                            tradesDiv.innerHTML = `
                                <table>
                                    <tr><th>时间</th><th>股票</th><th>类型</th><th>数量</th><th>价格</th><th>金额</th><th>备注</th></tr>
                                    ${data.map(trade => `
                                        <tr>
                                            <td>${new Date(trade.trade_date).toLocaleString()}</td>
                                            <td>${trade.stock_name}</td>
                                            <td class="${trade.trade_type === 'buy' ? 'loss' : 'profit'}">${trade.trade_type === 'buy' ? '买入' : '卖出'}</td>
                                            <td>${trade.quantity}</td>
                                            <td>${trade.price.toFixed(2)}</td>
                                            <td>${trade.total_amount.toFixed(2)} ${trade.currency}</td>
                                            <td>${trade.notes || ''}</td>
                                        </tr>
                                    `).join('')}
                                </table>
                            `;
                        });
                }

                function sendReport() {
                    fetch('/api/send_report')
                        .then(response => response.json())
                        .then(data => {
                            alert(data.message);
                        });
                }

                function loadCurrentPrices() {
                    fetch('/api/update_prices')
                        .then(response => response.json())
                        .then(data => {
                            alert(data.message);
                            refreshPnl();
                            refreshPositions();
                        });
                }
            </script>
        </body>
        </html>
    ''')

# API路由
@app.route('/api/trade', methods=['POST'])
def add_trade():
    try:
        data = request.json
        stock_system.add_trade(
            data['stock_name'],
            data['stock_code'], 
            data['trade_type'],
            data['quantity'],
            data['price'],
            data.get('currency', 'HKD'),
            data.get('notes', '')
        )
        return jsonify({'success': True, 'message': '交易记录添加成功'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'交易失败: {str(e)}'})

@app.route('/api/positions')
def get_positions():
    try:
        positions = stock_system.get_positions()
        return jsonify(positions)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/trades')
def get_trades():
    try:
        trades = stock_system.get_trades()
        return jsonify(trades)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/pnl')
def get_pnl():
    try:
        pnl_data = stock_system.calculate_pnl()
        # 转换为人民币显示
        for key in ['total_unrealized_pnl', 'daily_realized_pnl', 'weekly_realized_pnl', 
                   'monthly_realized_pnl', 'daily_total_pnl', 'weekly_total_pnl', 'monthly_total_pnl']:
            pnl_data[key] = pnl_data[key] * HKD_TO_CNY
        return jsonify(pnl_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/send_report')
def send_report():
    try:
        result = stock_system.agent.run_analysis_and_send_email()
        return jsonify({'success': result, 'message': '报告发送成功' if result else '报告发送失败'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'发送失败: {str(e)}'})

@app.route('/api/update_prices')
def update_prices():
    try:
        # 更新价格历史记录
        positions = stock_system.get_positions()
        conn = sqlite3.connect('trading_data.db')
        cursor = conn.cursor()
        
        for pos in positions:
            try:
                ticker = yf.Ticker(pos['stock_code'])
                hist = ticker.history(period='1d')
                if not hist.empty:
                    current_price = hist.iloc[-1]['Close']
                    cursor.execute('''
                        INSERT INTO price_history (stock_name, stock_code, price, currency)
                        VALUES (?, ?, ?, ?)
                    ''', (pos['stock_name'], pos['stock_code'], current_price, pos['currency']))
            except Exception as e:
                print(f"更新价格失败 {pos['stock_name']}: {e}")
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': '价格更新完成'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'})

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)