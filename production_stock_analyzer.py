#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生产环境股票分析系统
Production Stock Analysis System
功能：每天10:00和16:00自动分析股票并发送Gmail邮件
"""

import pandas as pd
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import time
import os
import schedule
import threading
import logging
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/stock_analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ProductionStockAnalyzer:
    def __init__(self):
        # 投资组合数据
        self.stocks_data = {
            "腾讯控股": {"code": "00700.HK", "quantity": 300, "avg_cost": 320.85},
            "中芯国际": {"code": "00981.HK", "quantity": 1000, "avg_cost": 47.55},
            "小米集团-W": {"code": "01810.HK", "quantity": 2000, "avg_cost": 47.1071},
            "中国人寿": {"code": "02628.HK", "quantity": 2000, "avg_cost": 23.82},
            "美团-W": {"code": "03690.HK", "quantity": 740, "avg_cost": 123.2508},
            "新东方-S": {"code": "09901.HK", "quantity": 2000, "avg_cost": 44.3241},
            "阿里巴巴-W": {"code": "09988.HK", "quantity": 500, "avg_cost": 113.74}
        }
        
        # Gmail配置
        self.gmail_config = {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "sender_email": "zbin523@gmail.com",
            "sender_password": "sfnd dyld nznx xkbz",
            "recipient_email": "zhangbin19850523@163.com"
        }
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # 创建必要目录
        os.makedirs('logs', exist_ok=True)
        os.makedirs('reports', exist_ok=True)
        
        logger.info("生产环境股票分析系统初始化完成")
    
    def get_stock_price(self, symbol):
        """获取当前股价"""
        try:
            # 使用腾讯股票API
            if symbol.endswith(".HK"):
                hk_code = symbol.replace(".HK", "")
                url = f"https://qt.gtimg.cn/q=hk{hk_code}"
                
                response = self.session.get(url, timeout=10)
                content = response.text
                
                if '="' in content and '"~' in content:
                    data_str = content.split('="')[1].split('"~')[0]
                    fields = data_str.split('~')
                    
                    if len(fields) > 3:
                        try:
                            current_price = float(fields[3])
                            if current_price > 0:
                                return current_price
                        except (ValueError, IndexError):
                            pass
            
            # 如果腾讯失败，使用Yahoo Finance
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
                
                prev_close = result[0]['meta'].get('previousClose')
                if prev_close:
                    return float(prev_close)
            
            return None
            
        except Exception as e:
            logger.error(f"获取 {symbol} 价格失败: {e}")
            return None
    
    def calculate_signals(self, current_price, avg_cost, stock_name):
        """计算技术信号"""
        signals = []
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
        logger.info("开始分析投资组合...")
        
        for stock_name, data in self.stocks_data.items():
            current_price = self.get_stock_price(data["code"])
            
            if current_price:
                data["current_price"] = current_price
                data["market_value"] = current_price * data["quantity"]
                data["pnl"] = data["market_value"] - (data["avg_cost"] * data["quantity"])
                data["change_pct"] = ((current_price - data["avg_cost"]) / data["avg_cost"]) * 100
                
                logger.info(f"{stock_name}: ¥{current_price:.2f} (盈亏: ¥{data['pnl']:,.2f})")
            else:
                logger.warning(f"无法获取 {stock_name} 的价格，使用上次价格")
                # 如果获取失败，使用一个默认值或跳过
                data["current_price"] = 0
                data["market_value"] = 0
                data["pnl"] = 0
                data["change_pct"] = 0
        
        # 创建表格
        portfolio_df = pd.DataFrame.from_dict(self.stocks_data, orient='index')
        portfolio_df = portfolio_df.reset_index().rename(columns={'index': '股票名称'})
        portfolio_df = portfolio_df[['股票名称', 'code', 'quantity', 'current_price', 'avg_cost', 'market_value', 'pnl', 'change_pct']]
        portfolio_df.columns = ['股票名称', '代码', '数量', '现价', '摊薄成本价', '市值', '浮动盈亏', '涨跌幅']
        
        # 计算总体统计
        total_market_value = portfolio_df['市值'].sum()
        total_cost = portfolio_df['数量'].mul(portfolio_df['摊薄成本价']).sum()
        total_pnl = portfolio_df['浮动盈亏'].sum()
        total_pnl_pct = (total_pnl / total_cost) * 100 if total_cost > 0 else 0
        
        # 生成技术分析
        analysis_results = []
        for _, row in portfolio_df.iterrows():
            signals, recommendation = self.calculate_signals(
                row['现价'], row['摊薄成本价'], row['股票名称']
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
        
        return portfolio_df, analysis_df, total_market_value, total_pnl, total_pnl_pct
    
    def generate_report(self, portfolio_df, analysis_df, total_market_value, total_pnl, total_pnl_pct):
        """生成分析报告"""
        report_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        report = f"""
📊 股票投资组合分析报告
生成时间: {report_time}

{'='*60}

💰 投资组合总览
{'-'*40}
总市值: ¥{total_market_value:,.2f}
总成本: ¥{total_market_value - total_pnl:,.2f}
总浮动盈亏: ¥{total_pnl:,.2f}
总收益率: {total_pnl_pct:.2f}%

📈 持仓明细
{'-'*40}
{portfolio_df.to_string(index=False, float_format='%.2f')}

🔍 技术分析
{'-'*40}
{analysis_df.to_string(index=False, float_format='%.2f')}

💡 操作建议
{'-'*40}
"""
        
        # 盈利股票
        profit_stocks = portfolio_df[portfolio_df['浮动盈亏'] > 0]
        if not profit_stocks.empty:
            report += "\n✅ 盈利股票:\n"
            for _, row in profit_stocks.iterrows():
                report += f"- {row['股票名称']}: +¥{row['浮动盈亏']:,.2f} (+{row['涨跌幅']:.2f}%)\n"
        
        # 亏损股票
        loss_stocks = portfolio_df[portfolio_df['浮动盈亏'] < 0]
        if not loss_stocks.empty:
            report += "\n❌ 亏损股票:\n"
            for _, row in loss_stocks.iterrows():
                report += f"- {row['股票名称']}: -¥{abs(row['浮动盈亏']):,.2f} ({row['涨跌幅']:.2f}%)\n"
        
        # 重点关注
        report += f"""
🎯 重点关注
{'-'*40}
"""
        
        big_changes = portfolio_df[abs(portfolio_df['涨跌幅']) > 15]
        if not big_changes.empty:
            for _, row in big_changes.iterrows():
                if row['涨跌幅'] > 15:
                    report += f"- {row['股票名称']}: 大幅盈利 +{row['涨跌幅']:.2f}%，建议考虑减仓锁定利润\n"
                else:
                    report += f"- {row['股票名称']}: 大幅亏损 {row['涨跌幅']:.2f}%，建议考虑止损或补仓策略\n"
        
        report += f"""
{'='*60}
⚠️ 风险提示: 
1. 以上分析仅供参考，不构成投资建议
2. 股市有风险，投资需谨慎
3. 请根据个人风险承受能力做出投资决策
{'='*60}

📧 自动化股票分析系统
"""
        
        return report
    
    def send_gmail_email(self, report_content):
        """发送Gmail邮件"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.gmail_config['sender_email']
            msg['To'] = self.gmail_config['recipient_email']
            msg['Subject'] = f"📊 股票投资组合分析报告 - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            # 添加邮件正文
            msg.attach(MIMEText(report_content, 'plain', 'utf-8'))
            
            # 创建Excel附件
            portfolio_df, analysis_df, total_market_value, total_pnl, total_pnl_pct = self.analyze_portfolio()
            
            excel_filename = f"reports/stock_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            with pd.ExcelWriter(excel_filename) as writer:
                portfolio_df.to_excel(writer, sheet_name='持仓明细', index=False)
                analysis_df.to_excel(writer, sheet_name='技术分析', index=False)
            
            # 添加Excel附件
            with open(excel_filename, 'rb') as f:
                part = MIMEApplication(f.read())
                part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(excel_filename))
                msg.attach(part)
            
            # 发送Gmail邮件
            with smtplib.SMTP(self.gmail_config['smtp_server'], self.gmail_config['smtp_port']) as server:
                server.starttls()
                server.login(self.gmail_config['sender_email'], self.gmail_config['sender_password'])
                server.send_message(msg)
            
            logger.info(f"邮件已发送至 {self.gmail_config['recipient_email']}")
            return True
            
        except Exception as e:
            logger.error(f"Gmail邮件发送失败: {e}")
            return False
    
    def run_analysis_and_send_email(self):
        """运行分析并发送邮件"""
        try:
            logger.info(f"开始分析 - {datetime.now()}")
            
            # 分析投资组合
            portfolio_df, analysis_df, total_market_value, total_pnl, total_pnl_pct = self.analyze_portfolio()
            
            # 生成报告
            report = self.generate_report(portfolio_df, analysis_df, total_market_value, total_pnl, total_pnl_pct)
            
            # 保存报告
            report_filename = f"reports/stock_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(report_filename, 'w', encoding='utf-8') as f:
                f.write(report)
            
            # 发送邮件
            email_sent = self.send_gmail_email(report)
            
            if email_sent:
                logger.info("分析完成，邮件已发送")
            else:
                logger.error("分析完成，但邮件发送失败")
            
            return email_sent
            
        except Exception as e:
            logger.error(f"分析失败: {e}")
            return False
    
    def setup_schedule(self):
        """设置定时任务"""
        # 每天10:00和16:00运行
        schedule.every().day.at("10:00").do(self.run_analysis_and_send_email)
        schedule.every().day.at("16:00").do(self.run_analysis_and_send_email)
        
        logger.info("定时任务已设置：每天10:00和16:00")
    
    def run_scheduler(self):
        """运行定时调度器"""
        self.setup_schedule()
        
        logger.info("定时调度器启动...")
        logger.info("⏰ 定时任务：每天10:00和16:00")
        logger.info("📧 邮件发送至：zhangbin19850523@163.com")
        logger.info("按 Ctrl+C 停止程序")
        
        while True:
            schedule.run_pending()
            time.sleep(60)
    
    def run_once(self):
        """运行一次分析"""
        logger.info("运行单次分析...")
        return self.run_analysis_and_send_email()

def main():
    """主函数"""
    print("🚀 生产环境股票分析系统")
    print("=" * 60)
    
    analyzer = ProductionStockAnalyzer()
    
    # 运行一次分析
    print("正在运行分析...")
    success = analyzer.run_once()
    
    if success:
        print("✅ 分析完成，邮件已发送")
        
        # 启动定时调度器
        print("\n🚀 启动定时调度器...")
        analyzer.run_scheduler()
    else:
        print("❌ 分析失败")

if __name__ == "__main__":
    main()
