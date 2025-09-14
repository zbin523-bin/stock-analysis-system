#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生产环境股票分析系统部署脚本
Production Stock Analysis System Deployment Script
"""

import os
import sys
import subprocess
import platform
import shutil
from datetime import datetime

def create_production_analyzer():
    """创建生产环境版本的分析器"""
    production_code = '''#!/usr/bin/env python3
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
            report += "\\n✅ 盈利股票:\\n"
            for _, row in profit_stocks.iterrows():
                report += f"- {row['股票名称']}: +¥{row['浮动盈亏']:,.2f} (+{row['涨跌幅']:.2f}%)\\n"
        
        # 亏损股票
        loss_stocks = portfolio_df[portfolio_df['浮动盈亏'] < 0]
        if not loss_stocks.empty:
            report += "\\n❌ 亏损股票:\\n"
            for _, row in loss_stocks.iterrows():
                report += f"- {row['股票名称']}: -¥{abs(row['浮动盈亏']):,.2f} ({row['涨跌幅']:.2f}%)\\n"
        
        # 重点关注
        report += f"""
🎯 重点关注
{'-'*40}
"""
        
        big_changes = portfolio_df[abs(portfolio_df['涨跌幅']) > 15]
        if not big_changes.empty:
            for _, row in big_changes.iterrows():
                if row['涨跌幅'] > 15:
                    report += f"- {row['股票名称']}: 大幅盈利 +{row['涨跌幅']:.2f}%，建议考虑减仓锁定利润\\n"
                else:
                    report += f"- {row['股票名称']}: 大幅亏损 {row['涨跌幅']:.2f}%，建议考虑止损或补仓策略\\n"
        
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
        print("\\n🚀 启动定时调度器...")
        analyzer.run_scheduler()
    else:
        print("❌ 分析失败")

if __name__ == "__main__":
    main()
'''
    
    with open('production_stock_analyzer.py', 'w', encoding='utf-8') as f:
        f.write(production_code)
    
    # 使文件可执行
    os.chmod('production_stock_analyzer.py', 0o755)
    print("✅ 创建生产环境分析器: production_stock_analyzer.py")

def create_launch_scripts():
    """创建启动脚本"""
    # macOS/Linux 启动脚本
    bash_script = '''#!/bin/bash
# 股票分析系统启动脚本

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到Python3，请先安装Python3"
    exit 1
fi

# 创建必要目录
mkdir -p logs reports

echo "🚀 启动生产环境股票分析系统..."
echo "⏰ 定时任务：每天10:00和16:00"
echo "📧 邮件发送至：zhangbin19850523@163.com"
echo "按 Ctrl+C 停止程序"
echo ""

# 启动分析系统
python3 production_stock_analyzer.py
'''
    
    with open('start_stock_system.sh', 'w') as f:
        f.write(bash_script)
    
    os.chmod('start_stock_system.sh', 0o755)
    print("✅ 创建启动脚本: start_stock_system.sh")
    
    # Windows 启动脚本
    windows_script = '''@echo off
REM 股票分析系统启动脚本 (Windows)

REM 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到Python，请先安装Python
    pause
    exit /b 1
)

REM 创建必要目录
if not exist "logs" mkdir logs
if not exist "reports" mkdir reports

echo 🚀 启动生产环境股票分析系统...
echo ⏰ 定时任务：每天10:00和16:00
echo 📧 邮件发送至：zhangbin19850523@163.com
echo 按 Ctrl+C 停止程序
echo.

REM 启动分析系统
python production_stock_analyzer.py
pause
'''
    
    with open('start_stock_system.bat', 'w') as f:
        f.write(windows_script)
    
    print("✅ 创建Windows启动脚本: start_stock_system.bat")

def create_systemd_service():
    """创建systemd服务文件"""
    service_content = f'''[Unit]
Description=Stock Analysis Automated System
After=network.target

[Service]
Type=simple
User={os.getenv('USER', 'user')}
WorkingDirectory={os.getcwd()}
ExecStart={sys.executable} production_stock_analyzer.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
'''
    
    with open('stock-analysis.service', 'w') as f:
        f.write(service_content)
    
    print("✅ 创建systemd服务文件: stock-analysis.service")
    print("要启用服务，请运行:")
    print("  sudo cp stock-analysis.service /etc/systemd/system/")
    print("  sudo systemctl daemon-reload")
    print("  sudo systemctl enable stock-analysis")
    print("  sudo systemctl start stock-analysis")

def create_cron_job():
    """创建cron任务"""
    cron_content = f'''
# 股票分析系统定时任务
# 每天10:00和16:00运行分析
0 10 * * * cd {os.getcwd()} && {sys.executable} production_stock_analyzer.py >> logs/cron.log 2>&1
0 16 * * * cd {os.getcwd()} && {sys.executable} production_stock_analyzer.py >> logs/cron.log 2>&1
'''
    
    with open('stock_analysis_cron.txt', 'w') as f:
        f.write(cron_content)
    
    print("✅ 创建cron任务文件: stock_analysis_cron.txt")
    print("要启用cron任务，请运行:")
    print("  crontab stock_analysis_cron.txt")

def create_readme():
    """创建README文件"""
    readme_content = '''# 股票投资组合分析系统

## 功能特性

- 📊 自动分析股票投资组合
- 📈 实时获取港股价格
- 📧 自动发送分析报告到邮箱
- ⏰ 定时任务：每天10:00和16:00
- 💡 提供买卖建议和技术分析
- 📋 生成Excel格式报告

## 系统要求

- Python 3.7+
- pandas, requests, schedule 库
- Gmail账户和应用程序密码

## 快速开始

### 1. 安装依赖
```bash
pip install pandas requests schedule
```

### 2. 运行系统

#### 方式一：直接运行
```bash
python3 production_stock_analyzer.py
```

#### 方式二：使用启动脚本
```bash
# macOS/Linux
./start_stock_system.sh

# Windows
start_stock_system.bat
```

#### 方式三：系统服务 (Linux)
```bash
# 复制服务文件
sudo cp stock-analysis.service /etc/systemd/system/

# 启用服务
sudo systemctl daemon-reload
sudo systemctl enable stock-analysis
sudo systemctl start stock-analysis
```

#### 方式四：Cron任务
```bash
# 添加定时任务
crontab stock_analysis_cron.txt
```

## 配置说明

### Gmail配置
系统已预配置Gmail账户：
- 发件人：zbin523@gmail.com
- 收件人：zhangbin19850523@163.com

### 股票配置
系统监控以下港股：
- 腾讯控股 (00700.HK)
- 中芯国际 (00981.HK)
- 小米集团-W (01810.HK)
- 中国人寿 (02628.HK)
- 美团-W (03690.HK)
- 新东方-S (09901.HK)
- 阿里巴巴-W (09988.HK)

## 文件结构

```
├── production_stock_analyzer.py    # 主程序
├── start_stock_system.sh          # Linux/macOS启动脚本
├── start_stock_system.bat         # Windows启动脚本
├── stock-analysis.service         # systemd服务文件
├── stock_analysis_cron.txt       # Cron任务文件
├── logs/                         # 日志目录
├── reports/                       # 报告目录
└── README.md                     # 说明文档
```

## 定时任务

系统会在每天以下时间自动运行：
- **10:00** - 上午开盘分析
- **16:00** - 下午收盘分析

## 邮件报告

每次分析会发送包含以下内容的邮件：
- 📊 投资组合总览
- 📈 持仓明细表格
- 🔍 技术分析
- 💡 操作建议
- 📎 Excel格式附件

## 日志监控

- 系统日志：`logs/stock_analysis.log`
- Cron日志：`logs/cron.log`

## 故障排除

### Gmail发送失败
1. 检查Gmail应用程序密码是否正确
2. 确保开启了"不够安全的应用的访问权限"
3. 检查网络连接

### 股票价格获取失败
1. 检查网络连接
2. 查看日志文件了解具体错误
3. 系统会自动重试

### 定时任务不执行
1. 检查系统时间是否正确
2. 查看日志文件
3. 手动运行测试：`python3 production_stock_analyzer.py`

## 停止系统

### 手动运行
按 `Ctrl+C` 停止程序

### 系统服务
```bash
sudo systemctl stop stock-analysis
```

### Cron任务
```bash
crontab -l  # 查看当前任务
crontab -r  # 删除所有任务
```

## 技术支持

如有问题，请查看日志文件或联系技术支持。
'''
    
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("✅ 创建README文件: README.md")

def main():
    """主部署函数"""
    print("🚀 生产环境股票分析系统部署工具")
    print("=" * 60)
    
    # 检查当前目录
    print(f"部署目录: {os.getcwd()}")
    
    # 创建生产环境分析器
    create_production_analyzer()
    
    # 创建启动脚本
    create_launch_scripts()
    
    # 创建系统服务
    create_systemd_service()
    
    # 创建Cron任务
    create_cron_job()
    
    # 创建README
    create_readme()
    
    print("\\n🎉 部署完成！")
    print("\\n📋 部署文件列表:")
    print("  • production_stock_analyzer.py  - 主程序")
    print("  • start_stock_system.sh        - Linux/macOS启动脚本")
    print("  • start_stock_system.bat       - Windows启动脚本")
    print("  • stock-analysis.service       - systemd服务文件")
    print("  • stock_analysis_cron.txt     - Cron任务文件")
    print("  • README.md                   - 说明文档")
    
    print("\\n🚀 启动方式:")
    print("  1. 直接运行: python3 production_stock_analyzer.py")
    print("  2. 使用脚本: ./start_stock_system.sh")
    print("  3. 系统服务: sudo systemctl start stock-analysis")
    print("  4. Cron任务: crontab stock_analysis_cron.txt")
    
    print("\\n📧 系统功能:")
    print("  • ⏰ 定时任务：每天10:00和16:00")
    print("  • 📧 邮件发送至：zhangbin19850523@163.com")
    print("  • 📊 自动分析7只港股")
    print("  • 📈 技术分析和买卖建议")
    print("  • 📋 Excel报告附件")
    
    # 询问是否立即测试
    test_now = input("\\n是否立即测试系统？(y/n): ").lower().strip()
    if test_now == 'y':
        print("\\n🧪 运行测试...")
        try:
            subprocess.run([sys.executable, 'production_stock_analyzer.py'], timeout=60)
        except subprocess.TimeoutExpired:
            print("✅ 测试完成（系统正在运行）")
        except Exception as e:
            print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    main()