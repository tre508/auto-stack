# Plan B Strategy Guide: FreqAI Development

## 1. Introduction & Core Philosophy

This document outlines the "Plan B" approach to developing a FreqAI trading strategy, moving away from pure Reinforcement Learning (RL) experimentation towards a more structured, data-driven methodology. The lessons learned from the "RagsToRichesRLModel" project emphasize the need for robust foundations, proven indicators, and rigorous backtesting.

**Core Philosophy:**
*   **Data-Driven Decisions:** Rely on historical data and statistical analysis rather than speculative RL.
*   **Proven Indicators:** Leverage well-understood technical indicators as the primary source for feature engineering.
*   **Risk Management:** Implement comprehensive risk management techniques (stop-loss, ROI targets).
*   **Iterative Improvement:** Focus on incremental improvements through hyperparameter optimization and feature selection.
*   **Simplicity and Robustness:** Favor simpler models and strategies that are less prone to overfitting and perform consistently across different market conditions.

## 2. Key Lessons Learned from RL (RagsToRiches)

The attempt to build a purely RL-driven model highlighted several challenges:
*   **Complexity:** RL models can be complex to design, train, and debug.
*   **Data Requirements:** Effective RL often requires vast amounts of diverse data.
*   **Stability:** RL agents can exhibit unstable behavior, especially in dynamic market environments.
*   **Interpretability:** Understanding *why* an RL agent makes a particular decision can be difficult.
*   **Overfitting:** RL models can easily overfit to specific training data or market regimes.

While RL holds promise, "Plan B" prioritizes a more conventional machine learning approach for FreqAI until RL techniques for trading mature further or specific, well-defined use cases emerge.

## 3. "Plan B" Strategy Development Framework

### 3.1. Foundation: Solid Technical Analysis

*   **Indicator Selection:**
    *   Start with a core set of widely used and effective indicators (e.g., RSI, MACD, Bollinger Bands, EMA, SMA, ADX, StochRSI).
    *   Research and select indicators relevant to the chosen market and timeframe.
    *   Avoid an excessive number of indicators initially to prevent noise and multicollinearity.
*   **Timeframes:**
    *   Utilize multiple timeframes (e.g., 5m, 15m, 1h, 4h) to capture short-term, medium-term, and long-term trends.
    *   Ensure consistency in how timeframes are used for feature generation.

### 3.2. Feature Engineering

*   **Lagged Features:** Incorporate lagged values of indicators and price data to provide historical context.
*   **Transformations:** Apply transformations (e.g., normalization, standardization, differencing) as appropriate for the chosen model.
*   **Interaction Features:** Consider creating interaction features (e.g., RSI > 70 AND MACD_cross_bullish) if domain knowledge suggests their utility.
*   **Target Definition (`&label`):**
    *   Clearly define the prediction target (e.g., price will increase by X% in Y periods).
    *   Experiment with different `label_period_candles` and profit/loss thresholds.

### 3.3. Model Selection & Training

*   **Start Simple:** Begin with simpler, interpretable models (e.g., Logistic Regression, LightGBM, XGBoost, RandomForest).
*   **Hyperparameter Optimization:**
    *   Use Freqtrade's built-in hyperopt capabilities or external tools (e.g., Optuna) to find optimal model parameters.
    *   Define a clear search space and evaluation metric for optimization.
*   **Data Splitting:**
    *   Use appropriate train/validation/test splits to evaluate model performance and prevent overfitting.
    *   Consider time-series cross-validation techniques.
*   **Regularization:** Apply regularization techniques (L1, L2, dropout) if using models prone to overfitting.

### 3.4. Backtesting & Evaluation

*   **Rigorous Backtesting:**
    *   Backtest over extended and diverse market periods (bull, bear, sideways).
    *   Pay attention to metrics like Sharpe Ratio, Sortino Ratio, Max Drawdown, Profit Factor, and win/loss rate.
*   **Out-of-Sample Testing:** Ensure the model generalizes well to unseen data.
*   **Walk-Forward Optimization:** Consider walk-forward optimization for more robust parameter tuning.
*   **Analyze Trades:** Review individual trades made by the bot during backtesting to understand its behavior and identify potential flaws.

### 3.5. Risk Management (Freqtrade Configuration)

*   **Stop-Loss:**
    *   Implement a sensible stop-loss strategy (e.g., fixed percentage, trailing stop-loss).
    *   Optimize stop-loss values using hyperopt.
*   **Take Profit / ROI Table:**
    *   Define a realistic ROI table.
    *   Consider dynamic take-profit mechanisms if appropriate.
*   **Position Sizing:**
    *   Use a consistent and appropriate stake amount.
    *   Consider dynamic position sizing based on risk or confidence (advanced).
*   **Max Open Trades:** Limit the number of concurrent trades to manage overall risk exposure.

## 4. Integration with `auto-stack`

*   **Configuration (`config-planB.json`):**
    *   Ensure the API server is enabled and configured correctly for communication with the `auto-stack` Controller.
    *   Use environment variables for sensitive credentials.
    *   Set `freqai.identifier` to match the FreqAI model class name you develop (e.g., `PlanB_FreqAI_Identifier`).
*   **Strategy File:**
    *   Create a new Python strategy file in `freqtrade/user_data/strategies/`.
    *   The strategy class name should match the `freqai.identifier`.
    *   Implement `populate_indicators`, `populate_entry_trend`, and `populate_exit_trend` as placeholders if the FreqAI model handles all logic, or to add pre/post-processing filters.
*   **FreqAI Model File:**
    *   Create a new Python FreqAI model file in `freqtrade/user_data/freqaimodels/`.
    *   The model class name must match `freqai.identifier`.
    *   Implement the FreqAI interface methods (`def_features`, `train`, `predict`, etc.).

## 5. Iteration and Continuous Improvement

*   **Regular Retraining:** Schedule regular retraining of the model to adapt to changing market conditions.
*   **Performance Monitoring:** Continuously monitor the live performance of the strategy.
*   **A/B Testing:** If possible, A/B test different versions of the strategy or model.
*   **Documentation:** Keep detailed records of experiments, model versions, and performance metrics.

## 6. Resources & Best Practices (from `planB.md`)

*   **Study Existing Strategies:** Analyze successful open-source Freqtrade strategies.
*   **Freqtrade Documentation:** Refer to the official Freqtrade documentation for FreqAI, hyperopt, and general bot configuration.
*   **Machine Learning Resources:** Consult reliable machine learning resources for best practices in feature engineering, model selection, and evaluation.
*   **Community:** Engage with the Freqtrade community for insights and support.

This guide provides a roadmap for developing a robust and potentially profitable FreqAI strategy under the "Plan B" framework. Success will depend on careful implementation, rigorous testing, and continuous adaptation.
