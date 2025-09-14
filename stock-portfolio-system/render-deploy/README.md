# Render.com部署指南

## 快速部署到Render.com

### 1. 准备工作
- 确保您有一个GitHub账户
- 注册Render.com账户: https://render.com/

### 2. 创建GitHub仓库
1. 访问 https://github.com
2. 点击 "New repository"
3. 仓库名称: `stock-portfolio-management-system`
4. 设置为 Public (免费账户需要)
5. 点击 "Create repository"

### 3. 推送代码到GitHub
```bash
# 在本地项目目录中
git remote add origin https://github.com/yourusername/stock-portfolio-management-system.git
git branch -M main
git push -u origin main
```

### 4. 在Render.com上部署
1. 登录 Render.com
2. 点击 "New +" → "Web Service"
3. 选择 "Build and deploy from a Git repository"
4. 连接您的GitHub账户
5. 选择 `stock-portfolio-management-system` 仓库
6. 配置部署选项:
   - **Name**: `stock-portfolio-api`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r api/requirements.txt`
   - **Start Command**: `python api/app.py`
   - **Instance Type**: `Free` (免费版)
   - **Region**: 选择离您最近的区域

### 5. 环境变量配置 (可选)
在 "Environment" 选项卡中添加:
```bash
FLASK_ENV=production
# 可选的API密钥
ALPHA_VANTAGE_API_KEY=your_key_here
TUSHARE_TOKEN=your_token_here
```

### 6. 部署前端
重复步骤4，创建另一个Web服务:
- **Name**: `stock-portfolio-web`
- **Runtime**: `Docker`
- **Dockerfile路径**: `./web/Dockerfile`
- **Instance Type**: `Free`

### 7. 访问您的应用
部署完成后，您将获得两个URL:
- API服务: `https://stock-portfolio-api.onrender.com`
- Web服务: `https://stock-portfolio-web.onrender.com`

### 8. 配置前端API地址
修改 `web/static/api.js` 文件中的API_BASE_URL:
```javascript
const API_BASE_URL = 'https://stock-portfolio-api.onrender.com/api';
```

## 故障排除

### 常见问题
1. **构建失败**: 检查requirements.txt中的依赖是否正确
2. **启动失败**: 确认Start Command路径正确
3. **CORS错误**: 确保API服务器设置了正确的CORS头
4. **端口问题**: Render.com会自动分配端口，确保应用监听正确的端口

### 日志查看
在Render.com控制台中查看 "Logs" 选项卡，可以找到详细的错误信息。

## 更新部署

每次您推送代码到GitHub主分支时，Render.com会自动重新部署您的应用。

## 免费版限制

- **Web服务**: 512MB RAM，512MB磁盘空间
- **每月限制**: 750小时运行时间
- **睡眠时间**: 15分钟无访问后会休眠
- **启动时间**: 休眠后重启可能需要30秒到2分钟

## 升级到付费版

如果需要更好的性能，可以升级到付费计划:
- Starter计划: $7/月
- Standard计划: $19/月
- 更多内存和CPU
- 无休眠时间限制