#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版股票投资组合分析器
功能：获取当前股价，计算盈亏，生成分析报告
"""

import pandas as pd
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import time
import json
import os
from datetime import datetime, timedelta
import numpy as np
from bs4 import BeautifulSoup
import warnings
warnings.filterwarnings('ignore')

class SimpleStockAnalyzer:
    def __init__(self):
        self.stocks_data = {
            "腾讯控股": {"code": "00700.HK", "quantity": 300, "avg_cost": 320.85},
            "中芯国际": {"code": "00981.HK", "quantity": 1000, "avg_cost": 47.55},
            "小米集团-W": {"code": "01810.HK", "quantity": 2000, "avg_cost": 47.1071},
            "中国人寿": {"code": "02628.HK", "quantity": 2000, "avg_cost": 23.82},
            "美团-W": {"code": "03690.HK", "quantity": 740, "avg_cost": 123.2508},
            "新东方-S": {"code": "09901.HK", "quantity": 2000, "avg_cost": 44.3241},
            "阿里巴巴-W": {"code": "09988.HK", "quantity": 500, "avg_cost": 113.74}
        }
        
        # 邮件配置（请修改为实际配置）
        self.email_config = {
            "smtp_server": "smtp.163.com",
            "smtp_port": 465,
            "sender_email": "your_email@163.com",  # 发件人邮箱
            "sender_password": "your_password",    # 发件人密码或授权码
            "recipient_email": "zhangbin19850523@163.com"
        }
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def get_stock_price_yahoo(self, symbol):
        """从Yahoo Finance获取股价"""
        try:
            # 转换符号格式
            if symbol.endswith(".HK"):
                yahoo_symbol = symbol.replace(".HK", "") + ".HK"
            else:
                yahoo_symbol = symbol
            
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{yahoo_symbol}"
            params = {
                'interval': '1m',
                'range': '1d',
                'includePrePost': 'true'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            chart = data.get('chart', {})
            result = chart.get('result', [])
            
            if result and 'meta' in result[0]:
                current_price = result[0]['meta'].get('regularMarketPrice')
                if current_price:
                    return float(current_price)
                
                # 尝试获取前一天收盘价
                prev_close = result[0]['meta'].get('previousClose')
                if prev_close:
                    return float(prev_close)
            
            return None
            
        except Exception as e:
            print(f"获取 {symbol} 价格失败: {e}")
            return None
    
    def get_stock_price_qq(self, symbol):
        """从腾讯股票获取港股价格"""
        try:
            # 转换为腾讯股票代码格式
            if symbol.endswith(".HK"):
                hk_code = symbol.replace(".HK", "")
                url = f"https://qt.gtimg.cn/q=hk{hk_code}"
            else:
                url = f"https://qt.gtimg.cn/q={symbol}"
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # 解析返回数据
            content = response.text
            if '="' in content and '"~' in content:
                data_str = content.split('="')[1].split('"~')[0]
                fields = data_str.split('~')
                
                if len(fields) > 3:
                    try:
                        current_price = float(fields[3])  # 当前价格
                        if current_price > 0:
                            return current_price
                    except (ValueError, IndexError):
                        pass
            
            return None
            
        except Exception as e:
            print(f"从腾讯获取 {symbol} 价格失败: {e}")
            return None
    
    def get_stock_price_eastmoney(self, symbol):
        """从东方财富获取港股价格"""
        try:
            if symbol.endswith(".HK"):
                hk_code = symbol.replace(".HK", "")
                url = f"https://push2.eastmoney.com/api/qt/stock/kline/get?secid=1.{hk_code}&fields1=f1,f2,f3,f4&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61&klt=101&lmt=1"
            else:
                return None
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get('data') and data['data'].get('klines'):
                kline = data['data']['klines'][0]
                fields = kline.split(',')
                if len(fields) > 3:
                    return float(fields[2])  # 收盘价
            
            return None
            
        except Exception as e:
            print(f"从东方财富获取 {symbol} 价格失败: {e}")
            return None
    
    def get_current_price(self, symbol):
        """获取当前股价（多数据源）"""
        # 依次尝试不同数据源
        sources = [
            self.get_stock_price_yahoo,
            self.get_stock_price_qq,
            self.get_stock_price_eastmoney
        ]
        
        for source_func in sources:
            price = source_func(symbol)
            if price and price > 0:
                return price
        
        return None
    
    def calculate_simple_technical_signals(self, current_price, avg_cost):
        """简单技术分析信号"""
        signals = []
        
        # 基于成本价分析
        price_change_pct = ((current_price - avg_cost) / avg_cost) * 100
        
        if price_change_pct > 20:
            signals.append("大幅盈利")
        elif price_change_pct > 10:
            signals.append("盈利")
        elif price_change_pct > 5:
            signals.append("小幅盈利")
        elif price_change_pct < -20:
            signals.append("大幅亏损")
        elif price_change_pct < -10:
            signals.append("亏损")
        elif price_change_pct < -5:
            signals.append("小幅亏损")
        else:
            signals.append("持平")
        
        # 生成建议
        if price_change_pct > 15:
            recommendation = "考虑减仓"
        elif price_change_pct > 5:
            recommendation = "持有"
        elif price_change_pct < -15:
            recommendation = "考虑补仓"
        elif price_change_pct < -5:
            recommendation = "持有观望"
        else:
            recommendation = "持有"
        
        return signals, recommendation
    
    def analyze_portfolio(self):
        """分析投资组合"""
        print("开始分析投资组合...")
        
        # 获取当前价格
        print("获取最新股价...")
        for stock_name, data in self.stocks_data.items():
            print(f"正在获取 {stock_name} 的价格...")
            current_price = self.get_current_price(data["code"])
            
            if current_price:
                data["current_price"] = current_price
                data["market_value"] = current_price * data["quantity"]
                data["pnl"] = data["market_value"] - (data["avg_cost"] * data["quantity"])
                data["change_pct"] = ((current_price - data["avg_cost"]) / data["avg_cost"]) * 100
                
                print(f"✓ {stock_name}: ¥{current_price:.2f} (盈亏: ¥{data['pnl']:,.2f})")
            else:
                print(f"✗ 无法获取 {stock_name} 的价格")
                data["current_price"] = 0
                data["market_value"] = 0
                data["pnl"] = 0
                data["change_pct"] = 0
        
        # 创建投资组合表格
        portfolio_df = pd.DataFrame.from_dict(self.stocks_data, orient='index')
        portfolio_df = portfolio_df.reset_index().rename(columns={'index': '股票名称'})
        
        # 重新排列列
        portfolio_df = portfolio_df[['股票名称', 'code', 'quantity', 'current_price', 'avg_cost', 'market_value', 'pnl', 'change_pct']]
        portfolio_df.columns = ['股票名称', '代码', '数量', '现价', '摊薄成本价', '市值', '浮动盈亏', '涨跌幅']
        
        # 计算总体统计
        total_market_value = portfolio_df['市值'].sum()
        total_cost = portfolio_df['数量'].mul(portfolio_df['摊薄成本价']).sum()
        total_pnl = portfolio_df['浮动盈亏'].sum()
        total_pnl_pct = (total_pnl / total_cost) * 100
        
        # 生成技术分析
        analysis_results = []
        for _, row in portfolio_df.iterrows():
            signals, recommendation = self.calculate_simple_technical_signals(
                row['现价'], row['摊薄成本价']
            )
            
            analysis_results.append({
                '股票名称': row['股票名称'],
                '代码': row['代码'],
                '当前价格': row['现价'],
                '涨跌幅': row['涨跌幅'],
                '技术信号': ', '.join(signals),
                '建议操作': recommendation
            })
        
        analysis_df = pd.DataFrame(analysis_results)
        
        # 保存到Excel
        os.makedirs('output', exist_ok=True)
        excel_filename = f"output/stock_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        with pd.ExcelWriter(excel_filename) as writer:
            portfolio_df.to_excel(writer, sheet_name='持仓明细', index=False)
            analysis_df.to_excel(writer, sheet_name='技术分析', index=False)
        
        # 生成报告
        report = self.generate_report(portfolio_df, analysis_df, total_market_value, total_pnl, total_pnl_pct)
        
        # 保存报告
        report_filename = f"output/stock_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n分析完成！")
        print(f"数据已保存到: {excel_filename}")
        print(f"报告已保存到: {report_filename}")
        
        return portfolio_df, analysis_df, report, excel_filename
    
    def generate_report(self, portfolio_df, analysis_df, total_market_value, total_pnl, total_pnl_pct):
        """生成分析报告"""
        report = f"""
{'='*60}
股票投资组合分析报告
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*60}

📊 投资组合总览
{'-'*40}
总市值: ¥{total_market_value:,.2f}
总成本: ¥{total_market_value - total_pnl:,.2f}
总浮动盈亏: ¥{total_pnl:,.2f}
总收益率: {total_pnl_pct:.2f}%

📈 持仓明细表格
{'-'*40}
{portfolio_df.to_string(index=False, float_format='%.2f')}

🔍 技术分析摘要
{'-'*40}
{analysis_df.to_string(index=False, float_format='%.2f')}

💡 操作建议总结
{'-'*40}
"""
        
        # 添加操作建议
        buy_recommendations = analysis_df[analysis_df['建议操作'].str.contains('买|补', na=False)]
        sell_recommendations = analysis_df[analysis_df['建议操作'].str.contains('卖|减', na=False)]
        hold_recommendations = analysis_df[analysis_df['建议操作'] == '持有']
        
        if not buy_recommendations.empty:
            report += f"\n建议买入/补仓:\n"
            for _, row in buy_recommendations.iterrows():
                report += f"- {row['股票名称']} ({row['代码']}): 当前价 ¥{row['当前价格']:.2f}, {row['技术信号']}\n"
        
        if not sell_recommendations.empty:
            report += f"\n建议减仓:\n"
            for _, row in sell_recommendations.iterrows():
                report += f"- {row['股票名称']} ({row['代码']}): 当前价 ¥{row['当前价格']:.2f}, {row['技术信号']}\n"
        
        if not hold_recommendations.empty:
            report += f"\n建议持有:\n"
            for _, row in hold_recommendations.iterrows():
                report += f"- {row['股票名称']} ({row['代码']}): 当前价 ¥{row['当前价格']:.2f}, {row['技术信号']}\n"
        
        report += f"""
{'='*60}
风险提示: 
1. 以上分析仅供参考，不构成投资建议
2. 股市有风险，投资需谨慎
3. 请根据个人风险承受能力做出投资决策
{'='*60}
"""
        
        return report
    
    def send_email_report(self, report_content, excel_filename):
        """发送邮件报告"""
        try:
            if not all([self.email_config['sender_email'], self.email_config['sender_password']]):
                print("邮件配置不完整，跳过邮件发送")
                return False
            
            msg = MIMEMultipart()
            msg['From'] = self.email_config['sender_email']
            msg['To'] = self.email_config['recipient_email']
            msg['Subject'] = f"股票投资组合分析报告 - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            # 添加正文
            msg.attach(MIMEText(report_content, 'plain', 'utf-8'))
            
            # 添加Excel附件
            with open(excel_filename, 'rb') as f:
                part = MIMEApplication(f.read())
                part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(excel_filename))
                msg.attach(part)
            
            # 发送邮件
            with smtplib.SMTP_SSL(self.email_config['smtp_server'], self.email_config['smtp_port']) as server:
                server.login(self.email_config['sender_email'], self.email_config['sender_password'])
                server.send_message(msg)
            
            print(f"邮件已发送至 {self.email_config['recipient_email']}")
            return True
            
        except Exception as e:
            print(f"邮件发送失败: {e}")
            return False
    
    def run_analysis(self, send_email=True):
        """运行完整分析"""
        try:
            portfolio_df, analysis_df, report, excel_filename = self.analyze_portfolio()
            
            if send_email:
                self.send_email_report(report, excel_filename)
            
            return {
                'portfolio_df': portfolio_df,
                'analysis_df': analysis_df,
                'report': report,
                'excel_filename': excel_filename
            }
            
        except Exception as e:
            print(f"分析过程中出错: {e}")
            return None

if __name__ == "__main__":
    analyzer = SimpleStockAnalyzer()
    
    # 可以选择是否发送邮件（需要配置邮件信息）
    print("股票投资组合分析器")
    print("=" * 50)
    
    send_email_choice = input("是否发送邮件报告？(y/n): ").lower().strip()
    send_email = send_email_choice == 'y'
    
    if send_email:
        print("\n请配置邮件信息:")
        analyzer.email_config['sender_email'] = input("发件人邮箱: ")
        analyzer.email_config['sender_password'] = input("邮箱密码/授权码: ")
    
    print("\n开始分析...")
    results = analyzer.run_analysis(send_email=send_email)
    
    if results:
        print("\n" + "="*50)
        print("分析摘要:")
        print(f"总盈亏: ¥{results['portfolio_df']['浮动盈亏'].sum():,.2f}")
        print(f"总收益率: {(results['portfolio_df']['浮动盈亏'].sum() / (results['portfolio_df']['市值'].sum() - results['portfolio_df']['浮动盈亏'].sum())) * 100:.2f}%")
        
        # 显示盈利和亏损股票
        profit_stocks = results['portfolio_df'][results['portfolio_df']['浮动盈亏'] > 0]
        loss_stocks = results['portfolio_df'][results['portfolio_df']['浮动盈亏'] < 0]
        
        print(f"\n盈利股票 ({len(profit_stocks)}只):")
        for _, row in profit_stocks.iterrows():
            print(f"  {row['股票名称']}: +¥{row['浮动盈亏']:,.2f} (+{row['涨跌幅']:.2f}%)")
        
        print(f"\n亏损股票 ({len(loss_stocks)}只):")
        for _, row in loss_stocks.iterrows():
            print(f"  {row['股票名称']}: -¥{abs(row['浮动盈亏']):,.2f} ({row['涨跌幅']:.2f}%)")
    else:
        print("分析失败！")