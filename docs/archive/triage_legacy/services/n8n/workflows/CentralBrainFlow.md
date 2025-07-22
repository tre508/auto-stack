# CentralBrain_Agent Flow Diagram

**Location:** `docs/n8n/workflows/CentralBrainFlow.md`

---

## Overview

This document illustrates the end-to-end flow of how commands entered into Vercel AI Chat are routed through the CentralBrain_Agent workflow in n8n, and how they trigger additional agent workflows or actions. The diagram below uses [Mermaid](https://mermaid-js.github.io/) syntax for clarity and easy visualization.

---

## Legend
- **User**: Human operator using WhatsApp, Email, Vercel AI Chat, or other external channel
- **CentralBrain_Agent**: Main orchestrator workflow in n8n
- **DocAgent**: Documentation summarization/indexing
- **FreqtradeSpecialist_Agent**: Trading automation and analysis
- **NotificationAgent**: Alerts, emails, or status updates
- **Other Sub-Agents**: Strategist, DataAnalyst, LLM_RL_Specialist, MarketMonitor, etc.
- **DB/Storage**: CentralDocDatabase, Supabase/Neon, etc.

---

## Command Types (Examples)
- `summarize docs`
- `run backtest on BTCUSDT`
- `analyze trades last week`
- `update strategy parameters`
- `send notification to admin`
- `generate report`
- `monitor market`

---

## Flow Diagram

```mermaid
flowchart TD
    A[User (WhatsApp/Email/Vercel AI Chat/Other)] -->|Enter Command| B(CentralBrain_Agent Webhook)
    B --> C{Parse Command}
    C -->|summarize docs| D[DocAgent]
    C -->|run backtest| E[FreqtradeSpecialist_Agent]
    C -->|analyze trades| E
    C -->|update strategy| E
    C -->|send notification| F[NotificationAgent]
    C -->|generate report| G[DocAgent]
    C -->|monitor market| H[MarketMonitor_Agent]
    D --> I[Summarize/Index Docs]
    I --> J[Store in CentralDocDatabase]
    E --> K[Run Freqtrade CLI/Analysis]
    K --> L[Store/Report Results]
    F --> M[Send Email/Alert]
    G --> N[Generate/Send Report]
    H --> O[Monitor/Alert on Market Events]
    J --> P[CentralBrain_Agent (Status Callback)]
    L --> P
    M --> P
    N --> P
    O --> P
    P --> Q[User (WhatsApp/Email/Vercel AI Chat/Other) Receives Status/Result]
```

---

## Notes
- The CentralBrain_Agent can be triggered by WhatsApp, email, Vercel AI Chat, or any external channel supported by n8n (not just OpenWebUI).
- All status/results are routed back to the user via the originating channel (WhatsApp, email, etc.).
- Each sub-agent can be a modular n8n workflow, triggered via HTTP Request nodes from CentralBrain_Agent.
- The CentralDocDatabase can be any supported backend (Supabase, Neon, file system, etc.).

---

**Edit this diagram as your agent system evolves to keep documentation up to date.** 

[SYNC 2025-05-14] Agent roles, orchestration references, and diagrams cross-checked and updated for consistency with Agent-Orientation.md and AgentHub.md. All agents listed are now accounted for and match the current orchestration structure. 