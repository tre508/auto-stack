# TODO & Feature Roadmap

## Phase 4: `freq-chat` & Mem0 Integration (In Progress)

- **[IN PROGRESS]** 🚀 **Documentation & Configuration Cleanup**:
  - **[IN PROGRESS]** Standardize all service names in `docker-compose.yml` and documentation to use the `_auto` suffix (e.g., `n8n_auto`, `mem0_auto`).
  - **[IN PROGRESS]** Rename the main Docker Compose file from `compose-mcp.yml` to `docker-compose.yml` and update all references.
  - **[IN PROGRESS]** Consolidate and update all documentation (`00` through `06`, `README_agent.md`, etc.) to be consistent with the latest architecture (`freq-chat`, self-hosted Mem0, controller proxy, unified logging).
  - **[TODO]** Create a centralized `API_Contracts.md` document to formally define the endpoints, request/response schemas, and authentication methods for `controller_auto`, `mem0_auto`, `openrouter_proxy_auto`, and key n8n webhooks.

## Phase 5: Advanced Integration & Trading Features

- **[TODO]** **FreqAI Integration**:
  - [ ] Develop n8n workflows and controller endpoints to manage FreqAI models (training, evaluation).
  - [ ] Integrate FreqAI predictions into `freq-chat` for analysis.
- **[TODO]** **Eko Service Integration**:
  - [ ] Fully integrate the `eko_service` for real-time market data analysis, with results accessible via `freq-chat`.
- **[TODO]** **Freqtrade to Mem0 Logging**: Have Freqtrade log key events (trades, status changes) directly to Mem0 via the controller or a dedicated API endpoint for a unified event history.

## Phase 6: Production Hardening & Deployment

- **[TODO]** **Security Hardening**:
  - [ ] Secure all public-facing endpoints (Traefik, `freq-chat` backend, etc.).
  - [ ] Implement robust API key management for all internal services (`controller_auto`, `mem0_auto`, etc.).
- **[TODO]** **Deployment Automation**:
  - [ ] Create scripts to automate the deployment and update process for the entire stack.
  - [ ] Document the process for deploying to a cloud environment (e.g., DigitalOcean, AWS).

---

## Completed / Deprecated

- **[DEPRECATED]** Create `mem0-mcp` service to connect Cursor to Mem0 Cloud Platform.
  - **Reason for Deprecation:** Shift in focus to a fully self-hosted solution. The new `mem0_auto` service with its REST API is the primary memory backend. Direct Cursor integration via MCP would require adapting the `mem0-mcp` server to use this REST API, which is a future consideration, not a current priority.
- **[DEPRECATED]** Store `memory.json` in a shared volume.
  - **Reason for Deprecation:** The self-hosted `mem0_auto` service now manages its own state and history within its dedicated Docker volume (`mem0_data_auto`), using a SQLite DB (`mem0_history.db`) and Qdrant for vectors. This is more robust and scalable than a single JSON file.
- **[DEPRECATED]** Use a single, monolithic agent.
  - **Reason for Deprecation:** The architecture has evolved to a multi-agent system orchestrated by n8n, with specialized agents for different domains (docs, trading, research) for better modularity and scalability.
- **[DEPRECATED]** Use `json-server` for mock APIs.
  - **Reason for Deprecation:** Core services (`controller_auto`, `mem0_auto`, etc.) now have their own robust FastAPI/Node.js-based APIs, making mock servers unnecessary for development and testing.
- **[DEPRECATED]** Direct agent interaction with Freqtrade filesystem.
  - **Reason for Deprecation:** Interactions are now brokered through the FastAPI Controller or n8n workflows, which provide a secure and structured API layer, avoiding direct and potentially risky filesystem manipulation by the agent.
