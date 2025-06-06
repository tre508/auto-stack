# CentralBrain.md

**Location:** `docs/n8n/prompt_library/CentralBrain.md`

---

## Overview
This document provides detailed, copy-paste-ready n8nChat prompt templates for building a modular, multi-agent automation system using n8n. The architecture is based on a CentralBrain_Agent orchestrator, multiple manager agents, and specialized sub-agents for Freqtrade, FreqAI, research, and utility tasks.

---

## Org Chart

- **CentralBrain_Agent** (Orchestrator/Gatekeeper)
  - **FreqtradeManager_Agent**
    - StrategyAnalysis_Agent
    - Backtest_Agent
    - Hyperopt_Agent
    - TradeExecution_Agent
    - PerformanceMonitoring_Agent
  - **FreqAIManager_Agent**
    - FreqAI_ModelTrainer_Agent
    - FreqAI_RL_Agent
    - FeatureEngineering_Agent
    - OutlierDetection_Agent
  - **ResearchManager_Agent**
    - SentimentAnalysis_Agent
    - NewsAggregator_Agent
    - MarketMonitor_Agent
    - OrderflowAnalysis_Agent
  - **UtilityManager_Agent** (optional)
    - DataDownload_Agent
    - ModelPersistence_Agent
    - SQLAnalysis_Agent
    - NotificationAgent

---

## Best Practices for n8nChat Prompts
- Be explicit about agent roles, workflow triggers, and expected inputs/outputs.
- Use HTTP Request nodes for inter-agent communication.
- Include error handling, logging, and status reporting.
- Keep each workflow modular and focused on a single responsibility.
- Use structured JSON for all agent responses.

---

## Prompt Templates

### CentralBrain_Agent (Orchestrator)
```txt
Create an n8n workflow called 'CentralBrain_Agent' that acts as the main orchestrator for a multi-agent trading automation system.
- Trigger: Webhook node (POST, receives JSON commands from Vercel AI Chatbot).
- Parse the 'command' field and route to the appropriate manager agent (FreqtradeManager, FreqAIManager, ResearchManager, UtilityManager) using a Switch node.
- Each manager agent is called via HTTP Request node.
- Collect and aggregate responses, then return a structured JSON response to the user.
- Log all actions and errors.
- Output: { status, message, data }.
```

### FreqtradeManager_Agent
```txt
Create an n8n workflow called 'FreqtradeManager_Agent' to manage all Freqtrade-related sub-agents.
- Trigger: HTTP Request node (receives JSON with {command, parameters}).
- Use a Switch node to route to the correct sub-agent (StrategyAnalysis, Backtest, Hyperopt, TradeExecution, PerformanceMonitoring).
- Each sub-agent is called via HTTP Request node.
- Aggregate and return results to CentralBrain_Agent.
- Log all actions and errors.
```

### FreqAIManager_Agent
```txt
Create an n8n workflow called 'FreqAIManager_Agent' to manage all FreqAI/ML sub-agents.
- Trigger: HTTP Request node (receives JSON with {command, parameters}).
- Use a Switch node to route to the correct sub-agent (ModelTrainer, RL, FeatureEngineering, OutlierDetection).
- Each sub-agent is called via HTTP Request node.
- Aggregate and return results to CentralBrain_Agent.
- Log all actions and errors.
```

### ResearchManager_Agent
```txt
Create an n8n workflow called 'ResearchManager_Agent' to manage all research and market intelligence sub-agents.
- Trigger: HTTP Request node (receives JSON with {command, parameters}).
- Use a Switch node to route to the correct sub-agent (SentimentAnalysis, NewsAggregator, MarketMonitor, OrderflowAnalysis).
- Each sub-agent is called via HTTP Request node.
- Aggregate and return results to CentralBrain_Agent.
- Log all actions and errors.
```

### UtilityManager_Agent (optional)
```txt
Create an n8n workflow called 'UtilityManager_Agent' to manage utility sub-agents.
- Trigger: HTTP Request node (receives JSON with {command, parameters}).
- Use a Switch node to route to the correct sub-agent (DataDownload, ModelPersistence, SQLAnalysis, Notification).
- Each sub-agent is called via HTTP Request node.
- Aggregate and return results to CentralBrain_Agent.
- Log all actions and errors.
```

---

## Sub-Agent Prompt Templates

### StrategyAnalysis_Agent
```txt
Create an n8n workflow called 'StrategyAnalysis_Agent' for analyzing Freqtrade strategy logic and parameters.
- Trigger: HTTP Request node (receives JSON with {strategy_file}).
- Parse the strategy file, extract parameters, and summarize logic (optionally using an LLM node).
- Return a JSON summary of the strategy's logic and parameters.
- Handle errors and report status to FreqtradeManager_Agent.
```

### Backtest_Agent
```txt
Create an n8n workflow called 'Backtest_Agent' for running historical backtests on trading strategies.
- Trigger: HTTP Request node (receives JSON with {strategy, timerange, config}).
- Run the Freqtrade backtesting command using the Execute Command node.
- Parse the results and return a summary (PnL, Sharpe, drawdown) as JSON.
- Handle errors and report status to FreqtradeManager_Agent.
```

### Hyperopt_Agent
```txt
Create an n8n workflow called 'Hyperopt_Agent' for optimizing strategy parameters.
- Trigger: HTTP Request node (receives JSON with {strategy, config, hyperopt_params}).
- Run the Freqtrade hyperopt command using the Execute Command node.
- Parse and return optimal parameters and metrics as JSON.
- Handle errors and report status to FreqtradeManager_Agent.
```

### TradeExecution_Agent
```txt
Create an n8n workflow called 'TradeExecution_Agent' for executing live or dry-run trades.
- Trigger: HTTP Request node (receives JSON with {trade_action, parameters}).
- Execute the trade using Freqtrade CLI or API.
- Return trade execution status and details as JSON.
- Handle errors and report status to FreqtradeManager_Agent.
```

### PerformanceMonitoring_Agent
```txt
Create an n8n workflow called 'PerformanceMonitoring_Agent' for monitoring live bot and model performance.
- Trigger: HTTP Request node (receives JSON with {monitoring_params}).
- Collect and analyze performance data.
- Return alerts or performance summaries as JSON.
- Handle errors and report status to FreqtradeManager_Agent.
```

### FreqAI_ModelTrainer_Agent
```txt
Create an n8n workflow called 'FreqAI_ModelTrainer_Agent' for training and retraining FreqAI models.
- Trigger: HTTP Request node (receives JSON with {model_type, features, labels, config}).
- Run model training using Freqtrade CLI and FreqAI options.
- Return training status and model metrics as JSON.
- Handle errors and report status to FreqAIManager_Agent.
```

### FreqAI_RL_Agent
```txt
Create an n8n workflow called 'FreqAI_RL_Agent' for reinforcement learning model training and deployment.
- Trigger: HTTP Request node (receives JSON with {rl_params, config}).
- Run RL training using Freqtrade CLI and FreqAI RL options.
- Return RL training status and metrics as JSON.
- Handle errors and report status to FreqAIManager_Agent.
```

### FeatureEngineering_Agent
```txt
Create an n8n workflow called 'FeatureEngineering_Agent' for designing and testing new features for FreqAI models.
- Trigger: HTTP Request node (receives JSON with {feature_params, data}).
- Process and validate features, return results as JSON.
- Handle errors and report status to FreqAIManager_Agent.
```

### OutlierDetection_Agent
```txt
Create an n8n workflow called 'OutlierDetection_Agent' for detecting and removing outliers from datasets.
- Trigger: HTTP Request node (receives JSON with {data, detection_params}).
- Run outlier detection and return cleaned data or outlier report as JSON.
- Handle errors and report status to FreqAIManager_Agent.
```

### SentimentAnalysis_Agent
```txt
Create an n8n workflow called 'SentimentAnalysis_Agent' for analyzing news and social sentiment.
- Trigger: HTTP Request node (receives JSON with {text, source}).
- Analyze sentiment using LLM or external API.
- Return sentiment score and summary as JSON.
- Handle errors and report status to ResearchManager_Agent.
```

### NewsAggregator_Agent
```txt
Create an n8n workflow called 'NewsAggregator_Agent' for collecting and summarizing crypto news.
- Trigger: HTTP Request node (receives JSON with {topics, sources}).
- Fetch and summarize news articles.
- Return news summaries as JSON.
- Handle errors and report status to ResearchManager_Agent.
```

### MarketMonitor_Agent
```txt
Create an n8n workflow called 'MarketMonitor_Agent' for monitoring real-time market conditions.
- Trigger: HTTP Request node (receives JSON with {market_params}).
- Fetch and analyze market data.
- Return alerts or market summaries as JSON.
- Handle errors and report status to ResearchManager_Agent.
```

### OrderflowAnalysis_Agent
```txt
Create an n8n workflow called 'OrderflowAnalysis_Agent' for analyzing order book and trade flow data.
- Trigger: HTTP Request node (receives JSON with {orderflow_params, data}).
- Analyze order flow and return insights as JSON.
- Handle errors and report status to ResearchManager_Agent.
```

### DataDownload_Agent
```txt
Create an n8n workflow called 'DataDownload_Agent' for automating market data downloads.
- Trigger: HTTP Request node (receives JSON with {data_params}).
- Download and store data, return status as JSON.
- Handle errors and report status to UtilityManager_Agent.
```

### ModelPersistence_Agent
```txt
Create an n8n workflow called 'ModelPersistence_Agent' for managing model saving, loading, and purging.
- Trigger: HTTP Request node (receives JSON with {model_id, action}).
- Perform the requested persistence action and return status as JSON.
- Handle errors and report status to UtilityManager_Agent.
```

### SQLAnalysis_Agent
```txt
Create an n8n workflow called 'SQLAnalysis_Agent' for running advanced SQL queries on trade databases.
- Trigger: HTTP Request node (receives JSON with {query, db_params}).
- Run the query and return results as JSON.
- Handle errors and report status to UtilityManager_Agent.
```

### NotificationAgent
```txt
Create an n8n workflow called 'NotificationAgent' for sending alerts and notifications.
- Trigger: HTTP Request node (receives JSON with {message, recipients}).
- Send the notification and return status as JSON.
- Handle errors and report status to UtilityManager_Agent.
```

---

**Copy and adapt these prompt templates in n8nChat to rapidly build and maintain your multi-agent automation system.** 