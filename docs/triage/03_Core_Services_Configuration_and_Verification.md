# 03: Core Services Configuration and Verification

**Status:** New Document - $(date +%Y-%m-%d)

This document provides a guide for the initial configuration and verification of core services within both the `automation-stack` and the `freqtrade` dev container environment. It expands on the checklist items found in `AutomationChecklist.md`.

**Legend for Verification Status (as used in `AutomationChecklist.md`):**

* `[ ]` - Pending / To Be Verified
* `[✅]` - Verified / Completed Successfully
* `[❌]` - Failed / Error / Issue Noted
* `[🚧]` - In Progress / Under Development
* `[N/A]` - Not Applicable (for current baseline)

---

## I. `automation-stack` Core Service Verification

These steps help ensure all services defined in `automation-stack/docker-compose.yml` are operational and correctly configured.

### 1. `freq-chat` (Vercel AI Chatbot)

* **Purpose:** Primary user-facing chat interface using Next.js and Vercel AI SDK.
* **Local Directory:** `freq-chat/`
* **Deployment:** Hosted on Vercel.
* **Configuration:**
  * Vercel project settings (environment variables for API keys like `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, model provider configurations).
  * Local development: `.env.development.local` in the `freq-chat/` directory (pulled from Vercel or manually created).
  * Next.js configuration files within `freq-chat/` (e.g., `next.config.js`).
* **Verification:**
  * **Local Development Server:** From a WSL terminal, navigate to `~/projects/freq-chat` and run `pnpm dev`. Access at `http://localhost:3000`. Check the WSL terminal for console errors.
  * **Environment Variables:** Ensure necessary API keys and service URLs (e.g., for Mem0 if integrated) are present and correctly loaded in both local and Vercel environments.
  * **Core Chat Functionality:** Test sending messages, receiving responses from the configured LLM(s).
  * **Mem0 Integration (If applicable):** Verify that `freq-chat` can store and retrieve conversational memory from the Mem0 service. Check Mem0 logs for interaction.
  * **Deployment Status:** Check the Vercel dashboard for successful deployments of the `freq-chat` project.
  * **Connectivity to Backend Services:** If `freq-chat`'s backend calls other services in the `automation-stack` (e.g., controller, n8n, OpenRouter Proxy, Ollama), ensure these are reachable from the Vercel environment or its local dev environment.

#### Docker Compose Example (`docker-compose.yml`)
```yaml
services:
  freq_chat_auto:
    # Build context points to the Next.js app directory
    build: { context: ./freq-chat, dockerfile: Dockerfile }
    # Environment variables for the Next.js app
    # Environment variables for the Next.js app are typically in ./freq-chat/.env.development.local
    env_file: ["./freq-chat/.env.development.local"] # Or .env.production
    volumes:
      # Mount the source code for hot-reloading in development
      - "./freq-chat:/app"
      # Avoid overwriting node_modules inside the container
      - "/app/node_modules" # Standard practice for Node.js development
    ports:
      # Map host port (from .env) to container port 3000
      - "${FREQCHAT_EXTERNAL_PORT:-3001}:3000"
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.freq_chat_auto.rule=Host(`${FREQCHAT_TRAEFIK_HOST:-chat.localhost}`)"
      - "traefik.http.services.freq_chat_auto.loadbalancer.server.port=3000"
    networks:
      - auto-stack-net
```

### 2. Traefik Reverse Proxy (`traefik_auto`)

* **Purpose:** Manages external access to services, handles routing, and can provide a dashboard.
* **Configuration:** Primarily configured via labels in `docker-compose.yml` and its own static configuration (e.g., `traefik.yml` or command-line arguments in `docker-compose.yml`).
* **Verification:**
  * **Traefik Dashboard:** From your host machine's browser (or a browser in a desktop environment if using a GUI on Linux), if enabled in Traefik's configuration, attempt to access its dashboard. Common URLs are `http://localhost:8081/dashboard/` (if port 8081 is mapped to Traefik's API/dashboard port, which is different from its entrypoint ports like 80/443) or a hostname like `http://traefik.localhost/dashboard/` if configured.
    * *Note:* Dashboard access might be secured or disabled in some production-like setups.
  * **Service Routing:** From a WSL terminal, use `curl` to verify that other services (n8n, Controller) are accessible via their configured Traefik hostnames (e.g., `curl http://n8n.localhost`, `curl http://controller.localhost`). `freq-chat` itself is typically accessed via its Vercel URL or `localhost:3000` during local development, not through Traefik in this stack, unless explicitly configured for a custom domain proxied by Traefik.

#### Docker Compose Example (`docker-compose.yml`)
```yaml
services:
  traefik_auto:
    image: traefik:v2.11
    # Command to use the static configuration file
    command:
      - "--api.insecure=true"
      - "--providers.docker=true"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
    ports:
      # HTTP, HTTPS, and Dashboard ports
      - "80:80"
      - "443:443"
      - "8080:8080" # Traefik dashboard
    volumes:
      # Mount the Docker socket to discover services
      - "/var/run/docker.sock:/var/run/docker.sock:ro"
      # Mount the static configuration file
      - "./traefik.yml:/etc/traefik/traefik.yml:ro"
      # Optional: Mount a directory for TLS certificates
      - "./certs:/certs:ro"
    networks:
      - auto-stack-net
```

#### Static Configuration (`traefik.yml`)
```yaml
# API and dashboard configuration
api:
  dashboard: true
  insecure: true # Set to false and configure TLS for production

# Entrypoints for web traffic
entryPoints:
  web:
    address: ":80"
  websecure:
    address: ":443"

# Docker provider configuration
providers:
  docker:
    endpoint: "unix:///var/run/docker.sock"
    exposedByDefault: false # Only expose containers with traefik.enable=true label
```

### 3. n8n (`n8n_auto`)

* **Purpose:** Workflow automation.
* **Configuration:** Via environment variables in `.env` (e.g., timezone, generic functions usage, execution data pruning, `N8N_ALLOW_EXEC` for specific nodes) and within its web interface for workflows, credentials, etc.
* **Verification:**
  * **Web Interface Access:** Access via its Traefik hostname (e.g., `http://n8n.localhost`) or direct host port if mapped (e.g., `http://localhost:5678`) from a browser on the host machine.
  * **Workflow Creation/Execution:** Create a simple workflow (e.g., Manual Trigger -> Set Node -> Log to Console) and execute it to ensure basic functionality.
  * **Network Connectivity:** In a test workflow, use an "HTTP Request" node to try and reach other services on the `auto-stack-net` network by their service names (e.g., `http://controller_auto:5050/status`). This verifies container-to-container communication within the WSL-managed Docker network.
  * **Volume Access (If Used):** If workflows are designed to interact with shared volumes (e.g., `/host_vault/automation_docs/`), test a workflow that attempts to read a file from such a mount to ensure permissions and paths are correct. Note that paths like `/host_vault/` imply a specific volume mount from the host machine that must be correctly configured in `docker-compose.yml` to be accessible from WSL.
  * **n8nChat Extension Configuration:** If using the n8nChat browser extension, ensure it can connect to this n8n instance (`http://n8n.localhost`) and, if desired, that it's configured to use the `openrouter_proxy_auto` for LLM functionalities (see `../n8n/n8nChat.md` and `../proxy.md`).
  * **Agent Orchestration Workflows:** If implementing multi-agent orchestration (e.g., CentralBrain_Agent, DocAgent), verify that these workflows are present, correctly configured, and able to trigger sub-agent workflows via HTTP webhooks. Ensure all required webhook endpoints are accessible and that agent workflows can dispatch and aggregate tasks as designed. These might be initiated or present results through `freq-chat`.

#### Docker Compose Example (`docker-compose.yml`)
```yaml
services:
  n8n_auto:
    image: n8nio/n8n:latest
    env_file: [".env"] # Loads variables like N8N_BASIC_AUTH_USER, etc.
    volumes:
      # Mounts a host directory for persistent n8n data
      - "n8n_data_auto:/home/node/.n8n"
    ports: ["5678:5678"]
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.n8n_auto.rule=Host(`${N8N_TRAEFIK_HOST:-n8n.localhost}`)"
      - "traefik.http.services.n8n_auto.loadbalancer.server.port=5678"
    networks: [auto-stack-net]
```

### 4. Mem0 (`mem0_auto`)

* **Purpose:** Self-hosted, centralized memory and knowledge management service using Qdrant as its vector store and an OpenRouter proxy for LLM/embedding tasks. Exposes a REST API.
* **Local Directory:** `automation-stack/mem0/server/`
* **Configuration:**
  * **`docker-compose.yml`:** Defines the `mem0_auto` service, its build context (`./mem0/server`), Dockerfile, environment variables (see below), port mapping (e.g., `${MEM0_EXTERNAL_PORT}:8000`), volumes (`./mem0/server/config.yaml:/app/config.yaml:ro`, `mem0_data_auto:/data`), network (`auto-stack-net`), and dependencies (qdrant_auto, openrouter_proxy_auto).
  * **`mem0/server/config.yaml`:** Configures the Mem0 instance:
    * `vector_store`: Provider `qdrant`, host `qdrant_auto`, port `6333`.
    * `llm`: Provider `openai`, model (e.g., `tngtech/deepseek-r1t-chimera:free`). This request will be proxied by the controller.
    * `embedder`: Provider `openai`, model `BAAI/bge-base-en-v1.5`. This request will be proxied by the controller.
    * `history_db_path`: e.g., `/data/mem0_history.db` (persisted in `mem0_data_auto` volume).
  * **`.env` (root project) for `mem0_auto` service:**
    * `OPENAI_API_KEY`: Your **Hugging Face Token** (e.g., `hf_YourToken...`).
    * `OPENAI_BASE_URL`: Points to the controller proxy (e.g., `http://controller_auto:5050/mem0_openai_proxy/v1`).
  * **`.env` (root project) for `controller_auto` service (related to Mem0 proxying):**
    * `HF_SPACE_EMBEDDER_ENDPOINT`: URL of your HF Space embedder (e.g., `https://GleshenCOCO-bge-embedding-api.hf.space/v1/embeddings`).
    * `OPENROUTER_PROXY_SERVICE_URL`: Internal URL to your OpenRouter Proxy (e.g., `http://openrouter_proxy_auto:8000/v1`).
    * `CONTROLLER_OPENROUTER_API_KEY`: Your actual OpenRouter API key.
  * **Dependencies:** `mem0/server/requirements.txt` (includes `mem0ai`, `fastapi`, `uvicorn`, `qdrant-client`, `openai`).
* **Verification:**
  * **Container Status:** From a WSL terminal, run `docker ps | grep mem0_auto` (should be running).
  * **Server Logs:** From a WSL terminal, run `docker logs mem0_auto`. Check for successful initialization and connection to Qdrant. It will log the `OPENAI_BASE_URL` it's using.
  * **Controller Logs:** From a WSL terminal, run `docker logs controller_auto`. Check for logs related to receiving requests from Mem0 and proxying them to either the HF Space or OpenRouter Proxy if applicable.
  * **Health Check Endpoint (Mem0):** From a WSL terminal, run `curl http://${MEM0_TRAEFIK_HOST:-mem0.localhost}:${MEM0_EXTERNAL_PORT:-8000}/status` (or use Traefik URL `http://${MEM0_TRAEFIK_HOST}/status`). Expected: `{"status": "Mem0 service is running and client is healthy"}`.
  * **Memory Operations Test (REST API):**
    * **Add Memory:** From a WSL terminal, run `curl -X POST http://localhost:${MEM0_EXTERNAL_PORT:-8000}/memory -H "Content-Type: application/json" -d '{"messages": [{"role": "user", "content": "Test memory from core verification"}], "user_id": "core_verify_user", "metadata": {"source": "03_Core_Services"}}'`
    * **Search Memory:** From a WSL terminal, run `curl -X POST http://localhost:${MEM0_EXTERNAL_PORT:-8000}/search -H "Content-Type: application/json" -d '{"query": "Test memory from core verification", "user_id": "core_verify_user"}'`
  * **Data Persistence:**
    * Verify `mem0_data_auto` volume is created and used. This can be checked with `docker volume ls` in a WSL terminal.
    * Restart `mem0_auto` and `qdrant_auto` services and confirm previously added memories can be searched.
  * **Controller Integration (Direct, if any remains):** If controller still makes direct calls to `http://mem0_auto:8000` for other purposes, ensure `MEM0_API_URL` is set for the controller.
  * **n8n Integration (Direct, if any):** If n8n makes direct calls to `http://mem0_auto:8000`, these would bypass the controller proxy. For LLM/embedder functions, n8n should ideally also go via the controller proxy or have its own means to use the correct endpoints/tokens.
* **Detailed Guide:** `docs/guides/mem0_server_guide.md`.

#### Docker Compose Example (`docker-compose.yml`)
```yaml
services:
  mem0_auto:
    build: { context: ./mem0/server, dockerfile: Dockerfile }
    env_file:
      - ./.env
      - ./mem0/.env
    volumes:
      # Mount the service's specific config.yaml
      - "./mem0/server/config.yaml:/app/config.yaml:ro"
      # Mount a named volume for persistent data (history DB, etc.)
      - "mem0_data_auto:/data" # Ensure mem0_data_auto is defined in top-level volumes
    ports: ["${MEM0_EXTERNAL_PORT:-8000}:8000"] # Internal port 8000 from mem0/.env
    depends_on: [qdrant_auto, openrouter_proxy_auto]
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.mem0_auto.rule=Host(`${MEM0_TRAEFIK_HOST:-mem0.localhost}`)"
      - "traefik.http.services.mem0_auto.loadbalancer.server.port=8000"
    networks: [auto-stack-net]
```

### 5. Qdrant (`qdrant_auto`)

* **Purpose:** Vector database for the self-hosted Mem0 service.
* **Configuration:**
  * **`docker-compose.yml`:** Uses `qdrant/qdrant:latest` image, maps ports (e.g., `6333:6333`), mounts `qdrant_data_auto:/qdrant/storage` volume, and connects to `auto-stack-net`.
* **Verification:**
  * **Container Status:** From a WSL terminal, run `docker ps | grep qdrant_auto` (should be running).
  * **Server Logs:** From a WSL terminal, run `docker logs qdrant_auto`.
  * **Accessibility:** `http://localhost:6333` should show Qdrant info or allow access to its dashboard/UI if available. Mem0 service logs should indicate successful connection. This is accessed from a browser on the host.
  * **Data Persistence:** Verify `qdrant_data_auto` volume with `docker volume ls` in a WSL terminal. Data should persist across restarts.
* **Detailed Guide:** `docs/guides/mem0_server_guide.md`.

#### Docker Compose Example (`docker-compose.yml`)
```yaml
services:
  qdrant_auto:
    image: qdrant/qdrant:latest
    volumes:
      # Mount a named volume for persistent vector storage
      - "qdrant_data_auto:/qdrant/storage"
    ports:
      # Expose the gRPC and HTTP API ports
      - "6333:6333" # http
      - "6334:6334" # grpc
    networks: [auto-stack-net]
```

### 6. PostgreSQL for Unified Logging (`postgres_logging_auto`)

* **Purpose:** Centralized database for storing logs from various `automation-stack` services.
* **Configuration:**
  * **`docker-compose.yml`:** Uses `postgres:15` (or similar) image. Environment variables `POSTGRES_LOGGING_USER`, `POSTGRES_LOGGING_PASSWORD`, `POSTGRES_LOGGING_DB` are sourced from the root `.env` file. Maps host port (e.g., `${POSTGRES_LOGGING_PORT}:5432`). Mounts `pgdata_logging_auto:/var/lib/postgresql/data` volume. Connects to `auto-stack-net`.
  * **`.env` (root project):** Define `POSTGRES_LOGGING_USER`, `POSTGRES_LOGGING_PASSWORD`, `POSTGRES_LOGGING_DB`, `POSTGRES_LOGGING_PORT`.
* **Verification:**
  * **Container Status:** From a WSL terminal, run `docker ps | grep postgres_logging_auto` (should be running).
  * **Server Logs:** From a WSL terminal, run `docker logs postgres_logging_auto`.
  * **Connection:** From a WSL terminal, connect using `psql` by executing it inside the running container:

        ```bash
        docker exec -it postgres_logging_auto psql -U ${POSTGRES_LOGGING_USER} -d ${POSTGRES_LOGGING_DB}
        ```

  * **Table Creation:** Ensure the `agent_logs` table is created as per `docs/guides/mem0_server_guide.md`. Once inside `psql`, run:

        ```sql
        \dt agent_logs; 
        ```

  * **Data Persistence:** Verify `pgdata_logging_auto` volume. Logs should persist across restarts.
* **Detailed Guide:** `docs/guides/mem0_server_guide.md`.

#### Docker Compose Example (`docker-compose.yml`)
```yaml
services:
  postgres_logging_auto:
    image: postgres:15
    env_file: [".env"]
    volumes:
      # Mount a named volume for persistent database storage
      - "pgdata_logging_auto:/var/lib/postgresql/data"
    ports: ["${POSTGRES_LOGGING_EXTERNAL_PORT:-5432}:5432"] # Uses var from root .env
    networks: [auto-stack-net]
```

### 7. FastAPI Controller (`controller_auto`)

* **Purpose:** Custom API for automation tasks.
* **Configuration:**
  * The controller's Dockerfile now uses `ARG CONTROLLER_PORT` and `ENV PORT=$CONTROLLER_PORT` to set the port at build and runtime, and uses a shell-form `CMD` so `$PORT` is expanded at container start. The port is set via the `CONTROLLER_PORT` environment variable in `.env` and passed through `docker-compose.yml`.
  * **Troubleshooting:** If you see errors like `Error: Invalid value for '--port': '${PORT}' is not a valid integer.`, ensure the Dockerfile uses shell-form `CMD` (`CMD uvicorn controller:app --host 0.0.0.0 --port $PORT`) and that `ENV PORT=$CONTROLLER_PORT` (or similar) is set in the Dockerfile. The `controller/Dockerfile` has been updated to use `ENV PORT=$CONTROLLER_PORT` and `CMD uvicorn controller:app --host 0.0.0.0 --port $PORT`.
  * Other environment variables: `N8N_WEBHOOK_URL`, `EKO_SERVICE_URL`.
* **Verification:**
  * **Service Logs:** From a WSL terminal, run `docker logs controller_auto`. Check for startup messages, warnings about missing proxy env vars if not set.
  * **API Accessibility (Standard Endpoints):**
    * Via Traefik (from a WSL terminal): `curl http://controller.localhost/docs`, `curl http://controller.localhost/status`.
  * **API Accessibility (Proxy Endpoints):** These are for internal use by Mem0, but you could test them with `curl` from another container on `auto-stack-net` if needed, e.g., from a WSL terminal run `docker exec n8n_auto curl -X POST http://controller_auto:5050/mem0_openai_proxy/v1/embeddings -H "Authorization: Bearer YOUR_HF_TOKEN" -H "Content-Type: application/json" -d '{"input": "test", "model": "BAAI/bge-base-en-v1.5"}'`.
  * **Key Endpoints:**
    * `GET /status`: Should return `{"status": "Controller is running"}`.
    * The Mem0 proxy endpoints should function as intermediaries.

#### Docker Compose Example (`docker-compose.yml`)
```yaml
services:
  controller_auto:
    build: { context: ./controller, dockerfile: Dockerfile }
    env_file:
      - ./.env
      - ./controller/.env
    volumes:
      # Mount the controller's source code as read-only
      - "./controller:/app:ro"
    ports: ["${CONTROLLER_EXTERNAL_PORT:-5050}:${CONTROLLER_PORT:-5050}"] # CONTROLLER_PORT from controller/.env
    depends_on: [n8n_auto, mem0_auto, postgres_logging_auto, openrouter_proxy_auto, bge_embedding_auto]
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.controller_auto.rule=Host(`${CONTROLLER_TRAEFIK_HOST:-controller.localhost}`)"
      - "traefik.http.services.controller_auto.loadbalancer.server.port=${CONTROLLER_PORT:-5050}"
    networks: [auto-stack-net]
```

### 8. OpenRouter Proxy (`openrouter_proxy_auto`) (Optional)

* **Purpose:** Proxies requests to OpenRouter.ai, injecting API key.
* **Configuration:** Via `OPENROUTER_KEY` and other `OPENROUTER_PROXY_*` variables in `.env`.
* **Verification:**
  * **Service Logs:** From a WSL terminal, run `docker logs openrouter_proxy_auto`. Look for startup message like `🚀 OpenRouter Proxy (Node.js) listening on http://localhost:<PROXY_PORT>/v1`.
  * **Environment Variable Check:** Ensure `OPENROUTER_KEY` is set in `.env`. The proxy will exit if it's not set.
  * **Health Check:** From a WSL terminal, access `http://<OPENROUTER_PROXY_HOST>/healthz` (e.g., `curl http://openrouter-proxy.localhost/healthz`). Should return `OK`.
  * **Traefik Routing:** Verify the service is correctly routed via its Traefik hostname (e.g., `http://openrouter-proxy.localhost/v1/...`). Check Traefik dashboard for a healthy backend.
  * **Basic Proxy Test (cURL):** From a WSL terminal, use `curl` as shown in `../proxy.md` to make a test call through the proxy to an OpenRouter model. Ensure you get a valid JSON response from the model.
  * **Client Configuration (n8n, n8nChat):** Verify that clients intending to use this proxy (e.g., n8n HTTP Request nodes, n8n "MCP Client" nodes, or the n8nChat extension) are correctly configured with the proxy URL (`http://openrouter-proxy.localhost/v1`) and a dummy API key, as detailed in `../proxy.md` and `../n8n/n8nChat.md`.

#### Docker Compose Example (`docker-compose.yml`)
```yaml
services:
  openrouter_proxy_auto:
    # Build from the proxy's directory
    build: { context: ./openrouter_proxy, dockerfile: Dockerfile }
    env_file:
      - ./.env
      - ./openrouter_proxy/.env
    ports: ["${OPENROUTER_PROXY_EXTERNAL_PORT:-8001}:8000"] # Internal port 8000 from openrouter_proxy/.env
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.openrouter_proxy_auto.rule=Host(`${OPENROUTER_PROXY_TRAEFIK_HOST:-openrouter.localhost}`)"
      - "traefik.http.services.openrouter_proxy_auto.loadbalancer.server.port=8000"
    networks: [auto-stack-net]
```

---

## II. `freqtrade` Dev Container Verification

Ensure the Freqtrade dev container is operational and configured for development and testing.

### 1. Freqtrade Dev Container (`freqtrade_devcontainer`)

* **Purpose:** Algorithmic trading bot, strategy development, and backtesting.
* **Configuration:** `devcontainer.json`, Docker Compose file (`freqtrade/docker-compose.yml`), and `user_data/config.json`.
* **Verification:**
  * **Container Startup:** Ensure the container starts successfully by following the "Focused Workflow": in a WSL terminal, `cd ~/projects/freqtrade`, run `code .`, then use "Reopen in Container".
  * **Freqtrade UI Access:** If Freqtrade's API/UI port (default `8080`) is forwarded, verify access from a browser on the host at `http://localhost:8080`.
  * **Freqtrade REST API:** From a WSL terminal, test a basic API call, e.g., `curl http://localhost:8080/api/v1/ping` or `curl http://freqtrade_devcontainer:8080/api/v1/ping` from within another container on the Docker network.
  * **`user_data` Mount:** Verify that the `freqtrade/user_data` directory is correctly mounted into the container. From a WSL terminal, run `docker exec -it freqtrade_devcontainer bash` and then `ls -la /freqtrade/user_data/`.
  * **Freqtrade CLI Commands:** Open a terminal in VS Code (which should be connected to the dev container) and run basic Freqtrade commands:
    * `freqtrade --version`
    * `freqtrade list-strategies` (should list strategies from `user_data/strategies/`)
    * `freqtrade test-pairlist` (requires `config.json` to be minimally configured).
  * **Network Connectivity to `automation-stack` (If Needed):** If the Freqtrade container needs to call APIs on the `automation-stack` (e.g., the controller), ensure it's connected to the appropriate shared Docker network (e.g., `auto-stack-net`) and can resolve services by name.

---

## VII. Unified Logging & Multi-Agent Orchestration Verification

* **Unified Logging:**
  * [ ] Verify all agents log to unified PostgreSQL table with `agent` field (see UnifiedLogging.md).
  * [ ] Confirm log entries from CentralBrain_Agent, manager agents, and sub-agents are present and queryable.
* **Multi-Agent Orchestration:**
  * [ ] Confirm CentralBrain_Agent, manager agents, and sub-agents are present and correctly configured (see CentralBrain.md).
* **FastAPI Controller/n8n Integration:**
  * [ ] Verify n8n workflow can trigger and be triggered by the FastAPI Controller using /execute and /notify endpoints (see webhookFlows.md).
* **Mem0 Integration:**
  * [✅] Self-hosted Mem0 service (`mem0_auto`) is running, using Qdrant and OpenRouter proxy.
  * [✅] Mem0 REST API endpoints (`/status`, `/memory`, `/search`) are functional.
  * [ ] Controller can successfully interact with Mem0's REST API.
  * [ ] n8n workflows can successfully interact with Mem0's REST API.
  * [ ] `freq-chat` (if applicable for backend interaction) can interact with Mem0's REST API.
  * [ ] Data persistence for Mem0 (history DB) and Qdrant (vector store) is verified across container restarts.
  * [✅] Configuration in `docker-compose.yml` and `mem0/server/config.yaml` aligns with `docs/guides/mem0_server_guide.md`.
* **PostgreSQL Logging Integration:**
  * [✅] `postgres_logging_auto` service is running.
  * [ ] `agent_logs` table is created and accessible.
  * [ ] n8n workflows (or other services) can successfully write logs to the `agent_logs` table.
  * [ ] Log data persists across container restarts.

This guide provides a starting point for configuration and verification. Always refer to the specific documentation for each service, `docs/guides/mem0_server_guide.md` for Mem0/PostgreSQL specifics, and the project's `AutomationChecklist.md` for a live status of these checks.
