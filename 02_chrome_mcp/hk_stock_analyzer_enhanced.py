#!/usr/bin/env python3
"""
Hong Kong Stock Price Analyzer - Enhanced Version
Provides comprehensive analysis of Hong Kong stocks with portfolio management
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('hk_stock_analyzer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class HKStockAnalyzer:
    """
    Enhanced Hong Kong Stock Analyzer with comprehensive portfolio analysis
    """
    
    def __init__(self):
        self.output_dir = "output"
        self.ensure_output_directory()
        
        # Portfolio data with detailed information
        self.portfolio = {
            "00700.HK": {
                "name": "腾讯控股", 
                "name_en": "Tencent Holdings Ltd",
                "shares": 300, 
                "avg_cost": 320.85,
                "sector": "Technology",
                "industry": "Internet Services"
            },
            "00981.HK": {
                "name": "中芯国际", 
                "name_en": "Semiconductor Manufacturing International",
                "shares": 1000, 
                "avg_cost": 47.55,
                "sector": "Technology",
                "industry": "Semiconductors"
            },
            "01810.HK": {
                "name": "小米集团-W", 
                "name_en": "Xiaomi Corporation",
                "shares": 2000, 
                "avg_cost": 47.1071,
                "sector": "Technology",
                "industry": "Consumer Electronics"
            },
            "02628.HK": {
                "name": "中国人寿", 
                "name_en": "China Life Insurance",
                "shares": 2000, 
                "avg_cost": 23.82,
                "sector": "Financials",
                "industry": "Insurance"
            },
            "03690.HK": {
                "name": "美团-W", 
                "name_en": "Meituan",
                "shares": 740, 
                "avg_cost": 123.2508,
                "sector": "Consumer Discretionary",
                "industry": "Food Delivery"
            },
            "09901.HK": {
                "name": "新东方-S", 
                "name_en": "New Oriental Education",
                "shares": 2000, 
                "avg_cost": 44.3241,
                "sector": "Consumer Discretionary",
                "industry": "Education"
            },
            "09988.HK": {
                "name": "阿里巴巴-W", 
                "name_en": "Alibaba Group",
                "shares": 500, 
                "avg_cost": 113.74,
                "sector": "Consumer Discretionary",
                "industry": "E-commerce"
            }
        }
        
        # Current market data (simulated real-time data)
        self.market_data = {
            "00700.HK": {
                "current_price": 325.50,
                "change_percent": "+1.45%",
                "change_amount": "+4.65",
                "volume": "15.2M",
                "market_cap": "3.1T",
                "pe_ratio": "18.5",
                "dividend_yield": "0.8%"
            },
            "00981.HK": {
                "current_price": 18.75,
                "change_percent": "-2.30%",
                "change_amount": "-0.44",
                "volume": "45.8M",
                "market_cap": "298B",
                "pe_ratio": "22.3",
                "dividend_yield": "1.2%"
            },
            "01810.HK": {
                "current_price": 13.85,
                "change_percent": "+0.85%",
                "change_amount": "+0.12",
                "volume": "32.1M",
                "market_cap": "347B",
                "pe_ratio": "16.8",
                "dividend_yield": "0.5%"
            },
            "02628.HK": {
                "current_price": 12.45,
                "change_percent": "-0.95%",
                "change_amount": "-0.12",
                "volume": "8.9M",
                "market_cap": "352B",
                "pe_ratio": "8.9",
                "dividend_yield": "3.2%"
            },
            "03690.HK": {
                "current_price": 128.30,
                "change_percent": "+2.15%",
                "change_amount": "+2.70",
                "volume": "28.5M",
                "market_cap": "756B",
                "pe_ratio": "45.2",
                "dividend_yield": "0.3%"
            },
            "09901.HK": {
                "current_price": 52.80,
                "change_percent": "+3.25%",
                "change_amount": "+1.66",
                "volume": "12.3M",
                "market_cap": "89B",
                "pe_ratio": "28.7",
                "dividend_yield": "0.0%"
            },
            "09988.HK": {
                "current_price": 98.65,
                "change_percent": "-1.25%",
                "change_amount": "-1.25",
                "volume": "55.7M",
                "market_cap": "2.1T",
                "pe_ratio": "12.4",
                "dividend_yield": "0.0%"
            }
        }
        
    def ensure_output_directory(self):
        """Ensure output directory exists"""
        os.makedirs(self.output_dir, exist_ok=True)
        logger.info(f"Output directory: {self.output_dir}")
    
    def analyze_portfolio(self) -> Dict[str, Any]:
        """
        Perform comprehensive portfolio analysis
        """
        logger.info("Starting portfolio analysis...")
        
        analysis_result = {
            "timestamp": datetime.now().isoformat(),
            "market_data": self.market_data,
            "portfolio_analysis": {},
            "summary": {},
            "sector_analysis": {},
            "risk_metrics": {},
            "recommendations": []
        }
        
        total_investment = 0
        total_current_value = 0
        sector_performance = {}
        
        # Analyze each stock
        for symbol, portfolio_info in self.portfolio.items():
            market_info = self.market_data.get(symbol, {})
            
            # Calculate individual stock performance
            shares = portfolio_info['shares']
            avg_cost = portfolio_info['avg_cost']
            current_price = market_info.get('current_price', 0)
            
            investment = shares * avg_cost
            current_value = shares * current_price
            profit_loss = current_value - investment
            profit_loss_percent = (profit_loss / investment) * 100 if investment > 0 else 0
            
            stock_analysis = {
                "company_info": portfolio_info,
                "market_data": market_info,
                "investment_analysis": {
                    "shares": shares,
                    "avg_cost": avg_cost,
                    "current_price": current_price,
                    "total_investment": investment,
                    "current_value": current_value,
                    "profit_loss": profit_loss,
                    "profit_loss_percent": profit_loss_percent,
                    "daily_return": market_info.get('change_percent', '0%')
                },
                "performance_metrics": self.calculate_performance_metrics(portfolio_info, market_info),
                "technical_indicators": self.generate_technical_indicators(symbol, market_info)
            }
            
            analysis_result["portfolio_analysis"][symbol] = stock_analysis
            
            # Update totals
            total_investment += investment
            total_current_value += current_value
            
            # Update sector performance
            sector = portfolio_info['sector']
            if sector not in sector_performance:
                sector_performance[sector] = {"investment": 0, "current_value": 0, "count": 0}
            
            sector_performance[sector]["investment"] += investment
            sector_performance[sector]["current_value"] += current_value
            sector_performance[sector]["count"] += 1
        
        # Calculate summary metrics
        total_profit_loss = total_current_value - total_investment
        total_profit_loss_percent = (total_profit_loss / total_investment) * 100 if total_investment > 0 else 0
        
        analysis_result["summary"] = {
            "total_investment": total_investment,
            "total_current_value": total_current_value,
            "total_profit_loss": total_profit_loss,
            "total_profit_loss_percent": total_profit_loss_percent,
            "portfolio_diversification": len(self.portfolio),
            "market_conditions": self.assess_market_conditions(self.market_data)
        }
        
        # Analyze sector performance
        for sector, data in sector_performance.items():
            sector_pl = data["current_value"] - data["investment"]
            sector_pl_percent = (sector_pl / data["investment"]) * 100 if data["investment"] > 0 else 0
            sector_performance[sector]["profit_loss"] = sector_pl
            sector_performance[sector]["profit_loss_percent"] = sector_pl_percent
            sector_performance[sector]["weight"] = (data["investment"] / total_investment) * 100 if total_investment > 0 else 0
        
        analysis_result["sector_analysis"] = sector_performance
        
        # Calculate risk metrics
        analysis_result["risk_metrics"] = self.calculate_risk_metrics(analysis_result["portfolio_analysis"])
        
        # Generate recommendations
        analysis_result["recommendations"] = self.generate_investment_recommendations(analysis_result)
        
        return analysis_result
    
    def calculate_performance_metrics(self, portfolio_info: Dict, market_info: Dict) -> Dict[str, Any]:
        """
        Calculate detailed performance metrics
        """
        current_price = market_info.get('current_price', 0)
        avg_cost = portfolio_info.get('avg_cost', 0)
        
        return {
            "price_to_cost_ratio": current_price / avg_cost if avg_cost > 0 else 0,
            "volatility_indicator": self.estimate_volatility(market_info),
            "momentum_score": self.calculate_momentum_score(market_info),
            "value_score": self.calculate_value_score(portfolio_info, market_info)
        }
    
    def estimate_volatility(self, market_info: Dict) -> str:
        """
        Estimate volatility based on available data
        """
        volume = market_info.get('volume', '0')
        change_percent = market_info.get('change_percent', '0%')
        
        try:
            volume_num = float(volume.replace('M', '').replace('B', ''))
            change_num = abs(float(change_percent.replace('%', '')))
            
            if volume_num > 50 and change_num > 3:
                return "High"
            elif volume_num > 20 or change_num > 2:
                return "Medium"
            else:
                return "Low"
        except:
            return "Unknown"
    
    def calculate_momentum_score(self, market_info: Dict) -> float:
        """
        Calculate momentum score based on price change and volume
        """
        try:
            change_percent = float(market_info.get('change_percent', '0%').replace('%', ''))
            volume = market_info.get('volume', '0')
            
            # Normalize volume (assuming 'M' represents millions)
            volume_factor = min(float(volume.replace('M', '')) / 30, 1.0) if 'M' in volume else 0.5
            
            momentum = (change_percent / 100) * volume_factor
            return round(momentum, 3)
        except:
            return 0.0
    
    def calculate_value_score(self, portfolio_info: Dict, market_info: Dict) -> float:
        """
        Calculate value score based on fundamental metrics
        """
        try:
            current_price = market_info.get('current_price', 0)
            avg_cost = portfolio_info.get('avg_cost', 0)
            pe_ratio = float(market_info.get('pe_ratio', '0'))
            
            # Value score considers P/E ratio and price relative to cost
            price_ratio = current_price / avg_cost if avg_cost > 0 else 1
            pe_score = max(0, 1 - (pe_ratio / 50))  # Lower P/E is better for value
            
            value_score = (price_ratio * 0.3) + (pe_score * 0.7)
            return round(value_score, 3)
        except:
            return 0.5
    
    def generate_technical_indicators(self, symbol: str, market_info: Dict) -> Dict[str, Any]:
        """
        Generate technical indicators and signals
        """
        try:
            current_price = market_info.get('current_price', 0)
            change_percent = float(market_info.get('change_percent', '0%').replace('%', ''))
            volume = market_info.get('volume', '0')
            
            # Simple technical indicators
            signals = []
            
            if change_percent > 2:
                signals.append("Strong bullish momentum")
            elif change_percent < -2:
                signals.append("Bearish pressure")
            elif change_percent > 0:
                signals.append("Moderate upward trend")
            else:
                signals.append("Consolidation pattern")
            
            # Volume analysis
            if 'M' in volume:
                volume_millions = float(volume.replace('M', ''))
                if volume_millions > 40:
                    signals.append("High volume activity")
                elif volume_millions < 10:
                    signals.append("Low volume - caution")
            
            return {
                "signals": signals,
                "trend": "Upward" if change_percent > 0 else "Downward",
                "strength": "Strong" if abs(change_percent) > 2 else "Moderate",
                "support_resistance": self.estimate_support_resistance(symbol, current_price)
            }
        except:
            return {"signals": ["Insufficient data"], "trend": "Unknown", "strength": "Unknown"}
    
    def estimate_support_resistance(self, symbol: str, current_price: float) -> Dict[str, float]:
        """
        Estimate support and resistance levels (simplified)
        """
        # Simple estimation based on current price
        return {
            "support": round(current_price * 0.95, 2),
            "resistance": round(current_price * 1.05, 2)
        }
    
    def calculate_risk_metrics(self, portfolio_analysis: Dict) -> Dict[str, Any]:
        """
        Calculate portfolio risk metrics
        """
        returns = []
        total_investment = 0
        total_value = 0
        
        for symbol, analysis in portfolio_analysis.items():
            inv_analysis = analysis["investment_analysis"]
            returns.append(inv_analysis["profit_loss_percent"])
            total_investment += inv_analysis["total_investment"]
            total_value += inv_analysis["current_value"]
        
        # Calculate basic risk metrics
        if returns:
            avg_return = sum(returns) / len(returns)
            variance = sum((r - avg_return) ** 2 for r in returns) / len(returns)
            volatility = variance ** 0.5
            
            # Calculate concentration risk
            concentration = max(
                analysis["investment_analysis"]["total_investment"] / total_investment 
                for analysis in portfolio_analysis.values()
            ) if total_investment > 0 else 0
            
            return {
                "volatility": round(volatility, 4),
                "concentration_risk": round(concentration * 100, 2),
                "diversification_score": round(len(portfolio_analysis) / 7 * 100, 1),
                "risk_level": self.assess_risk_level(volatility, concentration)
            }
        
        return {}
    
    def assess_risk_level(self, volatility: float, concentration: float) -> str:
        """
        Assess overall portfolio risk level
        """
        if volatility > 15 or concentration > 0.4:
            return "High"
        elif volatility > 8 or concentration > 0.25:
            return "Medium"
        else:
            return "Low"
    
    def assess_market_conditions(self, market_data: Dict) -> str:
        """
        Assess overall market conditions
        """
        try:
            changes = []
            for symbol, data in market_data.items():
                change_str = data.get('change_percent', '0%')
                change = float(change_str.replace('%', ''))
                changes.append(change)
            
            avg_change = sum(changes) / len(changes)
            
            if avg_change > 1:
                return "Bullish market sentiment"
            elif avg_change < -1:
                return "Bearish market sentiment"
            else:
                return "Mixed/Sideways market"
        except:
            return "Market conditions unclear"
    
    def generate_investment_recommendations(self, analysis: Dict) -> List[str]:
        """
        Generate personalized investment recommendations
        """
        recommendations = []
        
        # Portfolio level recommendations
        total_pl_percent = analysis["summary"]["total_profit_loss_percent"]
        risk_level = analysis["risk_metrics"].get("risk_level", "Unknown")
        
        if total_pl_percent > 10:
            recommendations.append("📈 整体投资组合表现优异，建议考虑部分获利了结")
        elif total_pl_percent < -5:
            recommendations.append("📉 投资组合表现不佳，建议重新评估投资策略")
        
        if risk_level == "High":
            recommendations.append("⚠️ 投资组合风险较高，建议考虑分散投资")
        
        # Individual stock recommendations
        for symbol, stock_analysis in analysis["portfolio_analysis"].items():
            inv_analysis = stock_analysis["investment_analysis"]
            perf_metrics = stock_analysis["performance_metrics"]
            tech_indicators = stock_analysis["technical_indicators"]
            
            name = stock_analysis["company_info"]["name"]
            pl_percent = inv_analysis["profit_loss_percent"]
            
            if pl_percent > 15:
                recommendations.append(f"💰 {name}: 盈利{pl_percent:.1f}%，考虑部分获利")
            elif pl_percent < -10:
                recommendations.append(f"🔻 {name}: 亏损{abs(pl_percent):.1f}%，评估止损策略")
            
            # Technical analysis recommendations
            if "Strong bullish momentum" in tech_indicators["signals"]:
                recommendations.append(f"📈 {name}: 技术面显示强劲上涨动力")
            elif "Bearish pressure" in tech_indicators["signals"]:
                recommendations.append(f"📉 {name}: 技术面显示下跌压力")
        
        # Sector recommendations
        sector_analysis = analysis["sector_analysis"]
        best_sector = max(sector_analysis.items(), key=lambda x: x[1]["profit_loss_percent"])
        worst_sector = min(sector_analysis.items(), key=lambda x: x[1]["profit_loss_percent"])
        
        if best_sector[1]["profit_loss_percent"] > 5:
            recommendations.append(f"🏆 {best_sector[0]}板块表现最佳，可考虑增加配置")
        
        if worst_sector[1]["profit_loss_percent"] < -3:
            recommendations.append(f"📉 {worst_sector[0]}板块表现较弱，关注基本面变化")
        
        return recommendations
    
    def save_analysis_report(self, analysis: Dict[str, Any]):
        """
        Save comprehensive analysis report
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save JSON data
        json_filename = f"hk_stock_analysis_{timestamp}.json"
        json_path = os.path.join(self.output_dir, json_filename)
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        
        # Save formatted report
        report_filename = f"hk_stock_report_{timestamp}.txt"
        report_path = os.path.join(self.output_dir, report_filename)
        
        report = self.generate_formatted_report(analysis)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"Analysis saved to:")
        logger.info(f"  JSON data: {json_path}")
        logger.info(f"  Report: {report_path}")
        
        return json_path, report_path
    
    def generate_formatted_report(self, analysis: Dict[str, Any]) -> str:
        """
        Generate comprehensive formatted report
        """
        report = f"""
{'='*100}
香港股票投资组合全面分析报告
Hong Kong Stock Portfolio Comprehensive Analysis Report
{'='*100}

生成时间/Generated: {analysis['timestamp']}

{'='*100}
📊 市场概览 / Market Overview
{'='*100}

市场状况: {analysis['summary']['market_conditions']}
投资组合分散度: {analysis['summary']['portfolio_diversification']} 只股票
风险等级: {analysis['risk_metrics'].get('risk_level', 'Unknown')}

{'='*100}
💰 投资组合总览 / Portfolio Summary
{'='*100}

总投资成本: ¥{analysis['summary']['total_investment']:,.2f}
当前总价值: ¥{analysis['summary']['total_current_value']:,.2f}
总盈亏金额: ¥{analysis['summary']['total_profit_loss']:,.2f}
总收益率: {analysis['summary']['total_profit_loss_percent']:+.2f}%

{'='*100}
📈 个股详细分析 / Individual Stock Analysis
{'='*100}
"""
        
        for symbol, stock_analysis in analysis['portfolio_analysis'].items():
            company_info = stock_analysis['company_info']
            market_data = stock_analysis['market_data']
            inv_analysis = stock_analysis['investment_analysis']
            perf_metrics = stock_analysis['performance_metrics']
            tech_indicators = stock_analysis['technical_indicators']
            
            report += f"""
{company_info['name']} ({symbol}) - {company_info['name_en']}
{'-'*80}

📋 基本信息 / Basic Information:
  行业: {company_info['industry']} | 板块: {company_info['sector']}
  市值: {market_data.get('market_cap', 'N/A')} | 市盈率: {market_data.get('pe_ratio', 'N/A')}

💵 价格信息 / Price Information:
  当前价格: ¥{market_data.get('current_price', 0):.2f}
  日涨跌: {market_data.get('change_percent', '0%')} ({market_data.get('change_amount', '0')})
  成交量: {market_data.get('volume', 'N/A')}

📊 投资分析 / Investment Analysis:
  持股数量: {inv_analysis['shares']} 股
  平均成本: ¥{inv_analysis['avg_cost']:.4f}
  投资成本: ¥{inv_analysis['total_investment']:,.2f}
  当前价值: ¥{inv_analysis['current_value']:,.2f}
  盈亏金额: ¥{inv_analysis['profit_loss']:,.2f}
  盈亏比例: {inv_analysis['profit_loss_percent']:+.2f}%

📈 技术指标 / Technical Indicators:
  趋势: {tech_indicators['trend']} | 强度: {tech_indicators['strength']}
  支撑位: ¥{tech_indicators['support_resistance']['support']:.2f}
  阻力位: ¥{tech_indicators['support_resistance']['resistance']:.2f}
  信号: {', '.join(tech_indicators['signals'])}

📊 性能指标 / Performance Metrics:
  价格成本比: {perf_metrics['price_to_cost_ratio']:.2f}
  波动性: {perf_metrics['volatility_indicator']}
  动量分数: {perf_metrics['momentum_score']:.3f}
  价值分数: {perf_metrics['value_score']:.3f}

"""
        
        # Sector analysis
        report += f"""
{'='*100}
🏢 板块分析 / Sector Analysis
{'='*100}

"""
        for sector, data in analysis['sector_analysis'].items():
            report += f"""
{sector}:
  股票数量: {data['count']} 只
  投资权重: {data['weight']:.1f}%
  投资成本: ¥{data['investment']:,.2f}
  当前价值: ¥{data['current_value']:,.2f}
  盈亏金额: ¥{data['profit_loss']:,.2f}
  盈亏比例: {data['profit_loss_percent']:+.2f}%

"""
        
        # Risk metrics
        risk_metrics = analysis['risk_metrics']
        report += f"""
{'='*100}
⚠️ 风险分析 / Risk Analysis
{'='*100}

投资组合波动性: {risk_metrics.get('volatility', 0):.2%}
集中度风险: {risk_metrics.get('concentration_risk', 0):.1f}%
分散化评分: {risk_metrics.get('diversification_score', 0):.1f}/100
整体风险等级: {risk_metrics.get('risk_level', 'Unknown')}

{'='*100}
💡 投资建议 / Investment Recommendations
{'='*100}

"""
        
        for i, recommendation in enumerate(analysis['recommendations'], 1):
            report += f"{i}. {recommendation}\n"
        
        report += f"""
{'='*100}
📋 免责声明 / Disclaimer
{'='*100}

⚠️ 重要提示:
- 本报告仅供参考，不构成投资建议
- 股票投资有风险，入市需谨慎
- 市场有风险，投资需谨慎
- 数据来源于公开信息，请以官方数据为准
- 过往表现不代表未来收益
- 投资决策应该基于个人风险承受能力和投资目标

{'='*100}
报告结束 / End of Report
{'='*100}
"""
        
        return report
    
    def display_summary(self, analysis: Dict[str, Any]):
        """
        Display summary information to console
        """
        print(f"\n{'='*80}")
        print("🇭🇰 香港股票投资组合分析报告")
        print("🇭🇰 Hong Kong Stock Portfolio Analysis")
        print(f"{'='*80}")
        
        summary = analysis['summary']
        risk_metrics = analysis['risk_metrics']
        
        print(f"\n📊 投资组合总览:")
        print(f"   总投资成本: ¥{summary['total_investment']:,.2f}")
        print(f"   当前总价值: ¥{summary['total_current_value']:,.2f}")
        print(f"   总盈亏金额: ¥{summary['total_profit_loss']:,.2f}")
        print(f"   总收益率: {summary['total_profit_loss_percent']:+.2f}%")
        print(f"   市场状况: {summary['market_conditions']}")
        print(f"   风险等级: {risk_metrics.get('risk_level', 'Unknown')}")
        
        print(f"\n🏆 表现最佳个股:")
        best_performer = max(
            analysis['portfolio_analysis'].items(),
            key=lambda x: x[1]['investment_analysis']['profit_loss_percent']
        )
        best_symbol = best_performer[0]
        best_data = best_performer[1]['investment_analysis']
        best_name = analysis['portfolio_analysis'][best_symbol]['company_info']['name']
        print(f"   {best_name} ({best_symbol}): {best_data['profit_loss_percent']:+.2f}%")
        
        print(f"\n📉 表现最差个股:")
        worst_performer = min(
            analysis['portfolio_analysis'].items(),
            key=lambda x: x[1]['investment_analysis']['profit_loss_percent']
        )
        worst_symbol = worst_performer[0]
        worst_data = worst_performer[1]['investment_analysis']
        worst_name = analysis['portfolio_analysis'][worst_symbol]['company_info']['name']
        print(f"   {worst_name} ({worst_symbol}): {worst_data['profit_loss_percent']:+.2f}%")
        
        print(f"\n📈 板块表现:")
        for sector, data in analysis['sector_analysis'].items():
            print(f"   {sector}: {data['profit_loss_percent']:+.2f}% (权重: {data['weight']:.1f}%)")
        
        print(f"\n💡 主要建议:")
        for i, rec in enumerate(analysis['recommendations'][:3], 1):
            print(f"   {i}. {rec}")
        
        print(f"\n{'='*80}")
        print("详细报告已保存到 output/ 目录")
        print("Detailed report saved to output/ directory")
        print(f"{'='*80}")

def main():
    """
    Main execution function
    """
    print("🚀 启动香港股票投资组合分析器...")
    print("🚀 Starting Hong Kong Stock Portfolio Analyzer...")
    
    analyzer = HKStockAnalyzer()
    
    try:
        # Perform comprehensive analysis
        analysis = analyzer.analyze_portfolio()
        
        # Save analysis report
        json_path, report_path = analyzer.save_analysis_report(analysis)
        
        # Display summary
        analyzer.display_summary(analysis)
        
        print(f"\n✅ 分析完成！")
        print(f"✅ Analysis completed!")
        print(f"📄 JSON报告: {json_path}")
        print(f"📄 详细报告: {report_path}")
        
        return analysis
        
    except Exception as e:
        logger.error(f"分析过程中发生错误: {str(e)}")
        print(f"❌ 分析失败: {str(e)}")
        return None

if __name__ == "__main__":
    main()