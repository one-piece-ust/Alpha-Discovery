#!/bin/bash

# Alpha 因子回测框架 - 安装脚本

echo "================================================"
echo "  Alpha 因子回测框架 - 开始安装"
echo "================================================"

# 检查 Python 版本
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "检测到 Python 版本: $python_version"

# 创建必要的目录
echo ""
echo "📁 创建项目目录..."
mkdir -p data/qlib_data
mkdir -p results/reports
mkdir -p results/data
mkdir -p results/plots
mkdir -p logs
mkdir -p cache
mkdir -p notebooks

echo "✅ 目录创建完成"

# 安装依赖
echo ""
echo "📦 安装 Python 依赖..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ 依赖安装成功"
else
    echo "❌ 依赖安装失败，请检查错误信息"
    exit 1
fi

# 提示下载数据
echo ""
echo "================================================"
echo "  安装完成！"
echo "================================================"
echo ""
echo "📋 下一步操作:"
echo ""
echo "1. 下载 Qlib 数据:"
echo "   python scripts/download_data.py"
echo ""
echo "2. 运行快速开始示例:"
echo "   python quickstart.py"
echo ""
echo "3. 或者直接运行回测:"
echo "   python scripts/run_backtest.py single momentum_20"
echo ""
echo "4. 查看可用因子:"
echo "   python scripts/run_backtest.py list"
echo ""
echo "================================================"
echo "  祝使用愉快！"
echo "================================================"
