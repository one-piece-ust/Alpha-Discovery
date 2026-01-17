"""
自定义因子模块

在这里添加你自己挖掘的因子
"""


class CustomFactor:
    """自定义因子基类"""
    
    def __init__(self, name: str, expression: str, description: str = ""):
        self.name = name
        self.expression = expression
        self.description = description
        
    def get_expression(self) -> str:
        return self.expression
        
    def __str__(self):
        return f"{self.name}: {self.expression}"
    
    def __repr__(self):
        return f"CustomFactor(name='{self.name}', expression='{self.expression}')"


# ==================== 示例自定义因子 ====================

# 示例 1: 价格动量与成交量结合
PRICE_VOLUME_MOMENTUM = CustomFactor(
    name="price_volume_momentum",
    expression="(Ref($close, 20) / $close - 1) * ($volume / Mean($volume, 20))",
    description="价格动量与量比的组合因子"
)

# 示例 2: 波动率调整的动量
VOLATILITY_ADJUSTED_MOMENTUM = CustomFactor(
    name="vol_adj_momentum",
    expression="(Ref($close, 20) / $close - 1) / Std($close / Ref($close, 1) - 1, 20)",
    description="波动率调整的动量因子"
)

# 示例 3: 相对强弱动量
RELATIVE_STRENGTH = CustomFactor(
    name="relative_strength",
    expression="(Ref($close, 60) / $close - 1) - (Ref($close, 20) / $close - 1)",
    description="长期动量减去短期动量"
)

# 示例 4: 价格加速度
PRICE_ACCELERATION = CustomFactor(
    name="price_acceleration",
    expression="(Ref($close, 1) / $close - 1) - (Ref($close, 2) / Ref($close, 1) - 1)",
    description="价格变化的加速度"
)

# 示例 5: 量价背离
VOLUME_PRICE_DIVERGENCE = CustomFactor(
    name="vol_price_div",
    expression="Corr($close, $volume, 20) * -1",
    description="价量相关性的负值，负相关时因子值高"
)

# 示例 6: 高低价差比率
HIGH_LOW_RATIO = CustomFactor(
    name="high_low_ratio",
    expression="Mean(($high - $low) / $close, 20)",
    description="平均振幅比率"
)

# 示例 7: 收盘价相对位置
CLOSE_POSITION = CustomFactor(
    name="close_position",
    expression="($close - $low) / ($high - $low)",
    description="收盘价在当日高低价之间的位置"
)

# 示例 8: 趋势强度
TREND_STRENGTH = CustomFactor(
    name="trend_strength",
    expression="($close - Mean($close, 20)) / Std($close, 20)",
    description="价格相对均线的标准化距离"
)

# 示例 9: 成交额波动率
AMOUNT_VOLATILITY = CustomFactor(
    name="amount_volatility",
    expression="Std($amount / Ref($amount, 1) - 1, 20)",
    description="成交额变化的波动率"
)

# 示例 10: 多周期动量组合
MULTI_PERIOD_MOMENTUM = CustomFactor(
    name="multi_period_momentum",
    expression="0.5 * (Ref($close, 5) / $close - 1) + 0.3 * (Ref($close, 20) / $close - 1) + 0.2 * (Ref($close, 60) / $close - 1)",
    description="多个周期动量的加权组合"
)


# 自定义因子字典
CUSTOM_FACTORS = {
    "price_volume_momentum": PRICE_VOLUME_MOMENTUM,
    "vol_adj_momentum": VOLATILITY_ADJUSTED_MOMENTUM,
    "relative_strength": RELATIVE_STRENGTH,
    "price_acceleration": PRICE_ACCELERATION,
    "vol_price_div": VOLUME_PRICE_DIVERGENCE,
    "high_low_ratio": HIGH_LOW_RATIO,
    "close_position": CLOSE_POSITION,
    "trend_strength": TREND_STRENGTH,
    "amount_volatility": AMOUNT_VOLATILITY,
    "multi_period_momentum": MULTI_PERIOD_MOMENTUM,
}


def get_factor(name: str) -> CustomFactor:
    """获取自定义因子"""
    if name in CUSTOM_FACTORS:
        return CUSTOM_FACTORS[name]
    else:
        raise ValueError(f"Unknown custom factor: {name}")


def list_factors() -> list:
    """列出所有自定义因子"""
    return list(CUSTOM_FACTORS.keys())


def add_factor(factor: CustomFactor):
    """添加新的自定义因子到字典"""
    CUSTOM_FACTORS[factor.name] = factor
    

def create_factor(name: str, expression: str, description: str = "") -> CustomFactor:
    """快速创建并注册自定义因子"""
    factor = CustomFactor(name, expression, description)
    add_factor(factor)
    return factor
