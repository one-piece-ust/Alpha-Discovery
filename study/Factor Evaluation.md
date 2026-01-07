# Factor Evaluation



## IC



### Intro to IC

**IC (Information Coefficient)** is a cross-sectional correlation computed at each time \(t\) between a factor’s current values and **future returns**:

- At time \(t\), every asset \(i\) has a factor exposure \(f_{i,t}\).
- We look forward and compute the realized return \(R_{i,\,t+\delta\rightarrow t+\delta+h}\).
- We then compute a cross-sectional correlation across assets \(i\).

If a factor has **predictive power**, assets with **higher** (or **lower**) factor values at time \(t\) should systematically realize **higher** (or **lower**) returns over the forward window. That means the cross-sectional association between \(\{f_{i,t}\}\) and \(\{R_{i,\cdot}\}\) will be consistently positive or negative, producing IC values with a non-zero mean over time. Conversely, if the factor has no forecasting ability, the relationship should look like noise and IC should fluctuate around zero.



### Pearson IC vs. Spearman (Rank) IC

**Pearson IC** measures the **linear** relationship between a factor and future returns in the cross-section at each time \(t\):
$$
IC_t = \mathrm{corr}_i\!\left( f_{i,t},\; R_{i,\,t+\delta \rightarrow t+\delta+h} \right)
$$

- \(IC_t\) is the (cross-sectional) Information Coefficient at time \(t\).
- \(\mathrm{corr}_i(\cdot)\) means the correlation is computed **across assets \(i\)** (i.e., across the cross-section at the same time \(t\)).
- \(f_{i,t}\) is the factor value (exposure) for asset \(i\) observed at time \(t\).
- \(R_{i,\,t+\delta \rightarrow t+\delta+h}\) is the **forward return** of asset \(i\) measured from time \(t+\delta\) to time \(t+\delta+h\),
  where:
  - \(\delta\) is the signal/implementation delay (e.g., compute + order + fill latency),
  - \(h\) is the prediction horizon (holding period length).
- Intuition: \(IC_t\) measures how well the factor values at time \(t\) align with the ranking (or linear relationship, depending on the correlation type) of future returns over the chosen forward window.

**Spearman IC (Rank IC)** measures the relationship after converting both variables to **ranks**, so it focuses on **monotonic** (order-preserving) association:
$$
IC_t^{(S)}=\mathrm{corr}_i\!\left(\mathrm{rank}(f_{i,t}),\;\mathrm{rank}(R_{i,\,t+\delta\rightarrow t+\delta+h})\right)
$$
- Uses ranks, so it cares about whether **higher factor → higher (or lower) future return**, not strict linearity.
- More **robust to outliers**.
- Often preferred when the signal is mainly about **sorting/ordering** assets.



### Example (Funding Rate Factor)

We take a single timestamp \(t\) (same moment for all coins) and evaluate whether a factor measured at \(t\) predicts **forward returns** over the next hour.

- **Factor**: current **funding rate** \(f_{i,t}\)  
  (Higher funding often means longs are crowded; a common hypothesis is short-term mean reversion, so we may expect a **negative** IC.)
- **Forward return window**: from \(t+1\text{m}\) to \(t+1\text{h}+1\text{m}\)

### Cross-sectional sample data (same time \(t\), multiple coins)

| Coin | \(f_{i,t}\) funding (%) | \(R_{i,\,t+1m\rightarrow t+1h+1m}\) next-hour return |
| ---- | ----------------------: | ---------------------------------------------------: |
| BTC  |                   0.012 |                                               +0.10% |
| ETH  |                   0.020 |                                               +0.08% |
| XRP  |                   0.030 |                                               -0.10% |
| SOL  |                   0.055 |                                               -0.20% |
| DOGE |                   0.080 |                                               -1.50% |

**Intuition:** higher funding \(\Rightarrow\) worse next-hour return \(\Rightarrow\) expect **negative** IC.

---

#### Pearson IC (linear correlation)

Pearson IC is the cross-sectional **linear** correlation between factor values and forward returns:

$$
IC_t^{(P)}=\mathrm{corr}_i\!\left(f_{i,t},\;R_{i,\,t+\delta\rightarrow t+\delta+h}\right)
$$

For this toy cross-section (5 points):

- **Pearson IC \(\approx -0.903\)**

**Interpretation:** in a linear sense, higher funding is associated with lower future returns, strongly negative but not perfectly linear.

---

#### Spearman IC / Rank IC (rank correlation)

Spearman IC (Rank IC) converts both columns to **ranks** first, then computes correlation:

$$
IC_t^{(S)}=\mathrm{corr}_i\!\left(\mathrm{rank}(f_{i,t}),\;\mathrm{rank}(R_{i,\cdot})\right)
$$

Ranks (small = 1, large = 5; returns ranked from low to high):

| Coin | rank(funding) | rank(return) |
| ---- | ------------: | -----------: |
| BTC  |             1 |            5 |
| ETH  |             2 |            4 |
| XRP  |             3 |            3 |
| SOL  |             4 |            2 |
| DOGE |             5 |            1 |

The ordering is perfectly reversed (higher funding \(\Rightarrow\) lower return), so:

- **Spearman / Rank IC = -1.000** (perfect negative monotonic relationship)

---

#### Why Pearson and Spearman can differ

DOGE has an extreme return (-1.50%), which can strongly affect **Pearson** (outlier-sensitive) and pull it away from \(-1\).  
**Spearman** uses ranks, so as long as the ordering is perfectly monotonic, it remains \(-1\).

---

#### How this is used in practice

You don’t compute IC only once. You compute \(IC_t\) for every bar (e.g., every hour) to form an IC time series \(\{IC_t\}\), then evaluate:

- Mean IC (does it consistently deviate from 0?)
- IC volatility / ICIR (is it stable?)
- Quantile (group) returns: Top funding vs Bottom funding, monotonicity, tradability with fees/slippage



### Real-World Example (Twitter Factor)

We got over 100000 tweets from https://github.com/JupiterXiaoxiaoYu/twitter_data_getter during 2025-05-01 to 2025-05-31

Then we generated sentiment score using sft bert model for each tweets

For each minute we got an average score, like this list, we got close price from binance, and calculated average sentiment during this minute

| time                      | close     | avg_sen      |
| ------------------------- | --------- | ------------ |
| 2025-05-01 00:00:00+00:00 | 94147.3   | 0.338707868  |
| 2025-05-01 00:01:00+00:00 | 94187.02  | 0.260627352  |
| 2025-05-01 00:02:00+00:00 | 94198.75  | 0.309769669  |
| 2025-05-01 00:03:00+00:00 | 94169.45  | 0.551348449  |
| 2025-05-01 00:04:00+00:00 | 94238.09  | 0.384302549  |
| 2025-05-01 00:05:00+00:00 | 94221.4   | -0.05904488  |
| 2025-05-01 00:06:00+00:00 | 94231.71  | 0.305721922  |
| 2025-05-01 00:07:00+00:00 | 94248     | 0.114702689  |
| 2025-05-01 00:08:00+00:00 | 94285.71  | 0.056137977  |
| 2025-05-01 00:09:00+00:00 | 94303.99  | 0.265248009  |
| 2025-05-01 00:10:00+00:00 | 94331.04  | -0.058866525 |
| ...                       | ...       | ...          |
| 2025-05-31 23:51:00+00:00 | 104654.77 | -0.080587339 |
| 2025-05-31 23:52:00+00:00 | 104644.3  | -0.15305393  |
| 2025-05-31 23:53:00+00:00 | 104638.62 | -0.323020328 |
| 2025-05-31 23:54:00+00:00 | 104615.68 | 0.226892108  |
| 2025-05-31 23:55:00+00:00 | 104615.67 | 0.27649651   |
| 2025-05-31 23:56:00+00:00 | 104610.09 | -0.062401101 |
| 2025-05-31 23:57:00+00:00 | 104585    | 0.172323186  |
| 2025-05-31 23:58:00+00:00 | 104595.95 | 0.428677825  |
| 2025-05-31 23:59:00+00:00 | 104591.88 | -0.113140269 |

Then, we calculated several average IC score. For example, 30 min window with mean method, we first calculated average sentiment in this 30 minutes(like 2025-05-01 00:00 - 2025-05-01 00:30), and calculated 

\(corr\) with next 30 minutes (like 2025-05-01 00:30 - 2025-05-01 01:00), here we set \(\delta\) to zero, but this is not rigorous. And got IC results(Pearson IC)

| Window  | Minutes | Sentiment method (CN) | Sentiment method (EN) | Key            |                     IC |
| ------- | ------: | --------------------- | --------------------- | -------------- | ---------------------: |
| 30 min  |      30 | 均值                  | Mean                  | mean           |   -0.03522490010357632 |
| 30 min  |      30 | 中位数                | Median                | median         |   -0.05070706143676836 |
| 30 min  |      30 | 最大值                | Maximum               | max            |   -0.04374780640209397 |
| 30 min  |      30 | 最小值                | Minimum               | min            |  -0.002279024957751452 |
| 30 min  |      30 | 极差(最大-最小)       | Range (max − min)     | range          |  -0.022409712858946787 |
| 30 min  |      30 | 标准差                | Standard deviation    | std            |  -0.016108480060523584 |
| 30 min  |      30 | 绝对值均值            | Mean absolute value   | abs_mean       |  -0.039240044404393305 |
| 30 min  |      30 | 正向比例              | Positive ratio        | positive_ratio |  -0.017789279140512516 |
| 30 min  |      30 | 偏度(skew)            | Skewness              | skew           |   0.025428687263111663 |
| 30 min  |      30 | 峰度(kurtosis)        | Kurtosis              | kurtosis       |   -0.03308331246090556 |
| 1 hour  |      60 | 均值                  | Mean                  | mean           |  -0.014310695565440448 |
| 1 hour  |      60 | 中位数                | Median                | median         |  -0.021266102860569312 |
| 1 hour  |      60 | 最大值                | Maximum               | max            |   -0.06019936860587907 |
| 1 hour  |      60 | 最小值                | Minimum               | min            |    0.02592650693494805 |
| 1 hour  |      60 | 极差(最大-最小)       | Range (max − min)     | range          |   -0.05040581852312238 |
| 1 hour  |      60 | 标准差                | Standard deviation    | std            |  -0.026669114801147916 |
| 1 hour  |      60 | 绝对值均值            | Mean absolute value   | abs_mean       |  -0.016986671223605244 |
| 1 hour  |      60 | 正向比例              | Positive ratio        | positive_ratio |  0.0053038127202037644 |
| 1 hour  |      60 | 偏度(skew)            | Skewness              | skew           |  -0.008964667492947838 |
| 1 hour  |      60 | 峰度(kurtosis)        | Kurtosis              | kurtosis       |   -0.09404042907875362 |
| 2 hours |     120 | 均值                  | Mean                  | mean           |   -0.04499493449542747 |
| 2 hours |     120 | 中位数                | Median                | median         |   -0.04435953058263174 |
| 2 hours |     120 | 最大值                | Maximum               | max            |    -0.0560925233839451 |
| 2 hours |     120 | 最小值                | Minimum               | min            | -0.0028981829232749903 |
| 2 hours |     120 | 极差(最大-最小)       | Range (max − min)     | range          |  -0.025959178428747322 |
| 2 hours |     120 | 标准差                | Standard deviation    | std            |  -0.040673510769991754 |
| 2 hours |     120 | 绝对值均值            | Mean absolute value   | abs_mean       |   -0.04506485363548281 |
| 2 hours |     120 | 正向比例              | Positive ratio        | positive_ratio |  -0.010702283631482803 |
| 2 hours |     120 | 偏度(skew)            | Skewness              | skew           |  -0.032027246714863476 |
| 2 hours |     120 | 峰度(kurtosis)        | Kurtosis              | kurtosis       |  -0.012995071202814448 |



## Factor Decay