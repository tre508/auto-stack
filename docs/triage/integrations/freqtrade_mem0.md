# Freqtrade-Mem0 Integration Guide

**Note for AI Agent:** This guide explains how Mem0 (`mem0_mcp` service) relates to Freqtrade operations. Crucially, Freqtrade does **not** directly integrate with Mem0. Mem0 is used by other services (FastAPI Controller, n8n) to store or retrieve data *about* Freqtrade tasks. Use this guide to understand these indirect interactions and how to troubleshoot them.

## Purpose
<!-- source: docs/setup/02_Trading.md, docs/setup/05_Agent_Capabilities_and_Interaction.md -->
This document clarifies the relationship between Freqtrade and the Mem0 service (`mem0_mcp`). It's important to understand that **Freqtrade does not directly integrate with Mem0**. Instead, Mem0 supports Freqtrade-related operations by providing memory and knowledge persistence for the `automation-stack` services (like the FastAPI Controller and n8n workflows) that orchestrate or interact with Freqtrade.

## Architecture
<!-- source: docs/setup/02_Trading.md, docs/setup/05_Agent_Capabilities_and_Interaction.md -->

### No Direct Freqtrade <-> Mem0 Link
Currently, there is no built-in mechanism for the Freqtrade application itself to make calls to the Mem0 API, nor does Mem0 directly query or interact with Freqtrade.
<!-- source: docs/setup/02_Trading.md ("Current Status: Direct Freqtrade <-> Mem0 integration is not yet implemented.") -->

### Mediated Interaction via `automation-stack` Services
Mem0's role in the context of Freqtrade is to serve as a memory layer for the services that manage Freqtrade tasks. These intermediary services include:
*   **FastAPI Controller (`controller_mcp`):** Can use Mem0 to store context related to Freqtrade operations it manages, or to retrieve knowledge that might inform those operations.
*   **n8n Workflows (`n8n_mcp`):** Can store results of Freqtrade tasks (e.g., backtest summaries, trade data), maintain state for long-running Freqtrade automations, or retrieve historical data/context from Mem0 to guide workflow logic. This includes agent-based n8n workflows like `FreqtradeManager_Agent` and its sub-agents.
    <!-- source: docs/setup/02_Trading.md, docs/setup/05_Agent_Capabilities_and_Interaction.md -->

## Integration Flow (Illustrative Use Cases)

The following scenarios illustrate how Mem0 supports Freqtrade-related activities indirectly:

### 1. Storing Context/Results of Freqtrade Operations
<!-- source: docs/setup/04_Cross_Stack_Integration_Guide.md (n8n <-> Mem0), docs/services/n8n/prompt_library/CentralBrain.md (Backtest_Agent concept) -->
*   **Scenario:** An n8n workflow, such as a `Backtest_Agent`, executes a Freqtrade backtest using the `Execute Command` node.
*   **Mem0 Interaction:** After the backtest completes and the n8n workflow parses the results (e.g., P&L, drawdown, trades), it uses an "HTTP Request" node to call the Mem0 API (e.g., `POST http://mem0_mcp:8000/memory`). The workflow stores a structured summary of the backtest parameters and key results, possibly associating it with a specific strategy ID, task ID, or timestamp.
    *   Example data stored: `{"type": "freqtrade_backtest_summary", "strategy": "SuperTrendV1", "timerange": "20230101-20230630", "pnl_percent": 15.7, "max_drawdown": 0.08, "total_trades": 75}`

### 2. Retrieving Knowledge to Inform Freqtrade-Related Tasks
<!-- source: docs/setup/05_Agent_Capabilities_and_Interaction.md (Mem0 for knowledge retrieval) -->
*   **Scenario:** An AI agent, orchestrated by n8n or the FastAPI Controller, is tasked with analyzing a Freqtrade strategy's recent performance or suggesting potential improvements.
*   **Mem0 Interaction:** The agent (via the Controller or an n8n workflow) queries Mem0 using its search endpoint (e.g., `POST http://mem0_mcp:8000/search`). The query might look for previously stored backtest results, performance metrics, manual notes, or analyses related to that specific strategy or similar trading concepts. The retrieved information can then be used to augment prompts for an LLM or inform the agent's decision-making process.

### 3. Maintaining State for Multi-Step Freqtrade Automations
<!-- source: docs/setup/02_Trading.md (Potential uses for Mem0) -->
*   **Scenario:** A complex, potentially long-running Freqtrade automation, such as a series of hyperparameter optimizations or walk-forward analyses, is managed by an n8n workflow.
*   **Mem0 Interaction:** The n8n workflow can store intermediate results, the current best set of parameters, progress checkpoints, or error states in Mem0. This allows the automation to be paused and resumed, to track its evolution over time, or to recover from interruptions.

## Input/Output Data Formats (for Mem0)

*   **Data Stored in Mem0:** Typically JSON objects. For Freqtrade-related information, this could include structured data like:
    *   Backtest results: `{"type": "backtest_result", "strategy_id": "...", "parameters": {...}, "metrics": {...}}`
    *   Trade summaries: `{"type": "trade_summary", "trade_id": "...", "pair": "...", "profit_percent": "..."}`
    *   Strategy notes or analyses: `{"type": "strategy_analysis", "strategy_name": "...", "notes": "..."}`
    *   Task states: `{"type": "automation_state", "task_id": "...", "status": "running", "current_step": "..."}`
*   **Queries to Mem0:**
    *   Text-based queries for semantic search (e.g., "recent backtests for strategy X").
    *   Structured queries using metadata filters (e.g., `{"filters": {"type": "backtest_result", "strategy_id": "..."}}`).
*   **Responses from Mem0:** JSON arrays of matching memory entries, including their content and metadata.

## Config Requirements
<!-- source: docs/setup/04_Cross_Stack_Integration_Guide.md, docs/setup/03_Core_Services_Configuration_and_Verification.md -->

### Mem0 Service
*   The Mem0 service (`mem0_mcp`) must be running, correctly configured (as per `mem0/server/config.yaml`), and accessible on the Docker network (e.g., `mcp-net`).

### Interacting Services (FastAPI Controller / n8n)
*   **Network Access:** Must be able to reach the `mem0_mcp` service (e.g., at `http://mem0_mcp:8000`).
*   **FastAPI Controller:**
    *   Requires the `mem0ai` Python package in its `requirements.txt`.
    *   Needs the Mem0 API URL configured (e.g., via an environment variable).
*   **n8n Workflows:**
    *   Use "HTTP Request" nodes configured to target the Mem0 API endpoints.

## Dependencies or Env Vars Needed
(Covered in "Config Requirements" for the interacting services that call Mem0.)

## Failover or Fallback Behavior

The services (FastAPI Controller, n8n workflows) that interact with Mem0 are responsible for handling potential errors from the Mem0 API:
*   Catching network errors if Mem0 is unavailable.
*   Handling HTTP error responses from Mem0 (e.g., issues with search queries, write failures).
*   Logging errors related to Mem0 interactions.
*   Workflows and Controller logic should be designed to function gracefully, perhaps with reduced capabilities or default behaviors, if Mem0 is temporarily unavailable or returns errors.

## Where prompts, signals, or configs are injected

This section is less directly applicable in the Freqtrade-Mem0 context because Freqtrade itself does not interact with Mem0.
*   **Data related to Freqtrade operations** (e.g., results, analyses, states) is injected into Mem0 *by* the FastAPI Controller or n8n workflows after these services have interacted with Freqtrade.
*   **Configuration for Mem0 access** resides within the Controller and n8n workflows that call Mem0.

## Troubleshooting
<!-- source: FT_int_guide.md (adapted general troubleshooting) -->
If Freqtrade-related data is expected to be in Mem0 (stored by an intermediary service) but is missing, or if retrieval fails:

1.  **Action: Verify the Intermediary Service (Controller or n8n).**
    *   Check the logs of the FastAPI Controller (`docker logs controller_mcp`) or the execution history of the relevant n8n workflow. Look for errors specifically during the steps where Mem0 interaction (add, search, get) was supposed to occur.
    *   Ensure the logic within the Controller or n8n workflow for preparing data for Mem0 and calling the Mem0 API is correct.

2.  **Action: Check Mem0 Service Health.**
    *   Examine the Mem0 service logs (`docker logs mem0_mcp`) for any errors that occurred around the time the write or read operation was attempted by the intermediary service.
    *   Test the Mem0 `/status` endpoint directly: `curl http://mem0_mcp:8000/status`. Expect `{"status": "Mem0 service is running"}`.

3.  **Action: Confirm Network and Configuration for Intermediary Service.**
    *   Ensure the Controller or n8n service has the correct Mem0 API endpoint configured (e.g., `http://mem0_mcp:8000`) and can reach the `mem0_mcp` service over the Docker network.

4.  **Action: Test Mem0 API Directly.**
    *   Use `curl` or a similar tool to make direct API calls to Mem0, mimicking the request that the Controller or n8n workflow *should* have sent. This helps isolate whether the issue lies with Mem0 itself or with the logic of the calling service.
    *   **Example: Add a memory related to a Freqtrade task:**
        ```bash
        # From a terminal that can reach mem0_mcp (e.g., host, or another container on mcp-net)
        curl -X POST -H "Content-Type: application/json" \
        -d '{"content": "Freqtrade backtest for MyStrategy on 2023-01-01 completed with PnL 5%", "metadata": {"app": "freqtrade", "task": "backtest", "strategy": "MyStrategy"}}' \
        http://mem0_mcp:8000/memory
        ```
    *   **Example: Search for the added memory:**
        ```bash
        curl -X POST -H "Content-Type: application/json" \
        -d '{"query": "MyStrategy backtest results"}' \
        http://mem0_mcp:8000/search
        ```
