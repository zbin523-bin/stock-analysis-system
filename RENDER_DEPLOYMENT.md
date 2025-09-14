# 股票分析系统 - Render.com 部署指南

## 🚀 快速部署到 Render.com

### 1. 准备工作

#### 1.1 注册 Render.com 账户
- 访问 [render.com](https://render.com) 并注册账户
- 可以使用 GitHub 账户直接登录

#### 1.2 准备代码仓库
- 将此代码推送到 GitHub 仓库
- 确保包含所有必要文件：
  - `stock_web_app.py` - 主应用文件
  - `stock_notification_agent_enhanced.py` - 股票分析核心
  - `requirements.txt` - Python 依赖
  - `Procfile` - Render 启动配置
  - `config.py` - 配置文件

### 2. Render.com 配置

#### 2.1 创建新服务
1. 登录 Render.com 控制台
2. 点击 "New +" 
3. 选择 "Web Service"
4. 连接您的 GitHub 仓库
5. 选择包含股票系统的仓库

#### 2.2 配置服务设置
- **Name**: `stock-analysis-system` (或您喜欢的名称)
- **Region**: 选择离您最近的区域
- **Branch**: `main` 或 `master`
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn --bind 0.0.0.0:$PORT --timeout 120 stock_web_app:app`
- **Instance Type**: `Free` (免费套餐) 或 `Starter` ($7/月)

#### 2.3 环境变量配置
在 "Environment" 部分添加以下环境变量：

```bash
# Gmail 配置
GMAIL_EMAIL=your_email@gmail.com
GMAIL_PASSWORD=your_app_password

# 其他配置（可选）
PYTHONUNBUFFERED=1
```

### 3. Gmail 应用密码设置

#### 3.1 启用两步验证
1. 登录 Gmail 账户
2. 进入 Google 账户设置
3. 安全性 → 两步验证 → 启用

#### 3.2 生成应用密码
1. 安全性 → 应用密码
2. 选择 "邮件" 应用
3. 选择 "其他(自定义名称)"
4. 输入名称如 "Stock Analysis System"
5. 生成 16 位密码并保存

### 4. 部署和测试

#### 4.1 首次部署
- 点击 "Create Web Service"
- 等待构建完成（约 2-5 分钟）
- 查看部署日志确保无错误

#### 4.2 访问应用
- 部署成功后，Render 会提供 URL
- 访问该 URL 查看股票交易系统

#### 4.3 测试功能
1. **交易功能**：测试买入卖出操作
2. **盈亏统计**：查看当日/本周/本月盈亏
3. **邮件发送**：测试分析报告发送
4. **定时任务**：验证自动调度

### 5. 定时任务配置

#### 5.1 使用 Render Cron Jobs
Render.com 提供 Cron Jobs 功能：

1. 在服务页面点击 "Cron Jobs"
2. 添加新的定时任务：
   - **Schedule**: `0 10,16 * * *` (每天10:00和16:00)
   - **Command**: `curl -X POST https://your-app-url.onrender.com/api/send_report`

#### 5.2 备用方案：外部调度服务
如果 Render Cron 不可用，可以使用：
- **GitHub Actions** - 定时触发 API
- **EasyCron** - 免费的外部定时服务
- **UptimeRobot** - 监控服务兼定时器

### 6. 数据持久化

#### 6.1 SQLite 数据库
系统使用 SQLite 存储交易记录：
- 优点：无需额外配置，自动创建
- 缺点：Render 重启时数据会丢失

#### 6.2 数据备份建议
1. **定期导出数据**：
   ```bash
   # 在应用中添加导出功能
   curl https://your-app-url.onrender.com/api/export_data > backup.json
   ```

2. **使用云数据库**（高级）：
   - 升级到 Render 付费套餐
   - 配置 PostgreSQL 数据库
   - 修改代码使用 PostgreSQL

### 7. 监控和维护

#### 7.1 查看日志
- Render 控制台 → Logs
- 监控错误和异常
- 检查定时任务执行情况

#### 7.2 健康检查
- 访问 `/health` 端点检查服务状态
- 设置外部监控确保服务可用性

#### 7.3 性能优化
- **免费套餐限制**：
  - 512MB RAM
  - 每月 750小时运行时间
  - 10GB 出站流量

- **优化建议**：
  - 定期清理旧数据
  - 优化数据库查询
  - 使用缓存减少API调用

### 8. 故障排除

#### 8.1 常见问题

**问题：部署失败**
- 检查 requirements.txt 依赖版本
- 查看 build 日志定位错误
- 确保所有文件在仓库中

**问题：邮件发送失败**
- 验证 Gmail 应用密码
- 检查网络连接
- 查看 Render 日志中的错误信息

**问题：定时任务不执行**
- 检查 Cron 配置语法
- 验证 API 端点可访问性
- 查看任务执行日志

#### 8.2 调试命令
```bash
# 本地测试
python stock_web_app.py

# 检查依赖
pip install -r requirements.txt

# 测试数据库
sqlite3 trading_data.db ".tables"
```

### 9. 成本估算

#### 9.1 Render.com 定价
- **Free Tier**: $0/月 (有限制)
- **Starter**: $7/月 (推荐)
- **Standard**: $25/月 (生产环境)

#### 9.2 推荐配置
- **个人使用**: Free Tier 足够
- **小型团队**: Starter 套餐
- **生产环境**: Standard 套餐

### 10. 安全考虑

#### 10.1 数据安全
- 使用环境变量存储敏感信息
- 定期更换 Gmail 应用密码
- 启用 HTTPS (Render 自动提供)

#### 10.2 访问控制
- 考虑添加基本认证
- 限制 API 访问频率
- 定期备份数据

---

## 📞 技术支持

如遇问题，请检查：
1. Render 部署日志
2. 应用运行时日志
3. Gmail 配置正确性
4. 网络连接状态

系统已配置完整的错误处理和日志记录，便于问题诊断。