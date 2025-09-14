#!/bin/bash
# -*- coding: utf-8 -*-
"""
部署步骤执行脚本
请依次执行以下命令
"""

echo "🚀 开始部署股票分析系统到云端"
echo "================================"

echo "📋 第一步：初始化Git仓库"
git init

echo "📋 第二步：配置Git用户信息"
git config --global user.name "zbin-523"
git config --global user.email "zbin523@gmail.com"

echo "📋 第三步：添加必要文件到Git"
# 添加核心部署文件
git add stock_web_app.py
git add stock_notification_agent_enhanced.py  
git add requirements.txt
git add Procfile
git add config.py
git add RENDER_DEPLOYMENT.md
git add deploy_to_render.sh

echo "📋 第四步：创建初始提交"
git commit -m "feat: 添加股票分析系统 - 包含Web界面和云端部署支持

- ✅ 完整的Web交易管理系统
- ✅ 实时盈亏统计 (当日/本周/本月)
- ✅ 买入卖出交易功能
- ✅ 邮件报告增强
- ✅ Render.com云部署配置
- ✅ SQLite数据持久化
- ✅ 响应式Web界面"

echo "✅ 本地Git仓库已准备完成！"
echo ""
echo "🎯 下一步操作："
echo "1. 访问 https://github.com 登录您的账户"
echo "2. 创建新仓库，名称建议：stock-analysis-system"
echo "3. 复制仓库URL，然后执行以下命令："
echo ""
echo "   git remote add origin https://github.com/zbin-523/stock-analysis-system.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "📞 完成这些步骤后，继续进行Render.com部署！"