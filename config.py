import os
from datetime import datetime, timedelta

# Gmail配置
GMAIL_EMAIL = os.environ.get('GMAIL_EMAIL', 'your_email@gmail.com')
GMAIL_PASSWORD = os.environ.get('GMAIL_PASSWORD', 'your_app_password')

# 投资组合配置
STOCKS_CONFIG = {
    "腾讯控股": {"code": "00700.HK", "quantity": 300, "avg_cost": 320.85, "currency": "HKD"},
    "中芯国际": {"code": "00981.HK", "quantity": 1000, "avg_cost": 47.55, "currency": "HKD"},
    "小米集团-W": {"code": "01810.HK", "quantity": 2000, "avg_cost": 47.1071, "currency": "HKD"},
    "中国人寿": {"code": "02628.HK", "quantity": 2000, "avg_cost": 23.82, "currency": "HKD"},
    "美团-W": {"code": "03690.HK", "quantity": 740, "avg_cost": 123.2508, "currency": "HKD"},
    "新东方-S": {"code": "09901.HK", "quantity": 2000, "avg_cost": 44.3241, "currency": "HKD"},
    "阿里巴巴-W": {"code": "09988.HK", "quantity": 500, "avg_cost": 113.74, "currency": "HKD"}
}

# 汇率配置
HKD_TO_CNY = 0.92  # 港币兑人民币汇率

# 数据存储配置
DATA_FILE = "stock_trades.json"
POSITIONS_FILE = "stock_positions.json"

# 调度配置
SCHEDULE_TIMES = ["10:00", "16:00"]  # 发送时间
TIMEZONE = "Asia/Shanghai"