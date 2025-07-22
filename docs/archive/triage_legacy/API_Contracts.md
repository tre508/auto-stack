# API Contracts and Interface Definitions

**Status:** New Document - $(date +%Y-%m-%d)

This document serves as the single source of truth for the API contracts between the services in the `auto-stack`. All services exposing an API should have their endpoints, request/response schemas, and authentication methods formally defined here.

---

## 1. `controller_auto` (FastAPI Controller)

* **Internal URL:** `http://controller_auto:5050`
* **External URL (via Traefik):** `http://controller.localhost/`
* **Swagger/OpenAPI Docs:** `http://controller.localhost/docs`
* **Authentication:** Varies by endpoint. Can include API Key (`X-API-Key` header) for sensitive operations.

### Standard Endpoints

#### `GET /status`

* **Description:** Returns the operational status of the controller.
* **Authentication:** None.
* **Response (200 OK):**

    ```json
    {
      "status": "Controller is running"
    }
    ```

#### `POST /execute`

* **Description:** Triggers the primary n8n webhook defined by `N8N_WEBHOOK_URL`. Used for initiating master agent workflows.
* **Authentication:** API Key (`X-API-Key: ${CONTROLLER_API_KEY}`).
* **Request Body:**

    ```json
    {
      "command": "string",
      "args": {
        "arg1": "value1"
      },
      "metadata": {
        "source": "string (e.g., 'freq-chat')",
        "user_id": "string"
      }
    }
    ```

* **Response (202 Accepted):** An immediate acknowledgment that the request was received and is being processed asynchronously by n8n.

### Mem0 Proxy Endpoints

These endpoints are for internal use by the `mem0_auto` service and should not be called directly by other clients. The controller acts as a proxy, adding authentication and routing logic.

#### `POST /mem0_openai_proxy/v1/embeddings`

* **Description:** Proxies embedding requests from Mem0 to the Hugging Face Space API specified by `HF_SPACE_EMBEDDER_ENDPOINT`.
* **Authentication:** Expects a Bearer token (`Authorization: Bearer ${HF_TOKEN}`) from Mem0, which is then forwarded to the HF Space.
* **Request/Response:** Follows the OpenAI Embeddings API format.

#### `POST /mem0_openai_proxy/v1/chat/completions`

* **Description:** Proxies chat completion (LLM) requests from Mem0 to the `openrouter_proxy_auto` service.
* **Authentication:** Uses its own `CONTROLLER_OPENROUTER_API_KEY` when calling the proxy.
* **Request/Response:** Follows the OpenAI Chat Completions API format.

---

## 2. `mem0_auto` (Self-Hosted Mem0 Service)

* **Internal URL:** `http://mem0_auto:8000`
* **External URL (via Traefik):** `http://mem0.localhost/` (if configured)
* **Swagger/OpenAPI Docs:** `http://mem0.localhost/docs`
* **Authentication:** None for the self-hosted REST API itself. Access is controlled by network exposure.

#### `GET /status`

* **Description:** Returns the operational status of the Mem0 service.
* **Response (200 OK):**

    ```json
    {
      "status": "Mem0 service is running and client is healthy"
    }
    ```

#### `POST /memory`

* **Description:** Adds a new memory.
* **Request Body:**

    ```json
    {
      "messages": [
        {
          "role": "user",
          "content": "string"
        }
      ],
      "user_id": "string (optional)",
      "agent_id": "string (optional)",
      "metadata": "object (optional)"
    }
    ```

* **Response (200 OK):** Confirmation message.

#### `POST /search`

* **Description:** Searches for a memory.
* **Request Body:**

    ```json
    {
      "query": "string",
      "user_id": "string (optional)",
      "agent_id": "string (optional)",
      "metadata": "object (optional)"
    }
    ```

* **Response (200 OK):** An array of search results.

---

## 3. `openrouter_proxy_auto` (OpenRouter Proxy)

* **Internal URL:** `http://openrouter_proxy_auto:8000`
* **External URL (via Traefik):** `http://openrouter-proxy.localhost/`
* **Authentication:** The proxy injects the `OPENROUTER_API_KEY` for outgoing requests. Clients can use a dummy API key.

#### `GET /healthz`

* **Description:** Health check endpoint.
* **Response (200 OK):** `OK`

#### `POST /v1/chat/completions`

* **Description:** Proxies requests to OpenRouter.ai's chat completions endpoint.
* **Request/Response:** Follows the OpenAI Chat Completions API format.

---

## 4. `n8n_auto` (n8n Webhooks)

This section defines key webhook endpoints exposed by n8n workflows.

### CentralBrain Agent Webhook

* **Endpoint:** `/webhook/centralbrain_agent`
* **URL:** `http://n8n.localhost/webhook/centralbrain_agent`
* **Method:** `POST`
* **Authentication:** None (relies on unguessable URL).
* **Description:** The primary entry point for the main orchestration agent.
* **Request Body:** See contract for `controller_auto:/execute`.
* **Response:** Asynchronous. The workflow may call back to the `controller_auto:/notify` endpoint or another service.
