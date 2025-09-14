#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版股票投资组合分析系统
功能：实时股价获取、基础技术分析、雪球情绪分析、自动邮件发送
"""

import pandas as pd
import requests
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
import numpy as np
import time
import json
import os
from datetime import datetime, timedelta
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import schedule
import threading
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')
EMAIL_SENDER = os.getenv('EMAIL_SENDER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
EMAIL_RECEIVER = os.getenv('EMAIL_RECEIVER')
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))

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
        
        print("股票分析系统初始化完成")
        print(f"包含 {len(self.stocks_data)} 只股票")
    
    def fetch_stock_data(self, symbol, max_retries=3):
        """获取历史股票数据"""
        for attempt in range(max_retries):
            try:
                url = f"https://www.alphavantage.co/query"
                params = {
                    "function": "TIME_SERIES_DAILY",
                    "symbol": symbol,
                    "outputsize": "compact",
                    "apikey": ALPHA_VANTAGE_API_KEY
                }
                
                response = requests.get(url, params=params, timeout=30)
                data = response.json()
                
                if "Time Series (Daily)" in data:
                    df = pd.DataFrame(data["Time Series (Daily)"]).T
                    df.index = pd.to_datetime(df.index)
                    df = df.astype(float)
                    df.columns = [col.split('. ')[1] for col in df.columns]
                    return df
                elif "Note" in data:
                    print(f"API限制，等待60秒...")
                    time.sleep(60)
                    continue
                else:
                    print(f"获取{symbol}数据失败: {data}")
                    return None
                    
            except Exception as e:
                print(f"第{attempt + 1}次尝试获取{symbol}失败: {e}")
                if attempt < max_retries - 1:
                    time.sleep(5)
                continue
        
        return None
    
    def fetch_current_price(self, symbol):
        """获取当前股价"""
        df = self.fetch_stock_data(symbol)
        if df is not None and not df.empty:
            return df['close'].iloc[-1]
        return None
    
    def simple_technical_analysis(self, df):
        """简化版技术分析"""
        if len(df) < 20:
            return {}, df
        
        signals = {}
        
        # 计算移动平均线
        df['ma20'] = df['close'].rolling(window=20).mean()
        df['ma50'] = df['close'].rolling(window=50).mean()
        
        # 简单RSI计算
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # 布林带
        df['ma20_std'] = df['close'].rolling(window=20).std()
        df['upper'] = df['ma20'] + (df['ma20_std'] * 2)
        df['lower'] = df['ma20'] - (df['ma20_std'] * 2)
        
        # 生成信号
        if df['ma20'].iloc[-1] > df['ma50'].iloc[-1]:
            signals['moving_average'] = "BUY"
        else:
            signals['moving_average'] = "SELL"
        
        if df['rsi'].iloc[-1] < 30:
            signals['rsi'] = "BUY"
        elif df['rsi'].iloc[-1] > 70:
            signals['rsi'] = "SELL"
        else:
            signals['rsi'] = "HOLD"
        
        if df['close'].iloc[-1] < df['lower'].iloc[-1]:
            signals['bollinger_bands'] = "BUY"
        elif df['close'].iloc[-1] > df['upper'].iloc[-1]:
            signals['bollinger_bands'] = "SELL"
        else:
            signals['bollinger_bands'] = "HOLD"
        
        return signals, df
    
    def get_xueqiu_sentiment_simple(self, stock_name, stock_code):
        """简化版雪球情绪分析"""
        sentiment = "中性"
        high_quality_posts = []
        
        try:
            # 使用简单的网页请求获取雪球数据
            search_url = f"https://xueqiu.com/search?q={stock_code}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(search_url, headers=headers, timeout=10)
            if response.status_code == 200:
                # 简单的关键词搜索
                content = response.text.lower()
                positive_count = content.count('买') + content.count('涨') + content.count('好')
                negative_count = content.count('卖') + content.count('跌') + content.count('差')
                
                if positive_count > negative_count * 1.5:
                    sentiment = "积极"
                elif negative_count > positive_count * 1.5:
                    sentiment = "消极"
                else:
                    sentiment = "中性"
                    
        except Exception as e:
            print(f"雪球数据获取失败: {e}")
        
        return sentiment, high_quality_posts
    
    def create_simple_chart(self, df, symbol):
        """创建简化版图表"""
        fig, axes = plt.subplots(2, 1, figsize=(12, 8))
        fig.suptitle(f'{symbol} Technical Analysis', fontsize=16)
        
        # 价格和移动平均线
        axes[0].plot(df.index, df['close'], label='Close Price', color='black', linewidth=1)
        if 'ma20' in df.columns:
            axes[0].plot(df.index, df['ma20'], label='MA20', color='blue', linewidth=1)
        if 'ma50' in df.columns:
            axes[0].plot(df.index, df['ma50'], label='MA50', color='red', linewidth=1)
        if 'upper' in df.columns and 'lower' in df.columns:
            axes[0].fill_between(df.index, df['lower'], df['upper'], color='gray', alpha=0.2)
        axes[0].set_title('Price with Moving Averages and Bollinger Bands')
        axes[0].legend()
        axes[0].grid(True)
        
        # RSI
        if 'rsi' in df.columns:
            axes[1].plot(df.index, df['rsi'], label='RSI', color='purple')
            axes[1].axhline(70, color='red', linestyle='--')
            axes[1].axhline(30, color='green', linestyle='--')
            axes[1].set_title('Relative Strength Index (RSI)')
            axes[1].set_ylim(0, 100)
            axes[1].grid(True)
        
        plt.tight_layout()
        
        # 保存图表
        os.makedirs('output_charts', exist_ok=True)
        chart_filename = f"output_charts/{symbol}_chart.png"
        plt.savefig(chart_filename)
        plt.close()
        
        return chart_filename
    
    def send_email(self, subject, content, attachments=None):
        """发送邮件"""
        if not all([EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECEIVER]):
            print("邮件配置不完整，跳过发送邮件")
            print(f"当前配置: 发件人={EMAIL_SENDER}, 收件人={EMAIL_RECEIVER}")
            return False
        
        msg = MIMEMultipart()
        msg['From'] = EMAIL_SENDER
        msg['To'] = EMAIL_RECEIVER
        msg['Subject'] = subject
        
        msg.attach(MIMEText(content, 'plain', 'utf-8'))
        
        if attachments:
            for filename, file_path in attachments.items():
                try:
                    with open(file_path, 'rb') as f:
                        if filename.endswith('.png'):
                            part = MIMEImage(f.read())
                        else:
                            part = MIMEApplication(f.read())
                        part.add_header('Content-Disposition', 'attachment', filename=filename)
                        msg.attach(part)
                except Exception as e:
                    print(f"添加附件{filename}失败: {e}")
        
        try:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            text = msg.as_string()
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, text)
            server.quit()
            print("邮件发送成功")
            return True
        except Exception as e:
            print(f"邮件发送失败: {e}")
            return False
    
    def generate_signals_summary(self, signals):
        """生成信号摘要"""
        buy_signals = [indicator for indicator, signal in signals.items() if signal == "BUY"]
        sell_signals = [indicator for indicator, signal in signals.items() if signal == "SELL"]
        
        summary = "技术信号分析:\n"
        if buy_signals:
            summary += f"买入信号: {', '.join(buy_signals)}\n"
        if sell_signals:
            summary += f"卖出信号: {', '.join(sell_signals)}\n"
        if not buy_signals and not sell_signals:
            summary += "当前无明显买卖信号，建议持有观望\n"
        
        return summary
    
    def analyze_portfolio(self):
        """分析整个投资组合"""
        print("开始分析投资组合...")
        
        # 获取当前价格
        print("获取当前价格...")
        for stock_name, data in self.stocks_data.items():
            current_price = self.fetch_current_price(data["code"])
            if current_price:
                data["current_price"] = current_price
                data["market_value"] = current_price * data["quantity"]
                data["pnl"] = data["market_value"] - (data["avg_cost"] * data["quantity"])
                data["change_pct"] = ((current_price - data["avg_cost"]) / data["avg_cost"]) * 100
                print(f"{stock_name}: {current_price:.2f}")
            else:
                print(f"无法获取{stock_name}价格，使用上次已知价格")
                data["current_price"] = data.get("current_price", 0)
                data["market_value"] = data["current_price"] * data["quantity"]
                data["pnl"] = data["market_value"] - (data["avg_cost"] * data["quantity"])
                data["change_pct"] = ((data["current_price"] - data["avg_cost"]) / data["avg_cost"]) * 100
        
        # 创建投资组合表格
        portfolio_df = pd.DataFrame.from_dict(self.stocks_data, orient='index')
        portfolio_df = portfolio_df.reset_index().rename(columns={'index': '股票名称'})
        portfolio_df = portfolio_df[['股票名称', 'code', 'market_value', 'quantity', 'current_price', 'avg_cost', 'pnl', 'change_pct']]
        portfolio_df.columns = ['股票名称', '代码', '市值', '数量', '现价', '摊薄成本价', '浮动盈亏', '涨跌幅']
        
        # 保存到Excel
        os.makedirs('output', exist_ok=True)
        excel_filename = "output/stock_portfolio_analysis.xlsx"
        with pd.ExcelWriter(excel_filename) as writer:
            portfolio_df.to_excel(writer, sheet_name='Portfolio Summary', index=False)
        
        # 分析每个股票
        analysis_results = []
        charts = {}
        
        for stock_name, data in self.stocks_data.items():
            print(f"\n分析{stock_name}...")
            
            # 获取历史数据
            hist_data = self.fetch_stock_data(data["code"])
            
            if hist_data is not None and len(hist_data) > 20:
                # 执行技术分析
                signals, hist_data_with_indicators = self.simple_technical_analysis(hist_data)
                
                # 创建图表
                chart_filename = self.create_simple_chart(hist_data_with_indicators, data["code"])
                charts[data["code"]] = chart_filename
                
                # 生成信号摘要
                signals_summary = self.generate_signals_summary(signals)
                
                # 支撑/阻力位
                recent_data = hist_data.tail(20)
                support = recent_data['low'].min()
                resistance = recent_data['high'].max()
                
                # 雪球情绪分析
                sentiment, high_quality_posts = self.get_xueqiu_sentiment_simple(stock_name, data["code"])
                
                # 生成建议
                buy_signals = sum(1 for signal in signals.values() if signal == "BUY")
                sell_signals = sum(1 for signal in signals.values() if signal == "SELL")
                
                if buy_signals > sell_signals:
                    recommendation = "买入"
                elif sell_signals > buy_signals:
                    recommendation = "卖出"
                else:
                    recommendation = "持有"
                
                analysis_result = {
                    "股票名称": stock_name,
                    "代码": data["code"],
                    "当前价格": data["current_price"],
                    "支撑位": support,
                    "阻力位": resistance,
                    "技术信号摘要": signals_summary,
                    "雪球情绪": sentiment,
                    "建议操作": recommendation
                }
                
                analysis_results.append(analysis_result)
                
                print(f"技术分析完成 - {stock_name}")
                print(f"当前价格: {data['current_price']:.2f}")
                print(f"支撑位: {support:.2f}, 阻力位: {resistance:.2f}")
                print(f"雪球情绪: {sentiment}")
                print(f"建议操作: {recommendation}")
                print("-" * 50)
        
        # 创建分析表格
        if analysis_results:
            analysis_df = pd.DataFrame(analysis_results)
            
            # 保存分析到Excel
            with pd.ExcelWriter(excel_filename, mode='a') as writer:
                analysis_df.to_excel(writer, sheet_name='Technical Analysis', index=False)
        else:
            analysis_df = pd.DataFrame()
        
        # 准备邮件内容
        email_subject = f"股票投资组合分析报告 - {datetime.now().strftime('%Y-%m-%d')}"
        
        email_content = f"""
股票投资组合分析报告
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

==============
投资组合概览
==============

总市值: {portfolio_df['市值'].sum():,.2f}
总浮动盈亏: {portfolio_df['浮动盈亏'].sum():,.2f}
盈亏比例: {((portfolio_df['浮动盈亏'].sum() / (portfolio_df['市值'].sum() - portfolio_df['浮动盈亏'].sum())) * 100):.2f}%

==============
详细持仓信息
==============
{portfolio_df.to_string(index=False)}

"""
        
        if not analysis_df.empty:
            email_content += f"""
==============
技术分析摘要
==============
{analysis_df.to_string(index=False)}

"""
        
        # 交易建议
        email_content += """
==============
交易建议
==============
"""
        if analysis_results:
            for result in analysis_results:
                if result["建议操作"] != "持有":
                    email_content += f"\n{result['股票名称']} ({result['代码']}): 建议{result['建议操作']}\n"
                    email_content += f"当前价格: {result['当前价格']:.2f}\n"
                    email_content += f"支撑位: {result['支撑位']:.2f}, 阻力位: {result['阻力位']:.2f}\n"
                    email_content += f"雪球情绪: {result['雪球情绪']}\n"
                    email_content += "-" * 50 + "\n"
        else:
            email_content += "\n暂无具体交易建议，请关注市场变化。\n"
        
        # 发送邮件
        email_attachments = {}
        for code, chart_path in charts.items():
            email_attachments[f"{code}_chart.png"] = chart_path
        email_attachments["portfolio_analysis.xlsx"] = excel_filename
        
        self.send_email(email_subject, email_content, email_attachments)
        
        print("\n分析完成！")
        print(f"投资组合数据已保存到 {excel_filename}")
        
        return analysis_results

def main():
    """主函数"""
    print("股票投资组合分析系统")
    print("=" * 50)
    
    analyzer = SimpleStockAnalyzer()
    
    try:
        results = analyzer.analyze_portfolio()
        print(f"\n分析完成，共分析了 {len(results)} 只股票")
    except Exception as e:
        print(f"分析过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()