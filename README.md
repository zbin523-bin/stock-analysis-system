# 股票投资组合分析系统

## 功能特性

- 📊 自动分析股票投资组合
- 📈 实时获取港股价格
- 📧 自动发送分析报告到邮箱
- ⏰ 定时任务：每天10:00和16:00
- 💡 提供买卖建议和技术分析
- 📋 生成Excel格式报告

## 系统要求

- Python 3.7+
- pandas, requests, schedule 库
- Gmail账户和应用程序密码

## 快速开始

### 1. 安装依赖
```bash
pip install pandas requests schedule
```

### 2. 运行系统

#### 方式一：直接运行
```bash
python3 production_stock_analyzer.py
```

#### 方式二：使用启动脚本
```bash
# macOS/Linux
./start_stock_system.sh

# Windows
start_stock_system.bat
```

#### 方式三：系统服务 (Linux)
```bash
# 复制服务文件
sudo cp stock-analysis.service /etc/systemd/system/

# 启用服务
sudo systemctl daemon-reload
sudo systemctl enable stock-analysis
sudo systemctl start stock-analysis
```

#### 方式四：Cron任务
```bash
# 添加定时任务
crontab stock_analysis_cron.txt
```

## 配置说明

### Gmail配置
系统已预配置Gmail账户：
- 发件人：zbin523@gmail.com
- 收件人：zhangbin19850523@163.com

### 股票配置
系统监控以下港股：
- 腾讯控股 (00700.HK)
- 中芯国际 (00981.HK)
- 小米集团-W (01810.HK)
- 中国人寿 (02628.HK)
- 美团-W (03690.HK)
- 新东方-S (09901.HK)
- 阿里巴巴-W (09988.HK)

## 文件结构

```
├── production_stock_analyzer.py    # 主程序
├── start_stock_system.sh          # Linux/macOS启动脚本
├── start_stock_system.bat         # Windows启动脚本
├── stock-analysis.service         # systemd服务文件
├── stock_analysis_cron.txt       # Cron任务文件
├── logs/                         # 日志目录
├── reports/                       # 报告目录
└── README.md                     # 说明文档
```

## 定时任务

系统会在每天以下时间自动运行：
- **10:00** - 上午开盘分析
- **16:00** - 下午收盘分析

## 邮件报告

每次分析会发送包含以下内容的邮件：
- 📊 投资组合总览
- 📈 持仓明细表格
- 🔍 技术分析
- 💡 操作建议
- 📎 Excel格式附件

## 日志监控

- 系统日志：`logs/stock_analysis.log`
- Cron日志：`logs/cron.log`

## 故障排除

### Gmail发送失败
1. 检查Gmail应用程序密码是否正确
2. 确保开启了"不够安全的应用的访问权限"
3. 检查网络连接

### 股票价格获取失败
1. 检查网络连接
2. 查看日志文件了解具体错误
3. 系统会自动重试

### 定时任务不执行
1. 检查系统时间是否正确
2. 查看日志文件
3. 手动运行测试：`python3 production_stock_analyzer.py`

## 停止系统

### 手动运行
按 `Ctrl+C` 停止程序

### 系统服务
```bash
sudo systemctl stop stock-analysis
```

### Cron任务
```bash
crontab -l  # 查看当前任务
crontab -r  # 删除所有任务
```

## 技术支持

如有问题，请查看日志文件或联系技术支持。
