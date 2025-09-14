#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用雅虎财经数据源的股票投资组合分析系统
功能：实时股价获取、技术分析、邮件发送
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
from dotenv import load_dotenv
import yfinance as yf

# 加载环境变量
load_dotenv()

# 配置
EMAIL_SENDER = os.getenv('EMAIL_SENDER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
EMAIL_RECEIVER = os.getenv('EMAIL_RECEIVER')
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))

class YahooStockAnalyzer:
    def __init__(self):
        self.stocks_data = {
            "腾讯控股": {"code": "0700.HK", "quantity": 300, "avg_cost": 320.85},
            "中芯国际": {"code": "0981.HK", "quantity": 1000, "avg_cost": 47.55},
            "小米集团-W": {"code": "1810.HK", "quantity": 2000, "avg_cost": 47.1071},
            "中国人寿": {"code": "2628.HK", "quantity": 2000, "avg_cost": 23.82},
            "美团-W": {"code": "3690.HK", "quantity": 740, "avg_cost": 123.2508},
            "新东方-S": {"code": "9901.HK", "quantity": 2000, "avg_cost": 44.3241},
            "阿里巴巴-W": {"code": "9988.HK", "quantity": 500, "avg_cost": 113.74}
        }
        
        print("股票分析系统初始化完成（雅虎财经数据源）")
        print(f"包含 {len(self.stocks_data)} 只股票")
    
    def fetch_stock_data_yahoo(self, symbol, period="1mo"):
        """使用雅虎财经获取历史数据"""
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period=period)
            
            if not hist.empty:
                hist.index = pd.to_datetime(hist.index)
                return hist
            else:
                print(f"无法获取{symbol}数据")
                return None
                
        except Exception as e:
            print(f"获取{symbol}数据失败: {e}")
            return None
    
    def fetch_current_price_yahoo(self, symbol):
        """获取当前股价"""
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period="2d")
            
            if not hist.empty and len(hist) > 1:
                return hist['Close'].iloc[-1]
            elif not hist.empty:
                return hist['Close'].iloc[0]
            else:
                return None
                
        except Exception as e:
            print(f"获取{symbol}当前价格失败: {e}")
            return None
    
    def simple_technical_analysis(self, df):
        """简化版技术分析"""
        if len(df) < 20:
            return {}, df
        
        signals = {}
        
        # 计算移动平均线
        df['ma20'] = df['Close'].rolling(window=20).mean()
        df['ma50'] = df['Close'].rolling(window=50).mean()
        
        # 简单RSI计算
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # 布林带
        df['ma20_std'] = df['Close'].rolling(window=20).std()
        df['upper'] = df['ma20'] + (df['ma20_std'] * 2)
        df['lower'] = df['ma20'] - (df['ma20_std'] * 2)
        
        # 生成信号
        if pd.notna(df['ma20'].iloc[-1]) and pd.notna(df['ma50'].iloc[-1]):
            if df['ma20'].iloc[-1] > df['ma50'].iloc[-1]:
                signals['moving_average'] = "BUY"
            else:
                signals['moving_average'] = "SELL"
        
        if pd.notna(df['rsi'].iloc[-1]):
            if df['rsi'].iloc[-1] < 30:
                signals['rsi'] = "BUY"
            elif df['rsi'].iloc[-1] > 70:
                signals['rsi'] = "SELL"
            else:
                signals['rsi'] = "HOLD"
        
        if pd.notna(df['lower'].iloc[-1]) and pd.notna(df['upper'].iloc[-1]):
            if df['Close'].iloc[-1] < df['lower'].iloc[-1]:
                signals['bollinger_bands'] = "BUY"
            elif df['Close'].iloc[-1] > df['upper'].iloc[-1]:
                signals['bollinger_bands'] = "SELL"
            else:
                signals['bollinger_bands'] = "HOLD"
        
        return signals, df
    
    def get_simple_sentiment(self, stock_name, stock_code):
        """简化版情绪分析"""
        # 模拟情绪分析，实际应用中可以接入真实的社交媒体数据
        sentiment = "中性"
        
        # 基于价格变化的简单情绪判断
        return sentiment, []
    
    def create_simple_chart(self, df, symbol):
        """创建简化版图表"""
        fig, axes = plt.subplots(2, 1, figsize=(12, 8))
        fig.suptitle(f'{symbol} Technical Analysis', fontsize=16)
        
        # 价格和移动平均线
        axes[0].plot(df.index, df['Close'], label='Close Price', color='black', linewidth=1)
        if 'ma20' in df.columns and not df['ma20'].isna().all():
            axes[0].plot(df.index, df['ma20'], label='MA20', color='blue', linewidth=1)
        if 'ma50' in df.columns and not df['ma50'].isna().all():
            axes[0].plot(df.index, df['ma50'], label='MA50', color='red', linewidth=1)
        if 'upper' in df.columns and 'lower' in df.columns and not df['upper'].isna().all():
            axes[0].fill_between(df.index, df['lower'], df['upper'], color='gray', alpha=0.2)
        axes[0].set_title('Price with Moving Averages and Bollinger Bands')
        axes[0].legend()
        axes[0].grid(True)
        
        # RSI
        if 'rsi' in df.columns and not df['rsi'].isna().all():
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
        success_count = 0
        for stock_name, data in self.stocks_data.items():
            current_price = self.fetch_current_price_yahoo(data["code"])
            if current_price:
                data["current_price"] = current_price
                data["market_value"] = current_price * data["quantity"]
                data["pnl"] = data["market_value"] - (data["avg_cost"] * data["quantity"])
                data["change_pct"] = ((current_price - data["avg_cost"]) / data["avg_cost"]) * 100
                print(f"✅ {stock_name}: {current_price:.2f} HKD")
                success_count += 1
            else:
                print(f"❌ 无法获取{stock_name}价格")
                data["current_price"] = 0
                data["market_value"] = 0
                data["pnl"] = 0
                data["change_pct"] = 0
        
        print(f"成功获取 {success_count}/{len(self.stocks_data)} 只股票价格")
        
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
            if data["current_price"] == 0:
                continue
                
            print(f"\n分析{stock_name}...")
            
            # 获取历史数据
            hist_data = self.fetch_stock_data_yahoo(data["code"])
            
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
                support = recent_data['Low'].min()
                resistance = recent_data['High'].max()
                
                # 情绪分析
                sentiment, high_quality_posts = self.get_simple_sentiment(stock_name, data["code"])
                
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
                    "市场情绪": sentiment,
                    "建议操作": recommendation
                }
                
                analysis_results.append(analysis_result)
                
                print(f"✅ 技术分析完成 - {stock_name}")
                print(f"   当前价格: {data['current_price']:.2f} HKD")
                print(f"   支撑位: {support:.2f}, 阻力位: {resistance:.2f}")
                print(f"   建议操作: {recommendation}")
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
        email_subject = f"📊 股票投资组合分析报告 - {datetime.now().strftime('%Y-%m-%d')}"
        
        total_market_value = portfolio_df['市值'].sum()
        total_pnl = portfolio_df['浮动盈亏'].sum()
        total_cost = total_market_value - total_pnl
        total_return_pct = (total_pnl / total_cost * 100) if total_cost > 0 else 0
        
        email_content = f"""
🔥 股票投资组合分析报告 🔥
⏰ 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

==========================
📈 投资组合概览
==========================
💰 总市值: {total_market_value:,.2f} HKD
📊 总浮动盈亏: {total_pnl:,.2f} HKD
📈 总收益率: {total_return_pct:.2f}%
📊 分析股票数: {len(analysis_results)} 只

==========================
📋 详细持仓信息
==========================
{portfolio_df.to_string(index=False)}

"""
        
        if not analysis_df.empty:
            email_content += f"""
==========================
🔍 技术分析摘要
==========================
{analysis_df.to_string(index=False)}

"""
        
        # 交易建议
        email_content += """
==========================
💡 交易建议
==========================
"""
        if analysis_results:
            for result in analysis_results:
                if result["建议操作"] != "持有":
                    email_content += f"""
📌 {result['股票名称']} ({result['代码']}): 
   🎯 建议{result['建议操作']}
   💵 当前价格: {result['当前价格']:.2f} HKD
   📉 支撑位: {result['支撑位']:.2f} HKD
   📈 阻力位: {result['阻力位']:.2f} HKD
   😊 市场情绪: {result['市场情绪']}
"""
                    email_content += "-" * 50 + "\n"
        else:
            email_content += "\n📝 暂无具体交易建议，请关注市场变化。\n"
        
        email_content += f"""
==========================
🤖 系统信息
==========================
📧 本邮件由自动化股票分析系统生成
🔧 数据源: 雅虎财经 (Yahoo Finance)
📊 分析方法: 技术分析 (MA, RSI, 布林带)
📱 如有问题请联系系统管理员

==========================
⚠️ 免责声明
==========================
本分析仅供参考，不构成投资建议。
投资有风险，决策需谨慎。
"""
        
        # 发送邮件
        email_attachments = {}
        for code, chart_path in charts.items():
            email_attachments[f"{code}_chart.png"] = chart_path
        email_attachments["portfolio_analysis.xlsx"] = excel_filename
        
        email_sent = self.send_email(email_subject, email_content, email_attachments)
        
        print("\n" + "="*60)
        print("🎉 分析完成！")
        print(f"📊 投资组合数据已保存到: {excel_filename}")
        print(f"📧 邮件发送状态: {'✅ 成功' if email_sent else '❌ 失败'}")
        print(f"📈 共分析了 {len(analysis_results)} 只股票")
        print("="*60)
        
        return analysis_results

def main():
    """主函数"""
    print("🚀 股票投资组合分析系统 (雅虎财经版)")
    print("=" * 60)
    
    analyzer = YahooStockAnalyzer()
    
    try:
        results = analyzer.analyze_portfolio()
        print(f"\n✅ 分析完成，共分析了 {len(results)} 只股票")
        
        if len(results) == 0:
            print("⚠️ 警告: 未能获取任何股票数据，请检查网络连接和股票代码")
        
    except Exception as e:
        print(f"❌ 分析过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()