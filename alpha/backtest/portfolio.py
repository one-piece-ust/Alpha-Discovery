"""
组合构建和多因子回测模块
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any
from loguru import logger

from .factor_test import FactorBacktest


class MultiFactorBacktest:
    """
    多因子组合回测
    
    支持多个因子的线性组合
    """
    
    def __init__(
        self,
        factors: Dict[str, str],
        weights: Dict[str, float] = None,
        start_date: str = "2018-01-01",
        end_date: str = "2023-12-31",
        universe: str = "csi300",
        **kwargs
    ):
        """
        初始化多因子回测
        
        Args:
            factors: 因子字典，{name: expression}
            weights: 因子权重字典，{name: weight}
            start_date: 回测开始日期
            end_date: 回测结束日期
            universe: 股票池
        """
        self.factors = factors
        
        # 如果没有提供权重，使用等权
        if weights is None:
            n = len(factors)
            self.weights = {name: 1.0/n for name in factors.keys()}
        else:
            # 归一化权重
            total_weight = sum(weights.values())
            self.weights = {k: v/total_weight for k, v in weights.items()}
        
        self.start_date = start_date
        self.end_date = end_date
        self.universe = universe
        self.kwargs = kwargs
        
        self.factor_tests = {}
        self.composite_factor_data = None
        self.results = {}
        
        logger.info(f"Initialized MultiFactorBacktest with {len(factors)} factors")
        logger.info(f"Weights: {self.weights}")
    
    def run_individual_tests(self) -> Dict[str, Dict]:
        """
        运行单因子测试
        
        Returns:
            Dict: 各因子的测试结果
        """
        logger.info("Running individual factor tests...")
        
        individual_results = {}
        
        for name, expr in self.factors.items():
            logger.info(f"Testing factor: {name}")
            
            bt = FactorBacktest(
                factor_expr=expr,
                start_date=self.start_date,
                end_date=self.end_date,
                universe=self.universe,
                name=name,
                **self.kwargs
            )
            
            results = bt.run(preprocess=True)
            self.factor_tests[name] = bt
            individual_results[name] = results
        
        self.results['individual'] = individual_results
        return individual_results
    
    def build_composite_factor(self) -> pd.DataFrame:
        """
        构建复合因子
        
        Returns:
            DataFrame: 复合因子数据
        """
        logger.info("Building composite factor...")
        
        # 确保已运行单因子测试
        if not self.factor_tests:
            self.run_individual_tests()
        
        # 获取所有因子的标准化数据
        factor_dfs = []
        
        for name, bt in self.factor_tests.items():
            # 获取标准化后的因子
            factor_df = bt.factor_data.copy()
            factor_df.columns = [name]
            factor_dfs.append(factor_df)
        
        # 合并所有因子
        all_factors = pd.concat(factor_dfs, axis=1)
        
        # 加权合成
        composite = pd.Series(0, index=all_factors.index)
        for name, weight in self.weights.items():
            composite += all_factors[name].fillna(0) * weight
        
        self.composite_factor_data = composite.to_frame('composite_factor')
        
        logger.info(f"Composite factor built. Shape: {self.composite_factor_data.shape}")
        
        return self.composite_factor_data
    
    def run_composite_test(self) -> Dict[str, Any]:
        """
        运行复合因子测试
        
        Returns:
            Dict: 复合因子测试结果
        """
        logger.info("Running composite factor test...")
        
        # 构建复合因子
        if self.composite_factor_data is None:
            self.build_composite_factor()
        
        # 创建复合因子回测
        bt = FactorBacktest(
            factor_expr=None,  # 直接使用数据
            start_date=self.start_date,
            end_date=self.end_date,
            universe=self.universe,
            name='composite_factor',
            **self.kwargs
        )
        
        # 手动设置因子数据
        bt.factor_data = self.composite_factor_data
        bt.factor_name = 'composite_factor'
        
        # 运行回测（跳过预处理，因为已经标准化）
        bt.initialize_qlib()
        bt.load_returns_data()
        bt.calculate_ic(method='pearson')
        bt.group_backtest()
        
        self.results['composite'] = bt.results
        self.results['composite_backtest'] = bt
        
        return bt.results
    
    def run(self) -> Dict[str, Any]:
        """
        运行完整的多因子回测
        
        Returns:
            Dict: 回测结果
        """
        logger.info("=" * 60)
        logger.info("Starting multi-factor backtest")
        logger.info("=" * 60)
        
        # 单因子测试
        self.run_individual_tests()
        
        # 复合因子测试
        self.run_composite_test()
        
        # 比较分析
        self._compare_factors()
        
        logger.info("=" * 60)
        logger.info("Multi-factor backtest completed!")
        logger.info("=" * 60)
        
        return self.results
    
    def _compare_factors(self):
        """比较各因子表现"""
        logger.info("\n" + "=" * 60)
        logger.info("Factor Comparison")
        logger.info("=" * 60)
        
        comparison = []
        
        # 单因子
        for name, results in self.results['individual'].items():
            comparison.append({
                'Factor': name,
                'IC Mean': results['ic_mean'],
                'ICIR': results['icir'],
                'Annual Return': results['annual_return'],
                'Sharpe Ratio': results['sharpe_ratio'],
                'Max Drawdown': results['max_drawdown']
            })
        
        # 复合因子
        comp_results = self.results['composite']
        comparison.append({
            'Factor': 'Composite',
            'IC Mean': comp_results['ic_mean'],
            'ICIR': comp_results['icir'],
            'Annual Return': comp_results['annual_return'],
            'Sharpe Ratio': comp_results['sharpe_ratio'],
            'Max Drawdown': comp_results['max_drawdown']
        })
        
        comparison_df = pd.DataFrame(comparison)
        self.results['comparison'] = comparison_df
        
        logger.info("\n" + comparison_df.to_string())
    
    def generate_report(self, save_path: str = None):
        """生成多因子回测报告"""
        from .analysis import ReportGenerator
        
        generator = ReportGenerator(self.results, 'Multi-Factor')
        generator.generate_multi_factor_report(save_path)


class PortfolioOptimizer:
    """
    组合优化器
    
    基于多个因子构建最优权重组合
    """
    
    def __init__(self, factors: Dict[str, str], **kwargs):
        """
        初始化组合优化器
        
        Args:
            factors: 因子字典
        """
        self.factors = factors
        self.kwargs = kwargs
        
    def optimize_weights_ic(self) -> Dict[str, float]:
        """
        基于 IC 优化权重
        
        Returns:
            Dict: 最优权重
        """
        logger.info("Optimizing weights based on IC...")
        
        # 运行多因子回测获取各因子 IC
        mbt = MultiFactorBacktest(
            factors=self.factors,
            weights=None,  # 等权
            **self.kwargs
        )
        mbt.run_individual_tests()
        
        # 提取 IC 均值
        ic_means = {}
        for name, results in mbt.results['individual'].items():
            ic_means[name] = abs(results['ic_mean'])  # 使用绝对值
        
        # 归一化为权重
        total_ic = sum(ic_means.values())
        weights = {k: v/total_ic for k, v in ic_means.items()}
        
        logger.info(f"Optimized weights: {weights}")
        
        return weights
    
    def optimize_weights_sharpe(self) -> Dict[str, float]:
        """
        基于 Sharpe 比率优化权重
        
        Returns:
            Dict: 最优权重
        """
        logger.info("Optimizing weights based on Sharpe ratio...")
        
        # 运行多因子回测
        mbt = MultiFactorBacktest(
            factors=self.factors,
            weights=None,
            **self.kwargs
        )
        mbt.run_individual_tests()
        
        # 提取 Sharpe 比率
        sharpes = {}
        for name, results in mbt.results['individual'].items():
            sharpes[name] = max(0, results['sharpe_ratio'])  # 只考虑正值
        
        # 归一化为权重
        total_sharpe = sum(sharpes.values())
        if total_sharpe == 0:
            # 如果所有 Sharpe 都 <= 0，使用等权
            n = len(sharpes)
            weights = {k: 1.0/n for k in sharpes.keys()}
        else:
            weights = {k: v/total_sharpe for k, v in sharpes.items()}
        
        logger.info(f"Optimized weights: {weights}")
        
        return weights
    
    def optimize_weights_mean_variance(self) -> Dict[str, float]:
        """
        均值-方差优化（最大化 Sharpe 比率）
        
        Returns:
            Dict: 最优权重
        """
        logger.info("Optimizing weights using mean-variance optimization...")
        
        # 需要计算因子收益的协方差矩阵
        # 这里简化实现，实际应使用优化算法
        
        # TODO: 实现完整的均值-方差优化
        logger.warning("Mean-variance optimization not fully implemented yet")
        
        return self.optimize_weights_sharpe()
