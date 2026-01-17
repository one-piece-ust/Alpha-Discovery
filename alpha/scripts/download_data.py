"""
数据下载脚本

下载 Qlib 所需的市场数据
"""

import argparse
import qlib
from qlib.data import dataset
from loguru import logger
import sys


def download_data(market: str = "csi300", start_date: str = "2015-01-01", end_date: str = "2023-12-31"):
    """
    下载市场数据
    
    Args:
        market: 市场代码 (csi300, csi500, all)
        start_date: 开始日期
        end_date: 结束日期
    """
    logger.info(f"Downloading {market} data from {start_date} to {end_date}...")
    
    try:
        # 使用 qlib 的数据下载工具
        from qlib.contrib.data.handler import check_transform_proc
        from qlib.data import dataset_cache
        
        # 设置数据存储路径
        qlib_data_path = "./data/qlib_data"
        
        # 初始化
        qlib.init(provider_uri=qlib_data_path, region="cn")
        
        # 下载数据
        logger.info("Downloading from online source...")
        
        # 使用 qlib 提供的数据下载方法
        from qlib.data import dataset_init_cn
        
        # 实际使用时,需要从以下地址下载数据:
        # https://github.com/microsoft/qlib/tree/main/scripts/get_data.py
        
        logger.info("""
        ============================================================
        Qlib 数据下载说明
        ============================================================
        
        方法1: 使用官方脚本下载
        
        ```bash
        # 下载 CSI 300 数据 (2015-2023)
        python scripts/get_data.py qlib_data --target_dir ./data/qlib_data --region cn
        ```
        
        方法2: 从百度网盘下载预处理数据
        
        链接: https://github.com/microsoft/qlib/tree/main/scripts
        
        下载后解压到: ./data/qlib_data/
        
        方法3: 使用 Tushare/AKShare 自己准备数据
        
        可以参考: https://qlib.readthedocs.io/en/latest/component/data.html
        
        ============================================================
        """)
        
    except Exception as e:
        logger.error(f"Failed to download data: {e}")
        logger.info("\n请手动下载数据或使用 Qlib 官方提供的数据下载脚本")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Download Qlib market data")
    parser.add_argument("--market", type=str, default="csi300", 
                       choices=["csi300", "csi500", "all"],
                       help="Market to download")
    parser.add_argument("--start", type=str, default="2015-01-01",
                       help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end", type=str, default="2023-12-31",
                       help="End date (YYYY-MM-DD)")
    
    args = parser.parse_args()
    
    download_data(args.market, args.start, args.end)


if __name__ == "__main__":
    main()
