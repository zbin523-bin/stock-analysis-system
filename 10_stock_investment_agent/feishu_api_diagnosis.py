#!/usr/bin/env python3
"""
飞书API诊断工具
检查访问令牌和应用状态
"""

import json
import requests
from datetime import datetime
from utils.feishu_bitable_manager import FeishuBitableManager

def test_feishu_api_token():
    """测试飞书API访问令牌"""
    print("=" * 80)
    print("🔍 飞书API访问令牌测试")
    print("=" * 80)
    
    try:
        # 初始化飞书管理器
        with open('config/api_keys.json', 'r', encoding='utf-8') as f:
            api_keys = json.load(f)
        
        manager = FeishuBitableManager(api_keys['feishu'])
        
        # 测试获取访问令牌
        print("📡 正在获取访问令牌...")
        token = manager.get_access_token()
        
        if token:
            print(f"✅ 访问令牌获取成功: {token[:20]}...")
            
            # 测试令牌有效性
            print("🔍 正在验证令牌有效性...")
            
            # 测试用户信息API
            user_url = f"{manager.base_url}/contact/v3/users/me"
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(user_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                user_data = response.json()
                if user_data.get('code') == 0:
                    print("✅ 访问令牌验证成功")
                    print(f"👤 用户信息: {user_data.get('data', {}).get('name', 'N/A')}")
                else:
                    print(f"⚠️  令牌验证失败: {user_data.get('msg', 'Unknown error')}")
            else:
                print(f"❌ 令牌验证请求失败: {response.status_code}")
                print(f"   错误信息: {response.text}")
            
            return True
        else:
            print("❌ 访问令牌获取失败")
            return False
            
    except Exception as e:
        print(f"❌ API测试异常: {e}")
        return False

def test_app_creation():
    """测试应用创建"""
    print("\n" + "=" * 80)
    print("🏗️ 飞书应用创建测试")
    print("=" * 80)
    
    try:
        with open('config/api_keys.json', 'r', encoding='utf-8') as f:
            api_keys = json.load(f)
        
        manager = FeishuBitableManager(api_keys['feishu'])
        
        # 创建新应用
        print("📝 正在创建测试应用...")
        app_result = manager.create_app("股票投资分析测试应用")
        
        if app_result:
            print(f"✅ 应用创建成功: {app_result}")
            
            # 测试应用访问
            app_url = f"{manager.base_url}/bitable/v1/apps/{app_result}"
            token = manager.get_access_token()
            
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            print("🔍 正在验证应用访问...")
            response = requests.get(app_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                app_data = response.json()
                if app_data.get('code') == 0:
                    print("✅ 应用访问验证成功")
                    print(f"📱 应用名称: {app_data.get('data', {}).get('name', 'N/A')}")
                    print(f"🆔 应用Token: {app_result}")
                else:
                    print(f"⚠️  应用访问失败: {app_data.get('msg', 'Unknown error')}")
            else:
                print(f"❌ 应用访问请求失败: {response.status_code}")
                print(f"   错误信息: {response.text}")
            
            return app_result
        else:
            print("❌ 应用创建失败")
            return None
            
    except Exception as e:
        print(f"❌ 应用创建异常: {e}")
        return None

def check_existing_apps():
    """检查已存在的应用"""
    print("\n" + "=" * 80)
    print("📋 检查已存在的应用")
    print("=" * 80)
    
    try:
        with open('config/api_keys.json', 'r', encoding='utf-8') as f:
            api_keys = json.load(f)
        
        manager = FeishuBitableManager(api_keys['feishu'])
        token = manager.get_access_token()
        
        # 获取应用列表
        apps_url = f"{manager.base_url}/bitable/v1/apps"
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        print("📡 正在获取应用列表...")
        response = requests.get(apps_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            apps_data = response.json()
            if apps_data.get('code') == 0:
                apps = apps_data.get('data', {}).get('items', [])
                print(f"✅ 找到 {len(apps)} 个应用")
                
                for app in apps:
                    app_token = app.get('app_token')
                    app_name = app.get('name')
                    print(f"   📱 {app_name} ({app_token})")
                
                return apps
            else:
                print(f"⚠️  获取应用列表失败: {apps_data.get('msg', 'Unknown error')}")
        else:
            print(f"❌ 获取应用列表请求失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
        
        return []
        
    except Exception as e:
        print(f"❌ 检查应用异常: {e}")
        return []

def analyze_access_error():
    """分析访问错误"""
    print("\n" + "=" * 80)
    print("🔍 访问错误分析")
    print("=" * 80)
    
    print("❌ 错误代码: 99991661")
    print("❌ 错误信息: Missing access token for authorization")
    print()
    
    print("🔧 可能的原因:")
    print("-" * 40)
    print("1. 📱 飞书应用配置错误")
    print("2. 🔑 应用权限不足")
    print("3. 🌐 API链接格式错误")
    print("4. 🚫 应用未发布或已禁用")
    print("5. 🔐 用户权限问题")
    print()
    
    print("💡 解决方案:")
    print("-" * 40)
    print("1. 检查飞书应用配置")
    print("2. 确认应用权限设置")
    print("3. 使用正确的访问链接")
    print("4. 联系飞书管理员")
    print()
    
    print("📞 飞书技术支持:")
    print("-" * 40)
    print("🔗 排查建议: https://open.feishu.cn/search?from=openapi&log_id=202509111202409080CA46FA4285715A2B&code=99991661&method_id=6965347212289654786")

def show_correct_access_method():
    """显示正确的访问方法"""
    print("\n" + "=" * 80)
    print("✅ 正确的飞书应用访问方法")
    print("=" * 80)
    
    print("🌐 飞书应用访问的正确步骤:")
    print("-" * 40)
    print("1. 📱 打开飞书桌面端或网页版")
    print("2. 🔐 使用您的飞书账号登录")
    print("3. 🏢 进入您的工作空间")
    print("4. 🔍 在工作台中搜索'多维表格'")
    print("5. ➕ 创建新的多维表格")
    print("6. 📋 导入CSV数据文件")
    print()
    
    print("🔗 直接API链接的问题:")
    print("-" * 40)
    print("❌ API链接需要访问令牌")
    print("❌ 浏览器直接访问无法提供令牌")
    print("❌ 需要通过飞书客户端访问")
    print()
    
    print("✅ 推荐的替代方案:")
    print("-" * 40)
    print("1. 📱 使用飞书客户端手动创建表格")
    print("2. 📊 导入系统生成的CSV文件")
    print("3. 🔗 使用飞书分享功能生成链接")
    print("4. 📧 通过邮件接收数据更新")

def main():
    print("🎯 飞书API诊断工具")
    print(f"📅 运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 测试API令牌
    token_ok = test_feishu_api_token()
    
    # 2. 检查已存在的应用
    existing_apps = check_existing_apps()
    
    # 3. 测试应用创建
    if token_ok:
        new_app_token = test_app_creation()
    else:
        new_app_token = None
    
    # 4. 分析访问错误
    analyze_access_error()
    
    # 5. 显示正确的访问方法
    show_correct_access_method()
    
    print("\n" + "=" * 80)
    print("✅ 诊断完成")
    print("=" * 80)
    
    if token_ok and existing_apps:
        print("💡 建议: 飞书API正常，请使用飞书客户端访问应用")
    elif token_ok:
        print("💡 建议: API正常，但需要创建应用或配置权限")
    else:
        print("💡 建议: 飞书API配置有问题，请检查应用凭证")

if __name__ == "__main__":
    main()