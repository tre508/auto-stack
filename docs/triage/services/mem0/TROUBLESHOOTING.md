# Mem0 Troubleshooting Guide

This guide helps diagnose and resolve common issues encountered while setting up and running the Mem0 service and related components.

## Table of Contents

1.  [Project Configuration & Code Issues](#project-configuration--code-issues)
    *   [Dependencies](#dependencies)
    *   [Mem0 Server (`mem0/server`)](#mem0-server-mem0server)
    *   [Vector Store (ChromaDB/Qdrant)](#vector-store-chromadbqdrant)
    *   [Embedding Models](#embedding-models)
    *   [Database (History & Graph)](#database-history--graph)
    *   [Linter Issues & Code Quirks](#linter-issues--code-quirks)
    *   [`embedchain` Submodule Issues](#embedchain-submodule-issues)
2.  [Logging & Debugging](#logging--debugging)
3.  [User-Specific Actions & Environment Setup](#user-specific-actions--environment-setup)
    *   [Local Development Environment](#local-development-environment)
    *   [API Keys & External Services](#api-keys--external-services)
    *   [Docker & Networking](#docker--networking)

---

## 1. Project Configuration & Code Issues

### Dependencies
-   Key Python packages are listed in `mem0/pyproject.toml`.
-   For the `mem0/server` (if run via Docker using `requirements.txt`): `mem0/server/requirements.txt`.
-   **Issue**: `ModuleNotFoundError` for packages like `qdrant-client` or `sentence_transformers`.
-   **Solution (AI Actionable)**:
    1.  **For `mem0` library development (using Poetry):**
        Ensure `qdrant-client` and `sentence-transformers` are in `mem0/pyproject.toml` and install:
        ```toml
        # In mem0/pyproject.toml
        [tool.poetry.dependencies]
        # ... other dependencies
        qdrant-client = ">=1.7.0" # Or compatible version
        sentence-transformers = ">=2.7.0" 
        ```
        Then, the user should run `poetry lock && poetry install`.
    2.  **For the `mem0/server` Docker image:**
        Ensure `qdrant-client` and `sentence-transformers` are in `mem0/server/requirements.txt`:
        ```
        qdrant-client>=1.7.0
        sentence-transformers>=2.7.0
        ```
        The Docker image will then need to be rebuilt by the user.

### Mem0 Server (`mem0/server`)

#### Server Configuration (`config.yaml`)
-   **Location**: Path specified by `MEM0_CONFIG_PATH` (e.g., `mem0/server/config.yaml`).
-   **Content**: Defines providers and configurations for `vector_store`, `graph_store`, `llm`, `embedder`, and `history_db_path`.
-   **AI Actionable**: Configuration settings for Qdrant, Hugging Face, OpenRouter, and SQLite persistence can be updated in this file.

#### Common Server Issues
-   **Symptom**: "Mem0 Memory instance not available" or "Mem0 Memory class not available".
    -   **Cause**:
        1.  The `mem0` library failed to import `Memory` class.
        2.  `Memory.from_config(cfg)` failed during initialization due to incorrect `config.yaml` or missing dependencies for configured providers.
    -   **Solution**:
        1.  **AI Actionable**: Ensure the `try-except` block in `mem0/server/main.py` for `Memory` import is correct.
        2.  **User Action**: Verify `config.yaml` is correct and all specified providers have valid configurations. Check server logs for detailed errors.
-   **Symptom**: API requests fail (4xx or 5xx errors).
    -   **Cause**: Issues with request payload, underlying service (LLM, DB), or internal server logic.
    -   **Solution (User Action)**: Check server logs. FastAPI provides detailed validation errors.

### Vector Store (ChromaDB/Qdrant)
The current stack uses Qdrant.

#### Configuration (`config.yaml` for Qdrant)
-   **AI Actionable**: Update `mem0/server/config.yaml` for Qdrant:
    ```yaml
    vector_store:
      provider: "qdrant"
      config:
        host: "qdrant_auto" # Service name in docker-compose.yml
        port: 6333
        collection_name: "memories_autostack" # Or your preferred collection name
    ```

#### Common Qdrant Issues
-   **Symptom**: Errors related to "collection not found" or connection issues.
    -   **Cause**: Qdrant service (`qdrant_auto`) not running, network issues, configuration mismatch.
    -   **Solution (User Action)**: Verify `host` and `port` in `config.yaml` are correct. Ensure `qdrant_auto` is running and accessible from `mem0_auto` on the Docker network. Check server logs.
-   **Symptom**: Linter errors in `mem0/mem0/vector_stores/qdrant.py` regarding `qdrant_client` import.
    -   **Solution (User Action)**: Install `qdrant-client` in the local development environment where the linter runs.

### Embedding Models

#### Hugging Face Embedders (Local Sentence Transformers)
-   **Configuration (`config.yaml` - AI Actionable):**
    ```yaml
    embedder:
      provider: "sentence_transformer" # Corrected from "huggingface" for local models
      config:
        model: "all-MiniLM-L6-v2" # Default or your chosen model
        # model_kwargs: {"device": "cuda"} # Optional
    ```
-   **Dependency**: `sentence-transformers`. (Handled in [Dependencies](#dependencies) section).
-   **Common Issues**:
    -   **Symptom**: `ModuleNotFoundError: No module named 'sentence_transformers'`.
        -   **Solution**: Install the dependency (see [Dependencies](#dependencies)).

#### OpenRouter for Embeddings/LLMs (via OpenAI provider type)
-   **Configuration (`config.yaml` - AI Actionable):**
    -   **For LLM:**
        ```yaml
        llm:
          provider: "openai" # Uses OpenRouter due to env vars set by user
          config:
            model: "openai/gpt-3.5-turbo" # User choice of OpenRouter model
            # api_key and base_url are picked from environment variables (user-set)
        ```
    -   **For Embeddings (via OpenAI provider to OpenRouter, if proxy supports it):**
        ```yaml
        embedder:
          provider: "openai" # Uses OpenRouter due to env vars set by user
          config:
            model: "text-embedding-ada-002" # User choice of OpenRouter embedding model
            # api_key and base_url are picked from environment variables (user-set)
        ```
    *Note: For embeddings, using local `sentence_transformer` is often more reliable if the proxy doesn't support embedding endpoints well.*

### Database (History & Graph)

#### SQLite (History)
-   **Default path**: `/app/history/history.db` (in container, if not overridden).
-   **Persistence**: `docker-compose.yml` maps `mem0_data_auto:/data`.
-   **Recommendation (AI Actionable config change)**: Update `config.yaml` or use environment variable `HISTORY_DB_PATH` to point within `/data`:
    ```yaml
    # In mem0/server/config.yaml
    history_db_path: "/data/history/history.db"
    ```

### Linter Issues & Code Quirks
(Refer to original content for these, as they are less about env rationalization)

### `embedchain` Submodule Issues
(Refer to original content, this is about vendored code structure)

---

## 2. Logging & Debugging
-   **Mem0 Server Logs (User Action)**: `docker logs mem0_auto`.
-   **FastAPI Debug Mode (User Action)**: Check `uvicorn` startup in `Dockerfile`.
-   **Poetry Environment (User Action)**: Use `poetry shell` for library debugging.
-   **Step-through Debugging (User Action)**: Use `pdb` or IDE debugger.

---

## 3. User-Specific Actions & Environment Setup

This section consolidates actions that require your direct intervention or local environment configuration.

### Local Development Environment
(Refer to original content)

### API Keys & External Services
-   **Environment Variables (`.env` file)**:
    -   **Location**: Root of `auto-stack` (for `docker-compose.yml`) or `mem0/server` (if running server standalone, though less common with Docker). Refer to `mem0/server/.env.example` if it exists, but primary config is via root `.env` and `mem0/.env`.
    -   **Action**: Ensure your root `.env` and service-specific `mem0/.env` files are populated with necessary API keys (like `HF_TOKEN`, `OPENROUTER_API_KEY`) and service configurations.
    -   **`OPENROUTER_API_KEY`**: **Crucial.** In root `.env`.
-   **OpenRouter Setup**:
    -   **Action**: `mem0_auto` service in `docker-compose.yml` should use `HF_TOKEN` (as `OPENAI_API_KEY`) and `OPENAI_BASE_URL` (pointing to `openrouter_proxy_auto` or `controller_auto` proxy) from the root `.env` or its own `mem0/.env`.
-   **Hugging Face API Key (HF_TOKEN)**:
    -   **Action**: Ensure `HF_TOKEN` is in the root `.env`. This is used by `mem0_auto` as its `OPENAI_API_KEY` when `OPENAI_BASE_URL` points to an embedder proxy.

### Docker & Networking
-   **Running Mem0 Server with Docker Compose**:
    -   **Command**: `docker-compose up -d --build mem0_auto`. Rebuild if `Dockerfile` or `requirements.txt` change.
    -   **Port Conflicts**: If host port (e.g., `${MEM0_EXTERNAL_PORT:-8000}`) is in use, change `MEM0_EXTERNAL_PORT` in your root `.env` file.
-   **Docker Volume Permissions**:
    -   **Issue**: Qdrant or SQLite errors related to read/write access.
    -   **Action**: Ensure the Docker daemon has correct permissions to manage volumes, and the paths inside the container (e.g., `/data`) are writable by the server process.
-   **Internet Connectivity for Docker**:
    -   **Issue**: Model download failures during Docker build or runtime.
    -   **Action**: Ensure your Docker environment has internet access.
-   **GPU Access for Docker (Optional)**:
    -   **Issue**: CUDA/GPU errors if Hugging Face models are configured for GPU.
    -   **Action**: Ensure Docker is configured for GPU access and the `mem0_auto` service definition in `docker-compose.yml` includes GPU resources, if intended.

---

This guide should help in resolving many common issues. If problems persist, refer to specific library documentation (Qdrant, SentenceTransformers, OpenRouter) and check for updates or known issues in the Mem0 project itself.
