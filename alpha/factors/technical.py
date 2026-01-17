"""
技术指标因子库

常见的技术指标因子，基于 Qlib 的表达式语言实现
"""

from typing import Dict, Any


class TechnicalFactor:
    """技术指标因子基类"""
    
    def __init__(self, name: str = None):
        self.name = name or self.__class__.__name__
        
    def get_expression(self) -> str:
        """返回因子的 Qlib 表达式"""
        raise NotImplementedError
        
    def __str__(self):
        return f"{self.name}: {self.get_expression()}"


class Momentum(TechnicalFactor):
    """动量因子"""
    
    def __init__(self, period: int = 20, name: str = None):
        super().__init__(name)
        self.period = period
        
    def get_expression(self) -> str:
        return f"Ref($close, {self.period}) / $close - 1"


class Reversal(TechnicalFactor):
    """反转因子"""
    
    def __init__(self, period: int = 1, name: str = None):
        super().__init__(name)
        self.period = period
        
    def get_expression(self) -> str:
        return f"Ref($close, {self.period}) / $close - 1"


class MA(TechnicalFactor):
    """移动平均线因子"""
    
    def __init__(self, period: int = 20, name: str = None):
        super().__init__(name)
        self.period = period
        
    def get_expression(self) -> str:
        return f"Mean($close, {self.period})"


class MACD(TechnicalFactor):
    """MACD 因子"""
    
    def __init__(self, fast: int = 12, slow: int = 26, signal: int = 9, name: str = None):
        super().__init__(name)
        self.fast = fast
        self.slow = slow
        self.signal = signal
        
    def get_expression(self) -> str:
        ema_fast = f"EMA($close, {self.fast})"
        ema_slow = f"EMA($close, {self.slow})"
        dif = f"({ema_fast} - {ema_slow})"
        dea = f"EMA({dif}, {self.signal})"
        return f"({dif} - {dea})"


class RSI(TechnicalFactor):
    """RSI 相对强弱指标"""
    
    def __init__(self, period: int = 14, name: str = None):
        super().__init__(name)
        self.period = period
        
    def get_expression(self) -> str:
        # RSI = 100 - 100 / (1 + RS)
        # RS = Average Gain / Average Loss
        return f"RSI($close, {self.period})"


class BBANDS(TechnicalFactor):
    """布林带因子 - 返回价格相对布林带的位置"""
    
    def __init__(self, period: int = 20, std: float = 2.0, name: str = None):
        super().__init__(name)
        self.period = period
        self.std = std
        
    def get_expression(self) -> str:
        # (price - lower_band) / (upper_band - lower_band)
        ma = f"Mean($close, {self.period})"
        std = f"Std($close, {self.period})"
        upper = f"({ma} + {self.std} * {std})"
        lower = f"({ma} - {self.std} * {std})"
        return f"($close - {lower}) / ({upper} - {lower})"


class ATR(TechnicalFactor):
    """平均真实波动幅度"""
    
    def __init__(self, period: int = 14, name: str = None):
        super().__init__(name)
        self.period = period
        
    def get_expression(self) -> str:
        # ATR = MA(max(high-low, abs(high-close_prev), abs(low-close_prev)))
        tr = "Max($high - $low, Abs($high - Ref($close, 1)), Abs($low - Ref($close, 1)))"
        return f"Mean({tr}, {self.period})"


class VolumeRatio(TechnicalFactor):
    """量比因子"""
    
    def __init__(self, period: int = 20, name: str = None):
        super().__init__(name)
        self.period = period
        
    def get_expression(self) -> str:
        return f"$volume / Mean($volume, {self.period})"


class AmountRatio(TechnicalFactor):
    """成交额比率"""
    
    def __init__(self, period: int = 20, name: str = None):
        super().__init__(name)
        self.period = period
        
    def get_expression(self) -> str:
        return f"$amount / Mean($amount, {self.period})"


class VWAP(TechnicalFactor):
    """成交量加权平均价格"""
    
    def __init__(self, period: int = 20, name: str = None):
        super().__init__(name)
        self.period = period
        
    def get_expression(self) -> str:
        return f"Sum($amount, {self.period}) / Sum($volume, {self.period})"


class ROC(TechnicalFactor):
    """变动率因子"""
    
    def __init__(self, period: int = 12, name: str = None):
        super().__init__(name)
        self.period = period
        
    def get_expression(self) -> str:
        return f"($close - Ref($close, {self.period})) / Ref($close, {self.period})"


class CCI(TechnicalFactor):
    """顺势指标"""
    
    def __init__(self, period: int = 14, name: str = None):
        super().__init__(name)
        self.period = period
        
    def get_expression(self) -> str:
        tp = "($high + $low + $close) / 3"
        ma_tp = f"Mean({tp}, {self.period})"
        md = f"Mean(Abs({tp} - {ma_tp}), {self.period})"
        return f"({tp} - {ma_tp}) / (0.015 * {md})"


class KDJ(TechnicalFactor):
    """KDJ 随机指标 - 返回 K 值"""
    
    def __init__(self, period: int = 9, name: str = None):
        super().__init__(name)
        self.period = period
        
    def get_expression(self) -> str:
        # K = (close - lowest_low) / (highest_high - lowest_low) * 100
        lowest = f"Rolling(Min($low, {self.period}), {self.period})"
        highest = f"Rolling(Max($high, {self.period}), {self.period})"
        return f"($close - {lowest}) / ({highest} - {lowest}) * 100"


class PriceVolCorr(TechnicalFactor):
    """价量相关性因子"""
    
    def __init__(self, period: int = 20, name: str = None):
        super().__init__(name)
        self.period = period
        
    def get_expression(self) -> str:
        return f"Corr($close, $volume, {self.period})"


class Volatility(TechnicalFactor):
    """波动率因子"""
    
    def __init__(self, period: int = 20, name: str = None):
        super().__init__(name)
        self.period = period
        
    def get_expression(self) -> str:
        return f"Std($close / Ref($close, 1) - 1, {self.period})"


class Skewness(TechnicalFactor):
    """收益率偏度"""
    
    def __init__(self, period: int = 20, name: str = None):
        super().__init__(name)
        self.period = period
        
    def get_expression(self) -> str:
        return f"Skew($close / Ref($close, 1) - 1, {self.period})"


class Kurtosis(TechnicalFactor):
    """收益率峰度"""
    
    def __init__(self, period: int = 20, name: str = None):
        super().__init__(name)
        self.period = period
        
    def get_expression(self) -> str:
        return f"Kurt($close / Ref($close, 1) - 1, {self.period})"


# 预定义因子字典
TECHNICAL_FACTORS: Dict[str, TechnicalFactor] = {
    "momentum_20": Momentum(20),
    "momentum_60": Momentum(60),
    "reversal_1": Reversal(1),
    "reversal_5": Reversal(5),
    "ma_20": MA(20),
    "ma_60": MA(60),
    "macd": MACD(),
    "rsi_14": RSI(14),
    "bbands": BBANDS(),
    "atr_14": ATR(14),
    "volume_ratio": VolumeRatio(20),
    "amount_ratio": AmountRatio(20),
    "vwap_20": VWAP(20),
    "roc_12": ROC(12),
    "cci_14": CCI(14),
    "kdj_9": KDJ(9),
    "price_vol_corr": PriceVolCorr(20),
    "volatility_20": Volatility(20),
    "skewness_20": Skewness(20),
    "kurtosis_20": Kurtosis(20),
}


def get_factor(name: str) -> TechnicalFactor:
    """获取预定义的技术因子"""
    if name in TECHNICAL_FACTORS:
        return TECHNICAL_FACTORS[name]
    else:
        raise ValueError(f"Unknown factor: {name}")


def list_factors() -> list:
    """列出所有预定义的技术因子"""
    return list(TECHNICAL_FACTORS.keys())
