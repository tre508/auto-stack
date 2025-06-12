Of course. I will analyze the files from your previous `freqtrade` project and determine the best way to integrate them into the `auto-stack`.

First, I need to understand the contents of the backup. I will start by listing all the files and subdirectories within `/home/glenn/projects/auto-stack/docs/triage/reference/FreqBackup`.
Ran tool
Okay, I see the contents of the `FreqBackup` directory. It contains several subdirectories (`models - Copy`, `API-Cheet-sheets`, `freqaimodels - Copy`, `strategies - Copy`) and some markdown and JSON configuration files.

To effectively integrate these, I need to understand their content. I'll start by reading the markdown files and the JSON config to understand the high-level plan and configuration of the old project. This will inform how I approach the code in the `strategies` and `models` directories.

I will read the following files:
*   `RL_RagsToRiches_Plan.md`
*   `planB.md`
*   `Origional-config.json`
*   `obsidian_service_docs.md`
*   `pipe_mcp.md``
Read file: 
My apologies for the error. I need to read the entire file. Let me correct that and proceed to read the files.
Read file: docs/triage/reference/FreqBackup/RL_RagsToRiches_Plan.md
That's a very detailed plan. It seems the core of this backup revolves around developing a Reinforcement Learning model (`RagsToRichesRLModel`) for a `KrakenFreqAI` strategy. The document `RL_RagsToRiches_Plan.md` captures a lot of valuable lessons learned and a clear shift towards a "Plan B."

Now, I'll read the other files to get the full context before I start planning the integration.
Read file: docs/triage/reference/FreqBackup/planB.md
Okay, `planB.md` is a concise summary of best practices and resources, pointing towards using proven indicators and a structured approach rather than pure Reinforcement Learning experimentation. This is a very important piece of context.

Now, I'll examine the configuration and the other markdown files.
Read file: docs/triage/reference/FreqBackup/Origional-config.json
Okay, the `Origional-config.json` confirms the use of `Kraken` exchange, a `BTC` stake currency, and a FreqAI configuration pointing to `RagsToRichesRLModel`. A key finding is that the `api_server` was disabled (`"enabled": false`). This will definitely need to be changed to integrate with the `auto-stack`.

Now for the last two markdown files.
Read file: docs/triage/reference/FreqBackup/obsidian_service_docs.md
Okay, `obsidian_service_docs.md` describes a documentation management strategy using Obsidian and `git`, with an `n8n` workflow for automation. This is interesting and could be a valuable addition to the `auto-stack`'s own documentation strategy.

One file left.
Read file: docs/triage/reference/FreqBackup/pipe_mcp.md
This final file, `pipe_mcp.md`, explains how to integrate a "Model Control Protocol" (MCP) tool with `OpenWebUI` via an OpenAPI proxy. This strongly suggests the old project was interacting with an AI agent or a similar system, which aligns perfectly with the architecture of the `auto-stack` (which uses a `Controller` and `freq-chat`).

---

### Analysis Summary & Integration Plan

I have now reviewed all the provided files. Here's a summary of my findings and the plan to integrate these legacy assets into your current `auto-stack`.

**Key Findings:**

1.  **Project Goal:** The old project was heavily focused on developing a `FreqAI` strategy using Reinforcement Learning (`RagsToRichesRLModel`).
2.  **Shift in Strategy:** The project pivoted from pure RL experimentation to a more robust, data-driven approach outlined in `planB.md`, focusing on proven indicators, risk management, and hyperparameter optimization. This is a crucial insight.
3.  **Configuration:** The `Origional-config.json` is a standard `freqtrade` config for the Kraken exchange. Its most important feature for our purposes is that the **API server was disabled**, which prevented any external interaction.
4.  **Agent/AI Interaction:** The `pipe_mcp.md` file shows a clear intent to integrate with an AI front-end (`OpenWebUI`), which is analogous to the `freq-chat` and `Controller` in the `auto-stack`.
5.  **Documentation:** The `obsidian_service_docs.md` outlines a documentation automation strategy using `n8n`, which can be adapted.

**Integration Plan:**

My plan is to resurrect the *spirit* of the "Plan B" strategy by adapting the old configuration and preparing the ground for using the old strategies and models within the `auto-stack` ecosystem. I will not make any changes to the `strategies - Copy` or `models - Copy` directories at this time, as they require a working configuration first.

Here are the concrete steps I will take:

1.  **Create a New `freqtrade` Configuration:**
    *   I will create a new file named `config-planB.json` in the `docs/triage/reference/FreqBackup/` directory.
    *   This file will be based on `Origional-config.json` but with critical modifications:
        *   **Enable the API Server:** I will set `"enabled": true` in the `api_server` section.
        *   **Set Credentials:** I will set the `username` and `password` to align with the `auto-stack` documentation's recommendations (e.g., `your_api_user`, `a_very_secure_password`).
        *   **Update FreqAI Identifier:** I will update the `freqai.identifier` to reflect the "Plan B" approach.
        *   **Add Comments:** I will add comments explaining the changes.

2.  **Consolidate Documentation:**
    *   I will create a new guide named `PLAN_B_STRATEGY_GUIDE.md` in `docs/triage/reference/FreqBackup/`.
    *   This file will merge the key findings from `RL_RagsToRiches_Plan.md` and `planB.md` into a single, actionable playbook for developing a strategy based on the "Plan B" principles. It will serve as a project plan.

3.  **Propose Documentation Automation:**
    *   I will create a file named `N8N_DOC_AUTOMATION.md` that adapts the ideas from `obsidian_service_docs.md` into a concrete proposal for an `n8n` workflow that fits the `auto-stack` architecture.

I will start with step 1: creating the new configuration file.
My apologies for the error. I cannot create a new file directly. Instead, I will propose the content for the new files, and you can create them.

I will start by generating the content for the new configuration file, `config-planB.json`.

---

### **Content for `docs/triage/reference/FreqBackup/config-planB.json`**

```json
{
    "$schema": "https://schema.freqtrade.io/schema.json",
    "max_open_trades": 5,
    "stake_currency": "BTC",
    "stake_amount": 0.001,
    "tradable_balance_ratio": 0.99,
    "dry_run": true,
    "dry_run_wallet": 0.0011,
    "cancel_open_orders_on_exit": false,
    "trading_mode": "spot",
    "unfilledtimeout": {
      "entry": 5,
      "exit": 5,
      "exit_timeout_count": 0,
      "unit": "minutes"
    },
    "exit_pricing": {
        "price_side": "same",
        "order_book_top": 1,
        "use_order_book": false
    },
    "entry_pricing": {
        "price_side": "same",
        "order_book_top": 1,
        "use_order_book": false
    },
    "exchange": {
      "name": "kraken",
      "key": "${KRAKEN_API_KEY}",
      "secret": "${KRAKEN_API_SECRET}",
      "ccxt_config": { "enableRateLimit": true },
      "ccxt_async_config": { "enableRateLimit": true, "rateLimit": 3100 },
      "pair_whitelist": [
        "ADA/BTC",
        "XRP/BTC",
        "DOT/BTC",
        "LINK/BTC",
        "XLM/BTC",
        "ALGO/BTC",
        "UNI/BTC",
        "SOL/BTC"
      ]
    },
    "pairlists": [
      { "method": "StaticPairList" }
    ],
    "api_server": {
      "enabled": true,
      "listen_ip_address": "0.0.0.0",
      "listen_port": 8080,
      "verbosity": "error",
      "enable_openapi": true,
      "jwt_secret_key": "${API_JWT_SECRET:-your_jwt_secret_fallback}",
      "ws_token": "${API_WS_TOKEN:-your_ws_token_fallback}",
      "CORS_origins": [],
      "username": "${FREQTRADE_API_USERNAME:-your_api_user}",
      "password": "${FREQTRADE_API_PASSWORD:-a_very_secure_password}"
    },
    "bot_name": "PlanB-FreqAI",
    "internals": { "process_throttle_secs": 5 },
    "logger": {
        "loglevel": "info",
        "logfile": "user_data/logs/freqtrade.log"
     },
    "freqai": {
      "enabled": true,
      "identifier": "PlanB_FreqAI_Identifier",
      "train_period_days": 30,
      "backtest_period_days": 7,
      "live_retrain_hours": 6,
      "feature_parameters": {
        "include_timeframes": ["5m", "15m", "1h"],
        "indicator_periods_candles": [10, 20, 50],
        "label_period_candles": 24
      },
      "data_split_parameters": {
        "test_size": 0.2
      },
      "model_training_parameters": {}
    }
  }
```

### **Explanation of Changes:**

*   **`api_server.enabled`**: Changed from `false` to `true`. This is the most critical change, allowing the `auto-stack` Controller to communicate with `freqtrade`.
*   **`api_server.enable_openapi`**: Set to `true` to provide a Swagger UI for the API, which is helpful for development and aligns with the `auto-stack`'s use of FastAPI.
*   **`api_server.username` & `api_server.password`**: Updated to use environment variables (`${FREQTRADE_API_USERNAME}`, `${FREQTRADE_API_PASSWORD}`) with sensible defaults. This is a security best practice and aligns with how the `auto-stack` manages credentials.
*   **`api_server.jwt_secret_key`**: Added a fallback value to prevent errors if the environment variable is not set.
*   **`bot_name`**: Changed to `PlanB-FreqAI` to reflect the new focus.
*   **`freqai.identifier`**: Changed to `PlanB_FreqAI_Identifier`. This is a placeholder; you will need to create a corresponding FreqAI model class with this name.
*   **Simplified `freqai` config**: I have removed the complex `rl_config` section, as "Plan B" moves away from pure RL to a more traditional FreqAI model.

Please create a new file named `config-planB.json` inside `docs/triage/reference/FreqBackup/` and paste this content into it. Once you have done that, I will proceed with creating the consolidated strategy guide.