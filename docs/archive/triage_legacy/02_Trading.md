# 02: Freqtrade Dev Environment Setup

**Status:** New Document - 2025-05-14

This document describes the setup and key components of the `freqtrade` algorithmic trading environment, which runs within a VS Code Dev Container. It is designed to work in conjunction with the `automation-stack`.

## Purpose

The `freqtrade/` stack is dedicated to:

* **Algorithmic Crypto Trading:** Running live trading bots based on user-defined strategies.
* **Strategy Development:** Creating, testing, and refining trading strategies in Python.
* **Backtesting:** Evaluating strategy performance on historical market data.
* **FreqAI Integration:** Utilizing machine learning (via FreqAI) to enhance or develop trading strategies.

## Setup: VS Code Dev Container

The Freqtrade environment is designed to be run as a **VS Code Dev Container**. This provides a consistent, isolated, and reproducible development environment.

* **Launch:** You **must** launch the dev container using the "Focused Workflow". From a WSL terminal, navigate to your `freqtrade` project directory (`cd ~/projects/freqtrade`) and run `code .`. Once VS Code opens, use the "Dev Containers: Reopen in Container" command from the Command Palette.
* **Underlying Technology:** The dev container setup is defined and managed by Docker and Docker Compose.

## Key Configuration Files for Dev Container

1. **`freqtrade/.devcontainer/devcontainer.json`:**
    * This is the primary configuration file for the VS Code Dev Containers extension.
    * It specifies how the development container should be built and run, including:
        * The Docker image to use (often referencing a `docker-compose.yml` file).
        * Extensions to install within VS Code once the container is running (e.g., Python extension).
        * Ports to forward from the container to the host (e.g., Freqtrade UI port `8080`).
        * Volume mounts (e.g., mounting the `freqtrade/user_data/` directory into the container).
        * Post-create commands or lifecycle scripts.

2. **`freqtrade/docker-compose.yml` (or equivalent referenced by `devcontainer.json`):**
    * This Docker Compose file defines the actual Freqtrade service(s) that run within the dev container environment.
    * It specifies:
        * The Freqtrade Docker image (official or custom).
        * Service name (e.g., `freqtrade_devcontainer`).
        * Volume mounts, especially for `user_data` to persist strategies, configurations, data, etc.
        * Port mappings (e.g., `8080:8080` for the Freqtrade UI/API).
        * Network configuration, including potential connection to shared networks like `auto-stack-net` if direct API interaction from the `automation-stack` is required.
        * Environment variables specific to the Freqtrade container.

#### Example `docker-compose.yml` Snippet for Freqtrade Service
```yaml
services:
  freqtrade_devcontainer: # Or 'freqtrade_auto' if running standalone
    image: freqtradeorg/freqtrade:stable
    # restart: unless-stopped # Recommended for production
    volumes:
      # Mount the entire user_data directory for persistence
      - "./user_data:/freqtrade/user_data:rw"
    env_file:
      # Load environment variables from a dedicated .env file
      - ".env"
    ports:
      # Expose Freqtrade UI/API to the host
      - "8080:8080"
    networks:
      # Connect to the shared network for inter-service communication
      - auto-stack-net
    # Example command to run Freqtrade in trade mode
    # command: trade --config /freqtrade/user_data/config.json --strategy SampleStrategy
```

## Key Components & Directory Structure (`freqtrade/user_data/`)

The `freqtrade/user_data/` directory is critical for Freqtrade's operation and persists your custom configurations, strategies, and data. It is typically mounted into the dev container.

* **`user_data/strategies/`**: Contains your custom Python strategy files (`.py`). This is where you define your trading logic.
* **`user_data/freqaimodels/`**: Stores FreqAI model data, configurations, and trained models if you are using the FreqAI component.
* **`user_data/notebooks/`**: A place for Jupyter notebooks used for data analysis, strategy research, or FreqAI model development.
* **`user_data/data/`**: Stores downloaded historical market data used for backtesting and FreqAI training.
* **`user_data/logs/`**: Contains Freqtrade's operational logs.
* **`user_data/backtest_results/`**: Default location where backtest result files (JSON) are saved.
* **`user_data/config.json`**: The main runtime configuration file for Freqtrade. It defines:
  * Exchange settings (API keys, target exchange).
  * Stake currency, amount, and other trading parameters.
  * Pair whitelists/blacklists.
  * Strategy to run.
  * Telegram/Discord bot integration (if used).
  * API server settings (enable/disable, port, username/password for protection).
  * Many other operational parameters.
* **`user_data/docs/`**: A recommended location for your personal Freqtrade-related documentation, strategy notes, research, etc. This is separate from the official Freqtrade documentation.
* **`.env`**: A file at the root of the `freqtrade/` directory to store sensitive credentials and environment-specific settings.

#### Example `.env` for Freqtrade
```env
# For Freqtrade's own API server (must be enabled in config.json)
# These are used by other services (like the Controller) to authenticate
FREQTRADE_API_USERNAME=your_api_user
FREQTRADE_API_PASSWORD=a_very_secure_password

# For Freqtrade to connect to the live exchange
# Replace with your actual exchange API credentials
FREQTRADE_EXCHANGE_API_KEY=YOUR_EXCHANGE_API_KEY
FREQTRADE_EXCHANGE_SECRET=YOUR_EXCHANGE_SECRET_KEY

# General Freqtrade settings
FT_ENV=develop # Can be 'prod' for live trading
TZ=UTC # It is highly recommended to run in UTC timezone
```

## Accessing Freqtrade

Once the dev container is running:

* **Freqtrade UI:** Typically accessible on `http://localhost:8080` (or the host port you've configured if different).
* **Freqtrade API:** Accessible at `http://localhost:8080/api/v1/...` (e.g., `http://localhost:8080/api/v1/ping`). If running on a shared Docker network with the `automation-stack`, services like the controller or `freq-chat` (via its backend) might access it via its service name (e.g., `http://freqtrade_devcontainer:8080/api/v1/...`).
* **VS Code Terminal:** You will have a terminal within VS Code connected directly to the running dev container, allowing you to execute `freqtrade` CLI commands.

Refer to the official Freqtrade documentation for comprehensive details on strategy development, configuration options, and FreqAI usage.

## Setup Verification

### Basic Freqtrade Verification

**1. Container Status Check:**

```bash
# Check if dev container is running
docker ps | grep freqtrade

# Check container logs for startup issues
docker logs freqtrade_devcontainer
```

**2. Service Accessibility:**

```bash
# Test Freqtrade UI accessibility
curl -f http://localhost:8080 || echo "UI not accessible"

# Test Freqtrade API endpoint
curl http://localhost:8080/api/v1/ping
# Expected response: {"status": "pong"}
```

**3. CLI Functionality:**

```bash
# From within the dev container terminal (VS Code)
freqtrade --version
freqtrade list-strategies
freqtrade test-pairlist --config user_data/config.json
```

### Configuration Verification

**4. User Data Mount:**

```bash
# Verify user_data directory is mounted correctly
ls -la /freqtrade/user_data/
# Should show: strategies/, data/, logs/, config.json, etc.
```

**5. Configuration Validation:**

```bash
# Test configuration file validity
freqtrade show-config --config user_data/config.json
```

### Integration Verification

**6. Cross-Stack Communication:**

```bash
# Test from automation-stack containers
curl http://freqtrade_devcontainer:8080/api/v1/ping

# Test from host (if on shared network)
docker exec controller_auto curl http://freqtrade_devcontainer:8080/api/v1/ping
```

**7. Network Connectivity:**

```bash
# Verify shared network connection
docker network inspect auto-stack-net | grep freqtrade
```

### Trading Setup Verification Checklist

<details>
<summary>Click to expand Trading Environment Verification Checklist</summary>

**Development Environment:**
* [x] **T1:** VS Code Dev Container starts successfully
* [ ] **T2:** Freqtrade UI accessible at `http://localhost:8080`
* [ ] **T3:** Freqtrade API responds to ping: `http://localhost:8080/api/v1/ping`
* [ ] **T4:** VS Code terminal connected to dev container
* [ ] **T5:** Python extensions and dev tools loaded in VS Code

**Configuration & Data:**
* [ ] **T6:** `user_data/` directory mounted and accessible
* [ ] **T7:** `config.json` file present and valid
* [ ] **T8:** Strategy files present in `user_data/strategies/`
* [ ] **T9:** Freqtrade CLI commands functional (`freqtrade --version`)
* [ ] **T10:** Configuration validation passes (`freqtrade show-config`)

**Integration & Networking:**
* [ ] **T11:** Container connected to `auto-stack-net` network
* [ ] **T12:** Cross-stack API communication functional
* [ ] **T13:** Port forwarding operational (8080)
* [ ] **T14:** No firewall blocking container communications
* [ ] **T15:** Authentication configured for automation-stack access

**Trading Functionality:**
* [ ] **T16:** Strategy listing works (`freqtrade list-strategies`)
* [ ] **T17:** Pair list testing works (`freqtrade test-pairlist`)
* [ ] **T18:** Data download capability functional
* [ ] **T19:** Backtesting capability operational
* [ ] **T20:** FreqAI integration functional (if used)

**Automation Integration:**
* [ ] **T21:** Controller can reach Freqtrade API endpoints
* [ ] **T22:** n8n workflows can trigger Freqtrade operations
* [ ] **T23:** Unified logging operational (if configured)
* [ ] **T24:** Multi-agent orchestration connectivity verified
* [ ] **T25:** Mem0 integration accessible (if configured)

</details>

### Common Issues and Solutions

**Container Won't Start:**
* Check Docker Desktop is running and resources are available
* Verify VS Code Dev Containers extension is installed
* Try rebuilding the container: "Dev Containers: Rebuild Container"

**UI/API Not Accessible:**
* Verify port 8080 is not in use by another service
* Check `devcontainer.json` port forwarding configuration
* Ensure firewall isn't blocking port 8080

**Configuration Issues:**
* Validate JSON syntax in `config.json`
* Check API keys are properly formatted
* Ensure exchange settings are correct

**Cross-Stack Communication Problems:**
* Verify `auto-stack-net` network connectivity
* Check automation-stack services can reach Freqtrade
* Test authentication credentials match between services

## Integration with Automation Stack (Logging & Orchestration)

* **Unified Logging:** Freqtrade-related agents (e.g., FreqtradeManager_Agent, sub-agents) log to a unified PostgreSQL table with an `agent` field for separation. See `docs/n8n/prompt_library/UnifiedLogging.md` for schema and best practices. Data or summaries from these logs might be surfaced through `freq-chat`.
* **Multi-Agent Orchestration:** Freqtrade automation is managed via the CentralBrain_Agent and manager/sub-agent workflows. These workflows might be triggered or monitored via interactions originating in `freq-chat`. See `docs/n8n/prompt_library/CentralBrain.md` for org chart and workflow prompts.
* **Mem0 Integration (Potential):** While Mem0 is primarily integrated with the `automation-stack` services (Controller, n8n, freq-chat), there is potential for future integration with Freqtrade agents or strategies for purposes like:
  * Storing historical trading decisions or rationales.
  * Retrieving global market knowledge during strategy execution.
  * Maintaining state for complex multi-step trading automation workflows orchestrated by n8n or the Controller.
  * *Current Status:* Direct Freqtrade <-> Mem0 integration is not yet implemented. Interaction is typically mediated via the Controller or n8n. Refer to `docs/guides/mem0_server_guide.md` for self-hosted Mem0 setup and usage within the automation stack.

## Troubleshooting: Full Clean Rebuild & Integration for Freqtrade Dev Container

If you encounter persistent build/startup issues with the Freqtrade dev container, follow this step-by-step process to ensure a completely fresh environment and robust integration with the automation-stack:

### 1. **Stop and Remove All Freqtrade Containers**

```bash
# List all containers (running and stopped)
docker ps -a | grep freqtrade
# Stop and remove all Freqtrade-related containers
for c in $(docker ps -a --filter "ancestor=ghcr.io/freqtrade/freqtrade-devcontainer:latest" --format "{{.ID}}"); do docker rm -f $c; done
```

### 2. **Remove All Freqtrade Images**

```bash
docker images | grep freqtrade
# Remove all Freqtrade images
docker rmi -f $(docker images --filter=reference='*freqtrade*' -q)
```

### 3. **Remove All Freqtrade Volumes**

```bash
# List and remove all volumes related to freqtrade
docker volume ls | grep freqtrade
for v in $(docker volume ls -q | grep freqtrade); do docker volume rm $v; done
```

### 4. **Prune All Unused Docker Data (Optional, CAUTION)**

```bash
docker system prune -af --volumes
```

### 5. **Delete Workspace Caches/Artifacts**

- Remove any `.pytest_cache`, `__pycache__`, `.mypy_cache`, or other build/test artifacts in the workspace:

```bash
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type d -name ".pytest_cache" -exec rm -rf {} +
find . -type d -name ".mypy_cache" -exec rm -rf {} +
```

### 6. **Verify Clean State**

- Ensure `docker ps -a`, `docker images`, and `docker volume ls` show no Freqtrade-related artifacts.

### 7. **Rebuild and Start Freqtrade Dev Container**

```bash
docker compose build
docker compose up -d
```

### 8. **Integration Checks with automation-stack**

- Confirm the following for cross-stack integration:
  * Freqtrade API is accessible at `http://localhost:8080/api/v1/ping` (from host)
  * Freqtrade API is accessible at `http://freqtrade_devcontainer:8080/api/v1/ping` (from other containers on the shared Docker network, e.g., automation-stack)
  * Freqtrade is connected to the correct Docker network (e.g., `auto-stack-net`) as defined in `docker-compose.yml`
  * All required ports are exposed and not blocked by firewalls
  * `user_data` is correctly mounted and persists between rebuilds
  * Authentication (JWT, username/password) matches what automation-stack expects (see `user_data/config.json`)

### 9. **Test Integration Endpoints**

- Use `curl` or `docker exec` to test endpoints from both host and within containers.
* If using the FastAPI Controller, test its ability to reach Freqtrade API endpoints as described in the integration guide.

### 10. **Log and Document Issues**

- Record any errors, logs, or edge cases encountered during this process.
* Update the integration checklist and troubleshooting docs as needed.

---

**References:**
* `04_Cross_Stack_Integration_Guide.md`
* `AutomationChecklist.md`
* `docker-compose.yml` (network/volume config)
* `user_data/config.json` (API/auth settings)
* `controller/controller.py` (integration logic)
* `docs/guides/mem0_server_guide.md` (Self-hosted Mem0 and PostgreSQL logging setup)
