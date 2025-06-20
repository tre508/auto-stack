# 🚀 Agent Tasking & Operational Workflow

**Effective Date:** 2025-05-19 (Revised for `freq-chat` Integration)

**Welcome, Agent!**

You are an AI assistant integrated into a two-stack AI-powered development and trading environment (`automation-stack` and `freqtrade`). Your primary goal is to assist with coding, automation, analysis, system verification, and operations as directed by the user, **primarily through the `freq-chat` interface.**

## `freq-chat`: Your Primary Interaction Hub

**`freq-chat` (Vercel AI Chatbot)** is the **primary user interface and command center** for all interactions with the `automation-stack`. It serves as the gateway for:
- Issuing commands to various Large Language Models (LLMs).
- Orchestrating complex workflows spanning multiple services.
- Retrieving and displaying results from automated tasks.

This application is built with Next.js, deployed on Vercel, and its source code resides in the `freq-chat/` directory.

### Key `freq-chat` Capabilities & Integrations:

1.  **Unified LLM Access:**
    *   `freq-chat` routes requests to the appropriate LLM provider based on configuration and potentially user specification.
    *   **Supported Backends for LLM Tasks:**
        *   **OpenRouter:** Via the `openrouter_proxy_auto` service for a wide selection of models. `freq-chat` can be configured to use this as its primary LLM endpoint.
        *   **Direct to Model Providers:** `freq-chat` can be configured with API keys (e.g., `OPENAI_API_KEY`, `ANTHROPIC_API_KEY` stored as Vercel environment variables) to call providers like OpenAI, Anthropic, etc., directly.
        *   **Local Models via Ollama:** If an `ollama_auto` service (if planned with this naming) is running and integrated, `freq-chat` can potentially route requests to local models.

2.  **Chat-Driven Workflow Orchestration:**
    *   Users can initiate complex automation tasks by issuing commands or queries within `freq-chat`.
    *   **Vercel-Hosted API Routes:** The `freq-chat` backend (Next.js API routes) translates these chat commands into actions. These API routes are the integration points for backend services.
    *   **n8n Integration:** `freq-chat` API routes can trigger n8n workflows via webhooks. This is the primary mechanism for automating multi-step processes, data manipulation, and scheduled tasks.
        *   *Example:* A user types "Summarize today's trades." `freq-chat` calls an API route, which triggers an n8n workflow. The workflow queries Freqtrade (via the controller), gets data, uses an LLM (via OpenRouter proxy) to summarize, and then posts the result back to `freq-chat` or stores it in Mem0 for display.
    *   **FastAPI Controller (`controller_auto`) Integration:** `freq-chat` API routes can call endpoints on the `controller_auto` to perform specific actions like workspace operations, privileged Freqtrade interactions, or other custom tasks not suited for an n8n workflow.

3.  **Mem0 for Conversational Memory & Knowledge:**
    *   `freq-chat` integrates deeply with the **Mem0 (`mem0_auto`) service** to:
        *   Persist conversation history.
        *   Store and retrieve user preferences and context.
        *   Enable Retrieval Augmented Generation (RAG) by fetching relevant information from Mem0's knowledge base to provide more informed and accurate responses.
    *   Interactions occur via `freq-chat` backend API routes calling Mem0's HTTP API.

### Chat Routing Logic & Prompt Conventions (Agent Guidance):

*   **Model Selection:** While `freq-chat` might have a default model, users (or agents operating through it) might be able to specify a preferred model or provider for certain tasks if the backend routing logic supports it (e.g., using a keyword like `@openai: summarize this` or `@deepseek: analyze this code`).
*   **Task-Specific Prompts:** When instructing `freq-chat` to perform complex tasks that involve backend orchestration:
    *   Be explicit about the desired action and the services involved (e.g., "Trigger the 'daily_report' n8n workflow and display the summary here.").
    *   Utilize clear, structured language.
    *   If `topic:` syntax or similar is implemented for tagging messages to trigger specific n8n workflows automatically, use it (e.g., `topic:generate_report Find all trades for BTC/USDT from yesterday.`).
*   **Error Handling:** `freq-chat` should surface errors from backend services (n8n, controller, Mem0, LLMs). As an agent, note these errors and potentially suggest retry mechanisms or alternative approaches.

## Mem0: Memory & Knowledge Store Service

Mem0 (service: `mem0_auto`) is a critical component of the automation-stack that provides persistent memory for AI agents and knowledge management capabilities. **It is now installed and runs locally within the `automation-stack` workspace at `mem0/server/` and is exposed via the `mem0_auto` Docker service.** It integrates with multiple services to enhance reasoning, context retention, and information retrieval.

### Purpose & Architecture
- **Centralized Memory Store:** Mem0 serves as a unified, persistent memory system for all agents and workflows.
- **Vector & Graph Storage:** Combines vector embeddings and graph relationships for sophisticated knowledge representation.
- **Multi-Modal Integration:** Connects with LLMs, embedders, and vector databases to provide comprehensive memory capabilities.
- **Context-Aware Retrieval:** Maintains agent context across sessions and enables context-aware information retrieval.

### Required Dependencies & Setup
- **Core Dependencies:** Docker, Docker Compose. The Mem0 service itself runs in a Python 3.10 container.
- **Vector Database:** Qdrant (run as a Docker service, `qdrant_auto`).
- **LLM & Embeddings:** Configured to use an OpenRouter proxy (e.g., `openrouter_proxy_auto`) via an OpenAI-compatible API.
- **Setup Process:** Follow the comprehensive guide in `docs/guides/mem0_server_guide.md` for detailed setup, Docker configurations for Mem0 and Qdrant, `config.yaml` settings for OpenRouter proxy usage, and PostgreSQL for unified logging.

### Integration Points
- **Controller (`controller_auto`):** Interacts with the self-hosted Mem0 service's REST API (e.g., `http://mem0_auto:8000`). Requires an HTTP client like `httpx`.
- **n8n (`n8n_auto`):** Interacts via Mem0's REST API using HTTP Request nodes (e.g., `http://mem0_auto:8000`).
- **Vercel AI Chat (`freq-chat`):** Backend API routes interact with Mem0's REST API (e.g., `http://mem0_auto:8000` or its publicly exposed URL) for conversational memory and RAG.
- **Cursor:** Direct integration with the self-hosted Mem0 REST API as an MCP server is not out-of-the-box. The `mem0-mcp` repository (if this refers to an old component) provides a separate server for Cursor that connects to the Mem0 Cloud Platform. To use with a self-hosted Mem0, this server would need adaptation, or a new MCP wrapper would be required.
- **Environment Configuration:** Requires specific environment variables for the Mem0 service (e.g., `OPENAI_API_KEY` which is `HF_TOKEN`, and `OPENAI_BASE_URL` for the OpenRouter proxy or embedder proxy, `MEM0_CONFIG_PATH`) and volume mapping in `.env` and `docker-compose.yml`.
- **Configuration File:** `mem0/server/config.yaml` defines vector store (Qdrant), LLM provider (OpenAI-compatible for OpenRouter), embedder, and other settings for the self-hosted server.
- **Unified Logging:** A separate PostgreSQL service (`postgres_logging_auto`) is used for unified logging, including logs from n8n workflows that interact with Mem0.

## Core Task: Executing User Requests

Your main function is to understand and execute user-provided tasks, **primarily received through or executed via the `freq-chat` interface.** These may involve:
*   Verifying system components (as per `AutomationChecklist.md`).
*   Implementing new features or modifying existing code in the `automation-stack` or `freq-chat` itself.
*   Developing or updating n8n workflows, potentially initiated or tested via `freq-chat`.
*   Orchestrating and monitoring LLM tasks and backend workflows via `freq-chat`.
*   Analyzing data or logs, with results presented in `freq-chat`.
*   Updating or creating documentation.
*   Interacting with various services (n8n, Controller, Freqtrade, Mem0) via their APIs, often triggered by a `freq-chat` API route.
*   Setting up and configuring the Mem0 memory service, and verifying its integration with `freq-chat` and other components.

## Standard Operational Workflow

Please follow this general process when undertaking tasks:

1.  **Understand Task & Objectives**: 
    *   Thoroughly analyze the user's request.
    *   Consult primary planning documents like `docs/TODO.md` or `docs/setup/MasterGameplan.md` if referenced.
    *   Identify specific goals and deliverables for the task.
2.  **Gather Context & Information**: 
    *   Review relevant current documentation, especially the guides in `docs/triage/` (like `00_MasterSetup.md`) and `README_agent.md`.
    *   Examine pertinent code (e.g., `docker-compose.yml`, `controller/controller.py`, Freqtrade strategies) or configuration files.
    *   If necessary, use tools to list directory contents or read specific files for more detail.
3.  **Propose Plan / Intended Action**: 
    *   For complex requests, briefly outline the steps you intend to take.
    *   For direct actions (e.g., running a command, a single file edit), clearly state your intended action and rationale.
4.  **Execute with Tools**: 
    *   Utilize the available tools (terminal access for `docker` commands, `curl`, etc.; file editing; web searches; MCP server functions) to perform the task.
    *   Prioritize non-destructive actions and API-based interactions where possible.
5.  **Verify & Report**: 
    *   After execution, verify that the action was successful and achieved the intended outcome (e.g., check logs, API responses, file changes).
    *   Clearly report the results, including any relevant output, logs, or error messages if issues were encountered.
6.  **Targeted Documentation Updates (Post-Task Completion)**:
    *   **Crucially, only update documentation *after* a task is successfully completed and verified.**
    *   Identify the *specific, most relevant* document(s) that need updating to reflect the change (e.g., `docs/triage/AutomationChecklist.md` for a verified item, a specific setup guide in `docs/triage/` if a configuration changes, or `README_agent.md` if core agent interaction patterns are altered).
    *   Propose concise, targeted edits to these documents using the `replace_in_file` tool. Clearly state the reason for the update, linking it back to the completed task.
    *   Avoid broad, speculative, or premature documentation changes.
7.  **Log Key Observations/Decisions (MCP Servers)**:
    *   For significant findings, decisions made during a task, or before proposing large code changes or concluding complex multi-step operations, use MCP server tools (`add_observations`, `create_entities`, etc.) to log this information for persistence and context.

## Key Files for Contextual Understanding

To operate effectively, maintain familiarity with:

1.  **This Document (`Agent-Orientation.md`)**: Your primary operational guide, emphasizing `freq-chat`.
2.  **`docs/README_agent.md`**: Core onboarding information, updated for `freq-chat`.
3.  **The `docs/triage/` directory (especially `00_MasterSetup.md` and other guides)**: Detailed guides, including `03_Core_Services_Configuration_and_Verification.md` and `04_Cross_Stack_Integration_Guide.md` which detail `freq-chat` and its integrations.
4.  **`docs/triage/TODO.md`**: Current tasks, including `freq-chat` specific items.
5.  **`docs/triage/reference/guides/MasterGameplan.md`**: Higher-level project goals.
6.  **`docs/triage/AutomationChecklist.md`**: For verifying system components, including `freq-chat` functionality.
7.  **`docker-compose.yml`**: Defines services in the `auto-stack`.
8.  **`controller/controller.py`**: FastAPI controller code.
9.  **`freq-chat/` directory:** Source code for the Next.js AI Chatbot, including its API routes (`pages/api/` or `app/api/`) which are key integration points.
10. **`docs/Vercel-integration.md`**: Details on Vercel deployment, environment variables, and API patterns relevant to `freq-chat`.
11. **`docs/guides/mem0_server_guide.md`**: The central guide for self-hosting the Mem0 service (with Qdrant and OpenRouter proxy) and setting up PostgreSQL for unified logging within the `automation-stack`.

## Tooling Issues Encountered (Important Reminder!)

The `edit_file` tool has shown limitations when attempting to apply **large-scale rewrites or full-file replacements,** particularly for `README_agent.md`. 
*   Do NOT attempt full rewrites on this specific file with the `edit_file` tool in its current state.
*   If instructed by the user to work on such a file, communicate this limitation. Incremental, highly targeted edits may be attempted with caution if necessary.

## General Guiding Principles

*   **Accuracy & Detail**: Ensure information provided and actions taken are accurate and sufficiently detailed.
*   **Clear Communication**: Report actions, results, and issues clearly and concisely.
*   **Maintain Standards**: Adhere to coding conventions, documentation styles, and architectural patterns found within the project.
*   **Prioritize Safety & Confirmation**: Prefer non-destructive actions. Ask for confirmation before making significant changes to code, configurations, or critical system parameters.
*   **Iterative Development & Verification**: Focus on incremental progress. Verify each step or component before moving to the next, especially when implementing new features or performing verifications from `AutomationChecklist.md`.

---

# 🧠 Agent Orientation: automation-stack Documentation

**Date:** 2025-05-26 (Revised for `freq-chat` local setup progress)

## ❗ Important: Project Rebuild Context

This `automation-stack` project has undergone a significant rebuild. The primary goal has been to establish a foundational Docker-based environment for Traefik, n8n, Ollama, and a FastAPI `controller.py`, designed to integrate with a `freqtrade` dev container environment.

**Current documentation efforts should focus on refining guides in `docs/triage/`, and maintaining `README_agent.md` and `docs/triage/AutomationChecklist.md` as primary live operational documents.**

## 📜 Legacy Documentation Artifacts

**BE AWARE:** Many older documents within the `/docs` directory and its subdirectories (especially those now in `docs/depreciated/` or listed with legacy status in `DocsUpdateHistory.md`) are **legacy artifacts**. They **DO NOT** accurately reflect the current, simplified, and rebuilt architecture in its entirety.

Specifically, you may find references to:

*   **Different Controller Architecture:** (e.g., Python controller on Windows host using Flask/Playwright).
*   **Alternative Freqtrade Setup:** (e.g., `compose-freqtrade.yml`, different service names).
*   **Additional Obsolete Services:** (e.g., Optuna Dashboard, Watchtower, old n8nChat components).
*   **Outdated Directory Structures or File Paths.**
*   **Obsolete Checklists and TODOs** in files like the original `MasterSetup.md`.

## ⚠️ Guidance for Agents and Contributors

1.  **Prioritize Current Code & Configuration:** The primary source of truth is the actual current codebase and main configuration files (`docker-compose.yml`, `controller/controller.py`, `.env` files, Freqtrade's devcontainer files).
2.  **Prioritize Current Documentation:** Focus on and trust information in `Agent-Orientation.md` (this file), `README_agent.md`, `docs/triage/AutomationChecklist.md`, and the guides within the `docs/triage/` directory (especially `00_MasterSetup.md`).
3.  **Review Legacy Docs With Extreme Caution:** If you must consult any document outside the ones listed above (e.g., from `docs/depreciated/` or `docs/triage/reference/docs-update-history.md`), assume its content is outdated unless verified against the current codebase and newer documentation.
4.  **Mark Outdated Sections (If Found in *Current* Docs):** If, while working on supposedly current documents, you identify specific outdated sections, please clearly propose an edit to mark or fix them.
5.  **Focus on Current Objectives:** Refer to user prompts, `docs/triage/TODO.md`, and `docs/triage/reference/guides/MasterGameplan.md` for the actual goals of current tasks.
6.  **Incremental Updates to Core Docs:** As new features are implemented or system configurations change, ensure `README_agent.md`, `docs/triage/AutomationChecklist.md`, and relevant `docs/triage/` guides are updated in a targeted manner.

**Your primary directive when referencing any documentation is to validate information against the live project state and current core documents before taking action based on potentially obsolete instructions.**

## Multi-Agent Orchestration Model

- **CentralBrain_Agent:** Orchestrates commands and workflow state, dispatching tasks to specialized agents. User interaction with CentralBrain often occurs via `freq-chat`.
- **Manager Agents:** FreqtradeManager, FreqAIManager, ResearchManager, UtilityManager—each coordinates a domain and its sub-agents.
- **DocAgent(s):** Process and summarize documentation from both stacks, storing results in a central doc database.
- **FreqtradeSpecialist_Agent:** Manages Freqtrade automations, delegating to sub-agents for strategy analysis, data operations, and FreqAI tasks.
- **Sub-Agents:** Strategist_Agent, DataAnalyst_Agent, LLM_RL_Specialist_Agent, MarketMonitor_Agent, and others for focused tasks.

These agents are orchestrated via n8n workflows and interact through webhooks, controller endpoints, and shared storage. For implementation details, see the conceptual prompt in `docs/n8n/prompt_library/n8nChat_prompt_templates.md` (search for 'Multi-Agent Documentation & Task Orchestration Hub') and `CentralBrain.md`.

## Memory and Context Management with Mem0

Mem0 provides critical memory and knowledge management functionality for the agent orchestration model, and is a key backend for `freq-chat`.

- **Agent Memory Persistence:** Enables agents to maintain context and knowledge across sessions using Mem0's vector and graph capabilities.
- **Knowledge Retrieval:** DocAgents can store processed documentation in Mem0 for later retrieval by other agents.
- **Context-Aware Reasoning:** Mem0 enriches agent workflows with relevant context and knowledge.
- **Multimedia Storage:** Can store and retrieve multi-modal information (text, images, structured data).
- **Integration with Agent Workflows:** All agents should interact with Mem0 API for context retention and knowledge acquisition.
- **Cursor Integration:** Cursor utilizes Mem0 via the Controller's MCP endpoints.

For complete setup, configuration, and integration guidance for the self-hosted Mem0 service and PostgreSQL logging, follow the steps in `docs/guides/mem0_server_guide.md`. This guide details Docker Compose setup, `config.yaml` for Mem0 (including Qdrant and OpenRouter proxy), environment variables, PostgreSQL setup for unified logs, and verification procedures.

## Updates (as of 2025-05-19)

- **Unified Logging:** All agents log to a unified PostgreSQL database.
- **Multi-Agent Orchestration:** CentralBrain, manager, and sub-agents for modular automation.
- **FastAPI Controller/n8n Integration:** As per `docs/n8n/webhookFlows.md`.
- **Mem0 Memory Service:** Core for memory/knowledge. **Now running locally as the `mem0_auto` Docker service.**
- **`freq-chat` as Primary UI:** All LLM interactions and workflow initiations are now primarily channeled through `freq-chat`. **Mem0 integration with `freq-chat` is key for conversational memory and RAG.**
- **n8n Workflow Setup Progress:**
    - `n8n_workflow_UnifiedLogging.json` (subworkflow for logging to `agent_logs` table) has been successfully configured and tested.
    - The `agent_logs` and `mem0_memory_events` tables have been created in the PostgreSQL database.
    - Next workflow to configure: `n8n_workflow_Mem0_Memory_Logger.json`.

> **Key Priority for All Agents:**
> - Complete Cross-Stack Integration Validation, focusing on `freq-chat`'s ability to drive workflows through n8n, the Controller, and interact with Mem0 and Freqtrade.
> - Ensure `freq-chat` API routes are robust and correctly call backend services.
> - Verify Mem0 integration with `freq-chat` for seamless conversational memory.
> - **Finalize Mem0 Integration:** Complete the documentation consolidation, ensure the Docker service runs reliably, and verify the Controller <-> Mem0 and n8n <-> Mem0 interaction loops.

---

_Updated May 2025: Fully integrated `freq-chat` as the primary LLM front-end and workflow orchestration hub. Replaced OpenWebUI references. Structured for autonomous agent deployment and orchestration via chat._

## 🔄 Handoff Notes (from previous agent)

- Mem0 endpoints implemented in `mem0/server/app.py` (/status, /memory, /search).
- Docker config & service partially verified—status endpoint working locally.
- Addressed: A new comprehensive guide `docs/guides/mem0_server_guide.md` has been created, covering self-hosted Mem0 and PostgreSQL logging setup.
- Incomplete: Legacy doc cleanup (must delete deprecated Mem0 docs after content is merged).
- Pending: Final verification of controller → Mem0 and n8n → Mem0 interaction loops.
- Pending: Final verification of Mem0 volume mapping for data persistence.

## 🚀 `freq-chat` Local Development Status (as of 2025-05-26)

Significant progress has been made in setting up the `freq-chat` application for local development:
- **Database Setup:** A local PostgreSQL database (`freqchat_db`) with a dedicated user (`freqchat_user`) has been successfully configured. The database is located on the D: drive using tablespaces to conserve C: drive space.
- **Dependencies Aligned:** The `freq-chat/package.json` has been merged with the Vercel AI Chatbot template's dependencies. This involved aligning versions for core packages like Next.js, React, Tailwind CSS (downgraded to v3.4.1), NextAuth.js, and Drizzle ORM.
- **`pnpm install --shamefully-hoist`:** This command was used to resolve issues with the `next` CLI not being found, likely due to pnpm's default symlinking behavior on Windows.
- **Server Running:** The `freq-chat` development server (`pnpm run dev`) now starts successfully, and the basic UI from the Vercel AI Chatbot template is rendering at `http://localhost:3000`.
- **Database Migrations:** The database schema appears to be correctly applied, with tables existing as confirmed by `test-db.mjs` and `drizzle-kit generate` reporting no schema changes.

**Current Hurdles & Next Steps for `freq-chat`:**
- **TypeScript Errors:** Numerous "Cannot find module" and "Cannot find name 'process'" errors are present in VS Code.
    - *Next Action:* Restarting the TypeScript server in VS Code. If errors persist, investigate `tsconfig.json` and potentially install missing `@types/*` packages.
- **UI Issues ("Wonky UI"):** The rendered UI is not perfect.
    - *Next Action:* Investigate Tailwind CSS v3 compatibility (due to downgrade from v4). Check `tailwind.config.ts`, global CSS, and component classes.
- **NextAuth.js Warnings:** `headers()` and `cookies()` warnings in the `/api/auth/guest` route persist.
    - *Next Action:* Lower priority; revisit after UI/TS issues are resolved.
- **Peer Dependency Warnings:** For `@vercel/otel` and `next-themes` (React versions).
    - *Next Action:* Monitor for runtime issues.
