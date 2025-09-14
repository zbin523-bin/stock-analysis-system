#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书多维表格配置指南
帮助用户完成飞书开放平台应用的配置和权限设置
"""

def print_config_guide():
    """打印配置指南"""
    
    guide = """
🔧 飞书多维表格股票投资管理系统配置指南
============================================================

📋 第一步：创建飞书应用
----------------------------
1. 访问飞书开放平台：https://open.feishu.cn/app/
2. 点击"创建应用"
3. 选择"企业自建应用"
4. 填写应用信息：
   - 应用名称：股票投资管理系统
   - 应用描述：股票投资管理和分析系统
   - 应用图标：选择合适的图标

🔑 第二步：获取应用凭证
----------------------------
1. 进入应用详情页
2. 点击"凭证与基础信息"
3. 获取以下信息：
   - App ID: cli_**********
   - App Secret: ********************************
4. 记录这些信息，稍后需要使用

📋 第三步：开启应用权限
----------------------------
必须开启以下权限：
1. 查看、评论、编辑和管理多维表格
2. 查看、评论、编辑和管理云空间中所有文件
3. 查看云空间中文件元数据
4. 获取与发送单聊、群组消息
5. 获取用户在群组中@机器人的消息

🤖 第四步：启用机器人能力
----------------------------
1. 在应用后台点击"应用能力"
2. 点击"添加应用能力"
3. 选择"机器人"并添加
4. 创建机器人版本并提交审核
5. 审核通过后即可使用

👥 第五步：创建群组并添加机器人
----------------------------
1. 打开飞书客户端
2. 创建新群组（可以创建一人群组）
3. 群名称：股票投资管理系统
4. 点击群设置 > 群机器人
5. 找到您的应用机器人并添加

📁 第六步：文件夹授权
----------------------------
1. 在飞书云文档中创建或选择文件夹
2. 右键点击文件夹，选择"分享"
3. 选择"添加协作者"
4. 搜索并选择刚才创建的群组
5. 授予"管理权限"
6. 记录文件夹token（可选）

⚙️ 第七步：运行系统
----------------------------
1. 运行配置脚本：
   python3 feishu_bitable_manager.py
   
2. 输入App ID和App Secret
3. 系统将自动创建多维表格和数据表
4. 导入示例数据

📊 第八步：使用系统
----------------------------
系统创建完成后，您将获得：
- 4个功能完整的数据表
- 总仓位和总营收统计
- 按市场分类的统计分析
- 实时价格更新功能
- 投资分析和建议系统

🔧 故障排除
----------------------------
常见问题及解决方案：

1. "获取访问令牌失败"
   - 检查App ID和App Secret是否正确
   - 确认应用已发布

2. "创建多维表格失败"
   - 确认已开启多维表格权限
   - 检查文件夹权限设置

3. "没有云空间节点权限"
   - 确认应用机器人能力已启用
   - 确认文件夹已分享给群组

4. "权限不足"
   - 确认所有必需权限已开启
   - 确认应用版本已发布

📞 技术支持
----------------------------
如遇到问题，请检查：
1. 飞书开放平台文档：https://open.feishu.cn/
2. 应用权限配置
3. 机器人能力设置
4. 文件夹分享权限

============================================================
🎯 配置完成后，您将拥有一个功能完整的股票投资管理系统！
"""
    
    print(guide)

def check_requirements():
    """检查环境要求"""
    print("🔍 检查环境要求...")
    
    try:
        import requests
        print("✅ requests库已安装")
    except ImportError:
        print("❌ requests库未安装，请运行: pip install requests")
    
    try:
        import json
        print("✅ json库已安装")
    except ImportError:
        print("❌ json库未安装")
    
    try:
        from datetime import datetime
        print("✅ datetime库已安装")
    except ImportError:
        print("❌ datetime库未安装")
    
    print("\n📋 Python版本检查...")
    import sys
    print(f"Python版本: {sys.version}")
    
    if sys.version_info >= (3, 6):
        print("✅ Python版本符合要求")
    else:
        print("❌ Python版本过低，需要Python 3.6+")
    
    print("\n🌐 网络连接检查...")
    try:
        response = requests.get("https://open.feishu.cn", timeout=10)
        if response.status_code == 200:
            print("✅ 可以访问飞书开放平台")
        else:
            print("❌ 无法访问飞书开放平台")
    except:
        print("❌ 网络连接异常")

def main():
    """主函数"""
    print("🛠️ 飞书多维表格配置工具")
    print("=" * 60)
    
    print("\n📋 功能菜单:")
    print("1. 查看配置指南")
    print("2. 检查环境要求")
    print("3. 生成配置模板")
    print("4. 退出")
    
    while True:
        choice = input("\n请选择功能 (1-4): ").strip()
        
        if choice == "1":
            print_config_guide()
        elif choice == "2":
            check_requirements()
        elif choice == "3":
            generate_config_template()
        elif choice == "4":
            print("👋 再见！")
            break
        else:
            print("❌ 无效选择，请重新输入")

def generate_config_template():
    """生成配置模板"""
    config = """
# 飞书应用配置模板
# 请将以下信息替换为您的实际应用信息

APP_ID = "cli_xxxxxxxxxxxxxxxx"  # 替换为您的App ID
APP_SECRET = "xxxxxxxxxxxxxxxx"  # 替换为您的App Secret

# 可选配置
SYSTEM_NAME = "股票投资管理系统"
FOLDER_TOKEN = ""  # 可选：指定文件夹token

# 示例数据配置
IMPORT_SAMPLE_DATA = True
SAMPLE_HOLDINGS = [
    {
        "股票代码": "AAPL",
        "股票名称": "Apple Inc.",
        "市场类型": "美股",
        "持仓数量": 100,
        "买入价格": 193.78,
        "当前价格": 226.78,
        "买入日期": "2024-01-15",
        "备注": "长期持有"
    },
    # 可以添加更多示例数据
]

# 权限要求
REQUIRED_PERMISSIONS = [
    "查看、评论、编辑和管理多维表格",
    "查看、评论、编辑和管理云空间中所有文件", 
    "查看云空间中文件元数据",
    "获取与发送单聊、群组消息",
    "获取用户在群组中@机器人的消息"
]
"""
    
    print("📄 配置模板已生成：")
    print("=" * 50)
    print(config)
    print("=" * 50)
    print("💡 请将上述配置保存为 config.py 文件")
    print("💡 并填入您的实际应用信息")

if __name__ == "__main__":
    main()