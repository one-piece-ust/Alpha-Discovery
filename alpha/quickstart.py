"""
快速开始示例

演示如何使用因子回测框架
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backtest.factor_test import FactorBacktest
from backtest.portfolio import MultiFactorBacktest
from factors import technical, custom
from loguru import logger

# 配置日志
logger.add("logs/quickstart.log", rotation="10 MB")


def example_1_simple_momentum():
    """示例 1: 简单动量因子测试"""
    logger.info("\n" + "="*60)
    logger.info("示例 1: 测试 20 日动量因子")
    logger.info("="*60)
    
    # 定义因子表达式
    factor_expr = "Ref($close, 20) / $close - 1"
    
    # 创建回测实例
    bt = FactorBacktest(
        factor_expr=factor_expr,
        start_date="2020-01-01",
        end_date="2023-12-31",
        universe="csi300",
        name="momentum_20d"
    )
    
    # 运行回测
    results = bt.run()
    
    # 打印结果
    print(f"\n📊 回测结果:")
    print(f"IC 均值: {results['ic_mean']:.4f}")
    print(f"ICIR: {results['icir']:.4f}")
    print(f"年化收益率: {results['annual_return']:.2%}")
    print(f"Sharpe 比率: {results['sharpe_ratio']:.4f}")
    print(f"最大回撤: {results['max_drawdown']:.2%}")
    
    # 生成报告
    bt.generate_report("results/reports/momentum_20d_report.html")
    print(f"\n✅ 报告已生成: results/reports/momentum_20d_report.html")


def example_2_predefined_factor():
    """示例 2: 使用预定义的技术因子"""
    logger.info("\n" + "="*60)
    logger.info("示例 2: 使用预定义的 RSI 因子")
    logger.info("="*60)
    
    # 使用预定义因子
    rsi_factor = technical.RSI(period=14)
    
    bt = FactorBacktest(
        factor=rsi_factor,
        start_date="2020-01-01",
        end_date="2023-12-31",
        universe="csi300"
    )
    
    results = bt.run()
    
    print(f"\n📊 {rsi_factor.name} 回测结果:")
    print(f"IC 均值: {results['ic_mean']:.4f}")
    print(f"ICIR: {results['icir']:.4f}")
    print(f"年化收益率: {results['annual_return']:.2%}")


def example_3_custom_factor():
    """示例 3: 自定义因子测试"""
    logger.info("\n" + "="*60)
    logger.info("示例 3: 测试自定义组合因子")
    logger.info("="*60)
    
    # 使用预定义的自定义因子
    factor = custom.PRICE_VOLUME_MOMENTUM
    
    bt = FactorBacktest(
        factor=factor,
        start_date="2020-01-01",
        end_date="2023-12-31",
        universe="csi300"
    )
    
    results = bt.run()
    
    print(f"\n📊 {factor.name} 回测结果:")
    print(f"描述: {factor.description}")
    print(f"IC 均值: {results['ic_mean']:.4f}")
    print(f"ICIR: {results['icir']:.4f}")
    print(f"年化收益率: {results['annual_return']:.2%}")


def example_4_multi_factor():
    """示例 4: 多因子组合测试"""
    logger.info("\n" + "="*60)
    logger.info("示例 4: 多因子组合测试")
    logger.info("="*60)
    
    # 定义多个因子
    factors = {
        "momentum_20": "Ref($close, 20) / $close - 1",
        "reversal_5": "Ref($close, 5) / $close - 1",
        "volume_ratio": "$volume / Mean($volume, 20)"
    }
    
    # 定义权重
    weights = {
        "momentum_20": 0.5,
        "reversal_5": 0.3,
        "volume_ratio": 0.2
    }
    
    # 创建多因子回测
    mbt = MultiFactorBacktest(
        factors=factors,
        weights=weights,
        start_date="2020-01-01",
        end_date="2023-12-31",
        universe="csi300"
    )
    
    # 运行回测
    results = mbt.run()
    
    # 打印比较结果
    print(f"\n📊 因子对比:")
    print(results['comparison'].to_string())
    
    print(f"\n✅ 多因子回测完成!")


def example_5_create_custom_factor():
    """示例 5: 创建并测试自己的因子"""
    logger.info("\n" + "="*60)
    logger.info("示例 5: 创建并测试自定义因子")
    logger.info("="*60)
    
    # 创建自定义因子
    my_factor = custom.create_factor(
        name="my_awesome_factor",
        expression="(Ref($close, 10) / $close - 1) * Std($close / Ref($close, 1) - 1, 10)",
        description="10日动量乘以波动率"
    )
    
    print(f"创建因子: {my_factor.name}")
    print(f"表达式: {my_factor.expression}")
    print(f"描述: {my_factor.description}")
    
    # 测试因子
    bt = FactorBacktest(
        factor=my_factor,
        start_date="2020-01-01",
        end_date="2023-12-31",
        universe="csi300"
    )
    
    results = bt.run()
    
    print(f"\n📊 回测结果:")
    print(f"IC 均值: {results['ic_mean']:.4f}")
    print(f"ICIR: {results['icir']:.4f}")
    print(f"年化收益率: {results['annual_return']:.2%}")


def main():
    """运行所有示例"""
    print("""
╔══════════════════════════════════════════════════════════╗
║          Alpha 因子回测框架 - 快速开始示例                ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    print("请选择要运行的示例:")
    print("1. 简单动量因子测试")
    print("2. 使用预定义技术因子 (RSI)")
    print("3. 使用自定义组合因子")
    print("4. 多因子组合测试")
    print("5. 创建并测试自己的因子")
    print("6. 运行所有示例")
    print("0. 退出")
    
    choice = input("\n请输入选项 (0-6): ").strip()
    
    examples = {
        '1': example_1_simple_momentum,
        '2': example_2_predefined_factor,
        '3': example_3_custom_factor,
        '4': example_4_multi_factor,
        '5': example_5_create_custom_factor,
    }
    
    if choice == '0':
        print("退出程序")
        return
    elif choice == '6':
        for func in examples.values():
            try:
                func()
            except Exception as e:
                logger.error(f"示例运行失败: {e}")
                print(f"❌ 错误: {e}")
    elif choice in examples:
        try:
            examples[choice]()
        except Exception as e:
            logger.error(f"示例运行失败: {e}")
            print(f"❌ 错误: {e}")
            print("\n💡 提示:")
            print("1. 确保已安装所有依赖: pip install -r requirements.txt")
            print("2. 确保已下载数据: python scripts/download_data.py")
            print("3. 检查 config.yaml 配置文件")
    else:
        print("无效选项")


if __name__ == "__main__":
    main()
