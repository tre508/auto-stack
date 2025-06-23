# 00: Master Setup Guide

**Status:** Phase 4 Consolidation - 2025-05-23

This document provides a comprehensive setup guide for the automation-stack project, covering prerequisites, initial configuration, and basic verification steps. It serves as the primary entry point for new developers or fresh environment setup.

## Overview

This document provides a comprehensive setup guide for the auto-stack project, covering prerequisites, initial configuration, and basic verification steps. It serves as the primary entry point for new developers or fresh environment setup.

### Project Vision and Objectives
- **Name:** auto-stack
- **Vision:** To create a unified, modular, and robust platform for AI-driven automation and algorithmic trading.
- **Core Objectives:**
  - **Modularity:** Design services that are independent and easy to manage.
  - **Data Persistence:** Ensure critical data is stored reliably, with a default strategy of using the `D:` drive on Windows hosts for Docker volumes.
  - **Clear Documentation:** Maintain a canonical set of documents that are clear, concise, and up-to-date.

### Core Services at a Glance

| Service | Role | Key Technology |
|---|---|---|
| **Traefik** | Reverse Proxy & API Gateway | Go |
| **n8n** | Workflow Automation Engine | Node.js, TypeScript |
| **Controller** | AI Orchestrator & Logic Router | Python, FastAPI |
| **Mem0** | Long-Term Memory Service | Python, FastAPI |
| **Qdrant** | Vector Database for Embeddings | Rust |
| **PostgreSQL** | Structured Logging Database | SQL |
| **OpenRouter Proxy**| LLM Gateway & Fallback Manager | - |
| **freq-chat** | Primary User Interface | Next.js, React |
| **Freqtrade** | (Future) Trading Bot & Backtester | Python |

The `automation-stack` project consists of two main components:

1. **`automation-stack/`** - Core orchestration services (n8n, Controller, self-hosted Mem0 with Qdrant, PostgreSQL for logging, Traefik, OpenRouter Proxy, etc.)
2. **`freqtrade/`** - Algorithmic trading environment (dev container-based)

These components work together to provide a unified development and automation environment for AI-assisted coding, workflow orchestration, and algorithmic trading.

## System Architecture and Components

This project is designed to be run primarily using Docker within a WSL (Windows Subsystem for Linux) environment on Windows, or a native Linux environment.

### 1. Orchestration Layer

#### 1.1 n8n

- Role: Workflow engine
- ENV: `N8N_BASIC_AUTH_*`, `N8N_HOST`, `N8N_PORT`, `DB_TYPE`, `DB_SQLITE_DATABASE`
- Volume: `D:\docker-volumes\n8n_data:/home/node/.n8n`
- Ports: `5678:5678`
- Traefik labels: Host(`n8n.localhost`)

#### 1.2 Controller (FastAPI)

- Role: AI routing
- ENV: `CONTROLLER_*`, `MEM0_API_URL`, `QDRANT_URL`, `POSTGRES_LOGGING_URL`, `N8N_WEBHOOK_URL`, `FREQTRADE_API_URL`
- Volume: `./controller:/app:ro`
- Ports: `3000:3000`
- Traefik labels: Host(`controller.localhost`)

### 2. Memory & Knowledge Layer

#### 2.1 Mem0 (FastAPI)

- Role: Memory API
- ENV: `MEM0_*`, `OPENAI_API_KEY`, `QDRANT_HOST`, `QDRANT_PORT`
- Volume: `D:\docker-volumes\mem0_data:/data`
- Ports: `8000:8000`
- Traefik labels: Host(`mem0.localhost`)

#### 2.2 Qdrant

- Role: Vector DB
- Volume: `D:\docker-volumes\qdrant_data:/qdrant/storage`
- Ports: `6335:6333`, `6336:6334`

#### 2.3 OpenRouter Proxy

- Role: LLM proxy
- ENV: `OPENROUTER_API_KEY`, `OPENROUTER_PROXY_PORT`
- Ports: `8001:3000`
- Traefik labels: Host(`openrouter.localhost`)

### 3. Logging Layer

#### 3.1 PostgreSQL

- Role: Logs/audit
- ENV: `POSTGRES_LOGGING_*`
- Volume: `D:\docker-volumes\pg_logs_data:/var/lib/postgresql/data`
- Ports: `5433:5432`
- Traefik labels: none (internal)

### 4. User-Facing Services

#### 4.1 freq-chat (Next.js)

- Role: Chat UI
- ENV: `NEXT_PUBLIC_*`
- Volume: `./freq-chat:/app`
- Ports: `3001:3000`
- Traefik labels: Host(`chat.localhost`)

#### 4.2 Freqtrade (Future)

- Role: Trading bot/backtester
- ENV: `FREQTRADE_*`
- Volume: `./freqtrade/user_data`
- Ports: `8080:8080`
- Traefik labels: Host(`freqtrade.localhost`)

### 5. Reverse Proxy & Networking

#### 5.1 Traefik

- Role: HTTP router
- Config: `traefik/traefik.yml`
- Ports: `80:80`, `443:443`, `8080:8080`
- Docker socket: `/var/run/docker.sock`

#### 5.2 Network

All services are connected via the `auto-stack-net` bridge network, which is defined in the primary `docker-compose.yml` file.

## Prerequisites

| Requirement | Version/Notes | Installation |
|-------------|---------------|--------------|
| **Operating System** | WSL 2 | Required for Docker Desktop integration and consistent tooling. |
| **Docker Desktop** | >= 25.0 | Install with WSL 2 integration enabled, **reboot after installation**. |
| **Git** | Latest | Required for cloning repositories. Must be accessible from WSL. |
| **VS Code or Cursor** | Latest | Must be connected to the WSL instance via the "Remote - WSL" extension. |
| **Hardware** | 16+ GB RAM recommended | GPU recommended for local LLM performance. |

### Additional Requirements

- **Node.js** >= 18 LTS (for freq-chat development, must be installed in WSL, `nvm` recommended).
- **Python** >= 3.8 (for local development, optional, must be in WSL).
- **API Keys** (Optional):
  - OpenRouter API Key (for remote LLM access)
  - OpenAI/Anthropic keys (for freq-chat)

## Initial Setup

### 1. Project Structure Setup (Inside WSL)

All project setup must be performed from within your WSL terminal.

```bash
# Create a parent directory for projects in your WSL home folder
mkdir -p ~/projects
cd ~/projects

# Clone the automation-stack repository
git clone <your-automation-stack-repo-url> automation-stack

# Clone the freqtrade repository (separate project)
cd ..
git clone <your-freqtrade-repo-url> freqtrade
```

### 2. The "Focused Workflow" (Mandatory)

**This is the most critical step for a stable development environment.** Due to how VS Code extensions and Node.js toolchains resolve paths, you **must not** open the root `auto-stack` folder in your editor.

The correct procedure is:

1.  Launch a **WSL terminal** (e.g., Ubuntu, Debian).
2.  Navigate (`cd`) into the specific sub-project you intend to work on.
    *   For the automation stack: `cd ~/projects/auto-stack`
    *   For Freqtrade development: `cd ~/projects/freqtrade`
3.  From *within that subdirectory*, run `code .` to launch VS Code.

This action scopes the workspace correctly, ensuring all tools function as expected.

### 3. Environment Configuration

From within the `~/projects/auto-stack` directory in your WSL terminal, copy the example environment file and edit it.

```bash
# Change directory into the main project
cd ~/projects/auto-stack

# Copy the example environment file
cp .env.example .env

# Edit the .env file with your specific values.
# See the detailed reference guide below for an explanation of each variable.
nano .env
```

### 3.1 Understanding the `.env` File Hierarchy (New Strategy)

The `auto-stack` project employs a hierarchical approach to managing environment variables to ensure clarity, reduce redundancy, and simplify configuration.

*   **Root `.env` File (`auto-stack/.env`):**
    *   **Purpose:** This is the central configuration file for all **shared variables** and global secrets.
    *   **Contents:** Any variable required by two or more services (e.g., `OPENROUTER_API_KEY`, `HF_TOKEN`, `POSTGRES_LOGGING_USER/PASSWORD/DB`, `N8N_API_KEY`), as well as common settings like Traefik hostnames and external port mappings, belong exclusively in this file.
    *   **Principle:** If a variable is in the root `.env`, it **must not** be duplicated in service-specific `.env` files.

*   **Service-Specific `.env` Files (e.g., `controller/.env`, `mem0/.env`, `n8n.env`):**
    *   **Purpose:** These files contain variables that are **only** required by that specific service.
    *   **Location:** They are typically located within the service's subdirectory (e.g., `controller/.env`, `mem0/.env`) or at the root for services without a dedicated subdirectory for their Docker context (e.g., `n8n.env`).
    *   **Contents:** Examples include internal port numbers the service application listens on (e.g., `CONTROLLER_PORT=5050` in `controller/.env`), specific paths, or flags relevant only to that service.
    *   **Example for `eko_service_auto`:** It uses `controller/eko.env` for its specific settings like `EKO_LLM_PROVIDER`.

*   **Loading Order in `docker-compose.yml`:**
    *   For services that use both a root and a service-specific `.env` file, the `docker-compose.yml` is configured to load them in order:
        1.  `./.env` (root shared variables)
        2.  `./path/to/service/.env` (service-specific variables)
    *   This allows service-specific files to potentially override a shared variable if absolutely necessary, though the goal of this strategy is to eliminate such overrides through clear separation.

*   **Special Note on `freq-chat/.env.development.local`:**
    *   The file `freq-chat/.env.development.local` is managed **separately** as part of the `freq-chat` Next.js application's own development workflow.
    *   While it's loaded by `docker-compose.yml` for the `freq_chat_auto` service during local Docker-based development, its primary purpose is for `pnpm dev` and Vercel deployments.
    *   It contains variables specific to `freq-chat`'s frontend and backend needs, including `localhost` URLs for other services (for direct calls during development) and `NEXT_PUBLIC_` variables.
    *   Ensure any shared API keys (like an OpenRouter key if `freq-chat` calls it directly or via its local proxy) in this file are consistent with the values in the root `auto-stack/.env`.

This hierarchical approach ensures that shared configurations are managed in one place, reducing the risk of conflicts and making the system easier to understand and maintain.

<details>
<summary>Click to expand Detailed Environment Variable Reference</summary>

This section provides a comprehensive reference for all environment variables used across the `auto-stack` services.

#### 1. n8n (`n8n_auto`)
- **`N8N_BASIC_AUTH_ACTIVE`**: Enables (`true`) or disables (`false`) basic authentication for the n8n UI.
  - *Sample Value:* `true`
- **`N8N_BASIC_AUTH_USER`**: Username for n8n basic auth.
  - *Sample Value:* `n8nuser`
- **`N8N_BASIC_AUTH_PASSWORD`**: Password for n8n basic auth.
  - *Sample Value:* `a_strong_password`
- **`N8N_HOST`**: Hostname n8n listens on. For Traefik routing, this is typically `n8n.localhost`.
  - *Sample Value:* `n8n.localhost`
- **`N8N_PORT`**: Internal port n8n listens on.
  - *Sample Value:* `5678`
- **`DB_TYPE`**: Database type for n8n.
  - *Sample Value:* `sqlite`
- **`DB_SQLITE_DATABASE`**: Path to the SQLite database file inside the container.
  - *Sample Value:* `/home/node/.n8n/database.sqlite`

#### 2. Controller (`controller_auto`)
- **`CONTROLLER_PORT`**: Internal port the Controller listens on.
  - *Sample Value:* `5050`
- **`CONTROLLER_API_KEY`**: API key to secure the Controller's endpoints.
  - *Sample Value:* `your_controller_secret_key`
- **`MEM0_API_URL`**: URL for the Mem0 service, used by the Controller.
  - *Sample Value:* `http://mem0_auto:8000`
- **`N8N_WEBHOOK_URL`**: The specific n8n webhook URL the Controller calls to trigger master workflows.
  - *Sample Value:* `http://n8n_auto:5678/webhook/controller-master-workflow`
- **`HF_SPACE_EMBEDDER_ENDPOINT`**: URL for the Hugging Face Space embedder API, used when the Controller proxies requests for Mem0.
  - *Sample Value:* `https://YourUser-YourSpace.hf.space/v1/embeddings`
- **`OPENROUTER_PROXY_SERVICE_URL`**: Internal URL for the OpenRouter Proxy, used when the Controller proxies LLM requests for Mem0.
  - *Sample Value:* `http://openrouter_proxy_auto:8000/v1`
- **`CONTROLLER_OPENROUTER_API_KEY`**: Your actual OpenRouter API key, used by the Controller for Mem0's LLM requests.
  - *Sample Value:* `<OPENROUTER_API_KEY>`

#### 3. Mem0 (`mem0_auto`)
- **`MEM0_HOST_PORT`**: The **host port** mapped to Mem0's internal port, for direct access from the host machine.
  - *Sample Value:* `7860`
- **`MEM0_HOST`**: The hostname for Mem0, used for Traefik routing.
  - *Sample Value:* `mem0.localhost`
- **`OPENAI_API_KEY`**: **Your Hugging Face Token** (e.g., `hf_...`). Mem0 sends this as the bearer token to the Controller's embedding proxy.
  - *Sample Value:* `<HF_TOKEN>`
- **`OPENAI_BASE_URL`**: **Must point to the Controller's proxy URL** for OpenAI-compatible requests.
  - *Sample Value:* `http://controller_auto:5050/mem0_openai_proxy/v1`
- **`QDRANT_HOST`**: Hostname of the Qdrant service.
  - *Sample Value:* `qdrant_auto`
- **`QDRANT_PORT`**: Port of the Qdrant service.
  - *Sample Value:* `6333`

#### 4. PostgreSQL (`postgres_logging_auto`)
- **`POSTGRES_LOGGING_USER`**: Username for the logging database.
  - *Sample Value:* `autostack_logger`
- **`POSTGRES_LOGGING_PASSWORD`**: Password for the logging database user.
  - *Sample Value:* `your_secure_db_password`
- **`POSTGRES_LOGGING_DB`**: Name of the logging database.
  - *Sample Value:* `autostack_logs`
- **`POSTGRES_LOGGING_PORT`**: **Host port** mapped to the internal PostgreSQL port.
  - *Sample Value:* `5433`

#### 5. OpenRouter Proxy (`openrouter_proxy_auto`)
- **`OPENROUTER_API_KEY`**: Your API Key for OpenRouter.
  - *Sample Value:* `<OPENROUTER_API_KEY>`
- **`OPENROUTER_PROXY_PORT`**: **Host port** mapped to the internal proxy port.
  - *Sample Value:* `8000`
- **`YOUR_SITE_URL`** (Optional): Your app's URL, sent as `HTTP-Referer` to OpenRouter for analytics.
  - *Sample Value:* `http://chat.localhost`
- **`YOUR_SITE_NAME`** (Optional): Your app's name, sent as `X-Title` to OpenRouter for analytics.
  - *Sample Value:* `Auto-Stack Chat`

#### 6. freq-chat (`freq-chat_auto`)
- **`NEXTAUTH_URL`**: Canonical URL of your `freq-chat` deployment for NextAuth.
  - *Sample Value:* `http://localhost:3001`
- **`AUTH_SECRET`**: A secret key for NextAuth session encryption. Generate a strong random string.
  - *Sample Value:* `your_strong_nextauth_secret`

</details>

### 4. Docker Network Setup

The Docker network (`auto-stack-net`) is automatically created by the compose file, but you can verify from your WSL terminal:

```bash
# Check if network exists
docker network ls | grep auto-stack-net

# If needed, create manually
docker network create auto-stack-net
```

## Service Startup

### 1. Start Automation Stack

From a WSL terminal inside `~/projects/auto-stack`:

```bash
# Pull latest images
docker compose -f docker-compose.yml pull

# Start all services
docker compose -f docker-compose.yml up -d

# Verify services are running
docker compose -f docker-compose.yml ps
```

### 2. Start Freqtrade Dev Container

From a WSL terminal inside `~/projects/freqtrade`:

```bash
# Open the freqtrade project in VS Code using the "Focused Workflow"
code .

# Once VS Code opens, use the Command Palette to run:
# "Dev Containers: Reopen in Container"

# This will build and start the Freqtrade dev container.
# You can verify it's running with 'docker ps' from another WSL terminal.
```

## Basic Verification

### Automation Stack Services

Access these URLs to verify services are running:

| Service | URL | Expected Result |
|---------|-----|-----------------|
| **Traefik Dashboard** | `http://localhost:8080/dashboard/` | Traefik management interface |
| **n8n** | `http://n8n.localhost` or `http://localhost:5678` | n8n workflow interface |
| **Controller API** | `http://controller.localhost/docs` | FastAPI documentation |
| **OpenRouter Proxy** | `http://openrouter-proxy.localhost/healthz` | Returns "OK" |
| **freq-chat** | `http://localhost:3000` | Next.js chat interface |
| **Mem0 API** | `http://${MEM0_HOST:-mem0.localhost}:${MEM0_HOST_PORT:-7860}/status` or `http://mem0.localhost/status` (if Traefik & MEM0_HOST=mem0.localhost) | Mem0 service status (should return "Mem0 service is running and client is healthy") |
| **Qdrant API** | `http://localhost:6333` | Qdrant dashboard / REST API |
| **PostgreSQL (Logging)** | (Connect via psql or DB client on `${POSTGRES_LOGGING_PORT}`) | Database accessible |

### Freqtrade Verification

```bash
# From within the dev container terminal
freqtrade --version
freqtrade list-strategies

# Check API access
curl http://localhost:8080/api/v1/ping
```

## Integration Testing

### 1. Controller ↔ n8n Integration

```bash
# Test Controller to n8n webhook
curl -X POST http://controller.localhost/execute \
  -H "Content-Type: application/json" \
  -d '{"message": "test integration"}'
```

### 2. Mem0 Memory Operations

```bash
# Add a memory (replace MEM0_HOST_PORT if not 7860)
curl -X POST http://localhost:${MEM0_HOST_PORT:-7860}/memory \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Test memory entry from master setup"}], "user_id": "master_setup_test", "metadata": {"source": "master_setup"}}'

# Search memories (replace MEM0_HOST_PORT if not 7860)
curl -X POST http://localhost:${MEM0_HOST_PORT:-7860}/search \
  -H "Content-Type: application/json" \
  -d '{"query": "Test memory entry from master setup", "user_id": "master_setup_test"}'
```

### 3. Cross-Stack Communication

Verify that automation-stack can reach Freqtrade:

```bash
# From automation-stack container
curl http://freqtrade_devcontainer:8080/api/v1/ping
```

## Setup Verification Checklist

<details>
<summary>Click to expand Master Setup Verification Checklist</summary>

### Prerequisites Verification

- [ ] **P1:** WSL 2 is installed and operational on the host system.
- [ ] **P2:** Docker Desktop >= 25.0 installed with WSL 2 integration enabled, system rebooted.
- [ ] **P3:** Git installed and accessible from the WSL command line.
- [ ] **P4:** VS Code or Cursor installed with the "Remote - WSL" extension.
- [ ] **P5:** Node.js >= 18 LTS installed within WSL (preferably using `nvm`).
- [ ] **P6:** Hardware meets minimum requirements (16+ GB RAM).

### Environment Setup

- [ ] **E1:** Project directories created inside the WSL filesystem (`~/projects`).
- [ ] **E2:** Repositories cloned successfully into the WSL filesystem.
- [ ] **E3:** `.env` file created in `auto-stack/` and configured with required API keys.
- [ ] **E4:** Docker network `auto-stack-net` available.
- [ ] **E5:** Required ports are available (3000, 5678, 8080, etc.).

### Service Deployment

- [ ] **S1:** All automation-stack services started successfully
- [ ] **S2:** Freqtrade dev container operational
- [ ] **S3:** No critical errors in service logs
- [ ] **S4:** All required Docker volumes created and mounted

### Service Accessibility

- [ ] **A1:** Traefik dashboard accessible
- [ ] **A2:** n8n web interface accessible and functional
- [ ] **A3:** Controller API documentation accessible
- [ ] **A4:** OpenRouter proxy health check passes
- [ ] **A5:** freq-chat interface loads and responds
- [ ] **A6:** Mem0 API status endpoint (`http://<MEM0_HOST>:<MEM0_HOST_PORT>/status`) responds correctly.
- [ ] **A7:** Qdrant dashboard/API (`http://localhost:6333`) accessible.
- [ ] **A8:** PostgreSQL logging database accessible.
- [ ] **A9:** Freqtrade UI accessible and API responds

### Integration Verification

- [ ] **I1:** Controller can execute n8n webhooks
- [ ] **I2:** Mem0 memory operations (add/search via REST API) work as per `docs/guides/mem0_server_guide.md`.
- [ ] **I3:** Cross-stack communication functional (automation-stack ↔ freqtrade)
- [ ] **I4:** Basic n8n workflow creation and execution
- [ ] **I5:** freq-chat can communicate with AI providers

### Development Environment

- [ ] **D1:** VS Code connects successfully to the WSL instance.
- [ ] **D2:** The "Focused Workflow" is followed for opening projects.
- [ ] **D3:** Freqtrade Dev Container connects successfully.
- [ ] **D4:** Freqtrade CLI commands work in the dev container terminal.
- [ ] **D5:** File editing and saving works across mounted volumes from WSL.
- [ ] **D6:** Port forwarding operational for all services.

</details>

## Troubleshooting

### Common Issues

**Docker Services Won't Start**

- Verify Docker Desktop is running and WSL2 integration is enabled
- Check if required ports are already in use
- Restart Docker Desktop and try again

**Network Connectivity Issues**

- Ensure `auto-stack-net` network exists: `docker network ls`
- Verify service hostnames resolve within Docker network
- Check firewall settings for Docker containers

**Freqtrade Dev Container Issues**

- Ensure VS Code has the Dev Containers extension installed
- Try rebuilding the container: "Dev Containers: Rebuild Container"
- Check for volume mount issues in `docker-compose.yml`

**Service Access Problems**

- Verify Traefik is routing requests correctly
- Check service-specific logs: `docker logs <service_name>`
- Ensure `.env` file contains all required variables

### Log Analysis

View service logs for debugging:

```bash
# View all automation-stack logs
docker compose -f docker-compose.yml logs -f

# View specific service logs
docker logs controller_auto
docker logs n8n_auto
docker logs mem0_auto
docker logs qdrant_auto
docker logs postgres_logging_auto

# View Freqtrade logs
docker logs freqtrade_devcontainer
```

## Next Steps

After completing the master setup:

1. **Mem0 & PostgreSQL Setup**: If not already covered by `docker-compose up`, ensure Mem0, Qdrant, and PostgreSQL logging are fully configured by following `docs/guides/mem0_server_guide.md`.
2. **Service Configuration**: Review `01_Automation_Stack_Overview.md` for detailed service information.
3. **Trading Setup**: Follow `02_Trading.md` for Freqtrade-specific configuration.
4. **Service Verification**: Use `03_Core_Services_Configuration_and_Verification.md` for detailed testing.
5. **Integration Guide**: Refer to `04_Cross_Stack_Integration_Guide.md` for advanced integration patterns.

## Maintenance

### Regular Tasks

- **Update Docker Images**: `docker compose -f docker-compose.yml pull && docker compose -f docker-compose.yml up -d`
- **Clean Docker Resources**: `docker system prune -f` (use cautiously)
- **Backup Important Data**: Back up `user_data/` (Freqtrade), `mem0_data_auto/` (Mem0 history), `qdrant_data_auto/` (Qdrant vectors), `pgdata_logging_auto/` (PostgreSQL logs), and configuration files.
- **Monitor Service Health**: Check service logs and accessibility regularly

### Environment Updates

When updating the environment:

1. Stop all services
2. Update repository code
3. Update Docker images
4. Review and update `.env` file
5. Restart services
6. Run verification checklist

---

**Documentation References:**

- [docs/guides/mem0_server_guide.md](../guides/mem0_server_guide.md)
- [01_Automation_Stack_Overview.md](./01_Automation_Stack_Overview.md)
- [02_Trading.md](./02_Trading.md)
- [03_Core_Services_Configuration_and_Verification.md](./03_Core_Services_Configuration_and_Verification.md)
- [../checklists/AutomationChecklist.md](../checklists/AutomationChecklist.md)
