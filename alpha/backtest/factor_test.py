"""
因子回测核心模块

提供单因子回测、IC分析、分层测试等功能
"""

import pandas as pd
import numpy as np
from typing import Union, Dict, Any, Optional
from pathlib import Path
import yaml
from loguru import logger

try:
    import qlib
    from qlib.data import D
    from qlib.data.dataset import DatasetH
    from qlib.data.dataset.handler import DataHandlerLP
except ImportError:
    logger.warning("Qlib not installed. Please run: pip install pyqlib")
    

class FactorBacktest:
    """
    单因子回测类
    
    用于测试单个因子的有效性，包括 IC 分析、分层回测等
    """
    
    def __init__(
        self,
        factor_expr: Union[str, object] = None,
        factor: object = None,
        start_date: str = "2018-01-01",
        end_date: str = "2023-12-31",
        universe: str = "csi300",
        benchmark: str = "SH000300",
        config_path: str = None,
        **kwargs
    ):
        """
        初始化因子回测
        
        Args:
            factor_expr: 因子表达式字符串（Qlib 格式）
            factor: 因子对象（需要有 get_expression 方法）
            start_date: 回测开始日期
            end_date: 回测结束日期
            universe: 股票池
            benchmark: 基准指数
            config_path: 配置文件路径
            **kwargs: 其他参数
        """
        # 加载配置
        self.config = self._load_config(config_path)
        
        # 设置参数
        self.start_date = start_date
        self.end_date = end_date
        self.universe = universe
        self.benchmark = benchmark
        
        # 处理因子
        if factor is not None and hasattr(factor, 'get_expression'):
            self.factor_expr = factor.get_expression()
            self.factor_name = factor.name if hasattr(factor, 'name') else 'custom_factor'
        elif factor_expr is not None:
            self.factor_expr = factor_expr
            self.factor_name = kwargs.get('name', 'custom_factor')
        else:
            raise ValueError("Either factor_expr or factor must be provided")
        
        # 其他参数
        self.n_groups = kwargs.get('n_groups', self.config['portfolio']['n_groups'])
        self.top_pct = kwargs.get('top_pct', self.config['portfolio']['top_pct'])
        self.bottom_pct = kwargs.get('bottom_pct', self.config['portfolio']['bottom_pct'])
        
        # 结果存储
        self.factor_data = None
        self.returns_data = None
        self.ic_data = None
        self.group_returns = None
        self.results = {}
        
        logger.info(f"Initialized FactorBacktest: {self.factor_name}")
        logger.info(f"Period: {self.start_date} to {self.end_date}")
        logger.info(f"Factor expression: {self.factor_expr}")
        
    def _load_config(self, config_path: str = None) -> Dict:
        """加载配置文件"""
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config.yaml"
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        return config
    
    def initialize_qlib(self):
        """初始化 Qlib"""
        try:
            qlib.init(
                provider_uri=self.config['data']['data_path'],
                region="cn"
            )
            logger.info("Qlib initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Qlib: {e}")
            raise
    
    def load_factor_data(self) -> pd.DataFrame:
        """
        加载因子数据
        
        Returns:
            DataFrame: 因子值，index 为 (date, instrument)
        """
        logger.info("Loading factor data...")
        
        try:
            # 使用 Qlib 计算因子
            fields = [self.factor_expr]
            names = [self.factor_name]
            
            df = D.features(
                instruments=self.universe,
                fields=fields,
                start_time=self.start_date,
                end_time=self.end_date,
                freq="day"
            )
            
            df.columns = names
            self.factor_data = df
            
            logger.info(f"Factor data loaded. Shape: {df.shape}")
            logger.info(f"Date range: {df.index.get_level_values('datetime').min()} to {df.index.get_level_values('datetime').max()}")
            logger.info(f"Coverage: {df[self.factor_name].notna().sum() / len(df) * 100:.2f}%")
            
            return df
            
        except Exception as e:
            logger.error(f"Failed to load factor data: {e}")
            raise
    
    def load_returns_data(self, forward_period: int = 1) -> pd.DataFrame:
        """
        加载收益率数据
        
        Args:
            forward_period: 前向收益期数
            
        Returns:
            DataFrame: 收益率数据
        """
        logger.info(f"Loading returns data (forward period: {forward_period})...")
        
        try:
            # 加载收盘价
            close = D.features(
                instruments=self.universe,
                fields=["$close"],
                start_time=self.start_date,
                end_time=self.end_date,
                freq="day"
            )
            
            # 计算前向收益率
            returns = close.groupby(level='instrument').apply(
                lambda x: x.pct_change(forward_period).shift(-forward_period)
            )
            returns.columns = [f'return_{forward_period}d']
            
            self.returns_data = returns
            
            logger.info(f"Returns data loaded. Shape: {returns.shape}")
            
            return returns
            
        except Exception as e:
            logger.error(f"Failed to load returns data: {e}")
            raise
    
    def preprocess_factor(self, 
                         neutralize: bool = None,
                         standardize: bool = None,
                         winsorize: bool = None) -> pd.DataFrame:
        """
        因子预处理
        
        Args:
            neutralize: 是否中性化
            standardize: 是否标准化
            winsorize: 是否去极值
            
        Returns:
            处理后的因子数据
        """
        if self.factor_data is None:
            self.load_factor_data()
        
        df = self.factor_data.copy()
        factor_col = self.factor_name
        
        # 使用配置文件的默认值
        if neutralize is None:
            neutralize = self.config['factor']['neutralize']
        if standardize is None:
            standardize = self.config['factor']['standardize']
        if winsorize is None:
            winsorize = self.config['factor']['winsorize']
        
        logger.info("Preprocessing factor...")
        
        # 去极值
        if winsorize:
            method = self.config['factor']['winsorize_method']
            if method == 'std':
                std_num = self.config['factor']['winsorize_std']
                df = df.groupby(level='datetime').apply(
                    lambda x: self._winsorize_std(x[factor_col], std_num)
                )
            elif method == 'quantile':
                lower, upper = self.config['factor']['winsorize_quantile']
                df = df.groupby(level='datetime').apply(
                    lambda x: self._winsorize_quantile(x[factor_col], lower, upper)
                )
            logger.info(f"Winsorized using {method} method")
        
        # 标准化
        if standardize:
            df = df.groupby(level='datetime').apply(
                lambda x: (x[factor_col] - x[factor_col].mean()) / x[factor_col].std()
            )
            logger.info("Standardized")
        
        # 市值中性化
        if neutralize:
            logger.info("Neutralization not implemented yet (requires market cap data)")
        
        # 转换回 DataFrame
        if isinstance(df, pd.Series):
            df = df.to_frame(factor_col)
        
        self.factor_data = df
        return df
    
    @staticmethod
    def _winsorize_std(series: pd.Series, n_std: float = 3) -> pd.Series:
        """标准差去极值"""
        mean = series.mean()
        std = series.std()
        upper = mean + n_std * std
        lower = mean - n_std * std
        return series.clip(lower, upper)
    
    @staticmethod
    def _winsorize_quantile(series: pd.Series, lower: float = 0.01, upper: float = 0.99) -> pd.Series:
        """分位数去极值"""
        lower_val = series.quantile(lower)
        upper_val = series.quantile(upper)
        return series.clip(lower_val, upper_val)
    
    def calculate_ic(self, method: str = 'pearson') -> pd.Series:
        """
        计算 IC (Information Coefficient)
        
        Args:
            method: 相关系数方法，'pearson' 或 'spearman'
            
        Returns:
            Series: 每日 IC 值
        """
        if self.factor_data is None:
            self.load_factor_data()
        if self.returns_data is None:
            self.load_returns_data()
        
        logger.info(f"Calculating IC ({method})...")
        
        # 合并因子和收益数据
        data = pd.concat([self.factor_data, self.returns_data], axis=1).dropna()
        
        # 按日期计算相关系数
        ic_series = data.groupby(level='datetime').apply(
            lambda x: x[self.factor_name].corr(x.iloc[:, -1], method=method)
        )
        
        self.ic_data = ic_series
        
        # 计算统计指标
        ic_mean = ic_series.mean()
        ic_std = ic_series.std()
        icir = ic_mean / ic_std if ic_std != 0 else 0
        ic_positive_rate = (ic_series > 0).sum() / len(ic_series)
        
        logger.info(f"IC Mean: {ic_mean:.4f}")
        logger.info(f"IC Std: {ic_std:.4f}")
        logger.info(f"ICIR: {icir:.4f}")
        logger.info(f"IC Positive Rate: {ic_positive_rate:.2%}")
        
        self.results.update({
            'ic_mean': ic_mean,
            'ic_std': ic_std,
            'icir': icir,
            'ic_positive_rate': ic_positive_rate,
            'ic_series': ic_series
        })
        
        return ic_series
    
    def group_backtest(self) -> pd.DataFrame:
        """
        分层回测
        
        Returns:
            DataFrame: 各分层的累计收益
        """
        if self.factor_data is None:
            self.load_factor_data()
        if self.returns_data is None:
            self.load_returns_data()
        
        logger.info(f"Running group backtest ({self.n_groups} groups)...")
        
        # 合并数据
        data = pd.concat([self.factor_data, self.returns_data], axis=1).dropna()
        
        # 按日期分组
        group_returns_list = []
        
        for date, date_data in data.groupby(level='datetime'):
            # 按因子值分组
            date_data['group'] = pd.qcut(
                date_data[self.factor_name], 
                q=self.n_groups, 
                labels=False,
                duplicates='drop'
            )
            
            # 计算各组平均收益
            group_ret = date_data.groupby('group')[date_data.columns[-2]].mean()
            group_ret.name = date
            group_returns_list.append(group_ret)
        
        # 合并所有日期的分组收益
        group_returns = pd.DataFrame(group_returns_list)
        
        # 计算累计收益
        cumulative_returns = (1 + group_returns).cumprod()
        
        self.group_returns = cumulative_returns
        
        # 计算多空组合收益
        long_short_returns = group_returns.iloc[:, -1] - group_returns.iloc[:, 0]
        cumulative_ls = (1 + long_short_returns).cumprod()
        
        # 统计指标
        annual_return = self._annualized_return(long_short_returns)
        annual_vol = self._annualized_volatility(long_short_returns)
        sharpe = annual_return / annual_vol if annual_vol != 0 else 0
        max_dd = self._max_drawdown(cumulative_ls)
        
        logger.info(f"Long-Short Annual Return: {annual_return:.2%}")
        logger.info(f"Long-Short Sharpe Ratio: {sharpe:.4f}")
        logger.info(f"Long-Short Max Drawdown: {max_dd:.2%}")
        
        self.results.update({
            'group_returns': cumulative_returns,
            'long_short_returns': cumulative_ls,
            'annual_return': annual_return,
            'annual_volatility': annual_vol,
            'sharpe_ratio': sharpe,
            'max_drawdown': max_dd
        })
        
        return cumulative_returns
    
    @staticmethod
    def _annualized_return(returns: pd.Series, periods_per_year: int = 252) -> float:
        """计算年化收益率"""
        cumulative = (1 + returns).prod()
        n_periods = len(returns)
        return cumulative ** (periods_per_year / n_periods) - 1
    
    @staticmethod
    def _annualized_volatility(returns: pd.Series, periods_per_year: int = 252) -> float:
        """计算年化波动率"""
        return returns.std() * np.sqrt(periods_per_year)
    
    @staticmethod
    def _max_drawdown(cumulative_returns: pd.Series) -> float:
        """计算最大回撤"""
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max
        return drawdown.min()
    
    def run(self, preprocess: bool = True) -> Dict[str, Any]:
        """
        运行完整的因子回测流程
        
        Args:
            preprocess: 是否进行因子预处理
            
        Returns:
            Dict: 回测结果
        """
        logger.info("=" * 60)
        logger.info(f"Starting backtest for factor: {self.factor_name}")
        logger.info("=" * 60)
        
        # 初始化 Qlib
        self.initialize_qlib()
        
        # 加载数据
        self.load_factor_data()
        self.load_returns_data()
        
        # 预处理
        if preprocess:
            self.preprocess_factor()
        
        # 计算 IC
        self.calculate_ic(method='pearson')
        self.calculate_ic(method='spearman')  # 同时计算 RankIC
        
        # 分层回测
        self.group_backtest()
        
        logger.info("=" * 60)
        logger.info("Backtest completed!")
        logger.info("=" * 60)
        
        return self.results
    
    def generate_report(self, save_path: str = None):
        """
        生成回测报告
        
        Args:
            save_path: 报告保存路径
        """
        if not self.results:
            logger.warning("No results to generate report. Run backtest first.")
            return
        
        from .analysis import ReportGenerator
        
        generator = ReportGenerator(self.results, self.factor_name)
        generator.generate_html_report(save_path)
        
        logger.info(f"Report generated: {save_path}")
    
    def plot_ic(self, save_path: str = None):
        """绘制 IC 时序图"""
        import matplotlib.pyplot as plt
        
        if self.ic_data is None:
            logger.warning("No IC data available")
            return
        
        fig, axes = plt.subplots(2, 1, figsize=(12, 8))
        
        # IC 时序图
        axes[0].plot(self.ic_data.index, self.ic_data.values)
        axes[0].axhline(y=0, color='r', linestyle='--', alpha=0.5)
        axes[0].set_title(f'{self.factor_name} - IC Time Series')
        axes[0].set_xlabel('Date')
        axes[0].set_ylabel('IC')
        axes[0].grid(True, alpha=0.3)
        
        # IC 累计图
        cumulative_ic = self.ic_data.cumsum()
        axes[1].plot(cumulative_ic.index, cumulative_ic.values)
        axes[1].set_title(f'{self.factor_name} - Cumulative IC')
        axes[1].set_xlabel('Date')
        axes[1].set_ylabel('Cumulative IC')
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"IC plot saved: {save_path}")
        else:
            plt.show()
    
    def plot_group_returns(self, save_path: str = None):
        """绘制分层收益图"""
        import matplotlib.pyplot as plt
        
        if self.group_returns is None:
            logger.warning("No group returns data available")
            return
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        for col in self.group_returns.columns:
            ax.plot(self.group_returns.index, self.group_returns[col], 
                   label=f'Group {col+1}', alpha=0.7)
        
        ax.set_title(f'{self.factor_name} - Group Returns')
        ax.set_xlabel('Date')
        ax.set_ylabel('Cumulative Return')
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Group returns plot saved: {save_path}")
        else:
            plt.show()
