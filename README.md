# 智能投资组合管理系统

一个功能完整的股票投资组合管理系统，支持A股、美股、港股实时数据抓取和交易记录管理。

## 🚀 功能特点

### 📊 实时数据抓取
- **A股数据**: 支持上海、深圳交易所股票实时价格
- **美股数据**: 支持NASDAQ、NYSE交易所股票实时价格  
- **港股数据**: 支持香港交易所股票实时价格
- **基金数据**: 支持国内基金净值查询

### 💼 投资组合管理
- **持仓管理**: 实时显示持仓股票、基金的市场价值和盈亏情况
- **交易记录**: 完整的买入、卖出记录管理
- **自动计算**: 自动计算成本价、盈亏比例、持仓占比
- **多币种支持**: 支持人民币、美元、港币

### 🔧 智能功能
- **自动获取股票名称**: 输入股票代码自动获取对应名称
- **手动编辑**: 支持手动修改股票名称和其他信息
- **数据验证**: 完整的数据验证和错误处理
- **响应式设计**: 支持桌面端和移动端访问

## 🛠️ 技术栈

- **后端**: Python Flask + 多源数据抓取
- **前端**: HTML5 + CSS3 + JavaScript (ES6+)
- **数据源**: 网易财经、腾讯财经、Yahoo Finance等
- **部署**: 支持Docker容器化部署

## 📦 快速开始

### 本地运行

1. **克隆仓库**
```bash
git clone <your-repo-url>
cd stock-portfolio-management-system
```

2. **安装依赖**
```bash
pip install -r api/requirements.txt
```

3. **启动API服务器**
```bash
cd api
python app.py
```

4. **启动Web服务器**
```bash
cd web
python -m http.server 8080
```

5. **访问系统**
打开浏览器访问: http://localhost:8080/index.html

### Docker部署

```bash
# 构建并启动
docker-compose up -d

# 访问系统
http://localhost:8080
```

## 🌐 云平台部署

### 推荐的云平台

#### 1. **Render.com** (推荐)
- **免费额度**: Web服务 $0/月
- **特点**: 支持Python Flask，简单易用
- **网址**: https://render.com/

#### 2. **PythonAnywhere** 
- **免费额度**: 基础账户免费
- **特点**: 专为Python应用设计
- **网址**: https://www.pythonanywhere.com/

#### 3. **Heroku**
- **免费额度**: 550 dyno小时/月
- **特点**: 经典PaaS平台
- **网址**: https://www.heroku.com/

### Render.com部署步骤

1. **注册账户**
   - 访问 https://render.com/
   - 使用GitHub账户注册

2. **创建新的Web服务**
   - 点击"New +" → "Web Service"
   - 连接您的GitHub仓库
   - 选择您的仓库

3. **配置环境**
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r api/requirements.txt`
   - **Start Command**: `python api/app.py`
   - **Port**: 5000

4. **环境变量** (如果需要)
   ```bash
   FLASK_ENV=production
   ```

5. **部署**
   - 点击"Create Web Service"
   - 等待部署完成

## 📱 系统界面

### 主要功能页面
- **仪表板**: 总览投资组合表现
- **持仓管理**: 查看和管理股票/基金持仓
- **交易记录**: 添加、编辑、删除交易记录
- **资金管理**: 现金流水记录

### 交易记录功能
- ✅ 新建买入/卖出记录
- ✅ 自动获取股票名称
- ✅ 手动编辑交易信息
- ✅ 删除交易记录
- ✅ 查看交易详情

## 🔑 API密钥配置

### 可选的数据源API密钥

1. **Alpha Vantage** (美股数据)
   - 注册: https://www.alphavantage.co/support/#api-key
   - 免费额度: 每日25次调用
   - 环境变量: `ALPHA_VANTAGE_API_KEY`

2. **TuShare Pro** (A股数据)
   - 注册: https://tushare.pro/register
   - 免费额度: 每日100次调用  
   - 环境变量: `TUSHARE_TOKEN`

## 📝 使用说明

### 添加交易记录
1. 点击"新建买入"按钮
2. 输入股票代码 (如: 600036)
3. 选择股票市场 (A股/美股/港股/基金)
4. 系统自动获取股票名称，也可手动修改
5. 填写交易数量、价格等信息
6. 点击确认完成添加

### 编辑交易记录
1. 在交易记录列表中点击"编辑"
2. 修改需要更新的字段
3. 点击"更新"保存修改

### 查看持仓情况
- 切换到不同市场标签查看对应持仓
- 系统自动计算盈亏和持仓占比
- 实时更新股票价格

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目！

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 📞 联系方式

如有问题或建议，请通过以下方式联系：
- GitHub Issues
- Email: your-email@example.com

---

**注意**: 本系统仅供学习和研究使用，投资有风险，请谨慎决策。