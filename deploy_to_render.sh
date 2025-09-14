#!/bin/bash
# -*- coding: utf-8 -*-
"""
Render.com 一键部署脚本
Render.com One-Click Deployment Script
"""

echo "🚀 股票分析系统 - Render.com 部署助手"
echo "==========================================="

# 检查必要文件
required_files=("stock_web_app.py" "stock_notification_agent_enhanced.py" "requirements.txt" "Procfile" "config.py")

echo "📋 检查部署文件..."
missing_files=()
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -gt 0 ]; then
    echo "❌ 缺少必要文件:"
    for file in "${missing_files[@]}"; do
        echo "   - $file"
    done
    exit 1
fi

echo "✅ 所有必要文件存在"

# 检查 Git 仓库
if [ ! -d ".git" ]; then
    echo "❌ 当前目录不是 Git 仓库"
    echo "请先运行: git init"
    exit 1
fi

# 检查 Git 远程仓库
if ! git remote -v | grep -q "origin"; then
    echo "⚠️  未检测到 Git 远程仓库"
    echo "请先添加远程仓库:"
    echo "   git remote add origin https://github.com/yourusername/yourrepo.git"
    echo "   git add ."
    echo "   git commit -m 'Initial commit'"
    echo "   git push -u origin main"
    exit 1
fi

echo "✅ Git 仓库配置正常"

# 显示部署清单
echo ""
echo "📋 部署清单:"
echo "==========================================="
echo "📁 核心文件:"
for file in "${required_files[@]}"; do
    echo "   ✅ $file"
done

echo ""
echo "🌐 Web 应用功能:"
echo "   ✅ 股票交易管理 (买入/卖出)"
echo "   ✅ 实时盈亏统计 (当日/本周/本月)"
echo "   ✅ 持仓管理与分析"
echo "   ✅ 邮件报告发送"
echo "   ✅ 数据可视化界面"

echo ""
echo "📧 邮件通知功能:"
echo "   ✅ 专业HTML邮件报告"
echo "   ✅ 雪球讨论链接集成"
echo "   ✅ 详细盈亏统计分析"
echo "   ✅ 智能投资建议"

echo ""
echo "⏰ 定时任务选项:"
echo "   ✅ Render Cron Jobs (推荐)"
echo "   ✅ 外部调度服务"
echo "   ✅ GitHub Actions"

echo ""
echo "🔧 Render.com 配置:"
echo "   ✅ Python 3.9 运行环境"
echo "   ✅ 自动依赖安装"
echo "   ✅ HTTPS 证书"
echo "   ✅ 健康检查端点"

# 显示部署步骤
echo ""
echo "🚀 部署步骤:"
echo "==========================================="
echo "1. 📤 提交代码到 GitHub:"
echo "   git add ."
echo "   git commit -m 'Add stock analysis system'"
echo "   git push origin main"

echo ""
echo "2. 🌐 登录 Render.com:"
echo "   访问: https://render.com"
echo "   使用 GitHub 账户登录"

echo ""
echo "3. ➕ 创建新服务:"
echo "   点击 'New +' → 'Web Service'"
echo "   选择您的 GitHub 仓库"
echo "   配置服务设置"

echo ""
echo "4. ⚙️ 配置环境变量:"
echo "   GMAIL_EMAIL=your_email@gmail.com"
echo "   GMAIL_PASSWORD=your_app_password"

echo ""
echo "5. 📅 设置定时任务 (可选):"
echo "   在服务页面添加 Cron Job"
echo "   调度: 0 10,16 * * *"
echo "   命令: curl -X POST https://your-app-url.onrender.com/api/send_report"

# 显示成本信息
echo ""
echo "💰 成本估算:"
echo "==========================================="
echo "🆓 免费套餐: \$0/月"
echo "   - 512MB RAM"
echo "   - 750小时/月"
echo "   - 10GB 流量"
echo ""
echo "💎 启动套餐: \$7/月 (推荐)"
echo "   - 1GB RAM"
echo "   - 无限制运行时间"
echo "   - 50GB 流量"

# 显示测试命令
echo ""
echo "🧪 本地测试:"
echo "==========================================="
echo "安装依赖: pip install -r requirements.txt"
echo "启动服务: python stock_web_app.py"
echo "访问地址: http://localhost:5000"

# 显示重要提醒
echo ""
echo "⚠️  重要提醒:"
echo "==========================================="
echo "1. 📧 必须配置 Gmail 应用密码"
echo "2. 🔄 Render 免费套餐数据不持久化"
echo "3. 📊 建议定期备份交易数据"
echo "4. 🔒 定期更换应用密码确保安全"

echo ""
echo "📚 详细文档请查看: RENDER_DEPLOYMENT.md"
echo ""

# 询问是否继续
read -p "是否已准备好部署到 Render.com? (y/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🎉 太好了！请按照上述步骤开始部署"
    echo ""
    echo "📞 需要帮助？查看 RENDER_DEPLOYMENT.md 获取详细指导"
else
    echo "📝 如需准备，请先完成必要配置后再次运行此脚本"
fi

echo ""
echo "👋 部署助手完成！"