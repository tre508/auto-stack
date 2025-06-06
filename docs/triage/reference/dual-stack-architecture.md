**Dual-Stack Architecture Overview**

The project is organized into two interconnected Dockerized stacks: the **automation-stack** and the **Freqtrade** development environment. The **automation-stack** serves as the central orchestration and AI gateway, while the **Freqtrade** stack provides algorithmic trading, strategy development, and backtesting within a VS Code Dev Container .

---

### Automation-Stack

* **Purpose & Services:**

  * **`freq-chat`**: A Next.js/Vercel AI chatbot serving as the primary user interface for natural-language commands and LLM interactions .
  * **n8n**: Workflow automation platform for designing, triggering, and monitoring complex multi-step processes .
  * **Mem0**: Centralized memory and knowledge service providing vector-based similarity search, graph relationships, and persistent conversational context .
  * **FastAPI Controller**: Custom Python API exposing endpoints for automation tasks, acting as a bridge to other services (e.g., Freqtrade, n8n) .
  * **Traefik**: Reverse proxy and load balancer managing external access, routing, and TLS termination for all stack services .
  * **OpenRouter Proxy (Optional)**: Node.js service that transparently injects API keys to route OpenAI-compatible requests to OpenRouter.ai .

---

### Core Service Configuration & Verification

All services in the automation-stack are defined in a unified `compose-mcp.yml` file and a shared `.env`. Verification is guided by a detailed checklist covering:

* Container health and logs (Docker ps/logs)
* Endpoint accessibility via Traefik hostnames and direct network calls
* Functional tests (e.g., sending messages in `freq-chat`, triggering sample n8n workflows, Mem0 memory operations)
* Persistence across restarts via Docker volumes for Qdrant, SQLite, and other data stores .

---

### Freqtrade Dev Container

The Freqtrade stack runs inside a VS Code Dev Container, ensuring a reproducible environment for:

* **Algorithmic Trading Bots**: Live deployment and management of trading strategies.
* **Strategy Development & Backtesting**: Python-based strategy coding, historical data analysis, and FreqAI model integration.
* **User Data Persistence**: Mounting `user_data/` for strategies, notebooks, logs, and backtest results.
* **API & UI Access**: Freqtrade’s REST API and web UI are forwarded to the host (e.g., `http://localhost:8080`) and can join the shared `mcp-net` network for cross-stack calls .

---

### Cross-Stack Integration Patterns

Interactions between the two stacks follow several patterns:

1. **n8n ↔ FastAPI Controller**:

   * n8n “HTTP Request” nodes call controller endpoints (e.g., `/api/v1/execute`, `/api/v1/notify`) for orchestrating tasks .
2. **Controller ↔ Freqtrade API**:

   * Controller makes authenticated HTTP calls to Freqtrade’s API (`/ping`, `/backtest`, `/trades`), handling JWT for protected endpoints .
3. **n8n ↔ Freqtrade (Direct)**:

   * Less common, but possible for simple data fetches via HTTP nodes.
4. **Mem0 Integration Across Components**:

   * Controller uses the `mem0ai` Python client, n8n workflows use HTTP nodes, and `freq-chat` backend API routes proxy requests to Mem0 for memory storage and retrieval .

---

### Multi-Agent Orchestration

A hierarchical, multi-agent model orchestrates complex tasks:

* **CentralBrain\_Agent** dispatches commands to manager agents and aggregates results.
* **Manager Agents** (FreqtradeManager, FreqAIManager, ResearchManager, UtilityManager) coordinate domain-specific workflows.
* **DocAgent & FreqtradeSpecialist\_Agent** handle documentation summarization and trading-specific automations, respectively.
* Agents leverage Mem0 for persistent state, context sharing, and knowledge retrieval, and communicate via n8n workflows and controller webhooks .

---

### Developer Tools & Extensions

Recommended tools streamline development across both stacks:

* **n8nChat Browser Extension**: AI-assisted n8n workflow creation and debugging.
* **Mem0 Debugging Tools**: Vector DB UIs (Qdrant, ChromaDB), API testing (Postman, Insomnia, curl).
* **VS Code Extensions**: Dev Containers, Python, Docker, Markdown, Poetry, Tailwind CSS IntelliSense, REST Client.
* **API Testing & DB Clients**: pgAdmin/DBeaver for PostgreSQL, TablePlus, HTTPie.
* **Vercel CLI & PNPM**: For `freq-chat` deployment and local development .

---

### `freq-chat` & Vercel Integration

* **Deployment**: `freq-chat` is linked to a Vercel project, with environment variables managed via `vercel env` commands.
* **Orchestration Routes**: Next.js API routes (`/api/orchestration/n8n`, `/api/orchestration/controller`, `/api/orchestration/mem0`) securely proxy requests to backend services, requiring NextAuth.js sessions .
* **Command Flow**: User messages in the chat UI invoke these API routes, which trigger n8n workflows, controller actions, or Mem0 operations and return results to the UI .

---

### Strategic Roadmap & Goals

In the near term, the Master Gameplan focuses on:

1. **Cross-Stack Integration Validation**
2. **Modular Multi-Agent Orchestration Deployment**
3. **Unified Agent Logging**
4. **Documentation Synchronization & Audit**
5. **End-to-End Workflow Testing (Chat → Agents → Freqtrade → Reporting)**
6. **Next-Phase Scaling & Technical Debt Assessment** .

---

This **dual-stack** model unifies AI-driven orchestration with algorithmic trading, enabling seamless, context-aware automation and development workflows across services.

-----------------------------------------------------------
### Potential weak points in the current dual-stack, categorized by domain:

---

### Infrastructure

1. **Monolithic Docker Compose**
   All core services (n8n, Mem0/Qdrant, FastAPI controller, Traefik, etc.) run under a single `compose-mcp.yml`. There’s no higher-level orchestration (e.g. Kubernetes) for auto-scaling, rolling updates, or node failure recovery .

2. **Lack of Centralized Monitoring & Alerting**
   While agent actions are logged to PostgreSQL, there’s no metrics stack (Prometheus/Grafana) or centralized log aggregation (ELK/EFK). This makes it hard to track container resource usage, request latencies, error rates, or set up automated alerts before incidents cascade.

3. **Single-Node Mem0 Persistence**
   Mem0 relies on one Qdrant instance with a local Docker volume for vector storage. There’s no documented backup/restore or clustering plan—so disk corruption or host failure could result in unrecoverable memory data .

---

### Implementation & Deployment

4. **Manual Deployment Outside `freq-chat`**
   Only `freq-chat` enjoys Vercel’s CI/CD. n8n, Mem0, and the controller still require manual `docker-compose up` and `.env` edits, leading to error-prone rollouts and drift between environments.

5. **Environment-Variable Sprawl**
   With dozens of env-vars across Vercel and local `.env` files (API keys, URLs, ports), synchronization is manual (`vercel env pull`) and brittle—one mismatch can break integrations silently .

---

### Security

6. **Exposed n8n & Controller UIs**
   n8n’s workflow UI and the controller’s Swagger docs (e.g. at `/docs`) may be publicly routable via Traefik; without strict network ACLs, RBAC or API-key enforcement, attackers could list or invoke sensitive workflows/endpoints .

7. **Optional / Weak Auth for Mem0**
   Mem0’s API-key protection is optional and env-based. No vault integration or key-rotation strategies are documented, increasing the risk of credential leakage or replay attacks.

---

### Logical & Integration

8. **Tight Synchronous Coupling**
   Cross-stack calls (n8n → controller → Freqtrade API) are all synchronous HTTP requests with no message queue, backoff, or circuit breaker. A slow or down stream service can block entire workflows .

9. **Complex Multi-Agent Flows**
   The CentralBrain → manager → sub-agent model spans many n8n workflows and HTTP webhooks. Without formal orchestration (e.g., a state machine) or guaranteed idempotency beyond guidelines, race conditions and partial failures are likely .

10. **Intelligence**
    Read the `agent.prompt.md` file for more information on the intelligence of prompting within the project.
---

### Documentation & Verification

11. **Incomplete Integration Checks**
    The TODO lists still show unfinished Mem0 verification, controller wiring, and documentation cleanup. Gaps here can mask latent misconfigurations or broken integration loops .

---

**Next Actions to Mitigate:**

* Introduce a lightweight orchestration layer (e.g., K3s or Docker Swarm) and add health checks.
* Deploy a metrics/logging stack for real-time observability.
* Define backup/restore procedures for Mem0/Qdrant.
* Automate full-stack deployments via GitOps pipelines.
* Harden service endpoints with strict API-key or OAuth2 enforcement, and consider a secrets vault.
* Evaluate adding a message broker (e.g., RabbitMQ, Kafka) or retry/circuit-breaker patterns for cross-service calls.
* Formalize multi-agent orchestration with a state machine (e.g., Temporal, Durable Functions).
* Complete outstanding integration and documentation tasks as per `TODO.md`.
