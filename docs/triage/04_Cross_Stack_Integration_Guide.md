# 04: Cross-Stack Integration Guide

**Status:** Consolidated Document - $(date +%Y-%m-%d)

This document details how services within the `automation-stack` and `freqtrade` environments interact, focusing on API communication, authentication, and data flows.

## 1. Core Integration Patterns

Services within the auto-stack interact primarily through REST APIs over the internal Docker network (`auto-stack-net`). Key integrations include:

- **`freq-chat` (UI) <-> Backend Services:** The primary user interface, `freq-chat`, interacts with Mem0 for memory, LLM providers (directly or via a proxy), and can trigger n8n workflows or Controller actions.
- **n8n <-> Controller (FastAPI):** n8n workflows call Controller API endpoints to delegate tasks or receive commands.
- **Controller (FastAPI) <-> Freqtrade API:** The Controller acts as a secure intermediary to the Freqtrade bot.
- **Mem0 <-> All Services:** The Mem0 service provides a centralized long-term memory accessible by the Controller, n8n, and `freq-chat`.
- **n8n <-> OpenRouter Proxy:** n8n workflows leverage the proxy to access a wide range of external LLM models.
- **Shared Volumes:** Services can exchange file-based data through shared Docker volumes.

## 2. n8n <-> Controller (FastAPI) Integration

- **Mechanism:** n8n workflows use the "HTTP Request" node to call API endpoints on the `controller_auto` service.
- **Controller Endpoints:**
  - `POST /execute`: Can be called to trigger the master n8n webhook defined by `N8N_WEBHOOK_URL`.
  - `POST /notify`: Allows n8n workflows to send status updates or results back to the controller.
  - Custom endpoints for specific tasks (e.g., "initiate Freqtrade backtest").
- **Communication:** Internal Docker network, e.g., `http://controller_auto:5050/...`
- **Authentication:** If the Controller API is secured (e.g., with `CONTROLLER_API_KEY`), n8n HTTP Request nodes must include the key in an `Authorization: Bearer <key>` header.

## 3. Controller (FastAPI) <-> Freqtrade API Integration

This is a key integration for enabling automated Freqtrade operations from the `automation-stack`.

- **Mechanism:** The Controller makes HTTP requests to the Freqtrade API, typically running at `http://freqtrade_devcontainer:8080/api/v1/...` on the shared Docker network.
- **Purpose:**
  - Fetch Freqtrade status, version, and health.
  - List trades, performance data, and stats.
  - Initiate backtests and hyperopts.
  - Manage live trades (with caution).
- **Authentication (Freqtrade API):**
  - Freqtrade's API uses JWT (JSON Web Token) authentication, configured via `api_server.username` and `api_server.password` in `user_data/config.json`.
  - **Flow:**
    1. The Controller requests a token from `POST /api/v1/token/auth` using the username and password.
    2. Freqtrade responds with an `access_token`.
    3. The Controller includes this token in an `Authorization: Bearer <token>` header for all subsequent Freqtrade API calls.
    4. The Controller is responsible for managing token expiration and renewal.
- **Example Request (after auth):**
  - `GET http://freqtrade_devcontainer:8080/api/v1/status`
  - Headers: `Authorization: Bearer <retrieved_access_token>`

## 4. Mem0 <-> Other Services Integration

Mem0 (`mem0_auto`) provides a REST API for centralized memory and knowledge management, routing its LLM/embedding needs through the Controller.

### 4.1 Controller <-> Mem0

- **Mechanism:** The Controller calls the Mem0 API using a client library like `httpx`.
- **Configuration:** The Controller's `.env` must have `MEM0_API_URL` set to `http://mem0_auto:8000` and a `MEM0_API_KEY` for authentication.
- **Endpoints:**
  - `POST /memory`: Adds a new memory entry.
  - `POST /search`: Searches existing memories.
  - `GET /status`: Checks service health.
- **Use Cases:** Storing context for long-running tasks, retrieving knowledge to inform actions, and maintaining task state.

### 4.2 n8n <-> Mem0

- **Mechanism:** n8n workflows use the "HTTP Request" node to call the Mem0 API at `http://mem0_auto:8000`.
- **Authentication:** The `MEM0_API_KEY` must be included as a Bearer token in the request headers.
- **Use Cases:** Storing workflow results, retrieving context to influence workflow decisions, and giving n8n-orchestrated agents persistent memory.

### 4.3 `freq-chat` <-> Mem0

- **Mechanism:** The `freq-chat` backend (Next.js API routes) calls the Mem0 API.
- **Configuration:** `freq-chat` requires environment variables for Mem0's URL and API key.
- **Use Cases:** Maintaining conversational history, implementing RAG (Retrieval Augmented Generation) by augmenting prompts with context from Mem0, and personalizing the user experience.

### 4.4 Cursor <-> Mem0

- **Mechanism:** Direct integration with the self-hosted Mem0 via Cursor's native MCP is not supported out-of-the-box. The official `mem0-mcp` server connects to the Mem0 Cloud Platform.
- **To use Cursor with self-hosted Mem0, an adaptation is required:**
    1. Modify the `mem0-mcp` server to use the self-hosted Mem0 REST API as its backend.
    2. Build a new wrapper service that translates MCP requests into REST calls for the `mem0_auto` service.
- **Use Cases (with adaptation):** Allowing Cursor to use the same memory and knowledge base as the rest of the stack for tasks like adding observations and searching history.

## 5. n8n <-> OpenRouter Proxy Integration

This pattern allows n8n workflows to access a wide range of LLMs from OpenRouter.ai via a managed proxy.

- **Mechanism:** n8n workflows use the "HTTP Request" node to call the `openrouter_proxy_auto` service.
- **Endpoint:** `http://openrouter-proxy.localhost/v1/chat/completions` (via Traefik).
- **Payload:** Standard OpenAI API request format.
- **Authentication:** The `openrouter_proxy_auto` service injects the `OPENROUTER_API_KEY`. The n8n request node should send a dummy `Authorization: Bearer sk-dummykey` header.
- **Response:** Standard OpenAI API response format.
- **n8nChat and AI Nodes:** The **n8nChat browser extension** and n8n's **AI/MCP nodes** can also be configured to use this proxy, enabling natural language workflow creation and the ability to expose n8n workflows as callable tools for other AI agents.

## 6. n8n Webhook Usage (General)

- **As a Trigger:** Workflows starting with a "Webhook" node generate a unique URL. External services (like the Controller or GitHub) can `POST` data to this URL to trigger the workflow.
- **As a Caller:** The "HTTP Request" node can `POST` data to webhooks exposed by other services (e.g., a `freq-chat` API route).
- **Authentication:** n8n webhooks can be secured with Header or Basic Auth. When calling external webhooks, n8n must provide the authentication required by the target service.

## 7. General API Best Practices

- Use HTTPS for all external communication (Traefik can handle SSL).
- Validate incoming data and API responses.
- Implement robust error handling and logging in all services.
- Use environment variables for all secrets, keys, and URLs.

## 8. Shared Documentation & File Access

While APIs are preferred for dynamic data, shared volumes can be used for file-based exchange. This is configured by mounting the same Docker volume into multiple service definitions in the `docker-compose.yml` file.
