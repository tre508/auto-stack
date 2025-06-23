## Status: ✅ Rebuilt & `freq-chat` Integrated

# 🤖 Agent Onboarding: `freq-chat` Driven Development & Trading Environment

**Welcome!** You are an AI assistant integrated into a full-stack development and algorithmic trading environment. Your primary goal is to assist with coding, automation, analysis, and operations within this ecosystem, **with `freq-chat` as your main interaction and command interface.**

This document provides the initial context for the **current architecture, centered around `freq-chat`.**

## Stacks Overview

The environment is composed of two main, interconnected Dockerized stacks:

1. **`automation-stack/`**:
    * **Purpose**: Orchestration, AI gateway, and custom tooling, all accessible and drivable via `freq-chat`.
    * **Key Services** (managed by `automation-stack/docker-compose.yml`):
        * **`freq-chat` (Vercel AI Chatbot)**:
            * **Location:** `freq-chat/` directory (local source), deployed on Vercel.
            * **Role:** The primary user interface and agent command center. All LLM tasks, workflow initiations, and status queries are channeled through `freq-chat`.
            * **Backend:** Next.js API routes within `freq-chat` handle communication with other services.
        * **Ollama (`ollama_auto`)**: (Optional, low priority, if local models are needed) Serves local LLMs. `freq-chat` can be configured to route to Ollama.
        * **n8n (`n8n_auto`)**: Workflow automation platform. `freq-chat` triggers n8n workflows via webhooks for complex/scheduled tasks.
        * **Mem0 (`mem0_auto`)**: Self-hosted centralized memory service using Qdrant and OpenRouter proxy. Runs locally from `automation-stack/mem0/server/` and exposes a REST API. `freq-chat` and other services use this for memory.
        * **Qdrant (`qdrant_auto`)**: Vector database for the self-hosted Mem0 service.
        * **PostgreSQL (`postgres_logging_auto`)**: Database for unified logging across services.
        * **FastAPI Controller (`controller_auto`)**: Python API for specific actions. `freq-chat` can call controller endpoints. The Controller interacts with the self-hosted Mem0 via its REST API.
        * **Traefik (`traefik_auto`)**: Reverse proxy.
        * **OpenRouter Proxy (`openrouter_proxy_auto`)**: Routes LLM/embedding requests to OpenRouter.ai, used by Mem0 and potentially other services.
    * **Key Configuration**: `.env`, `docker-compose.yml`, `freq-chat/.env.development.local` and Vercel environment variables.

2. **`freqtrade/`**: (Remains largely the same, but interactions are now often brokered by `automation-stack` services triggered from `freq-chat`)
    * **Purpose**: Algorithmic crypto trading bot, strategy development, backtesting, and FreqAI (machine learning for strategies).
    * **Setup**: Runs within a **VS Code Dev Container**.
    * **Key Components**:
        * Freqtrade application.
        * User data (strategies, configs, notebooks, FreqAI models) typically located in `freqtrade/user_data/` (mounted into the dev container).
        * Managed by `.devcontainer/devcontainer.json` and `docker-compose.yml` within the `freqtrade` directory.

**Documentation Sharing**:
Project documentation is primarily shared via Docker volumes. Key documentation sets:

* `automation-stack/docs/`: Documentation for the automation stack, n8n workflows, controller, etc.
* `freqtrade/user_data/docs/`: User-specific Freqtrade documentation, strategy notes, etc. (This is separate from the official Freqtrade docs).

## 🔍 Your Core Responsibilities (Interacting via `freq-chat`)

Your interactions are primarily through `freq-chat`. You will:

1. **Understand and Execute Tasks from Chat**: Interpret user commands in `freq-chat` to perform coding, analysis, automation, and documentation tasks.
2. **Drive Services via `freq-chat` Backend APIs**:
    * Formulate requests that `freq-chat`'s backend API routes will translate into calls to:
        * **FastAPI Controller (`controller_auto`)**: For workspace operations (e.g., "Ask controller to list files in `docs/`").
        * **n8n (`n8n_auto`)**: To trigger workflows (e.g., "Start the 'generate_report' n8n workflow with params X, Y.").
        * **Mem0 (`mem0_auto`)**: To store/retrieve conversational context or knowledge (e.g., "Remember this preference...", "What did we discuss about X?").
        * **Freqtrade API**: Usually indirectly via the FastAPI Controller or an n8n workflow (e.g., "Request Freqtrade status via controller.").
        * **LLM Providers (OpenRouter, OpenAI, etc.)**: `freq-chat` handles the direct LLM calls for chat completion, summarization, etc.
3. **Maintain Consistency**: Ensure changes across strategies, configs, and docs (often initiated or confirmed via chat) are coherent.
4. **Prioritize Automation via Chat Commands**: Identify how repetitive tasks can be mapped to `freq-chat` commands that trigger n8n workflows or controller actions.
5. **Log and Report in Chat**: Clearly communicate your actions and results within the `freq-chat` interface. Surface errors from backend services.
6. **Adhere to Project Standards**: Follow conventions as reflected in existing code and documentation.

## 📁 Simplified Workspace Directory Structure

```
projects/
├── automation-stack/
│   ├── controller/         # FastAPI controller application
│   ├── docs/               # Documentation for this stack
│   ├── n8n_data/           # n8n persistent data
│   ├── ollama_data/        # Ollama models (if used)
│   ├── mem0_data/          # Mem0 persistent data
│   ├── docker-compose.yml
│   └── .env
│
├── freq-chat/              # Vercel AI Chatbot (Next.js application)
│   ├── app/                # Next.js App Router (or pages/)
│   ├── public/
│   ├── .env.development.local # Local env vars for freq-chat
│   ├── next.config.js
│   ├── package.json
│   └── pnpm-lock.yaml
│
├── freqtrade/
│   ├── .devcontainer/
│   ├── user_data/
│   └── docker-compose.yml
...
```

## 🧠 Mem0 Memory & Knowledge Service (Accessed via `freq-chat` & Controller)

Mem0 is a critical component, and `freq-chat` is a primary consumer for conversational memory. Agents can also interact with Mem0 (e.g., for deeper knowledge tasks) typically via `freq-chat` API routes or dedicated controller endpoints.

### Core Features

- **Vector & Graph Storage:** Combines embedding-based similarity search with graph relationships
* **Multi-Modal Support:** Handles various data types including text, structured data, and potentially images
* **Context Management:** Maintains context across agent interactions and sessions
* **Knowledge Retrieval:** Enables semantic search and relevant information retrieval
* **Integration Points:** Interfaces with Controller, n8n workflows, and potentially Vercel AI Chat

### Architecture & Dependencies

- **Server Component:** Runs as a containerized service (`mem0_auto`) defined in `docker-compose.yml`, built from `mem0/server/Dockerfile`.
* **Dependencies:** Uses Qdrant as a vector store and an OpenRouter proxy for LLM/embedding tasks. Configuration is via `mem0/server/config.yaml` and environment variables.
* **Data Persistence:** Uses Docker volumes for Qdrant data (`qdrant_data_auto`) and Mem0's internal history DB (`mem0_data_auto`).

### Key Documentation

- **Setup Guide:** Comprehensive setup for self-hosted Mem0, Qdrant, OpenRouter proxy, and PostgreSQL logging is in `docs/guides/mem0_server_guide.md`.
* **Integration Tests:** Verification procedures in `docs/setup/03_Core_Services_Configuration_and_Verification.md` and `AutomationChecklist.md`.
* **API Reference:** The self-hosted Mem0 service exposes REST API endpoints (e.g., `/status`, `/memory`, `/search`) detailed in `mem0/server/app.py`. OpenAPI docs are available at its `/docs` endpoint (e.g., `http://mem0_auto:8000/docs`).

## ✅ Key Documents & Contextual Files

To effectively operate, familiarize yourself with:

1. **This Document (`README_agent.md`)**: Your primary onboarding guide focusing on `freq-chat`.
2. **`automation-stack/docs/Agent-Orientation.md`**: Detailed operational protocols for `freq-chat` driven interactions.
3. **`automation-stack/docs/Vercel-integration.md`**: Details on `freq-chat` deployment and Vercel environment.
4. **`freq-chat/README.md`**: Specifics of the Next.js AI Chatbot template.
5. **`automation-stack/docker-compose.yml`**: Defines backend services.
6. **`automation-stack/controller/controller.py`**: FastAPI controller capabilities.
7. **`docs/guides/mem0_server_guide.md`**: The central guide for self-hosting Mem0 (with Qdrant, OpenRouter proxy) and PostgreSQL logging.
8. **`docs/services/mem0/TROUBLESHOOTING.md`**: General troubleshooting for Mem0.
9. Key files within `automation-stack/docs/n8n/` for workflow understanding.

⚠️ **Avoid relying on outdated documents.** Prioritize those listed above and current setup guides (`docs/setup/`).

## 📌 Initial Onboarding Tasks (Revised for `freq-chat`)

1. **Confirm Understanding**: State you've processed this `freq-chat` focused onboarding.
2. **Review Key `freq-chat` & Integration Files**: Listed above.
3. **Summarize `freq-chat` to Backend Flow**: Describe how a user command in `freq-chat` would trigger an n8n workflow via a Next.js API route and then the FastAPI controller.
4. **Identify `freq-chat`'s Role in Mem0 Interaction**: Explain how `freq-chat` uses Mem0 for conversation history and how an agent might leverage this.
5. **Propose a `freq-chat` Driven Test**: Suggest a simple test initiated from `freq-chat` that verifies communication through a Next.js API route to the controller, then to n8n, and logs to Mem0.

## Example Task Flows via `freq-chat`

1. **User in `freq-chat`**: "Summarize my Freqtrade performance for yesterday."
    * **`freq-chat` Backend (API Route)**: Receives command.
    * Calls an n8n webhook (e.g., `/webhook/freqtrade/performance_report`).
    * **n8n Workflow**:
        * Receives trigger.
        * Calls FastAPI Controller endpoint (e.g., `/freqtrade/daily_stats`).
        * Controller queries Freqtrade API.
        * n8n receives data, sends to an LLM (via OpenRouter Proxy) for summarization.
        * n8n posts summary to a `freq-chat` API endpoint for display or stores in Mem0.
    * **`freq-chat` Frontend**: Displays summary.

2. **User in `freq-chat`**: "Remember that I prefer using the Deepseek model for coding tasks."
    * **`freq-chat` Backend (API Route)**: Receives preference.
    * Calls Mem0 API (`/memory`) to store this preference linked to the user/session.
    * **Mem0**: Stores the memory.
    * Later, when user asks for coding help, `freq-chat` can retrieve this preference from Mem0 to guide model selection if backend logic supports it.

## 🧠 Guiding Principles

1. **Safety First**: Prioritize non-destructive actions. Ask for confirmation before making significant changes to code, configurations, or live trading parameters.
2. **API-Driven Interaction**: Prefer interacting with services (Controller, Freqtrade, Vercel AI Chat) via their defined APIs.
3. **Modularity**: Keep suggestions and solutions modular and aligned with the microservice architecture.
4. **Idempotency**: Where possible, ensure that operations you perform or suggest can be run multiple times with the same outcome.
5. **Clarity and Conciseness**: In your responses and code, be clear, concise, and well-documented.
6. **Use Provided Tools**: Leverage the capabilities of n8n for automation and the FastAPI controller for system interaction before suggesting custom scripts for common tasks.

## 🧪 Basic Sanity Tests (Initiated from `freq-chat`)

1. **`freq-chat` to Controller API Check**:
    * **Action**: In `freq-chat`, type a command that you know maps to a `freq-chat` API route which in turn calls a status endpoint on the FastAPI controller.
    * **Expected**: `freq-chat` displays a successful status from the controller.
2. **`freq-chat` to Mem0 Search**:
    * **Action**: After storing a test memory via a chat command, type another command in `freq-chat` designed to trigger a search in Mem0 for that memory via a `freq-chat` API route.
    * **Expected**: `freq-chat` displays the retrieved memory.
    * **Verification**: Check Mem0 logs (`docker logs mem0_auto`) and potentially `freq-chat` logs to confirm the interaction.
3. **`freq-chat` to Freqtrade (via Controller/n8n)**:
    * **Action**: Type a command in `freq-chat` that triggers a `freq-chat` API route, which then calls an n8n workflow or controller endpoint to fetch a simple read-only status from Freqtrade (e.g., `/ping`).
    * **Expected**: `freq-chat` displays the Freqtrade status.
    * **Verification**: Check controller/n8n/Freqtrade logs to trace the request.

## Your Next Step

Confirm you have reviewed and understood this `freq-chat` focused onboarding. Then, proceed with the "Initial Onboarding Tasks" outlined above.

## Multi-Agent Documentation & Task Orchestration Hub

A core architectural pattern in this environment is the Multi-Agent Documentation & Task Orchestration Hub. This system uses n8n workflows and agent sub-workflows (e.g., CentralBrain_Agent, manager agents (FreqtradeManager, FreqAIManager, ResearchManager, UtilityManager), DocAgent, FreqtradeSpecialist_Agent, and specialized sub-agents) to:
* Orchestrate documentation processing and summarization across both stacks.
* Coordinate specialized agents for intelligent automation, reporting, and task delegation.
* Enable scalable, modular automation by dispatching commands to sub-agents and aggregating results.

For a detailed conceptual architecture and workflow prompt, see: `docs/n8n/prompt_library/n8nChat_prompt_templates.md` (search for 'Multi-Agent Documentation & Task Orchestration Hub') and `CentralBrain.md`.

## Mem0 Integration with Agent Workflows

Mem0 enhances the Multi-Agent Orchestration model by providing:

1. **Persistent Memory:** Agents can store and retrieve context across sessions using Mem0
2. **Knowledge Retrieval:** DocAgent workflows can store processed documentation in Mem0's vector/graph store
3. **Context-Aware Reasoning:** Agent workflows can query Mem0 for relevant context before performing tasks
4. **Structured Data Storage:** Maintains relationships between entities via graph capabilities
5. **Cross-Agent Communication:** Allows agents to share information via a centralized memory store

For complete Mem0 integration guidance, refer to `docs/guides/mem0_server_guide.md`. This document details:
* Required dependencies and installation steps using Poetry
* Configuration file structure and options
* Environment variable requirements
* Docker volume setup for data persistence
* Integration verification procedures
* Troubleshooting for common issues

Follow this guide carefully when working with Mem0 integration tasks to ensure proper functionality across the stack.

## Recent System Updates

* **`freq-chat` Integration**: `freq-chat` is now the primary UI and command interface.
* **Unified Logging:** All agents (CentralBrain_Agent, manager agents, sub-agents) now log to a unified PostgreSQL table with an `agent` field for separation. See `docs/n8n/prompt_library/UnifiedLogging.md` for schema and best practices.
* **Multi-Agent Orchestration:** The system now uses a CentralBrain_Agent, manager agents (FreqtradeManager, FreqAIManager, ResearchManager, UtilityManager), and specialized sub-agents for modular, scalable automation and documentation. See `docs/n8n/prompt_library/CentralBrain.md` for org chart and workflow prompts.
* **FastAPI Controller/n8n Integration:** A step-by-step guide for integrating n8n workflows with the FastAPI Controller is available in `docs/n8n/webhookFlows.md`.
* **Mem0 Memory Service:** The stack now utilizes a self-hosted Mem0 service (using Qdrant and OpenRouter proxy) for persistent memory and knowledge management. It runs locally as the `mem0_auto` Docker service with a REST API. Comprehensive setup guide available in `docs/guides/mem0_server_guide.md`.
* **n8n Workflow Setup:**
  * `n8n_workflow_UnifiedLogging.json` (subworkflow for logging to `agent_logs` table) has been successfully configured and tested.
  * The `agent_logs` and `mem0_memory_events` tables have been created in the PostgreSQL database.
  * **[DONE]** `n8n_workflow_Mem0_Memory_Logger.json` configured and validated against n8n CE v1.97.1.

## 🔄 Handoff Notes & Current `freq-chat` Status (as of 2025-05-26)

**Previous Mem0 Handoff:**
* Mem0 REST API endpoints implemented in `mem0/server/app.py` (`/status`, `/memory`, `/search`).
* Mem0 Docker service (`mem0_auto`) definition added to `docker-compose.yml` and basic startup verified. Status endpoint reachable.
* Addressed: A new comprehensive guide `docs/guides/mem0_server_guide.md` covers self-hosted Mem0, Qdrant, OpenRouter proxy, and PostgreSQL logging setup.
* Incomplete: Deletion of deprecated Mem0 docs.
* Pending: Full verification of Mem0 volume mapping for data persistence.
* Pending: Integration testing of Controller ↔ Mem0, n8n ↔ Mem0, `freq-chat` ↔ Mem0, and Cursor ↔ Controller ↔ Mem0 interaction loops.

**`freq-chat` Local Development Progress:**
* **Database:** Local PostgreSQL (`freqchat_db` user, `freqchat_db` database) configured on D: drive (tablespaces).
* **Dependencies:** `package.json` merged with Vercel AI Chatbot template; `pnpm install --shamefully-hoist` resolved `next` CLI issues.
* **Server Status:** `freq-chat` dev server (`pnpm run dev`) starts; basic UI from template renders at `http://localhost:3000`.
* **DB Migrations:** Schema appears aligned; tables exist.
* **Current Hurdles:**
  * Numerous TypeScript "Cannot find module" / "Cannot find name 'process'" errors in VS Code. *Next Action: Restart TS Server, then potentially install missing `@types/*`.*
  * "Wonky UI" rendering. *Next Action: Investigate Tailwind CSS v3 compatibility (downgraded from v4).*
  * NextAuth.js `headers()`/`cookies()` warnings. *Next Action: Lower priority, revisit later.*
  * Peer dependency warnings. *Next Action: Monitor for runtime issues.*

## Onboarding Tasks (Updated for `freq-chat`)

1. **Confirm Understanding**: State you've processed this `freq-chat` focused onboarding.
2. **Review Key Files**: As listed, focusing on `freq-chat` and its integration points.
3. **Verify `freq-chat` to Backend Communication Paths**: Check `freq-chat` API routes, controller endpoints, n8n webhooks.
4. **Test `freq-chat` driven LLM calls, Mem0 interaction, and a simple n8n workflow trigger.**

> **Key Priority:**
>
> * Validate `freq-chat` as the central command interface. Test its API routes and their ability to correctly orchestrate backend services (Controller, n8n, Mem0, LLMs).
> * Ensure robust conversational memory in `freq-chat` via Mem0.

---
*Updated May 2025: Fully integrated `freq-chat` as the primary LLM front-end and workflow orchestration hub.*
