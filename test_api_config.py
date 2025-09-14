#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试API配置和邮件配置
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_alpha_vantage_api():
    """测试Alpha Vantage API"""
    api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
    print(f"测试API密钥: {api_key}")
    
    if not api_key:
        print("❌ API密钥未配置")
        return False
    
    # 测试API调用
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": "00700.HK",
        "outputsize": "compact",
        "apikey": api_key
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        print(f"API响应状态: {response.status_code}")
        print(f"API响应内容: {data}")
        
        if "Time Series (Daily)" in data:
            print("✅ API调用成功")
            return True
        elif "Error Message" in data:
            print(f"❌ API错误: {data['Error Message']}")
            return False
        elif "Note" in data:
            print(f"⚠️ API限制: {data['Note']}")
            return False
        else:
            print("❌ 未知API响应")
            return False
            
    except Exception as e:
        print(f"❌ API调用异常: {e}")
        return False

def test_email_config():
    """测试邮件配置"""
    email_sender = os.getenv('EMAIL_SENDER')
    email_password = os.getenv('EMAIL_PASSWORD')
    email_receiver = os.getenv('EMAIL_RECEIVER')
    
    print(f"\n邮件配置检查:")
    print(f"发件人: {email_sender}")
    print(f"密码: {'已配置' if email_password else '未配置'}")
    print(f"收件人: {email_receiver}")
    
    missing = []
    if not email_sender:
        missing.append("EMAIL_SENDER")
    if not email_password:
        missing.append("EMAIL_PASSWORD")
    
    if missing:
        print(f"❌ 缺少配置: {', '.join(missing)}")
        return False
    else:
        print("✅ 邮件配置完整")
        return True

def main():
    print("=" * 50)
    print("股票分析系统配置测试")
    print("=" * 50)
    
    # 测试API
    api_ok = test_alpha_vantage_api()
    
    # 测试邮件
    email_ok = test_email_config()
    
    print("\n" + "=" * 50)
    print("测试结果:")
    print(f"API配置: {'✅ 正常' if api_ok else '❌ 异常'}")
    print(f"邮件配置: {'✅ 正常' if email_ok else '❌ 异常'}")
    
    if api_ok and email_ok:
        print("\n🎉 所有配置正常，可以运行股票分析系统！")
        print("\n运行命令:")
        print("python3 stock_analyzer_simple.py")
    else:
        print("\n⚠️ 请先修复配置问题")
        
        if not api_ok:
            print("\n🔧 API修复建议:")
            print("1. 检查API密钥是否正确: 5DGMRPMMEUBMX7PU")
            print("2. 等待1分钟后重试（API限制）")
            print("3. 访问 https://www.alphavantage.co/support/#api-key 确认密钥状态")
        
        if not email_ok:
            print("\n📧 邮件配置步骤:")
            print("1. 在.env文件中配置Gmail邮箱")
            print("2. 开启Gmail两步验证")
            print("3. 生成应用专用密码")
            print("4. 将应用专用密码填入EMAIL_PASSWORD字段")

if __name__ == "__main__":
    main()