#!/usr/bin/env node

/**
 * Chrome页面内容获取工具
 * 使用Playwright MCP服务器获取当前页面的主要内容
 */

const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

class ChromeContentExtractor {
    constructor() {
        this.isConfigured = false;
        this.configPath = path.join(process.env.HOME, '.config', 'claude', 'chrome-mcp-config.json');
    }

    /**
     * 检查并配置MCP服务器
     */
    async setupMCPServer() {
        try {
            // 检查配置文件
            if (!fs.existsSync(this.configPath)) {
                await this.createConfig();
            }

            // 启动MCP服务器
            console.log('正在启动Chrome MCP服务器...');
            const serverProcess = spawn('npx', ['@playwright/mcp'], {
                stdio: ['pipe', 'pipe', 'pipe']
            });

            this.serverProcess = serverProcess;
            this.isConfigured = true;

            // 等待服务器启动
            await new Promise(resolve => setTimeout(resolve, 2000));

            console.log('Chrome MCP服务器已启动');
            return true;
        } catch (error) {
            console.error('MCP服务器配置失败:', error.message);
            return false;
        }
    }

    /**
     * 创建配置文件
     */
    async createConfig() {
        const config = {
            "mcpServers": {
                "playwright": {
                    "command": "npx",
                    "args": ["@playwright/mcp"],
                    "env": {}
                }
            },
            "browser": {
                "headless": false,
                "viewport": { "width": 1280, "height": 720 },
                "timeout": 30000
            },
            "extraction": {
                "maxContentLength": 10000,
                "includeImages": false,
                "includeStyles": false,
                "mainContentOnly": true
            }
        };

        const configDir = path.dirname(this.configPath);
        if (!fs.existsSync(configDir)) {
            fs.mkdirSync(configDir, { recursive: true });
        }

        fs.writeFileSync(this.configPath, JSON.stringify(config, null, 2));
        console.log('配置文件已创建:', this.configPath);
    }

    /**
     * 获取页面内容
     */
    async getPageContent(url = null) {
        if (!this.isConfigured) {
            const success = await this.setupMCPServer();
            if (!success) {
                throw new Error('无法配置MCP服务器');
            }
        }

        try {
            // 如果没有提供URL，尝试获取当前活动页面
            if (!url) {
                url = await this.getActivePageUrl();
            }

            console.log('正在获取页面内容:', url);

            // 使用Playwright获取页面内容
            const content = await this.extractContentWithPlaywright(url);
            
            // 提取主要内容
            const mainContent = this.extractMainContent(content);
            
            return {
                url: url,
                title: this.extractTitle(content),
                mainContent: mainContent,
                fullContent: content,
                timestamp: new Date().toISOString(),
                wordCount: mainContent.split(' ').length,
                readingTime: Math.ceil(mainContent.split(' ').length / 200) // 假设每分钟阅读200词
            };

        } catch (error) {
            console.error('获取页面内容失败:', error.message);
            throw error;
        }
    }

    /**
     * 使用Playwright提取内容
     */
    async extractContentWithPlaywright(url) {
        return new Promise((resolve, reject) => {
            const pythonScript = `
import asyncio
from playwright.async_api import async_playwright
import json

async def extract_content(url):
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # 设置视窗大小
            await page.set_viewport_size({"width": 1280, "height": 720})
            
            # 导航到页面
            await page.goto(url, wait_until="networkidle", timeout=30000)
            
            # 等待页面加载完成
            await page.wait_for_timeout(2000)
            
            # 提取页面内容
            title = await page.title()
            
            # 提取主要内容（去除导航、广告等）
            content = await page.evaluate('''
                () => {
                    // 移除不需要的元素
                    const elementsToRemove = [
                        'nav', 'header', 'footer', 'aside',
                        '.nav', '.navigation', '.menu', '.sidebar',
                        '.ads', '.advertisement', '.comments',
                        'script', 'style', 'noscript'
                    ];
                    
                    elementsToRemove.forEach(selector => {
                        document.querySelectorAll(selector).forEach(el => el.remove());
                    });
                    
                    // 提取主要内容
                    const mainContent = document.querySelector('main') || 
                                     document.querySelector('.main') || 
                                     document.querySelector('.content') || 
                                     document.querySelector('article') || 
                                     document.body;
                    
                    return mainContent ? mainContent.innerText : document.body.innerText;
                }
            ''');
            
            await browser.close()
            
            return {
                'title': title,
                'content': content,
                'url': url
            }
            
    except Exception as e:
        return {'error': str(e)}

# 执行内容提取
result = asyncio.run(extract_content('${url}'))
print(json.dumps(result, ensure_ascii=False))
            `;

            const pythonProcess = spawn('python3', ['-c', pythonScript]);
            
            let output = '';
            let error = '';

            pythonProcess.stdout.on('data', (data) => {
                output += data.toString();
            });

            pythonProcess.stderr.on('data', (data) => {
                error += data.toString();
            });

            pythonProcess.on('close', (code) => {
                if (code !== 0) {
                    reject(new Error(`Python script failed with code ${code}: ${error}`));
                    return;
                }

                try {
                    const result = JSON.parse(output);
                    if (result.error) {
                        reject(new Error(result.error));
                    } else {
                        resolve(result.content || result.title || '无法提取内容');
                    }
                } catch (parseError) {
                    reject(new Error('无法解析Python脚本输出'));
                }
            });

        });
    }

    /**
     * 提取页面标题
     */
    extractTitle(content) {
        const titleMatch = content.match(/<title[^>]*>([^<]+)<\/title>/i);
        return titleMatch ? titleMatch[1].trim() : '无标题';
    }

    /**
     * 提取主要内容
     */
    extractMainContent(content) {
        // 如果内容已经是纯文本，直接返回
        if (!content.includes('<')) {
            return content;
        }

        // 移除HTML标签，保留文本内容
        return content
            .replace(/<script[^>]*>[\s\S]*?<\/script>/gi, '')
            .replace(/<style[^>]*>[\s\S]*?<\/style>/gi, '')
            .replace(/<[^>]+>/g, '')
            .replace(/\s+/g, ' ')
            .trim();
    }

    /**
     * 获取当前活动页面URL（需要浏览器扩展支持）
     */
    async getActivePageUrl() {
        // 由于我们无法直接访问浏览器的当前页面，
        // 这里返回一个示例URL或要求用户输入
        const readline = require('readline');
        const rl = readline.createInterface({
            input: process.stdin,
            output: process.stdout
        });

        return new Promise((resolve) => {
            rl.question('请输入要分析的页面URL: ', (url) => {
                rl.close();
                resolve(url);
            });
        });
    }

    /**
     * 格式化输出结果
     */
    formatResult(result) {
        return `
📄 页面内容分析报告
============================

🔗 页面URL: ${result.url}
📰 页面标题: ${result.title}
⏰ 提取时间: ${result.timestamp}
📊 内容统计: ${result.wordCount} 词，预计阅读 ${result.readingTime} 分钟

📋 主要内容:
------------------
${result.mainContent.substring(0, 1000)}${result.mainContent.length > 1000 ? '...' : ''}

📈 内容摘要:
------------------
${this.generateSummary(result.mainContent)}
        `.trim();
    }

    /**
     * 生成内容摘要
     */
    generateSummary(content) {
        // 简单的摘要生成（前200个字符）
        return content.substring(0, 200) + (content.length > 200 ? '...' : '');
    }

    /**
     * 保存结果到文件
     */
    saveResult(result, filename = null) {
        if (!filename) {
            const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
            filename = `page-content-${timestamp}.json`;
        }

        const filepath = path.join(process.cwd(), filename);
        fs.writeFileSync(filepath, JSON.stringify(result, null, 2));
        console.log('结果已保存到:', filepath);
        return filepath;
    }

    /**
     * 清理资源
     */
    cleanup() {
        if (this.serverProcess) {
            this.serverProcess.kill();
        }
    }
}

// 主函数
async function main() {
    const extractor = new ChromeContentExtractor();
    
    try {
        const url = process.argv[2]; // 从命令行参数获取URL
        
        console.log('🚀 开始提取页面内容...');
        
        const result = await extractor.getPageContent(url);
        
        // 显示格式化结果
        console.log(extractor.formatResult(result));
        
        // 保存结果
        const savedFile = extractor.saveResult(result);
        
        console.log(`\n✅ 内容提取完成！结果已保存到: ${savedFile}`);
        
    } catch (error) {
        console.error('❌ 提取失败:', error.message);
        process.exit(1);
    } finally {
        extractor.cleanup();
    }
}

// 如果直接运行此脚本
if (require.main === module) {
    main();
}

module.exports = ChromeContentExtractor;