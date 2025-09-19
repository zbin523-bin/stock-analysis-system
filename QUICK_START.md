# 股票投资组合管理系统 - 快速启动指南

## 🚀 快速开始

### 1. 环境要求
- Python 3.7+
- pip包管理器
- 现代浏览器

### 2. 依赖安装
```bash
# 进入项目目录
cd stock-portfolio-system

# 安装Python依赖
pip install flask requests
```

### 3. 启动系统
```bash
# 启动API服务器
python api/app.py

# 或者使用重启脚本
python restart_api.py
```

### 4. 访问系统
打开浏览器访问: http://localhost:5000

## 📊 当前系统状态

### ✅ 正常功能
- A股实时数据抓取
- 港股实时数据抓取
- 基金实时数据抓取
- 投资组合管理
- 盈亏计算分析
- Web界面操作

### ⚠️ 需要注意
- 美股数据使用Fallback数据（非实时）
- 部分API有访问限制
- 建议定期重启服务器

## 🔧 常用命令

### 启动管理
```bash
# 启动API服务器
python api/app.py

# 重启API服务器
python restart_api.py

# 重置数据库
python reset_database.py
```

### 健康检查
```bash
# 检查API状态
curl http://localhost:5000/api/health

# 检查浏览器访问
# http://localhost:5000
```

### 日志查看
```bash
# 查看API日志 (控制台输出)
# 或者检查服务器输出
```

## 🔄 使用Claude Code继续开发

### 1. 项目迁移
```bash
# 复制整个项目文件夹到新电脑
cp -r stock-portfolio-system/ /new/location/

# 进入新目录
cd /new/location/stock-portfolio-system
```

### 2. 快速恢复开发环境
```bash
# 1. 安装依赖
pip install flask requests

# 2. 启动服务器
python api/app.py

# 3. 访问系统
# http://localhost:5000
```

### 3. Claude Code开发提示
- **首先阅读 PROJECT_PROGRESS.md** - 了解完整开发历史
- **查看当前API日志** - 了解数据源状态
- **优先解决美股数据源** - 这是主要问题
- **测试所有功能** - 确保修改不影响现有功能

## 🐛 常见问题

### Q: 美股数据不更新怎么办？
A: 当前使用Fallback数据，建议：
1. 注册Finnhub.io免费账户
2. 或使用Polygon.io免费层
3. 修改api/app.py中的美股数据源配置

### Q: 页面显示错误数据？
A: 清除浏览器缓存或强制刷新：
```javascript
// 在浏览器控制台执行
location.reload(true)
```

### Q: 服务器无法启动？
A: 检查端口占用：
```bash
# Windows
netstat -ano | findstr :5000

# 杀死占用进程
taskkill /PID <进程ID> /F
```

### Q: 数据库出现问题？
A: 重置数据库：
```bash
python reset_database.py
```

## 📝 开发重点

### 优先级1: 美股数据源
- 集成Finnhub.io API
- 替换Fallback数据为实时数据

### 优先级2: 功能优化
- 添加数据导出功能
- 优化用户界面
- 增加技术分析指标

### 优先级3: 系统优化
- 性能优化
- 错误处理改进
- 单元测试覆盖

## 📞 快速参考

### API接口
- 健康检查: `GET /api/health`
- 投资组合: `GET /api/portfolio`
- 添加交易: `POST /api/transaction`

### 数据库结构
- 持仓表: positions
- 交易表: transactions
- 数据文件: stock_portfolio.db

### 配置文件
- 主应用: api/app.py
- 前端界面: web/index.html
- 数据库类: database/database.py

## 🎯 下一步行动

1. **立即行动** - 阅读完整项目文档 (PROJECT_PROGRESS.md)
2. **评估现状** - 检查当前系统运行状态
3. **制定计划** - 根据业务需求确定开发优先级
4. **开始开发** - 使用Claude Code进行迭代开发

---

**快速启动完成！** 系统现在已经可以正常运行，您可以开始使用或继续开发了。