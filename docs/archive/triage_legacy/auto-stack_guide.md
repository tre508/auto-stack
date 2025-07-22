# Auto-Stack Integration Guide for Freqtrade Developers

This guide serves as a central reference for developers working within the `freqtrade` environment to understand and interact with the broader `auto-stack` ecosystem. It provides an overview of the architecture, key interaction patterns, API endpoints, and configuration essentials.

## 1. Core Architecture Overview

The `auto-stack` is an AI-powered orchestration and automation layer designed to assist with trading-related tasks, data management, and development workflows. From a `freqtrade` developer's perspective, the most important services are:

-   **Controller (`controller_auto`)**: The central brain of the stack. It exposes a primary API for executing tasks, interacting with the AI agent, and coordinating other services. **Most interactions from `freqtrade` will target the Controller.**
-   **Mem0 (`mem0_auto`)**: The long-term memory service. Used to store and retrieve structured data like trade summaries, strategy performance notes, or configuration snapshots.
-   **n8n (`n8n_auto`)**: The workflow automation engine. It runs scheduled tasks and responds to webhooks to perform automated actions, such as documentation backups or logging events to `Mem0`.
-   **Freq-Chat (`freq_chat_auto`)**: The web-based UI for interacting with the AI agent, which is powered by the `Controller`.
-   **Traefik (`traefik_auto`)**: The reverse proxy that routes requests to all services. All API calls should be made through the ports exposed by Traefik (e.g., `80`, `8080`).

## 2. Key Interaction Patterns

As a `freqtrade` developer, you will primarily interact with the stack programmatically to log data, execute tasks, or trigger automations.

### A. Executing a Task via the Controller

The most common interaction is to ask the `Controller` to execute a command or a complex task. This is done by sending a POST request to the `/api/v1/execute` endpoint.

**Use Case**: Your `freqtrade` strategy has just completed a hyperopt run, and you want to trigger a script to analyze and store the results.

**Example `curl` command:**

```bash
# Port 5050 should match CONTROLLER_EXTERNAL_PORT from your .env file
curl -X POST http://localhost:${CONTROLLER_EXTERNAL_PORT:-5050}/api/v1/execute \
-H "Content-Type: application/json" \
-d '{
    "task": "Analyze the latest hyperopt results and save a summary to Mem0",
    "session_id": "freqtrade-hyperopt-run-123"
}'
```

The `Controller` will receive this task, use its AI capabilities to understand the intent, and execute the necessary steps.

### B. Storing Data in Mem0

You can store key-value data directly in `Mem0` for long-term persistence. This is useful for logging trade data, model performance metrics, or any structured information you want to recall later.

**Use Case**: After a trade closes, your `freqtrade` strategy logs the pair, profit, and duration to `Mem0`.

**Example `curl` command (direct to Mem0):**

```bash
# Port 8000 should match MEM0_EXTERNAL_PORT from your .env file
curl -X POST http://localhost:${MEM0_EXTERNAL_PORT:-8000}/v1/memories \
-H "Content-Type: application/json" \
-d '{
    "data": "Closed trade for BTC/USDT. Profit: 2.5%, Duration: 4 hours.",
    "metadata": {
        "source": "freqtrade_strategy_v3",
        "trade_id": "ft_1a2b3c",
        "pair": "BTC/USDT",
        "profit_pct": 0.025
    },
    "user_id": "freqtrade_bot"
}'
```

### C. Triggering an n8n Automation

Automations can be triggered via webhooks. For example, the `Mem0_Memory_Logger` workflow listens for `POST` requests to log data.

**Use Case**: You want to use a predefined `n8n` workflow for logging instead of calling `Mem0` directly.

**Example `curl` command (to `n8n` webhook):**

```bash
# The specific webhook URL can be found in your n8n workflow settings
curl -X POST http://n8n.localhost/webhook/mem0-logger \
-H "Content-Type: application/json" \
-d '{
    "event_type": "trade_summary",
    "payload": {
        "pair": "ETH/USDT",
        "profit": "1.8%"
    }
}'
```

## 3. Core API Reference

The following endpoints on the `Controller` are most relevant for integration.

#### `POST /api/v1/execute`

-   **Description**: The primary endpoint for all task and command execution. It takes a natural language task description.
-   **URL**: `http://localhost:${CONTROLLER_EXTERNAL_PORT:-5050}/api/v1/execute`
-   **Payload**:
    ```json
    {
      "task": "Your detailed request or command.",
      "session_id": "A unique identifier for this interaction or session."
    }
    ```

#### `POST /api/v1/chat/completions`

-   **Description**: For direct, conversational interaction with the AI agent. This is what the `Freq-Chat` UI uses.
-   **URL**: `http://localhost:${CONTROLLER_EXTERNAL_PORT:-5050}/api/v1/chat/completions`
-   **Payload**:
    ```json
    {
      "messages": [
        {
          "role": "user",
          "content": "What was the result of the last backtest?"
        }
      ],
      "session_id": "freqtrade-chat-session-xyz"
    }
    ```

## 4. Configuration & Service Verification

To ensure the stack is operational, use the following checks.

### A. Environment Configuration (`.env`)

Your `freqtrade` workspace may need to know the following ports defined in the root `.env` file of the `auto-stack`:

-   `CONTROLLER_EXTERNAL_PORT`: The port for the Controller API (default: `5050`).
-   `MEM0_EXTERNAL_PORT`: The port for the Mem0 API (default: `8000`).
-   `N8N_TRAEFIK_HOST`: The hostname for n8n (default: `n8n.localhost`), accessible on port `80`.
-   `TRAEFIK_DASHBOARD_PORT`: The port for the Traefik dashboard (default: `8080`).

### B. Service Health Checklist

1.  **Traefik Dashboard**: Open `http://localhost:${TRAEFIK_DASHBOARD_PORT:-8080}/dashboard/`. You should see green lights for all services (`controller_auto`, `mem0_auto`, etc.).
2.  **n8n UI**: Navigate to `http://${N8N_TRAEFIK_HOST:-n8n.localhost}` (usually on port 80 via Traefik). You should be able to log in and see your workflows.
3.  **Controller Health**: Visit `http://localhost:${CONTROLLER_EXTERNAL_PORT:-5050}/health`. It should return `{"status": "ok"}`.
4.  **Mem0 Health**: Visit `http://localhost:${MEM0_EXTERNAL_PORT:-8000}/health`. It should return `{"status": "ok"}`.

## 5. Developer Workflow

Always follow the **Focused Workflow** principle for development:

1.  Open your terminal in WSL.
2.  Navigate (`cd`) into the specific sub-project you are working on (e.g., `/path/to/auto-stack/freqtrade-user-data`).
3.  Run `code .` from *within that directory* to launch VS Code.

This ensures that all local tools, extensions, and configurations (like the `.vscode/settings.json` in this workspace) are loaded correctly.
