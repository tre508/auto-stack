# 06: Developer Tools and Practices

**Status:** Consolidated $(date +%Y-%m-%d)

**Purpose:** Outline recommended tools, VS Code extensions, CLI commands, and best practices for developing and maintaining the auto-stack.

## 1. Core Development Environment

### 1.1. Docker and Docker Compose

- **Role:** Essential for running the entire auto-stack as a collection of containerized services.
- **Syntax:** The project uses Docker Compose V2+ syntax (e.g., `docker compose up`).
- **Key Commands (run from WSL terminal):**
  - `docker compose up -d`: Start all services in detached mode.
  - `docker compose down`: Stop and remove containers and networks.
  - `docker compose ps`: List running services.
  - `docker compose logs <service_name>`: View logs for a specific service.
  - `docker compose build <service_name>`: Build or rebuild a service image.
  - `docker compose exec <service_name> <command>`: Execute a command inside a running container.
- **WSL2 Best Practices:**
  - **Mandatory Environment:** For Windows users, development **must** be done within WSL2 for compatibility.
  - **File System:** For optimal performance, project files should reside **within the WSL2 filesystem** (e.g., `/home/<user>/projects/auto-stack`).

### 1.2. VS Code (Visual Studio Code)

- **Role:** Primary code editor and development IDE.
- **WSL Integration:** Use the **Remote - WSL** extension to connect VS Code to your WSL environment.
- **Recommended Workflow ("Focused Workflow"):**
  - **The mandatory workflow is to open each service in its own dedicated VS Code window.** This ensures that extensions and settings are loaded correctly without conflict.
  - **How-To:**
    1. Open your WSL terminal.
    2. Navigate to the service directory (e.g., `cd ~/projects/auto-stack/freq-chat`).
    3. Run `code .` to open that folder in a new VS Code window.
- **Essential Extensions:**
  - **Remote - WSL (Microsoft):** The foundation for this workflow.
  - **Docker (Microsoft):** Manage containers, images, and view logs directly in the editor.
  - **Python (Microsoft):** For Controller, Mem0, and Freqtrade development.
  - **Ruff (Astral Software):** For high-performance Python linting.
  - **ESLint & Prettier (Microsoft & Prettier):** For `freq-chat` (Next.js/TypeScript) code quality.
  - **Dev Containers (Microsoft):** Essential for working within the Freqtrade dev container.
  - **Markdown All in One (Yu Zhang):** For editing documentation.
  - **REST Client (Huachao Mao) or Thunder Client (Ranga Vadhineni):** For testing APIs directly within VS Code.

### 1.3. Git

- **Role:** Version control for all code and documentation.
- **Practices:**
  - Use feature branches for new development.
  - Write clear, concise, conventional commit messages (e.g., `feat:`, `fix:`, `docs:`).
  - Regularly pull changes from the main repository.

## 2. Service-Specific Tools & Practices

### 2.1. n8n Workflow Development

- **n8n Editor:** The primary web UI (`http://n8n.localhost`) for creating workflows.
- **n8nChat Browser Extension:** AI-powered assistant for generating and debugging workflows using natural language. It connects to your local n8n instance and uses your LLM keys (via the OpenRouter Proxy). See `docs/triage/services/n8n/n8nChat.md`.
- **CLI for n8n (via `docker compose exec`):**
  - Use `n8n export:workflow` and `n8n import:workflow` for programmatic management.

### 2.2. Controller & Mem0 (FastAPI) Development

- **Python Environment (in WSL):** For local testing, create a Python virtual environment in your WSL terminal (`python3 -m venv .venv`, `source .venv/bin/activate`, `pip install -r requirements.txt`).
- **Poetry:** The `mem0` library uses Poetry for dependency management. Use `poetry install` and `poetry shell` within the `mem0/` directory in WSL.
- **API Testing:** Use the recommended VS Code REST extensions, Postman, or `curl`/`httpie` from the WSL terminal.
- **Linters:** Ruff is recommended for its speed and comprehensive checks.

### 2.3. `freq-chat` (Next.js) Development

- **Node.js & pnpm (in WSL):** Node.js **must** be installed and managed within your WSL environment (use `nvm`).
- **Package Manager:** `pnpm` is the required package manager. Run all commands (`pnpm install`, `pnpm dev`) from the WSL terminal.
- **Vercel CLI:** For managing deployments and environment variables (`vercel env pull`).
- **Browser Developer Tools:** Essential for debugging the frontend and its API interactions.

### 2.4. Database Management

- **PostgreSQL (`postgres_logging_auto`):**
  - **Tools:** Use pgAdmin, DBeaver, or TablePlus for a GUI.
  - **CLI Access:** `docker compose exec postgres_logging_auto psql -U autostack_logger -d autostack_logs`
- **Qdrant (`qdrant_auto`):**
  - **Web UI:** Access at `http://localhost:6333` to inspect collections and points, crucial for debugging Mem0.

## 3. General CLI Utilities (in WSL)

- **`curl` or `httpie`:** For quick API testing from the WSL command line.
- **`jq`:** A command-line JSON processor for parsing API responses (`| jq .`).
- **`markdownlint-cli`:** Use `npm install -g markdownlint-cli` and `markdownlint **/*.md` to check documentation for style consistency.

## 4. Debugging Practices

- **Start with Logs:** Always check service logs first: `docker compose logs <service_name>`.
- **Isolate with API Tests:** Use API testing tools to check endpoints directly, isolating frontend from backend issues.
- **Browser Dev Tools:** Use the Network and Console tabs for frontend and API debugging.
- **VS Code Debugger:** Use the built-in debugger for step-through debugging of Python and Node.js services.
- **Simplify:** When stuck, temporarily remove dependencies to isolate the problematic component.
