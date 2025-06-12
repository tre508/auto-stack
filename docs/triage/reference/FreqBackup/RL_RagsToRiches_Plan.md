# RL Rags-to-Riches Plan (Legacy)

> **Note:** As of [date], active RL development has shifted to "Plan B" (see `planB.md`). This file is now a historical reference for the initial RL exploration and lessons learned. All new RL, feature, and hyperopt work should follow the step-by-step playbook in `planB.md`.

**Plan B Implementation Status:** RL model, config, and strategy refactored to match Plan B (numeric &-s_close, custom reward, debug logging). Current focus: feature refinement, hyperopt, monitoring.

Goal: Implement and progressively refine a Reinforcement Learning model for the KrakenFreqAI strategy.

**Phase 1: Basic Setup**

- [✅] **Confirm Dependencies**: *(Completed)*
- [✅] **Update Strategy (`KrakenFreqAI.py`)**: *(Completed)*
- [✅] **Update Configuration (`config.json`)**: *(Completed, including `add_state_info` fix)*
- [✅] **Initial Run**: *(Completed)* Performed backtest with default `ReinforcementLearner`. Monitored via logs and Tensorboard. Result: -12.92% profit.

**Phase 2: Initial Analysis & Custom Reward Function**

- [✅] **Analyze Initial Results:** (Post Phase 1 completion) *(Completed)*
    *   Executed checklist from `user_data/_notes_/RL_Initial_Analysis_Checklist.md`. *(Main finding: Default reward function ineffective for profit)*.
    *   Reviewed web search findings (SB3 docs, examples) for implementation ideas, particularly around custom environments and reward structures.
- [✅] **Implement Custom Reward Function:** *(Completed)*
    *   Implemented and cleaned up `RagsToRichesRLModel.py` with a custom RL environment and reward logic. Model is ready for RL training/backtesting.
- [⏳] **Retrain & Re-analyze:** *(In Progress)*
    *   Run backtest with the custom model and analyze results (backtest table, Tensorboard).

## Phase 2.5: Exponential Profit Growth Improvement Plan

- [ ] **Detailed Trade/Exit Analysis:**
    - Use `freqtrade backtesting-analysis` with `--analysis-groups 2 4 5` to break down results by enter/exit tag and pair.
    - Deep-dive into losing trades, especially those with `trailing_stop_loss` and `exit_signal`.
- [ ] **Refine RL Reward Function:**
    - Penalize large drawdowns and long unprofitable holds.
    - Reward exponential equity growth (e.g., log(final_balance/start_balance)).
    - Shape reward to encourage compounding returns.
- [ ] **Feature Engineering:**
    - Add predictive features (volatility, trend, volume spikes, regime filters).
    - Ensure RL agent has access to regime/context features.
- [ ] **Action Space & Policy Review:**
    - Evaluate if the RL action space is too limited; consider multi-action (e.g., position sizing, partial exits).
- [ ] **Training Regimen Enhancement:**
    - Increase training cycles, use more data, validate on out-of-sample periods.
    - Use curriculum learning: start with simple markets, then add complexity.
- [ ] **Risk Controls:**
    - Tighten stoploss, add dynamic position sizing, or volatility scaling.
    - Limit max open trades if drawdown persists.
- [ ] **Hyperparameter Optimization:**
    - Use FreqAI hyperopt for RL config and model parameters.
    - Optimize for exponential profit metrics (CAGR, log-return, Sortino).
- [ ] **Visualization & Monitoring:**
    - Plot equity curve, drawdown, and trade distribution.
    - Use Tensorboard for RL training diagnostics.

### RL Backtest Results (2025-04-24)
- **Config:** KrakenFreqAI, RagsToRichesRLModel, timerange=20240101-20240418, seed=42, z-score normalization, dropout=0.2, batch norm enabled.
- **Total Trades:** 12
- **Winrate:** 33%
- **Total Profit:** -0.129 BTC (~-13%)
- **Max Drawdown:** 13%
- **Sharpe:** -1.56, **Sortino:** -1.43, **CAGR:** -42.6%
- **Expectancy:** -0.0012% per trade
- **Best Pair:** None (DOT/BTC, 0 trades)
- **Worst Pair:** ADA/BTC (6 trades, -9.5% total)
- **Exit Reason Summary:**
    - ROI: 6 trades, winrate 67%, small gains
    - Exit Signal: 4 trades, all losses
    - Trailing Stop Loss: 2 trades, all losses
- **Observations:**
    - No pairs were profitable; most losses from trailing stop and exit signals.
    - RL policy not yet capturing profitable patterns; further reward/feature tuning needed.
- **Next Actions:**
    - Refined reward function: penalizes drawdown, long unprofitable holds, volatility; rewards log equity growth and compounding returns.
    - Added predictive features: volatility, trend, volume spike, regime/context indicator (all normalized).
    - Increased RL training cycles and total_timesteps for more robust training.
    - Continue iterative backtesting and analysis.

### RL Backtest Results (2025-04-26)
- **Config:** KrakenFreqAI, RagsToRichesRLModel, timerange=20240101-20240418, seed=42, z-score normalization, dropout=0.2, batch norm enabled, new reward and features.
- **Total Trades:** 0
- **Winrate:** 0%
- **Total Profit:** 0 BTC
- **Max Drawdown:** 0%
- **Sharpe:** 0, **Sortino:** 0, **CAGR:** 0
- **Best/Worst Pair:** ADA/BTC (0 trades)
- **Exit Reason Summary:** No trades taken by RL agent.
- **Observations:**
    - RL agent did not take any trades. This may indicate overly restrictive entry logic, feature/target misalignment, or a bug in the RL pipeline.
    - Next step: Debug RL action/target generation, ensure features and targets are correctly set, and verify RL model is producing actionable signals.

**Workflow Notes:**
*   Reward and feature changes invalidate prior results; retrain and re-analyze after each major update.
*   Use longer timeranges and more cycles for robust RL convergence.

## Phase 3: Iterative Refinement (Parallel Tracks)**

- [⏳] **Feature Engineering:** (In Progress)
    *   Incrementally add/modify features (interaction features, regime filters) after custom reward is working.
    *   Retrain RL model and analyze impact.
- [⏳] **Hyperparameter Optimization:** (In Progress)
    *   Optimize core strategy params (`roi`, `stoploss`, `trailing`) after custom reward and features are stable.
    *   Optimize RL config params (`train_cycles`, etc.).
    *   (Advanced) Optimize RL model hyperparams (PPO specifics).
    *   **Always validate** optimized parameters rigorously on out-of-sample data, as per SB3 recommendations.
- [⏳] **Reward Function Tuning:** (In Progress) Refine the logic in `calculate_reward` based on observed agent behavior and performance.

**Workflow Notes:**
*   Use shorter timeranges/pairlists during development for faster feedback.
*   Remember feature or reward function changes invalidate prior hyperopt results for related parameters.
*   Prioritize establishing a working custom reward function before deep dives into features or hyperopt.
*   Feature and hyperopt refinement are parallel/iterative and not blocking for reward engineering.

## Phase 4: Real-World RLModel Usage Insights

- **Custom Reward Functions are Essential:**
  - The default RL reward in FreqAI is a showcase, not production-ready. All successful RLModel users design and iterate on their own `calculate_reward()` ([Freqtrade RL Docs](https://www.freqtrade.io/en/stable/freqai-reinforcement-learning/)).
  - Best results come from rewards that are continuous, well-scaled, and penalize undesirable behaviors (e.g., large drawdowns, long unprofitable holds).

- **Feature Engineering Drives Results:**
  - Add regime/context features (trend, volatility, volume spikes, shifted indicators). See [feature engineering docs](https://www.freqtrade.io/en/stable/freqai-feature-engineering/).
  - Use informative pairs and multiple timeframes for richer state information ([Strategy Customization](https://www.freqtrade.io/en/stable/strategy-customization/)).

- **Iterative Backtesting and Forward Testing:**
  - Backtest on diverse timeranges and market conditions. Forward test in dry-run for at least 2 months before live deployment ([Case Study](https://imbuedeskpicasso.medium.com/2509-profit-unlocked-a-case-study-on-algorithmic-trading-with-freqtrade-39b1051c0f1e)).
  - Monitor win/loss ratio, drawdown, and profit per 100+ trades. Optimize for stability, not just peak profit.

- **Hyperopt and Parameter Tuning:**
  - Use FreqAI hyperopt to tune both strategy and RL model parameters. Optimize for exponential profit metrics (CAGR, log-return, Sortino).

- **Risk Management is Critical:**
  - Limit max open trades, use dynamic position sizing, and set conservative stoplosses. High leverage increases risk ([Case Study](https://imbuedeskpicasso.medium.com/2509-profit-unlocked-a-case-study-on-algorithmic-trading-with-freqtrade-39b1051c0f1e)).

- **No Strategy is Universally Profitable:**
  - Even highly optimized RL strategies can have long losing streaks or fail in new market regimes ([Bot Academy](https://botacademy.ddns.net/2024/04/15/thanks-freqtrade-im-quitting-my-job-right-now/)).
  - Regularly review and adapt strategies; expect to retire or rework bots as conditions change.

- **Community and Documentation:**
  - Leverage Freqtrade's [official docs](https://www.freqtrade.io/en/stable/freqai-reinforcement-learning/) and community forums for up-to-date examples and troubleshooting.

- **Actionable Checklist:**
  - [x] Design and iterate a custom reward function.
  - [x] Engineer features for regime/context awareness.
  - [⏳] Backtest and forward test extensively.
  - [⏳] Use hyperopt for RL and strategy parameters.
  - [⏳] Monitor risk and adapt to market changes.
  - [ ] Engage with the community for support and new ideas.

### Golden Nuggets from Real-World RLModel Usage

- **Seed Everything for Reproducibility:**
  - RL backtests can yield different results if you don't set seeds for both the algorithm and the environment. Always set all relevant seeds to ensure reproducible results ([GitHub Issue #9306](https://github.com/freqtrade/freqtrade/issues/9306)).

- **Handle Data Shape Mismatches:**
  - ValueErrors like 'could not broadcast input array from shape (1,270) into shape (1,273)' often stem from inconsistent feature engineering or insufficient data. Always check that your feature columns and data shapes match across all timeframes and pairs ([GitHub Issue #7881](https://github.com/freqtrade/freqtrade/issues/7881)).

- **Custom RLModel Examples:**
  - See [twbrandon7/rl-trading-freqtrade](https://github.com/twbrandon7/rl-trading-freqtrade) for a public repo with RL integration and custom environments.
  - For advanced LSTM-based models with dynamic weighting and aggregate scoring, check [Netanelshoshan/freqAI-LSTM](https://github.com/Netanelshoshan/freqAI-LSTM). This repo demonstrates:
    - Multi-factor target scoring
    - Dynamic indicator weighting
    - Market regime and volatility filters
    - Extensive normalization and regularization

- **Feature Engineering Best Practices:**
  - Normalize all indicators (z-score, min-max, etc.) before feeding to the model.
  - Use dynamic weighting and market regime filters to adapt to changing conditions ([freqAI-LSTM](https://github.com/Netanelshoshan/freqAI-LSTM)).
  - Always include raw OHLCV features for RL models.

- **Model Architecture Tips:**
  - For LSTM/NN models, use dropout and batch normalization to avoid overfitting.
  - Tune window sizes, hidden dimensions, and number of layers for your dataset size and volatility.

- **Debugging RLModel Training:**
  - If you see warnings like 'add_state_info is not available in backtesting', set `add_state_info: false` in your config for backtests ([GitHub Issue #7881](https://github.com/freqtrade/freqtrade/issues/7881)).
  - Insufficient data is a common cause of RL model failures—always ensure you have enough candles for all timeframes and features.

- **General RLModel Project Examples:**
  - [rlellep/ML_BOT](https://github.com/rlellep/ML_BOT): Example of ML and RL integration with Freqtrade.

- **Community Wisdom:**
  - Many users report that RL models are powerful but require careful tuning, lots of data, and regular retraining. Expect to iterate frequently and monitor for regime changes.

## Plan B: Real-World Freqtrade/FreqAI Strategy Research

**(This section was merged into `docs/planB.md`)**

---

*This section is a living reference. Use it as a launchpad for the detailed Plan B playbook in `planB.md`.* 