# Vercel AI Chat: Integration Guide

**Last updated:** 2025-05-26

This document describes how the Vercel AI Chat service (`freq-chat` when run locally, or a Vercel deployment) integrates with other components of the `automation-stack`, such as the FastAPI Controller and n8n workflows.

---

## 1. Core API Endpoint

The Vercel AI Chat service (`freq-chat`), especially when built using the Vercel AI SDK and templates like the Next.js AI Chatbot, typically exposes an OpenAI-compatible API endpoint for chat completions.

*   **Standard Endpoint:** `POST /api/llm` (if following Next.js AI Chatbot template pattern, often mapped from a route like `/app/api/llm/route.ts`) or directly `POST /v1/chat/completions` if it strictly emulates an OpenAI-compatible service directly at its root or a `/v1` base path.
*   **Local Development Access:** When `freq-chat` is run locally (e.g., `pnpm run dev`), this endpoint is accessible at `http://localhost:3000/api/llm` (or the relevant port if 3000 is occupied).
*   **Local Docker Service Name (Hypothetical):** If `freq-chat` were containerized as `vercel_chat_mcp` (as older docs might suggest), it would be `http://vercel_chat_mcp:3000/api/llm`. For current local development, direct host access is used.
*   **Payload Structure:** Standard OpenAI chat completion request/response format.
    ```json
    // Request Example
    {
      "model": "your-configured-model-id", // e.g., "deepseek/deepseek-prover-v2:free" via OpenRouter
      "messages": [
        {"role": "user", "content": "Explain quantum computing."}
      ],
      "stream": false
    }
    ```
    ```json
    // Response Example (non-streaming)
    {
      "id": "chatcmpl-xxxx",
      "object": "chat.completion",
      "created": 1677652288,
      "model": "deepseek/deepseek-prover-v2:free",
      "choices": [{
        "index": 0,
        "message": {
          "role": "assistant",
          "content": "Quantum computing is..."
        },
        "finish_reason": "stop"
      }],
      "usage": {
        "prompt_tokens": 9,
        "completion_tokens": 12,
        "total_tokens": 21
      }
    }
    ```
*   This endpoint is the primary way other services (like n8n or the FastAPI controller) will interact with `freq-chat` for LLM functionalities.

---

## 2. Integration with FastAPI Controller (`controller_mcp`)

The `freq-chat` application can interact with the FastAPI Controller (`controller_mcp`):

*   **`freq-chat` calling Controller Endpoints:** The Next.js backend of `freq-chat` can make HTTP requests to the FastAPI controller (e.g., `http://controller_mcp:5050/api/v1/some_endpoint` if both are on `mcp-net`, or `http://localhost:5050/...` if controller is port-mapped to host and `freq-chat` runs on host) to fetch data or trigger actions.
    *   **Example Use Case:** A user asks `freq-chat` to perform an action managed by the controller (e.g., "Get status of Freqtrade bot"). `freq-chat`'s backend would call the relevant controller endpoint.
    *   **Configuration:** `freq-chat` would need the controller's address configured, typically via an environment variable in `.env.development.local` (e.g., `CONTROLLER_FREQCHAT_URL=http://localhost:5050` or `http://controller_mcp:5050`).

*   **Controller calling `freq-chat` (Less Common):** If the controller needed to use an LLM for an internal task, it could call the `freq-chat` API endpoint. However, n8n or `freq-chat` frontend usually orchestrate LLM interactions.

---

## 3. Integration with n8n Workflows (`n8n_mcp`)

n8n plays a crucial role in orchestrating workflows involving `freq-chat`.

*   **n8n Calling `freq-chat` API:**
    *   n8n workflows can use the "HTTP Request" node to send prompts to the `freq-chat` API endpoint (e.g., `http://localhost:3000/api/llm` if n8n can reach the host, or `http://host.docker.internal:3000/api/llm` from n8n Docker container if host networking is set up, or via a Traefik-exposed `freq-chat` URL if `freq-chat` were also Dockerized and exposed).
    *   **Example Node Configuration (HTTP Request in n8n):**
        *   **Method:** `POST`
        *   **URL:** `http://host.docker.internal:3000/api/llm` (Example: n8n Docker to host-running `freq-chat`)
        *   **Body:** `={{ ({ model: 'deepseek/deepseek-prover-v2:free', messages: [{role: 'user', content: $json.prompt_from_previous_node }] }) }}`

*   **`freq-chat` Triggering n8n Workflows (via Webhooks):**
    *   The `freq-chat` backend (Next.js API routes) can trigger n8n workflows by sending HTTP requests to n8n webhook URLs (e.g., `http://n8n_mcp:5678/webhook/some_workflow` or `http://n8n.localhost/webhook/...` via Traefik).
    *   **Configuration:** `freq-chat` would need the n8n webhook URL, via an environment variable in `.env.development.local` (e.g., `N8N_LOGGING_WEBHOOK_URL`).

---

## 4. Environment Variable Examples for Integration

For local `freq-chat` development (`freq-chat/.env.development.local`):
```env
# LLM Provider Configuration (e.g., for OpenRouter)
OPENROUTER_API_KEY=your_openrouter_api_key
# Or other direct LLM keys if freq-chat calls them directly
# OPENAI_API_KEY=your_openai_key

# --- For connecting to other automation-stack services ---
# Assuming controller_mcp is running in Docker and mapped to host port 5050
CONTROLLER_FREQCHAT_URL=http://localhost:5050
# Assuming n8n_mcp is running in Docker and accessible via Traefik or direct port
N8N_WEBHOOK_URL_EXAMPLE=http://localhost:5678/webhook/some_generic_n8n_task

# --- NextAuth.js ---
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your_strong_secret_for_local_dev

# --- Database ---
POSTGRES_URL="postgresql://freqchat_user:your_password@localhost:5432/freqchat_db"
```

---

## 5. Docker Configuration (Hypothetical for `freq-chat`)

While current setup focuses on local `pnpm run dev` for `freq-chat`, if it were to be containerized as `vercel_chat_mcp` (as some older documentation might imply for a fully Dockerized stack), its `compose-mcp.yml` entry would be similar to what was previously outlined, ensuring it's on `mcp-net` and environment variables point to other Docker service names (e.g., `http://controller_mcp:5050`). For now, local development uses host networking or `host.docker.internal` for `freq-chat` to reach Dockerized services.

---

For usage patterns and specific API call examples, refer to `usage.md`.
For troubleshooting, see `troubleshooting.md`.
