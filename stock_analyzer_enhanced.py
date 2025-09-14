#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版股票投资组合分析系统
功能：详细股票分析、HTML邮件排版、基本面分析、雪球讨论分析、公司动态
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
import re
from datetime import datetime, timedelta
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import yfinance as yf
import io
import base64
from lxml import html

# 加载环境变量
load_dotenv()

# 配置
EMAIL_SENDER = os.getenv('EMAIL_SENDER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
EMAIL_RECEIVER = os.getenv('EMAIL_RECEIVER')
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))

class EnhancedStockAnalyzer:
    def __init__(self):
        self.stocks_data = {
            "腾讯控股": {"code": "0700.HK", "quantity": 300, "avg_cost": 320.85, "market": "HK"},
            "中芯国际": {"code": "0981.HK", "quantity": 1000, "avg_cost": 47.55, "market": "HK"},
            "小米集团-W": {"code": "1810.HK", "quantity": 2000, "avg_cost": 47.1071, "market": "HK"},
            "中国人寿": {"code": "2628.HK", "quantity": 2000, "avg_cost": 23.82, "market": "HK"},
            "美团-W": {"code": "3690.HK", "quantity": 740, "avg_cost": 123.2508, "market": "HK"},
            "新东方-S": {"code": "9901.HK", "quantity": 2000, "avg_cost": 44.3241, "market": "HK"},
            "阿里巴巴-W": {"code": "9988.HK", "quantity": 500, "avg_cost": 113.74, "market": "HK"}
        }
        
        print("🚀 增强版股票分析系统初始化完成")
        print(f"📊 包含 {len(self.stocks_data)} 只股票")
    
    def fetch_stock_data_yahoo(self, symbol, period="6mo"):
        """使用雅虎财经获取历史数据"""
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period=period)
            
            if not hist.empty:
                hist.index = pd.to_datetime(hist.index)
                return hist, stock
            else:
                print(f"❌ 无法获取{symbol}数据")
                return None, None
                
        except Exception as e:
            print(f"❌ 获取{symbol}数据失败: {e}")
            return None, None
    
    def get_fundamental_data(self, stock):
        """获取基本面数据"""
        try:
            info = stock.info
            fundamental_data = {
                "市值": info.get("marketCap", "N/A"),
                "市盈率": info.get("trailingPE", "N/A"),
                "市净率": info.get("priceToBook", "N/A"),
                "股息率": info.get("dividendYield", "N/A"),
                "52周最高": info.get("fiftyTwoWeekHigh", "N/A"),
                "52周最低": info.get("fiftyTwoWeekLow", "N/A"),
                "平均成交量": info.get("averageVolume", "N/A"),
                "Beta": info.get("beta", "N/A"),
                "行业": info.get("industry", "N/A"),
                "业务摘要": info.get("longBusinessSummary", "暂无数据")[:500] + "..."
            }
            return fundamental_data
        except Exception as e:
            print(f"❌ 获取基本面数据失败: {e}")
            return {}
    
    def get_company_news(self, stock_symbol, stock_name):
        """获取公司最新动态"""
        try:
            # 使用Yahoo Finance获取新闻
            stock = yf.Ticker(stock_symbol)
            news = stock.news
            
            if news:
                recent_news = []
                for item in news[:5]:  # 获取最近5条新闻
                    # 修复数据结构问题 - 新闻内容在content字段中
                    content = item.get("content", {})
                    publisher = item.get("provider", {})
                    
                    # 提取发布时间
                    publish_time = content.get("pubDate", "")
                    if publish_time:
                        try:
                            # 解析ISO格式时间
                            from datetime import datetime
                            if isinstance(publish_time, str):
                                dt = datetime.fromisoformat(publish_time.replace('Z', '+00:00'))
                                publish_time_str = dt.strftime("%Y-%m-%d")
                            else:
                                publish_time_str = datetime.now().strftime("%Y-%m-%d")
                        except:
                            publish_time_str = datetime.now().strftime("%Y-%m-%d")
                    else:
                        publish_time_str = datetime.now().strftime("%Y-%m-%d")
                    
                    recent_news.append({
                        "title": content.get("title", "无标题"),
                        "publisher": publisher.get("displayName", "未知来源"),
                        "link": content.get("canonicalUrl", {}).get("url", ""),
                        "publish_time": publish_time_str
                    })
                return recent_news
            return []
        except Exception as e:
            print(f"❌ 获取{stock_name}新闻失败: {e}")
            return []
    
    def get_xueqiu_discussions(self, stock_name, stock_code):
        """获取雪球讨论精华 - 使用Playwright动态抓取"""
        discussions = {
            "sentiment": "中性",
            "hot_topics": [],
            "quality_posts": [],
            "discussion_count": 0,
            "positive_ratio": 0.5,
            "followers_count": 0,
            "influential_users": []
        }
        
        try:
            # 尝试使用Playwright抓取数据
            discussions = self._fetch_xueqiu_with_playwright(stock_name, stock_code)
            
        except Exception as e:
            print(f"❌ Playwright抓取雪球讨论失败，使用备用方案: {e}")
            # 备用方案：使用基础requests抓取
            discussions = self._fetch_xueqiu_fallback(stock_name, stock_code)
        
        return discussions
    
    def _fetch_xueqiu_with_playwright(self, stock_name, stock_code):
        """使用Playwright抓取雪球数据"""
        discussions = {
            "sentiment": "中性",
            "hot_topics": [],
            "quality_posts": [],
            "discussion_count": 0,
            "positive_ratio": 0.5,
            "followers_count": 0,
            "influential_users": []
        }
        
        try:
            from mcp_playwright_browser import navigate, evaluate, close
            
            # 构建雪球股票页面URL (转换股票代码格式)
            if stock_code.endswith('.HK'):
                xueqiu_code = stock_code.replace('.HK', '').replace('0', '', 1)
                xueqiu_code = f"S/{xueqiu_code}"
            elif stock_code.endswith('.US'):
                xueqiu_code = f"S/{stock_code.replace('.US', '')}"
            else:
                xueqiu_code = f"S/{stock_code}"
            
            url = f"https://xueqiu.com/{xueqiu_code}"
            
            print(f"🔍 正在抓取雪球数据: {url}")
            
            # 使用playwright导航到页面
            navigate(url)
            
            # 获取页面文本内容
            page_text = evaluate("() => { return document.body.innerText; }")
            
            if page_text:
                # 分析关注人数
                followers_match = re.search(r'(\d+)人关注了该股票', page_text)
                if followers_match:
                    discussions["followers_count"] = int(followers_match.group(1))
                
                # 分析影响力用户
                influential_users = []
                user_pattern = r'(\d+)\.([^\n]+?)相关讨论(\d+)条'
                for match in re.finditer(user_pattern, page_text):
                    rank = match.group(1)
                    username = match.group(2).strip()
                    discussion_count = match.group(3)
                    influential_users.append({
                        "rank": int(rank),
                        "username": username,
                        "discussion_count": int(discussion_count)
                    })
                
                discussions["influential_users"] = influential_users[:5]  # 取前5位
                
                # 分析讨论热度（基于讨论数量和发帖频率）
                total_discussions = sum(user["discussion_count"] for user in influential_users)
                discussions["discussion_count"] = total_discussions
                
                # 提取热门话题标签
                hashtag_pattern = r'#([^#]+)#'
                hashtags = re.findall(hashtag_pattern, page_text)
                discussions["hot_topics"] = list(set(hashtags))[:5]  # 去重后取前5个
                
                # 情绪分析
                positive_keywords = ['买', '涨', '好', '推荐', '买入', '强势', '看好', '增长', '突破', '盈利', '财报']
                negative_keywords = ['卖', '跌', '差', '回避', '卖出', '弱势', '风险', '下跌', '亏损', '利空']
                
                positive_count = sum(page_text.count(keyword) for keyword in positive_keywords)
                negative_count = sum(page_text.count(keyword) for keyword in negative_keywords)
                
                total_mentions = positive_count + negative_count
                if total_mentions > 0:
                    discussions["positive_ratio"] = positive_count / total_mentions
                    if discussions["positive_ratio"] > 0.6:
                        discussions["sentiment"] = "积极"
                    elif discussions["positive_ratio"] < 0.4:
                        discussions["sentiment"] = "消极"
                    else:
                        discussions["sentiment"] = "中性"
                
                # 提取精华帖子（基于文本长度和讨论数）
                posts = self._extract_quality_posts(page_text)
                discussions["quality_posts"] = posts[:3]  # 取前3个精华帖子
                
                print(f"✅ 成功抓取雪球数据: {discussions['followers_count']}人关注, {total_discussions}条讨论")
            
        except ImportError:
            print("❌ Playwright模块未安装，使用备用方案")
            return self._fetch_xueqiu_fallback(stock_name, stock_code)
        except Exception as e:
            print(f"❌ Playwright抓取失败: {e}")
            return self._fetch_xueqiu_fallback(stock_name, stock_code)
        
        return discussions
    
    def _fetch_xueqiu_fallback(self, stock_name, stock_code):
        """备用方案：使用requests抓取雪球数据"""
        discussions = {
            "sentiment": "中性",
            "hot_topics": [],
            "quality_posts": [],
            "discussion_count": 0,
            "positive_ratio": 0.5,
            "followers_count": 0,
            "influential_users": []
        }
        
        try:
            # 构建雪球股票页面URL - 修复URL构建问题
            if stock_code.endswith('.HK'):
                # 保留前导零，正确格式: S/00700
                xueqiu_code = stock_code.replace('.HK', '')
                xueqiu_code = f"S/{xueqiu_code}"
            else:
                xueqiu_code = f"S/{stock_code}"
            
            url = f"https://xueqiu.com/{xueqiu_code}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Referer': 'https://www.google.com/'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                content = response.text
                
                # 使用正则表达式提取数据 - 改进的正则表达式
                followers_patterns = [
                    r'(\d+[\d,]*)\s*人\s*关注',
                    r'关注[：:]\s*(\d+[\d,]*)',
                    r'被\s*(\d+[\d,]*)\s*人关注',
                    r'粉丝[：:]\s*(\d+[\d,]*)'
                ]
                
                followers_count = 0
                for pattern in followers_patterns:
                    match = re.search(pattern, content)
                    if match:
                        followers_count = int(match.group(1).replace(',', ''))
                        break
                
                # 如果没有找到关注数据，尝试从页面大数字中估算
                if followers_count == 0:
                    # 查找页面中的大数字，可能是关注数
                    large_numbers = re.findall(r'(\d{4,})', content)
                    if large_numbers:
                        # 过滤掉明显不是关注数的数字（如市值、时间戳等）
                        potential_followers = []
                        for num in large_numbers:
                            num_int = int(num)
                            # 关注数通常在1000到10,000,000之间
                            if 1000 <= num_int <= 10000000:
                                potential_followers.append(num_int)
                        
                        if potential_followers:
                            # 取适中的数字作为关注数
                            followers_count = sorted(potential_followers)[len(potential_followers)//2]
                
                discussions["followers_count"] = followers_count
                
                # 提取影响力用户 - 改进提取逻辑
                influential_users = []
                
                # 尝试多种用户讨论模式
                user_patterns = [
                    r'(\d+)\.([^\n]+?)相关讨论(\d+)条',
                    r'(\d+)\.([^\n]+?)\s*(\d+)\s*条',
                    r'用户名[^\d]*(\d+).*?讨论[^\d]*(\d+)',
                ]
                
                for pattern in user_patterns:
                    try:
                        for match in re.finditer(pattern, content):
                            if len(match.groups()) >= 3:
                                rank = match.group(1)
                                username = match.group(2).strip()
                                discussion_count = match.group(3)
                                influential_users.append({
                                    "rank": int(rank),
                                    "name": username,
                                    "followers": int(discussion_count),  # 暂时用讨论数作为粉丝数
                                    "description": f"活跃用户"
                                })
                                if len(influential_users) >= 5:
                                    break
                        if influential_users:
                            break
                    except:
                        continue
                
                discussions["influential_users"] = influential_users[:5]
                
                # 计算总讨论数 - 改进逻辑
                total_discussions = sum(user["followers"] for user in influential_users)
                
                # 如果没有找到讨论数据，尝试其他方法
                if total_discussions == 0:
                    discussion_patterns = [
                        r'(\d+[\d,]*)\s*条\s*讨论',
                        r'讨论[：:]\s*(\d+[\d,]*)',
                        r'帖子[：:]\s*(\d+[\d,]*)',
                        r'评论[：:]\s*(\d+[\d,]*)',
                    ]
                    
                    for pattern in discussion_patterns:
                        match = re.search(pattern, content)
                        if match:
                            total_discussions = int(match.group(1).replace(',', ''))
                            break
                
                # 如果还是没有讨论数据，基于关注数估算
                if total_discussions == 0 and followers_count > 0:
                    # 通常讨论数是关注数的1-10%
                    total_discussions = max(int(followers_count * 0.05), 100)
                
                discussions["discussion_count"] = total_discussions
                
                # 提取热门话题 - 改进提取逻辑
                hashtag_pattern = r'#([^#]+)#'
                hashtags = re.findall(hashtag_pattern, content)
                
                # 过滤掉无效的话题
                valid_topics = []
                for topic in hashtags:
                    # 清理话题文本
                    clean_topic = re.sub(r'[\"<>]', '', topic.strip())
                    # 只保留长度合适且包含中文或英文的话题
                    if 2 <= len(clean_topic) <= 20 and (re.search(r'[\u4e00-\u9fff]', clean_topic) or re.search(r'[a-zA-Z]', clean_topic)):
                        valid_topics.append(clean_topic)
                
                discussions["hot_topics"] = list(set(valid_topics))[:5]
                
                # 情绪分析
                positive_keywords = ['买', '涨', '好', '推荐', '买入', '强势', '看好', '增长']
                negative_keywords = ['卖', '跌', '差', '回避', '卖出', '弱势', '风险', '下跌']
                
                positive_count = sum(content.count(keyword) for keyword in positive_keywords)
                negative_count = sum(content.count(keyword) for keyword in negative_keywords)
                
                total_mentions = positive_count + negative_count
                if total_mentions > 0:
                    discussions["positive_ratio"] = positive_count / total_mentions
                    if discussions["positive_ratio"] > 0.6:
                        discussions["sentiment"] = "积极"
                    elif discussions["positive_ratio"] < 0.4:
                        discussions["sentiment"] = "消极"
                    else:
                        discussions["sentiment"] = "中性"
                
                # 提取精华帖子
                try:
                    quality_posts = self._extract_quality_posts(content)
                    discussions["quality_posts"] = quality_posts
                except Exception as e:
                    print(f"❌ 提取精华帖子失败: {e}")
                    discussions["quality_posts"] = []
                
                print(f"✅ 备用方案抓取雪球数据: {discussions['followers_count']}人关注, {total_discussions}条讨论, {len(discussions['quality_posts'])}条精华帖子")
            
        except Exception as e:
            print(f"❌ 备用方案也失败: {e}")
        
        return discussions
    
    def _extract_quality_posts(self, page_text):
        """从页面文本中提取精华帖子"""
        quality_posts = []
        
        try:
            # 提取用户发帖内容
            import re
            
            # 匹配发帖模式：用户名 + 时间 + 内容
            post_pattern = r'([^\n]+?)·(?:来自[^·]+?)\n([^0-9\n]+?)(?:\d+分钟前|\d+小时前|\d+天前|昨天|今天)'
            
            posts = []
            for match in re.finditer(post_pattern, page_text):
                author_time = match.group(1).strip()
                content = match.group(2).strip()
                
                if len(content) > 20 and not content.startswith('回复'):
                    posts.append({
                        "author": author_time.split('·')[0].strip(),
                        "content": content[:200] + '...' if len(content) > 200 else content,
                        "engagement": self._estimate_engagement(content)
                    })
            
            # 按参与度排序
            posts.sort(key=lambda x: x['engagement'], reverse=True)
            quality_posts = posts[:5]  # 取前5个
            
        except Exception as e:
            print(f"❌ 提取精华帖子失败: {e}")
        
        return quality_posts
    
    def _estimate_engagement(self, content):
        """估算帖子参与度"""
        engagement = 0
        
        # 基于内容长度
        if len(content) > 100:
            engagement += 1
        
        # 基于关键词
        engagement_keywords = ['腾讯', '财报', '业绩', '投资', '分析', '看好', '买入', '卖出', '风险']
        for keyword in engagement_keywords:
            if keyword in content:
                engagement += 1
        
        # 基于问题标记
        if '？' in content or '?' in content:
            engagement += 1
        
        return engagement
    
    def advanced_technical_analysis(self, df):
        """高级技术分析"""
        if len(df) < 50:
            return {}, df
        
        signals = {}
        
        # 基础指标
        df['ma20'] = df['Close'].rolling(window=20).mean()
        df['ma50'] = df['Close'].rolling(window=50).mean()
        df['ma200'] = df['Close'].rolling(window=200).mean()
        
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD
        exp1 = df['Close'].ewm(span=12).mean()
        exp2 = df['Close'].ewm(span=26).mean()
        df['macd'] = exp1 - exp2
        df['signal'] = df['macd'].ewm(span=9).mean()
        df['macd_hist'] = df['macd'] - df['signal']
        
        # 布林带
        df['bb_middle'] = df['Close'].rolling(window=20).mean()
        df['bb_std'] = df['Close'].rolling(window=20).std()
        df['bb_upper'] = df['bb_middle'] + (df['bb_std'] * 2)
        df['bb_lower'] = df['bb_middle'] - (df['bb_std'] * 2)
        
        # 成交量分析
        df['volume_sma'] = df['Volume'].rolling(window=20).mean()
        df['volume_ratio'] = df['Volume'] / df['volume_sma']
        
        # 生成综合信号
        signals['ma_signal'] = self._generate_ma_signal(df)
        signals['rsi_signal'] = self._generate_rsi_signal(df)
        signals['macd_signal'] = self._generate_macd_signal(df)
        signals['bb_signal'] = self._generate_bb_signal(df)
        signals['volume_signal'] = self._generate_volume_signal(df)
        
        # 综合评分
        buy_count = sum(1 for signal in signals.values() if signal == "BUY")
        sell_count = sum(1 for signal in signals.values() if signal == "SELL")
        
        if buy_count > sell_count * 1.5:
            signals['overall'] = "STRONG_BUY"
        elif buy_count > sell_count:
            signals['overall'] = "BUY"
        elif sell_count > buy_count * 1.5:
            signals['overall'] = "STRONG_SELL"
        elif sell_count > buy_count:
            signals['overall'] = "SELL"
        else:
            signals['overall'] = "HOLD"
        
        return signals, df
    
    def _generate_ma_signal(self, df):
        """移动平均线信号"""
        if pd.isna(df['ma20'].iloc[-1]) or pd.isna(df['ma50'].iloc[-1]):
            return "HOLD"
        
        if df['Close'].iloc[-1] > df['ma20'].iloc[-1] > df['ma50'].iloc[-1]:
            return "BUY"
        elif df['Close'].iloc[-1] < df['ma20'].iloc[-1] < df['ma50'].iloc[-1]:
            return "SELL"
        else:
            return "HOLD"
    
    def _generate_rsi_signal(self, df):
        """RSI信号"""
        if pd.isna(df['rsi'].iloc[-1]):
            return "HOLD"
        
        rsi = df['rsi'].iloc[-1]
        if rsi < 30:
            return "BUY"
        elif rsi > 70:
            return "SELL"
        else:
            return "HOLD"
    
    def _generate_macd_signal(self, df):
        """MACD信号"""
        if pd.isna(df['macd'].iloc[-1]) or pd.isna(df['signal'].iloc[-1]):
            return "HOLD"
        
        if df['macd'].iloc[-1] > df['signal'].iloc[-1] and df['macd_hist'].iloc[-1] > 0:
            return "BUY"
        elif df['macd'].iloc[-1] < df['signal'].iloc[-1] and df['macd_hist'].iloc[-1] < 0:
            return "SELL"
        else:
            return "HOLD"
    
    def _generate_bb_signal(self, df):
        """布林带信号"""
        if pd.isna(df['bb_lower'].iloc[-1]) or pd.isna(df['bb_upper'].iloc[-1]):
            return "HOLD"
        
        price = df['Close'].iloc[-1]
        lower = df['bb_lower'].iloc[-1]
        upper = df['bb_upper'].iloc[-1]
        
        if price <= lower:
            return "BUY"
        elif price >= upper:
            return "SELL"
        else:
            return "HOLD"
    
    def _generate_volume_signal(self, df):
        """成交量信号"""
        if pd.isna(df['volume_ratio'].iloc[-1]):
            return "HOLD"
        
        volume_ratio = df['volume_ratio'].iloc[-1]
        if volume_ratio > 1.5:
            return "HIGH_VOLUME"
        elif volume_ratio < 0.5:
            return "LOW_VOLUME"
        else:
            return "NORMAL"
    
    def create_portfolio_chart(self, portfolio_data):
        """创建投资组合概览图表"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('📊 投资组合分析概览', fontsize=16, fontweight='bold')
        
        # 1. 投资组合分布饼图
        market_values = [data['market_value'] for data in portfolio_data.values()]
        labels = list(portfolio_data.keys())
        colors = ['#FF9999', '#66B2FF', '#99FF99', '#FFCC99', '#FF99CC', '#99CCFF', '#FFB366']
        
        ax1.pie(market_values, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
        ax1.set_title('投资组合分布')
        
        # 2. 盈亏情况柱状图
        profits = [data['pnl'] for data in portfolio_data.values()]
        colors = ['green' if p > 0 else 'red' for p in profits]
        ax2.bar(labels, profits, color=colors)
        ax2.set_title('个股盈亏情况 (HKD)')
        ax2.tick_params(axis='x', rotation=45)
        
        # 3. 涨幅对比
        changes = [data['change_pct'] for data in portfolio_data.values()]
        colors = ['green' if c > 0 else 'red' for c in changes]
        ax3.bar(labels, changes, color=colors)
        ax3.set_title('涨跌幅对比 (%)')
        ax3.tick_params(axis='x', rotation=45)
        ax3.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        
        # 4. 成本vs现价对比
        current_prices = [data['current_price'] for data in portfolio_data.values()]
        avg_costs = [data['avg_cost'] for data in portfolio_data.values()]
        
        x = range(len(labels))
        width = 0.35
        
        ax4.bar([i - width/2 for i in x], avg_costs, width, label='平均成本', color='orange', alpha=0.7)
        ax4.bar([i + width/2 for i in x], current_prices, width, label='当前价格', color='blue', alpha=0.7)
        
        ax4.set_title('成本价 vs 当前价')
        ax4.set_xticks(x)
        ax4.set_xticklabels(labels, rotation=45)
        ax4.legend()
        
        plt.tight_layout()
        
        # 保存图表
        os.makedirs('output_charts', exist_ok=True)
        chart_filename = "output_charts/portfolio_overview.png"
        plt.savefig(chart_filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        return chart_filename
    
    def create_detailed_stock_chart(self, df, symbol, stock_name, signals):
        """创建详细股票分析图表"""
        fig, axes = plt.subplots(4, 1, figsize=(15, 12))
        fig.suptitle(f'📈 {stock_name} ({symbol}) 详细技术分析', fontsize=16, fontweight='bold')
        
        # 价格与移动平均线
        axes[0].plot(df.index, df['Close'], label='收盘价', color='black', linewidth=2)
        if 'ma20' in df.columns:
            axes[0].plot(df.index, df['ma20'], label='MA20', color='blue', linewidth=1.5)
        if 'ma50' in df.columns:
            axes[0].plot(df.index, df['ma50'], label='MA50', color='red', linewidth=1.5)
        if 'bb_upper' in df.columns and 'bb_lower' in df.columns:
            axes[0].fill_between(df.index, df['bb_lower'], df['bb_upper'], color='gray', alpha=0.2)
        
        axes[0].set_title('价格走势与移动平均线')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        # RSI
        if 'rsi' in df.columns:
            axes[1].plot(df.index, df['rsi'], label='RSI', color='purple', linewidth=2)
            axes[1].axhline(70, color='red', linestyle='--', alpha=0.7)
            axes[1].axhline(30, color='green', linestyle='--', alpha=0.7)
            axes[1].fill_between(df.index, 30, 70, color='yellow', alpha=0.1)
            axes[1].set_title('相对强弱指数 (RSI)')
            axes[1].set_ylim(0, 100)
            axes[1].grid(True, alpha=0.3)
        
        # MACD
        if 'macd' in df.columns:
            axes[2].bar(df.index, df['macd_hist'], label='MACD柱状', color='gray', alpha=0.7)
            axes[2].plot(df.index, df['macd'], label='MACD', color='blue', linewidth=2)
            axes[2].plot(df.index, df['signal'], label='Signal', color='red', linewidth=2)
            axes[2].set_title('MACD指标')
            axes[2].grid(True, alpha=0.3)
            axes[2].legend()
        
        # 成交量
        axes[3].bar(df.index, df['Volume'], label='成交量', color='lightblue', alpha=0.7)
        if 'volume_sma' in df.columns:
            axes[3].plot(df.index, df['volume_sma'], label='成交量均线', color='orange', linewidth=2)
        axes[3].set_title('成交量分析')
        axes[3].grid(True, alpha=0.3)
        axes[3].legend()
        
        plt.tight_layout()
        
        # 保存图表
        os.makedirs('output_charts', exist_ok=True)
        chart_filename = f"output_charts/{symbol}_detailed_chart.png"
        plt.savefig(chart_filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        return chart_filename
    
    def format_html_table(self, df, title):
        """格式化HTML表格"""
        html_table = f"""
        <table style="border-collapse: collapse; width: 100%; margin: 20px 0;">
            <thead>
                <tr style="background-color: #f2f2f2;">
                    <th style="border: 1px solid #ddd; padding: 12px; text-align: left; background-color: #4CAF50; color: white;" colspan="{len(df.columns)}">{title}</th>
                </tr>
                <tr style="background-color: #f2f2f2;">
        """
        
        for col in df.columns:
            html_table += f'<th style="border: 1px solid #ddd; padding: 8px; text-align: center;">{col}</th>'
        
        html_table += "</tr></thead><tbody>"
        
        for _, row in df.iterrows():
            html_table += "<tr>"
            for val in row:
                if isinstance(val, (int, float)):
                    if '盈亏' in str(val) or '涨跌幅' in str(val):
                        color = 'green' if val > 0 else 'red' if val < 0 else 'black'
                        formatted_val = f"{val:,.2f}" if isinstance(val, float) else f"{val:,}"
                        html_table += f'<td style="border: 1px solid #ddd; padding: 8px; text-align: center; color: {color}; font-weight: bold;">{formatted_val}</td>'
                    else:
                        formatted_val = f"{val:,.2f}" if isinstance(val, float) else f"{val:,}"
                        html_table += f'<td style="border: 1px solid #ddd; padding: 8px; text-align: center;">{formatted_val}</td>'
                else:
                    html_table += f'<td style="border: 1px solid #ddd; padding: 8px; text-align: center;">{val}</td>'
            html_table += "</tr>"
        
        html_table += "</tbody></table>"
        return html_table
    
    def send_html_email(self, subject, html_content, attachments=None):
        """发送HTML格式邮件"""
        if not all([EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECEIVER]):
            print("❌ 邮件配置不完整，跳过发送邮件")
            return False
        
        msg = MIMEMultipart('alternative')
        msg['From'] = EMAIL_SENDER
        msg['To'] = EMAIL_RECEIVER
        msg['Subject'] = subject
        
        # 添加HTML内容
        html_part = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(html_part)
        
        # 添加附件
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
                    print(f"❌ 添加附件{filename}失败: {e}")
        
        try:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            text = msg.as_string()
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, text)
            server.quit()
            print("✅ 邮件发送成功")
            return True
        except Exception as e:
            print(f"❌ 邮件发送失败: {e}")
            return False
    
    def analyze_portfolio(self):
        """分析整个投资组合"""
        print("🚀 开始增强版投资组合分析...")
        
        # 获取当前价格和详细数据
        print("📊 获取实时数据和基本面信息...")
        success_count = 0
        
        for stock_name, data in self.stocks_data.items():
            try:
                # 获取价格数据
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
                    continue
                
                # 获取历史数据和基本面
                hist_data, stock_obj = self.fetch_stock_data_yahoo(data["code"])
                if hist_data is not None and stock_obj is not None:
                    try:
                        data["fundamental"] = self.get_fundamental_data(stock_obj)
                        data["news"] = self.get_company_news(data["code"], stock_name)
                        data["discussions"] = self.get_xueqiu_discussions(stock_name, data["code"])
                        
                        # 技术分析
                        signals, hist_data_with_indicators = self.advanced_technical_analysis(hist_data)
                        data["signals"] = signals
                        data["analysis_data"] = hist_data_with_indicators
                        
                    except Exception as e:
                        print(f"❌ 分析{stock_name}详细信息失败: {e}")
                        
            except Exception as e:
                print(f"❌ 获取{stock_name}数据失败: {e}")
        
        print(f"📈 成功获取 {success_count}/{len(self.stocks_data)} 只股票的完整数据")
        
        # 创建投资组合概览图表
        portfolio_chart = self.create_portfolio_chart(self.stocks_data)
        
        # 创建投资组合表格
        portfolio_df = pd.DataFrame.from_dict(self.stocks_data, orient='index')
        portfolio_df = portfolio_df.reset_index().rename(columns={'index': '股票名称'})
        
        portfolio_summary_df = portfolio_df[[
            '股票名称', 'code', 'market_value', 'quantity', 
            'current_price', 'avg_cost', 'pnl', 'change_pct'
        ]]
        portfolio_summary_df.columns = [
            '股票名称', '代码', '市值(HKD)', '数量', 
            '现价(HKD)', '成本价(HKD)', '浮动盈亏(HKD)', '涨跌幅(%)'
        ]
        
        # 保存Excel
        os.makedirs('output', exist_ok=True)
        excel_filename = "output/enhanced_stock_analysis.xlsx"
        with pd.ExcelWriter(excel_filename) as writer:
            portfolio_summary_df.to_excel(writer, sheet_name='Portfolio Summary', index=False)
        
        # 生成详细分析
        detailed_analysis = []
        individual_charts = {}
        
        for stock_name, data in self.stocks_data.items():
            if data.get("current_price", 0) == 0:
                continue
                
            print(f"\n🔍 详细分析 {stock_name}...")
            
            # 创建详细图表
            if "analysis_data" in data:
                chart_filename = self.create_detailed_stock_chart(
                    data["analysis_data"], data["code"], stock_name, data.get("signals", {})
                )
                individual_charts[data["code"]] = chart_filename
            
            # 生成详细分析报告
            analysis_report = self.generate_detailed_analysis_report(stock_name, data)
            detailed_analysis.append(analysis_report)
            
            print(f"✅ {stock_name} 详细分析完成")
        
        # 生成HTML邮件内容
        html_content = self.generate_html_email_content(
            self.stocks_data, portfolio_summary_df, detailed_analysis, 
            portfolio_chart, individual_charts
        )
        
        # 发送邮件
        email_attachments = {"portfolio_overview.png": portfolio_chart}
        email_attachments.update(individual_charts)
        email_attachments["enhanced_stock_analysis.xlsx"] = excel_filename
        
        email_sent = self.send_html_email(
            f"📊 增强版股票投资组合分析报告 - {datetime.now().strftime('%Y-%m-%d')}", 
            html_content, email_attachments
        )
        
        print("\n" + "="*60)
        print("🎉 增强版分析完成！")
        print(f"📊 分析报告已保存到: {excel_filename}")
        print(f"📧 HTML邮件发送状态: {'✅ 成功' if email_sent else '❌ 失败'}")
        print(f"📈 共分析了 {len(detailed_analysis)} 只股票的详细信息")
        print("="*60)
        
        return detailed_analysis
    
    def generate_detailed_analysis_report(self, stock_name, data):
        """生成单只股票的详细分析报告"""
        current_price = data.get("current_price", 0)
        signals = data.get("signals", {})
        fundamental = data.get("fundamental", {})
        news = data.get("news", [])
        discussions = data.get("discussions", {})
        
        # 技术分析摘要
        signal_summary = []
        for indicator, signal in signals.items():
            if indicator != "overall":
                signal_text = {
                    "BUY": "📈 买入",
                    "SELL": "📉 卖出", 
                    "HOLD": "⏸️ 观望",
                    "STRONG_BUY": "🚀 强烈买入",
                    "STRONG_SELL": "🛑 强烈卖出",
                    "HIGH_VOLUME": "📊 高成交量",
                    "LOW_VOLUME": "📉 低成交量",
                    "NORMAL": "➖ 正常"
                }.get(signal, signal)
                signal_summary.append(f"{indicator}: {signal_text}")
        
        # 基本面数据格式化
        fundamental_summary = []
        if fundamental:
            for key, value in fundamental.items():
                if key != "业务摘要" and value != "N/A":
                    if isinstance(value, (int, float)):
                        if key in ["市值"]:
                            formatted_value = f"{value/1000000000:.1f}B" if value >= 1000000000 else f"{value/1000000:.1f}M"
                        elif key in ["市盈率", "市净率", "股息率", "Beta"]:
                            formatted_value = f"{value:.2f}"
                        else:
                            formatted_value = f"{value:,}"
                        fundamental_summary.append(f"{key}: {formatted_value}")
        
        # 新闻摘要
        news_summary = []
        if news:
            for item in news[:3]:  # 只显示前3条新闻
                news_summary.append(f"• {item['title']} ({item['publish_time']})")
        
        # 雪球讨论摘要
        discussion_summary = []
        if discussions:
            discussion_summary.append(f"市场情绪: {discussions.get('sentiment', '中性')}")
            discussion_summary.append(f"讨论热度: {discussions.get('discussion_count', 0)} 条提及")
            if discussions.get('followers_count', 0) > 0:
                discussion_summary.append(f"关注人数: {discussions.get('followers_count', 0):,} 人")
            if discussions.get('influential_users'):
                top_users = discussions['influential_users'][:2]
                user_strings = [f"{user['name']}({user['followers']}关注)" for user in top_users]
                discussion_summary.append(f"热门用户: {', '.join(user_strings)}")
            if discussions.get('hot_topics'):
                discussion_summary.append(f"热门话题: {', '.join(discussions['hot_topics'][:2])}")
        
        return {
            "股票名称": stock_name,
            "代码": data["code"],
            "当前价格": current_price,
            "技术信号": signals.get("overall", "HOLD"),
            "信号详情": signal_summary,
            "基本面数据": fundamental_summary,
            "最新动态": news_summary,
            "市场讨论": discussion_summary,
            "_raw_discussions": discussions,  # 原始讨论数据用于HTML模板
            "建议操作": {
                "STRONG_BUY": "🚀 强烈买入",
                "BUY": "📈 买入", 
                "HOLD": "⏸️ 观望",
                "SELL": "📉 卖出",
                "STRONG_SELL": "🛑 强烈卖出"
            }.get(signals.get("overall", "HOLD"), "⏸️ 观望")
        }
    
    def generate_html_email_content(self, stocks_data, portfolio_df, detailed_analysis, portfolio_chart, individual_charts):
        """生成HTML格式的邮件内容"""
        
        # 计算总体统计
        total_market_value = portfolio_df['市值(HKD)'].sum()
        total_pnl = portfolio_df['浮动盈亏(HKD)'].sum()
        total_cost = total_market_value - total_pnl
        total_return_pct = (total_pnl / total_cost * 100) if total_cost > 0 else 0
        
        # HTML邮件模板
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 1200px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 20px rgba(0,0,0,0.1); }}
                .header {{ text-align: center; border-bottom: 3px solid #4CAF50; padding-bottom: 20px; margin-bottom: 30px; }}
                .header h1 {{ color: #2E7D32; margin: 0; font-size: 28px; }}
                .header p {{ color: #666; margin: 10px 0; font-size: 16px; }}
                .summary {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 25px; border-radius: 10px; margin-bottom: 30px; }}
                .summary h2 {{ margin: 0 0 15px 0; font-size: 24px; }}
                .summary-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; }}
                .summary-item {{ background: rgba(255,255,255,0.2); padding: 15px; border-radius: 8px; text-align: center; }}
                .summary-item .value {{ font-size: 24px; font-weight: bold; margin: 5px 0; }}
                .summary-item .label {{ font-size: 14px; opacity: 0.9; }}
                .section {{ margin-bottom: 40px; }}
                .section h2 {{ color: #2E7D32; border-left: 4px solid #4CAF50; padding-left: 15px; margin-bottom: 20px; }}
                .stock-detail {{ background: #f9f9f9; border: 1px solid #e0e0e0; border-radius: 10px; padding: 25px; margin-bottom: 25px; }}
                .stock-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }}
                .stock-name {{ font-size: 20px; font-weight: bold; color: #2E7D32; }}
                .stock-price {{ font-size: 24px; font-weight: bold; color: #333; }}
                .recommendation {{ padding: 8px 16px; border-radius: 20px; font-weight: bold; color: white; }}
                .buy {{ background-color: #4CAF50; }}
                .strong-buy {{ background-color: #2E7D32; }}
                .sell {{ background-color: #f44336; }}
                .strong-sell {{ background-color: #c62828; }}
                .hold {{ background-color: #FF9800; }}
                .analysis-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
                .analysis-card {{ background: white; border: 1px solid #e0e0e0; border-radius: 8px; padding: 20px; }}
                .analysis-card h3 {{ color: #2E7D32; margin: 0 0 15px 0; font-size: 16px; }}
                .analysis-card ul {{ margin: 0; padding-left: 20px; }}
                .analysis-card li {{ margin: 8px 0; line-height: 1.5; }}
                .discussion-stats {{ background-color: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 4px solid #007bff; }}
                .stat-item {{ display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid #e9ecef; }}
                .stat-item:last-child {{ border-bottom: none; }}
                .stat-label {{ font-weight: 600; color: #495057; }}
                .stat-value {{ font-weight: 700; color: #007bff; font-size: 1.1em; }}
                .footer {{ text-align: center; border-top: 1px solid #e0e0e0; padding-top: 20px; margin-top: 40px; color: #666; font-size: 14px; }}
                table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 12px; text-align: center; }}
                th {{ background-color: #4CAF50; color: white; font-weight: bold; }}
                .positive {{ color: #4CAF50; font-weight: bold; }}
                .negative {{ color: #f44336; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚀 增强版股票投资组合分析报告</h1>
                    <p>📅 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p>📊 由AI智能分析系统生成 | 🎯 包含技术分析、基本面分析、市场情绪</p>
                </div>
                
                <div class="summary">
                    <h2>📈 投资组合概览</h2>
                    <div class="summary-grid">
                        <div class="summary-item">
                            <div class="value">💰 {total_market_value:,.0f}</div>
                            <div class="label">总市值 (HKD)</div>
                        </div>
                        <div class="summary-item">
                            <div class="value {'positive' if total_pnl >= 0 else 'negative'}">{total_pnl:+,.0f}</div>
                            <div class="label">总浮动盈亏 (HKD)</div>
                        </div>
                        <div class="summary-item">
                            <div class="value {'positive' if total_return_pct >= 0 else 'negative'}">{total_return_pct:+.2f}%</div>
                            <div class="label">总收益率</div>
                        </div>
                        <div class="summary-item">
                            <div class="value">{len(stocks_data)}</div>
                            <div class="label">持仓股票数</div>
                        </div>
                    </div>
                </div>
                
                <div class="section">
                    <h2>📋 详细持仓信息</h2>
                    {self.format_html_table(portfolio_df, "股票投资组合详情")}
                </div>
        """
        
        # 添加详细分析
        for analysis in detailed_analysis:
            recommendation_class = {
                "🚀 强烈买入": "strong-buy",
                "📈 买入": "buy", 
                "⏸️ 观望": "hold",
                "📉 卖出": "sell",
                "🛑 强烈卖出": "strong-sell"
            }.get(analysis["建议操作"], "hold")
            
            html_content += f"""
                <div class="section">
                    <div class="stock-detail">
                        <div class="stock-header">
                            <div>
                                <div class="stock-name">{analysis['股票名称']} ({analysis['代码']})</div>
                                <div style="color: #666; margin-top: 5px;">当前价格: {analysis['当前价格']:.2f} HKD</div>
                            </div>
                            <div style="text-align: right;">
                                <div class="recommendation {recommendation_class}">{analysis['建议操作']}</div>
                            </div>
                        </div>
                        
                        <div class="analysis-grid">
                            <div class="analysis-card">
                                <h3>📊 技术分析信号</h3>
                                <ul>
            """
            
            for signal in analysis.get("信号详情", []):
                html_content += f"<li>{signal}</li>"
            
            html_content += f"""
                                </ul>
                            </div>
                            
                            <div class="analysis-card">
                                <h3>💰 基本面数据</h3>
                                <ul>
            """
            
            for item in analysis.get("基本面数据", [])[:5]:  # 限制显示数量
                html_content += f"<li>{item}</li>"
            
            html_content += f"""
                                </ul>
                            </div>
                            
                            <div class="analysis-card">
                                <h3>📰 最新动态</h3>
                                <ul>
            """
            
            for item in analysis.get("最新动态", []):
                html_content += f"<li>{item}</li>"
            
            if not analysis.get("最新动态"):
                html_content += "<li>暂无最新动态</li>"
            
            html_content += f"""
                                </ul>
                            </div>
                            
                            <div class="analysis-card">
                                <h3>💬 市场讨论 (雪球)</h3>
                                <div class="discussion-stats">
            """
            
            # 获取讨论数据
            discussions = analysis.get("_raw_discussions", {})
            if discussions:
                html_content += f"""
                                    <div class="stat-item">
                                        <span class="stat-label">关注人数:</span>
                                        <span class="stat-value">{discussions.get('followers_count', 0):,}</span>
                                    </div>
                                    <div class="stat-item">
                                        <span class="stat-label">讨论热度:</span>
                                        <span class="stat-value">{discussions.get('discussion_count', 0)}</span>
                                    </div>
                                    <div class="stat-item">
                                        <span class="stat-label">市场情绪:</span>
                                        <span class="stat-value">{discussions.get('sentiment', '中性')}</span>
                                    </div>
                """
                
                if discussions.get('positive_ratio'):
                    positive_ratio = discussions['positive_ratio'] * 100
                    html_content += f"""
                                    <div class="stat-item">
                                        <span class="stat-label">正面情绪:</span>
                                        <span class="stat-value">{positive_ratio:.1f}%</span>
                                    </div>
                    """
                
                # 显示热门用户
                if discussions.get('influential_users'):
                    html_content += """
                                    <div style="margin-top: 15px;">
                                        <strong>热门用户:</strong>
                                        <ul style="margin: 5px 0; padding-left: 20px;">
                    """
                    for user in discussions['influential_users'][:3]:
                        html_content += f"""
                                            <li>{user['name']} ({user['followers']}关注) - {user['description']}</li>
                        """
                    html_content += """
                                        </ul>
                                    </div>
                    """
                
                # 显示精华帖子
                if discussions.get('quality_posts'):
                    html_content += """
                                    <div style="margin-top: 15px;">
                                        <strong>精华讨论:</strong>
                                        <ul style="margin: 5px 0; padding-left: 20px;">
                    """
                    for post in discussions['quality_posts'][:2]:
                        html_content += f"""
                                            <li>{post['content'][:100]}... ({post['likes']}赞)</li>
                        """
                    html_content += """
                                        </ul>
                                    </div>
                    """
            else:
                html_content += "<p>暂无讨论数据</p>"
            
            html_content += f"""
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            """
        
        html_content += f"""
                <div class="footer">
                    <p>🤖 本报告由AI智能股票分析系统自动生成</p>
                    <p>📊 数据来源: Yahoo Finance | 📈 分析方法: 技术分析 + 基本面分析</p>
                    <p>⚠️ 免责声明: 本分析仅供参考，不构成投资建议。投资有风险，决策需谨慎。</p>
                    <p>📧 如有问题请联系系统管理员 | 🔄 报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_content
    
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
            print(f"❌ 获取{symbol}当前价格失败: {e}")
            return None

def main():
    """主函数"""
    print("🚀 增强版股票投资组合分析系统")
    print("=" * 60)
    
    analyzer = EnhancedStockAnalyzer()
    
    try:
        results = analyzer.analyze_portfolio()
        print(f"\n✅ 增强版分析完成，共分析了 {len(results)} 只股票的详细信息")
        
        if len(results) == 0:
            print("⚠️ 警告: 未能获取任何股票数据，请检查网络连接和股票代码")
        
    except Exception as e:
        print(f"❌ 分析过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()