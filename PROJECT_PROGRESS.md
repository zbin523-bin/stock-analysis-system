# 股票投资组合管理系统 - 项目进展文档

## 项目概述

这是一个智能投资组合管理系统，支持A股、美股、港股和基金的实时数据抓取、交易记录管理和投资组合分析。

**当前版本:** 1.0.0
**最后更新:** 2025-09-19
**开发状态:** 功能完整，需要优化美股数据源

## 系统架构

### 后端技术栈
- **Python Flask** - Web服务器
- **SQLite** - 数据库存储
- **多种数据API** - 实时股票数据抓取

### 前端技术栈
- **HTML5 + CSS3 + JavaScript** - 用户界面
- **Bootstrap** - 响应式布局
- **Chart.js** - 数据可视化

## 文件结构

```
stock-portfolio-system/
├── api/                     # 后端API目录
│   ├── app.py               # 主应用程序 (当前活跃)
│   ├── app_backup.py        # 备份版本
│   ├── enhanced_app.py      # 增强版本
│   └── reliable_app.py      # 可靠版本
├── database/                # 数据库模块
│   └── database.py          # 数据库操作类
├── web/                     # 前端文件
│   ├── index.html           # 主页面
│   ├── static/              # 静态资源
│   │   └── api.js           # 前端JavaScript
│   └── templates/           # HTML模板
├── fund_crawler/            # 基金爬虫工具
├── package.json             # 项目配置
├── restart_api.py           # API重启脚本
├── reset_database.py        # 数据库重置脚本
└── README.md                # 项目说明
```

## 核心功能

### 1. 多市场支持
- **A股市场** - 上海证券交易所、深圳证券交易所
- **美股市场** - 纽约证券交易所、纳斯达克
- **港股市场** - 香港交易所
- **基金市场** - 开放式基金、ETF

### 2. 实时数据抓取
- **当前价格** - 实时股价获取
- **涨跌数据** - 涨跌额、涨跌幅计算
- **交易量** - 成交量统计
- **技术指标** - 最高价、最低价、开盘价

### 3. 投资组合管理
- **持仓管理** - 添加、修改、删除持仓
- **成本计算** - 平均成本价计算
- **盈亏统计** - 累计盈亏、盈亏比例
- **市值分布** - 各市场市值占比

### 4. 数据分析功能
- **市场分析** - 各市场表现统计
- **风险评估** - 收益率、波动率分析
- **历史数据** - 价格走势图表
- **报告生成** - 投资组合报告

## 已解决的关键问题

### 1. 数据计算错误修复
**问题:** A股、美股、港股的涨跌额、涨跌幅、盈亏金额都显示为"10.8万"

**原因分析:**
- HTML自动更新函数调用formatNumber函数进行"万"格式化
- 多个自动更新函数覆盖了正确的API数据

**解决方案:**
```javascript
// 禁用所有自动更新函数
function updateAnalysisCharts() {
    console.log('Analysis charts update disabled to prevent data overwriting');
    return;
}

// 修改formatNumber函数防止万格式化
function formatNumber(num) {
    // 禁用万格式化，直接返回数字格式
    return num.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}
```

### 2. 基金数据抓取修复
**问题:** 基金当前价显示与成本价相同，无法获取实时数据

**原因分析:**
- TuShare API需要付费权限
- 基金代码格式不匹配
- API响应解析错误

**解决方案:**
```python
def _get_fund_code_variants(self, code):
    variants = [code]
    # 添加.sz/.sh后缀
    if not code.endswith('.sz') and not code.endswith('.sh'):
        if code.startswith('15') or code.startswith('16') or code.startswith('50'):
            variants.append(f"{code}.sz")
        elif code.startswith('5'):
            variants.append(f"{code}.sh")
    return list(set(variants))
```

### 3. 涨跌数据拆分
**需求:** 将涨跌额改为累计涨跌额，拆分涨跌幅为累计涨跌幅和今日涨跌幅

**实现:**
```python
# 后端新增字段
'cumulativeChange': current_price - cost_price,
'cumulativeChangePercent': ((current_price - cost_price) / cost_price) * 100,
'todayChange': change,
'todayChangePercent': change_percent,
```

### 4. 数据源优化
**问题:** 多个API服务不稳定或受限制

**解决方案:**
- **A股:** 新浪财经API → 腾讯财经API → TuShare Pro
- **港股:** 腾讯财经API → 新浪财经API → qos.hk → Alpha Vantage
- **美股:** Alpha Vantage → Yahoo Finance → qos.hk → Fallback数据

## 当前系统状态

### 运行状态
- ✅ **API服务器**: 正常运行 (http://localhost:5000)
- ✅ **Web界面**: 正常访问 (http://localhost:5000)
- ✅ **数据库**: SQLite数据库正常
- ✅ **A股数据**: 实时抓取正常
- ✅ **港股数据**: 实时抓取正常
- ✅ **基金数据**: 实时抓取正常
- ⚠️ **美股数据**: 使用Fallback数据 (API受限)

### 数据源状态

#### A股数据源
1. **新浪财经API** - 主要数据源
2. **腾讯财经API** - 备用数据源
3. **TuShare Pro** - 需要付费权限

#### 港股数据源
1. **腾讯财经API** - 主要数据源
2. **新浪财经API** - 备用数据源
3. **qos.hk** - 第三备用
4. **Alpha Vantage** - 最后备用

#### 美股数据源
1. **Alpha Vantage** - 已达每日25次限制
2. **Yahoo Finance** - 返回403错误
3. **qos.hk** - 连接超时
4. **Fallback数据** - 当前使用

#### 基金数据源
1. **TuShare Pro** - 需要付费权限
2. **天天基金** - 通过Web抓取
3. **新浪财经** - 备用数据源

### 已知问题

#### 1. 美股API限制
**问题:** Alpha Vantage和Yahoo Finance都受到访问限制

**影响:** 美股数据使用预定义的Fallback数据，不是实时数据

**解决方案建议:**
- 注册Finnhub.io免费账户 (60次/分钟)
- 使用Polygon.io免费层
- 考虑付费数据源 (Bloomberg/Refinitiv)

#### 2. 服务器资源占用
**问题:** 多个Python进程同时运行

**解决:** 使用restart_api.py脚本重启服务器

#### 3. 浏览器缓存
**问题:** 前端JS文件更新后需要清除缓存

**解决:** 使用时间戳参数: `api.js?v=timestamp`

## 数据库结构

### 持仓表 (positions)
- id: 主键
- code: 股票代码
- name: 股票名称
- market: 市场类型
- quantity: 持仓数量
- cost_price: 成本价
- industry: 行业分类
- currency: 货币类型

### 交易记录表 (transactions)
- id: 主键
- code: 股票代码
- name: 股票名称
- market: 市场类型
- quantity: 交易数量
- price: 交易价格
- trade_type: 交易类型 (买入/卖出)
- trade_date: 交易日期

## API接口

### 1. 健康检查
- **GET** `/api/health`
- 返回服务器状态

### 2. 获取投资组合
- **GET** `/api/portfolio`
- 返回完整投资组合数据

### 3. 添加交易记录
- **POST** `/api/transaction`
- 添加新的交易记录

### 4. 获取股票数据
- **GET** `/api/stock/{market}/{code}`
- 获取特定股票数据

## 启动说明

### 1. 启动API服务器
```bash
cd api
python app.py
```

### 2. 访问Web界面
打开浏览器访问: http://localhost:5000

### 3. 重启服务器
```bash
python restart_api.py
```

## 配置说明

### 环境要求
- Python 3.7+
- Flask
- requests
- sqlite3

### 依赖安装
```bash
pip install flask requests
```

### 数据库配置
- 自动创建SQLite数据库
- 数据文件: stock_portfolio.db

## 开发历史

### 2025-09-19 主要更新
1. **修复数据显示问题** - 解决"10.8万"显示错误
2. **优化基金数据抓取** - 多API源支持
3. **拆分涨跌数据** - 累计涨跌幅和今日涨跌幅
4. **改进美股数据源** - 添加Fallback机制
5. **优化前端性能** - 禁用自动更新函数

### 关键技术突破
1. **多API源切换** - 提高数据抓取成功率
2. **缓存机制** - 减少API调用频率
3. **错误处理** - 优雅降级机制
4. **数据验证** - 确保数据准确性

## 下一步开发计划

### 1. 美股数据源优化
- 集成Finnhub.io API
- 实现Polygon.io支持
- 优化Fallback数据更新机制

### 2. 功能增强
- 添加用户认证
- 实现数据导出功能
- 增加技术分析指标
- 移动端适配

### 3. 性能优化
- 数据库连接池
- API响应缓存
- 前端资源优化
- 服务器负载均衡

## 使用Claude Code继续开发

### 1. 项目迁移
将整个项目文件夹复制到新电脑:
```bash
# 复制项目文件夹
cp -r stock-portfolio-system/ /new/path/

# 进入项目目录
cd /new/path/stock-portfolio-system
```

### 2. 快速启动
```bash
# 启动API服务器
python api/app.py

# 访问Web界面
# http://localhost:5000
```

### 3. Claude Code开发建议
1. **首先阅读本文档** - 了解项目状态和已知问题
2. **查看API日志** - 了解当前数据源状态
3. **优先解决美股数据源** - 这是当前的主要问题
4. **测试所有功能** - 确保修改不影响现有功能

### 4. 开发环境准备
```bash
# 安装依赖
pip install flask requests

# 检查数据库
python -c "from database.database import StockDatabase; db = StockDatabase('stock_portfolio.db'); print('Database OK')"

# 启动服务器
python api/app.py
```

### 5. 常用开发命令
```bash
# 重启API服务器
python restart_api.py

# 重置数据库
python reset_database.py

# 测试API
curl http://localhost:5000/api/health

# 查看日志
tail -f /var/log/stock_portfolio.log
```

## 技术债务

### 1. 代码优化
- 重构重复代码
- 优化数据库查询
- 改进错误处理
- 添加单元测试

### 2. 安全性
- 添加输入验证
- 实现用户认证
- 加密敏感数据
- 防止SQL注入

### 3. 可扩展性
- 微服务架构
- 容器化部署
- 负载均衡
- 数据库分片

## 联系方式

如有问题或建议，请通过以下方式联系:
- 项目Issues: GitHub Issues
- 邮箱: [your-email@example.com]

---

**文档版本:** 1.0
**最后更新:** 2025-09-19
**维护者:** Claude Code Assistant