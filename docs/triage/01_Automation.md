# 01: Automation Stack Setup

**Status:** Phase 4 Consolidation - 2025-05-23

This document provides detailed setup, configuration, and verification procedures for the automation-stack services. It covers the core orchestration platform including n8n, Controller, Mem0, and supporting services.

## Purpose

The `automation-stack/` serves as the central hub for:

* **Orchestration:** Managing and coordinating tasks between different services and the `freqtrade` stack.
* **AI Gateway:** Providing a unified interface (n8n) to various Large Language Models (LLMs).
* **Custom Tooling:** Housing a FastAPI-based controller for bespoke automation scripts and API endpoints.
* **Workflow Automation:** Utilizing n8n for creating and managing complex automated workflows.
* **Secure Service Exposure:** Using Traefik as a reverse proxy to manage access to the stack's services.
* **Memory & Knowledge Management:** Using a self-hosted Mem0 service (with Qdrant as vector store and OpenRouter proxy for LLM/embeddings) to provide persistent memory.
* **Unified Logging:** Utilizing a PostgreSQL database for centralized logging from various services.

## Architecture & Services

The automation-stack is managed by `docker-compose.yml` and includes these core services:

### 1. freq-chat (Vercel AI Chatbot)
* **Description:** The primary user-facing chat interface, built with Next.js and the Vercel AI SDK. This application is locally located in the `freq-chat/` directory and deployed on Vercel.
* **Function:** Provides a centralized UI for interacting with various LLMs, managing conversations, and potentially accessing automation features. It can be configured to connect to different model providers (e.g., OpenAI, Anthropic, or local models via Ollama) through its own backend, or could be set up to utilize the `openrouter_proxy_auto` for broader model access.
* **Interaction:** Serves as the main front-end for LLM access. Integrates with Mem0 for persistent conversational memory and context. May trigger n8n workflows or FastAPI controller endpoints for specific automated tasks initiated via chat.
* **Configuration:**
    * Vercel project settings (environment variables for API keys)
    * Local development: `.env.development.local` in `freq-chat/` directory
    * Next.js configuration files (e.g., `next.config.js`)

**Setup Steps:**

```bash
# Navigate to the projects directory in WSL
cd ~/projects/freq-chat

# Install dependencies
pnpm install

# Configure environment variables
cp .env.example .env.development.local
# Edit with your API keys (OPENAI_API_KEY, ANTHROPIC_API_KEY, etc.)

# Start development server
pnpm dev

# Deploy to Vercel
vercel deploy
```

### 2. n8n (`n8n_auto`)
* **Description:** A fair-code workflow automation platform.
* **Function:** Used to design, execute, and monitor automated workflows that can connect various services, APIs, and data sources.
* **Interaction:** Can trigger and be triggered by other services (like the FastAPI Controller or Freqtrade via API calls), perform data transformation, and orchestrate complex sequences of operations. It can also be enhanced with the **n8nChat browser extension**, which allows for AI-powered workflow generation and modification, potentially leveraging the **OpenRouter Proxy** for LLM access.
* **Configuration:**
    * Environment variables in `.env` (timezone, execution settings, `N8N_ALLOW_EXEC`)
    * Web interface configuration for workflows, credentials, etc.
* **Key Features:**
    * Multi-agent orchestration workflows
    * Integration with Controller via `/execute` and `/notify` endpoints
    * n8nChat browser extension support for AI-powered workflow generation
    * MCP (Model Control Protocol) nodes for LLM integration

### 3. Mem0 (`mem0_auto`)
* **Description:** A self-hosted, centralized memory and knowledge management service. The server code is located in `automation-stack/mem0/server/`.
* **Function:** Provides persistent memory using Qdrant as a vector store. Its LLM calls and embedding calls (which use the `openai` provider type in `config.yaml`) are now routed through the **FastAPI Controller (`controller_auto`)**. The controller then directs LLM calls to the OpenRouter Proxy and embedding calls to the Hugging Face Space API.
* **Interaction:** Integrates with the FastAPI Controller, n8n workflows, and `freq-chat` via its REST API (e.g., `http://mem0_auto:8000`).
* **Configuration:**
    * `mem0/server/config.yaml`: Sets `provider: "openai"` for both `llm` and `embedder`.
    * Environment variables for `mem0_auto` service (via `.env` and `docker-compose.yml`):
        * `OPENAI_API_KEY`: Set to your **Hugging Face Token** (e.g., `hf_YourToken...`).
        * `OPENAI_BASE_URL`: Set to the controller's proxy endpoint (e.g., `http://controller_auto:5050/mem0_openai_proxy/v1`).
* **Setup:** Detailed setup and integration instructions are available in `docs/guides/mem0_server_guide.md`.

**Data Persistence:**
```yaml
# Volume mapping in docker-compose.yml for the mem0_auto service
volumes:
  - mem0_data_auto:/data # For SQLite history DB and potentially other Mem0 data
# Qdrant data is persisted via its own volume, see Qdrant section.
```

### 4. Qdrant (`qdrant_auto`)
* **Description:** An open-source vector similarity search engine.
* **Function:** Serves as the vector database for the self-hosted Mem0 service, storing and indexing memory embeddings.
* **Interaction:** Accessed by the `mem0_auto` service on the internal Docker network.
* **Configuration:**
    * Defined in `docker-compose.yml` with a persistent volume for data. Mem0's `config.yaml` points to this service.
    * `docker-compose.yml`: Defines ports (e.g., `6333:6333`), volume (`qdrant_data_auto:/qdrant/storage`), and network (`auto-stack-net`).
* **Setup Guide:** Refer to `docs/guides/mem0_server_guide.md`.

**Data Persistence:**
```yaml
# Volume mapping in docker-compose.yml for the qdrant_auto service
volumes:
  - qdrant_data_auto:/qdrant/storage
```

### 5. PostgreSQL (`postgres_logging_auto`)
* **Description:** An open-source relational database.
* **Function:** Provides a centralized database for unified logging from various services in the `automation-stack`. Stores logs in the `agent_logs` table.
* **Interaction:** Accessed by services like n8n to write log entries.
* **Configuration:**
    * `.env` (root project): `POSTGRES_LOGGING_USER`, `POSTGRES_LOGGING_PASSWORD`, `POSTGRES_LOGGING_DB`, `POSTGRES_LOGGING_PORT`.
    * `docker-compose.yml`: Defines environment variables from `.env`, port mapping, volume (`pgdata_logging_auto:/var/lib/postgresql/data`), and network.
* **Setup Guide:** Refer to `docs/guides/mem0_server_guide.md`.

**Data Persistence:**
```yaml
# Volume mapping in docker-compose.yml for the postgres_logging_auto service
volumes:
  - pgdata_logging_auto:/var/lib/postgresql/data
```

### 6. FastAPI Controller (`controller_auto`)
* **Description:** A custom Python-based API server built with FastAPI. Now also acts as a proxy for Mem0's LLM and embedder calls.
* **Function:**
    * Provides defined endpoints for automation tasks, workspace interactions, bridging services.
    * **Mem0 Proxy Endpoints** (e.g., `/mem0_openai_proxy/v1/embeddings`, `/mem0_openai_proxy/v1/chat/completions`): Receives requests from Mem0.
        * Forwards embedding requests to the Hugging Face Space API (using HF Token received from Mem0).
        * Forwards LLM chat completion requests to the OpenRouter Proxy service (using its own `CONTROLLER_OPENROUTER_API_KEY`).
* **Interaction:** Acts as a programmable interface and a routing/authentication layer for Mem0.
* **Location:** Code for this service is typically found in `controller/`.
* **Configuration:**
    * `CONTROLLER_PORT` environment variable in `.env` (e.g., `5050`).
    * `N8N_WEBHOOK_URL` for n8n integration.
    * `EKO_SERVICE_URL`.
    * `MEM0_API_URL` (for any direct, non-proxied calls to Mem0, e.g., `http://mem0_auto:8000`).
    * **New variables for Mem0 proxying (from `.env`):**
      * `HF_SPACE_EMBEDDER_ENDPOINT`: URL of your HF Space embedder API.
      * `OPENROUTER_PROXY_SERVICE_URL`: Internal URL to your OpenRouter Proxy service.
      * `CONTROLLER_OPENROUTER_API_KEY`: Your actual OpenRouter API key (used by controller to call OpenRouter Proxy).

### 7. Traefik (`traefik_auto`)
* **Description:** A modern reverse proxy and load balancer.
* **Function:** Manages external access to the services within the `automation-stack`. It handles routing based on hostnames (e.g., `vercel-chat.localhost`, `n8n.localhost`), can manage SSL/TLS termination, and provides a dashboard for monitoring.
* **Interaction:** All external HTTP/S requests to the `automation-stack` services typically pass through Traefik.
* **Managed Routes:**
    * `n8n.localhost` → n8n service
    * `controller.localhost` → Controller API
    * `openrouter-proxy.localhost` → OpenRouter Proxy

### 8. OpenRouter Proxy (`openrouter_proxy_auto`) (Optional)
* **Description:** A Node.js proxy service that routes OpenAI API compatible requests to OpenRouter.ai.
* **Function:** Allows usage of various OpenRouter models through clients expecting an OpenAI endpoint, injecting the necessary `OPENROUTER_API_KEY`. This proxy is used by the self-hosted Mem0 service for LLM and embedding tasks.
* **Interaction:** Accessed via a Traefik-managed hostname (e.g., `openrouter-proxy.localhost`) or directly by service name on the Docker network (e.g., `http://openrouter_proxy_auto:8000/v1`).
* **Configuration:** Requires `OPENROUTER_API_KEY` in the `.env` file.

## Multi-Agent Documentation & Task Orchestration Hub

A core architectural pattern of the automation-stack is the Multi-Agent Documentation & Task Orchestration Hub. This system leverages n8n workflows and agent sub-workflows to:

* Orchestrate documentation processing and summarization across the stack and Freqtrade environments.
* Coordinate specialized agents (e.g., CentralBrain_Agent, DocAgent, FreqtradeSpecialist_Agent) for intelligent automation, reporting, and task delegation.
* Enable scalable, modular automation by dispatching commands to sub-agents and aggregating results.

The Mem0 service plays a critical role in this architecture by providing:
* Persistent memory for agents to maintain context across sessions
* Vector and graph-based storage for efficient knowledge retrieval
* Structured data representation for complex relationships
* Cross-agent knowledge sharing through a centralized repository
* Context-aware information retrieval to enhance agent reasoning

For a detailed conceptual architecture and workflow prompt, see: `docs/n8n/prompt_library/n8nChat_prompt_templates.md` (search for 'Multi-Agent Documentation & Task Orchestration Hub').

## Service Startup and Verification

### 1. Start All Services

From a WSL terminal inside `~/projects/auto-stack`:
```bash
# Pull latest images
docker compose -f docker-compose.yml pull

# Start all services
docker compose -f docker-compose.yml up -d

# Verify services are running
docker compose -f docker-compose.yml ps
```

### 2. Service Verification

| Service | Verification Command | Expected Result |
|---------|---------------------|-----------------|
| **Traefik** | `curl http://localhost:8080/dashboard/` | Dashboard interface |
| **n8n** | `curl http://n8n.localhost` | n8n login page |
| **Controller** | `curl http://controller.localhost/docs` | OpenAPI documentation |
| **Mem0** | `curl http://${MEM0_HOST:-mem0.localhost}:${MEM0_HOST_PORT:-7860}/status` | `{"status": "Mem0 service is running and client is healthy"}` |
| **Qdrant** | `curl http://localhost:6333` (or check UI/logs) | Qdrant accessible |
| **PostgreSQL Logging** | (Connect via psql or DB client on `${POSTGRES_LOGGING_PORT}`) | Database accessible |
| **OpenRouter Proxy** | `curl http://openrouter-proxy.localhost/healthz` | `OK` |
| **freq-chat** | `curl http://localhost:3000` | Next.js application |

## Integration Testing

### Controller ↔ n8n Integration

```bash
# Test Controller to n8n webhook forwarding
curl -X POST http://controller.localhost/execute \
  -H "Content-Type: application/json" \
  -d '{"message": "test integration", "workflow": "test"}'
```

### Mem0 Memory Operations

```bash
# Add memory (replace MEM0_HOST_PORT if not 7860, or use Traefik host e.g., http://mem0.localhost/memory)
curl -X POST http://localhost:${MEM0_HOST_PORT:-7860}/memory \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Test automation setup"}], "user_id": "system_setup_test", "metadata": {"source": "01_Automation.md"}}'

# Search memories (replace MEM0_HOST_PORT if not 7860, or use Traefik host e.g., http://mem0.localhost/search)
curl -X POST http://localhost:${MEM0_HOST_PORT:-7860}/search \
  -H "Content-Type: application/json" \
  -d '{"query": "Test automation setup", "user_id": "system_setup_test"}'
```

### Multi-Agent Workflow Testing

1. Create CentralBrain_Agent workflow in n8n
2. Configure manager agents (FreqtradeManager, FreqAIManager, etc.)
3. Test agent orchestration via HTTP webhooks
4. Verify unified logging to PostgreSQL

## Automation Verification Checklist

<details>
<summary>Click to expand Automation Stack Verification Checklist</summary>

### Core Service Verification

**Traefik Reverse Proxy:**
* [ ] Traefik dashboard accessible (`http://localhost:8080/dashboard/`)
* [ ] Services routed correctly via host rules (`http://n8n.localhost`, `http://controller.localhost`)

**freq-chat (Vercel AI Chatbot):**
* [ ] Web interface accessible (`http://localhost:3000`)
* [ ] User registration and login functional
* [ ] Environment variables loaded correctly
* [ ] Core chat functionality works
* [ ] Mem0 integration functional (if configured)
* [ ] Deployment status verified on Vercel

**n8n (`n8n_auto`):**
* [ ] Web interface accessible (`http://n8n.localhost` or `http://localhost:5678`)
* [ ] Basic workflow creation and execution functional
* [ ] HTTP Request node can reach other services on `auto-stack-net`
* [ ] Access to shared volumes verified (if configured)
* [ ] n8nChat extension connected and functional
* [ ] MCP nodes operational

**Mem0 (`mem0_auto`):**
* [ ] Container running: `docker ps | grep mem0_auto`
* [ ] Server logs clean: `docker logs mem0_auto` (check for successful Qdrant connection and OpenRouter proxy readiness if used)
* [ ] Health check passes: `curl http://${MEM0_HOST:-mem0.localhost}:${MEM0_HOST_PORT:-7860}/status` (should return healthy status)
* [ ] Memory operations work (add/search/retrieve via REST API)
* [ ] Data persistence for Mem0 history (e.g., `/data/mem0_history.db`) across restarts verified.
* [ ] Controller integration functional (calls to Mem0 REST API).
* [ ] n8n integration via HTTP Request node works (calls to Mem0 REST API).

**Qdrant (`qdrant_auto`):**
* [ ] Container running: `docker ps | grep qdrant_auto`
* [ ] Server logs clean: `docker logs qdrant_auto`
* [ ] Qdrant UI/API accessible: `http://localhost:6333`
* [ ] Data persistence for Qdrant vectors across restarts verified.

**PostgreSQL Logging (`postgres_logging_auto`):**
* [ ] Container running: `docker ps | grep postgres_logging_auto`
* [ ] Server logs clean: `docker logs postgres_logging_auto`
* [ ] Can connect with `psql` or DB client.
* [ ] `agent_logs` table created.
* [ ] Test log insertion from n8n works.
* [ ] Data persistence for logs across restarts verified.

**FastAPI Controller (`controller_auto`):**
* [ ] Service logs indicate successful startup
* [ ] API accessible via Traefik (`http://controller.localhost/docs`)
* [ ] Direct network access works (`http://controller_auto:5050/status`)
* [ ] OpenAPI docs accessible and shows defined routes
* [ ] Key endpoints respond: `/status`, `/execute`, `/notify`

**OpenRouter Proxy (`openrouter_proxy_auto`):**
* [ ] Service logs show successful startup
* [ ] Health check passes: `curl http://openrouter-proxy.localhost/healthz`
* [ ] API accessible via Traefik
* [ ] Basic proxy functionality verified
* [ ] Client connections work (n8n, n8nChat)

### Cross-Stack Integration

**n8n → Controller API:**
* [ ] n8n workflow can call FastAPI Controller endpoints

**Controller → Freqtrade API:**
* [ ] Controller can call Freqtrade API endpoints
* [ ] Authentication (JWT) handled correctly

**n8n → OpenRouter Proxy:**
* [ ] n8n HTTP Request node can call proxy endpoints
* [ ] Valid responses received from OpenRouter models

**n8n → Mem0:**
* [ ] n8n can send prompts to Mem0 API
* [ ] Memory operations accessible from workflows

**Multi-Agent Orchestration:**
* [ ] CentralBrain_Agent workflow present and configured
* [ ] Manager agents (FreqtradeManager, FreqAIManager, etc.) operational
* [ ] Sub-agents can be triggered via HTTP webhooks
* [ ] Results aggregation functional

### Example Automation Tasks

**System Health Monitoring:**
* [ ] Scheduled n8n workflow for health checks
* [ ] Service status endpoints monitored
* [ ] Notifications on service failures

**Multi-Agent Documentation Processing:**
* [ ] CentralBrain_Agent can dispatch to DocAgent(s)
* [ ] Results aggregated and stored in central database
* [ ] Document summaries accessible via Mem0

**Unified Logging:**
* [ ] All agents log to unified PostgreSQL table
* [ ] Agent field separation working
* [ ] Log entries queryable and structured

### n8n AI Capabilities

**n8nChat Extension:**
* [ ] Extension installed and connected to n8n
* [ ] Configured to use OpenRouter proxy
* [ ] Can generate basic workflows
* [ ] Can modify existing workflows

**MCP Nodes:**
* [ ] MCP Client node can call OpenRouter proxy
* [ ] Workflow receives and processes LLM responses
* [ ] MCP Server Trigger exposes tools via webhooks

### Agent-Specific Capabilities

**Code Generation/Modification:**
* [ ] Agent can request file reads via Controller
* [ ] Agent can propose and apply file changes
* [ ] Safeguards against malicious code functional

**Information Retrieval:**
* [ ] Agent can search documentation via Controller
* [ ] Workspace file access functional

**n8n Workflow Management:**
* [ ] Agent can list available workflows via n8n API
* [ ] Agent can trigger workflows via webhooks
* [ ] Agent can deploy new workflows via n8n API

</details>

## Troubleshooting

### Common Issues

**Service Connectivity Problems:**

From a WSL terminal:
```bash
# Check service status
docker compose -f docker-compose.yml ps

# View service logs
docker logs n8n_auto
docker logs controller_auto
docker logs mem0_auto

# Test internal network connectivity
docker exec n8n_auto ping controller_auto
```

**Traefik Routing Issues:**
* Verify service labels in `docker-compose.yml`
* Check Traefik dashboard for backend health
* Ensure hostnames resolve correctly

**Mem0 Configuration Issues:**
* Ensure `mem0/server/config.yaml` is correctly configured for Qdrant (host: `qdrant_auto`) and LLM/Embedder (provider: `openai`).
* Verify environment variables `OPENAI_API_KEY` (using `OPENROUTER_API_KEY`) and `OPENAI_BASE_URL` (pointing to `openrouter_proxy_auto`) are correctly passed to the `mem0_auto` container in `docker-compose.yml`.
* Check volume mounts for `config.yaml` and `/data` are correct in `docker-compose.yml`.
* Test API endpoints (e.g., `http://${MEM0_HOST:-mem0.localhost}:${MEM0_HOST_PORT:-7860}/status`).

**Controller Integration Problems:**
* Verify `MEM0_API_URL` in `controller_auto` environment (in `docker-compose.yml`) points to `http://mem0_auto:8000`.
* Ensure controller uses an HTTP client (e.g. `httpx`) to interact with Mem0's REST API.
* Test controller endpoints that use Mem0.

### Service-Specific Debugging

**n8n Workflow Issues:**
* Check workflow logs in n8n interface
* Verify node configurations and credentials
* Test HTTP Request nodes with manual execution

**Multi-Agent Orchestration:**
* Verify webhook URLs are accessible
* Check PostgreSQL unified logging table
* Test agent communication patterns

## Recent System Enhancements

* **Unified Logging:** All agents log to PostgreSQL with agent field separation
* **Multi-Agent Orchestration:** CentralBrain_Agent with manager and sub-agent hierarchy
* **FastAPI Controller/n8n Integration:** Tight integration using `/execute` and `/notify` endpoints
* **Mem0 Memory Service:** Self-hosted deployment using Qdrant and OpenRouter proxy, with comprehensive memory management. See `docs/guides/mem0_server_guide.md`.
* **PostgreSQL for Unified Logging:** Centralized logging database setup. See `docs/guides/mem0_server_guide.md`.
* **n8nChat Integration:** AI-powered workflow generation and modification
* **MCP Node Support:** Model Control Protocol for enhanced LLM integration

## Next Steps

After completing automation stack setup:

1. **Mem0 & PostgreSQL Full Setup**: Ensure Mem0, Qdrant, and PostgreSQL logging are fully configured by following `docs/guides/mem0_server_guide.md`.
2. **Trading Integration:** Follow `02_Trading.md` for Freqtrade configuration.
3. **Advanced Verification:** Use `03_Core_Services_Configuration_and_Verification.md`.
4. **Cross-Stack Integration:** Refer to integration guides for connecting services.
5. **Multi-Agent Configuration:** Implement CentralBrain and manager agent workflows.

---

**References:**
* [00_MasterSetup.md](./00_MasterSetup.md) - Prerequisites and initial setup
* [docs/guides/mem0_server_guide.md](../guides/mem0_server_guide.md) - Detailed Mem0 and PostgreSQL setup
* [02_Trading.md](./02_Trading.md) - Freqtrade environment setup
* [03_Core_Services_Configuration_and_Verification.md](./03_Core_Services_Configuration_and_Verification.md) - Detailed verification
* [../services/n8n/Tasklist.md](../services/n8n/Tasklist.md) - n8n service details
* [../services/mem0/Tasklist.md](../services/mem0/Tasklist.md) - Mem0 service details (Note: may need update to reflect self-hosted focus)
* [../services/controller/Tasklist.md](../services/controller/Tasklist.md) - Controller service details
