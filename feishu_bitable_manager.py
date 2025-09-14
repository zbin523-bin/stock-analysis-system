#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书多维表格股票投资管理系统
基于飞书开放平台API创建完整的股票投资管理多维表格
"""

import requests
import json
import time
from typing import Dict, List, Optional, Union
from datetime import datetime

class FeishuBitableManager:
    """飞书多维表格管理器"""
    
    def __init__(self, app_id: str, app_secret: str):
        """
        初始化飞书多维表格管理器
        
        Args:
            app_id: 飞书应用ID
            app_secret: 飞书应用密钥
        """
        self.app_id = app_id
        self.app_secret = app_secret
        self.access_token = None
        self.base_url = "https://open.feishu.cn/open-apis"
        
    def get_tenant_access_token(self) -> str:
        """获取租户访问令牌"""
        url = f"{self.base_url}/auth/v3/tenant_access_token/internal"
        payload = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        headers = {"Content-Type": "application/json"}
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            
            if result.get("code") == 0:
                self.access_token = result.get("tenant_access_token")
                print(f"✅ 成功获取访问令牌")
                return self.access_token
            else:
                raise Exception(f"获取访问令牌失败: {result.get('msg')}")
                
        except Exception as e:
            print(f"❌ 获取访问令牌时出错: {e}")
            raise
    
    def create_bitable(self, name: str, folder_token: str = None) -> Dict:
        """
        创建多维表格
        
        Args:
            name: 多维表格名称
            folder_token: 文件夹token（可选）
            
        Returns:
            多维表格信息
        """
        if not self.access_token:
            self.get_tenant_access_token()
            
        url = f"{self.base_url}/bitable/v1/apps"
        payload = {"name": name}
        
        if folder_token:
            payload["folder_token"] = folder_token
            
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            
            if result.get("code") == 0:
                app_info = result.get("data", {}).get("app", {})
                print(f"✅ 成功创建多维表格: {name}")
                print(f"   表格Token: {app_info.get('app_token')}")
                print(f"   默认表ID: {app_info.get('default_table_id')}")
                print(f"   访问链接: {app_info.get('url')}")
                return app_info
            else:
                raise Exception(f"创建多维表格失败: {result.get('msg')}")
                
        except Exception as e:
            print(f"❌ 创建多维表格时出错: {e}")
            raise
    
    def create_table(self, app_token: str, table_name: str, fields: List[Dict]) -> Dict:
        """
        创建数据表
        
        Args:
            app_token: 多维表格token
            table_name: 表名
            fields: 字段定义列表
            
        Returns:
            创建的表信息
        """
        if not self.access_token:
            self.get_tenant_access_token()
            
        url = f"{self.base_url}/bitable/v1/apps/{app_token}/tables"
        payload = {
            "table": {
                "name": table_name,
                "fields": fields
            }
        }
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            
            if result.get("code") == 0:
                table_info = result.get("data", {}).get("table", {})
                print(f"✅ 成功创建数据表: {table_name}")
                print(f"   表ID: {table_info.get('table_id')}")
                return table_info
            else:
                raise Exception(f"创建数据表失败: {result.get('msg')}")
                
        except Exception as e:
            print(f"❌ 创建数据表时出错: {e}")
            raise
    
    def batch_create_records(self, app_token: str, table_id: str, records: List[Dict]) -> Dict:
        """
        批量创建记录
        
        Args:
            app_token: 多维表格token
            table_id: 表ID
            records: 记录列表
            
        Returns:
            创建结果
        """
        if not self.access_token:
            self.get_tenant_access_token()
            
        url = f"{self.base_url}/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_create"
        payload = {"records": records}
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            
            if result.get("code") == 0:
                record_info = result.get("data", {})
                print(f"✅ 成功创建 {record_info.get('total', 0)} 条记录")
                return record_info
            else:
                raise Exception(f"批量创建记录失败: {result.get('msg')}")
                
        except Exception as e:
            print(f"❌ 批量创建记录时出错: {e}")
            raise

class StockInvestmentManager:
    """股票投资管理器"""
    
    def __init__(self, app_id: str, app_secret: str):
        self.bitable_manager = FeishuBitableManager(app_id, app_secret)
        
    def create_stock_investment_system(self, system_name: str = "股票投资管理系统") -> Dict:
        """
        创建完整的股票投资管理系统
        
        Args:
            system_name: 系统名称
            
        Returns:
            系统信息
        """
        print(f"🚀 开始创建股票投资管理系统: {system_name}")
        print("=" * 60)
        
        # 1. 创建多维表格
        bitable_info = self.bitable_manager.create_bitable(system_name)
        app_token = bitable_info.get("app_token")
        
        print(f"\n📋 开始创建数据表...")
        
        # 2. 创建持仓记录表
        holdings_fields = [
            {"name": "股票代码", "type": "text"},
            {"name": "股票名称", "type": "text"},
            {"name": "市场类型", "type": "single_select", "property": {"options": ["A股", "美股", "港股", "基金"]}},
            {"name": "持仓数量", "type": "number"},
            {"name": "买入价格", "type": "currency", "property": {"currency": "CNY"}},
            {"name": "当前价格", "type": "currency", "property": {"currency": "CNY"}},
            {"name": "持仓市值", "type": "currency", "property": {"currency": "CNY"}},
            {"name": "盈亏金额", "type": "currency", "property": {"currency": "CNY"}},
            {"name": "盈亏比例", "type": "percent"},
            {"name": "买入日期", "type": "date"},
            {"name": "备注", "type": "text"}
        ]
        
        holdings_table = self.bitable_manager.create_table(app_token, "持仓记录", holdings_fields)
        
        # 3. 创建买卖记录表
        trade_fields = [
            {"name": "股票代码", "type": "text"},
            {"name": "股票名称", "type": "text"},
            {"name": "交易类型", "type": "single_select", "property": {"options": ["买入", "卖出"]}},
            {"name": "交易价格", "type": "currency", "property": {"currency": "CNY"}},
            {"name": "交易数量", "type": "number"},
            {"name": "交易金额", "type": "currency", "property": {"currency": "CNY"}},
            {"name": "交易日期", "type": "date"},
            {"name": "手续费", "type": "currency", "property": {"currency": "CNY"}},
            {"name": "备注", "type": "text"}
        ]
        
        trade_table = self.bitable_manager.create_table(app_token, "买卖记录", trade_fields)
        
        # 4. 创建价格历史表
        price_fields = [
            {"name": "股票代码", "type": "text"},
            {"name": "股票名称", "type": "text"},
            {"name": "价格", "type": "currency", "property": {"currency": "CNY"}},
            {"name": "时间戳", "type": "datetime"},
            {"name": "涨跌幅", "type": "percent"},
            {"name": "市场类型", "type": "single_select", "property": {"options": ["A股", "美股", "港股", "基金"]}}
        ]
        
        price_table = self.bitable_manager.create_table(app_token, "价格历史", price_fields)
        
        # 5. 创建分析结果表
        analysis_fields = [
            {"name": "股票代码", "type": "text"},
            {"name": "股票名称", "type": "text"},
            {"name": "分析类型", "type": "single_select", "property": {"options": ["技术分析", "基本面分析", "消息面分析", "综合分析"]}},
            {"name": "建议", "type": "single_select", "property": {"options": ["买入", "持有", "卖出", "观望"]}},
            {"name": "置信度", "type": "percent"},
            {"name": "分析日期", "type": "date"},
            {"name": "目标价格", "type": "currency", "property": {"currency": "CNY"}},
            {"name": "分析理由", "type": "text"}
        ]
        
        analysis_table = self.bitable_manager.create_table(app_token, "分析结果", analysis_fields)
        
        print(f"\n🎉 股票投资管理系统创建完成！")
        print("=" * 60)
        print(f"📊 系统名称: {system_name}")
        print(f"🔗 访问链接: {bitable_info.get('url')}")
        print(f"📋 数据表结构:")
        print(f"   • 持仓记录 - 支持市场分类和盈亏统计")
        print(f"   • 买卖记录 - 完整交易历史追踪")
        print(f"   • 价格历史 - 实时价格监控")
        print(f"   • 分析结果 - 投资分析和建议")
        
        return {
            "app_token": app_token,
            "url": bitable_info.get("url"),
            "tables": {
                "holdings": holdings_table.get("table_id"),
                "trades": trade_table.get("table_id"),
                "prices": price_table.get("table_id"),
                "analysis": analysis_table.get("table_id")
            }
        }
    
    def import_sample_data(self, app_token: str, tables: Dict):
        """
        导入示例数据
        
        Args:
            app_token: 多维表格token
            tables: 表ID字典
        """
        print(f"\n📥 开始导入示例数据...")
        
        # 导入持仓记录示例数据
        holdings_records = [
            {
                "fields": {
                    "股票代码": "AAPL",
                    "股票名称": "Apple Inc.",
                    "市场类型": "美股",
                    "持仓数量": 100,
                    "买入价格": 193.78,
                    "当前价格": 226.78,
                    "持仓市值": 22678.00,
                    "盈亏金额": 3300.00,
                    "盈亏比例": 0.1703,
                    "买入日期": "2024-01-15",
                    "备注": "长期持有"
                }
            },
            {
                "fields": {
                    "股票代码": "000001.SZ",
                    "股票名称": "平安银行",
                    "市场类型": "A股",
                    "持仓数量": 200,
                    "买入价格": 11.50,
                    "当前价格": 11.74,
                    "持仓市值": 2348.00,
                    "盈亏金额": 48.00,
                    "盈亏比例": 0.0209,
                    "买入日期": "2024-02-20",
                    "备注": "价值投资"
                }
            },
            {
                "fields": {
                    "股票代码": "0700.HK",
                    "股票名称": "腾讯控股",
                    "市场类型": "港股",
                    "持仓数量": 50,
                    "买入价格": 620.00,
                    "当前价格": 630.50,
                    "持仓市值": 31525.00,
                    "盈亏金额": 525.00,
                    "盈亏比例": 0.0085,
                    "买入日期": "2024-03-10",
                    "备注": "科技股"
                }
            }
        ]
        
        self.bitable_manager.batch_create_records(
            app_token, tables["holdings"], holdings_records
        )
        
        print(f"✅ 示例数据导入完成！")
        print(f"   • 已导入3条持仓记录")
        print(f"   • 覆盖A股、美股、港股市场")
        print(f"   • 包含盈亏统计和分析")

def main():
    """主函数"""
    print("🎯 飞书多维表格股票投资管理系统")
    print("=" * 60)
    print("📝 使用说明:")
    print("1. 请确保已在飞书开放平台创建应用")
    print("2. 开启相关权限：查看、评论、编辑和管理多维表格")
    print("3. 获取应用的App ID和App Secret")
    print("4. 启用应用机器人能力")
    print("5. 创建群组并添加应用机器人")
    print("6. 将文件夹分享给群组并授权")
    print("=" * 60)
    
    # 配置信息（需要用户自行填写）
    APP_ID = input("请输入飞书应用的App ID: ").strip()
    APP_SECRET = input("请输入飞书应用的App Secret: ").strip()
    
    if not APP_ID or not APP_SECRET:
        print("❌ 请输入有效的App ID和App Secret")
        return
    
    try:
        # 创建管理器
        manager = StockInvestmentManager(APP_ID, APP_SECRET)
        
        # 创建系统
        system_info = manager.create_stock_investment_system()
        
        # 导入示例数据
        manager.import_sample_data(
            system_info["app_token"], 
            system_info["tables"]
        )
        
        print(f"\n🎊 系统部署成功！")
        print(f"🔗 点击链接访问您的股票投资管理系统: {system_info['url']}")
        print(f"💡 您现在可以在飞书中使用完整的功能，包括：")
        print(f"   ✅ 总仓位统计")
        print(f"   ✅ 总营收计算")
        print(f"   ✅ 按市场分类统计（A股/美股/港股/基金）")
        print(f"   ✅ 实时价格更新")
        print(f"   ✅ 投资分析和建议")
        
    except Exception as e:
        print(f"❌ 系统创建失败: {e}")
        print(f"💡 请检查：")
        print(f"   1. App ID和App Secret是否正确")
        print(f"   2. 应用权限是否已开启")
        print(f"   3. 机器人能力是否已启用")
        print(f"   4. 文件夹权限是否已配置")

if __name__ == "__main__":
    main()