# 📘 MCP Tools Reference Guide

**Version:** 1.0.0
**Last Updated:** 2025-05-16
**Maintainer:** automation-stack/infra

---

## 🧩 MCP Server Overview

This guide documents available MCP (Model Control Protocol) servers and tools integrated into the automation-stack, optimized for AI agents and Cursor IDE workflows.

---

## ✅ Active Servers & Tools

### 🧠 `mem0` Server

**Tools:**

* `add_memory`
* `search_memory`
* `delete_memory`

**Project Use Cases:**

* Log task outcomes or summaries (e.g., results of `AutomationChecklist.md` verifications).
* Recall past documentation, commands, or frequently used configuration snippets (e.g., Vercel API endpoint structure, n8n webhook URLs) to improve accuracy.
* Purge outdated memory entries.
* Track the state of multi-step automation sequences.
* Log key decisions made during complex task execution.
* Cache checksums or versions of critical config files (`compose-mcp.yml`, `.env`) to detect unintended changes.

**Example:**

```bash
mem0::add_memory { "content": "Summarized agent checklist run for Vercel API, item 3.1 success", "tags": ["agent", "checklist", "vercel_api"] }
mem0::search_memory { "query": "controller_mcp status endpoint" }
```

---

### 🔗 `servers` (Smithery CLI)

**Tools:**

* `create_entities`, `create_relations`, `add_observations`
* `delete_entities`, `delete_observations`, `delete_relations`
* `read_graph`, `search_nodes`, `open_nodes`

**Project Use Cases:**

* Construct or visualize agent graphs and service dependencies.
* Link agents to tasks or events.
* Model relationships between services in `compose-mcp.yml` (e.g., `controller_mcp` depends_on `mem0`).
* Represent `n8n` workflows as entities and link them to the services they interact with.
* Track documentation entities and their dependencies.
* Log successful/failed integration test results from `AutomationChecklist.md` as observations on relevant service entities.

**Example:**

```bash
servers::create_entities { "type": "Agent", "name": "CentralBrain_Agent" }
servers::create_relations { "source": "CentralBrain_Agent", "target": "VercelChat_Node", "type": "uses" }
servers::add_observations { "entityName": "controller_mcp", "contents": ["Responded to /status check successfully at $(Get-Date)"] }
```

---

### 🐳 `MCP_DOCKER`

**Tools:**

* Full Docker + system interface:

  * `execute_command`, `read_file`, `write_file`, `list_directory`
  * `search_files`, `get_config`, `edit_block`, `force_terminate`

**Project Use Cases:**

* Monitor or restart containers (`vercel_chat_mcp`, `mem0`, `controller_mcp`, `n8n_mcp`).
* Fetch `.env` files or service logs for troubleshooting (e.g., `docker logs controller_mcp`).
* Adjust configs in-place (e.g., port mappings in `compose-mcp.yml`, followed by `docker-compose up -d --force-recreate <service_name>`). **Use with extreme caution and backup original values.**
* Check disk usage within the Docker environment.

**Automation-Stack Tips:**
*   For `execute_command`:
    *   Automate restarting services: `MCP_DOCKER::execute_command { "command": "docker restart controller_mcp" }`
    *   Tail logs: `MCP_DOCKER::execute_command { "command": "docker logs vercel_chat_mcp --tail 50" }`
*   For `read_file`:
    *   Inspect service configurations: `MCP_DOCKER::read_file { "path": "/app/.env" }` (assuming path inside the container, adjust as needed for mounted volumes like `~/projects/auto-stack/controller/.env`).
*   For `edit_block`:
    *   Carefully update API keys in service `.env` files. **Always log original values via `mem0` before editing.**

**Example:**

```bash
MCP_DOCKER::read_file { "path": "~/projects/auto-stack/compose-mcp.yml" }
MCP_DOCKER::execute_command { "command": "docker ps -a --filter name=controller_mcp" }
```

---

### 📁 `Filesystem (Reference)`

**Paths Allowed:**

*   `/mnt/c/Users/glenn/projects/*` (Example for accessing Windows filesystem from WSL)
*   `~/projects/*` (Example for accessing WSL home directory)

**Tools:**

* `read_file`, `write_file`, `search_files`, `create_directory`, `move_file`

**Project Use Cases:**

* Update or diff Markdown docs (e.g., `AutomationChecklist.md`, `docs/vercel/*.md`). Use relative paths from workspace root for consistency.
* Search code or configuration patterns across folders.
* Auto-generate doc directories as outlined in `MasterGameplan.md` or `TODO.md`.
* Verify existence and content of critical files like `.env` or `compose-mcp.yml` before starting automation tasks.

**Example:**

```bash
Filesystem::search_files { "path": "~/projects/auto-stack/docs/setup", "pattern": "*.md" }
Filesystem::write_file { "path": "docs/vercel/troubleshooting.md", "content": "# Vercel Troubleshooting\nUpdated: $(date)\n..." }
Filesystem::read_file { "path": "compose-mcp.yml" }
```

---

### 📦 `Docker`

**Tool:** `docker`

**Use Cases:**

* Start, stop, inspect, or debug containers defined in `compose-mcp.yml`.
* Regularly inspect logs of `vercel_chat_mcp`, `n8n_mcp`, and `controller_mcp`.

**Example:**

```bash
Docker::docker { "args": "logs vercel_chat_mcp --tail 100" }
Docker::docker { "args": "ps -a --filter label=com.docker.compose.project=automation-stack" }
Docker::docker { "args": "restart n8n_mcp" }
```

---

### 🌍 `Fetch`

**Tool:** `fetch`

**Use Cases:**

* Fetch documentation or changelogs as markdown, especially for key dependencies (Vercel AI SDK, Next.js, FastAPI, n8n) if troubleshooting.
* Cross-reference information from local docs (e.g., `Vercel-integration.md`) with official sources.

**Example:**

```bash
Fetch::fetch { "url": "https://vercel.com/docs/integrations/create-integration/approval-checklist" }
Fetch::fetch { "url": "https://fastapi.tiangolo.com/tutorial/first-steps/" }
```

---

### 🧰 Utility Servers

* `OpenAPI Schema`: Generate & inspect Swagger/OpenAPI routes.
    * **Automation-Stack Tip:** Use to inspect the `/docs` endpoint of `controller_mcp` to understand available API routes and their schemas, crucial for `n8n` workflow design or direct API calls.
* `Time`: Convert timezones or compute durations.
* `Git`: Stage/commit/push directly from workflows.
    * **Automation-Stack Tip:** Automate committing documentation changes after successful task completion (e.g., `Git::git { "args": "add docs/AutomationChecklist.md" }`, then `Git::git { "args": "commit -m 'Verified item X on AutomationChecklist'" }`).
* `Bootstrap`: Register new tools from code (primarily for agent/tool development).

---

## 🧠 Best Practices

* Always verify paths before using `write_file`, `edit_block`, or any `MCP_DOCKER` file operations.
* Pair `get_config` with `read_file` for environment diagnostics.
* Use `mem0` to track troubleshooting context, task memory, and pre-change states of critical configurations.
* When invoking multiple tools, namespace responses or log entries per task context for clarity.
* For tasks involving `AutomationChecklist.md`, structure `mem0` entries or `servers` observations with consistent tagging (e.g., `checklist_item_id`, `status:success/failure`, `timestamp`).
* **Crucial for Configs:** When using `MCP_DOCKER::edit_block` or `Filesystem::write_file` on sensitive files (`compose-mcp.yml`, `.env` files):
    1. Read the file first.
    2. Log the existing relevant section using `mem0::add_memory` (for snippets) or `servers::add_observations` (for entity states).
    3. Make the change.
    4. Re-read the file or relevant section to verify the change was applied as expected. This provides a basic rollback/audit trail.
* Before running `docker` commands that might affect service availability (restart, stop), consider if a less disruptive check (logs, ps) is sufficient.

---

*This guide is agent-readable and version-tracked.*
