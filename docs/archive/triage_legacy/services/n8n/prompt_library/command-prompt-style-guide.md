# Command Prompt Style Guide for Dual-Stack Integration Agent

**Purpose:**  
Guide the agent through the next logical steps after Freqtrade API enablement, ensuring all cross-stack integration points are tested, validated, and documented.

---

## 1. **Test Cross-Container Network Connectivity**

**Goal:** Ensure the Freqtrade container and automation-stack services (Controller, n8n) are on the same Docker network (e.g., `mcp-net`).

**Prompt Example:**
```
# List Docker networks and check if both containers are attached
docker network ls
docker network inspect mcp-net

# From Freqtrade container, ping Controller and n8n by service name
ping -c 2 controller_mcp
ping -c 2 n8n_mcp

# From Controller container, curl Freqtrade API
curl -s http://freqtrade_devcontainer:8080/api/v1/ping
```

**Required Info:**
- Docker network name (default: `mcp-net`)
- Service/container names (e.g., `freqtrade_devcontainer`, `controller_mcp`, `n8n_mcp`)

---

## 2. **Test FastAPI Controller → Freqtrade API Integration**

**Goal:** Confirm the Controller can authenticate and interact with the Freqtrade API.

**Prompt Example:**
```
# From Controller container, authenticate and call Freqtrade API
curl -u freqtrader:SuperSecurePassword -X POST http://freqtrade_devcontainer:8080/api/v1/token/login
# Use returned access_token for further requests
curl -H "Authorization: Bearer <access_token>" http://freqtrade_devcontainer:8080/api/v1/status
```

**Required Info:**
- Freqtrade API credentials (username, password)
- Freqtrade API endpoint URLs
- Controller container access

---

## 3. **Test n8n → Freqtrade API (Direct or via Controller)**

**Goal:** Ensure n8n workflows can trigger Freqtrade actions.

**Prompt Example:**
```
# In n8n, create an HTTP Request node:
# - Method: POST
# - URL: http://controller_mcp:8000/api/v1/execute (or direct to Freqtrade API)
# - Auth: Use JWT or HTTP Basic as required
# - Body: Example payload to trigger a Freqtrade action

# Test the workflow and check for expected response
```

**Required Info:**
- n8n instance access (web UI or API)
- Controller endpoint details
- Example payloads for Freqtrade actions

---

## 4. **Verify Unified Logging**

**Goal:** Confirm all agent actions are logged to the unified PostgreSQL table.

**Prompt Example:**
```
# Connect to PostgreSQL (from any container with psql or via pgAdmin)
psql -h postgres -U automation_user -d automation_stack

# Query the logs table
SELECT * FROM agent_logs WHERE agent = 'FreqtradeManager_Agent' ORDER BY timestamp DESC LIMIT 10;
```

**Required Info:**
- PostgreSQL connection details (host, user, password, db)
- Log table/schema name (e.g., `agent_logs`)
- Agent identifier(s)

---

## 5. **Validate Shared Volumes (if used)**

**Goal:** Ensure file-based data (e.g., backtest results) is accessible across containers.

**Prompt Example:**
```
# From n8n or Controller container, list files in the shared volume
ls /host_vault/freqtrade_docs/
ls /host_vault/backtest_results/
```

**Required Info:**
- Volume mount paths in each container
- Expected files/directories

---

## 6. **Document and Mark Completion**

**Goal:** Update checklists and documentation with results and any new findings.

**Prompt Example:**
```
# Mark steps as complete in dual-stack-checklist.md
# Add troubleshooting notes or new integration steps as needed
# Summarize findings in a log or report file
```

**Required Info:**
- Path to checklist/documentation files
- Any issues or deviations encountered

---

## **General Troubleshooting Prompts**

- If a command fails, check:
  - Network connectivity (`ping`, `curl`)
  - Service logs (`docker logs <container>`)
  - API credentials and tokens
  - File permissions and mounts

- If unsure, consult:
  - `/docs` endpoints (e.g., `http://controller_mcp:8000/docs`)
  - Project documentation in `docs/setup/` and `docs/n8n/prompt_library/`
  - Web search for error messages

---

## **Agent Best Practices**

- Log all actions and results.
- Validate each step before proceeding.
- Update documentation with any new findings or fixes.
- If a required piece of information is missing, prompt the user or search the documentation.

---

## Agent Design & Guardrails: Best Practices for Dual-Stack Integration Agents

**Purpose:**  
Apply proven agent design principles to maximize reliability, safety, and autonomy for agents operating in the Freqtrade + automation-stack environment.

### 1. **Agent Structure & Orchestration**
- **Start simple:** Use a single agent with well-defined tools and clear instructions. Only split into multiple agents when workflows become too complex or tool overlap/confusion arises.
- **Manager pattern:** For multi-agent setups, use a central "manager" agent to coordinate specialized sub-agents via tool calls. This keeps workflows organized and scalable.
- **Decentralized pattern:** Use peer agents with handoff capability for workflows that require flexible, dynamic delegation.

### 2. **Tool Definition & Usage**
- Define tools (API calls, file ops, DB queries) with clear, descriptive names and parameters.
- Prefer reusable, well-documented tools to avoid duplication and confusion.
- Assign risk ratings to tools (read-only, write, high-impact) and require extra checks for high-risk actions.

### 3. **Prompt & Instruction Clarity**
- Use existing SOPs, checklists, and docs to create explicit, stepwise agent instructions.
- Break down dense tasks into atomic, numbered steps. Each step should map to a concrete action or output.
- Anticipate edge cases and specify fallback or escalation steps for missing/ambiguous info.

### 4. **Guardrails & Safety**
- Implement layered guardrails:
  - **Relevance classifier:** Keep agent actions on-topic and within scope.
  - **Safety classifier:** Detect and block unsafe/jailbreak inputs.
  - **PII filter:** Prevent exposure of sensitive data.
  - **Moderation:** Flag/stop harmful or inappropriate actions.
  - **Rules-based protections:** Use blocklists, regex, and output validation for known threats.
- For high-risk or irreversible actions, require human-in-the-loop approval or escalation.

### 5. **Human Intervention & Logging**
- Set thresholds for retries/failures; escalate to a human if exceeded.
- Always log actions, decisions, and errors for traceability and post-mortem analysis.
- Update documentation and checklists with new edge cases, fixes, or workflow changes.

### 6. **Iterative Improvement**
- Start with a minimal, working agent. Validate with real tasks and users.
- Add new tools, guardrails, and orchestration patterns as complexity grows.
- Regularly review logs and user feedback to refine instructions, tools, and safety measures.

---

**Reference:**
- See `docs/n8n/guide-to-building-agents.md` for detailed frameworks, orchestration patterns, and guardrail examples.

**End of Addendum**

---

**End of Guide**  
Use this as a reference for all future cross-stack integration and troubleshooting tasks. 