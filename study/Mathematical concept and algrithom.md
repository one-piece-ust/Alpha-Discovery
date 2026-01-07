## 1. OpenFE
**Full Title:** *Automated Feature Generation with Expert-level Performance*

### 1.1 Gradient Boosting Decision Trees (GBDT) & LightGBM
**Context:** The core estimator used for feature evaluation (FeatureBoost) and importance ranking.
*   **Description:** GBDT constructs an ensemble of weak decision trees in a stage-wise fashion to minimize a loss function. **LightGBM** is an optimized implementation used in the paper for its speed and ability to handle large datasets and categorical features natively.
*   **Application:** In OpenFE, a LightGBM model is trained to fit the residuals of the current prediction, allowing the system to measure the incremental gain of a new candidate feature without retraining the entire model from scratch.

### 1.2 Successive Halving (Multi-Armed Bandit)
**Context:** Used in the "Successive Featurewise Pruning" stage (Algorithm 3).
*   **Description:** An algorithm originally designed for hyperparameter tuning, derived from the Multi-Armed Bandit problem. It efficiently allocates resources to the most promising candidates.
*   **Process:**
    1.  Start with a massive pool of candidate features and a small subset of data.
    2.  Evaluate all candidates.
    3.  Discard the worst-performing half.
    4.  Double the data sample size and repeat until only the best features remain.
*   **Benefit:** It avoids spending computational resources on poor features using the full dataset.

### 1.3 Rademacher Complexity (Generalization Bound)
**Context:** Used in the "Theoretical Advantage" section (Section 4 & Appendix A) to prove why feature generation works.
*   **Description:** A measure of the richness (complexity) of a class of functions. It quantifies a model's ability to fit random noise. The paper introduces **Group Rademacher Complexity** to handle tabular data where rows (e.g., transactions) are grouped by entities (e.g., users).
*   **Mathematical Formulation:**

$$
Rad_k(\mathcal{F}) = \mathbb{E} \left[ \sup_{f \in \mathcal{F}} \frac{1}{k} \sum_{i=1}^{k} \sigma_i L(H, f, X_i, Y_i) \right]
$$

| Symbol | Definition |
| :--- | :--- |
| $\sigma_i$ | Independent Rademacher variables (+1 or -1 with probability 0.5) |
| $L$ | Loss function |
| $H$ | Feature generation function |

## 2. OpenFE++
**Full Title:** *Efficient Automated Feature Generation via Feature Interaction*

### 2.1 Feature Interaction via Tree Path Co-occurrence
**Context:** Used to prune the search space by identifying features that likely interact before generating formulas.
*   **Description:** Instead of brute-force enumerating all combinations ($O(N^2)$), OpenFE++ uses a pre-trained LightGBM model to detect interactions.
*   **Mechanism:** If two features $x_i$ and $x_j$ frequently appear on the **same path** (from root to leaf) in the decision trees, they are considered to have a strong interaction strength. This is based on the logic that the model found a non-linear dependency between them.

### 2.2 Wiener-Khinchin Theorem & Fast Fourier Transform (FFT)
**Context:** Used for "Temporal Feature Generation" to efficiently identify lagged effects in time-series data.
*   **Description:**
    *   **FFT:** Converts time-series data from the time domain to the frequency domain to identify periodic patterns (seasonality).
    *   **Wiener-Khinchin Theorem:** States that the autocorrelation of a stationary process is the inverse Fourier transform of its power spectral density.
*   **Application:** It allows the algorithm to calculate the correlation between two variables at *all* possible time lags simultaneously in $O(L \log L)$ time, rather than $O(L^2)$ via brute force.
*   **Mathematical Formulation:**

$$
\{Q^{(i,j)}_t(T)\}_{T=0}^{L-1} = \frac{1}{L} \mathcal{F}^{-1} \left( \mathcal{F}\left(x^{(j)}\right) \odot \overline{\mathcal{F}\left(x^{(i)}\right)} \right)
$$

| Symbol | Definition |
| :--- | :--- |
| $\mathcal{F}$ | Fast Fourier Transform |
| $\mathcal{F}^{-1}$ | Inverse Fast Fourier Transform |
| $\odot$ | Element-wise product |
| $\overline{\mathcal{F}}$ | Complex conjugate of the Fourier Transform |


## 3. AlphaEvolve
**Full Title:** *A Learning Framework to Discover Novel Alphas in Quantitative Investment*

### 3.1 Evolutionary Algorithms (Genetic Programming)
**Context:** The core search engine used to "evolve" new alpha factors from existing ones.
*   **Description:** A heuristic search algorithm inspired by natural selection.
*   **Key Operations:**
    1.  **Population:** A set of alpha factors represented as expression trees.
    2.  **Mutation:** Randomly changing an operator (e.g., `+` to `-`) or replacing a subtree to create diversity.
    3.  **Crossover:** Combining parts of two "parent" alphas to create a child.
    4.  **Selection:** Keeping the alphas with the highest fitness scores (IC or Sharpe Ratio) for the next generation.

### 3.2 Information Coefficient (IC)
**Context:** A primary metric (Fitness Function) to evaluate how well an alpha predicts future returns.
*   **Description:** The Pearson Correlation between the predicted signal (the alpha value) and the actual future stock return.
*   **Mathematical Formulation:**

$$
IC = \frac{1}{N} \sum_{t=1}^{N} corr(\hat{y}_t, y_t)
$$

| Symbol | Definition |
| :--- | :--- |
| $\hat{y}_t$ | Vector of predicted values (alpha scores) at time $t$ |
| $y_t$ | Vector of actual returns at time $t$ |
| $N$ | Number of time periods |

