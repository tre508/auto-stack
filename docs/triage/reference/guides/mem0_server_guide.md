# Comprehensive Guide: Mem0 Service and PostgreSQL Integration

**Version:** 1.0
**Date:** $(date +%Y-%m-%d)

## 1. Introduction

This guide provides a comprehensive walkthrough for setting up and integrating the self-hosted Mem0 service and a PostgreSQL database within the `automation-stack` project.

### Mem0 Overview
Mem0 is an intelligent memory layer designed to enhance AI assistants and agents by enabling personalized AI interactions. It remembers user preferences, adapts to individual needs, and continuously learns over time. In the `automation-stack`, the self-hosted Mem0 service will provide persistent memory for various components, including `freq-chat`, n8n workflows, and the FastAPI controller, facilitating context retention and Retrieval Augmented Generation (RAG). The self-hosted Mem0 server exposes a REST API for these interactions.

### PostgreSQL for Unified Logging Overview
A PostgreSQL database will be set up to serve as a centralized store for unified logging across different services and agents within the `automation-stack`. This allows for easier monitoring, debugging, and auditing of system activities. The primary table for this will be `agent_logs`.

## 2. Prerequisites

Before you begin, ensure you have the following software, tools, and access:

*   **Docker and Docker Compose:** For running containerized services. Ensure they are installed and operational.
*   **Git:** For cloning repositories if any external dependencies or examples are needed (though for this guide, we primarily use existing project files).
*   **Text Editor/IDE:** For editing configuration files (e.g., VS Code).
*   **Terminal/Command Line Interface:** For executing Docker commands.
*   **`.env` file:** Access to the root `.env` file in the `automation-stack` project to manage secrets and environment-specific configurations.
*   **Project Files:** Access to the `automation-stack` project structure, particularly `compose-mcp.yml` and the `mem0/server/` directory.

## 3. PostgreSQL Setup for Unified Logging

This section details setting up a PostgreSQL container for unified logging.

### 3.1. Docker Compose Configuration (`compose-mcp.yml`)

Add or update the PostgreSQL service definition in your `compose-mcp.yml` file.

```yaml
services:
  # ... other services (traefik_mcp, n8n_mcp, controller_mcp, mem0_mcp, qdrant_mcp, etc.)

  postgres_logging_mcp:
    image: postgres:15 # Or latest, e.g., postgres:latest
    container_name: postgres_logging_mcp
    restart: unless-stopped
    environment:
      POSTGRES_USER: ${POSTGRES_LOGGING_USER} # Define in your .env file
      POSTGRES_PASSWORD: ${POSTGRES_LOGGING_PASSWORD} # Define in your .env file
      POSTGRES_DB: ${POSTGRES_LOGGING_DB} # Define in your .env file
    volumes:
      - pgdata_logging_mcp:/var/lib/postgresql/data
    ports:
      - "5433:5432" # Define POSTGRES_LOGGING_PORT in .env (e.g., 5433), hardcoded here due to potential .env parsing issues
    networks:
      - mcp-net

# ... other services

volumes:
  # ... other volumes
  pgdata_logging_mcp: {}

# networks:
#   mcp-net:
#     driver: bridge
```

**Note:** Ensure you add the corresponding variables (`POSTGRES_LOGGING_USER`, `POSTGRES_LOGGING_PASSWORD`, `POSTGRES_LOGGING_DB`, `POSTGRES_LOGGING_PORT`) to your root `.env` file. For example:

```env
# In .env
POSTGRES_LOGGING_USER=autostack_logger
POSTGRES_LOGGING_PASSWORD=yoursecurepassword_logger
POSTGRES_LOGGING_DB=autostack_logs
POSTGRES_LOGGING_PORT=5433 # Example host port
```

### 3.2. Initialization
On the first run of `docker-compose up -d postgres_logging_mcp`, Docker will pull the PostgreSQL image, create the container, and PostgreSQL will automatically initialize the database specified by `POSTGRES_DB` and create the user specified by `POSTGRES_USER` with the given `POSTGRES_PASSWORD`. The data will be persisted in the `pgdata_logging_mcp` volume.

### 3.3. Table Creation (`agent_logs`)
After the PostgreSQL container is running, you need to create the `agent_logs` table.

1.  **Connect to the PostgreSQL container:**
    ```bash
    docker exec -it postgres_logging_mcp psql -U ${POSTGRES_LOGGING_USER} -d ${POSTGRES_LOGGING_DB}
    ```
    (Replace `${POSTGRES_LOGGING_USER}` and `${POSTGRES_LOGGING_DB}` with the actual values from your `.env` file if your shell doesn't expand them directly, or use the values directly, e.g., `psql -U autostack_logger -d autostack_logs`). You will be prompted for the password.

2.  **Run the SQL `CREATE TABLE` statement:**
    Once connected via `psql`, execute the following SQL command:
    ```sql
    CREATE TABLE IF NOT EXISTS agent_logs (
        id SERIAL PRIMARY KEY,
        timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        agent VARCHAR(64),
        workflow VARCHAR(64),
        action TEXT,
        status VARCHAR(16),
        details JSONB,
        error TEXT
    );
    ```
    To exit `psql`, type `\q` and press Enter.

## 4. Mem0 Service Setup (Self-Hosted)

This section covers setting up the self-hosted Mem0 service using Docker.

### 4.1. Vector Database Choice & Setup (Qdrant)

Qdrant is chosen as the vector database for Mem0 due to its performance, scalability, and ease of use, particularly with Docker. It's also explicitly supported by the Mem0 library.

#### 4.1.1. Qdrant Docker Compose Configuration (`compose-mcp.yml`)
Ensure the following service definition for Qdrant exists in your `compose-mcp.yml`:

```yaml
services:
  # ... other services

  qdrant_mcp:
    image: qdrant/qdrant:latest
    container_name: qdrant_mcp
    restart: unless-stopped
    ports:
      - "6335:6333" # REST API - Host port changed from 6333 due to potential conflicts
      - "6336:6334" # gRPC - Host port changed from 6334 due to potential conflicts
    volumes:
      - qdrant_data_mcp:/qdrant/storage # Persists Qdrant data
    networks:
      - mcp-net

# ... other services

volumes:
  # ... other volumes
  qdrant_data_mcp: {}
```
The `qdrant_data_mcp` volume ensures that your vector embeddings persist across container restarts.

### 4.2. Mem0 Docker Compose Configuration (`compose-mcp.yml`)

Update or add the Mem0 service definition in `compose-mcp.yml`:

```yaml
services:
  # ... other services (traefik_mcp, n8n_mcp, controller_mcp, qdrant_mcp, postgres_logging_mcp, etc.)

  mem0_mcp:
    build:
      context: ./mem0/server
      dockerfile: Dockerfile
    container_name: mem0_mcp
    restart: unless-stopped
    environment:
      # --- Core Mem0 Server Settings ---
      - MEM0_CONFIG_PATH=/app/config.yaml # Path inside the container
      - PORT=8000 # Internal port the FastAPI server runs on (as per Dockerfile)

      # --- LLM & Embedder Configuration (via OpenAI provider pointing to OpenRouter Proxy) ---
      # These are picked up by mem0/server/app.py if config.yaml uses provider: "openai" for LLM
      - OPENAI_API_KEY=${OPENROUTER_API_KEY} # Use your OpenRouter API key from .env
      - OPENAI_BASE_URL=http://openrouter_proxy_mcp:8000/v1 # Points to your openrouter_proxy_mcp service

      # --- Optional: Direct Database Connection Strings (if not using default SQLite for history) ---
      # - NEO4J_URI=bolt://neo4j_mcp:7687
      # - NEO4J_USERNAME=neo4j
      # - NEO4J_PASSWORD=your_neo4j_password
      # - POSTGRES_URI=postgresql://user:pass@postgres_mcp:5432/mem0historydb # For history DB if using Postgres

    ports:
      - "7860:8000" # Define MEM0_HOST_PORT in .env (e.g., 7860), hardcoded here due to potential .env parsing issues
    volumes:
      - ./mem0/server/config.yaml:/app/config.yaml:ro # Mount your config file
      - mem0_data_mcp:/data # For persistent data (vector store, history DB if SQLite)
    networks:
      - mcp-net
    depends_on:
      - qdrant_mcp
      - openrouter_proxy_mcp # Depends on the proxy for LLM calls
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.mem0_mcp.rule=Host(`${MEM0_HOST}`)" # Define MEM0_HOST in .env, e.g., mem0.localhost
      - "traefik.http.services.mem0_mcp.loadbalancer.server.port=8000"

# ... other services

volumes:
  # ... other volumes
  mem0_data_mcp: {}
```
**Notes on `.env` variables for Mem0:**
- `OPENROUTER_API_KEY`: Your API key for OpenRouter.ai.
- `MEM0_HOST_PORT`: The host port you want to map to Mem0's internal port 8000 (e.g., `7860`).
- `MEM0_HOST`: The hostname for accessing Mem0 via Traefik (e.g., `mem0.localhost`).

### 4.3. Mem0 `config.yaml` Configuration (`mem0/server/config.yaml`)

Create or update the `mem0/server/config.yaml` file with the following content. This configuration prioritizes Qdrant for vector storage, uses the "openai" provider type for the LLM (to leverage OpenRouter proxy), and "sentence_transformer" for local embeddings.

```yaml
# mem0/server/config.yaml

# --- Vector Store ---
vector_store:
  provider: "qdrant"
  config:
    host: "qdrant_mcp" # Service name of Qdrant in Docker Compose network
    port: 6333
    collection_name: "mem0_autostack_collection" # Or your preferred collection name

# --- LLM Configuration ---
# Uses the "openai" provider type. The actual endpoint and API key are determined
# by OPENAI_BASE_URL and OPENAI_API_KEY environment variables set in docker-compose.yml,
# pointing to your OpenRouter proxy.
llm:
  provider: "openai"
  config:
    model: "deepseek/deepseek-chat" # Example: Choose a model available on OpenRouter
    # temperature: 0.7 # Optional

# --- Embedder Configuration ---
# Using a local SentenceTransformer model to avoid proxy issues for embeddings.
embedder:
  provider: "sentence_transformer" 
  config:
    model: "all-MiniLM-L6-v2" # A popular, lightweight SentenceTransformer model

# --- Graph Store (Optional) ---
# If you want to use a graph database (e.g., Neo4j), uncomment and configure.
# Ensure the Neo4j service is also defined in compose-mcp.yml and env vars are set.
# graph_store:
#   provider: "neo4j"
#   config:
#     uri: ${NEO4J_URI} # e.g., bolt://neo4j_mcp:7687
#     user: ${NEO4J_USER}
#     password: ${NEO4J_PASSWORD}

# --- History Database (Optional) ---
# Defaults to an in-memory SQLite database if not specified.
# For persistence, use a file path that maps to a Docker volume.
history_db_path: "/data/mem0_history.db" # Path inside the container, mapped to mem0_data_mcp volume

# --- Other Configurations (Optional) ---
# verbose: true
# log_level: "INFO"
```

**Explanation of LLM/Embedder Configuration:**
- **LLM (Large Language Model):**
    - By setting `provider: "openai"` for `llm` in `config.yaml`, Mem0's underlying Python SDK will attempt to use the standard OpenAI client.
    - The `mem0/server/app.py` (and the Mem0 SDK it uses) picks up the `OPENAI_API_KEY` and `OPENAI_BASE_URL` environment variables.
    - In `compose-mcp.yml`, these are set for the `mem0_mcp` service as:
        - `OPENAI_API_KEY=${OPENROUTER_API_KEY}`
        - `OPENAI_BASE_URL=http://openrouter_proxy_mcp:8000/v1`
    - This routes Mem0's LLM calls through your `openrouter_proxy_mcp` service.
- **Embedder:**
    - The `embedder` is configured with `provider: "sentence_transformer"` and `model: "all-MiniLM-L6-v2"`.
    - This uses a local SentenceTransformer model for generating embeddings, which is downloaded by the `mem0ai` library when the service starts. This avoids issues with the `openrouter_proxy_mcp` not supporting the `/v1/embeddings` endpoint.
    - Ensure `sentence-transformers` is listed in `mem0/server/requirements.txt`.

### 4.4. Building and Running
1.  **Ensure Dependencies are Met:**
    *   The `mem0/server/requirements.txt` should include `mem0ai`, `fastapi`, `uvicorn[standard]`, `qdrant-client`, `openai` (for the LLM OpenAI provider), and `sentence-transformers` (for the local embedder).
    *   The `mem0/server/Dockerfile` copies these requirements and installs them.
2.  **Build and Run with Docker Compose:**
    From the root of the `automation-stack` project:
    ```bash
    docker-compose -f compose-mcp.yml up -d --build mem0_mcp qdrant_mcp postgres_logging_mcp openrouter_proxy_mcp
    ```
    (Include any other services `mem0_mcp` depends on or that you want to run).
    To see logs:
    ```bash
    docker-compose -f compose-mcp.yml logs -f mem0_mcp qdrant_mcp
    ```

## 5. Mem0 MCP Server Setup

The self-hosted Mem0 server (from `mem0ai/mem0/server/`) exposes a REST API and is not inherently an MCP (Model-defined Context Protocol) server in the way Cursor IDE or similar tools might expect (e.g., with an SSE endpoint for streaming tools).

The `mem0ai/mem0-mcp` repository provides a separate, specific MCP server implementation designed to work with Cursor. This `mem0-mcp` server appears to use the Mem0 Python SDK to connect to the **Mem0 Cloud Platform** (requiring a `MEM0_API_KEY` from their dashboard) rather than a self-hosted Mem0 instance directly.

**To use the self-hosted Mem0 instance described in this guide, other services (`controller`, `n8n`, `freq-chat`) will interact with its REST API (e.g., `http://mem0_mcp:8000/memory`, `http://mem0_mcp:8000/search`).**

If true MCP server functionality (compatible with Cursor's MCP client expectations) is required for the self-hosted Mem0, one would need to:
1.  Adapt the `mem0-mcp` server code to point to the self-hosted Mem0 REST API instead of the Mem0 Cloud Platform. This would involve changing how the `mem0-mcp` server initializes its Mem0 client.
2.  Or, create a new MCP wrapper around the self-hosted Mem0 REST API.

This guide focuses on setting up the self-hosted Mem0 REST API server. Integrating it as a direct MCP server for tools like Cursor is outside the current scope but could be a future enhancement.

## 6. Integration Verification

### 6.1. Controller & Mem0
The FastAPI controller (`controller_mcp`) should be configured to communicate with the self-hosted Mem0 service.
- **Environment Variable:** Ensure `MEM0_API_URL` in the `controller` service definition within `compose-mcp.yml` points to the Mem0 service: `MEM0_API_URL=http://mem0_mcp:8000`.
- **Testing:**
    - Add a test endpoint to the controller that uses its Mem0 client (initialized with `mem0ai` library pointing to `MEM0_API_URL`) to add a test memory and then search for it.
    - Call this controller endpoint and verify a successful response.
    - Check Mem0 server logs (`docker logs mem0_mcp`) for incoming requests from the controller.

### 6.2. n8n & Mem0
Create an n8n workflow to test adding and searching memories via Mem0's REST API.
- **Workflow Steps:**
    1.  **Manual Trigger.**
    2.  **HTTP Request Node (Add Memory):**
        *   **URL:** `http://mem0_mcp:8000/memory` (assuming n8n is on the `mcp-net` network)
        *   **Method:** `POST`
        *   **Body (JSON):**
            ```json
            {
              "messages": [{"role": "user", "content": "Test memory from n8n"}],
              "user_id": "n8n_test_user",
              "metadata": {"source": "n8n_workflow_test"}
            }
            ```
    3.  **HTTP Request Node (Search Memory):**
        *   **URL:** `http://mem0_mcp:8000/search`
        *   **Method:** `POST`
        *   **Body (JSON):**
            ```json
            {
              "query": "Test memory from n8n",
              "user_id": "n8n_test_user"
            }
            ```
- **Verification:** Execute the workflow. Check the output of the search node for the test memory. Check Mem0 server logs.

### 6.3. `freq-chat` & Mem0
`freq-chat` (a Vercel AI SDK application) needs to be configured to use the self-hosted Mem0 service. Since the `@mem0/vercel-ai-provider` seems tailored for the Mem0 Cloud Platform, `freq-chat` will likely interact with the self-hosted Mem0 server via direct HTTP calls from its backend API routes.

- **Configuration in `freq-chat`:**
    - The backend API routes in `freq-chat` (e.g., in `app/api/.../route.ts` or `pages/api/...`) that handle memory operations will need to make HTTP requests to the self-hosted Mem0 server.
    - The URL for the self-hosted Mem0 server would be `http://mem0_mcp:8000` if `freq-chat`'s backend can resolve services on the `mcp-net` Docker network. If `freq-chat` runs externally (e.g., local dev server not in Docker, or Vercel deployment), it needs to use the publicly accessible URL for Mem0 (e.g., `http://mem0.localhost:${MEM0_HOST_PORT}` or the public URL if exposed through a tunnel/reverse proxy).
    - **Environment Variable for `freq-chat`:** Add an environment variable like `SELF_HOSTED_MEM0_API_URL` to `freq-chat`'s environment (e.g., `.env.development.local` or Vercel environment variables) and use this in the API route logic.
      ```
      # In freq-chat/.env.development.local (example)
      SELF_HOSTED_MEM0_API_URL=http://localhost:7860 # If accessing via host port
      # Or if freq-chat backend is dockerized on mcp-net:
      # SELF_HOSTED_MEM0_API_URL=http://mem0_mcp:8000
      ```
- **Testing:**
    - Implement a simple chat interaction in `freq-chat` that explicitly tries to save a piece of information to memory and then retrieve it in a subsequent message.
    - Verify the interaction in the `freq-chat` UI.
    - Check `freq-chat` backend logs and Mem0 server logs for the API calls.

### 6.4. PostgreSQL Logging Verification
Verify that services (e.g., n8n workflows) can log to the `agent_logs` table in the PostgreSQL database.
- **n8n Workflow:**
    1. Create a simple n8n workflow.
    2. Add a "Postgres" node.
    3. Configure the node with credentials for the `postgres_logging` database.
    4. Set the operation to "Execute Query" and use an `INSERT` statement:
       ```sql
       INSERT INTO agent_logs (agent, workflow, action, status, details)
       VALUES ('n8n_logging_test', 'test_workflow', 'insert_log_entry', 'success', '{"message": "Test log from n8n"}');
       ```
- **Verification:**
    1. Run the n8n workflow.
    2. Connect to the `postgres_logging` database using `psql` (as described in section 3.3.1) or a DB client.
    3. Query the `agent_logs` table: `SELECT * FROM agent_logs WHERE agent = 'n8n_logging_test';`
    4. Verify the test log entry is present.

## 7. Troubleshooting

Common issues and resolutions:

*   **Mem0 Server Fails to Start:**
    *   **Symptom:** `mem0_mcp` container exits or shows errors in logs.
    *   **Check:**
        *   `config.yaml`: Ensure it's valid YAML and paths/configurations are correct.
        *   Dependencies: `requirements.txt` correctly installed in Docker image.
        *   Environment Variables: `OPENAI_API_KEY`, `OPENAI_BASE_URL` are correctly set and passed to the container, especially if `provider: "openai"` is used for LLM/embedder.
        *   Qdrant: Ensure `qdrant_mcp` service is running and accessible from the `mem0_mcp` container (check network, Qdrant logs).
        *   Port conflicts on the host if mapping ports.
*   **Cannot Connect to Mem0 API (e.g., from Controller, n8n):**
    *   **Symptom:** Connection refused, timeout, or 404 errors.
    *   **Check:**
        *   **Service Name/Port:** Ensure clients are using the correct service name (`mem0_mcp`) and internal port (`8000`) if on the same Docker network. If accessing via host, use `localhost` and the mapped host port (e.g., `7860`).
        *   **Traefik:** If using Traefik (`http://mem0.localhost`), ensure Traefik is configured correctly and routing to the `mem0_mcp` service.
        *   **Network:** All relevant services are on the `mcp-net` Docker network.
        *   **Mem0 Server Logs:** Check for any errors when the connection is attempted.
*   **Qdrant Issues:**
    *   **Symptom:** Mem0 logs errors related to Qdrant connection or operations.
    *   **Check:**
        *   Qdrant service (`qdrant_mcp`) is running. Check `docker ps` and `docker logs qdrant_mcp`.
        *   Mem0's `config.yaml` points to the correct Qdrant host (`qdrant_mcp`) and port (`6333`).
        *   Qdrant data volume (`qdrant_data_mcp`) has correct permissions.
*   **OpenRouter Proxy Issues:**
    *   **Symptom:** Mem0 logs errors related to LLM calls (if configured via OpenRouter).
    *   **Check:**
        *   `openrouter_proxy_mcp` service is running and healthy.
        *   `OPENAI_BASE_URL` for `mem0_mcp` service correctly points to the proxy (e.g., `http://openrouter_proxy_mcp:8000/v1`).
        *   `OPENROUTER_API_KEY` is valid and has credits.
        *   The LLM model specified in Mem0's `config.yaml` (with `provider: "openai"`) is available via your OpenRouter proxy setup.
    *   **Embedding Endpoint (404 Not Found):** If you initially configure the `embedder` in `mem0/server/config.yaml` to use `provider: "openai"` (expecting it to go through the `openrouter_proxy_mcp`), you might encounter 404 errors during search operations. This is because the `openrouter_proxy_mcp` (as per `openrouter_proxy/server.js`) might only proxy chat completion endpoints (e.g., `/v1/chat/completions`) and not the embeddings endpoint (`/v1/embeddings`).
        *   **Solution:** Configure Mem0 to use a local embedder like `sentence_transformer` as described in section 4.3. This involves adding `sentence-transformers` to `mem0/server/requirements.txt` and updating the `embedder` section in `mem0/server/config.yaml`.
*   **`.env` File Parsing Issues with Docker Compose (Windows/PowerShell):**
    *   **Symptom:** `docker-compose up` or `docker-compose down` fails with "invalid hostPort" errors, even if the `.env` file appears correct. The error message might include parts of comments from the `.env` file.
    *   **Cause:** Docker Compose on Windows (especially with PowerShell) can be very sensitive to `.env` file formatting, including comments on the same line as variable assignments, trailing spaces, or unusual line endings/encodings.
    *   **Troubleshooting Steps:**
        1. Ensure no comments or extra spaces exist on lines with variable assignments, especially for port mappings (e.g., `MEM0_HOST_PORT=7860` should be exactly that).
        2. Ensure the `.env` file is saved with standard UTF-8 encoding and LF line endings.
        3. Try running `docker-compose -f compose-mcp.yml down` before `up` to clear cached configurations.
        *   **Workaround:** If issues persist, temporarily hardcode the problematic port mappings directly in `compose-mcp.yml` (e.g., change `ports: - "${MEM0_HOST_PORT}:8000"` to `ports: - "7860:8000"`). This was done for `controller_mcp`, `openrouter_proxy_mcp`, `mem0_mcp`, and `postgres_logging_mcp` in this guide's examples.
*   **PostgreSQL Logging Issues:**
    *   **Symptom:** n8n (or other services) cannot write to `agent_logs`.
    *   **Check:**
        *   `postgres_logging_mcp` service is running.
        *   Database, user, password, and port in client configurations match the PostgreSQL setup.
        *   The `agent_logs` table exists and has the correct schema.
        *   Network connectivity between the client service and PostgreSQL.
*   **Data Persistence Issues:**
    *   **Symptom:** Memories or Qdrant data are lost after container restarts.
    *   **Check:**
        *   Docker volumes (`mem0_data_mcp`, `qdrant_data_mcp`, `pgdata_logging_mcp`) are correctly defined in `compose-mcp.yml` and mapped in the service definitions.
        *   Paths inside containers in `config.yaml` (e.g., `history_db_path`, Qdrant storage path if configurable there) align with volume mount points.

For further issues, consult the official Mem0 documentation, Qdrant documentation, and check GitHub issues for `mem0ai/mem0`.
