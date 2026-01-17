"""
数据下载脚本 - 修复版

支持多种数据源下载 A 股市场数据
"""

import argparse
import sys
import os
from pathlib import Path


def show_guide():
    """显示使用指南"""
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                    数据下载工具 - 使用指南                          ║
╚══════════════════════════════════════════════════════════════════════╝

【问题诊断】
原始脚本导入了不存在的 qlib 模块: dataset_cache
这个模块在新版 qlib 中已被移除或改名。

【解决方案】
支持3种数据源:

1. AKShare (推荐，免费，无需注册) ⭐
   pip install akshare
   python scripts/download_data_fixed.py --source akshare

2. Tushare (需要注册，功能更全面)
   pip install tushare
   python scripts/download_data_fixed.py --source tushare --token YOUR_TOKEN

3. Qlib 官方数据 (最完整)
   python -m qlib.run.get_data qlib_data --target_dir ./data/qlib_data --region cn

【快速开始】
# 安装 akshare
pip install akshare

# 下载沪深300最近1年数据（示例：前30只股票）
python scripts/download_data_fixed.py --source akshare --market csi300

【参数说明】
--source    数据源: akshare, tushare, qlib
--market    市场: csi300 (沪深300), csi500 (中证500)
--start     开始日期，默认: 2023-01-01
--end       结束日期，默认: 2023-12-31
--token     Tushare Token (仅 tushare 需要)
--data-dir  数据保存目录，默认: ./data
--full      下载所有股票（默认只下载前10只作示例）

【更多信息】
AKShare: https://akshare.akfamily.xyz/
Tushare: https://tushare.pro/
Qlib:    https://github.com/microsoft/qlib

╚══════════════════════════════════════════════════════════════════════╝
    """)


def download_akshare(market, start_date, end_date, data_dir, full=False):
    """使用 AKShare 下载数据"""
    try:
        import akshare as ak
        import pandas as pd
        from loguru import logger
        
        logger.info(f"使用 AKShare 下载 {market} 数据...")
        logger.info(f"时间范围: {start_date} 至 {end_date}")
        
        # 创建数据目录
        os.makedirs(data_dir, exist_ok=True)
        
        # 获取股票列表
        if market == "csi300":
            logger.info("获取沪深300成分股...")
            stock_list_df = ak.index_stock_cons_csindex(symbol="000300")
            stock_codes = stock_list_df['成分券代码'].tolist()
        elif market == "csi500":
            logger.info("获取中证500成分股...")
            stock_list_df = ak.index_stock_cons_csindex(symbol="000905")
            stock_codes = stock_list_df['成分券代码'].tolist()
        else:
            logger.error("不支持的市场类型")
            return
        
        # 限制数量
        if not full:
            stock_codes = stock_codes[:30]
            logger.info(f"示例模式: 仅下载前30只股票（使用 --full 下载全部 {len(stock_list_df)} 只）")
        else:
            logger.info(f"完整模式: 下载全部 {len(stock_codes)} 只股票")
        
        # 下载数据
        all_data = []
        success_count = 0
        
        for i, code in enumerate(stock_codes, 1):
            try:
                logger.info(f"[{i}/{len(stock_codes)}] 下载 {code}...")
                
                df = ak.stock_zh_a_hist(
                    symbol=code,
                    period="daily",
                    start_date=start_date.replace('-', ''),
                    end_date=end_date.replace('-', ''),
                    adjust="qfq"
                )
                
                if df is not None and not df.empty:
                    df['code'] = code
                    all_data.append(df)
                    success_count += 1
                    
            except Exception as e:
                logger.warning(f"下载 {code} 失败: {e}")
                continue
        
        # 保存数据
        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            output_file = os.path.join(data_dir, f"{market}_data.csv")
            combined_df.to_csv(output_file, index=False, encoding='utf-8-sig')
            
            logger.success(f"✓ 数据已保存到: {output_file}")
            logger.info(f"  成功下载: {success_count}/{len(stock_codes)} 只股票")
            logger.info(f"  总记录数: {len(combined_df)} 条")
            logger.info(f"  数据列: {', '.join(combined_df.columns.tolist())}")
        else:
            logger.error("未能下载任何数据")
            
    except ImportError:
        print("\n❌ AKShare 未安装")
        print("请运行: pip install akshare")
        print("文档: https://akshare.akfamily.xyz/installation.html")
    except Exception as e:
        print(f"\n❌ 下载失败: {e}")
        import traceback
        traceback.print_exc()


def download_tushare(market, start_date, end_date, data_dir, token, full=False):
    """使用 Tushare 下载数据"""
    if not token:
        print("""
        ❌ Tushare 需要 Token
        
        1. 注册账号: https://tushare.pro/register
        2. 获取 Token: https://tushare.pro/user/token
        3. 使用:
           python scripts/download_data_fixed.py --source tushare --token YOUR_TOKEN
        """)
        return
    
    try:
        import tushare as ts
        import pandas as pd
        from loguru import logger
        
        ts.set_token(token)
        pro = ts.pro_api()
        
        logger.info(f"使用 Tushare 下载 {market} 数据...")
        
        # 创建数据目录
        os.makedirs(data_dir, exist_ok=True)
        
        # 获取指数成分股
        index_code = "000300.SH" if market == "csi300" else "000905.SH"
        
        logger.info(f"获取 {index_code} 成分股...")
        df_stocks = pro.index_weight(index_code=index_code)
        stock_codes = df_stocks['con_code'].unique().tolist()
        
        if not full:
            stock_codes = stock_codes[:30]
            logger.info(f"示例模式: 仅下载前30只股票")
        
        # 下载数据
        all_data = []
        for i, code in enumerate(stock_codes, 1):
            try:
                logger.info(f"[{i}/{len(stock_codes)}] 下载 {code}...")
                
                df = pro.daily(
                    ts_code=code,
                    start_date=start_date.replace('-', ''),
                    end_date=end_date.replace('-', '')
                )
                
                if df is not None and not df.empty:
                    all_data.append(df)
                    
            except Exception as e:
                logger.warning(f"下载 {code} 失败: {e}")
                continue
        
        # 保存数据
        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            output_file = os.path.join(data_dir, f"{market}_data.csv")
            combined_df.to_csv(output_file, index=False, encoding='utf-8-sig')
            logger.success(f"✓ 数据已保存到: {output_file}")
        else:
            logger.error("未能下载任何数据")
            
    except ImportError:
        print("\n❌ Tushare 未安装")
        print("请运行: pip install tushare")
    except Exception as e:
        print(f"\n❌ 下载失败: {e}")


def download_qlib(market, data_dir):
    """显示 Qlib 官方下载说明"""
    print(f"""
    ============================================================
    Qlib 官方数据下载
    ============================================================
    
    方法1: 使用命令行工具
    
    python -m qlib.run.get_data qlib_data --target_dir {data_dir}/qlib_data --region cn
    
    方法2: 下载官方脚本
    
    wget https://raw.githubusercontent.com/microsoft/qlib/main/scripts/get_data.py
    python get_data.py qlib_data --target_dir {data_dir}/qlib_data --region cn
    
    数据说明:
      - 包含沪深300/500成分股
      - 时间范围: 2008-01-01 至今
      - 包含价格、成交量、因子等数据
      - 数据格式: Qlib 原生格式
    
    ============================================================
    """)


def main():
    parser = argparse.ArgumentParser(
        description="A股数据下载工具",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("--source", type=str, default="akshare",
                       choices=["akshare", "tushare", "qlib"],
                       help="数据源")
    parser.add_argument("--market", type=str, default="csi300",
                       choices=["csi300", "csi500"],
                       help="市场")
    parser.add_argument("--start", type=str, default="2023-01-01",
                       help="开始日期")
    parser.add_argument("--end", type=str, default="2023-12-31",
                       help="结束日期")
    parser.add_argument("--data-dir", type=str, default="./data",
                       help="数据目录")
    parser.add_argument("--token", type=str, default=None,
                       help="Tushare Token")
    parser.add_argument("--full", action="store_true",
                       help="下载全部股票（默认只下载前10只）")
    parser.add_argument("--guide", action="store_true",
                       help="显示使用指南")
    
    args = parser.parse_args()
    
    if args.guide or len(sys.argv) == 1:
        show_guide()
        return
    
    print(f"\n数据源: {args.source}")
    print(f"市场: {args.market}")
    print(f"时间: {args.start} ~ {args.end}")
    print(f"目录: {args.data_dir}\n")
    
    if args.source == "akshare":
        download_akshare(args.market, args.start, args.end, args.data_dir, args.full)
    elif args.source == "tushare":
        download_tushare(args.market, args.start, args.end, args.data_dir, args.token, args.full)
    elif args.source == "qlib":
        download_qlib(args.market, args.data_dir)


if __name__ == "__main__":
    main()
