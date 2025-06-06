# Mem0 Troubleshooting Guide

This guide helps diagnose and resolve common issues encountered while setting up and running the Mem0 service and related components.

## Table of Contents

1.  [Project Configuration & Code Issues](#project-configuration--code-issues)
    *   [Dependencies](#dependencies)
    *   [Mem0 Server (`mem0/server`)](#mem0-server-mem0server)
    *   [Vector Store (ChromaDB)](#vector-store-chromadb)
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
-   **Issue**: `ModuleNotFoundError` for packages like `chromadb` or `sentence_transformers`.
-   **Solution (AI Actionable)**:
    1.  **For `mem0` library development (using Poetry):**
        Ensure `chromadb` and `sentence-transformers` are in `mem0/pyproject.toml` and install:
        ```toml
        # In mem0/pyproject.toml
        [tool.poetry.dependencies]
        # ... other dependencies
        chromadb = ">=0.4.24" # Ensure version compatibility
        sentence-transformers = ">=2.7.0" # Ensure version compatibility
        ```
        Then, the user should run `poetry lock && poetry install`.
    2.  **For the `mem0/server` Docker image:**
        Ensure `chromadb` and `sentence-transformers` are in `mem0/server/requirements.txt`:
        ```
        chromadb>=0.4.24
        sentence-transformers>=2.7.0
        ```
        The Docker image will then need to be rebuilt by the user.

### Mem0 Server (`mem0/server`)

#### Server Configuration (`config.yaml`)
-   **Location**: Path specified by `MEM0_CONFIG_PATH` (e.g., `mem0/server/config.yaml`).
-   **Content**: Defines providers and configurations for `vector_store`, `graph_store`, `llm`, `embedder`, and `history_db_path`.
-   **AI Actionable**: Configuration settings for ChromaDB, Hugging Face, OpenRouter, and SQLite persistence can be updated in this file.

#### Common Server Issues
-   **Symptom**: "Mem0 Memory instance not available" or "Mem0 Memory class not available".
    -   **Cause**:
        1.  The `mem0` library failed to import `Memory` class (see [mem0/server/main.py Memory Import](#mem0servermainpy-memory-import)).
        2.  `Memory.from_config(cfg)` failed during initialization due to incorrect `config.yaml` or missing dependencies for configured providers.
    -   **Solution**:
        1.  **AI Actionable**: Ensure the `try-except` block in `mem0/server/main.py` for `Memory` import is correct.
        2.  **User Action**: Verify `config.yaml` is correct and all specified providers have valid configurations. Check server logs for detailed errors.
-   **Symptom**: API requests fail (4xx or 5xx errors).
    -   **Cause**: Issues with request payload, underlying service (LLM, DB), or internal server logic.
    -   **Solution (User Action)**: Check server logs. FastAPI provides detailed validation errors.

### Vector Store (ChromaDB)
You intend to use ChromaDB as the vector store.

#### Dependency
-   **Package**: `chromadb`. (Handled in [Dependencies](#dependencies) section).

#### Configuration (`config.yaml`)
-   **AI Actionable**: Update `mem0/server/config.yaml` for ChromaDB:
    ```yaml
    vector_store:
      provider: "chroma"
      config:
        path: "/data/chroma_db" # Persists within the mem0_data Docker volume
        collection_name: "memories_chroma"
        # host: "your_chroma_host" # For external ChromaDB
        # port: your_chroma_port
    ```

#### Common ChromaDB Issues
-   **Symptom**: Errors related to "collection not found" or connection issues.
    -   **Cause**: ChromaDB path not writable/accessible, configuration mismatch, version incompatibilities.
    -   **Solution (User Action)**: Verify `path` in `config.yaml` is correct and Docker volume permissions are set. Ensure `chromadb` version compatibility. Check server logs.
-   **Symptom**: Linter errors in `mem0/mem0/vector_stores/chroma.py` regarding `chromadb` import.
    -   **Solution (User Action)**: Install `chromadb` in the local development environment where the linter runs.

### Embedding Models

#### Hugging Face Embedders
-   **Configuration (`config.yaml` - AI Actionable):**
    ```yaml
    embedder:
      provider: "huggingface"
      config:
        model: "sentence-transformers/all-MiniLM-L6-v2" # Default or your chosen model
        # model_kwargs: {"device": "cuda"} # Optional
        # huggingface_base_url: "IF_USING_HF_INFERENCE_ENDPOINTS" # Optional
        # api_key: "YOUR_HF_API_KEY" # Optional
    ```
-   **Dependency**: `sentence-transformers`. (Handled in [Dependencies](#dependencies) section).
-   **Code (`mem0/mem0/embeddings/huggingface.py`):**
    -   Ensure `model_kwargs` in `BaseEmbedderConfig` defaults to `{}`. (Checked, it does).
-   **Common Issues**:
    -   **Symptom**: `ModuleNotFoundError: No module named 'sentence_transformers'`.
        -   **Solution**: Install the dependency (see [Dependencies](#dependencies)).

#### OpenRouter for Embeddings/LLMs
-   **Configuration (`config.yaml` - AI Actionable):**
    -   **For LLM:**
        ```yaml
        llm:
          provider: "openai" # Uses OpenRouter due to env vars set by user
          config:
            model: "openai/gpt-3.5-turbo" # User choice of OpenRouter model
            # api_key and base_url are picked from environment variables (user-set)
        ```
    -   **For Embeddings (via OpenAI provider to OpenRouter):**
        ```yaml
        embedder:
          provider: "openai" # Uses OpenRouter due to env vars set by user
          config:
            model: "text-embedding-ada-002" # User choice of OpenRouter embedding model
            # api_key and base_url are picked from environment variables (user-set)
        ```

### Database (History & Graph)

#### SQLite (History)
-   **Default path**: `/app/history/history.db` (in container).
-   **Persistence**: `compose-mcp.yml` maps `mem0_data:/data`.
-   **Recommendation (AI Actionable config change)**: Update `config.yaml` or use environment variable `HISTORY_DB_PATH` to point within `/data`:
    ```yaml
    # In mem0/server/config.yaml
    history_db_path: "/data/history/history.db"
    ```

### Linter Issues & Code Quirks

#### `mem0/server/main.py` Memory Import
-   **Issue**: `try-except` block for `Memory` import might be malformed.
-   **Correct Structure (AI Actionable Code Fix)**:
    ```python
    # In mem0/server/main.py
    try:
        from mem0 import Memory
    except ImportError as e:
        print(f"[ERROR] Could not import Memory from mem0: {e}", file=sys.stderr)
        Memory = None
    ```

#### `mem0.Memory.get_all()` Linter False Positive
-   **Status**: False positive. Can be ignored by the user.

#### HuggingFaceEmbedding `model_kwargs` False Positive
-   **Status**: Likely linter limitation. Can be ignored by the user if base class initializes correctly.

#### `httpx.Client` `proxies` parameter False Positive
-   **Status**: Likely linter stub issue. Can be ignored by the user if `httpx` version supports it.

#### Vendored `embedchain` Linter/Import Issues (2K+ Problems)
- **Symptom:** Thousands of linter errors in VS Code (or other IDEs) in `mem0/embedchain/embedchain`, mostly unresolved imports like `Import "embedchain.xyz" could not be resolved`.
- **Root Cause:** The `embedchain` directory is vendored inside `mem0/embedchain/`, but import statements use `from embedchain.xyz` (as if `embedchain` is a top-level package). This confuses linters and Python import resolution unless the workspace or `PYTHONPATH` is set up to treat `mem0/embedchain` as a root.
- **Troubleshooting Steps:**
    1. **For Linters/IDE:**
        - In VS Code, add the following to your `.vscode/settings.json`:
          ```json
          {
            "python.analysis.extraPaths": [
              "${workspaceFolder}/mem0/embedchain"
            ]
          }
          ```
        - This tells the linter to treat `mem0/embedchain` as a root, resolving `embedchain.xyz` imports.
    2. **For Runtime:**
        - If running scripts directly, set `PYTHONPATH`:
          ```sh
          export PYTHONPATH=$PYTHONPATH:$(pwd)/mem0/embedchain
          # or in PowerShell
          $env:PYTHONPATH = "$env:PYTHONPATH;$(Get-Location)\mem0\embedchain"
          ```
        - Or, adjust imports to use relative paths (not recommended unless refactoring the vendored codebase).
    3. **Suppressing Linter Noise:**
        - If you do not actively develop in `embedchain`, you may ignore or suppress these warnings. Consider adding `mem0/embedchain/embedchain` to your linter's exclude paths.
    4. **Why Not Fix Imports?**
        - Changing all imports to `from mem0.embedchain.embedchain.xyz` would break compatibility with upstream or external usage. The current structure is a compromise for vendoring.
- **Summary:** These linter errors are a known side effect of vendoring a package with top-level imports. Adjust your IDE/linter settings or suppress as needed. No action is needed if runtime works and you do not develop in `embedchain` directly.

### `embedchain` Submodule Issues
-   The `mem0/embedchain/` directory appears to be a vendored version. `mem0/pyproject.toml` excludes `embedchain/`.
-   **Symptom**: `Import "embedchain.xyz" could not be resolved` (linter). `ModuleNotFoundError` (runtime).
-   **Cause**: Linter path issues; runtime `PYTHONPATH` for the server.
-   **Troubleshooting (User-driven based on advice here)**:
    1.  **Runtime `PYTHONPATH`**: User needs to ensure `mem0/server/Dockerfile` correctly places `mem0/embedchain` to be importable as `embedchain`. Or adjust imports if it's `mem0.embedchain`.
    2.  **Import Style**: User to verify/adjust based on how `embedchain` is intended to be structured (top-level or sub-package `mem0.embedchain`).
    3.  **Linter Configuration (User Action)**: User might need to adjust local IDE/linter path settings.

---

## 2. Logging & Debugging
-   **Mem0 Server Logs (User Action)**: `docker logs mem0`.
-   **FastAPI Debug Mode (User Action)**: Check `uvicorn` startup in `Dockerfile`.
-   **Poetry Environment (User Action)**: Use `poetry shell` for library debugging.
-   **Step-through Debugging (User Action)**: Use `pdb` or IDE debugger.

---

## 3. User-Specific Actions & Environment Setup

This section consolidates actions that require your direct intervention or local environment configuration.

### Local Development Environment
-   **Python Version**:
    -   **Requirement**: Python >=3.9, <4.0.
    -   **Action**: Install a compatible Python version (e.g., using `pyenv` or from [python.org](https://python.org)). Verify with `python --version`.
-   **Poetry Installation & Usage**:
    -   **Requirement**: Poetry for dependency management.
    -   **Action**: Install Poetry from [Poetry's official site](https://python-poetry.org/docs/#installation). Verify with `poetry --version`. Ensure Poetry's `bin` directory is in your system's PATH.
    -   **Action**: Run `poetry install` in the `mem0` directory to install dependencies.
    -   **Action**: Activate virtual environment: `poetry shell`.
-   **Build Tools**:
    -   **Issue**: Errors during `poetry install` related to missing build tools.
    -   **Action**: Ensure you have necessary build tools (e.g., C compilers for some packages).
-   **Linter Configuration**:
    -   **Issue**: Linter errors for valid code or unresolved imports (e.g., for `embedchain` or missing dev dependencies like `chromadb`).
    -   **Action**: Configure your linter's path settings (e.g., in VS Code's `settings.json`). Install dev dependencies in your local environment (`poetry add package --group dev` or `pip install package`).

### API Keys & External Services
-   **Environment Variables (`.env` file)**:
    -   **Location**: Root of `automation-stack` (for `compose-mcp.yml`) or `mem0/server` (if running server standalone). Refer to `mem0/server/.env.example`.
    -   **Action**: Create and populate your `.env` file with necessary API keys and service configurations.
    -   **`OPENROUTER_API_KEY`**: **Crucial.** Obtain your API key from [OpenRouter.ai](https://openrouter.ai).
    -   **Database Credentials**: For PostgreSQL, Neo4j, or Memgraph if used.
-   **OpenRouter Setup**:
    -   **Action**: Set `OPENAI_API_KEY=${OPENROUTER_API_KEY}` and `OPENAI_BASE_URL=https://openrouter.ai/api/v1` in the environment for the `mem0` service (pre-configured in `compose-mcp.yml` to use `OPENROUTER_API_KEY` from `.env`).
-   **Hugging Face API Key (Optional)**:
    -   **Action**: If using private Hugging Face models or paid inference APIs, add `api_key: "YOUR_HF_API_KEY"` to the `embedder` config in `config.yaml` and/or set relevant environment variables.
-   **External Database Services (Neo4j/Memgraph)**:
    -   **Action**: If using Neo4j or Memgraph, ensure the database service is running, accessible, and connection details (URI, user, password) in your environment/`config.yaml` are correct.

### Docker & Networking
-   **Running Mem0 Server with Docker Compose**:
    -   **Command**: `docker-compose -f compose-mcp.yml up -d --build mem0`. Rebuild if `Dockerfile` or `requirements.txt` change.
    -   **Port Conflicts**: If host port (e.g., `7860`) is in use, change the mapping in `compose-mcp.yml` (e.g., `"7861:8000"`).
-   **Docker Volume Permissions**:
    -   **Issue**: ChromaDB or SQLite errors related to read/write access.
    -   **Action**: Ensure the Docker daemon has correct permissions to manage volumes, and the paths inside the container (e.g., `/data`) are writable by the server process.
-   **Internet Connectivity for Docker**:
    -   **Issue**: Model download failures during Docker build or runtime.
    -   **Action**: Ensure your Docker environment has internet access.
-   **GPU Access for Docker (Optional)**:
    -   **Issue**: CUDA/GPU errors if Hugging Face models are configured for GPU.
    -   **Action**: Ensure Docker is configured for GPU access and the `mem0` service definition in `compose-mcp.yml` includes GPU resources, if intended.

---

This guide should help in resolving many common issues. If problems persist, refer to specific library documentation (ChromaDB, SentenceTransformers, OpenRouter) and check for updates or known issues in the Mem0 project itself. 