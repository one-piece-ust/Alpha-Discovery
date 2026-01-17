"""
基本面因子库

常见的基本面因子，需要基本面数据支持
"""

from typing import Dict


class FundamentalFactor:
    """基本面因子基类"""
    
    def __init__(self, name: str = None):
        self.name = name or self.__class__.__name__
        
    def get_expression(self) -> str:
        """返回因子的 Qlib 表达式"""
        raise NotImplementedError
        
    def __str__(self):
        return f"{self.name}: {self.get_expression()}"


class PERatio(FundamentalFactor):
    """市盈率因子"""
    
    def get_expression(self) -> str:
        return "$pe_ratio"


class PBRatio(FundamentalFactor):
    """市净率因子"""
    
    def get_expression(self) -> str:
        return "$pb_ratio"


class PSRatio(FundamentalFactor):
    """市销率因子"""
    
    def get_expression(self) -> str:
        return "$ps_ratio"


class MarketCap(FundamentalFactor):
    """市值因子"""
    
    def get_expression(self) -> str:
        return "$market_cap"


class ROE(FundamentalFactor):
    """净资产收益率"""
    
    def get_expression(self) -> str:
        return "$roe"


class ROA(FundamentalFactor):
    """总资产收益率"""
    
    def get_expression(self) -> str:
        return "$roa"


class GrossMargin(FundamentalFactor):
    """毛利率"""
    
    def get_expression(self) -> str:
        return "$gross_margin"


class NetMargin(FundamentalFactor):
    """净利率"""
    
    def get_expression(self) -> str:
        return "$net_margin"


class DebtRatio(FundamentalFactor):
    """资产负债率"""
    
    def get_expression(self) -> str:
        return "$debt_ratio"


class CurrentRatio(FundamentalFactor):
    """流动比率"""
    
    def get_expression(self) -> str:
        return "$current_ratio"


class EarningsGrowth(FundamentalFactor):
    """盈利增长率"""
    
    def __init__(self, period: int = 4, name: str = None):
        super().__init__(name)
        self.period = period
        
    def get_expression(self) -> str:
        return f"$earnings / Ref($earnings, {self.period}) - 1"


class RevenueGrowth(FundamentalFactor):
    """营收增长率"""
    
    def __init__(self, period: int = 4, name: str = None):
        super().__init__(name)
        self.period = period
        
    def get_expression(self) -> str:
        return f"$revenue / Ref($revenue, {self.period}) - 1"


# 预定义基本面因子
FUNDAMENTAL_FACTORS: Dict[str, FundamentalFactor] = {
    "pe_ratio": PERatio(),
    "pb_ratio": PBRatio(),
    "ps_ratio": PSRatio(),
    "market_cap": MarketCap(),
    "roe": ROE(),
    "roa": ROA(),
    "gross_margin": GrossMargin(),
    "net_margin": NetMargin(),
    "debt_ratio": DebtRatio(),
    "current_ratio": CurrentRatio(),
    "earnings_growth": EarningsGrowth(),
    "revenue_growth": RevenueGrowth(),
}


def get_factor(name: str) -> FundamentalFactor:
    """获取预定义的基本面因子"""
    if name in FUNDAMENTAL_FACTORS:
        return FUNDAMENTAL_FACTORS[name]
    else:
        raise ValueError(f"Unknown factor: {name}")


def list_factors() -> list:
    """列出所有预定义的基本面因子"""
    return list(FUNDAMENTAL_FACTORS.keys())
