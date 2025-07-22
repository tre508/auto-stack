# Freqtrade Master Integration Guide

**Note for AI Agent:** This guide is designed to provide you with a comprehensive understanding of how Freqtrade integrates with the `automation-stack`. Refer to the specific sections when you need to understand architecture, identify integration methods, configure Freqtrade for API access, or troubleshoot issues. The service-specific guides linked at the end provide more granular details for `controller`, `n8n`, and `mem0` interactions.

## Purpose
<!-- source: Task Description -->
This guide provides a comprehensive overview of Freqtrade's integration within the `automation-stack`. It is intended for AI agents and developers who need to understand the architecture, interfacing services, integration strategies, common workflows, and configuration caveats related to Freqtrade interactions.

## Architecture
<!-- source: docs/reference/dual-stack-architecture.md, docs/setup/02_Trading.md, docs/setup/04_Cross_Stack_Integration_Guide.md, docs/setup/01_Automation_Stack_Overview.md, docs/setup/05_Agent_Capabilities_and_Interaction.md, docs/setup/Freqtrade_Project_Checklist.md -->
The system operates on a dual-stack model: the `automation-stack` (handling orchestration, AI, and tooling) and the `freqtrade` dev container (dedicated to trading logic, backtesting, and providing an API).

### 1. Dual-Stack Model
The `freqtrade` environment runs as a VS Code Dev Container, ensuring a consistent and isolated setup. This container exposes Freqtrade's UI and, crucially, its REST API for external interactions.
<!-- source: docs/reference/dual-stack-architecture.md, docs/setup/02_Trading.md -->

### 2. Key Interfacing Services from `automation-stack`
Several services within the `automation-stack` interact with Freqtrade:
*   **FastAPI Controller (`controller_auto`):** This Python-based service often acts as the primary bridge to Freqtrade. It makes authenticated API calls to Freqtrade and can expose simplified endpoints for other services or agents.
    <!-- source: docs/setup/04_Cross_Stack_Integration_Guide.md, docs/setup/01_Automation_Stack_Overview.md -->
*   **n8n (`n8n_auto`):** The workflow automation platform. n8n can interact with Freqtrade in multiple ways:
    *   Directly polling the Freqtrade API.
    *   Indirectly via the FastAPI Controller.
    *   Orchestrating `freqtrade` CLI commands using its "Execute Command" node, often within agent-based workflows.
    <!-- source: docs/setup/04_Cross_Stack_Integration_Guide.md, docs/services/n8n/prompt_library/CentralBrain.md -->
*   **Mem0 (`mem0_auto`):** The memory service. While Mem0 does not directly connect to Freqtrade, it supports Freqtrade-related tasks by providing persistent memory and knowledge storage for the agents and workflows (like n8n or the Controller) that manage or analyze Freqtrade operations.
    <!-- source: docs/setup/02_Trading.md, docs/setup/05_Agent_Capabilities_and_Interaction.md -->

### 3. Network Configuration for Integration
For successful integration, the Freqtrade container and the relevant `automation-stack` services must reside on the same Docker network (e.g., `auto-stack-net`). This allows services to reach the Freqtrade API, typically at `http://freqtrade_devcontainer:8080/api/v1/...` (using the Freqtrade container's service name).
<!-- source: docs/setup/02_Trading.md, docs/setup/Freqtrade_Project_Checklist.md -->

## Integration Strategies
<!-- source: docs/setup/04_Cross_Stack_Integration_Guide.md, docs/services/n8n/n8n_freqtrade_webhook_ideas.md, docs/reference/dual-stack-architecture.md, docs/services/n8n/prompt_library/CentralBrain.md, docs/setup/Freqtrade_Project_Checklist.md -->
Multiple strategies are employed to integrate Freqtrade with the `automation-stack`:

### 1. Freqtrade REST API (Primary Method)
The cornerstone of integration is Freqtrade's REST API. All programmatic interactions, whether for fetching data or triggering actions (where supported by the API), leverage these endpoints.
*   **Authentication:** The API is typically protected by JWT (JSON Web Token) authentication. Clients (like the FastAPI Controller or n8n workflows) must first obtain an `access_token` by sending credentials (username and password, configured in Freqtrade's `user_data/config.json`) to an authentication endpoint (e.g., `/api/v1/token/auth` or `/api/v1/token/user`). This token is then included as a Bearer token in the `Authorization` header of subsequent API requests.
    <!-- source: docs/setup/04_Cross_Stack_Integration_Guide.md, docs/services/n8n/n8n_freqtrade_webhook_ideas.md -->

### 2. Mediated vs. Direct API Access
*   **FastAPI Controller as Intermediary:** The Controller often abstracts direct Freqtrade API calls, providing a simplified or more secure interface for other services.
*   **n8n Access:** n8n workflows can poll the Freqtrade API directly or route their requests through the FastAPI Controller.
    <!-- source: docs/setup/04_Cross_Stack_Integration_Guide.md, docs/reference/dual-stack-architecture.md -->

### 3. n8n Orchestration of Freqtrade CLI
For operations not readily available or convenient via the REST API (like initiating backtests or hyperparameter optimization), n8n workflows can execute `freqtrade` CLI commands directly within the Freqtrade container. This is often achieved using the "Execute Command" node in n8n, typically as part of an agent-based workflow structure (e.g., `Backtest_Agent`).
<!-- source: docs/services/n8n/prompt_library/CentralBrain.md -->

### 4. Alternative n8n Data Retrieval (Less Common)
While API polling is recommended, n8n can also retrieve Freqtrade data through:
*   **Database Monitoring:** Periodically querying Freqtrade's database. If Freqtrade uses SQLite (default), this requires a shared Docker volume for the database file. A networked database (e.g., PostgreSQL) configured for Freqtrade is a cleaner approach for external access by n8n.
*   **Log File Parsing:** Monitoring Freqtrade's log files. This is generally brittle due to potential log format changes and requires shared volume access and `N8N_ALLOW_EXEC=true` for n8n.
    <!-- source: docs/services/n8n/n8n_freqtrade_webhook_ideas.md -->

### 5. File-Based Exchange (Shared Volumes)
For specific data outputs like backtest results (`user_data/backtest_results/`) or user-maintained documentation (`user_data/docs/`), shared Docker volumes can allow other `automation-stack` services to access these files directly.
<!-- source: docs/setup/Freqtrade_Project_Checklist.md -->

## Common Workflows
<!-- source: docs/setup/04_Cross_Stack_Integration_Guide.md, docs/services/n8n/n8n_freqtrade_webhook_ideas.md, docs/services/n8n/prompt_library/CentralBrain.md, docs/setup/05_Agent_Capabilities_and_Interaction.md, docs/services/n8n/n8n_multi_agent_concepts.md -->

### 1. Fetching Freqtrade Data & Status
The FastAPI Controller or n8n workflows regularly poll Freqtrade API endpoints like `/ping`, `/status`, `/trades`, `/performance` to retrieve operational data and trading status.
<!-- source: docs/setup/04_Cross_Stack_Integration_Guide.md, docs/services/n8n/n8n_freqtrade_webhook_ideas.md -->

### 2. Initiating Freqtrade Operations
*   **Backtests & Hyperparameter Optimization:** These are typically initiated by n8n workflows using the "Execute Command" node to run `freqtrade` CLI commands, or via FastAPI Controller endpoints that encapsulate these CLI calls.
*   **Strategy File Management:** The Controller might facilitate reading strategy files from Freqtrade's `user_data/strategies/` directory or proposing changes, although direct modification is a sensitive operation.
    <!-- source: docs/services/n8n/prompt_library/CentralBrain.md, docs/setup/05_Agent_Capabilities_and_Interaction.md -->

### 3. Multi-Agent Orchestration for Freqtrade Tasks (n8n)
A hierarchical agent model implemented in n8n manages complex Freqtrade automations.
*   A `CentralBrain_Agent` workflow receives high-level commands.
*   It dispatches tasks to a `FreqtradeManager_Agent` workflow.
*   The `FreqtradeManager_Agent` further delegates to specialized sub-agent workflows like `Backtest_Agent`, `TradeExecution_Agent`, or `PerformanceMonitoring_Agent`.
*   Communication between these n8n agent workflows typically occurs via HTTP webhooks.
    <!-- source: docs/services/n8n/prompt_library/CentralBrain.md, docs/setup/05_Agent_Capabilities_and_Interaction.md -->

### 4. Exposing Freqtrade Data/Actions as Callable Tools (n8n)
n8n workflows can use the "MCP Server Trigger" node to expose specific Freqtrade data points (e.g., a profit summary fetched via the API) or actions as callable tools for other AI agents or workflows.
<!-- source: docs/services/n8n/n8n_multi_agent_concepts.md -->

## Config Requirements (Freqtrade Side)
<!-- source: docs/services/n8n/n8n_freqtrade_webhook_ideas.md, docs/setup/04_Cross_Stack_Integration_Guide.md, docs/setup/02_Trading.md, docs/setup/Freqtrade_Project_Checklist.md -->
For successful integration, the Freqtrade environment must be configured correctly:

### 1. `user_data/config.json` - API Server Configuration
To enable API access, the Freqtrade API server **must** be enabled and configured with credentials in `user_data/config.json`. Ensure the following settings are present and correct:
```json
{
  "api_server": {
    "enabled": true,
    "listen_ip_address": "0.0.0.0", // Essential for Docker container accessibility
    "username": "your_api_user",    // Replace with your desired username
    "password": "your_api_password",  // Replace with a strong password
    "jwt_secret_key": "your_strong_jwt_secret_please_change_this", // MUST be changed to a unique, strong secret
    "CORS_origins": [] // Configure if API will be accessed from browser-based applications on different origins
    // Default port is 8080, can be changed here if needed, e.g., "listen_port": 8080
  }
}
```
**Action:** Verify the API port (default `8080`) is correctly set and accessible. The `jwt_secret_key` **must** be a unique, strong, and random string for security.
<!-- source: docs/services/n8n/n8n_freqtrade_webhook_ideas.md, docs/setup/04_Cross_Stack_Integration_Guide.md -->

### 2. Docker Network Configuration
The Freqtrade container must be part of the shared Docker network (e.g., `auto-stack-net`) that the `automation-stack` services use for inter-container communication. This is typically defined in Freqtrade's `docker-compose.yml` file.
<!-- source: docs/setup/02_Trading.md, docs/setup/Freqtrade_Project_Checklist.md -->

### 3. Database Configuration (for n8n DB Monitoring)
If n8n is to monitor Freqtrade's database directly:
*   **SQLite (default):** A shared Docker volume must map Freqtrade's database file/directory to a path accessible by the n8n container.
*   **Networked Database (Recommended):** Configure Freqtrade to use a database service (e.g., PostgreSQL) that is also on the shared Docker network and accessible by n8n.
    <!-- source: docs/services/n8n/n8n_freqtrade_webhook_ideas.md -->

### 4. Shared Volumes (for file-based exchange)
If direct file access is required (e.g., for backtest results), ensure Docker volumes for relevant `user_data` subdirectories are correctly defined in Freqtrade's Docker setup and potentially mountable by `automation-stack` services.
<!-- source: docs/setup/Freqtrade_Project_Checklist.md -->

## Troubleshooting Common Integration Issues
<!-- source: docs/setup/02_Trading.md, docs/services/n8n/n8n_freqtrade_webhook_ideas.md -->

*   **API Unreachable / Connection Refused:**
    *   Verify the Freqtrade container is running (`docker ps`).
    *   Check Freqtrade logs (`docker logs freqtrade_devcontainer`) for startup errors.
    *   Confirm `api_server.enabled` is `true` and `listen_ip_address` is `0.0.0.0` in `user_data/config.json`.
    *   Ensure the Freqtrade container is on the correct shared Docker network (e.g., `auto-stack-net`) with other services.
*   Test connectivity from another container on the same network: `docker exec -it <another_container_name> curl http://freqtrade_devcontainer:8080/api/v1/ping`. **Action:** Perform this test if direct API access issues are suspected.

*   **Authentication Errors (401 Unauthorized):**
    *   **Action:** Verify that the `username` and `password` in Freqtrade's `user_data/config.json` **exactly match** the credentials used by the client service (e.g., FastAPI Controller or n8n).
    *   **Action:** Confirm the client is correctly performing the JWT acquisition step (a `POST` request to `/api/v1/token/auth` or `/api/v1/token/user`) and is including the received `access_token` as a Bearer token in the `Authorization` header of subsequent API calls.
    *   **Action:** Ensure the `jwt_secret_key` in `user_data/config.json` is identical to what Freqtrade is using internally; a mismatch here can cause token validation failures. If changed, Freqtrade must be restarted.

*   **CLI Command Failures (via n8n "Execute Command"):**
    *   **Action:** Validate that the `freqtrade` command syntax is correct. Test the exact command by manually executing it inside the Freqtrade container.
    *   **Action:** Check n8n execution logs for any error messages returned by the executed command.
    *   **Action:** If using the n8n "Execute Command" node, ensure the `N8N_ALLOW_EXEC` environment variable is set to `true` for the n8n service (note the security implications).

*   **Data Discrepancies or Missing Data (when polling):**
    *   **Action:** Review the data polling logic in n8n workflows. Check for correct timestamp comparisons for identifying new trades, proper handling of API pagination if Freqtrade API endpoints use it, and correct parsing of API responses.
    *   Check Freqtrade logs for any errors that might have occurred during the time data was expected.
    *   Ensure the Freqtrade API endpoints being polled are returning the expected data structures.

## Service-Specific Integration Guides (Cross-References)
<!-- source: Task Description -->
For more detailed information on how specific `automation-stack` services integrate with Freqtrade, refer to the following guides:
*   [Freqtrade-Controller Integration](./freqtrade_controller.md)
*   [Freqtrade-n8n Integration](./freqtrade_n8n.md)
*   [Freqtrade-Mem0 Integration (Indirect)](./freqtrade_mem0.md)
