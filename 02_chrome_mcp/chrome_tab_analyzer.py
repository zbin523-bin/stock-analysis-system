#!/usr/bin/env python3
"""
Chrome标签页内容分析工具
通过Chrome DevTools Protocol分析当前打开的标签页
"""

import asyncio
import json
import sys
import websockets
import urllib.parse
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

class ChromeTabAnalyzer:
    def __init__(self):
        self.chrome_port = 9222  # Chrome远程调试端口
        self.ws_url = None
        
    async def connect_to_chrome(self) -> bool:
        """连接到Chrome远程调试端口"""
        try:
            # 获取Chrome标签页列表
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(f"http://localhost:{self.chrome_port}/json") as response:
                        if response.status == 200:
                            tabs = await response.json()
                            
                            # 找到当前活动标签页
                            active_tab = None
                            for tab in tabs:
                                if tab.get('type') == 'page' and tab.get('url'):
                                    active_tab = tab
                                    break
                            
                            if active_tab:
                                self.ws_url = active_tab['webSocketDebuggerUrl']
                                print(f"🔗 连接到标签页: {active_tab['title']}")
                                print(f"🌐 页面URL: {active_tab['url']}")
                                return True
                            else:
                                print("❌ 未找到活动标签页")
                                return False
                        else:
                            print(f"❌ 无法连接到Chrome (状态码: {response.status})")
                            return False
                            
                except Exception as e:
                    print(f"❌ 连接Chrome失败: {e}")
                    return False
                    
        except ImportError:
            print("❌ 需要安装aiohttp: pip install aiohttp")
            return False
    
    async def get_page_content(self) -> Dict[str, Any]:
        """获取页面内容"""
        if not self.ws_url:
            return {"error": "未连接到Chrome"}
        
        try:
            async with websockets.connect(self.ws_url) as websocket:
                # 启用页面域
                await websocket.send(json.dumps({
                    "id": 1,
                    "method": "Page.enable"
                }))
                
                # 启用DOM域
                await websocket.send(json.dumps({
                    "id": 2,
                    "method": "DOM.enable"
                }))
                
                # 获取页面HTML
                await websocket.send(json.dumps({
                    "id": 3,
                    "method": "DOM.getDocument",
                    "params": {"depth": -1, "pierce": True}
                }))
                
                # 获取页面标题
                await websocket.send(json.dumps({
                    "id": 4,
                    "method": "Page.getLayoutMetrics"
                }))
                
                # 等待响应
                responses = []
                for _ in range(4):
                    response = await websocket.recv()
                    responses.append(json.loads(response))
                
                # 提取页面内容
                content = await self._extract_content_via_script(websocket)
                
                return {
                    "content": content,
                    "responses": responses,
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            return {"error": f"获取页面内容失败: {e}"}
    
    async def _extract_content_via_script(self, websocket) -> str:
        """通过JavaScript提取页面内容"""
        try:
            # 执行JavaScript获取页面内容
            await websocket.send(json.dumps({
                "id": 5,
                "method": "Runtime.evaluate",
                "params": {
                    "expression": """
                    (function() {
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
                        
                        // 获取页面信息
                        const pageInfo = {
                            title: document.title,
                            url: window.location.href,
                            description: document.querySelector('meta[name="description"]')?.content || '',
                            keywords: document.querySelector('meta[name="keywords"]')?.content || '',
                            author: document.querySelector('meta[name="author"]')?.content || '',
                            content: contentElement.innerText || contentElement.textContent || '',
                            wordCount: (contentElement.innerText || contentElement.textContent || '').split(' ').length,
                            links: Array.from(document.querySelectorAll('a[href]')).map(a => a.href).slice(0, 10),
                            images: Array.from(document.querySelectorAll('img[src]')).map(img => img.src).slice(0, 5)
                        };
                        
                        return JSON.stringify(pageInfo);
                    })()
                    """,
                    "returnByValue": True
                }
            }))
            
            response = await websocket.recv()
            result = json.loads(response)
            
            if result.get('result', {}).get('result', {}).get('value'):
                page_data = json.loads(result['result']['result']['value'])
                return page_data
            else:
                return {"error": "无法提取页面内容"}
                
        except Exception as e:
            return {"error": f"JavaScript执行失败: {e}"}
    
    def format_analysis(self, data: Dict[str, Any]) -> str:
        """格式化分析结果"""
        if isinstance(data, dict) and 'error' in data:
            return f"❌ 分析失败: {data['error']}"
        
        if isinstance(data, dict) and 'content' in data and isinstance(data['content'], dict):
            content = data['content']
            
            return f"""
📄 Chrome标签页分析报告
============================

🔗 页面URL: {content.get('url', '未知')}
📰 页面标题: {content.get('title', '无标题')}
⏰ 分析时间: {data.get('timestamp', '未知时间')}

📝 页面描述: {content.get('description', '无描述')}

📝 作者: {content.get('author', '未知作者')}

🏷️ 关键词: {content.get('keywords', '无关键词')}

📊 内容统计: {content.get('wordCount', 0)} 词

🔗 相关链接:
{chr(10).join(f'  • {link}' for link in content.get('links', [])[:5])}

🖼️ 页面图片:
{chr(10).join(f'  • {img}' for img in content.get('images', [])[:3])}

📋 主要内容:
------------------
{self._truncate_text(content.get('content', ''), 1000)}

📈 内容摘要:
------------------
{self._generate_summary(content.get('content', ''))}
            """.strip()
        
        return "❌ 无法解析页面数据"
    
    def _truncate_text(self, text: str, max_length: int) -> str:
        """截断文本"""
        if len(text) <= max_length:
            return text
        return text[:max_length] + "..."
    
    def _generate_summary(self, text: str) -> str:
        """生成内容摘要"""
        if not text:
            return "无内容"
        
        # 简单的摘要生成
        sentences = text.split('。')
        if len(sentences) > 2:
            return sentences[0] + '。' + sentences[1] + '。'
        else:
            return text[:200] + (text[200:] if len(text) <= 200 else '...')
    
    def save_result(self, data: Dict[str, Any], filename: Optional[str] = None) -> str:
        """保存结果到文件"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"chrome_tab_analysis_{timestamp}.json"
        
        filepath = Path(filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"📁 结果已保存到: {filepath}")
        return str(filepath)

async def check_chrome_remote_debugging():
    """检查Chrome远程调试是否启用"""
    import aiohttp
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:9222/json") as response:
                if response.status == 200:
                    tabs = await response.json()
                    print(f"✅ Chrome远程调试已启用，发现 {len(tabs)} 个标签页")
                    return True
                else:
                    print("❌ Chrome远程调试未启用")
                    return False
    except:
        print("❌ 无法连接到Chrome远程调试端口")
        return False

async def show_setup_instructions():
    """显示Chrome远程调试设置说明"""
    print("""
🔧 Chrome远程调试设置说明
============================

1. 关闭所有Chrome窗口

2. 重新启动Chrome并启用远程调试：
   macOS:
   ```
   /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome --remote-debugging-port=9222
   ```
   
   Windows:
   ```
   "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" --remote-debugging-port=9222
   ```

3. 或者创建Chrome快捷方式，添加启动参数：
   ```
   --remote-debugging-port=9222
   ```

4. 验证设置：
   打开浏览器访问: http://localhost:9222/json

5. 然后重新运行此脚本

⚠️  注意：远程调试模式存在安全风险，请仅在可信环境中使用
    """)

async def main():
    """主函数"""
    print("🚀 Chrome标签页分析工具")
    print("=" * 50)
    
    # 检查Chrome远程调试是否启用
    if not await check_chrome_remote_debugging():
        await show_setup_instructions()
        return
    
    analyzer = ChromeTabAnalyzer()
    
    try:
        # 连接到Chrome
        if not await analyzer.connect_to_chrome():
            print("❌ 无法连接到Chrome")
            return
        
        print("🔍 正在分析页面内容...")
        
        # 获取页面内容
        data = await analyzer.get_page_content()
        
        # 显示分析结果
        print(analyzer.format_analysis(data))
        
        # 保存结果
        analyzer.save_result(data)
        
        print("✅ 分析完成！")
        
    except KeyboardInterrupt:
        print("\n⏹️  分析已取消")
    except Exception as e:
        print(f"❌ 分析失败: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  程序已退出")
    except Exception as e:
        print(f"❌ 程序运行错误: {e}")