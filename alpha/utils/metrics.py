"""
评价指标计算工具
"""

import pandas as pd
import numpy as np
from typing import Union
from scipy import stats


class MetricsCalculator:
    """指标计算器"""
    
    @staticmethod
    def ic(factor: pd.Series, returns: pd.Series, method: str = 'pearson') -> float:
        """
        计算 IC (Information Coefficient)
        
        Args:
            factor: 因子值
            returns: 收益率
            method: 相关系数方法 ('pearson' or 'spearman')
            
        Returns:
            float: IC 值
        """
        if method == 'pearson':
            return factor.corr(returns, method='pearson')
        elif method == 'spearman':
            return factor.corr(returns, method='spearman')
        else:
            raise ValueError(f"Unknown method: {method}")
    
    @staticmethod
    def icir(ic_series: pd.Series) -> float:
        """
        计算 ICIR (IC Information Ratio)
        
        Args:
            ic_series: IC 时间序列
            
        Returns:
            float: ICIR 值
        """
        ic_mean = ic_series.mean()
        ic_std = ic_series.std()
        return ic_mean / ic_std if ic_std != 0 else 0
    
    @staticmethod
    def sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.03, 
                     periods_per_year: int = 252) -> float:
        """
        计算 Sharpe 比率
        
        Args:
            returns: 收益率序列
            risk_free_rate: 无风险利率
            periods_per_year: 每年的期数
            
        Returns:
            float: Sharpe 比率
        """
        excess_returns = returns - risk_free_rate / periods_per_year
        return excess_returns.mean() / returns.std() * np.sqrt(periods_per_year) if returns.std() != 0 else 0
    
    @staticmethod
    def max_drawdown(cumulative_returns: Union[pd.Series, np.ndarray]) -> float:
        """
        计算最大回撤
        
        Args:
            cumulative_returns: 累计收益序列
            
        Returns:
            float: 最大回撤
        """
        if isinstance(cumulative_returns, np.ndarray):
            cumulative_returns = pd.Series(cumulative_returns)
        
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max
        return abs(drawdown.min())
    
    @staticmethod
    def calmar_ratio(returns: pd.Series, periods_per_year: int = 252) -> float:
        """
        计算 Calmar 比率
        
        Args:
            returns: 收益率序列
            periods_per_year: 每年的期数
            
        Returns:
            float: Calmar 比率
        """
        annual_return = (1 + returns).prod() ** (periods_per_year / len(returns)) - 1
        cumulative = (1 + returns).cumprod()
        max_dd = MetricsCalculator.max_drawdown(cumulative)
        return annual_return / max_dd if max_dd != 0 else 0
    
    @staticmethod
    def win_rate(returns: pd.Series) -> float:
        """
        计算胜率
        
        Args:
            returns: 收益率序列
            
        Returns:
            float: 胜率
        """
        return (returns > 0).sum() / len(returns)
    
    @staticmethod
    def profit_loss_ratio(returns: pd.Series) -> float:
        """
        计算盈亏比
        
        Args:
            returns: 收益率序列
            
        Returns:
            float: 盈亏比
        """
        profits = returns[returns > 0]
        losses = returns[returns < 0]
        
        avg_profit = profits.mean() if len(profits) > 0 else 0
        avg_loss = abs(losses.mean()) if len(losses) > 0 else 0
        
        return avg_profit / avg_loss if avg_loss != 0 else 0
    
    @staticmethod
    def information_ratio(returns: pd.Series, benchmark_returns: pd.Series, 
                         periods_per_year: int = 252) -> float:
        """
        计算信息比率
        
        Args:
            returns: 策略收益率
            benchmark_returns: 基准收益率
            periods_per_year: 每年的期数
            
        Returns:
            float: 信息比率
        """
        excess_returns = returns - benchmark_returns
        tracking_error = excess_returns.std() * np.sqrt(periods_per_year)
        return excess_returns.mean() * periods_per_year / tracking_error if tracking_error != 0 else 0
    
    @staticmethod
    def sortino_ratio(returns: pd.Series, risk_free_rate: float = 0.03,
                      periods_per_year: int = 252) -> float:
        """
        计算 Sortino 比率
        
        Args:
            returns: 收益率序列
            risk_free_rate: 无风险利率
            periods_per_year: 每年的期数
            
        Returns:
            float: Sortino 比率
        """
        excess_returns = returns - risk_free_rate / periods_per_year
        downside_returns = returns[returns < 0]
        downside_std = downside_returns.std() * np.sqrt(periods_per_year)
        
        if downside_std == 0 or len(downside_returns) == 0:
            return 0
        
        return excess_returns.mean() * periods_per_year / downside_std
    
    @staticmethod
    def turnover(positions: pd.DataFrame) -> pd.Series:
        """
        计算换手率
        
        Args:
            positions: 持仓权重 DataFrame
            
        Returns:
            Series: 换手率时间序列
        """
        position_change = positions.diff().abs().sum(axis=1)
        return position_change / 2  # 双边换手率
