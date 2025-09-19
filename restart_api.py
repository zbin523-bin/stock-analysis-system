#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重启API服务器
"""

import os
import sys
import subprocess
import time
import requests

def restart_api_server():
    """重启API服务器"""
    print("正在重启API服务器...")

    # 停止现有的Python进程
    try:
        # 在Windows上停止Python进程
        subprocess.run(['taskkill', '/F', '/IM', 'python.exe'], shell=True, check=False)
        print("已停止现有Python进程")
    except Exception as e:
        print(f"停止进程失败: {e}")

    # 等待一下
    time.sleep(2)

    # 启动新的API服务器
    try:
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        api_path = os.path.join('api', 'app.py')

        # 启动API服务器
        subprocess.Popen([sys.executable, api_path])
        print("已启动新的API服务器")

        # 等待服务器启动
        time.sleep(3)

        # 测试服务器
        try:
            response = requests.get("http://localhost:5000/api/health", timeout=5)
            if response.status_code == 200:
                print("API服务器启动成功！")
                return True
            else:
                print(f"API服务器启动失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"API服务器连接失败: {e}")
            return False

    except Exception as e:
        print(f"启动API服务器失败: {e}")
        return False

if __name__ == "__main__":
    if restart_api_server():
        print("API服务器重启成功")
    else:
        print("API服务器重启失败")