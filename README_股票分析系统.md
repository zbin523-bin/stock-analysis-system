# 股票投资组合分析系统

一个全自动化的股票投资组合分析系统，支持实时股价获取、技术分析、雪球情绪分析、邮件报告发送等功能。

## 功能特点

- 🔄 **实时股价获取** - 使用Alpha Vantage API获取最新股价
- 📊 **技术分析** - 移动平均线、RSI、布林带等技术指标
- 📈 **图表生成** - 自动生成技术分析图表
- 💬 **情绪分析** - 雪球平台投资者情绪分析
- 📧 **邮件报告** - 自动发送详细分析报告到邮箱
- 🔄 **定时任务** - 支持每日定时自动分析
- 📱 **移动端适配** - 支持邮件查看，随时随地掌握投资动态

## 文件结构

```
股票分析系统/
├── .env                          # 环境变量配置
├── requirements_simple.txt       # Python依赖包
├── stock_analyzer_simple.py      # 主分析程序（推荐使用）
├── stock_portfolio_analyzer.py   # 完整功能版本
├── stock_agent_daemon.py         # 定时任务守护进程
├── output_charts/                # 图表输出目录
└── output/                       # Excel报告输出目录
```

## 快速开始

### 1. 环境配置

#### 安装依赖包
```bash
pip install -r requirements_simple.txt
```

#### 安装TA-Lib（可选，用于高级技术分析）
```bash
# macOS
brew install ta-lib
pip install TA-Lib

# Linux
sudo apt-get install libta-lib-dev
pip install TA-Lib
```

### 2. 配置设置

编辑 `.env` 文件，填入你的配置信息：

```env
# Alpha Vantage API密钥
ALPHA_VANTAGE_API_KEY=5DGMRPMMEUBMX7PU

# 邮件配置
EMAIL_SENDER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_RECEIVER=zhangbin19850523@163.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

### 3. Gmail配置指南

#### 开启应用专用密码
1. 登录你的Gmail账户
2. 进入账户设置 → 安全性
3. 开启两步验证（必需）
4. 在"应用密码"部分生成新密码
5. 选择"邮件"应用和"其他设备"
6. 生成的16位密码填入`EMAIL_PASSWORD`

#### 其他邮箱配置
- **QQ邮箱**: `smtp.qq.com:587`
- **163邮箱**: `smtp.163.com:994`
- **Outlook**: `smtp-mail.outlook.com:587`

## 使用方法

### 单次运行分析
```bash
python3 stock_analyzer_simple.py
```

### 后台定时运行
```bash
# 启动守护进程
python3 stock_agent_daemon.py start

# 查看状态
python3 stock_agent_daemon.py status

# 停止服务
python3 stock_agent_daemon.py stop
```

### 定时任务说明
- **每日16:30** - 股市收盘后分析
- **每周一09:00** - 周策略分析  
- **每月最后一天15:00** - 月度总结

## 分析报告内容

### 投资组合概览
- 总市值、总盈亏
- 盈亏比例、个股表现

### 技术分析指标
- **移动平均线**: MA20、MA50交叉信号
- **相对强弱指数**: RSI超买超卖信号
- **布林带**: 价格突破信号
- **支撑/阻力位**: 关键价格位置

### 雪球情绪分析
- 投资者情绪：积极/消极/中性
- 高质量分析摘要
- 市场热点讨论

### 交易建议
- 基于技术指标的买卖信号
- 风险提示和建议

## 输出文件

### Excel报告
- `output/stock_portfolio_analysis.xlsx`
  - Portfolio Summary: 投资组合概览
  - Technical Analysis: 技术分析详情

### 图表文件
- `output_charts/{股票代码}_chart.png`
  - 价格走势图
  - 技术指标图
  - RSI指标图

## 邮件报告示例

```
主题: 股票投资组合分析报告 - 2024-09-12

股票投资组合分析报告
生成时间: 2024-09-12 16:30:00

==============
投资组合概览
==============

总市值: 625,230.00
总浮动盈亏: 87,467.21
盈亏比例: 16.27%

==============
详细持仓信息
==============
股票名称    代码      市值      数量  现价      摊薄成本价  浮动盈亏    涨跌幅
腾讯控股    00700.HK  181650.00  300   605.50   320.85     85395.00    88.72
中芯国际    00981.HK  58700.00   1000  58.70    47.55      11150.00    23.45

==============
交易建议
==============

腾讯控股 (00700.HK): 建议买入
当前价格: 605.50
支撑位: 580.20, 阻力位: 625.80
雪球情绪: 积极
--------------------------------------------------
```

## 常见问题

### Q: API调用限制
**A**: Alpha Vantage免费版有调用限制（每天25次，每分钟5次）。系统已内置重试机制和等待逻辑。

### Q: 邮件发送失败
**A**: 检查以下配置：
- 确认开启了邮箱的SMTP功能
- 使用应用专用密码（非登录密码）
- 检查网络连接和防火墙设置

### Q: 图表生成失败
**A**: 确保`matplotlib`后端配置正确，系统会自动保存为PNG格式。

### Q: 定时任务不运行
**A**: 检查系统时间和时区设置，确保程序在后台持续运行。

## 高级功能

### 自定义股票池
编辑`stock_analyzer_simple.py`中的`stocks_data`字典：

```python
self.stocks_data = {
    "股票名称": {
        "code": "股票代码", 
        "quantity": 持有数量,
        "avg_cost": 平均成本
    }
}
```

### 添加技术指标
在`simple_technical_analysis`方法中添加新的指标计算逻辑。

### 自定义邮件模板
修改`analyze_portfolio`方法中的`email_content`部分。

## 系统要求

- Python 3.7+
- 可用内存: 512MB+
- 网络连接: 需要访问Alpha Vantage API和雪网
- 存储空间: 100MB+ (用于图表和报告)

## 许可证

本项目仅供个人投资参考使用，不构成投资建议。

## 免责声明

本系统提供的所有数据和分析仅供参考，不构成投资建议。投资有风险，请谨慎决策。开发者不对因使用本系统造成的任何投资损失负责。

---

**作者**: Claude AI Assistant  
**创建时间**: 2024年9月12日  
**版本**: 1.0.0