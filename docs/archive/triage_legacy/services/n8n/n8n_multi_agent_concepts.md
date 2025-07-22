## Status: ✅ Updated

# n8n Workflow: AI Agent and Multi-Service Coordination Concepts

This document outlines conceptual and practical ways n8n can serve as an orchestrator for tasks involving multiple services or "agents" within the `automation-stack`. It also introduces n8n's native capabilities for building AI-powered workflows using Model Control Protocol (MCP) nodes and integrating with LLMs via your `openrouter_proxy_auto`.

**Note:** n8n is primarily a linear workflow automation tool. While it excels at sequences, its newer AI and MCP nodes are expanding its capabilities for more dynamic interactions.

## Goal

Use n8n to chain together actions across different services (OpenWebUI/Ollama via Proxy, FastAPI Controller, Freqtrade API, external APIs) and leverage LLMs to achieve multi-step objectives, including building simple AI agents and tool-زبpowered workflows.

## Core Concepts in n8n for AI and Orchestration

*   **Linear Flow & Branching:** Workflows execute node by node, with **IF** nodes for conditional logic.
*   **HTTP Requests:** The primary way to interact with other services (FastAPI `controller_auto`, Freqtrade API, `openrouter_proxy_auto`, external tools).
*   **Data Passing:** Each node passes its output data (JSON) to subsequent nodes.
*   **AI Nodes & Model Control Protocol (MCP):** n8n is introducing nodes that facilitate direct interaction with AI models and allow n8n workflows to act as tools for AI agents or for AI agents to be built within n8n.
    *   **OpenAI Node / HTTP Request to Proxy:** For standard LLM calls (chat, embeddings), you can use the generic OpenAI node or a configured HTTP Request node pointing to your `openrouter_proxy_auto` (`http://openrouter-proxy.localhost/v1`). See `docs/proxy.md` for configuration.
    *   **"MCP Client" Node:** This node allows an n8n workflow to act as a client to an MCP-compatible AI model or service. It can send requests to an LLM (potentially via your `openrouter_proxy_auto` if the LLM service is exposed in an MCP-compatible way, or directly if the MCP Client node supports standard OpenAI API calls) and process the response. This is useful for incorporating LLM reasoning or generation steps within a workflow.
    *   **"MCP Server Trigger" Node:** This powerful node allows an n8n workflow to be exposed as a "tool" that an external AI agent (e.g., a custom AI application, potentially n8nChat in the future, or another n8n workflow acting as an agent manager) can call. The workflow defined after an MCP Server Trigger effectively becomes the implementation of that tool.

## Example Coordination & AI Patterns (Reflecting `automation-stack`)

### 1. Information Gathering & LLM Summarization (via Proxy)

*   **Trigger:** Manual, Webhook, or File System trigger (if n8n has volume mounts to `docs/` folders).
*   **Step 1 (File Read/Data Ingest):** Read file content or receive data from trigger.
*   **Step 2 (HTTP Request to `openrouter_proxy_auto`):**
    *   Node: HTTP Request (or potentially "MCP Client" if targeting a compatible LLM endpoint).
    *   URL: `http://openrouter-proxy.localhost/v1/chat/completions`
    *   Method: POST
    *   Body: OpenAI-compatible JSON payload with the content and a prompt like "Summarize this: {{$json.data_to_summarize}}".
    *   Authentication: Bearer token with a dummy key (as per `docs/proxy.md`).
*   **Step 3 (Notification/Output):** Send the LLM's summary (e.g., `{{$json.choices[0].message.content}}`) to Slack, Discord, or return it via webhook.
*   **Coordination:** n8n orchestrates data retrieval, LLM call via the proxy, and result delivery.

### 2. Building an n8n Workflow as an AI Tool (MCP Server)

*   **Goal:** Create an n8n workflow that can, for example, fetch the latest Freqtrade profit summary and make it available as a tool for an AI.
*   **Trigger:** "MCP Server Trigger" Node.
    *   Configure a path (e.g., `/tools/freqtrade-summary`). This path becomes part of the URL an AI client would call.
*   **Step 1 (HTTP Request to Freqtrade):**
    *   Call Freqtrade's API (e.g., `http://freqtrade_devcontainer:8080/api/v1/profit` - verify endpoint and authentication if needed) to get profit data.
*   **Step 2 (Data Formatting - Optional):** Use a Set or Function node to format the Freqtrade data into a clean response suitable for the AI (e.g., a concise summary string).
*   **Step 3 (Tool Response):** The final output of this workflow (the data from Step 1 or 2) is automatically returned to the AI client that called the MCP Server Trigger.
*   **Usage:** An external AI agent (or another n8n workflow using an "MCP Client" node) could be configured to call `http://n8n.localhost/webhook/<MCP_SERVER_TRIGGER_PATH>` (e.g. `http://n8n.localhost/webhook/tools/freqtrade-summary`) to get the Freqtrade profit summary.

### 3. AI Agent within n8n using LLM for Decision Making (MCP Client)

*   **Goal:** An n8n workflow that takes a user query, decides which local service to ask for more info, gets it, and then summarizes.
*   **Trigger:** Webhook with a user query (e.g., `{"query": "What's the status of the controller?"}`).
*   **Step 1 ("MCP Client" Node or HTTP Request to `openrouter_proxy_auto`):
    *   Prompt: "Based on the query '{{$json.query}}', which service should I check: 'controller_auto' or 'freqtrade_devcontainer'? Respond with only the service name."
    *   LLM call via proxy.
*   **Step 2 (IF Node):** Based on LLM response (`{{$json.choices[0].message.content}}`):
    *   If "controller_auto", proceed to Step 3a.
    *   If "freqtrade_devcontainer", proceed to Step 3b.
*   **Step 3a (HTTP Request to `controller_auto`):** Call `http://controller.localhost/status`.
*   **Step 3b (HTTP Request to Freqtrade):** Call `http://freqtrade_devcontainer:8080/api/v1/status` (verify endpoint).
*   **Step 4 (Merge Node - Optional but good practice):** Merge outputs from 3a/3b.
*   **Step 5 ("MCP Client" Node or HTTP Request to `openrouter_proxy_auto`):
    *   Prompt: "Summarize this status information: {{$json.service_status_data}}".
    *   LLM call via proxy.
*   **Step 6 (Output):** Return the summary.
*   **Coordination:** n8n uses an LLM (via proxy) for an initial routing decision, then fetches data, and finally uses the LLM again for summarization.

## n8nChat Integration

As detailed in `docs/n8n/n8nChat.md`, the n8nChat browser extension can be configured to use your `openrouter_proxy_auto`. This enables AI-powered workflow generation and modification directly within the n8n UI, leveraging the models available through your proxy.

Conceptually, n8nChat could also interact with tools exposed by your n8n workflows via the "MCP Server Trigger," allowing for a powerful combination of natural language workflow design and execution of custom n8n-backed tools.

## Limitations

*   **State Management:** While MCP nodes enhance capabilities, complex, long-running stateful agent interactions are still better suited to dedicated frameworks (e.g., LangGraph, AutoGen).
*   **Error Handling:** Robust error handling across chained LLM calls or tool uses requires careful workflow design.

## Conclusion

n8n, with its core features and new AI/MCP nodes, is a versatile tool in the `automation-stack`. It can automate linear sequences, orchestrate multi-service tasks, and increasingly, build and interact with AI-driven logic. By integrating with `openrouter_proxy_auto`, you can centrally manage LLM access for n8n workflows, n8nChat, and other services. The MCP nodes open new possibilities for creating n8n workflows as callable tools for AI systems and for building simpler AI agent behaviors directly within n8n.

## Integrating External Chat & Email Channels as Agent Triggers

n8n can expose your agent workflows to users via WhatsApp, email, or any supported chat/messaging channel:

- **WhatsApp Integration:** Use n8n WhatsApp Cloud API node, Twilio WhatsApp, or a webhook from a WhatsApp bot. Incoming messages trigger the CentralBrain_Agent workflow. The agent's response is sent back to the user via WhatsApp.
- **Email Integration:** Use n8n IMAP Email Trigger node to watch a dedicated inbox. On new email, extract the command and trigger the agent workflow. Send the result back via Email Send node.
- **Other Channels:** n8n supports Telegram, Slack, Discord, and more—same pattern applies.

**Best Practices:**
- Restrict access to trusted users (whitelist numbers/emails).
- Log all incoming/outgoing messages for audit.
- Handle errors gracefully and notify user if command fails.
- Document endpoints and update your agent orchestration docs as new channels are added.

This approach makes your multi-agent system accessible from anywhere, not just via web dashboards or internal APIs.
