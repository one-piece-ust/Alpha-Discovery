"""
分析和报告生成模块
"""

import pandas as pd
import numpy as np
from typing import Dict, Any
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from loguru import logger


class PerformanceAnalyzer:
    """
    性能分析器
    
    计算各类性能指标
    """
    
    @staticmethod
    def calculate_metrics(returns: pd.Series, risk_free_rate: float = 0.03) -> Dict[str, float]:
        """
        计算性能指标
        
        Args:
            returns: 收益率序列
            risk_free_rate: 无风险利率
            
        Returns:
            Dict: 性能指标
        """
        cumulative_returns = (1 + returns).cumprod()
        
        metrics = {
            'total_return': cumulative_returns.iloc[-1] - 1,
            'annual_return': PerformanceAnalyzer._annualized_return(returns),
            'annual_volatility': PerformanceAnalyzer._annualized_volatility(returns),
            'sharpe_ratio': PerformanceAnalyzer._sharpe_ratio(returns, risk_free_rate),
            'max_drawdown': PerformanceAnalyzer._max_drawdown(cumulative_returns),
            'calmar_ratio': PerformanceAnalyzer._calmar_ratio(returns),
            'sortino_ratio': PerformanceAnalyzer._sortino_ratio(returns, risk_free_rate),
            'win_rate': (returns > 0).sum() / len(returns),
            'profit_loss_ratio': PerformanceAnalyzer._profit_loss_ratio(returns),
        }
        
        return metrics
    
    @staticmethod
    def _annualized_return(returns: pd.Series, periods_per_year: int = 252) -> float:
        """年化收益率"""
        cumulative = (1 + returns).prod()
        n_periods = len(returns)
        return cumulative ** (periods_per_year / n_periods) - 1
    
    @staticmethod
    def _annualized_volatility(returns: pd.Series, periods_per_year: int = 252) -> float:
        """年化波动率"""
        return returns.std() * np.sqrt(periods_per_year)
    
    @staticmethod
    def _sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.03, periods_per_year: int = 252) -> float:
        """Sharpe比率"""
        excess_returns = returns - risk_free_rate / periods_per_year
        return excess_returns.mean() / returns.std() * np.sqrt(periods_per_year) if returns.std() != 0 else 0
    
    @staticmethod
    def _max_drawdown(cumulative_returns: pd.Series) -> float:
        """最大回撤"""
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max
        return abs(drawdown.min())
    
    @staticmethod
    def _calmar_ratio(returns: pd.Series) -> float:
        """Calmar比率"""
        annual_return = PerformanceAnalyzer._annualized_return(returns)
        cumulative = (1 + returns).cumprod()
        max_dd = PerformanceAnalyzer._max_drawdown(cumulative)
        return annual_return / max_dd if max_dd != 0 else 0
    
    @staticmethod
    def _sortino_ratio(returns: pd.Series, risk_free_rate: float = 0.03, periods_per_year: int = 252) -> float:
        """Sortino比率"""
        excess_returns = returns - risk_free_rate / periods_per_year
        downside_returns = returns[returns < 0]
        downside_std = downside_returns.std() * np.sqrt(periods_per_year)
        return excess_returns.mean() * periods_per_year / downside_std if downside_std != 0 and len(downside_returns) > 0 else 0
    
    @staticmethod
    def _profit_loss_ratio(returns: pd.Series) -> float:
        """盈亏比"""
        profits = returns[returns > 0]
        losses = returns[returns < 0]
        avg_profit = profits.mean() if len(profits) > 0 else 0
        avg_loss = abs(losses.mean()) if len(losses) > 0 else 0
        return avg_profit / avg_loss if avg_loss != 0 else 0


class ReportGenerator:
    """
    报告生成器
    
    生成HTML格式的回测报告
    """
    
    def __init__(self, results: Dict[str, Any], factor_name: str):
        """
        初始化报告生成器
        
        Args:
            results: 回测结果字典
            factor_name: 因子名称
        """
        self.results = results
        self.factor_name = factor_name
        
    def generate_html_report(self, save_path: str = None):
        """
        生成HTML报告
        
        Args:
            save_path: 保存路径
        """
        if save_path is None:
            save_path = f"results/reports/{self.factor_name}_report.html"
        
        # 确保目录存在
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        
        html_content = self._build_html()
        
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"HTML report generated: {save_path}")
    
    def _build_html(self) -> str:
        """构建HTML内容"""
        html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.factor_name} 因子回测报告</title>
    <style>
        body {{
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            margin: 0;
            font-size: 32px;
        }}
        .section {{
            background: white;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .section h2 {{
            color: #667eea;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }}
        .metric-card {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #667eea;
        }}
        .metric-label {{
            font-size: 14px;
            color: #666;
            margin-bottom: 5px;
        }}
        .metric-value {{
            font-size: 24px;
            font-weight: bold;
            color: #333;
        }}
        .positive {{ color: #28a745; }}
        .negative {{ color: #dc3545; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #667eea;
            color: white;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .footer {{
            text-align: center;
            color: #666;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 {self.factor_name} 因子回测报告</h1>
        <p>生成时间: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    {self._build_summary_section()}
    {self._build_ic_section()}
    {self._build_returns_section()}
    
    <div class="footer">
        <p>Powered by Qlib Alpha Framework | © 2026</p>
    </div>
</body>
</html>
"""
        return html
    
    def _build_summary_section(self) -> str:
        """构建摘要部分"""
        ic_mean = self.results.get('ic_mean', 0)
        icir = self.results.get('icir', 0)
        annual_return = self.results.get('annual_return', 0)
        sharpe = self.results.get('sharpe_ratio', 0)
        max_dd = self.results.get('max_drawdown', 0)
        win_rate = self.results.get('ic_positive_rate', 0)
        
        ic_class = 'positive' if ic_mean > 0 else 'negative'
        ret_class = 'positive' if annual_return > 0 else 'negative'
        
        return f"""
    <div class="section">
        <h2>📈 核心指标摘要</h2>
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-label">IC 均值</div>
                <div class="metric-value {ic_class}">{ic_mean:.4f}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">ICIR</div>
                <div class="metric-value">{icir:.4f}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">年化收益率</div>
                <div class="metric-value {ret_class}">{annual_return:.2%}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Sharpe 比率</div>
                <div class="metric-value">{sharpe:.4f}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">最大回撤</div>
                <div class="metric-value negative">{max_dd:.2%}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">IC 胜率</div>
                <div class="metric-value">{win_rate:.2%}</div>
            </div>
        </div>
    </div>
"""
    
    def _build_ic_section(self) -> str:
        """构建IC分析部分"""
        ic_series = self.results.get('ic_series')
        if ic_series is None:
            return ""
        
        # IC 统计
        ic_stats = {
            'Mean': ic_series.mean(),
            'Std': ic_series.std(),
            'Min': ic_series.min(),
            'Max': ic_series.max(),
            'Positive %': (ic_series > 0).sum() / len(ic_series) * 100
        }
        
        stats_rows = "".join([
            f"<tr><td>{k}</td><td>{v:.4f}</td></tr>" if k != 'Positive %' 
            else f"<tr><td>{k}</td><td>{v:.2f}%</td></tr>"
            for k, v in ic_stats.items()
        ])
        
        return f"""
    <div class="section">
        <h2>📊 IC 分析</h2>
        <table>
            <thead>
                <tr>
                    <th>统计量</th>
                    <th>数值</th>
                </tr>
            </thead>
            <tbody>
                {stats_rows}
            </tbody>
        </table>
    </div>
"""
    
    def _build_returns_section(self) -> str:
        """构建收益分析部分"""
        return f"""
    <div class="section">
        <h2>💰 收益分析</h2>
        <p>多空组合年化收益: <strong class="positive">{self.results.get('annual_return', 0):.2%}</strong></p>
        <p>年化波动率: <strong>{self.results.get('annual_volatility', 0):.2%}</strong></p>
        <p>Sharpe 比率: <strong>{self.results.get('sharpe_ratio', 0):.4f}</strong></p>
        <p>最大回撤: <strong class="negative">{self.results.get('max_drawdown', 0):.2%}</strong></p>
    </div>
"""
    
    def generate_multi_factor_report(self, save_path: str = None):
        """生成多因子报告"""
        # TODO: 实现多因子报告
        pass
