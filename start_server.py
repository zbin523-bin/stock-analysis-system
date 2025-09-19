#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票投资组合系统启动脚本
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

def main():
    print("=" * 60)
    print("股票投资组合管理系统")
    print("=" * 60)

    # 获取当前目录
    current_dir = Path(__file__).parent
    api_dir = current_dir / "api"

    # 检查文件是否存在
    app_file = api_dir / "app.py"
    if not app_file.exists():
        print(f"错误: 找不到API文件 {app_file}")
        return

    print("正在启动股票投资组合系统...")
    print("API服务器启动中...")

    try:
        # 启动Flask服务器
        process = subprocess.Popen([
            sys.executable, str(app_file)
        ], cwd=api_dir, creationflags=subprocess.CREATE_NEW_CONSOLE)

        # 等待服务器启动
        time.sleep(3)

        # 检查服务器是否运行
        import requests
        try:
            response = requests.get("http://localhost:5000/api/health", timeout=5)
            if response.status_code == 200:
                print("✅ API服务器启动成功!")
                print(f"🌐 API地址: http://localhost:5000")
                print(f"📊 健康检查: http://localhost:5000/api/health")
                print(f"💼 投资组合: http://localhost:5000/api/portfolio")
                print("")
                print("系统功能:")
                print("• 实时股票数据获取 (A股/美股/港股)")
                print("• 交易记录管理 (增删改查)")
                print("• 持仓管理 (自动计算盈亏)")
                print("• 数据持久化 (SQLite数据库)")
                print("• 动态更新 (交易与持仓同步)")
                print("")
                print("使用说明:")
                print("1. 服务器已在后台运行")
                print("2. 可以通过浏览器访问API接口")
                print("3. 或使用API客户端进行操作")
                print("4. 按 Ctrl+C 停止服务器")
                print("")
                print("主要API接口:")
                print("• GET /api/health - 健康检查")
                print("• GET /api/portfolio - 获取投资组合")
                print("• GET /api/transactions - 获取交易记录")
                print("• POST /api/transactions - 添加交易记录")
                print("• PUT /api/transactions/{id} - 更新交易记录")
                print("• DELETE /api/transactions/{id} - 删除交易记录")
                print("• GET /api/stock/a/{code} - 获取A股数据")
                print("• GET /api/stock/us/{symbol} - 获取美股数据")
                print("• GET /api/stock/hk/{code} - 获取港股数据")
                print("")
                print("数据库文件: stock_portfolio.db")
                print("日志文件: 控制台输出")

                # 询问是否打开浏览器
                try:
                    open_browser = input("\n是否打开浏览器查看API文档? (y/n): ").lower().strip()
                    if open_browser in ['y', 'yes', '是']:
                        webbrowser.open("http://localhost:5000/api/health")
                except:
                    pass

            else:
                print("❌ API服务器启动失败")
                process.terminate()

        except requests.exceptions.ConnectionError:
            print("❌ 无法连接到API服务器")
            process.terminate()
        except Exception as e:
            print(f"❌ 检查服务器状态时出错: {e}")
            process.terminate()

        print("\n按 Enter 键停止服务器...")
        input()

        # 停止服务器
        process.terminate()
        print("服务器已停止")

    except KeyboardInterrupt:
        print("\n正在停止服务器...")
    except Exception as e:
        print(f"启动服务器时出错: {e}")

if __name__ == "__main__":
    main()