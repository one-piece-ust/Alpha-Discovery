"""
数据加载工具
"""

import pandas as pd
import numpy as np
from typing import Union, List
from loguru import logger

try:
    import qlib
    from qlib.data import D
except ImportError:
    logger.warning("Qlib not installed")


class DataLoader:
    """数据加载器"""
    
    def __init__(self, data_path: str = "./data/qlib_data"):
        """
        初始化数据加载器
        
        Args:
            data_path: Qlib 数据路径
        """
        self.data_path = data_path
        self.initialized = False
        
    def init_qlib(self):
        """初始化 Qlib"""
        if not self.initialized:
            try:
                qlib.init(provider_uri=self.data_path, region="cn")
                self.initialized = True
                logger.info("Qlib initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Qlib: {e}")
                raise
    
    def load_features(
        self,
        instruments: Union[str, List[str]],
        fields: List[str],
        start_time: str,
        end_time: str,
        freq: str = "day"
    ) -> pd.DataFrame:
        """
        加载特征数据
        
        Args:
            instruments: 股票代码或股票池
            fields: 字段列表
            start_time: 开始时间
            end_time: 结束时间
            freq: 频率
            
        Returns:
            DataFrame: 特征数据
        """
        if not self.initialized:
            self.init_qlib()
        
        df = D.features(
            instruments=instruments,
            fields=fields,
            start_time=start_time,
            end_time=end_time,
            freq=freq
        )
        
        logger.info(f"Loaded features: {df.shape}")
        return df
    
    def load_instruments(self, market: str = "csi300") -> List[str]:
        """
        加载股票池
        
        Args:
            market: 市场代码
            
        Returns:
            List: 股票代码列表
        """
        if not self.initialized:
            self.init_qlib()
        
        instruments = D.instruments(market=market)
        logger.info(f"Loaded {len(instruments)} instruments from {market}")
        return instruments
    
    def load_calendar(self, start_time: str, end_time: str, freq: str = "day") -> List:
        """
        加载交易日历
        
        Args:
            start_time: 开始时间
            end_time: 结束时间
            freq: 频率
            
        Returns:
            List: 交易日期列表
        """
        if not self.initialized:
            self.init_qlib()
        
        calendar = D.calendar(start_time=start_time, end_time=end_time, freq=freq)
        logger.info(f"Loaded {len(calendar)} trading days")
        return calendar
