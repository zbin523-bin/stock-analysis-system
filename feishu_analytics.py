#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书多维表格高级分析功能
实现总仓位、总营收、市场分类统计等功能
"""

import requests
import json
from typing import Dict, List, Any
from datetime import datetime, timedelta
from feishu_bitable_manager import FeishuBitableManager

class FeishuAnalytics:
    """飞书多维表格分析器"""
    
    def __init__(self, app_id: str, app_secret: str, app_token: str):
        self.bitable_manager = FeishuBitableManager(app_id, app_secret)
        self.app_token = app_token
        self.tables = {}
        
    def get_table_data(self, table_id: str) -> List[Dict]:
        """获取表格数据"""
        if not self.bitable_manager.access_token:
            self.bitable_manager.get_tenant_access_token()
            
        url = f"{self.bitable_manager.base_url}/bitable/v1/apps/{self.app_token}/tables/{table_id}/records"
        headers = {
            "Authorization": f"Bearer {self.bitable_manager.access_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            result = response.json()
            
            if result.get("code") == 0:
                records = result.get("data", {}).get("items", [])
                return records
            else:
                print(f"❌ 获取表格数据失败: {result.get('msg')}")
                return []
                
        except Exception as e:
            print(f"❌ 获取表格数据时出错: {e}")
            return []
    
    def calculate_total_position(self, holdings_data: List[Dict]) -> Dict[str, Any]:
        """计算总仓位"""
        total_value = 0
        total_profit = 0
        total_cost = 0
        
        market_stats = {
            "A股": {"value": 0, "profit": 0, "count": 0},
            "美股": {"value": 0, "profit": 0, "count": 0},
            "港股": {"value": 0, "profit": 0, "count": 0},
            "基金": {"value": 0, "profit": 0, "count": 0}
        }
        
        for record in holdings_data:
            fields = record.get("fields", {})
            
            try:
                market = fields.get("市场类型", "")
                market_value = float(fields.get("持仓市值", 0))
                profit = float(fields.get("盈亏金额", 0))
                cost = float(fields.get("买入价格", 0)) * float(fields.get("持仓数量", 0))
                
                total_value += market_value
                total_profit += profit
                total_cost += cost
                
                if market in market_stats:
                    market_stats[market]["value"] += market_value
                    market_stats[market]["profit"] += profit
                    market_stats[market]["count"] += 1
                    
            except (ValueError, TypeError) as e:
                print(f"⚠️ 跳过无效数据: {fields.get('股票代码', 'N/A')}")
                continue
        
        total_return_rate = (total_profit / total_cost * 100) if total_cost > 0 else 0
        
        return {
            "总市值": total_value,
            "总成本": total_cost,
            "总盈亏": total_profit,
            "总收益率": total_return_rate,
            "市场统计": market_stats,
            "持仓数量": sum(market_stats[market]["count"] for market in market_stats)
        }
    
    def calculate_trade_statistics(self, trade_data: List[Dict]) -> Dict[str, Any]:
        """计算交易统计"""
        total_trades = len(trade_data)
        buy_trades = 0
        sell_trades = 0
        total_buy_amount = 0
        total_sell_amount = 0
        
        trade_by_market = {}
        trade_by_month = {}
        
        for record in trade_data:
            fields = record.get("fields", {})
            
            try:
                trade_type = fields.get("交易类型", "")
                amount = float(fields.get("交易金额", 0))
                stock_code = fields.get("股票代码", "")
                trade_date = fields.get("交易日期", "")
                
                # 统计买卖交易
                if trade_type == "买入":
                    buy_trades += 1
                    total_buy_amount += amount
                elif trade_type == "卖出":
                    sell_trades += 1
                    total_sell_amount += amount
                
                # 按股票代码统计
                if stock_code not in trade_by_market:
                    trade_by_market[stock_code] = {"buy": 0, "sell": 0, "amount": 0}
                trade_by_market[stock_code][trade_type.lower()] += 1
                trade_by_market[stock_code]["amount"] += amount
                
                # 按月份统计
                if trade_date:
                    try:
                        month_key = trade_date[:7]  # YYYY-MM
                        if month_key not in trade_by_month:
                            trade_by_month[month_key] = 0
                        trade_by_month[month_key] += 1
                    except:
                        continue
                        
            except (ValueError, TypeError) as e:
                print(f"⚠️ 跳过无效交易数据: {fields.get('股票代码', 'N/A')}")
                continue
        
        net_amount = total_sell_amount - total_buy_amount
        
        return {
            "总交易次数": total_trades,
            "买入次数": buy_trades,
            "卖出次数": sell_trades,
            "买入总额": total_buy_amount,
            "卖出总额": total_sell_amount,
            "净交易额": net_amount,
            "按股票统计": trade_by_market,
            "按月份统计": trade_by_month
        }
    
    def analyze_price_trends(self, price_data: List[Dict]) -> Dict[str, Any]:
        """分析价格趋势"""
        price_trends = {}
        
        for record in price_data:
            fields = record.get("fields", {})
            
            try:
                stock_code = fields.get("股票代码", "")
                price = float(fields.get("价格", 0))
                change_pct = float(fields.get("涨跌幅", 0))
                timestamp = fields.get("时间戳", "")
                
                if stock_code not in price_trends:
                    price_trends[stock_code] = {
                        "prices": [],
                        "changes": [],
                        "latest_price": 0,
                        "avg_change": 0,
                        "volatility": 0
                    }
                
                price_trends[stock_code]["prices"].append(price)
                price_trends[stock_code]["changes"].append(change_pct)
                price_trends[stock_code]["latest_price"] = price
                
            except (ValueError, TypeError) as e:
                continue
        
        # 计算统计指标
        for stock_code, data in price_trends.items():
            if data["changes"]:
                data["avg_change"] = sum(data["changes"]) / len(data["changes"])
                data["volatility"] = sum(abs(c) for c in data["changes"]) / len(data["changes"])
        
        return price_trends
    
    def generate_investment_report(self, holdings_table_id: str, trade_table_id: str, price_table_id: str) -> Dict[str, Any]:
        """生成投资报告"""
        print("📊 正在生成投资分析报告...")
        
        # 获取数据
        holdings_data = self.get_table_data(holdings_table_id)
        trade_data = self.get_table_data(trade_table_id)
        price_data = self.get_table_data(price_table_id)
        
        # 计算统计指标
        position_stats = self.calculate_total_position(holdings_data)
        trade_stats = self.calculate_trade_statistics(trade_data)
        price_trends = self.analyze_price_trends(price_data)
        
        # 生成报告
        report = {
            "生成时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "持仓统计": position_stats,
            "交易统计": trade_stats,
            "价格趋势": price_trends,
            "投资建议": self.generate_investment_recommendations(position_stats, trade_stats, price_trends)
        }
        
        return report
    
    def generate_investment_recommendations(self, position_stats: Dict, trade_stats: Dict, price_trends: Dict) -> List[Dict]:
        """生成投资建议"""
        recommendations = []
        
        # 基于仓位分析
        total_value = position_stats["总市值"]
        market_stats = position_stats["市场统计"]
        
        # 检查市场配置建议
        for market, stats in market_stats.items():
            if stats["count"] > 0:
                weight = stats["value"] / total_value * 100 if total_value > 0 else 0
                if weight > 50:
                    recommendations.append({
                        "类型": "配置建议",
                        "股票代码": market,
                        "建议": f"{market}仓位占比{weight:.1f}%，建议适当分散风险",
                        "优先级": "中"
                    })
        
        # 基于盈亏分析
        total_profit = position_stats["总盈亏"]
        if total_profit < 0:
            recommendations.append({
                "类型": "风险提示",
                "股票代码": "整体组合",
                "建议": "当前组合处于亏损状态，建议审视持仓质量",
                "优先级": "高"
            })
        
        # 基于交易频率分析
        if trade_stats["总交易次数"] > 20:
            recommendations.append({
                "类型": "交易建议",
                "股票代码": "整体组合",
                "建议": "交易频率较高，建议降低交易频率，减少手续费支出",
                "优先级": "中"
            })
        
        # 基于价格趋势分析
        for stock_code, trends in price_trends.items():
            if trends["volatility"] > 5:  # 波动率超过5%
                recommendations.append({
                    "类型": "风险提示",
                    "股票代码": stock_code,
                    "建议": f"{stock_code}价格波动较大({trends['volatility']:.1f}%)，注意风险控制",
                    "优先级": "高"
                })
        
        return recommendations
    
    def print_investment_report(self, report: Dict[str, Any]):
        """打印投资报告"""
        print("\n" + "=" * 60)
        print("📊 股票投资分析报告")
        print("=" * 60)
        print(f"🕐 生成时间: {report['生成时间']}")
        
        # 持仓统计
        position_stats = report["持仓统计"]
        print(f"\n💼 持仓统计:")
        print(f"   总市值: ¥{position_stats['总市值']:,.2f}")
        print(f"   总成本: ¥{position_stats['总成本']:,.2f}")
        print(f"   总盈亏: ¥{position_stats['总盈亏']:,.2f}")
        print(f"   总收益率: {position_stats['总收益率']:.2f}%")
        print(f"   持仓数量: {position_stats['持仓数量']}只")
        
        print(f"\n📈 市场分布:")
        for market, stats in position_stats["市场统计"].items():
            if stats["count"] > 0:
                weight = stats["value"] / position_stats["总市值"] * 100 if position_stats["总市值"] > 0 else 0
                print(f"   {market}: ¥{stats['value']:,.2f} ({weight:.1f}%) 盈亏: ¥{stats['profit']:,.2f}")
        
        # 交易统计
        trade_stats = report["交易统计"]
        print(f"\n💰 交易统计:")
        print(f"   总交易次数: {trade_stats['总交易次数']}")
        print(f"   买入次数: {trade_stats['买入次数']}")
        print(f"   卖出次数: {trade_stats['卖出次数']}")
        print(f"   买入总额: ¥{trade_stats['买入总额']:,.2f}")
        print(f"   卖出总额: ¥{trade_stats['卖出总额']:,.2f}")
        print(f"   净交易额: ¥{trade_stats['净交易额']:,.2f}")
        
        # 投资建议
        recommendations = report["投资建议"]
        print(f"\n💡 投资建议:")
        for i, rec in enumerate(recommendations, 1):
            priority_icon = "🔴" if rec["优先级"] == "高" else "🟡" if rec["优先级"] == "中" else "🟢"
            print(f"   {i}. {priority_icon} [{rec['类型']}] {rec['股票代码']}: {rec['建议']}")
        
        print("\n" + "=" * 60)
    
    def export_report_to_json(self, report: Dict[str, Any], filename: str = None):
        """导出报告到JSON文件"""
        if filename is None:
            filename = f"investment_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            print(f"✅ 报告已导出到: {filename}")
        except Exception as e:
            print(f"❌ 导出报告失败: {e}")

def main():
    """主函数"""
    print("📊 飞书多维表格分析工具")
    print("=" * 60)
    
    # 配置信息
    app_id = input("请输入飞书应用的App ID: ").strip()
    app_secret = input("请输入飞书应用的App Secret: ").strip()
    app_token = input("请输入多维表格的App Token: ").strip()
    
    if not all([app_id, app_secret, app_token]):
        print("❌ 请输入完整的配置信息")
        return
    
    try:
        # 创建分析器
        analyzer = FeishuAnalytics(app_id, app_secret, app_token)
        
        # 生成报告
        report = analyzer.generate_investment_report(
            holdings_table_id="tblxxxxxxxx",  # 替换为实际的持仓表ID
            trade_table_id="tblxxxxxxxx",     # 替换为实际的交易表ID
            price_table_id="tblxxxxxxxx"      # 替换为实际的价格表ID
        )
        
        # 打印报告
        analyzer.print_investment_report(report)
        
        # 导出报告
        export_choice = input("\n是否导出报告到JSON文件? (y/n): ").strip().lower()
        if export_choice == 'y':
            analyzer.export_report_to_json(report)
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")

if __name__ == "__main__":
    main()