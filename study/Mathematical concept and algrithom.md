## 1. **OpenFE**

# 1. Gradient Boosting Decision Trees (GBDT) & LightGBM
**Context:** Used extensively in **OpenFE** and **OpenFE++** as the base learner for evaluation and for extracting feature interactions.

**Description:**
Gradient Boosting Decision Trees (GBDT) is an ensemble learning technique that builds a model in a stage-wise fashion. It constructs new decision trees to predict the residuals (errors) of the prior trees.
**LightGBM** is a specific, highly efficient implementation of GBDT that uses histogram-based algorithms and leaf-wise growth strategies.

**Key Applications in the Papers:**
*   **Performance Evaluation:** In **OpenFE**, a GBDT model is trained to evaluate the incremental performance gain ($\Delta$) of a new candidate feature (Algorithm 2: FeatureBoost).
*   **Feature Importance (MDI):** **OpenFE** uses Mean Decrease in Impurity (MDI). When a tree splits a node based on a feature, the impurity (e.g., variance or Gini index) decreases. The sum of these decreases across all trees indicates the feature's importance.
*   **Interaction Strength:** **OpenFE++** measures feature interaction by analyzing the co-occurrence of features in tree paths. If two features frequently appear on the same path in a decision tree, they are considered to have a strong interaction.

**Source:** *OpenFE (Section 3.3, 3.2.1), OpenFE++ (Section 4.1, 4.2)*

# 2. Successive Halving (Multi-Armed Bandit)
**Context:** Used in **OpenFE** for the "Successive Featurewise Pruning" stage.

**Description:**
Successive Halving is an algorithm derived from the Multi-Armed Bandit problem. It is used to efficiently allocate computational resources to the most promising candidates among a large set.

**Process:**
1.  Start with a large pool of candidate features and small subsets of data.
2.  Evaluate all candidates on the small data subset.
3.  Discard the worst-performing half of the candidates.
4.  Double the data size and repeat the process with the remaining candidates until only the best features remain.

**Mathematical Intuition:**
It relies on the assumption that a feature performing poorly on a small dataset is unlikely to be the best feature on the full dataset, allowing for early pruning.

**Source:** *OpenFE (Section 3.2.2, Algorithm 3)*

# 3. Rademacher Complexity
**Context:** Used in the theoretical analysis of **OpenFE** to prove the generalization bounds of generated features.

**Description:**
Rademacher Complexity measures the richness or capacity of a class of functions (hypothesis class). It quantifies the ability of a model to fit random noise.

**Theoretical Insight:**
The paper proves that utilizing feature generation (specifically aggregation operations like `GroupByThenMean`) reduces the generalization error bound compared to using raw features alone. They define a "Group Rademacher Complexity" to handle the dependency between data points within the same group (e.g., transactions by the same user).

**Formula Concept:**
$$ Rad_k(\mathcal{F}) = \mathbb{E} \left[ \sup_{f \in \mathcal{F}} \frac{1}{k} \sum_{i=1}^{k} \sigma_i L(H, f, X_i, Y_i) \right] $$
Where $\sigma_i$ are independent Rademacher variables (taking values +1 or -1 with probability 0.5).

**Source:** *OpenFE (Section 4, Appendix A)*

## 2. **OpenFE++**

# 1. Interaction Strength (Friedman's H-statistic variant)
**Context:** Used in **OpenFE++** to prune the search space.

**Description:**
Instead of brute-force enumerating all feature combinations ($x_i \times x_j$), OpenFE++ first estimates which features *interact* strongly.
It uses a trained tree model. The interaction strength between two features is measured by the frequency with which they appear on the *same path* (from root to leaf) in the decision trees.

**Logic:**
If feature $A$ and feature $B$ appear on the same branch often, it implies the optimal prediction depends on the values of both $A$ and $B$ conditionally (non-linear interaction).

**Source:** *OpenFE++ (Section 4.1, 4.2)*

# 2. Wiener-Khinchin Theorem & Fast Fourier Transform (FFT)
**Context:** Used in **OpenFE++** to efficiently generate time-series features by identifying lagged effects and periodicity.

**Description:**
*   **Fast Fourier Transform (FFT):** An algorithm that computes the Discrete Fourier Transform (DFT) of a sequence. It converts a signal from the time domain into the frequency domain. **OpenFE++** uses this to identify the $K$ most dominant frequencies (periodicity) in time-series data.
*   **Wiener-Khinchin Theorem:** This theorem states that the autocorrelation function of a wide-sense stationary random process can be computed using the power spectral density.

**Application in OpenFE++:**
Instead of calculating correlation for every possible lag (brute force $O(N^2)$), OpenFE++ uses the theorem to compute convolution via FFT in the frequency domain. This allows them to calculate the lagged effects for all time gaps simultaneously in $O(L \log L)$ time complexity.

**Formula:**
$$ \{Q^{(i,j)}_t(T)\}_{T=0}^{L-1} = \frac{1}{L} \mathcal{F}^{-1} \left( \mathcal{F}\left(x^{(j)}\right) \odot \overline{\mathcal{F}\left(x^{(i)}\right)} \right) $$
Where $\mathcal{F}$ is FFT, $\mathcal{F}^{-1}$ is inverse FFT, and $\odot$ is element-wise product.

**Source:** *OpenFE++ (Section 4.3, Eq. 4.5)*


## 3. **AlphaEvolve**
# 1. Evolutionary Algorithms (Genetic Algorithms)
**Context:** The core search engine for **AlphaEvolve**.

**Description:**
Evolutionary Algorithms (EA) are heuristic search methods inspired by natural selection. They maintain a population of candidate solutions (in this case, "Alphas" or trading signals).

**Key Components:**
1.  **Population:** A set of candidate alphas (represented as expression trees or computational graphs).
2.  **Fitness Function:** A metric used to evaluate how good an alpha is (e.g., Information Coefficient or Sharpe Ratio).
3.  **Selection (Tournament Selection):** A mechanism where a subset of individuals is chosen at random, and the best among them is selected to be a parent.
4.  **Mutation:** Random alterations to an alpha. **AlphaEvolve** uses:
    *   *Point Mutation:* Changing an operator (e.g., `+` to `-`).
    *   *Subtree Mutation:* Replacing a part of the expression tree with a new random subtree.
    *   *Hoist Mutation:* Replacing the tree with one of its subtrees.

**Source:** *AlphaEvolve (Section 3, Figure 3)*

# 2. Information Coefficient (IC) & Sharpe Ratio
**Context:** The objective functions (fitness scores) used in **AlphaEvolve** to evaluate stock prediction models.

**Information Coefficient (IC):**
The Pearson Correlation coefficient between the predicted stock returns and the actual future returns. It measures the predictive power of a factor.
$$ IC = \frac{1}{N} \sum_{t=1}^{N} corr(\hat{y}_t, y_t) $$
Where $\hat{y}$ is the predicted signal and $y$ is the true return.

**Sharpe Ratio:**
A measure of risk-adjusted return. It describes how much excess return you receive for the extra volatility that you endure for holding a risky asset.
$$ SR = \frac{R_p - R_f}{\sigma_p} $$
*   $R_p$: Portfolio return.
*   $R_f$: Risk-free rate.
*   $\sigma_p$: Standard deviation (volatility) of the portfolio return.

**Source:** *AlphaEvolve (Section 4.1 Eq. 1, Section 5.3)*
