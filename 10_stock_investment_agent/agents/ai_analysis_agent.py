"""
AI分析Agent
负责智能分析股票、生成投资建议、情感分析等功能
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from loguru import logger

from utils.logger import get_logger
from utils.date_utils import DateUtils


class AIAnalysisAgent:
    """AI分析Agent"""
    
    def __init__(self, api_keys: Dict, settings: Dict):
        self.logger = get_logger("ai_analysis")
        self.api_keys = api_keys
        self.settings = settings
        self.date_utils = DateUtils()
        
    def analyze_stock(self, symbol: str, market_type: str) -> Dict:
        """分析个股"""
        try:
            self.logger.info(f"开始分析个股: {symbol} ({market_type})")
            
            # 获取价格数据
            price_data = self._get_price_data(symbol, market_type)
            
            # 基本面分析
            fundamental_analysis = self._analyze_fundamental(symbol, market_type)
            
            # 技术面分析
            technical_analysis = self._analyze_technical(symbol, market_type)
            
            # 新闻情感分析
            news_data = self._get_news_data(symbol, market_type)
            sentiment_analysis = self._analyze_sentiment(news_data)
            
            # 生成投资建议
            recommendation = self._generate_recommendation(
                price_data, fundamental_analysis, technical_analysis, sentiment_analysis
            )
            
            result = {
                'success': True,
                'symbol': symbol,
                'market_type': market_type,
                'analysis': {
                    'fundamental': fundamental_analysis,
                    'technical': technical_analysis,
                    'sentiment': sentiment_analysis,
                    'recommendation': recommendation
                },
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.info(f"个股分析完成: {symbol}")
            return result
            
        except Exception as e:
            self.logger.error(f"分析个股失败 {symbol}: {e}")
            return {'success': False, 'error': str(e)}
    
    def run_analysis(self) -> Dict:
        """运行完整分析"""
        try:
            self.logger.info("开始运行完整AI分析...")
            
            # 加载持仓数据
            portfolio_data = self._load_portfolio_data()
            positions = portfolio_data.get('positions', [])
            
            if not positions:
                return {
                    'success': True,
                    'message': '没有持仓数据需要分析',
                    'analysis_results': [],
                    'timestamp': datetime.now().isoformat()
                }
            
            analysis_results = []
            alerts = []
            
            # 分析每个持仓
            for position in positions:
                symbol = position.get('symbol')
                market_type = position.get('market_type')
                
                if symbol and market_type:
                    result = self.analyze_stock(symbol, market_type)
                    if result.get('success'):
                        analysis_results.append(result)
                        
                        # 检查是否需要预警
                        alert = self._check_alert(position, result)
                        if alert:
                            alerts.append(alert)
            
            # 生成投资组合建议
            portfolio_recommendation = self._generate_portfolio_recommendation(analysis_results)
            
            # 保存分析结果
            self._save_analysis_results(analysis_results)
            
            return {
                'success': True,
                'analysis_results': analysis_results,
                'alerts': alerts,
                'portfolio_recommendation': portfolio_recommendation,
                'analyzed_positions': len(analysis_results),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"运行完整分析失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def _get_price_data(self, symbol: str, market_type: str) -> Dict:
        """获取价格数据"""
        try:
            # 这里应该调用数据抓取Agent
            # 现在返回模拟数据
            return {
                'current_price': 150.25,
                'change_percent': 2.5,
                'volume': 1000000,
                'high': 152.50,
                'low': 148.30,
                'open': 149.00
            }
        except Exception as e:
            self.logger.error(f"获取价格数据失败 {symbol}: {e}")
            return {}
    
    def _get_news_data(self, symbol: str, market_type: str) -> List[Dict]:
        """获取新闻数据"""
        try:
            # 这里应该调用新闻API
            # 现在返回模拟数据
            return [
                {
                    'title': f'{symbol}发布季度财报',
                    'summary': '公司营收超出预期',
                    'sentiment': 'positive',
                    'publish_time': '2024-01-15T10:00:00Z'
                },
                {
                    'title': f'{symbol}获得机构增持',
                    'summary': '知名基金增持股份',
                    'sentiment': 'positive',
                    'publish_time': '2024-01-14T15:30:00Z'
                }
            ]
        except Exception as e:
            self.logger.error(f"获取新闻数据失败 {symbol}: {e}")
            return []
    
    def _analyze_fundamental(self, symbol: str, market_type: str) -> Dict:
        """分析基本面"""
        try:
            # 这里应该调用财务数据API
            # 现在返回模拟数据
            return {
                'pe_ratio': 25.5,
                'pb_ratio': 3.2,
                'roe': 15.8,
                'debt_ratio': 35.2,
                'revenue_growth': 12.5,
                'profit_growth': 18.3,
                'analysis': '公司基本面良好，盈利能力稳定',
                'score': 75
            }
        except Exception as e:
            self.logger.error(f"基本面分析失败 {symbol}: {e}")
            return {'error': str(e)}
    
    def _analyze_technical(self, symbol: str, market_type: str) -> Dict:
        """分析技术面"""
        try:
            # 这里应该调用技术分析API
            # 现在返回模拟数据
            return {
                'ma5': 150.25,
                'ma10': 148.50,
                'ma20': 145.30,
                'rsi': 65.5,
                'macd': 2.35,
                'trend': 'uptrend',
                'support': 142.50,
                'resistance': 155.00,
                'analysis': '技术面显示上升趋势，但需要注意阻力位',
                'score': 70
            }
        except Exception as e:
            self.logger.error(f"技术面分析失败 {symbol}: {e}")
            return {'error': str(e)}
    
    def _analyze_sentiment(self, news_data: List[Dict]) -> Dict:
        """分析新闻情感"""
        try:
            if not news_data:
                return {
                    'sentiment': 'neutral',
                    'score': 50,
                    'analysis': '没有相关新闻数据',
                    'news_count': 0
                }
            
            # 简单的情感分析
            positive_count = 0
            negative_count = 0
            neutral_count = 0
            
            for news in news_data:
                sentiment = news.get('sentiment', 'neutral')
                if sentiment == 'positive':
                    positive_count += 1
                elif sentiment == 'negative':
                    negative_count += 1
                else:
                    neutral_count += 1
            
            total_count = len(news_data)
            sentiment_score = (positive_count / total_count) * 100 if total_count > 0 else 50
            
            if sentiment_score > 60:
                sentiment = 'positive'
            elif sentiment_score < 40:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
            
            return {
                'sentiment': sentiment,
                'score': sentiment_score,
                'positive_count': positive_count,
                'negative_count': negative_count,
                'neutral_count': neutral_count,
                'analysis': f'基于{total_count}条新闻分析，市场情绪为{sentiment}',
                'news_count': total_count
            }
            
        except Exception as e:
            self.logger.error(f"情感分析失败: {e}")
            return {'error': str(e)}
    
    def _generate_recommendation(self, price_data: Dict, fundamental: Dict, technical: Dict, sentiment: Dict) -> Dict:
        """生成投资建议"""
        try:
            # 综合评分
            fundamental_score = fundamental.get('score', 50)
            technical_score = technical.get('score', 50)
            sentiment_score = sentiment.get('score', 50)
            
            total_score = (fundamental_score * 0.4 + technical_score * 0.4 + sentiment_score * 0.2)
            
            # 生成建议
            if total_score >= 80:
                recommendation = 'strong_buy'
                action = '强烈建议买入'
            elif total_score >= 65:
                recommendation = 'buy'
                action = '建议买入'
            elif total_score >= 35:
                recommendation = 'hold'
                action = '建议持有'
            elif total_score >= 20:
                recommendation = 'sell'
                action = '建议卖出'
            else:
                recommendation = 'strong_sell'
                action = '强烈建议卖出'
            
            return {
                'recommendation': recommendation,
                'action': action,
                'total_score': round(total_score, 2),
                'fundamental_score': fundamental_score,
                'technical_score': technical_score,
                'sentiment_score': sentiment_score,
                'confidence': min(total_score / 100 * 100, 100),
                'reasoning': f'基于基本面({fundamental_score}分)、技术面({technical_score}分)和市场情绪({sentiment_score}分)的综合分析'
            }
            
        except Exception as e:
            self.logger.error(f"生成投资建议失败: {e}")
            return {'error': str(e)}
    
    def _check_alert(self, position: Dict, analysis: Dict) -> Optional[Dict]:
        """检查是否需要预警"""
        try:
            alerts = []
            
            # 检查价格变动
            current_price = position.get('current_price', 0)
            avg_cost = position.get('avg_cost', 0)
            
            if current_price > 0 and avg_cost > 0:
                change_percent = ((current_price - avg_cost) / avg_cost) * 100
                
                # 价格变动超过5%预警
                if abs(change_percent) > 5:
                    alerts.append({
                        'type': 'price_change',
                        'severity': 'medium' if abs(change_percent) < 10 else 'high',
                        'message': f'价格变动{change_percent:.2f}%，当前价格{current_price:.2f}',
                        'threshold': 5.0
                    })
            
            # 检查投资建议
            recommendation = analysis.get('analysis', {}).get('recommendation', {})
            if recommendation.get('recommendation') in ['strong_sell', 'sell']:
                alerts.append({
                    'type': 'recommendation',
                    'severity': 'high',
                    'message': f'AI建议{recommendation.get("action", "")}，建议关注',
                    'recommendation': recommendation.get('recommendation')
                })
            
            # 检查风险评分
            if recommendation.get('total_score', 50) < 30:
                alerts.append({
                    'type': 'risk_alert',
                    'severity': 'high',
                    'message': f'综合评分较低({recommendation.get("total_score", 0):.2f}分)，存在较大风险',
                    'score': recommendation.get('total_score', 0)
                })
            
            if alerts:
                return {
                    'symbol': position.get('symbol'),
                    'market_type': position.get('market_type'),
                    'alerts': alerts,
                    'timestamp': datetime.now().isoformat()
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"检查预警失败: {e}")
            return None
    
    def _generate_portfolio_recommendation(self, analysis_results: List[Dict]) -> Dict:
        """生成投资组合建议"""
        try:
            if not analysis_results:
                return {
                    'overall_recommendation': 'hold',
                    'risk_level': 'medium',
                    'suggestions': ['建议添加持仓以分散风险']
                }
            
            # 分析整体风险
            buy_count = 0
            sell_count = 0
            hold_count = 0
            avg_score = 0
            
            for result in analysis_results:
                recommendation = result.get('analysis', {}).get('recommendation', {})
                rec_type = recommendation.get('recommendation', 'hold')
                score = recommendation.get('total_score', 50)
                
                if rec_type in ['strong_buy', 'buy']:
                    buy_count += 1
                elif rec_type in ['strong_sell', 'sell']:
                    sell_count += 1
                else:
                    hold_count += 1
                
                avg_score += score
            
            avg_score /= len(analysis_results)
            
            # 生成整体建议
            if avg_score >= 70:
                overall_rec = 'aggressive_growth'
                risk_level = 'high'
                suggestions = ['建议适度增加仓位，关注成长股']
            elif avg_score >= 50:
                overall_rec = 'balanced_growth'
                risk_level = 'medium'
                suggestions = ['建议保持当前仓位，平衡配置']
            else:
                overall_rec = 'conservative'
                risk_level = 'low'
                suggestions = ['建议降低仓位，增加防御性配置']
            
            return {
                'overall_recommendation': overall_rec,
                'risk_level': risk_level,
                'average_score': round(avg_score, 2),
                'buy_recommendations': buy_count,
                'sell_recommendations': sell_count,
                'hold_recommendations': hold_count,
                'suggestions': suggestions
            }
            
        except Exception as e:
            self.logger.error(f"生成投资组合建议失败: {e}")
            return {'error': str(e)}
    
    def _load_portfolio_data(self) -> Dict:
        """加载投资组合数据"""
        try:
            with open('data/portfolio_data.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {'positions': [], 'last_update': None}
        except Exception as e:
            self.logger.error(f"加载投资组合数据失败: {e}")
            return {'positions': [], 'last_update': None}
    
    def _save_analysis_results(self, results: List[Dict]):
        """保存分析结果"""
        try:
            analysis_data = {
                'results': results,
                'timestamp': datetime.now().isoformat()
            }
            
            with open('data/analysis_cache.json', 'w', encoding='utf-8') as f:
                json.dump(analysis_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"保存分析结果失败: {e}")
    
    def get_status(self) -> Dict:
        """获取Agent状态"""
        return {
            'status': 'active',
            'last_analysis': None,
            'analysis_count': 0
        }
    
    def start(self):
        """启动Agent"""
        self.logger.info("AI分析Agent启动")
    
    def stop(self):
        """停止Agent"""
        self.logger.info("AI分析Agent停止")