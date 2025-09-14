#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票行情邮件通知 - Claude Code 子代理
Stock Market Notification Subagent for Claude Code
功能：自动分析港股投资组合，抓取雪球讨论，生成专业报告并发送邮件
"""

import pandas as pd
import requests
import smtplib
import time
import json
import os
import schedule
import threading
import logging
from datetime import datetime, timedelta
import numpy as np
from bs4 import BeautifulSoup
import warnings
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
warnings.filterwarnings('ignore')

# MCP 工具导入
try:
    from mcp__rube__RUBE_MULTI_EXECUTE_TOOL import RUBE_MULTI_EXECUTE_TOOL
    from mcp__rube__RUBE_REMOTE_WORKBENCH import RUBE_REMOTE_WORKBENCH
    from mcp__rube__RUBE_MANAGE_CONNECTIONS import RUBE_MANAGE_CONNECTIONS
    from mcp__rube__RUBE_CREATE_PLAN import RUBE_CREATE_PLAN
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("警告：MCP 工具不可用，将使用备用方案")

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('stock_notification_agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class StockNotificationAgent:
    """股票行情邮件通知子代理"""
    
    def __init__(self, name="股票行情邮件通知"):
        self.name = name
        self.version = "1.0.0"
        
        # 投资组合数据 - 修复成本数据问题
        self.stocks_data = {
            "腾讯控股": {
                "code": "00700.HK", 
                "quantity": 300, 
                "avg_cost": 320.85,
                "total_cost": 320.85 * 300,  # 计算总成本
                "currency": "HKD"
            },
            "中芯国际": {
                "code": "00981.HK", 
                "quantity": 1000, 
                "avg_cost": 47.55,
                "total_cost": 47.55 * 1000,
                "currency": "HKD"
            },
            "小米集团-W": {
                "code": "01810.HK", 
                "quantity": 2000, 
                "avg_cost": 47.1071,
                "total_cost": 47.1071 * 2000,
                "currency": "HKD"
            },
            "中国人寿": {
                "code": "02628.HK", 
                "quantity": 2000, 
                "avg_cost": 23.82,
                "total_cost": 23.82 * 2000,
                "currency": "HKD"
            },
            "美团-W": {
                "code": "03690.HK", 
                "quantity": 740, 
                "avg_cost": 123.2508,
                "total_cost": 123.2508 * 740,
                "currency": "HKD"
            },
            "新东方-S": {
                "code": "09901.HK", 
                "quantity": 2000, 
                "avg_cost": 44.3241,
                "total_cost": 44.3241 * 2000,
                "currency": "HKD"
            },
            "阿里巴巴-W": {
                "code": "09988.HK", 
                "quantity": 500, 
                "avg_cost": 113.74,
                "total_cost": 113.74 * 500,
                "currency": "HKD"
            }
        }
        
        # Gmail 配置
        self.gmail_config = {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "sender_email": "zbin523@gmail.com",
            "sender_password": "sfnd dyld nznx xkbz",
            "recipient_email": "zhangbin19850523@163.com"
        }
        
        # 雪球讨论配置
        self.snowball_config = {
            "base_url": "https://xueqiu.com",
            "discussion_urls": {
                "腾讯控股": "https://xueqiu.com/S/HK00700",
                "中芯国际": "https://xueqiu.com/S/HK00981", 
                "小米集团": "https://xueqiu.com/S/HK01810",
                "中国人寿": "https://xueqiu.com/S/HK02628",
                "美团": "https://xueqiu.com/S/HK03690",
                "新东方": "https://xueqiu.com/S/HK09901",
                "阿里巴巴": "https://xueqiu.com/S/HK09988"
            }
        }
        
        # 报告模板配置
        self.report_template = {
            "title": "📊 港股投资组合日报",
            "sections": [
                "executive_summary",
                "portfolio_snapshot", 
                "price_analysis",
                "sentiment_analysis",
                "key_insights",
                "risk_alerts"
            ]
        }
        
        # 会话配置
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
        })
        
        # 缓存和数据存储
        self.cache = {}
        self.cache_expiry = {}
        self.cache_duration = 300  # 5分钟缓存
        
        logger.info(f"🚀 {self.name} v{self.version} 初始化完成")
        logger.info(f"💼 监控股票数量: {len(self.stocks_data)}")
        logger.info(f"📧 邮件发送至: {self.gmail_config['recipient_email']}")
    
    def get_stock_price_multi_source(self, symbol):
        """多数据源获取股价 - 修复成本为0的问题"""
        cache_key = f"price_{symbol}"
        current_time = time.time()
        
        # 检查缓存
        if cache_key in self.cache and current_time < self.cache_expiry.get(cache_key, 0):
            return self.cache[cache_key]
        
        price = None
        source_used = None
        
        # 数据源1: Yahoo Finance
        try:
            price = self._get_price_yahoo(symbol)
            if price and price > 0:
                source_used = "Yahoo Finance"
        except Exception as e:
            logger.debug(f"Yahoo Finance 获取 {symbol} 失败: {e}")
        
        # 数据源2: 腾讯股票
        if not price:
            try:
                price = self._get_price_tencent(symbol)
                if price and price > 0:
                    source_used = "腾讯股票"
            except Exception as e:
                logger.debug(f"腾讯股票获取 {symbol} 失败: {e}")
        
        # 数据源3: 新浪财经
        if not price:
            try:
                price = self._get_price_sina(symbol)
                if price and price > 0:
                    source_used = "新浪财经"
            except Exception as e:
                logger.debug(f"新浪财经获取 {symbol} 失败: {e}")
        
        # 缓存结果
        if price and price > 0:
            self.cache[cache_key] = price
            self.cache_expiry[cache_key] = current_time + self.cache_duration
            logger.info(f"✅ {symbol} 价格: ¥{price:.2f} (来源: {source_used})")
            return price
        else:
            logger.warning(f"❌ 无法获取 {symbol} 价格")
            return None
    
    def _get_price_yahoo(self, symbol):
        """从 Yahoo Finance 获取股价"""
        try:
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
            
        except Exception as e:
            logger.debug(f"Yahoo Finance API 错误: {e}")
        
        return None
    
    def _get_price_tencent(self, symbol):
        """从腾讯股票获取股价"""
        try:
            if symbol.endswith(".HK"):
                hk_code = symbol.replace(".HK", "")
                url = f"https://qt.gtimg.cn/q=hk{hk_code}"
            else:
                url = f"https://qt.gtimg.cn/q={symbol}"
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
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
            
        except Exception as e:
            logger.debug(f"腾讯股票 API 错误: {e}")
        
        return None
    
    def _get_price_sina(self, symbol):
        """从新浪财经获取股价"""
        try:
            if symbol.endswith(".HK"):
                # 港股代码转换
                hk_code = symbol.replace(".HK", "")
                # 新浪港股API格式
                url = f"https://hq.sinajs.cn/?list=hk{hk_code}"
            else:
                url = f"https://hq.sinajs.cn/?list={symbol}"
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            content = response.text
            if '="' in content and '";' in content:
                data_str = content.split('="')[1].split('";')[0]
                fields = data_str.split(',')
                
                if len(fields) > 6:
                    try:
                        # 新浪数据格式：名称,开盘价,昨收价,当前价,最高价,最低价...
                        current_price = float(fields[3])
                        if current_price > 0:
                            return current_price
                    except (ValueError, IndexError):
                        pass
            
        except Exception as e:
            logger.debug(f"新浪财经 API 错误: {e}")
        
        return None
    
    def scrape_snowball_discussions(self, stock_name):
        """抓取雪球讨论 - 使用 MCP 工具"""
        if not MCP_AVAILABLE:
            return self._scrape_snowball_fallback(stock_name)
        
        discussions = []
        stock_url = self.snowball_config["discussion_urls"].get(stock_name)
        
        if not stock_url:
            logger.warning(f"未找到 {stock_name} 的雪球讨论URL")
            return discussions
        
        try:
            # 使用 MCP 工具抓取雪球讨论
            tools = [{
                "tool_slug": "FIRECRAWL_SCRAPE",
                "arguments": {
                    "url": stock_url,
                    "formats": ["markdown", "json"],
                    "onlyMainContent": True,
                    "includeTags": ["article", "div", "p", "span"],
                    "excludeTags": ["script", "style", "nav"],
                    "timeout": 30000,
                    "waitFor": 2000,
                    "jsonOptions": {
                        "prompt": f"提取关于{stock_name}的股票讨论，包括观点、情绪分析、关键评论",
                        "systemPrompt": "你是一个金融分析师，专注于提取和分析股票讨论的观点和情绪"
                    }
                }
            }]
            
            result = RUBE_MULTI_EXECUTE_TOOL(
                tools=tools,
                thought=f"抓取{stock_name}的雪球讨论数据",
                memory={},
                current_step="SCRAPING_DISCUSSIONS",
                current_step_metric={"completed": 0, "total": 1, "unit": "stocks"},
                next_step="ANALYZING_SENTIMENT"
            )
            
            if result and "data" in result:
                # 解析 MCP 工具返回的数据
                scraped_data = result["data"]
                if isinstance(scraped_data, list) and len(scraped_data) > 0:
                    first_result = scraped_data[0]
                    if "result" in first_result:
                        content = first_result["result"]
                        discussions = self._parse_snowball_content(content, stock_name)
            
        except Exception as e:
            logger.error(f"使用 MCP 工具抓取 {stock_name} 雪球讨论失败: {e}")
            # 回退到备用方案
            discussions = self._scrape_snowball_fallback(stock_name)
        
        logger.info(f"📝 {stock_name} 雪球讨论: 获取 {len(discussions)} 条")
        return discussions
    
    def _scrape_snowball_fallback(self, stock_name):
        """雪球抓取备用方案"""
        discussions = []
        stock_url = self.snowball_config["discussion_urls"].get(stock_name)
        
        if not stock_url:
            return discussions
        
        try:
            # 使用浏览器工具作为备用
            tools = [{
                "tool_slug": "BROWSER_TOOL_NAVIGATE",
                "arguments": {
                    "url": stock_url,
                    "idleTtlSec": 300
                }
            }]
            
            result = RUBE_MULTI_EXECUTE_TOOL(
                tools=tools,
                thought=f"使用浏览器工具访问{stock_name}雪球页面",
                memory={},
                current_step="BROWSER_SCRAPING",
                current_step_metric={"completed": 0, "total": 1, "unit": "stocks"},
                next_step="CONTENT_EXTRACTION"
            )
            
            if result:
                # 获取页面内容
                content_tools = [{
                    "tool_slug": "BROWSER_TOOL_FETCH_WEBPAGE",
                    "arguments": {
                        "format": "markdown",
                        "wait": 2000,
                        "returnPartialOnTimeout": True
                    }
                }]
                
                content_result = RUBE_MULTI_EXECUTE_TOOL(
                    tools=content_tools,
                    thought=f"提取{stock_name}雪球页面内容",
                    memory={},
                    current_step="CONTENT_FETCH",
                    current_step_metric={"completed": 0, "total": 1, "unit": "stocks"},
                    next_step="SENTIMENT_ANALYSIS"
                )
                
                if content_result and "data" in content_result:
                    content = content_result["data"]
                    if isinstance(content, list) and len(content) > 0:
                        page_content = content[0].get("result", "")
                        discussions = self._parse_snowball_content(page_content, stock_name)
        
        except Exception as e:
            logger.error(f"雪球备用抓取方案失败: {e}")
        
        return discussions
    
    def _parse_snowball_content(self, content, stock_name):
        """解析雪球内容"""
        discussions = []
        
        try:
            # 使用简单的文本分析提取讨论要点
            if isinstance(content, str):
                # 按段落分割内容
                paragraphs = content.split('\n\n')
                
                for paragraph in paragraphs[:10]:  # 限制数量
                    paragraph = paragraph.strip()
                    if len(paragraph) > 20 and self._is_relevant_discussion(paragraph, stock_name):
                        sentiment = self._analyze_sentiment(paragraph)
                        discussions.append({
                            "content": paragraph[:200],  # 截断长度
                            "sentiment": sentiment,
                            "timestamp": datetime.now().isoformat(),
                            "source": "雪球"
                        })
            
        except Exception as e:
            logger.error(f"解析雪球内容失败: {e}")
        
        return discussions
    
    def _is_relevant_discussion(self, text, stock_name):
        """判断是否为相关讨论"""
        relevant_keywords = [
            "股价", "涨跌", "买入", "卖出", "持有", "看好", "看空", 
            "财报", "业绩", "估值", "技术面", "基本面", "风险", "机会",
            stock_name, "腾讯", "阿里", "美团", "小米", "中芯", "人寿", "新东方"
        ]
        
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in relevant_keywords)
    
    def _analyze_sentiment(self, text):
        """分析情绪"""
        positive_words = ["买入", "持有", "看好", "上涨", "突破", "盈利", "增长", "推荐", "乐观", "强势"]
        negative_words = ["卖出", "看空", "下跌", "风险", "亏损", "回调", "谨慎", "悲观", "弱势", "危险"]
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    def analyze_portfolio(self):
        """分析投资组合 - 修复数据显示问题"""
        logger.info("🔍 开始分析投资组合...")
        
        analysis_results = []
        
        for stock_name, data in self.stocks_data.items():
            try:
                # 获取当前价格
                current_price = self.get_stock_price_multi_source(data["code"])
                
                if current_price:
                    # 计算各项指标 - 修复成本计算
                    market_value = current_price * data["quantity"]
                    total_cost = data.get("total_cost", data["avg_cost"] * data["quantity"])
                    pnl = market_value - total_cost
                    change_pct = ((current_price - data["avg_cost"]) / data["avg_cost"]) * 100
                    
                    # 抓取雪球讨论
                    discussions = self.scrape_snowball_discussions(stock_name)
                    sentiment_summary = self._summarize_sentiment(discussions)
                    
                    # 技术分析
                    technical_signals = self._generate_technical_signals(current_price, data["avg_cost"], change_pct)
                    
                    analysis_result = {
                        "股票名称": stock_name,
                        "代码": data["code"],
                        "数量": data["quantity"],
                        "摊薄成本价": data["avg_cost"],
                        "当前价格": current_price,
                        "总成本": total_cost,
                        "市值": market_value,
                        "浮动盈亏": pnl,
                        "涨跌幅": change_pct,
                        "技术信号": technical_signals,
                        "市场情绪": sentiment_summary,
                        "雪球讨论数": len(discussions),
                        "最后更新": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    analysis_results.append(analysis_result)
                    logger.info(f"✅ {stock_name}: ¥{current_price:.2f} ({change_pct:+.2f}%)")
                
                else:
                    # 价格获取失败的处理
                    total_cost = data.get("total_cost", data["avg_cost"] * data["quantity"])
                    
                    analysis_result = {
                        "股票名称": stock_name,
                        "代码": data["code"],
                        "数量": data["quantity"],
                        "摊薄成本价": data["avg_cost"],
                        "当前价格": 0,
                        "总成本": total_cost,
                        "市值": 0,
                        "浮动盈亏": -total_cost,
                        "涨跌幅": -100,
                        "技术信号": ["数据获取失败"],
                        "市场情绪": {"status": "unknown", "reason": "价格数据不可用"},
                        "雪球讨论数": 0,
                        "最后更新": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    analysis_results.append(analysis_result)
                    logger.warning(f"❌ {stock_name}: 价格获取失败")
                    
            except Exception as e:
                logger.error(f"分析 {stock_name} 时出错: {e}")
                continue
        
        return analysis_results
    
    def _summarize_sentiment(self, discussions):
        """总结情绪分析"""
        if not discussions:
            return {"status": "no_data", "positive": 0, "negative": 0, "neutral": 0}
        
        sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
        for discussion in discussions:
            sentiment = discussion.get("sentiment", "neutral")
            if sentiment in sentiment_counts:
                sentiment_counts[sentiment] += 1
        
        total = len(discussions)
        if total == 0:
            return {"status": "no_data", "positive": 0, "negative": 0, "neutral": 0}
        
        # 判断整体情绪
        positive_ratio = sentiment_counts["positive"] / total
        negative_ratio = sentiment_counts["negative"] / total
        
        if positive_ratio > 0.6:
            overall_sentiment = "positive"
        elif negative_ratio > 0.6:
            overall_sentiment = "negative"
        else:
            overall_sentiment = "neutral"
        
        return {
            "status": overall_sentiment,
            "positive": sentiment_counts["positive"],
            "negative": sentiment_counts["negative"],
            "neutral": sentiment_counts["neutral"],
            "total": total,
            "positive_ratio": positive_ratio,
            "negative_ratio": negative_ratio
        }
    
    def _generate_technical_signals(self, current_price, avg_cost, change_pct):
        """生成技术信号"""
        signals = []
        
        # 基于涨跌幅的信号
        if change_pct > 20:
            signals.append("大幅盈利")
        elif change_pct > 10:
            signals.append("盈利")
        elif change_pct > 5:
            signals.append("小幅盈利")
        elif change_pct < -20:
            signals.append("大幅亏损")
        elif change_pct < -10:
            signals.append("亏损")
        elif change_pct < -5:
            signals.append("小幅亏损")
        else:
            signals.append("持平")
        
        # 基于价格位置的信号
        price_ratio = current_price / avg_cost
        if price_ratio > 1.15:
            signals.append("高位")
        elif price_ratio > 1.05:
            signals.append("偏高位")
        elif price_ratio < 0.85:
            signals.append("低位")
        elif price_ratio < 0.95:
            signals.append("偏低位")
        else:
            signals.append("区间震荡")
        
        return signals
    
    def generate_morning_style_report(self, analysis_results):
        """生成早报风格的专业报告"""
        report_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 计算总体统计
        total_market_value = sum(r.get("市值", 0) for r in analysis_results)
        total_cost = sum(r.get("总成本", 0) for r in analysis_results)
        total_pnl = sum(r.get("浮动盈亏", 0) for r in analysis_results)
        total_pnl_pct = (total_pnl / total_cost * 100) if total_cost > 0 else 0
        
        # 统计情绪数据
        total_discussions = sum(r.get("雪球讨论数", 0) for r in analysis_results)
        positive_stocks = sum(1 for r in analysis_results if r.get("市场情绪", {}).get("status") == "positive")
        negative_stocks = sum(1 for r in analysis_results if r.get("市场情绪", {}).get("status") == "negative")
        
        # 生成报告
        report = f"""
┌─────────────────────────────────────────────────────────────────┐
│                    📊 港股投资组合日报                            
│                    🗓️  {report_time[:10]}                        
│                    ⏰  {report_time[11:19}                         
└─────────────────────────────────────────────────────────────────┘

💼 投资组合总览
┌─────────────────────────────────────────────────────────────────┐
│ 总市值: ¥{total_market_value:,.2f}                                      │
│ 总成本: ¥{total_cost:,.2f}                                      │
│ 浮动盈亏: ¥{total_pnl:+,.2f} ({total_pnl_pct:+.2f}%)                           │
│ 监控股票数: {len(analysis_results)} 只                                            │
│ 市场讨论: {total_discussions} 条 (正面: {positive_stocks}, 负面: {negative_stocks})        │
└─────────────────────────────────────────────────────────────────┘

📈 持仓明细
┌─────────────────────────────────────────────────────────────────┐
│ 股票名称      代码      数量      现价      成本价      盈亏         涨跌幅   │
├─────────────────────────────────────────────────────────────────┤
"""
        
        # 添加每只股票的详细信息
        for result in analysis_results:
            stock_name = result['股票名称'][:10] if len(result['股票名称']) > 10 else result['股票名称']
            code = result['代码'][:8] if len(result['代码']) > 8 else result['代码']
            quantity = f"{result['数量']:,}"
            current_price = f"¥{result['当前价格']:.2f}" if result['当前价格'] > 0 else "N/A"
            avg_price = f"¥{result['摊薄成本价']:.2f}"
            pnl = f"¥{result['浮动盈亏']:+,.2f}"
            change_pct = f"{result['涨跌幅']:+.2f}%" if result['涨跌幅'] != -100 else "N/A"
            
            report += f"│ {stock_name:<12} {code:<10} {quantity:>8} {current_price:>10} {avg_price:>10} {pnl:>12} {change_pct:>8} │\n"
        
        report += """└─────────────────────────────────────────────────────────────────┘

🔍 技术分析
┌─────────────────────────────────────────────────────────────────┐
"""
        
        # 添加技术分析
        for result in analysis_results:
            stock_name = result['股票名称'][:10] if len(result['股票名称']) > 10 else result['股票名称']
            signals = ', '.join(result.get('技术信号', []))[:30]
            sentiment_status = result.get('市场情绪', {}).get('status', 'unknown')
            discussion_count = result.get('雪球讨论数', 0)
            
            report += f"│ {stock_name:<12} 信号: {signals:<30} 情绪: {sentiment_status:<8} 讨论: {discussion_count:>3} │\n"
        
        report += """└─────────────────────────────────────────────────────────────────┘

💡 操作建议
┌─────────────────────────────────────────────────────────────────┐
"""
        
        # 添加操作建议
        for result in analysis_results:
            if result['当前价格'] > 0:  # 只为有价格的股票提供建议
                stock_name = result['股票名称'][:10] if len(result['股票名称']) > 10 else result['股票名称']
                change_pct = result['涨跌幅']
                pnl = result['浮动盈亏']
                
                if change_pct > 15:
                    recommendation = "考虑减仓锁定利润"
                elif change_pct > 5:
                    recommendation = "继续持有"
                elif change_pct < -15:
                    recommendation = "考虑补仓或止损"
                elif change_pct < -5:
                    recommendation = "持有观望"
                else:
                    recommendation = "持有"
                
                report += f"│ {stock_name:<12} {recommendation:<40} 盈亏: {pnl:+,.2f} │\n"
        
        report += """└─────────────────────────────────────────────────────────────────┘

🎯 重点关注
┌─────────────────────────────────────────────────────────────────┐
"""
        
        # 添加重点关注
        focus_stocks = []
        for result in analysis_results:
            if abs(result.get('涨跌幅', 0)) > 10 or result.get('雪球讨论数', 0) > 5:
                focus_stocks.append(result)
        
        if focus_stocks:
            for result in focus_stocks[:5]:  # 最多显示5只
                stock_name = result['股票名称'][:10] if len(result['股票名称']) > 10 else result['股票名称']
                change_pct = result.get('涨跌幅', 0)
                discussions = result.get('雪球讨论数', 0)
                sentiment = result.get('市场情绪', {}).get('status', 'unknown')
                
                focus_reason = []
                if abs(change_pct) > 10:
                    focus_reason.append(f"波动{'大' if abs(change_pct) > 15 else '较大'} ({change_pct:+.2f}%)")
                if discussions > 5:
                    focus_reason.append(f"讨论活跃 ({discussions}条)")
                if sentiment in ['positive', 'negative']:
                    focus_reason.append(f"市场情绪{sentiment}")
                
                report += f"│ {stock_name:<12} {', '.join(focus_reason):<45} │\n"
        else:
            report += "│ 今日无特别关注的股票                                           │\n"
        
        report += """└─────────────────────────────────────────────────────────────────┘

⚠️ 风险提示
┌─────────────────────────────────────────────────────────────────┐
│ • 以上分析仅供参考，不构成投资建议                                  │
│ • 股市有风险，投资需谨慎                                            │
│ • 请根据个人风险承受能力做出投资决策                                │
│ • 数据可能存在延迟，请以实际交易价格为准                            │
└─────────────────────────────────────────────────────────────────┘

📧 股票行情邮件通知系统 | Claude Code 子代理
Generated by Stock Notification Agent v1.0.0
"""
        
        return report
    
    def send_email(self, content):
        """发送邮件"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.gmail_config['sender_email']
            msg['To'] = self.gmail_config['recipient_email']
            msg['Subject'] = f"📊 港股投资组合日报 - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            # 添加邮件正文
            msg.attach(MIMEText(content, 'plain', 'utf-8'))
            
            # 发送邮件
            with smtplib.SMTP(self.gmail_config['smtp_server'], self.gmail_config['smtp_port']) as server:
                server.starttls()
                server.login(self.gmail_config['sender_email'], self.gmail_config['sender_password'])
                server.send_message(msg)
            
            logger.info(f"✅ 邮件已发送至 {self.gmail_config['recipient_email']}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 邮件发送失败: {e}")
            return False
    
    def run_analysis_and_send(self):
        """运行分析并发送邮件 - 主要执行方法"""
        try:
            logger.info(f"🚀 {self.name} 开始执行分析...")
            start_time = time.time()
            
            # 分析投资组合
            analysis_results = self.analyze_portfolio()
            
            if not analysis_results:
                logger.error("❌ 分析结果为空")
                return False
            
            # 生成报告
            report = self.generate_morning_style_report(analysis_results)
            
            # 保存报告到本地
            os.makedirs('reports', exist_ok=True)
            report_filename = f"reports/stock_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(report_filename, 'w', encoding='utf-8') as f:
                f.write(report)
            
            # 发送邮件
            email_sent = self.send_email(report)
            
            execution_time = time.time() - start_time
            logger.info(f"⏱️ 执行耗时: {execution_time:.2f}秒")
            
            if email_sent:
                logger.info("✅ 分析完成，邮件已发送")
                return True
            else:
                logger.error("❌ 分析完成，但邮件发送失败")
                return False
                
        except Exception as e:
            logger.error(f"❌ 执行过程中发生错误: {e}")
            return False
    
    def run_once(self):
        """运行一次分析（用于测试）"""
        logger.info("🧪 运行单次分析测试...")
        return self.run_analysis_and_send()
    
    def setup_scheduler(self):
        """设置定时任务 - 每天10:00和16:00"""
        schedule.every().day.at("10:00").do(self.run_analysis_and_send)
        schedule.every().day.at("16:00").do(self.run_analysis_and_send)
        
        logger.info("⏰ 定时任务已设置：每天10:00和16:00")
    
    def run_scheduler(self):
        """运行定时调度器"""
        self.setup_scheduler()
        
        logger.info("🔄 定时调度器启动...")
        logger.info("⏰ 定时任务：每天10:00和16:00")
        logger.info("📧 邮件发送至：zhangbin19850523@163.com")
        logger.info("按 Ctrl+C 停止程序")
        
        # 立即运行一次测试
        logger.info("🧪 启动时先运行一次测试...")
        self.run_once()
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # 每分钟检查一次
        except KeyboardInterrupt:
            logger.info("🛑 定时调度器已停止")
    
    def test_connection(self):
        """测试连接"""
        logger.info("🔧 测试系统连接...")
        
        # 测试Gmail连接
        try:
            with smtplib.SMTP(self.gmail_config['smtp_server'], self.gmail_config['smtp_port']) as server:
                server.starttls()
                server.login(self.gmail_config['sender_email'], self.gmail_config['sender_password'])
            logger.info("✅ Gmail 连接测试成功")
        except Exception as e:
            logger.error(f"❌ Gmail 连接测试失败: {e}")
            return False
        
        # 测试价格获取
        logger.info("🔍 测试价格数据获取...")
        test_price = self.get_stock_price_multi_source("00700.HK")
        if test_price:
            logger.info(f"✅ 价格获取测试成功: 腾讯控股 ¥{test_price:.2f}")
        else:
            logger.error("❌ 价格获取测试失败")
            return False
        
        logger.info("✅ 所有连接测试通过")
        return True
    
    def get_status(self):
        """获取系统状态"""
        return {
            "name": self.name,
            "version": self.version,
            "stocks_count": len(self.stocks_data),
            "gmail_configured": bool(self.gmail_config.get('sender_email')),
            "mcp_available": MCP_AVAILABLE,
            "cache_size": len(self.cache),
            "last_analysis": getattr(self, '_last_analysis_time', None),
            "next_scheduled_runs": [
                schedule.next_run() if schedule.jobs else None
            ]
        }

# Claude Code 子代理接口函数
def create_stock_notification_agent():
    """创建股票行情邮件通知子代理"""
    return StockNotificationAgent()

def run_stock_analysis():
    """运行股票分析 - Claude Code 入口点"""
    agent = StockNotificationAgent()
    
    print(f"🚀 启动 {agent.name} v{agent.version}")
    print("=" * 60)
    
    # 测试连接
    if not agent.test_connection():
        print("❌ 系统连接测试失败，请检查配置")
        return False
    
    # 选择运行模式
    print("\n请选择运行模式:")
    print("1. 运行一次分析（测试）")
    print("2. 启动定时调度器（每天10:00和16:00自动运行）")
    print("3. 仅生成报告不发送邮件")
    
    try:
        choice = input("请选择 (1/2/3): ").strip()
        
        if choice == "1":
            print("\n🧪 运行单次分析...")
            success = agent.run_once()
            if success:
                print("✅ 分析完成")
            else:
                print("❌ 分析失败")
            return success
                
        elif choice == "2":
            print("\n🔄 启动定时调度器...")
            print("系统将在每天10:00和16:00自动发送分析报告")
            print("按 Ctrl+C 停止程序")
            agent.run_scheduler()
            
        elif choice == "3":
            print("\n📄 仅生成报告...")
            analysis_results = agent.analyze_portfolio()
            if analysis_results:
                report = agent.generate_morning_style_report(analysis_results)
                
                # 保存报告
                os.makedirs('reports', exist_ok=True)
                report_filename = f"reports/stock_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                with open(report_filename, 'w', encoding='utf-8') as f:
                    f.write(report)
                
                print(f"✅ 报告已生成: {report_filename}")
                print("报告内容预览（前500字符）:")
                print("-" * 50)
                print(report[:500])
                print("-" * 50)
                return True
            else:
                print("❌ 报告生成失败")
                return False
                
        else:
            print("❌ 无效选择")
            return False
            
    except KeyboardInterrupt:
        print("\n🛑 程序已停止")
        return False
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        return False

# 主入口点
if __name__ == "__main__":
    success = run_stock_analysis()
    exit(0 if success else 1)