# Freqtrade-Controller Integration Guide

**Note for AI Agent:** This guide explains how the FastAPI Controller (`controller_auto` service) interacts with Freqtrade. Use this document to understand how the Controller authenticates with Freqtrade, calls its API, and what configurations are necessary on both the Controller and Freqtrade side for this integration to function.

## Purpose
<!-- source: docs/setup/04_Cross_Stack_Integration_Guide.md, docs/setup/05_Agent_Capabilities_and_Interaction.md -->
This document details how the FastAPI Controller (`controller_auto` service) integrates with and manages interactions with the Freqtrade API. The Controller serves as a secure and potentially logic-augmented bridge, enabling other services within the `automation-stack` (such as `freq-chat` or n8n agent workflows) to access Freqtrade functionalities without needing to handle Freqtrade API specifics like authentication directly.

## Architecture
<!-- source: docs/setup/04_Cross_Stack_Integration_Guide.md -->
The FastAPI Controller is a Python application running as part of the `automation-stack`. Its key architectural roles in Freqtrade integration are:
*   **Communication Bridge:** It communicates with the Freqtrade API (typically exposed at `http://freqtrade_devcontainer:8080/api/v1/...`) over the shared Docker network (e.g., `auto-stack-net`).
*   **Authentication Handler:** It manages the JWT (JSON Web Token) authentication required by the Freqtrade API, abstracting this complexity from its clients.
*   **Custom API Endpoints:** It exposes its own set of API endpoints (e.g., `/api/v1/freqtrade/status`) that can trigger specific Freqtrade operations or data retrieval.

## Integration Flow
<!-- source: docs/setup/04_Cross_Stack_Integration_Guide.md -->
The typical flow of interaction is as follows:

### 1. Receiving Client Requests
The Controller has dedicated API endpoints for Freqtrade-related actions (e.g., `/api/v1/freqtrade/status`, `/api/v1/freqtrade/get_trades`, `/api/v1/freqtrade/backtest`). Clients (like n8n workflows, the `freq-chat` backend, or other AI agents) call these endpoints. The request payloads may include parameters necessary for the Freqtrade operation (e.g., strategy name, time range for backtesting).

### 2. Authenticating with Freqtrade API
Before making any calls to Freqtrade, the Controller must authenticate:
*   It uses stored credentials (ideally configured via environment variables like `FREQTRADE_API_USER` and `FREQTRADE_API_PASSWORD`) to make a POST request to Freqtrade's token authentication endpoint (e.g., `/api/v1/token/auth` or `/api/v1/token/user`).
*   Freqtrade responds with an `access_token`.
*   The Controller includes this `access_token` as a Bearer token in the `Authorization` header for all subsequent API calls to Freqtrade.
*   The Controller should implement logic to manage the token's lifecycle, such as caching the token and renewing it when it expires or before it expires.

### 3. Calling Freqtrade API Endpoints
Based on the specific client request to its own endpoint, the Controller makes the appropriate HTTP calls to the Freqtrade API. This might involve:
*   Fetching status: `GET /api/v1/ping`, `GET /api/v1/status`
*   Listing trades or performance: `GET /api/v1/trades`, `GET /api/v1/performance`
*   Initiating actions (if Freqtrade API supports them directly): e.g., `POST /api/v1/forcebuy` (use with extreme caution).
*   For operations like backtests or hyperparameter optimization, which are primarily CLI-driven in Freqtrade, the Controller might trigger an n8n workflow designed to execute these CLI commands (see `freqtrade_n8n.md`).

The Controller uses Python HTTP client libraries like `httpx` or `requests` for these interactions.

### 4. Processing and Returning Responses
The Controller receives JSON responses from the Freqtrade API. It may:
*   Relay the raw JSON response directly to its client.
*   Process, filter, or transform the data into a more suitable format before returning it.
*   Aggregate data from multiple Freqtrade API calls.

## Input/Output Data Formats

*   **Input to Controller (from its clients):** JSON payloads specific to the Controller's defined Freqtrade-related endpoints. For example, a request to trigger a backtest might look like: `{"strategy_name": "MyAwesomeStrategy", "timerange": "20230101-20231231"}`.
*   **Output from Controller (to Freqtrade API):** Standard HTTP requests with JSON payloads as required by the Freqtrade API (e.g., for authentication).
*   **Input to Controller (from Freqtrade API):** JSON responses from various Freqtrade API endpoints.
*   **Output from Controller (to its clients):** JSON responses, either raw from Freqtrade or processed by the Controller.

## Config Requirements

### Controller-Side Configuration
*   **Environment Variables:**
    *   `FREQTRADE_API_URL`: The base URL for the Freqtrade API (e.g., `http://freqtrade_devcontainer:8080`).
    *   `FREQTRADE_API_USER`: The username for Freqtrade API authentication.
    *   `FREQTRADE_API_PASSWORD`: The password for Freqtrade API authentication.
*   **Python Dependencies:** Libraries like `httpx` or `requests` must be listed in the Controller's `requirements.txt`.
    <!-- source: docs/setup/04_Cross_Stack_Integration_Guide.md (general mention of Python HTTP libraries) -->

### Freqtrade-Side Configuration
Refer to the [Freqtrade Master Integration Guide](./FT_int_guide.md#config-requirements-freqtrade-side) for Freqtrade-specific setup, including:
*   API server enabled in `user_data/config.json` with matching credentials.
*   Network accessibility (e.g., on `mcp-net`).

## Dependencies or Env Vars Needed
(Covered in "Config Requirements" above.)

## Failover or Fallback Behavior
The FastAPI Controller must implement robust error handling for its interactions with the Freqtrade API:
*   **Network Errors:** Catch exceptions related to network issues (e.g., timeouts, connection refused if Freqtrade is down).
*   **HTTP Errors:** Properly handle HTTP error status codes from Freqtrade (e.g., 401 Unauthorized, 403 Forbidden, 404 Not Found, 500 Internal Server Error).
*   **Logging:** Implement detailed logging of requests to Freqtrade, responses received, and any errors encountered. This is crucial for debugging integration issues.
*   **Client Responses:** Return meaningful error messages and appropriate HTTP status codes to its own clients when Freqtrade interactions fail.
*   **Retries (Optional):** Consider implementing a retry mechanism (e.g., with exponential backoff) for transient network errors when calling Freqtrade.

## Where prompts, signals, or configs are injected

*   **Prompts/Commands for Freqtrade:** These are injected into the Controller via the request bodies of its API endpoints, sent by clients like n8n or `freq-chat`.
*   **Signals from Freqtrade:** The Controller actively polls or requests data from Freqtrade. Freqtrade does not typically push signals directly to the Controller in this architecture.
*   **Configuration for Freqtrade API Access:** These (URL, user, password) are injected into the Controller primarily through environment variables.

## Troubleshooting
<!-- source: FT_int_guide.md (adapted) -->
*   **Action: Examine Controller Logs.** Check the Docker logs for the `controller_auto` service: `docker logs controller_auto`. Look for error messages related to Freqtrade API calls, authentication failures, or network issues.
*   **Action: Verify Environment Variables.** Ensure that `FREQTRADE_API_URL`, `FREQTRADE_API_USER`, and `FREQTRADE_API_PASSWORD` are correctly set in the Controller's environment and are available to the service.
*   **Action: Test Freqtrade API Directly from Controller Container.** To isolate whether the issue is with the Controller's logic or Freqtrade itself, execute `curl` commands from within the `controller_auto` container:
    1.  Access the container shell: `docker exec -it controller_auto bash`
    2.  Test authentication (replace `your_freqtrade_user` and `your_freqtrade_pass` with actual credentials):
        ```bash
        curl -u your_freqtrade_user:your_freqtrade_pass -X POST http://freqtrade_devcontainer:8080/api/v1/token/user
        ```
    3.  If authentication is successful, copy the `access_token` from the response.
    4.  Test another Freqtrade API endpoint using the token:
        ```bash
        TOKEN="<paste_access_token_here>"
        curl -H "Authorization: Bearer $TOKEN" http://freqtrade_devcontainer:8080/api/v1/status
        ```
*   **Action: Confirm Network Connectivity.** Verify that the `controller_auto` container can resolve and reach the `freqtrade_devcontainer` service name on the shared Docker network (e.g., `auto-stack-net`).
*   **Action: Check Freqtrade API Status.** Ensure the Freqtrade API is enabled, running, and responsive as detailed in the [Freqtrade Master Integration Guide](./FT_int_guide.md#troubleshooting-common-integration-issues).
