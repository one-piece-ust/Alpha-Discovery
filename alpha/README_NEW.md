# Alpha 因子回测框架 - 完整流程已运行成功！ ✅

> 基于 Qlib 的量化因子研究与回测平台

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)]()
[![Status](https://img.shields.io/badge/status-✅%20Working-success)]()
[![Last Run](https://img.shields.io/badge/last_run-2026--01--15-green)]()

---

## 🎉 项目状态

**✅ 完整流程已成功运行！**

- ✅ 数据下载成功 (30只股票，2年数据)
- ✅ 因子计算完成 (动量、反转、成交量)
- ✅ IC分析完成
- ✅ 分层回测完成
- ✅ 报告生成完成

📊 **最新结果**: 详见 [`EXECUTION_REPORT.md`](./EXECUTION_REPORT.md)

---

## 🚀 快速开始 (仅需3步)

### 步骤1: 下载数据

```bash
python scripts/download_data_fixed.py --source akshare --market csi300
```

### 步骤2: 运行演示

```bash
python demo_complete_workflow.py
```

### 步骤3: 查看结果

```bash
cat EXECUTION_REPORT.md
```

**就是这么简单！** ✨

---

## 📊 最新运行结果

**执行时间**: 2026-01-15 16:19  
**数据规模**: 30只股票 × 2年 = 14,520条记录

### IC分析结果

| 因子 | IC均值 | ICIR | IC胜率 | 评价 |
|------|--------|------|--------|------|
| momentum_20 | 0.0040 | 0.0137 | 52.27% | 较弱 |
| reversal_1 | -0.0051 | -0.0180 | 49.46% | 反向弱 |
| volume_ratio | 0.0067 | 0.0257 | 50.97% | 较弱 |

### 分层回测 (动量因子)

- **多空组合收益**: 0.0890%
- **最佳组**: 组6 (0.0822%)
- **最差组**: 组1 (-0.0510%)

📖 **完整报告**: [`EXECUTION_REPORT.md`](./EXECUTION_REPORT.md)

---

## 📁 项目结构

```
alpha/
├── demo_complete_workflow.py        ⭐ 一键运行完整流程
├── EXECUTION_REPORT.md              📊 最新运行报告
├── PROJECT_STATUS.md                📋 项目状态说明
├── USAGE_GUIDE.md                   📖 详细使用指南
│
├── scripts/
│   ├── download_data_fixed.py       ⭐ 数据下载 (推荐)
│   └── run_backtest.py              (需要Qlib官方数据)
│
├── data/
│   ├── csi300_data.csv             ✅ 原始数据
│   └── factors_simple.csv          ✅ 因子数据
│
├── results/
│   └── simple_backtest_results.json ✅ 回测结果
│
├── backtest/                        回测模块
├── factors/                         因子库
└── utils/                           工具模块
```

---

## 💡 主要功能

### ✅ 数据获取
- **AKShare**: 免费、无需注册 (推荐)
- **Tushare**: 需要Token，功能更全
- **Qlib**: 官方数据，质量最高

### ✅ 因子研究
- 动量因子 (momentum)
- 反转因子 (reversal)
- 成交量因子 (volume)
- 支持自定义因子

### ✅ 回测分析
- IC (Information Coefficient) 分析
- ICIR (IC Information Ratio)
- IC胜率统计
- 10组分层回测
- 多空组合收益

### ✅ 结果输出
- JSON格式回测结果
- Markdown格式详细报告
- 完整的执行日志

---

## 📖 文档指南

| 文档 | 说明 | 何时查看 |
|------|------|----------|
| **README.md** (本文件) | 项目概览和快速开始 | 第一次使用 |
| **[EXECUTION_REPORT.md](./EXECUTION_REPORT.md)** | 最新运行的详细报告 | 查看运行结果 |
| **[PROJECT_STATUS.md](./PROJECT_STATUS.md)** | 项目当前状态 | 了解项目进展 |
| **[USAGE_GUIDE.md](./USAGE_GUIDE.md)** | 详细使用指南 | 深入学习 |
| **[QUICKSTART.md](./QUICKSTART.md)** | 快速入门教程 | 快速上手 |

---

## 🛠️ 安装

### 环境要求
- Python 3.8+
- pandas, numpy, scipy
- akshare (数据下载)
- loguru (日志)

### 快速安装

```bash
# 使用安装脚本
bash install.sh

# 或手动安装
pip install -r requirements.txt
```

---

## 📚 使用示例

### 示例1: 完整演示 (推荐新手)

```bash
# 一键运行完整流程
python demo_complete_workflow.py
```

输出:
- ✅ 数据检查
- ✅ 因子计算 (动量、反转、成交量)
- ✅ IC分析
- ✅ 分层回测
- ✅ 生成报告

### 示例2: 下载更多数据

```bash
# 下载全部300只股票
python scripts/download_data_fixed.py \
  --source akshare \
  --market csi300 \
  --full

# 指定时间范围
python scripts/download_data_fixed.py \
  --source akshare \
  --market csi300 \
  --start 2018-01-01 \
  --end 2024-12-31
```

### 示例3: 查看不同格式的结果

```bash
# 查看Markdown报告
cat EXECUTION_REPORT.md

# 查看JSON数据
cat results/simple_backtest_results.json | python -m json.tool

# 查看因子数据
head -20 data/factors_simple.csv
```

### 示例4: Python代码自定义

```python
import pandas as pd

# 加载数据
df = pd.read_csv('data/csi300_data.csv')

# 计算自定义因子
df['my_factor'] = df.groupby('code')['收盘'].pct_change(10)

# 进行分析...
```

---

## 🎯 下一步建议

### 1. 扩大数据集

```bash
python scripts/download_data_fixed.py --source akshare --market csi300 --full
```

**好处**:
- 更多样本提高统计显著性
- 更长周期验证因子稳定性

### 2. 优化因子设计

尝试:
- **复合因子**: momentum × volume_ratio
- **行业中性**: 减去行业均值
- **非线性变换**: 排名、对数等

### 3. 使用 Qlib 完整功能

```bash
# 下载 Qlib 官方数据
python -m qlib.run.get_data qlib_data --target_dir ./data/qlib_data --region cn

# 运行 Qlib 回测
python scripts/run_backtest.py single momentum_20 --plot
```

### 4. Jupyter Notebook 交互式分析

```bash
jupyter notebook quickstart.ipynb
```

---

## ❓ 常见问题

### Q: 如何快速查看结果？

```bash
python demo_complete_workflow.py
cat EXECUTION_REPORT.md
```

### Q: 为什么 IC 值很低？

**可能原因**:
1. 样本量较小 (仅30只股票)
2. 因子设计过于简单
3. 需要行业中性化

**解决方案**:
- 使用 `--full` 下载更多股票
- 尝试复合因子
- 添加控制变量

### Q: run_backtest.py 报错怎么办？

该脚本需要 Qlib 官方数据。

**推荐方案**:
```bash
# 使用不依赖 Qlib 的演示脚本
python demo_complete_workflow.py
```

**或下载 Qlib 数据**:
```bash
python -m qlib.run.get_data qlib_data --target_dir ./data/qlib_data --region cn
```

### Q: 如何添加自定义因子？

编辑 `demo_complete_workflow.py` 的因子计算部分:

```python
# 添加你的因子
df['my_factor'] = df.groupby('code')['收盘'].pct_change(30)
```

---

## 📞 获取帮助

- 📖 **详细文档**: [`USAGE_GUIDE.md`](./USAGE_GUIDE.md)
- 📊 **运行报告**: [`EXECUTION_REPORT.md`](./EXECUTION_REPORT.md)
- 📋 **项目状态**: [`PROJECT_STATUS.md`](./PROJECT_STATUS.md)
- 🚀 **快速开始**: [`QUICKSTART.md`](./QUICKSTART.md)

---

## 🎯 核心优势

### ✅ 开箱即用
- 一键运行，无需复杂配置
- 自动生成详细报告
- 完整的示例代码

### ✅ 易于理解
- 清晰的代码结构
- 详细的中文注释
- 丰富的文档说明

### ✅ 便于扩展
- 模块化设计
- 支持自定义因子
- 灵活的数据源

### ✅ 生产就绪
- 完整的错误处理
- 详细的日志记录
- 标准化的输出格式

---

## 📊 技术栈

- **数据源**: AKShare / Tushare / Qlib
- **计算框架**: pandas / numpy
- **回测引擎**: 自研 + Qlib
- **日志**: loguru
- **报告**: Markdown / JSON

---

## 🎉 立即开始

```bash
# 1. 下载数据
python scripts/download_data_fixed.py --source akshare --market csi300

# 2. 运行演示
python demo_complete_workflow.py

# 3. 查看结果
cat EXECUTION_REPORT.md
```

**就是这么简单！开始你的量化研究之旅吧！** 🚀

---

## 📜 更新日志

### 2026-01-15
- ✅ 完整流程测试通过
- ✅ 生成执行报告
- ✅ 更新所有文档
- ✅ 数据下载脚本修复

### 2026-01-13
- ✅ 项目初始化
- ✅ 基础框架搭建
- ✅ 文档编写

---

*Generated by Alpha Factor Backtest Framework*  
*Last Updated: 2026-01-15*
