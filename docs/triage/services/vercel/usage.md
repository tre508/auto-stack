# Vercel AI Chat: Usage Guide

**Last updated:** 2025-05-26

This document provides guidance for developers and AI agents on how to interact with and utilize the Vercel AI Chat service (`freq-chat` for local development, or a Vercel deployment) within the `automation-stack`. Refer to `integration.md` for how this service connects to others.

---

## 1. Calling the Vercel AI Chat API Directly

The `freq-chat` service, exposing an OpenAI-compatible endpoint (e.g., `/api/llm`), can be called directly using HTTP requests.

*   **Endpoint (Local Development):** `http://localhost:3000/api/llm` (or the port `freq-chat` is running on).
*   **Endpoint (Conceptual Dockerized `vercel_chat_mcp`):** `http://vercel_chat_mcp:3000/api/llm` (if `freq-chat` were run as `vercel_chat_mcp` in Docker on `mcp-net`).
*   **Method:** `POST`
*   **Headers:**
    *   `Content-Type: application/json`
    *   `Authorization: Bearer <YOUR_API_KEY>` (if the `freq-chat` service itself is protected with an API key).
*   **Body:** Standard OpenAI chat completion request payload.

**Example using `curl`:**

Assuming `freq-chat` is running locally at `http://localhost:3000`.

```bash
# Replace with the actual model name configured/available in your freq-chat
MODEL_NAME="deepseek/deepseek-prover-v2:free" # Example model for OpenRouter

# Example targeting the local dev server
curl -X POST http://localhost:3000/api/llm \
     -H "Content-Type: application/json" \
     -d \'''{
       "model": "${MODEL_NAME}",
       "messages": [{\"role\": "user", "content": "What are the key principles of effective project management?"}],
       "max_tokens": 150,
       "stream": false
     }''' | cat
```

**Example using Python `requests`:**

```python
import requests
import json

VERCEL_CHAT_API_URL = "http://localhost:3000/api/llm" # For local freq-chat dev server

MODEL_NAME = "deepseek/deepseek-prover-v2:free" # Or your configured model

payload = {
    "model": MODEL_NAME,
    "messages": [
        {"role": "system", "content": "You are a helpful assistant specializing in software development."},
        {"role": "user", "content": "Explain the concept of API idempotency."}
    ],
    "max_tokens": 200,
    "temperature": 0.7
}

headers = {
    "Content-Type": "application/json",
    # "Authorization": "Bearer YOUR_FREQ_CHAT_SERVICE_API_KEY" # If your service is protected
}

try:
    response = requests.post(VERCEL_CHAT_API_URL, headers=headers, data=json.dumps(payload))
    response.raise_for_status()
    result = response.json()
    print(result['choices'][0]['message']['content'])
except requests.exceptions.RequestException as e:
    print(f"API call failed: {e}")
```

---

## 2. Using `freq-chat` as an MCP-Compatible Tool (Conceptual)

For AI agents operating within the `automation-stack`, `freq-chat` acts as the primary LLM provider.
*   **Agent Interaction:** An agent needing LLM capabilities would formulate a request to the `freq-chat` API.
*   **Orchestration:** Typically via n8n workflows that call `freq-chat`.
*   **Tool Definition (Abstract):**
    *   **Tool Name:** `invoke_llm_via_freq_chat`
    *   **Input:** Standard OpenAI API request.
    *   **Action:** Sends request to the `freq-chat` service API.
    *   **Output:** Standard OpenAI API response.

---

## 3. LLM Chaining and Advanced Workflows via n8n

n8n is preferred for complex interactions with `freq-chat`.
*   **Single LLM Call:** n8n "HTTP Request" node calls `freq-chat` API.
*   **LLM Chaining:**
    1.  Call `freq-chat` for initial processing.
    2.  n8n logic processes the response.
    3.  Call `freq-chat` again with refined prompt.
*   **Example n8n Workflow Snippet (Conceptual - target `freq-chat` local dev URL or appropriate Docker URL):**
    1.  Webhook Trigger.
    2.  Set Node: Formats prompt for `freq-chat`.
    3.  HTTP Request Node: Sends prompt to `http://localhost:3000/api/llm` (or `http://host.docker.internal:3000/api/llm` if n8n is in Docker and `freq-chat` is on host).
    4.  ... (further processing) ...

---

## 4. Common Use Cases

(Content remains largely the same as these are conceptual use cases of an LLM service)
*   Strategy Brainstorming/Explanation (Freqtrade)
*   Code Generation/Debugging
*   Log Summarization/Analysis
*   Documentation Assistance
*   Natural Language Interface to Systems

---

## 5. Tips for Conversational Memory and Prompt Formatting

(Content remains largely the same as these are general LLM interaction tips)
*   **Conversational Memory:** Managed by the calling application (e.g., `freq-chat` frontend, n8n workflow) by sending chat history.
*   **Effective Prompt Formatting:** Use system prompts, be specific, provide context, use few-shot examples, iterate, request specific output formats.

---

For troubleshooting common issues when using `freq-chat`, refer to `troubleshooting.md`.
