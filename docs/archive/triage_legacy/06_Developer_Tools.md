# 06: Developer Tools and Practices

**Status:** Consolidated $(date +%Y-%m-%d)

**Purpose:** Outline recommended tools, VS Code extensions, CLI commands, and best practices for developing and maintaining the auto-stack on Ubuntu 24.04 Linux.


### 1.1. Docker and Docker Compose

- **Role:** Essential for running the entire auto-stack as a collection of containerized services.
- **Syntax:** The project uses Docker Compose V2+ syntax (e.g., `docker compose up`).

#### Essential Commands (run from terminal)

**Service Management:**

```bash
# Start all services in detached mode
docker compose up -d

# Start specific services
docker compose up -d n8n_auto controller_auto

# Stop and remove containers and networks
docker compose down

# Stop and remove containers, networks, and volumes (destructive)
docker compose down -v

# Restart specific service
docker compose restart <service_name>

# List running services with status
docker compose ps

# View service resource usage
docker compose top
```

**Log Management:**

```bash
# View logs for all services
docker compose logs

# View logs for specific service
docker compose logs <service_name>

# Follow logs in real-time
docker compose logs -f <service_name>

# View last 100 lines of logs
docker compose logs --tail=100 <service_name>

# View logs with timestamps
docker compose logs -t <service_name>
```

**Container Interaction:**

```bash
# Execute command inside running container
docker compose exec <service_name> <command>

# Get shell access to container
docker compose exec <service_name> /bin/bash
# or for Alpine-based containers
docker compose exec <service_name> /bin/sh

# Execute command as specific user
docker compose exec -u root <service_name> <command>
```

**Image and Build Management:**

```bash
# Build or rebuild service image
docker compose build <service_name>

# Build without using cache
docker compose build --no-cache <service_name>

# Pull latest images for all services
docker compose pull

# Pull image for specific service
docker compose pull <service_name>
```

#### Volume and Data Management

**Volume Operations:**

```bash
# List all Docker volumes
docker volume ls

# Inspect volume details
docker volume inspect <volume_name>

# Remove unused volumes (caution!)
docker volume prune

# Backup volume data
docker run --rm -v <volume_name>:/source -v $(pwd):/backup alpine tar czf /backup/backup.tar.gz -C /source .

# Restore volume data
docker run --rm -v <volume_name>:/target -v $(pwd):/backup alpine tar xzf /backup/backup.tar.gz -C /target
```

**Service-Specific Volume Names:**

- `n8n_data_auto` - n8n workflows and settings
- `mem0_data_auto` - Mem0 memory storage
- `qdrant_data_auto` - Vector database storage
- `pgdata_logging_auto` - PostgreSQL logging data

#### Debugging and Troubleshooting

**Container Inspection:**

```bash
# Inspect container configuration
docker inspect <container_name>

# View container resource usage
docker stats <container_name>

# View container processes
docker top <container_name>
```

**Network Debugging:**

```bash
# List Docker networks
docker network ls

# Inspect network configuration
docker network inspect auto-stack-net

# Test connectivity between containers
docker compose exec <service_name> ping <other_service_name>

# Check if port is accessible
docker compose exec <service_name> nc -zv <host> <port>
```

**Health Checks:**

```bash
# Check service health status
docker compose ps --format table

# View detailed service status
docker compose ps --services --filter "status=running"
```

#### Performance and Resource Management

**Resource Monitoring:**

```bash
# Monitor all container resources in real-time
docker stats

# Monitor specific container
docker stats <container_name>

# View Docker system usage
docker system df

# Clean up unused resources
docker system prune -f

# Clean up everything (very destructive!)
docker system prune -af --volumes
```

**Container Resource Limits:**

- Review `docker-compose.yml` for memory and CPU limits
- Use `docker compose config` to validate compose file syntax
- Monitor resource usage during development with `docker stats`

#### Development Workflow Best Practices

**Ubuntu 24.04 Integration:**

- **Native Environment:** Development is performed directly on Ubuntu 24.04 Linux for optimal performance and compatibility.
- **File System:** Project files should reside in the user's home directory (e.g., `/home/gleshen/projects/auto-stack`).
- **Docker Engine:** Uses native Docker Engine on Linux, providing better performance than Docker Desktop.

**Hot Reload and Development:**

```bash
# Rebuild service after code changes
docker compose up -d --build <service_name>

# Force recreate container (useful for environment changes)
docker compose up -d --force-recreate <service_name>

# Watch for changes and rebuild automatically (if using docker-compose-dev.yml)
docker compose -f docker-compose.yml -f docker-compose-dev.yml up --build
```

### 1.2. VS Code (Visual Studio Code)

- **Role:** Primary code editor and development IDE.
- **Native Linux Integration:** VS Code runs natively on Ubuntu 24.04 with full system integration.
- **Recommended Workflow ("Focused Workflow"):**
  - **The mandatory workflow is to open each service in its own dedicated VS Code window.** This ensures that extensions and settings are loaded correctly without conflict.
  - **How-To:**
    1. Open your terminal.
    2. Navigate to the service directory (e.g., `cd ~/projects/auto-stack/freq-chat`).
    3. Run `code .` to open that folder in a new VS Code window.
- **Essential Extensions:**
  - **Docker:** Manage containers, images, and view logs directly in the editor.
  - **Python:** For Controller, Mem0, and Freqtrade development.
  - **Ruff:** For high-performance Python linting and formatting.
  - **ESLint & Prettier:** For `freq-chat` (Next.js/TypeScript) code quality.
  - **Dev Containers:** Essential for working within the Freqtrade dev container.
  - **Markdown All in One:** For editing documentation.
  - **REST Client or Thunder Client:** For testing APIs directly within VS Code.
  - **GitLens:** Enhanced Git integration and history visualization.

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

- **Python Environment:** For local testing, create a Python virtual environment (`python3 -m venv .venv`, `source .venv/bin/activate`, `pip install -r requirements.txt`).
- **Poetry:** The `mem0` library uses Poetry for dependency management. Use `poetry install` and `poetry shell` within the `mem0/` directory.
- **API Testing:** Use the recommended VS Code REST extensions, Postman, or `curl`/`httpie` from the terminal.
- **Linters:** Ruff is recommended for its speed and comprehensive checks.

### 2.3. `freq-chat` (Next.js) Development

- **Node.js & pnpm:** Node.js should be installed using `nvm` for version management on Ubuntu 24.04.
- **Package Manager:** `pnpm` is the required package manager. Run all commands (`pnpm install`, `pnpm dev`) from the terminal.
- **Vercel CLI:** For managing deployments and environment variables (`vercel env pull`).
- **Browser Developer Tools:** Essential for debugging the frontend and its API interactions.

### 2.4. Database Management

- **PostgreSQL (`postgres_logging_auto`):**
  - **Tools:** Use pgAdmin, DBeaver, or native `psql` client for database management.
  - **CLI Access:** `docker compose exec postgres_logging_auto psql -U autostack_logger -d autostack_logs`
- **Qdrant (`qdrant_auto`):**
  - **Web UI:** Access at `http://localhost:6333` to inspect collections and points, crucial for debugging Mem0.

## 3. General CLI Utilities

- **`curl` or `httpie`:** For quick API testing from the command line.

  ```bash
  # Install httpie on Ubuntu
  sudo apt install httpie
  ```

- **`jq`:** A command-line JSON processor for parsing API responses (`| jq .`).

  ```bash
  # Install jq on Ubuntu
  sudo apt install jq
  ```

- **`markdownlint-cli`:** Use `npm install -g markdownlint-cli` and `markdownlint **/*.md` to check documentation for style consistency.
- **`tree`:** For visualizing directory structures.

  ```bash
  # Install tree on Ubuntu
  sudo apt install tree
  ```

- **`bat`:** Enhanced `cat` with syntax highlighting.

  ```bash
  # Install bat on Ubuntu
  sudo apt install bat
  ```

- **`fd`:** Modern alternative to `find`.

  ```bash
  # Install fd on Ubuntu
  sudo apt install fd-find
  ```

## 4. Debugging Practices

- **Start with Logs:** Always check service logs first: `docker compose logs <service_name>`.
- **Isolate with API Tests:** Use API testing tools to check endpoints directly, isolating frontend from backend issues.
- **Browser Dev Tools:** Use the Network and Console tabs for frontend and API debugging.
- **VS Code Debugger:** Use the built-in debugger for step-through debugging of Python and Node.js services.
- **Simplify:** When stuck, temporarily remove dependencies to isolate the problematic component.
