# 股票投资分析管理系统

## 📊 系统概述

这是一个基于AI的智能股票投资分析管理系统，提供实时股价监控、投资组合分析、智能预警和自动化报告功能。

## ✨ 主要功能

- **实时股价监控**: 支持A股、美股、港股、基金实时价格更新
- **投资组合分析**: 自动计算盈亏、风险评估、资产配置分析
- **AI智能分析**: 基本面分析、技术分析、新闻情感分析
- **自动化报告**: 每日/每周投资报告自动生成
- **智能预警**: 价格异常变动、风险提醒、投资建议
- **飞书集成**: 自动同步到飞书多维表格
- **邮件通知**: 重要事件邮件提醒

## 🚀 快速开始

### 1. 环境准备

```bash
# 进入项目目录
cd 10_stock_investment_agent

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置设置

确保以下配置文件已正确设置：

- `config/api_keys.json` - API密钥配置
- `config/settings.json` - 系统设置
- `config/stock_symbols.json` - 股票代码映射

### 3. 启动系统

```bash
# 交互式启动（推荐）
python scripts/run_agent.py --interactive

# 直接启动
python scripts/run_agent.py --start

# 查看状态
python scripts/run_agent.py --status

# 发送测试通知
python scripts/run_agent.py --test
```

## 📁 项目结构

```
10_stock_investment_agent/
├── main_agent.py              # 主控制器
├── config/                    # 配置文件
│   ├── api_keys.json         # API密钥
│   ├── settings.json         # 系统设置
│   └── stock_symbols.json    # 股票代码
├── agents/                   # Agent模块
│   ├── data_fetching_agent.py    # 数据抓取
│   ├── portfolio_analyzer.py     # 投资组合分析
│   ├── feishu_integration.py    # 飞书集成
│   ├── notification_agent.py     # 通知系统
│   └── ai_analysis_agent.py      # AI分析
├── utils/                    # 工具模块
│   ├── calculation_utils.py  # 计算工具
│   ├── date_utils.py         # 日期工具
│   ├── logger.py             # 日志系统
│   └── auto_scheduler.py     # 自动化调度
├── scripts/                  # 启动脚本
│   └── run_agent.py         # 主启动脚本
└── data/                    # 数据存储
    ├── portfolio_data.json   # 投资组合数据
    └── logs/               # 日志文件
```

## 🔧 配置说明

### API密钥配置 (config/api_keys.json)

```json
{
  "alpha_vantage": {
    "api_key": "YOUR_ALPHA_VANTAGE_API_KEY"
  },
  "tushare": {
    "api_key": "YOUR_TUSHARE_API_KEY"
  },
  "feishu": {
    "app_id": "YOUR_FEISHU_APP_ID",
    "app_secret": "YOUR_FEISHU_APP_SECRET"
  },
  "gmail": {
    "recipient_email": "your.email@example.com"
  }
}
```

### 系统设置 (config/settings.json)

主要配置项：
- `update_frequency`: 更新频率设置
- `notification_settings`: 通知设置
- `risk_management`: 风险管理参数
- `logging`: 日志配置

## 📈 使用方法

### 添加买入记录

```python
from main_agent import MainAgent

agent = MainAgent()

buy_data = {
    'symbol': 'AAPL',
    'name': '苹果公司',
    'market_type': 'us_stocks',
    'buy_price': 150.00,
    'quantity': 100,
    'fees': 10.00,
    'notes': '长期投资看好'
}

result = agent.add_buy_record(buy_data)
```

### 添加卖出记录

```python
sell_data = {
    'symbol': 'AAPL',
    'sell_price': 160.00,
    'quantity': 50,
    'fees': 10.00,
    'notes': '部分获利了结'
}

result = agent.add_sell_record(sell_data)
```

### 获取投资组合摘要

```python
summary = agent.get_portfolio_summary()
print(f"总市值: {summary['total_value']}")
print(f"总盈亏: {summary['total_profit_loss']}")
```

### 手动运行分析

```python
result = agent.run_manual_analysis()
```

## ⏰ 自动化任务

系统会自动执行以下任务：

- **价格更新**: 每5分钟更新所有持仓股票价格
- **投资组合分析**: 每小时分析投资组合状况
- **AI分析**: 每2小时运行智能分析
- **数据同步**: 每30分钟同步到飞书表格
- **每日报告**: 每天18:00发送投资报告
- **每周报告**: 每周日18:00发送周报

## 📧 通知功能

### 每日报告
包含内容：
- 投资组合摘要
- 盈亏情况
- 市场概况
- 个股表现

### 预警通知
触发条件：
- 价格变动超过5%
- AI分析建议卖出
- 风险评分过低

### 交易通知
每次买卖操作后自动发送通知。

## 📗 飞书集成

系统会自动同步以下数据到飞书多维表格：

- 买入记录表
- 卖出记录表
- 持仓统计表
- 分析报告表

## 🔍 故障排除

### 常见问题

1. **API密钥错误**
   - 检查 `config/api_keys.json` 文件
   - 确认API密钥有效且未过期

2. **网络连接问题**
   - 检查网络连接
   - 确认API服务可用

3. **依赖包缺失**
   - 运行 `pip install -r requirements.txt`
   - 检查Python版本兼容性

4. **权限问题**
   - 确认飞书应用权限设置正确
   - 检查Gmail访问权限

### 日志查看

日志文件位置：`data/logs/`

```bash
# 查看最新日志
tail -f data/logs/stock_agent_$(date +%Y%m%d).log
```

## 📊 API参考

### 主要接口

- `MainAgent.add_buy_record()` - 添加买入记录
- `MainAgent.add_sell_record()` - 添加卖出记录
- `MainAgent.get_portfolio_summary()` - 获取投资组合摘要
- `MainAgent.run_manual_analysis()` - 手动运行分析
- `MainAgent.get_system_status()` - 获取系统状态

### Agent接口

每个Agent提供以下接口：
- `start()` - 启动Agent
- `stop()` - 停止Agent
- `get_status()` - 获取状态

## 🛡️ 安全说明

- API密钥加密存储
- 敏感信息不记录日志
- 网络连接使用HTTPS
- 定期备份重要数据

## 📄 许可证

本项目仅供学习和研究使用。

## 🤝 贡献

欢迎提交Issue和Pull Request来改进本项目。

## 📞 支持

如有问题，请查看日志文件或联系开发者。