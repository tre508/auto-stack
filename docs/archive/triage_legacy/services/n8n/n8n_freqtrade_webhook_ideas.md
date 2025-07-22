## Status: ⏳ To Be Rebuilt

# n8n Workflow: Integrating with Freqtrade (Ideas & Patterns)

⚠️ **CONTEXT:** This document outlines **conceptual ideas and patterns** for integrating n8n with Freqtrade, primarily focusing on getting data or events *from* Freqtrade *into* n8n. The **Freqtrade API Polling** method is generally the most suitable for the current `automation-stack` and `freqtrade` devcontainer architecture.

<!-- TODO: Evaluate these patterns against Freqtrade's current capabilities (API, DB structure) and the desired integration goals. -->
<!-- TODO: If a specific pattern (e.g., API polling) is chosen, create detailed documentation for that implementation, including necessary Freqtrade configuration (enabling API, authentication) and n8n workflow setup. -->
<!-- TODO: Update example service names/ports (e.g., `freqtrade_devcontainer:8080`) to match the current devcontainer setup if API polling examples are developed. -->

Integrating n8n directly with Freqtrade for real-time events ideally requires Freqtrade to emit signals (e.g., webhooks). However, polling mechanisms via Freqtrade's API or database are common and practical alternatives.

## Goal

Trigger n8n workflows based on Freqtrade events (e.g., trades, errors, status changes) or data (e.g., performance metrics).

## Potential Integration Methods
(These are general integration strategies)

1.  **Webhook Support (Ideal but Requires Freqtrade Enhancement/Plugin):**
    *   **Concept:** Freqtrade could be modified or configured via a plugin/callback to send HTTP POST requests (webhooks) to an n8n Webhook Trigger node upon events like `trade_entry`, `trade_exit`, `strategy_error`.
    *   **n8n Setup:** Create a workflow starting with the **Webhook** trigger node. n8n provides a URL. Freqtrade would be configured to send JSON payloads to this URL.
    *   **Pros:** Real-time, event-driven, clean integration.
    *   **Cons:** Typically requires Freqtrade core changes or a suitable, well-maintained plugin that offers this capability.

2.  **Database Monitoring:**
    *   **Concept:** Freqtrade stores trade data in a database (SQLite by default, but configurable to others like PostgreSQL). n8n can periodically query this database.
    *   **n8n Setup:**
        *   Use a **Schedule** trigger node.
        *   Use a database node (e.g., **SQLite**, **PostgreSQL**) in n8n.
        *   **Configuration for Current Stack:**
            *   **SQLite:** If Freqtrade (in the `freqtrade_devcontainer`) uses its default SQLite DB, the n8n container (in `automation-stack`) needs access to this `.sqlite` file. This would require a shared Docker volume mapping the Freqtrade database file/directory to a path accessible by the n8n container. This can be complex to manage due to potential file locks and path consistencies across different container setups.
            *   **PostgreSQL/Networked DB (Recommended):** A cleaner approach is to configure Freqtrade to use a networked database (e.g., a PostgreSQL container). This database service would need to be accessible from the n8n container, typically by ensuring both Freqtrade's DB and n8n are on the same Docker network (e.g., `mcp-net`) or that the DB is properly exposed.
        *   Write SQL queries (e.g., `SELECT * FROM trades WHERE open_timestamp > :last_checked_time`).
        *   Use **Function** or **Set** nodes in n8n to store the timestamp of the last check for the next polling cycle.
    *   **Pros:** Doesn't require Freqtrade modification if DB is accessible.
    *   **Cons:** Not real-time (polling delay); potential database load; SQLite access from a separate container can be problematic, favoring a networked DB approach.

3.  **Log File Parsing:**
    *   **Concept:** Monitor Freqtrade's log files for specific patterns.
    *   **n8n Setup for Current Stack:**
        *   Requires n8n to have access to the Freqtrade log volume. The Freqtrade container (e.g., `freqtrade_devcontainer`) would need to write logs to a directory on a shared Docker volume that the n8n container also mounts. This is **not a default configuration** and requires manual `compose-mcp.yml` (for n8n) and Freqtrade's Docker setup modifications.
        *   Requires `N8N_ALLOW_EXEC=true` for n8n service (security implication, not default).
        *   Use a **Schedule** trigger and an **Execute Command** node (e.g., `tail`, `grep`).
        *   Use **Function** or **Regex Extractor** nodes to parse data.
    *   **Pros:** Doesn't require Freqtrade modification (beyond log sharing).
    *   **Cons:** Brittle (log format changes break parsing); not real-time; complex parsing; file access and `N8N_ALLOW_EXEC` requirements introduce complexity and security considerations.

4.  **Freqtrade API Polling (Recommended for Current Stack):**
    *   **Concept:** Freqtrade has a comprehensive REST API. n8n can poll API endpoints for trade history, status, performance, etc.
    *   **Freqtrade Configuration (in `config.json` or via ENV vars for Freqtrade container):**
        *   Enable the API server: `"api_server": { "enabled": true, "listen_ip_address": "0.0.0.0", ... }`.
        *   Set up API authentication (username/password for JWT): `"api_server": { ..., "username": "your_api_user", "password": "your_api_password", ... }`.
        *   Ensure the Freqtrade container (e.g., `freqtrade_devcontainer` from its own Docker setup) is connected to a Docker network that the `n8n_mcp` container can reach (e.g., both connected to `mcp-net`, or Traefik routing if Freqtrade is exposed via Traefik).
    *   **n8n Workflow Setup:**
        *   Use a **Schedule** trigger (e.g., every minute).
        *   **Step 1: Get JWT Token (if first time or token expired):**
            *   **HTTP Request Node:**
                *   Method: `POST`
                *   URL: `http://freqtrade_devcontainer:8080/api/v1/token/user` (Note: `freqtrade_devcontainer` is the typical service name for Freqtrade in its devcontainer Docker Compose setup. Port `8080` is the Freqtrade default. This assumes direct container-to-container communication on a shared Docker network like `mcp-net`. If Traefik is used to expose Freqtrade, the URL might be `http://freqtrade.localhost/api/v1/token/user` or similar, depending on Traefik rules.)
                *   Body Type: `JSON`
                *   Body: `{"username": "your_api_user", "password": "your_api_password"}` (use credentials from n8n credential store if possible)
                *   Output: Store the `token` from the response.
        *   **Step 2: Poll Freqtrade API Endpoint(s):**
            *   **HTTP Request Node:**
                *   Method: `GET`
                *   URL examples:
                    *   `http://freqtrade_devcontainer:8080/api/v1/trades`
                    *   `http://freqtrade_devcontainer:8080/api/v1/status`
                    *   `http://freqtrade_devcontainer:8080/api/v1/performance`
                    *   (Adjust service name/port/path as per your setup and API documentation)
                *   Authentication: `Header Auth`
                *   Name: `Authorization`
                *   Value: `Bearer {{ $item(0).$node["Get JWT Token"].json["token"] }}` (adjust expression to get token from previous step)
        *   **Step 3: Process Data:**
            *   Use **Function**, **Set**, or **IF** nodes to compare data with previous polls (e.g., to identify new trades since last check by comparing trade IDs or timestamps).
    *   **Pros:** Generally robust; utilizes Freqtrade's intended interface for external tools; cleaner than log parsing.
    *   **Cons:** Not real-time (polling delay); relies on API availability and stability; initial setup for token-based authentication.

## Example Use Cases
(Conceptual examples assuming an integration method is chosen)

Assuming an integration method is established (e.g., webhooks):

*   **Trade Notifications:** Send detailed trade entry/exit notifications to Discord/Slack.
*   **Error Alerts:** Immediately notify on critical strategy errors found in logs or via webhook.
*   **Performance Summary:** Periodically query trade data (via DB or API), calculate performance metrics, and send a summary report (potentially using Ollama for summarization).
*   **External Data Trigger:** Use n8n to fetch external market data/news and potentially trigger Freqtrade actions via its API (if available and secure).

## Conclusion
(Conceptually valid summary)

Direct, real-time integration often requires Freqtrade to actively send data out (like webhooks). Indirect methods like DB/API polling or log parsing are alternatives but come with trade-offs in timeliness and reliability. Choose the pattern that best fits the available mechanisms and your tolerance for complexity and delay. 