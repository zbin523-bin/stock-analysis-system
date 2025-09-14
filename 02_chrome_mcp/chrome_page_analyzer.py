#!/usr/bin/env python3
"""
Chrome页面分析工具 - URL输入版本
通过输入URL分析任何网页的关键信息
"""

import asyncio
import json
import sys
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

class ChromePageAnalyzer:
    def __init__(self):
        self.config = {
            "headless": True,
            "viewport": {"width": 1280, "height": 720},
            "timeout": 30000,
            "wait_until": "networkidle"
        }

    async def analyze_page(self, url: str) -> Dict[str, Any]:
        """分析网页内容"""
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError("Playwright未安装，请运行: pip install playwright")

        try:
            async with async_playwright() as p:
                # 启动浏览器
                browser = await p.chromium.launch(headless=self.config["headless"])
                page = await browser.new_page()
                
                # 设置视窗大小
                await page.set_viewport_size(self.config["viewport"])
                
                print(f"🌐 正在分析页面: {url}")
                
                # 导航到页面
                await page.goto(url, wait_until=self.config["wait_until"], timeout=self.config["timeout"])
                
                # 等待页面加载完成
                await page.wait_for_timeout(3000)
                
                # 获取页面信息
                title = await page.title()
                
                # 执行JavaScript分析页面
                analysis = await self._analyze_page_content(page)
                
                await browser.close()
                
                return {
                    "url": url,
                    "title": title,
                    "analysis": analysis,
                    "timestamp": datetime.now().isoformat(),
                    "analysis_summary": self._generate_analysis_summary(analysis)
                }
                
        except Exception as e:
            raise Exception(f"页面分析失败: {str(e)}")

    async def _analyze_page_content(self, page) -> Dict[str, Any]:
        """分析页面内容"""
        return await page.evaluate('''
            () => {
                // 页面基本信息
                const pageInfo = {
                    title: document.title,
                    url: window.location.href,
                    domain: window.location.hostname,
                    protocol: window.location.protocol,
                    language: document.documentElement.lang || 'unknown'
                };
                
                // 元数据提取
                const metadata = {};
                const metaTags = document.querySelectorAll('meta');
                metaTags.forEach(tag => {
                    const name = tag.getAttribute('name') || tag.getAttribute('property');
                    const content = tag.getAttribute('content');
                    if (name && content) {
                        metadata[name] = content;
                    }
                });
                
                // 主要内容区域识别
                const mainSelectors = [
                    'main', 'article', '.main', '.content', '.post',
                    '.article', '[role="main"]', '.main-content',
                    '.post-content', '.entry-content', '.article-content'
                ];
                
                let mainElement = null;
                for (const selector of mainSelectors) {
                    const element = document.querySelector(selector);
                    if (element && element.innerText.length > 100) {
                        mainElement = element;
                        break;
                    }
                }
                
                const contentElement = mainElement || document.body;
                
                // 内容统计
                const content = contentElement.innerText || contentElement.textContent || '';
                const wordCount = content.split(/\\s+/).filter(word => word.length > 0).length;
                const charCount = content.length;
                
                // 链接分析
                const links = Array.from(document.querySelectorAll('a[href]'));
                const internalLinks = links.filter(link => {
                    const href = link.href;
                    return href && (href.includes(window.location.hostname) || href.startsWith('/'));
                });
                const externalLinks = links.filter(link => {
                    const href = link.href;
                    return href && !href.includes(window.location.hostname) && href.startsWith('http');
                });
                
                // 图片分析
                const images = Array.from(document.querySelectorAll('img[src]'));
                const imagesWithAlt = images.filter(img => img.alt && img.alt.trim() !== '');
                
                // 标题结构分析
                const headings = {
                    h1: document.querySelectorAll('h1').length,
                    h2: document.querySelectorAll('h2').length,
                    h3: document.querySelectorAll('h3').length,
                    h4: document.querySelectorAll('h4').length,
                    h5: document.querySelectorAll('h5').length,
                    h6: document.querySelectorAll('h6').length
                };
                
                // 表单分析
                const forms = document.querySelectorAll('form').length;
                const inputs = document.querySelectorAll('input, textarea, select').length;
                
                // 表格分析
                const tables = document.querySelectorAll('table').length;
                
                // 视频分析
                const videos = document.querySelectorAll('video').length;
                const iframes = document.querySelectorAll('iframe').length;
                
                // 关键内容提取
                const keyContent = {
                    description: metadata.description || metadata['og:description'] || '',
                    keywords: metadata.keywords || metadata['og:keywords'] || '',
                    author: metadata.author || metadata['article:author'] || '',
                    publishDate: metadata['article:published_time'] || 
                                  document.querySelector('time')?.getAttribute('datetime') ||
                                  metadata.publish_date || '',
                    mainHeading: document.querySelector('h1')?.innerText || '',
                    summary: this._extractSummary(content)
                };
                
                return {
                    pageInfo,
                    metadata,
                    contentStats: {
                        wordCount,
                        charCount,
                        readingTime: Math.ceil(wordCount / 200) // 假设每分钟阅读200词
                    },
                    linkAnalysis: {
                        totalLinks: links.length,
                        internalLinks: internalLinks.length,
                        externalLinks: externalLinks.length
                    },
                    imageAnalysis: {
                        totalImages: images.length,
                        imagesWithAlt: imagesWithAlt.length,
                        accessibilityScore: images.length > 0 ? (imagesWithAlt.length / images.length * 100) : 100
                    },
                    structureAnalysis: {
                        headings,
                        forms,
                        inputs,
                        tables,
                        videos,
                        iframes
                    },
                    keyContent,
                    pageType: this._detectPageType(metadata, content),
                    seoScore: this._calculateSEOScore(metadata, headings, images)
                };
            }
            
            function _extractSummary(content) {
                // 提取内容摘要
                const sentences = content.split(/[.!?。！？]/).filter(s => s.trim().length > 10);
                return sentences.slice(0, 3).join('. ') + (sentences.length > 3 ? '.' : '');
            }
            
            function _detectPageType(metadata, content) {
                // 检测页面类型
                const url = window.location.href.toLowerCase();
                const title = document.title.toLowerCase();
                
                if (url.includes('article') || url.includes('post') || url.includes('blog') || metadata['og:type'] === 'article') {
                    return '文章页面';
                } else if (url.includes('product') || url.includes('item') || metadata['og:type'] === 'product') {
                    return '产品页面';
                } else if (url.includes('category') || url.includes('tag')) {
                    return '分类页面';
                } else if (url.includes('search') || url.includes('query')) {
                    return '搜索页面';
                } else if (url.includes('home') || url === '/' || url.includes('index')) {
                    return '首页';
                } else if (url.includes('about')) {
                    return '关于页面';
                } else if (url.includes('contact')) {
                    return '联系页面';
                } else if (content.includes('login') || content.includes('sign in')) {
                    return '登录页面';
                } else {
                    return '通用页面';
                }
            }
            
            function _calculateSEOScore(metadata, headings, images) {
                let score = 0;
                
                // 标题分 (30分)
                if (document.title && document.title.length > 10) score += 15;
                if (document.title.length <= 60) score += 15;
                
                // 描述分 (20分)
                if (metadata.description && metadata.description.length > 50) score += 20;
                
                // 关键词分 (10分)
                if (metadata.keywords) score += 10;
                
                // 标题结构分 (20分)
                if (headings.h1 === 1) score += 10;
                if (headings.h2 > 0) score += 10;
                
                // 图片优化分 (10分)
                if (images.length > 0) {
                    const altRatio = images.filter(img => img.alt).length / images.length;
                    score += Math.round(altRatio * 10);
                }
                
                // 内容长度分 (10分)
                const content = document.body.innerText || '';
                if (content.length > 300) score += 10;
                
                return Math.min(100, score);
            }
        ''')

    def _generate_analysis_summary(self, analysis: Dict[str, Any]) -> str:
        """生成分析摘要"""
        if not analysis:
            return "无法生成分析摘要"
        
        try:
            summary_parts = []
            
            # 页面类型
            page_type = analysis.get('pageType', '未知类型')
            summary_parts.append(f"这是一个{page_type}")
            
            # 内容统计
            content_stats = analysis.get('contentStats', {})
            word_count = content_stats.get('wordCount', 0)
            reading_time = content_stats.get('readingTime', 0)
            summary_parts.append(f"包含{word_count}词，预计阅读时间{reading_time}分钟")
            
            # 页面结构
            headings = analysis.get('structureAnalysis', {}).get('headings', {})
            if headings.get('h1') == 1:
                summary_parts.append("页面结构良好")
            elif headings.get('h1') == 0:
                summary_parts.append("缺少H1标题")
            elif headings.get('h1') > 1:
                summary_parts.append("存在多个H1标题")
            
            # SEO评分
            seo_score = analysis.get('seoScore', 0)
            if seo_score >= 80:
                summary_parts.append(f"SEO优化良好({seo_score}分)")
            elif seo_score >= 60:
                summary_parts.append(f"SEO优化一般({seo_score}分)")
            else:
                summary_parts.append(f"需要SEO优化({seo_score}分)")
            
            # 图片优化
            image_analysis = analysis.get('imageAnalysis', {})
            accessibility_score = image_analysis.get('accessibilityScore', 0)
            if accessibility_score < 100:
                summary_parts.append(f"图片可访问性得分{accessibility_score}%")
            
            return "，".join(summary_parts) + "。"
            
        except Exception as e:
            return f"分析摘要生成失败: {e}"

    def format_analysis_report(self, data: Dict[str, Any]) -> str:
        """格式化分析报告"""
        if isinstance(data, dict) and 'error' in data:
            return f"❌ 分析失败: {data['error']}"
        
        analysis = data.get('analysis', {})
        
        return f"""
📄 Chrome页面分析报告
============================

🔗 页面URL: {data.get('url', '未知')}
📰 页面标题: {data.get('title', '无标题')}
🏷️ 页面类型: {analysis.get('pageType', '未知')}
🌐 语言: {analysis.get('pageInfo', {}).get('language', '未知')}
⏰ 分析时间: {data.get('timestamp', '未知时间')}

📊 内容统计:
• 字数: {analysis.get('contentStats', {}).get('wordCount', 0)} 词
• 字符数: {analysis.get('contentStats', {}).get('charCount', 0)} 字符
• 预计阅读时间: {analysis.get('contentStats', {}).get('readingTime', 0)} 分钟

🔗 链接分析:
• 总链接数: {analysis.get('linkAnalysis', {}).get('totalLinks', 0)}
• 内部链接: {analysis.get('linkAnalysis', {}).get('internalLinks', 0)}
• 外部链接: {analysis.get('linkAnalysis', {}).get('externalLinks', 0)}

🖼️ 图片分析:
• 总图片数: {analysis.get('imageAnalysis', {}).get('totalImages', 0)}
• 有ALT文本: {analysis.get('imageAnalysis', {}).get('imagesWithAlt', 0)}
• 可访问性得分: {analysis.get('imageAnalysis', {}).get('accessibilityScore', 0):.1f}%

📋 页面结构:
• H1标题: {analysis.get('structureAnalysis', {}).get('headings', {}).get('h1', 0)} 个
• H2标题: {analysis.get('structureAnalysis', {}).get('headings', {}).get('h2', 0)} 个
• H3标题: {analysis.get('structureAnalysis', {}).get('headings', {}).get('h3', 0)} 个
• 表单: {analysis.get('structureAnalysis', {}).get('forms', 0)} 个
• 表格: {analysis.get('structureAnalysis', {}).get('tables', 0)} 个
• 视频: {analysis.get('structureAnalysis', {}).get('videos', 0)} 个
• iframe: {analysis.get('structureAnalysis', {}).get('iframes', 0)} 个

📈 SEO评分: {analysis.get('seoScore', 0)}/100

📝 关键内容:
• 描述: {analysis.get('keyContent', {}).get('description', '无描述')}
• 作者: {analysis.get('keyContent', {}).get('author', '未知作者')}
• 发布时间: {analysis.get('keyContent', {}).get('publishDate', '未知时间')}
• 主要标题: {analysis.get('keyContent', {}).get('mainHeading', '无主要标题')}

📋 内容摘要:
{analysis.get('keyContent', {}).get('summary', '无摘要')}

🎯 分析总结:
{data.get('analysis_summary', '无法生成总结')}

💡 优化建议:
{self._generate_optimization_suggestions(analysis)}
        """.strip()

    def _generate_optimization_suggestions(self, analysis: Dict[str, Any]) -> str:
        """生成优化建议"""
        suggestions = []
        
        # SEO建议
        seo_score = analysis.get('seoScore', 0)
        if seo_score < 80:
            suggestions.append("• 建议优化SEO配置")
        
        # 标题建议
        headings = analysis.get('structureAnalysis', {}).get('headings', {})
        if headings.get('h1') == 0:
            suggestions.append("• 添加H1标题")
        elif headings.get('h1') > 1:
            suggestions.append("• 页面应有且仅有一个H1标题")
        
        # 图片建议
        accessibility_score = analysis.get('imageAnalysis', {}).get('accessibilityScore', 0)
        if accessibility_score < 100:
            suggestions.append("• 为所有图片添加ALT文本")
        
        # 内容建议
        word_count = analysis.get('contentStats', {}).get('wordCount', 0)
        if word_count < 300:
            suggestions.append("• 建议增加内容长度")
        
        # 链接建议
        external_links = analysis.get('linkAnalysis', {}).get('externalLinks', 0)
        if external_links == 0:
            suggestions.append("• 添加相关的外部链接")
        
        return '\n'.join(suggestions) if suggestions else "• 页面优化良好，暂无特别建议"

    def save_result(self, data: Dict[str, Any], filename: Optional[str] = None) -> str:
        """保存结果到文件"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"page_analysis_{timestamp}.json"
        
        filepath = Path(filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"📁 结果已保存到: {filepath}")
        return str(filepath)

async def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("❌ 使用方法: python3 chrome_page_analyzer.py <URL>")
        print("示例: python3 chrome_page_analyzer.py https://www.example.com")
        print("\n🌐 支持的网站类型:")
        print("  • 新闻网站 (新浪、腾讯、网易等)")
        print("  • 技术博客 (CSDN、博客园、掘金等)")
        print("  • 官方文档 (各大技术平台)")
        print("  • 电商平台 (淘宝、京东等)")
        print("  • 社交媒体 (微博、知乎等)")
        sys.exit(1)
    
    url = sys.argv[1]
    
    # 验证URL格式
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    analyzer = ChromePageAnalyzer()
    
    try:
        print("🚀 开始分析页面...")
        result = await analyzer.analyze_page(url)
        
        # 显示分析报告
        print(analyzer.format_analysis_report(result))
        
        # 保存结果
        analyzer.save_result(result)
        
        print("✅ 页面分析完成！")
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())