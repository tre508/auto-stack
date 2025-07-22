Read file: docs/triage/services/n8n/templates/Freqtrade_Log_Monitor.json

Read file: docs/triage/services/n8n/templates/Freqtrade_Task_Runner.json

Read file: docs/triage/services/n8n/templates/n8n_workflow_Summarization_Agent.json

Read file: docs/triage/services/n8n/templates/n8n_workflow_Backtest_Agent.json

Read file: controller/controller.py

Read file: docs/triage/services/n8n/templates/n8n_workflow_CentralBrain_Agent.json

Read file: docs/triage/services/n8n/templates/n8n_workflow_FreqtradeSpecialist_Agent.json

Read file: docs/triage/services/n8n/templates/centralbrain_bundle/NotificationAgent.json

Read file: docs/triage/services/n8n/templates/centralbrain_bundle/LLM_ParserAgent.json

Read file: freq-chat/README.md
──────────────────────────────────────────
──────────────────────────────────────────

## 🚦 Integration Road-map (high-level → concrete tasks)

──────────────────────────────────────────
A. n8n side — post-backtest logging & routing
──────────────────────────────────────────

1. Activate the following workflows  
   • `Freqtrade_Task_Runner.json` – kicks off backtests/hyperopts from CentralBrain/Freq-Chat.  
   • `Backtest_Agent.json` – parses CLI output → JSON metrics.  
   • `Freqtrade_Log_Monitor.json` – already polls container logs for **ERROR**; leave active for health-checks.  

   (Optional but recommended)  
   • `PerformanceMonitoring_Agent` – missing file; create a stub identical to `Backtest_Agent` but fed by live-trade logs instead of backtesting output.  
   • `NotificationAgent.json` – for Discord/email alerting when PnL < 0 or draw-down > x %.

2. Persist the results  
   a. Inside each "parse" Function node (Back-/Live-test parser) build a compact result object, e.g.  

      ```
      {
        "strategy": "KrakenFreqAI_auto_stack",
        "timerange": "2023-01-01→2024-06-15",
        "pnl_pct": 12.7,
        "sharpe": 1.84,
        "drawdown_pct": -8.1,
        "trades": 321,
        "run_id": "bt_{{timestamp}}"
      }
      ```  

   b. Two outputs:  
      • Insert the raw JSON into `backtest_results` (or `agent_logs`) in Postgres.  
      • POST the same payload to Controller → `/notify` (already exposed).  

3. From Controller to Mem0  
   Update the `/notify` handler (or add a `/store_result`) to call `add_memory_to_mem0_service(...)` with:  
   • messages = `[{"role":"system","content":"Backtest run_id bt_... outcome: +12.7 % PnL, Sharpe 1.84, DD -8.1 %"}]`  
   • metadata = `{"type":"backtest","run_id":"bt_...","strategy":"KrakenFreqAI_auto_stack"}`  

   Result: every completed back- or hyper-opt run becomes a retrievable memory chunk in Mem0.

4. Trigger downstream automations  
   • Add an n8n "IF" node after DB insert:  
     – condition `pnl_pct < 0 OR drawdown_pct < -10` → call `NotificationAgent` ("alert: poor backtest").  
     – else → trigger `Summarization_Agent` to condense the stats; forward the summary to Mem0 and Discord.  

   • Expose each run as a webhook event (`POST /backtest-finished`) for other micro-services (e.g., dashboards).

──────────────────────────────────────────
B. Freq-Chat hooks
──────────────────────────────────────────

1. Required endpoints the UI must hit  
   • `GET /api/trade-history?run_id=bt_xxx`  – new Controller route that:  
     – looks up Mem0 memory by `run_id` (or searches `"backtest run_id bt_xxx"`).  
     – returns the stored JSON + summary.  

   • `GET /api/recent-backtests?limit=10`  – query Postgres `backtest_results` for latest runs if detailed data needed.  

2. Chat-side utilities  
   • Add a "/backtest <strategy> <timerange>" slash-command that POSTs to Controller `/execute` with payload:  

     ```
     {"command":"backtest",
      "strategy":"KrakenFreqAI_auto_stack",
      "timerange":"2023-01-01-20240615",
      "config":"/freqtrade/user_data/config.json"}
     ```  

     This flows: Freq-Chat → Controller → n8n CentralBrain → FreqtradeSpecialist → Backtest_Agent.  
     When Backtest_Agent finishes, the notification inserted in Mem0 is automatically visible to chat queries.

3. Surfacing results in chat  
   • Use the existing `Summarization_Agent` to turn raw metric JSON into a readable paragraph (PnL, Sharpe, etc.).  
   • In the chat app, when a user asks "How did my last back-test perform?", call `GET /api/trade-history?run_id=last` → show the summary.  
   • Optionally stream the log lines produced by `Freqtrade_Log_Monitor` into a "Backtest Console" tab via `/logs/tail?service=freqtrade&run_id=bt_xxx`.

──────────────────────────────────────────
C. Smoke-tests you should run in the dev stack
──────────────────────────────────────────

1. Trigger a manual back-test through Freq-Chat slash-command → ensure:  
   • Controller forwards to n8n.  
   • Backtest Agent completes; Postgres row written; `/notify` hits Controller.  
   • Mem0 `/memory` contains the newly-added message.  

2. Query chat with "Show me backtest bt_{{id}}" → UI should fetch from Controller and render summary.  

3. Force an error (e.g., bad strategy name) → verify `Freqtrade_Log_Monitor` captures **ERROR** and NotificationAgent publishes alert.

──────────────────────────────────────────
D. Immediate action items (chronological)
──────────────────────────────────────────

1. Mark `Freqtrade_Task_Runner`, `Backtest_Agent`, `Freqtrade_Log_Monitor`, and `NotificationAgent` as `active: true` in n8n.  
2. Add missing `PerformanceMonitoring_Agent.json` (clone Backtest_Agent, change parser regex for live trade stats).  
3. Extend Controller:  
   • `/notify` → push payload to Mem0.  
   • `/api/trade-history` + `/api/recent-backtests` read from Mem0 / Postgres.  
4. Update Freq-Chat front-end:  
   • Implement slash-command handler.  
   • Add data-fetching hooks to new endpoints.  
5. Run the three smoke-tests above and iterate.

Once those pieces are live, any strategy back-/live-test will automatically flow → n8n parsing → Mem0 storage → chat retrieval, giving traders immediate conversational access to performance stats.
