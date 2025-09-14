#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书股票投资管理系统一键启动器
"""

import os
import sys
import subprocess
import time

def print_banner():
    """打印系统横幅"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                    🎯 飞书股票投资管理系统                     ║
║                                                              ║
║            📊 完整的多维表格投资管理解决方案                 ║
║            💼 支持A股/美股/港股/基金分类管理               ║
║            📈 实时统计分析与投资建议                         ║
║                                                              ║
║                     🚀 一键启动程序                         ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(banner)

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 6):
        print("❌ Python版本过低，需要Python 3.6或更高版本")
        print(f"当前版本: {sys.version}")
        return False
    else:
        print(f"✅ Python版本检查通过: {sys.version.split()[0]}")
        return True

def check_dependencies():
    """检查依赖库"""
    try:
        import requests
        print("✅ requests库已安装")
        return True
    except ImportError:
        print("❌ requests库未安装")
        print("正在安装requests库...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "requests"], check=True)
            print("✅ requests库安装成功")
            return True
        except subprocess.CalledProcessError:
            print("❌ requests库安装失败")
            return False

def check_files():
    """检查必要文件"""
    required_files = [
        "feishu_bitable_manager.py",
        "feishu_config_guide.py", 
        "feishu_analytics.py",
        "README_飞书股票投资管理系统.md"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ 以下文件缺失:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    else:
        print("✅ 所有必要文件检查通过")
        return True

def show_menu():
    """显示主菜单"""
    print("\n📋 主菜单:")
    print("=" * 50)
    print("1. 🛠️ 查看配置指南")
    print("2. 🏗️ 创建股票投资管理系统")
    print("3. 📊 生成投资分析报告")
    print("4. 📖 查看系统文档")
    print("5. 🔍 检查系统状态")
    print("6. 🔄 更新系统")
    print("7. 📞 技术支持")
    print("8. 🚪 退出")
    print("=" * 50)

def run_config_guide():
    """运行配置指南"""
    print("\n🛠️ 启动配置指南...")
    try:
        subprocess.run([sys.executable, "feishu_config_guide.py"], check=True)
    except subprocess.CalledProcessError:
        print("❌ 配置指南启动失败")

def create_system():
    """创建股票投资管理系统"""
    print("\n🏗️ 创建股票投资管理系统...")
    try:
        subprocess.run([sys.executable, "feishu_bitable_manager.py"], check=True)
    except subprocess.CalledProcessError:
        print("❌ 系统创建失败")

def generate_report():
    """生成投资分析报告"""
    print("\n📊 生成投资分析报告...")
    try:
        subprocess.run([sys.executable, "feishu_analytics.py"], check=True)
    except subprocess.CalledProcessError:
        print("❌ 报告生成失败")

def show_documentation():
    """显示系统文档"""
    print("\n📖 系统文档:")
    try:
        with open("README_飞书股票投资管理系统.md", "r", encoding="utf-8") as f:
            lines = f.readlines()
            # 显示前50行作为预览
            for i, line in enumerate(lines[:50]):
                print(f"{i+1:2d}: {line.rstrip()}")
        
        print(f"\n...文档继续...")
        print(f"\n📄 完整文档请查看: README_飞书股票投资管理系统.md")
        
    except FileNotFoundError:
        print("❌ 文档文件未找到")
    except Exception as e:
        print(f"❌ 读取文档失败: {e}")

def check_system_status():
    """检查系统状态"""
    print("\n🔍 系统状态检查:")
    print("=" * 50)
    
    # Python版本
    python_ok = check_python_version()
    
    # 依赖库
    deps_ok = check_dependencies()
    
    # 文件检查
    files_ok = check_files()
    
    # 总结
    print("\n📊 检查结果:")
    if python_ok and deps_ok and files_ok:
        print("✅ 系统状态正常，可以开始使用")
        print("💡 建议下一步: 选择菜单选项2创建系统")
    else:
        print("❌ 系统存在问题，请先解决")
        if not python_ok:
            print("   - 请升级Python版本")
        if not deps_ok:
            print("   - 请安装依赖库")
        if not files_ok:
            print("   - 请检查必要文件")

def show_technical_support():
    """显示技术支持信息"""
    support_info = """
📞 技术支持
============

🔗 官方资源:
- 飞书开放平台: https://open.feishu.cn/
- API文档: https://open.feishu.cn/document/
- 开发者社区: https://open.feishu.cn/community/

🛠️ 常用工具:
- 飞书API调试台: https://open.feishu.cn/api-explorer/
- 多维表格文档: https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/bitable/notification

📋 配置步骤:
1. 创建飞书应用
2. 开启必要权限
3. 启用机器人能力
4. 创建群组并添加机器人
5. 文件夹授权
6. 运行系统创建脚本

🔧 故障排除:
- 检查App ID和App Secret
- 确认权限设置正确
- 验证机器人能力启用
- 检查文件夹权限

💡 使用提示:
- 先运行配置指南了解详细步骤
- 按照说明完成飞书应用配置
- 运行系统创建脚本生成多维表格
- 使用分析功能生成投资报告

📞 如需帮助:
- 查看README文档
- 运行系统状态检查
- 参考飞书官方文档
"""
    print(support_info)

def update_system():
    """更新系统"""
    print("\n🔄 系统更新...")
    print("当前系统已经是最新版本")
    print("💡 如需更新功能，请重新下载最新代码")

def main():
    """主函数"""
    print_banner()
    
    # 检查系统状态
    if not check_python_version():
        input("按回车键退出...")
        return
    
    if not check_dependencies():
        input("按回车键退出...")
        return
    
    if not check_files():
        input("按回车键退出...")
        return
    
    print("\n✅ 系统检查完成，可以开始使用！")
    
    # 主循环
    while True:
        show_menu()
        choice = input("\n请选择功能 (1-8): ").strip()
        
        if choice == "1":
            run_config_guide()
        elif choice == "2":
            create_system()
        elif choice == "3":
            generate_report()
        elif choice == "4":
            show_documentation()
        elif choice == "5":
            check_system_status()
        elif choice == "6":
            update_system()
        elif choice == "7":
            show_technical_support()
        elif choice == "8":
            print("\n👋 感谢使用飞书股票投资管理系统！")
            print("💼 祝您投资顺利！")
            break
        else:
            print("❌ 无效选择，请输入1-8之间的数字")
        
        # 暂停
        if choice != "8":
            input("\n按回车键继续...")

if __name__ == "__main__":
    main()