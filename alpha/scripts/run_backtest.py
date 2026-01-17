"""
运行因子回测脚本

快速运行因子回测的命令行工具
"""

import argparse
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from backtest.factor_test import FactorBacktest
from backtest.portfolio import MultiFactorBacktest
from factors import technical, custom
from loguru import logger


def run_single_factor(args):
    """运行单因子回测"""
    logger.info(f"Running single factor backtest: {args.factor}")
    
    # 从因子库获取因子
    if hasattr(technical, args.factor.upper()):
        factor_class = getattr(technical, args.factor.upper())
        factor = factor_class()
    elif args.factor in technical.TECHNICAL_FACTORS:
        factor = technical.get_factor(args.factor)
    elif args.factor in custom.CUSTOM_FACTORS:
        factor = custom.get_factor(args.factor)
    elif args.expression:
        # 使用自定义表达式
        factor_expr = args.expression
        factor = None
    else:
        logger.error(f"Unknown factor: {args.factor}")
        logger.info("Available factors:")
        logger.info(f"Technical: {technical.list_factors()}")
        logger.info(f"Custom: {custom.list_factors()}")
        return
    
    # 创建回测
    if factor:
        bt = FactorBacktest(
            factor=factor,
            start_date=args.start,
            end_date=args.end,
            universe=args.universe,
        )
    else:
        bt = FactorBacktest(
            factor_expr=factor_expr,
            start_date=args.start,
            end_date=args.end,
            universe=args.universe,
            name=args.factor
        )
    
    # 运行回测
    results = bt.run()
    
    # 生成报告
    if args.output:
        bt.generate_report(args.output)
    
    # 绘图
    if args.plot:
        bt.plot_ic(f"results/plots/{args.factor}_ic.png")
        bt.plot_group_returns(f"results/plots/{args.factor}_returns.png")
    
    logger.info("Backtest completed!")
    logger.info(f"IC Mean: {results['ic_mean']:.4f}")
    logger.info(f"ICIR: {results['icir']:.4f}")
    logger.info(f"Annual Return: {results['annual_return']:.2%}")
    logger.info(f"Sharpe Ratio: {results['sharpe_ratio']:.4f}")


def run_multi_factor(args):
    """运行多因子回测"""
    logger.info(f"Running multi-factor backtest with {len(args.factors)} factors")
    
    # 构建因子字典
    factors = {}
    for factor_name in args.factors:
        if factor_name in technical.TECHNICAL_FACTORS:
            factor = technical.get_factor(factor_name)
            factors[factor_name] = factor.get_expression()
        elif factor_name in custom.CUSTOM_FACTORS:
            factor = custom.get_factor(factor_name)
            factors[factor_name] = factor.get_expression()
        else:
            logger.warning(f"Unknown factor: {factor_name}, skipping...")
    
    if not factors:
        logger.error("No valid factors found")
        return
    
    # 创建多因子回测
    mbt = MultiFactorBacktest(
        factors=factors,
        start_date=args.start,
        end_date=args.end,
        universe=args.universe,
    )
    
    # 运行回测
    results = mbt.run()
    
    # 生成报告
    if args.output:
        mbt.generate_report(args.output)
    
    logger.info("Multi-factor backtest completed!")


def main():
    parser = argparse.ArgumentParser(description="Run factor backtest")
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # 单因子回测
    single_parser = subparsers.add_parser('single', help='Run single factor backtest')
    single_parser.add_argument('factor', type=str, help='Factor name or expression')
    single_parser.add_argument('--expression', type=str, help='Factor expression (if custom)')
    single_parser.add_argument('--start', type=str, default='2018-01-01', help='Start date')
    single_parser.add_argument('--end', type=str, default='2023-12-31', help='End date')
    single_parser.add_argument('--universe', type=str, default='csi300', help='Stock universe')
    single_parser.add_argument('--output', type=str, help='Output report path')
    single_parser.add_argument('--plot', action='store_true', help='Generate plots')
    
    # 多因子回测
    multi_parser = subparsers.add_parser('multi', help='Run multi-factor backtest')
    multi_parser.add_argument('factors', nargs='+', help='Factor names')
    multi_parser.add_argument('--start', type=str, default='2018-01-01', help='Start date')
    multi_parser.add_argument('--end', type=str, default='2023-12-31', help='End date')
    multi_parser.add_argument('--universe', type=str, default='csi300', help='Stock universe')
    multi_parser.add_argument('--output', type=str, help='Output report path')
    
    # 列出可用因子
    list_parser = subparsers.add_parser('list', help='List available factors')
    
    args = parser.parse_args()
    
    if args.command == 'single':
        run_single_factor(args)
    elif args.command == 'multi':
        run_multi_factor(args)
    elif args.command == 'list':
        logger.info("=== Technical Factors ===")
        for name in technical.list_factors():
            logger.info(f"  - {name}")
        logger.info("\n=== Custom Factors ===")
        for name in custom.list_factors():
            logger.info(f"  - {name}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
