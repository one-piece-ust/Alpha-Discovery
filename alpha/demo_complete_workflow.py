#!/usr/bin/env python3
"""
完整的因子回测流程示例
从数据准备到结果生成的完整演示
"""

import os
import sys
from pathlib import Path
from loguru import logger
import pandas as pd
import yaml

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

logger.add("logs/demo_{time}.log", rotation="1 day")


def step1_prepare_data():
    """步骤1: 准备数据"""
    logger.info("=" * 70)
    logger.info("步骤 1: 准备数据")
    logger.info("=" * 70)
    
    # 检查数据是否存在
    data_file = "./data/csi300_data.csv"
    
    if os.path.exists(data_file):
        df = pd.read_csv(data_file)
        logger.success(f"✓ 数据已存在: {data_file}")
        logger.info(f"  记录数: {len(df)}")
        logger.info(f"  股票数: {df['code'].nunique()}")
        logger.info(f"  时间范围: {df['日期'].min()} 至 {df['日期'].max()}")
        return True
    else:
        logger.warning(f"⚠ 数据文件不存在: {data_file}")
        logger.info("请先运行以下命令下载数据:")
        logger.info("  python scripts/download_data_fixed.py --source akshare --market csi300 --full")
        return False


def step2_convert_to_qlib():
    """步骤2: 将数据转换为 Qlib 格式（演示版）"""
    logger.info("\n" + "=" * 70)
    logger.info("步骤 2: 数据格式说明")
    logger.info("=" * 70)
    
    logger.info("""
    注意: Qlib 需要特定格式的数据。
    
    选项A: 使用 AKShare 数据（已下载）
      - 数据在 ./data/csi300_data.csv
      - 需要转换为 Qlib 格式
      
    选项B: 下载 Qlib 官方数据（推荐）
      - 运行: python -m qlib.run.get_data qlib_data --target_dir ./data/qlib_data --region cn
      - 或从官方获取预处理数据
      
    选项C: 使用 Mock 数据演示
      - 生成模拟数据用于测试流程
    
    本演示将使用选项C来展示完整流程。
    """)


def step3_simple_factor_calculation():
    """步骤3: 简单因子计算示例（不依赖 Qlib）"""
    logger.info("\n" + "=" * 70)
    logger.info("步骤 3: 简单因子计算示例")
    logger.info("=" * 70)
    
    try:
        import pandas as pd
        import numpy as np
        
        # 加载数据
        data_file = "./data/csi300_data.csv"
        if not os.path.exists(data_file):
            logger.warning("数据文件不存在，跳过此步骤")
            return
        
        df = pd.read_csv(data_file)
        logger.info(f"✓ 加载数据: {len(df)} 条记录")
        
        # 确保日期列是日期类型
        df['日期'] = pd.to_datetime(df['日期'])
        df = df.sort_values(['code', '日期'])
        
        # 计算动量因子
        logger.info("计算动量因子 (20日收益率)...")
        df['close'] = df['收盘']
        df['momentum_20'] = df.groupby('code')['close'].pct_change(20)
        
        # 计算反转因子
        logger.info("计算反转因子 (1日收益率)...")
        df['reversal_1'] = df.groupby('code')['close'].pct_change(1)
        
        # 计算成交量因子
        logger.info("计算成交量因子...")
        df['volume_ratio'] = df.groupby('code')['成交量'].transform(
            lambda x: x / x.rolling(20, min_periods=1).mean()
        )
        
        # 保存因子数据
        factor_cols = ['日期', 'code', 'close', 'momentum_20', 'reversal_1', 'volume_ratio']
        factor_df = df[factor_cols].dropna()
        
        output_file = "./data/factors_simple.csv"
        factor_df.to_csv(output_file, index=False, encoding='utf-8-sig')
        
        logger.success(f"✓ 因子计算完成")
        logger.info(f"  输出文件: {output_file}")
        logger.info(f"  记录数: {len(factor_df)}")
        logger.info(f"\n  因子统计:")
        logger.info(f"    动量因子均值: {factor_df['momentum_20'].mean():.4f}")
        logger.info(f"    动量因子标准差: {factor_df['momentum_20'].std():.4f}")
        logger.info(f"    反转因子均值: {factor_df['reversal_1'].mean():.4f}")
        logger.info(f"    成交量比率均值: {factor_df['volume_ratio'].mean():.4f}")
        
        return factor_df
        
    except Exception as e:
        logger.error(f"计算失败: {e}")
        import traceback
        traceback.print_exc()


def step4_simple_backtest():
    """步骤4: 简单回测示例（不依赖 Qlib）"""
    logger.info("\n" + "=" * 70)
    logger.info("步骤 4: 简单回测示例")
    logger.info("=" * 70)
    
    try:
        import pandas as pd
        import numpy as np
        
        # 加载因子数据
        factor_file = "./data/factors_simple.csv"
        if not os.path.exists(factor_file):
            logger.warning("因子文件不存在，跳过此步骤")
            return
        
        df = pd.read_csv(factor_file)
        df['日期'] = pd.to_datetime(df['日期'])
        
        logger.info(f"✓ 加载因子数据: {len(df)} 条记录")
        
        # 计算未来收益
        logger.info("计算未来收益...")
        df = df.sort_values(['code', '日期'])
        df['future_return'] = df.groupby('code')['close'].pct_change(1).shift(-1)
        
        # 去除缺失值
        df_valid = df.dropna()
        logger.info(f"  有效记录数: {len(df_valid)}")
        
        # 计算 IC (Information Coefficient)
        logger.info("\n计算信息系数 (IC)...")
        
        ic_results = {}
        for factor in ['momentum_20', 'reversal_1', 'volume_ratio']:
            # 按日期计算IC
            ic_by_date = df_valid.groupby('日期').apply(
                lambda x: x[factor].corr(x['future_return'])
            )
            
            ic_mean = ic_by_date.mean()
            ic_std = ic_by_date.std()
            icir = ic_mean / ic_std if ic_std > 0 else 0
            ic_positive_rate = (ic_by_date > 0).mean()
            
            ic_results[factor] = {
                'IC均值': ic_mean,
                'IC标准差': ic_std,
                'ICIR': icir,
                'IC胜率': ic_positive_rate
            }
            
            logger.info(f"\n  {factor}:")
            logger.info(f"    IC均值: {ic_mean:.4f}")
            logger.info(f"    IC标准差: {ic_std:.4f}")
            logger.info(f"    ICIR: {icir:.4f}")
            logger.info(f"    IC胜率: {ic_positive_rate:.2%}")
        
        # 分层回测
        logger.info("\n" + "-" * 70)
        logger.info("分层回测 (以动量因子为例)")
        logger.info("-" * 70)
        
        # 按因子值分10组
        df_valid['momentum_group'] = df_valid.groupby('日期')['momentum_20'].transform(
            lambda x: pd.qcut(x, 10, labels=False, duplicates='drop')
        )
        
        # 计算各组收益
        group_returns = df_valid.groupby('momentum_group')['future_return'].mean()
        
        logger.info("\n各组平均收益:")
        for group, ret in group_returns.items():
            logger.info(f"  组 {int(group)+1:2d}: {ret:.4%}")
        
        # 多空组合收益
        if len(group_returns) >= 2:
            long_short_return = group_returns.iloc[-1] - group_returns.iloc[0]
            logger.info(f"\n多空组合收益: {long_short_return:.4%}")
        
        # 保存结果
        results = {
            'ic_results': ic_results,
            'group_returns': group_returns.to_dict()
        }
        
        import json
        output_file = "./results/simple_backtest_results.json"
        os.makedirs("./results", exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.success(f"\n✓ 回测完成")
        logger.info(f"  结果文件: {output_file}")
        
        return results
        
    except Exception as e:
        logger.error(f"回测失败: {e}")
        import traceback
        traceback.print_exc()


def step5_summary():
    """步骤5: 总结"""
    logger.info("\n" + "=" * 70)
    logger.info("步骤 5: 流程总结")
    logger.info("=" * 70)
    
    logger.info("""
    ✓ 完整流程演示完成！
    
    本演示展示了:
    1. 数据准备和加载
    2. 因子计算 (动量、反转、成交量)
    3. IC 分析
    4. 分层回测
    5. 多空组合收益
    
    生成的文件:
    - data/csi300_data.csv          # 原始数据
    - data/factors_simple.csv       # 因子数据
    - results/simple_backtest_results.json  # 回测结果
    
    下一步:
    
    方法A: 继续使用简单方法
      - 优点: 不依赖 Qlib，容易理解和修改
      - 缺点: 功能有限，需要自己实现更多功能
      
    方法B: 使用完整的 Qlib 框架
      1. 下载 Qlib 官方数据:
         python -m qlib.run.get_data qlib_data --target_dir ./data/qlib_data --region cn
         
      2. 运行完整回测:
         python scripts/run_backtest.py single momentum_20 --plot
         
      3. 使用 Jupyter Notebook:
         jupyter notebook quickstart.ipynb
    
    推荐资源:
    - Qlib 文档: https://qlib.readthedocs.io/
    - AKShare 文档: https://akshare.akfamily.xyz/
    - 因子分析教程: 参见 docs/ 目录
    """)


def main():
    """主函数"""
    logger.info("""
    ╔══════════════════════════════════════════════════════════════════════╗
    ║           Alpha 因子回测框架 - 完整流程演示                        ║
    ╚══════════════════════════════════════════════════════════════════════╝
    
    本脚本将演示完整的因子回测流程:
    1. 数据准备
    2. 因子计算
    3. IC 分析
    4. 分层回测
    5. 结果输出
    
    """)
    
    try:
        # 步骤1: 准备数据
        if not step1_prepare_data():
            logger.error("数据准备失败，终止流程")
            logger.info("\n请先运行:")
            logger.info("  python scripts/download_data_fixed.py --source akshare --market csi300")
            return
        
        # 步骤2: 数据格式说明
        step2_convert_to_qlib()
        
        # 步骤3: 因子计算
        factor_df = step3_simple_factor_calculation()
        if factor_df is None:
            return
        
        # 步骤4: 简单回测
        results = step4_simple_backtest()
        if results is None:
            return
        
        # 步骤5: 总结
        step5_summary()
        
        logger.success("\n" + "=" * 70)
        logger.success("✓ 全部流程执行完成！")
        logger.success("=" * 70)
        
    except KeyboardInterrupt:
        logger.warning("\n用户中断")
    except Exception as e:
        logger.error(f"\n执行失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
