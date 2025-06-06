# 05: Agent Capabilities and Interaction

**Status:** ✅ Consolidated $(date +%Y-%m-%d)

This document outlines the core responsibilities, capabilities, and interaction patterns for AI-driven assistance within the integrated `automation-stack` and `freqtrade` environment. This assistance can be provided by a conceptual external AI agent, the **n8nChat browser extension**, **n8n workflows built with AI/MCP nodes**, or through interactions with the **`freq-chat` Vercel AI Chatbot**.

## Core Agent/Assistant Responsibilities

Regardless of the specific implementation (external agent, n8nChat, n8n workflow, or `freq-chat`), the AI-driven assistance aims to support development, automation, analysis, and operations. Key responsibilities include:

1. **Task Understanding and Execution:** Accurately interpret user requests (natural language for n8nChat and `freq-chat`, structured inputs for workflows) and execute tasks related to coding, data analysis, workflow automation, documentation updates, and system interaction.
2. **API-Driven Interaction:** Prioritize using defined APIs:
    * **FastAPI Controller (`controller_auto`):** For workspace operations, triggering Freqtrade actions, or initiating other n8n workflows.
    * **OpenRouter Proxy (`openrouter_proxy_auto`):** Preferred for most LLM tasks (generation, summarization, reasoning), providing access to a wide range of models. Both n8nChat and n8n workflows (via HTTP Request or MCP Client nodes) should be configured to use this. See `../proxy.md`.
    * **n8n API (via Controller or directly for meta-workflows):** To query, trigger, or manage n8n workflows.
    * **Freqtrade API (usually via Controller or n8n workflow):** For trading-related operations.
    * **Mem0 API:** For memory/context retrieval, knowledge storage, and persistent state management. Mem0's LLM and embedder calls are proxied by the `controller_auto` service. Direct interaction with Mem0's REST API (e.g., `http://mem0_auto:8000`) is still used for adding/searching memories.
3. **Consistency and Coherence:** Ensure changes are consistent with project standards.
4. **Automation Focus:** Proactively identify and implement automations using n8n workflows, potentially designed with n8nChat or exposing capabilities via MCP Server Triggers.
5. **Clear Communication:** Log actions, report results, and state issues clearly.
6. **Adherence to Project Standards:** Follow established conventions and guidelines.
7. **Safe Operations:** Prioritize non-destructive actions; seek confirmation for critical changes.

## AI-Driven Interaction Patterns & Capabilities

This section details how AI assistance interacts with the system through concrete scenarios.

### 1. Scenario: User Initiates Task via `freq-chat`

1.  **User Input:** User types a command like, "Summarize my Freqtrade performance for the last 7 days."
2.  **`freq-chat` Backend Processing:**
    *   The Next.js backend receives the request.
    *   It may first query **Mem0** to retrieve context (e.g., `POST http://mem0.localhost/search`).
    *   It then determines the action:
        *   **Direct LLM Call:** For simple queries, it calls an LLM via the **OpenRouter Proxy**.
        *   **Controller Call:** For complex tasks, it calls the **Controller**, e.g., `POST http://controller.localhost/freqtrade/performance`.
        *   **n8n Webhook Call:** To trigger a pre-defined workflow, e.g., `POST http://n8n.localhost/webhook/summarize-performance`.
3.  **Controller/n8n Processing:** The service interacts with the Freqtrade API, databases, etc.
4.  **Response & Memory:** The result is returned to `freq-chat` for display, and the interaction can be stored in Mem0 (`POST /memory`).

### 2. Scenario: Automated Reporting via n8n

1.  **Trigger:** An n8n workflow starts on a schedule (e.g., daily at 8 AM).
2.  **Fetch Data:** An "HTTP Request" node calls the **Controller** to get the daily P&L.
3.  **Store in Memory:** Another "HTTP Request" node calls **Mem0** (`POST /memory`) to store the result, including metadata. Mem0 automatically handles embedding and storing the data in **Qdrant**.
4.  **Send Notification:** The workflow sends the report to a service like Telegram.

### 3. Scenario: Agent Modifying a File

1.  **Agent Request:** An agent decides to modify a documentation file.
2.  **Controller Interaction:**
    *   The agent calls the **Controller** endpoint `.../workspace/file/read` to get the file's content.
    *   After processing, the agent calls `.../workspace/file/write` with the new content or a diff.
3.  **Controller Action & Logging:** The Controller writes the changes to the file system and logs the action to the PostgreSQL database.

### 4. Scenario: n8n Workflow Exposed as a Callable Tool

1.  **Workflow Design (n8n):**
    *   Create a workflow (e.g., "Get Active Trades") starting with an "MCP Server Trigger" node. This defines an input schema and exposes a unique webhook URL.
    *   The workflow fetches data from the Freqtrade API (via the Controller).
    *   The result is sent back to the trigger node.
2.  **Agent/Tool Invocation:**
    *   Another AI agent, `freq-chat`, or another n8n workflow calls the webhook URL provided by the MCP Server Trigger.
3.  **Execution & Response:** The n8n workflow runs and returns the requested data as a JSON response.

### 5. Mem0 and Qdrant Integration Details

- **Mem0's Role:** Provides an API for structured memory, using an LLM (via the Controller proxy) for embedding and Qdrant as the vector store.
- **Qdrant's Role:** Stores the vector embeddings and associated metadata provided by Mem0.
- **Interaction Flow (Adding Memory):**
    1. A client (Controller, n8n, `freq-chat`) sends `POST /memory` to `mem0_auto`.
    2. `mem0_auto` calls the Controller's embedding proxy.
    3. The Controller forwards the request to the Hugging Face Space embedder.
    4. The embedding is returned to Mem0.
    5. Mem0 upserts the vector and metadata into Qdrant.
- **Interaction Flow (Searching Memory):**
    1. A client sends `POST /search` to `mem0_auto` with a query.
    2. `mem0_auto` generates an embedding for the query (using the same proxy mechanism).
    3. `mem0_auto` searches Qdrant for similar vectors.
    4. Qdrant returns matching results, which Mem0 forwards to the client.

## Guiding Principles for AI-Driven Operation

1.  **API-First:** Interactions should primarily occur via well-defined APIs.
2.  **Modularity:** Leverage the microservice architecture. n8n workflows act as modular automation units.
3.  **Centralized Orchestration:** Use the Controller as a central point for complex or privileged operations.
4.  **Memory Utilization:** Use Mem0 for context, history, and knowledge sharing.
5.  **Security:** Authenticate API calls where necessary.
6.  **Logging:** Ensure actions are logged to the central PostgreSQL database.
7.  **Idempotency**: Design actions/workflows to be safely repeatable.
8.  **Safety First**: Always prioritize non-destructive actions. Confirm before changes.

By understanding these interaction patterns, the `automation-stack` can effectively leverage n8nChat, `freq-chat`, and AI-enhanced n8n workflows to achieve sophisticated automation and provide powerful assistance.

## Multi-Agent Orchestration Patterns

The automation-stack employs a multi-agent orchestration model for advanced documentation management and Freqtrade automation. Key agent roles include:

* **CentralBrain_Agent:** The primary orchestrator, receiving commands (via webhook), dispatching tasks to specialized agents (e.g., DocAgent, FreqtradeSpecialist_Agent), and managing workflow state.
* **DocAgent(s):** Specialized agents for processing and summarizing documentation from the automation-stack and Freqtrade environments, storing results in a central doc database.
* **FreqtradeSpecialist_Agent:** Manages Freqtrade-related automations, delegating to sub-agents for strategy analysis, data operations, and FreqAI tasks.
* **Sub-Agents:** Strategist_Agent, DataAnalyst_Agent, LLM_RL_Specialist_Agent, and MarketMonitor_Agent, each handling focused tasks within the Freqtrade domain.

Agents interact via n8n workflows, FastAPI controller endpoints, and shared storage. The CentralBrain_Agent typically triggers sub-agent workflows using HTTP requests and aggregates their results.

### Mem0-Enhanced Multi-Agent Orchestration

The integration of Mem0 significantly enhances this multi-agent orchestration model by providing:

1. **Persistent Agent Memory:** Agents can store their state, context, and knowledge, enabling:
   * Continuity across sessions and workflow runs
   * Incremental knowledge building
   * Long-term memory for complex operations

2. **Inter-Agent Knowledge Sharing:** Agents can access and build upon information from other agents:
   * DocAgent stores processed documentation that other agents can query
   * Specialist agents can store domain-specific knowledge
   * CentralBrain_Agent can access all agents' context and knowledge

3. **Context-Aware Decision Making:** Agents can retrieve relevant context before taking actions:
   * Access to historical operations and their outcomes
   * Retrieval of user preferences and past interactions
   * Consideration of related knowledge and insights

4. **Structured Knowledge Representation:** Using Mem0's graph capabilities:
   * Model complex relationships between entities
   * Traverse connections to discover related information
   * Build rich knowledge structures across domains

For a detailed conceptual workflow and agent hierarchy, see: `docs/n8n/prompt_library/n8nChat_prompt_templates.md` (search for 'Multi-Agent Documentation & Task Orchestration Hub').

## Unified Logging & Expanded Orchestration

* **Unified Logging:** All agent actions should be logged to a unified PostgreSQL table with an `agent` field for separation. See `docs/n8n/prompt_library/UnifiedLogging.md` for schema and best practices.
* **Expanded Multi-Agent Orchestration:** The system now uses a CentralBrain_Agent, multiple manager agents, and specialized sub-agents for modular, scalable automation. See `docs/n8n/prompt_library/CentralBrain.md` for org chart and workflow prompts.
* **Mem0 for Memory Management:** All agents should leverage the self-hosted Mem0 service for context retention and knowledge sharing via its REST API. Mem0 is running locally as the `mem0_auto` Docker service, using Qdrant. Its LLM/embedder calls are proxied by the controller. Follow the setup and integration guide in `docs/guides/mem0_server_guide.md` and relevant controller/proxy configurations.
