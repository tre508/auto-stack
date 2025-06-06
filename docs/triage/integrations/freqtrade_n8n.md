# Freqtrade-n8n Integration Guide

**Note for AI Agent:** This guide details how n8n (`n8n_mcp` service) workflows interact with Freqtrade. Use this to understand direct API polling, CLI command execution via n8n, interaction via the FastAPI Controller, and n8n's role in multi-agent Freqtrade automation. Pay close attention to configuration requirements for n8n (like credentials and `N8N_ALLOW_EXEC`) and Freqtrade.

## Purpose
<!-- source: docs/services/n8n/n8n_freqtrade_webhook_ideas.md, docs/services/n8n/n8n_multi_agent_concepts.md, docs/services/n8n/prompt_library/CentralBrain.md -->
This document outlines how n8n (`n8n_mcp` service) workflows are utilized to automate, orchestrate, and interact with the Freqtrade environment. It covers various integration patterns, including direct Freqtrade API polling, execution of Freqtrade CLI commands, interaction via the FastAPI Controller, and the role of n8n in multi-agent Freqtrade automation.

## Architecture
<!-- source: docs/services/n8n/n8n_freqtrade_webhook_ideas.md, docs/setup/04_Cross_Stack_Integration_Guide.md, docs/setup/Freqtrade_Project_Checklist.md, docs/services/n8n/prompt_library/CentralBrain.md, docs/setup/05_Agent_Capabilities_and_Interaction.md -->
n8n integrates with Freqtrade through several architectural patterns:

### 1. Direct Freqtrade API Polling (Recommended for Data Retrieval)
n8n workflows can directly query Freqtrade's REST API endpoints.
*   **Mechanism:** Uses "HTTP Request" nodes within n8n.
*   **Authentication:** The workflow must handle JWT authentication by first calling Freqtrade's token endpoint (e.g., `/api/v1/token/user`) and then using the received token as a Bearer token for subsequent requests.
*   **Use Cases:** Periodically fetching trade history, performance metrics, bot status, etc.
    <!-- source: docs/services/n8n/n8n_freqtrade_webhook_ideas.md -->

### 2. Interaction via FastAPI Controller
n8n workflows can call API endpoints exposed by the FastAPI Controller (`controller_mcp`), which then communicates with Freqtrade.
*   **Mechanism:** Uses "HTTP Request" nodes to call Controller endpoints.
*   **Use Cases:** Preferred when the Controller provides additional logic, abstraction, or security layers over direct Freqtrade API calls.
    <!-- source: docs/setup/04_Cross_Stack_Integration_Guide.md, docs/setup/Freqtrade_Project_Checklist.md -->

### 3. Orchestration of Freqtrade CLI Commands
n8n workflows, particularly those acting as specialized agents, can execute `freqtrade` command-line interface (CLI) commands.
*   **Mechanism:** Uses the "Execute Command" node in n8n.
*   **Target:** The commands are executed within the Freqtrade container environment. This implies n8n has a way to trigger command execution in that container (e.g., via Docker API, SSH, or a helper agent if direct exec is not feasible or secure). The agent prompts suggest direct CLI execution capability.
*   **Use Cases:** Initiating backtests (`freqtrade backtesting ...`), hyperparameter optimization (`freqtrade hyperopt ...`), data downloads, etc.
    <!-- source: docs/services/n8n/prompt_library/CentralBrain.md (Backtest_Agent, Hyperopt_Agent concepts) -->

### 4. Multi-Agent Orchestration (n8n as the Backbone)
n8n serves as the foundation for a hierarchical multi-agent system that manages complex Freqtrade automations.
*   **Structure:** A `CentralBrain_Agent` workflow receives high-level tasks and dispatches them to a `FreqtradeManager_Agent` workflow. The `FreqtradeManager_Agent` then delegates specific Freqtrade operations (like backtesting, trade execution, analysis) to specialized sub-agent workflows (e.g., `Backtest_Agent`, `TradeExecution_Agent`).
*   **Communication:** Inter-workflow communication (between these agent-like workflows) is typically handled via HTTP webhooks.
    <!-- source: docs/services/n8n/prompt_library/CentralBrain.md, docs/setup/05_Agent_Capabilities_and_Interaction.md -->

## Integration Flow Examples

### 1. Freqtrade API Polling Workflow (e.g., New Trade Detection)
<!-- source: docs/services/n8n/n8n_freqtrade_webhook_ideas.md -->
*   **Trigger:** "Schedule" node (e.g., runs every minute).
*   **Step 1: Get/Refresh JWT:** "HTTP Request" node makes a `POST` to Freqtrade's `/api/v1/token/user` (or `/api/v1/token/auth`) with credentials. The workflow stores the `access_token`.
*   **Step 2: Poll Trades Endpoint:** "HTTP Request" node makes a `GET` to Freqtrade's `/api/v1/trades`, including the `Authorization: Bearer <token>` header.
*   **Step 3: Process Data:** "Function" or "Set" node compares the fetched trades with trades from a previous run (e.g., by storing last seen trade IDs in workflow static data or an external store like Mem0).
*   **Step 4: Conditional Action:** "IF" node branches if new trades are detected.
*   **Step 5: Notify/Act:** Subsequent nodes send notifications (e.g., to Slack, Discord) or trigger other actions based on the new trade data.

### 2. CLI Orchestration Workflow (e.g., `Backtest_Agent`)
<!-- source: docs/services/n8n/prompt_library/CentralBrain.md (Backtest_Agent concept) -->
*   **Trigger:** "Webhook" node. This workflow is called by `FreqtradeManager_Agent` (or another orchestrator) with parameters like `strategy_name` and `timerange` in the JSON request body.
*   **Step 1: Construct Command:** "Set" node dynamically builds the `freqtrade backtesting` command string using the input parameters:
    `freqtrade backtesting --strategy {{ $json.body.strategy_name }} --timerange {{ $json.body.timerange }} --config user_data/config.json --export trades`
*   **Step 2: Execute Command:** "Execute Command" node runs the constructed command. The target for execution must be the Freqtrade container.
*   **Step 3: Parse Results:** "Function" node (or series of text parsing nodes) processes the `stdout` from the command execution to extract key backtest metrics (e.g., P&L, win rate, max drawdown). Freqtrade's JSON output from `--export trades` can also be read if accessible.
*   **Step 4: Respond:** "Respond to Webhook" node returns a structured JSON summary of the backtest results to the calling workflow.

### 3. Exposing Freqtrade Data as a Tool (MCP Server Trigger)
<!-- source: docs/services/n8n/n8n_multi_agent_concepts.md -->
*   **Trigger:** "MCP Server Trigger" node. Configure a specific path (e.g., `/tools/freqtrade-profit-summary`).
*   **Workflow Steps:**
    1.  Authenticate with Freqtrade API (get JWT).
    2.  Call a Freqtrade API endpoint (e.g., `/api/v1/profit` or `/api/v1/performance`).
    3.  Optionally, format the JSON response from Freqtrade into a more concise or AI-friendly structure.
*   **Output:** The final data processed by the workflow is automatically returned to the AI client that called the MCP Server Trigger URL.

## Input/Output Data Formats

*   **Input to n8n (Triggers):**
    *   Scheduled events (no specific data).
    *   JSON payloads from webhook calls (e.g., `{"command": "run_backtest", "parameters": {"strategy_name": "X", "timerange": "Y"}}`).
*   **Output from n8n (to Freqtrade API):**
    *   JSON payloads for Freqtrade API authentication (username/password).
    *   Standard HTTP GET/POST requests to Freqtrade API endpoints.
*   **Input to n8n (from Freqtrade API):**
    *   JSON responses from Freqtrade API endpoints.
*   **Output from n8n (Execute Command to Freqtrade CLI):**
    *   A string representing the `freqtrade` command and its arguments.
*   **Input to n8n (from Freqtrade CLI via Execute Command):**
    *   Raw text from `stdout` and `stderr` of the executed command. This requires parsing within the n8n workflow (e.g., using Regex, Function nodes, or specific parsing nodes if available).

## Config Requirements

### n8n-Side
*   **Credentials:** Freqtrade API username and password should be stored securely using n8n's built-in credential manager and referenced in "HTTP Request" nodes.
*   **Environment Variables:**
    *   `N8N_ALLOW_EXEC=true`: Required if using the "Execute Command" node. Be aware of the security implications of enabling command execution.
*   **Network Access:** The n8n container (`n8n_mcp`) must be on the same Docker network (e.g., `mcp-net`) as the Freqtrade container (`freqtrade_devcontainer`) to allow direct API calls and CLI execution (if applicable). It also needs access to the `controller_mcp` if interacting via the Controller.
    <!-- source: docs/services/n8n/n8n_freqtrade_webhook_ideas.md -->

### Freqtrade-Side
Refer to the [Freqtrade Master Integration Guide](./FT_int_guide.md#config-requirements-freqtrade-side) for Freqtrade-specific setup, including:
*   API server enabled in `user_data/config.json` with matching credentials.
*   Network accessibility.
*   Freqtrade CLI tools must be available and functional within its container if n8n is to execute them.

## Dependencies or Env Vars Needed
(Covered in "Config Requirements" above.)

## Failover or Fallback Behavior
n8n workflows should incorporate robust error handling:
*   **Error Triggers:** Use the "Error Trigger" node to define a separate path for handling failures within a workflow.
*   **Retry Mechanisms:** Configure the "Retry on Fail" option in "HTTP Request" and "Execute Command" nodes for transient issues.
*   **Conditional Logic:** Use "IF" nodes to check for expected responses or error conditions and branch the workflow accordingly.
*   **Logging:** Add "Log to Console" nodes or custom logging steps (e.g., writing to Mem0 or a database) at critical points for easier debugging.
*   **Timeouts:** Configure appropriate timeouts in "HTTP Request" and "Execute Command" nodes.

## Where prompts, signals, or configs are injected

*   **Prompts/Parameters for Freqtrade tasks:** These are typically injected into n8n workflows via the data from their trigger nodes (e.g., JSON body of a webhook, parameters from a manual execution, or data from a preceding node).
*   **Signals from Freqtrade:** In this architecture, n8n actively polls the Freqtrade API for data or status changes. Freqtrade does not inherently push signals or events directly to n8n unless a custom Freqtrade callback/plugin mechanism is developed to call an n8n webhook.
*   **Configuration for Freqtrade API access:** Stored as n8n credentials (for username/password) and directly in "HTTP Request" nodes (for URLs, headers, etc.).

## Troubleshooting
<!-- source: FT_int_guide.md (adapted), docs/services/n8n/n8n_freqtrade_webhook_ideas.md -->
*   **Action: Check n8n Execution Logs.** Always start by inspecting the detailed execution logs for the specific workflow run within the n8n UI. This will show input/output for each node and any error messages.
*   **"HTTP Request" Node Failures (API Calls):**
    *   **Action: Verify Freqtrade API Credentials.** Ensure the username, password, and subsequently fetched token used in n8n's "HTTP Request" nodes are correct and match Freqtrade's configuration. Use n8n's credential manager.
    *   **Action: Validate Freqtrade API Endpoint URL.** Confirm the URL is accurate and that the Freqtrade API is accessible from the n8n container's network environment.
    *   **Action: Test API Endpoint Directly.** If possible, use `curl` from within the `n8n_mcp` container (e.g., `docker exec -it n8n_mcp bash`) or from another container on the same network to test the Freqtrade API endpoint directly. This helps isolate whether the issue is with Freqtrade or n8n's request.
        ```bash
        # Example if n8n_mcp container has curl:
        # 1. Access n8n container shell:
        # docker exec -it n8n_mcp bash
        # 2. Test authentication (replace with actual credentials):
        # curl -u your_freqtrade_user:your_freqtrade_pass -X POST http://freqtrade_devcontainer:8080/api/v1/token/user
        # 3. If successful, copy the access_token and test another endpoint:
        # TOKEN="<paste_access_token_here>"
        # curl -H "Authorization: Bearer $TOKEN" http://freqtrade_devcontainer:8080/api/v1/status
        ```
*   **"Execute Command" Node Failures (CLI Calls):**
    *   **Action: Confirm `N8N_ALLOW_EXEC=true`.** This environment variable must be set to `true` for the n8n service in its Docker configuration (e.g., `compose-mcp.yml`) for the "Execute Command" node to function.
    *   **Action: Verify Command Syntax.** Ensure the `freqtrade` command and all its arguments are syntactically correct.
    *   **Action: Test Command Manually in Freqtrade Container.** Execute the exact command manually by `exec`-ing into the `freqtrade_devcontainer` to confirm it runs correctly there and produces the expected output.
        ```bash
        # Example:
        # docker exec -it freqtrade_devcontainer bash
        # freqtrade backtesting --strategy MyStrategy --timerange 20230101-
        ```
    *   **Action: Check Permissions.** If the command involves file system access within the Freqtrade container, ensure the necessary permissions are in place.
    *   **Action: Examine `stdout` and `stderr`.** Review the `stdout` and `stderr` outputs provided by the "Execute Command" node in the n8n execution log for error details.
*   **Action: Verify Network Connectivity.** Ensure the `n8n_mcp` container and the `freqtrade_devcontainer` (and `controller_mcp` if interaction is via the controller) are on the same Docker network (e.g., `mcp-net`) and can resolve each other's service names.
*   **Action: Debug Data Parsing.** If extracting data from Freqtrade API responses or CLI output, carefully inspect the structure of the incoming data. Use n8n's expression editor and the output inspector for each node to verify that your parsing logic (in "Function" nodes, "Set" nodes, or other data manipulation nodes) is correct.
