#!/usr/bin/env python3
"""
Chrome页面内容获取工具
使用Playwright获取网页的主要内容
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

class ChromeContentExtractor:
    def __init__(self):
        self.config = {
            "headless": True,
            "viewport": {"width": 1280, "height": 720},
            "timeout": 30000,
            "wait_until": "networkidle"
        }

    async def extract_content(self, url: str) -> Dict[str, Any]:
        """提取网页内容"""
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError("Playwright未安装，请运行: pip install playwright")

        try:
            async with async_playwright() as p:
                # 启动浏览器
                browser = await p.chromium.launch(headless=self.config["headless"])
                page = await browser.new_page()
                
                # 设置视窗大小
                await page.set_viewport_size(self.config["viewport"])
                
                print(f"🌐 正在访问: {url}")
                
                # 导航到页面
                await page.goto(url, wait_until=self.config["wait_until"], timeout=self.config["timeout"])
                
                # 等待页面加载完成
                await page.wait_for_timeout(2000)
                
                # 提取页面信息
                title = await page.title()
                
                # 提取页面内容
                content = await self._extract_page_content(page)
                
                # 提取元数据
                metadata = await self._extract_metadata(page)
                
                await browser.close()
                
                return {
                    "url": url,
                    "title": title,
                    "content": content,
                    "metadata": metadata,
                    "timestamp": datetime.now().isoformat(),
                    "word_count": len(content.split()),
                    "reading_time": max(1, len(content.split()) // 200)
                }
                
        except Exception as e:
            raise Exception(f"内容提取失败: {str(e)}")

    async def _extract_page_content(self, page) -> str:
        """提取页面主要内容"""
        content = await page.evaluate('''
            () => {
                // 移除不需要的元素
                const selectorsToRemove = [
                    'nav', 'header', 'footer', 'aside',
                    '.nav', '.navigation', '.menu', '.sidebar',
                    '.ads', '.advertisement', '.comments', '.comment-section',
                    '.social-share', '.share-buttons', '.related-posts',
                    'script', 'style', 'noscript', 'iframe'
                ];
                
                selectorsToRemove.forEach(selector => {
                    document.querySelectorAll(selector).forEach(el => el.remove());
                });
                
                // 尝试找到主要内容区域
                const mainSelectors = [
                    'main', 'article', '.main', '.content', '.post',
                    '.article', '[role="main"]', '.main-content'
                ];
                
                let mainElement = null;
                for (const selector of mainSelectors) {
                    mainElement = document.querySelector(selector);
                    if (mainElement && mainElement.innerText.length > 100) {
                        break;
                    }
                }
                
                // 如果没有找到主要内容区域，使用body
                const contentElement = mainElement || document.body;
                
                // 获取文本内容
                let text = contentElement.innerText || contentElement.textContent || '';
                
                // 清理文本
                text = text
                    .replace(/\\s+/g, ' ')  // 合并空白字符
                    .replace(/\\n\\s*\\n\\s*\\n/g, '\\n\\n')  // 移除多余的空行
                    .trim();
                
                return text;
            }
        ''');
        
        return content

    async def _extract_metadata(self, page) -> Dict[str, Any]:
        """提取页面元数据"""
        return await page.evaluate('''
            () => {
                const metadata = {};
                
                // 提取meta标签
                const metaTags = document.querySelectorAll('meta');
                metaTags.forEach(tag => {
                    const name = tag.getAttribute('name') || tag.getAttribute('property');
                    const content = tag.getAttribute('content');
                    if (name && content) {
                        metadata[name] = content;
                    }
                });
                
                // 提取基本信息
                metadata['author'] = metadata['author'] || 
                                   document.querySelector('meta[name="author"]')?.getAttribute('content') ||
                                   document.querySelector('.author')?.innerText ||
                                   '';
                
                metadata['description'] = metadata['description'] || 
                                        document.querySelector('meta[name="description"]')?.getAttribute('content') ||
                                        '';
                
                metadata['keywords'] = metadata['keywords'] || 
                                      document.querySelector('meta[name="keywords"]')?.getAttribute('content') ||
                                      '';
                
                // 提取发布时间
                metadata['publish_date'] = metadata['article:published_time'] || 
                                          metadata['publish_date'] ||
                                          document.querySelector('time')?.getAttribute('datetime') ||
                                          '';
                
                return metadata;
            }
        ''');

    def format_result(self, result: Dict[str, Any]) -> str:
        """格式化结果输出"""
        return f"""
📄 页面内容分析报告
============================

🔗 页面URL: {result['url']}
📰 页面标题: {result['title']}
⏰ 提取时间: {result['timestamp']}
📊 内容统计: {result['word_count']} 词，预计阅读 {result['reading_time']} 分钟

📝 页面描述: {result['metadata'].get('description', '无描述')}

📝 作者: {result['metadata'].get('author', '未知作者')}

📅 发布时间: {result['metadata'].get('publish_date', '未知时间')}

🏷️ 关键词: {result['metadata'].get('keywords', '无关键词')}

📋 主要内容:
------------------
{self._truncate_text(result['content'], 1500)}

📈 内容摘要:
------------------
{self._generate_summary(result['content'])}
        """.strip()

    def _truncate_text(self, text: str, max_length: int) -> str:
        """截断文本"""
        if len(text) <= max_length:
            return text
        return text[:max_length] + "..."

    def _generate_summary(self, text: str) -> str:
        """生成内容摘要"""
        # 简单的摘要生成：取前两个句子
        sentences = re.split(r'[.!?。！？]', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) >= 2:
            summary = '. '.join(sentences[:2]) + '.'
        else:
            summary = text[:200] + (text[200:] if len(text) <= 200 else '...')
        
        return summary

    def save_result(self, result: Dict[str, Any], filename: Optional[str] = None) -> str:
        """保存结果到文件"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"page_content_{timestamp}.json"
        
        filepath = Path(filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"📁 结果已保存到: {filepath}")
        return str(filepath)

async def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("❌ 使用方法: python chrome_content_extractor.py <URL>")
        print("示例: python chrome_content_extractor.py https://example.com")
        sys.exit(1)
    
    url = sys.argv[1]
    
    # 验证URL格式
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    extractor = ChromeContentExtractor()
    
    try:
        print("🚀 开始提取页面内容...")
        result = await extractor.extract_content(url)
        
        # 显示结果
        print(extractor.format_result(result))
        
        # 保存结果
        extractor.save_result(result)
        
        print("✅ 内容提取完成！")
        
    except Exception as e:
        print(f"❌ 提取失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())