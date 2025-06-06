# n8n Orchestration Prompts and Templates

This directory contains consolidated prompt templates, agent design patterns, and best practices for building n8n workflows in the Automation Stack.

## Contents

- [Multi-Agent Architecture](#multi-agent-architecture)
- [n8nChat Prompt Templates](#n8nchat-prompt-templates)  
- [Agent Design Patterns](#agent-design-patterns)
- [Command Prompt Style Guide](#command-prompt-style-guide)
- [Unified Logging](#unified-logging)

---

## Multi-Agent Architecture

### System Architecture Overview (Org Chart)

- **CentralBrain_Agent** (Orchestrator/Gatekeeper)
  - **FreqtradeManager_Agent**
    - StrategyAnalysis_Agent
    - Backtest_Agent
    - Hyperopt_Agent
    - TradeExecution_Agent
    - PerformanceMonitoring_Agent
  - **FreqAIManager_Agent**
    - FreqAI_ModelTrainer_Agent
    - FreqAI_RL_Agent
    - FeatureEngineering_Agent
    - OutlierDetection_Agent
  - **ResearchManager_Agent**
    - SentimentAnalysis_Agent
    - NewsAggregator_Agent
    - MarketMonitor_Agent
    - OrderflowAnalysis_Agent
  - **UtilityManager_Agent** (optional)
    - DataDownload_Agent
    - ModelPersistence_Agent
    - SQLAnalysis_Agent
    - NotificationAgent

### Best Practices for n8nChat Prompts
- Be explicit about agent roles, workflow triggers, and expected inputs/outputs
- Use HTTP Request nodes for inter-agent communication
- Include error handling, logging, and status reporting
- Keep each workflow modular and focused on a single responsibility
- Use structured JSON for all agent responses

---

## n8nChat Prompt Templates

### Core Orchestrator Templates

#### CentralBrain_Agent (Orchestrator)
```txt
Create an n8n workflow called 'CentralBrain_Agent' that acts as the main orchestrator for a multi-agent trading automation system.
- Trigger: Webhook node (POST, receives JSON commands from Vercel AI Chatbot).
- Parse the 'command' field and route to the appropriate manager agent (FreqtradeManager, FreqAIManager, ResearchManager, UtilityManager) using a Switch node.
- Each manager agent is called via HTTP Request node.
- Collect and aggregate responses, then return a structured JSON response to the user.
- Log all actions and errors.
- Output: { status, message, data }.
```

#### FreqtradeManager_Agent
```txt
Create an n8n workflow called 'FreqtradeManager_Agent' to manage all Freqtrade-related sub-agents.
- Trigger: HTTP Request node (receives JSON with {command, parameters}).
- Use a Switch node to route to the correct sub-agent (StrategyAnalysis, Backtest, Hyperopt, TradeExecution, PerformanceMonitoring).
- Each sub-agent is called via HTTP Request node.
- Aggregate and return results to CentralBrain_Agent.
- Log all actions and errors.
```

### Specialized Agent Templates

#### Backtest_Agent
```txt
Create an n8n workflow called 'Backtest_Agent' for running historical backtests on trading strategies.
- Trigger: HTTP Request node (receives JSON with {strategy, timerange, config}).
- Run the Freqtrade backtesting command using the Execute Command node.
- Parse the results and return a summary (PnL, Sharpe, drawdown) as JSON.
- Handle errors and report status to FreqtradeManager_Agent.
```

#### FreqAI_ModelTrainer_Agent
```txt
Create an n8n workflow called 'FreqAI_ModelTrainer_Agent' for training and retraining FreqAI models.
- Trigger: HTTP Request node (receives JSON with {model_type, features, labels, config}).
- Run model training using Freqtrade CLI and FreqAI options.
- Return training status and model metrics as JSON.
- Handle errors and report status to FreqAIManager_Agent.
```

### Utility Templates

#### Doc Mirror Cron Job
```txt
Create a scheduled workflow that:
- Runs daily at 3:00 AM
- Executes a bash command inside a Docker container to `git pull` inside the Obsidian Vault doc directory
- Responds with success/failure JSON
- Logs command output

Use these node steps:
1. Schedule trigger node
2. Execute Command node with shell script
3. Set node for formatting response
4. Respond to Webhook node

Set node descriptions for each step. Use `docker exec` format for the Execute Command.
```

#### Docker Container Health Check
```txt
Create a scheduled n8n workflow that:
- Runs daily at 7:00 AM.
- Checks the status of Docker containers named "n8n_mcp", "openwebui_mcp", and "traefik_mcp".
- If any of these containers are not in a "running" state, it sends an alert.
- The alert should list the down containers.

Use these node steps:
1. Schedule Trigger node.
2. Multiple "Execute Command" nodes (one for each container check).
3. Function Node to parse the statuses and identify non-running containers.
4. IF Node to check if there are any down containers.
5. HTTP Request Node to send the alert message if needed.
```

---

## Agent Design Patterns

### When to Build Agents

Build agents for workflows that have previously resisted automation, especially where traditional methods encounter friction:

1. **Complex Workflows** - Involving nuanced judgment, exceptions, or context-sensitive decisions
2. **Difficult-to-maintain Systems** - Unwieldy due to extensive and intricate rulesets  
3. **Heavy reliance on unstructured data** - Interpreting natural language, extracting meaning from documents

### Agent Design Foundations

Every agent consists of three core components:

1. **Model** - The LLM powering the agent's reasoning and decision-making
2. **Tools** - External functions or APIs the agent can use to take action
3. **Instructions** - Explicit guidelines and guardrails defining how the agent behaves

### Orchestration Patterns

#### Single-Agent Systems
- Single model equipped with appropriate tools executes workflows in a loop
- Good for simpler workflows with manageable complexity
- Each new tool expands capabilities without forcing multi-agent orchestration

#### Multi-Agent Systems

**Manager Pattern:**
- Central "manager" agent coordinates multiple specialized agents via tool calls
- Manager maintains context and control, synthesizing results into cohesive interaction
- Ideal when you want one agent controlling workflow execution and user access

**Decentralized Pattern:**
- Multiple agents operate as peers, handing off tasks based on specializations
- One-way transfer that allows agents to delegate to another agent
- Optimal when you don't need central control or synthesis

### Best Practices

#### Instructions
- Use existing documents (SOPs, support scripts, policy documents) to create LLM-friendly routines
- Break down dense tasks into smaller, clearer steps
- Define clear actions for every step
- Capture edge cases and include conditional handling

#### Tools
- Standardized definitions enabling flexible, many-to-many relationships
- Three types: Data (retrieve context), Action (interact with systems), Orchestration (agents as tools)
- Well-documented, thoroughly tested, and reusable tools

#### Guardrails
- Layered defense mechanism using multiple specialized guardrails
- Types: Relevance classifier, Safety classifier, PII filter, Moderation, Tool safeguards, Rules-based protections, Output validation
- Plan for human intervention at failure thresholds and high-risk actions

---

## Command Prompt Style Guide

### Test Cross-Container Network Connectivity
```bash
# List Docker networks and check if both containers are attached
docker network ls
docker network inspect mcp-net

# From Freqtrade container, ping Controller and n8n by service name
ping -c 2 controller_mcp
ping -c 2 n8n_mcp

# From Controller container, curl Freqtrade API
curl -s http://freqtrade_devcontainer:8080/api/v1/ping
```

### Test FastAPI Controller → Freqtrade API Integration
```bash
# From Controller container, authenticate and call Freqtrade API
curl -u freqtrader:SuperSecurePassword -X POST http://freqtrade_devcontainer:8080/api/v1/token/login
# Use returned access_token for further requests
curl -H "Authorization: Bearer <access_token>" http://freqtrade_devcontainer:8080/api/v1/status
```

### Verify Unified Logging
```sql
# Connect to PostgreSQL
psql -h postgres -U automation_user -d automation_stack

# Query the logs table
SELECT * FROM agent_logs WHERE agent = 'FreqtradeManager_Agent' ORDER BY timestamp DESC LIMIT 10;
```

### General Troubleshooting Prompts
- If a command fails, check: Network connectivity, Service logs, API credentials, File permissions
- If unsure, consult: `/docs` endpoints, Project documentation, Web search for error messages

---

## Unified Logging

### Recommended Pattern: Single Database, Unified Logs Table

All agents write to a single database with a unified `logs` table containing an `agent` field to distinguish sources.

#### Schema
```sql
CREATE TABLE IF NOT EXISTS agent_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT NOW(),
    agent VARCHAR(64),
    workflow VARCHAR(64),
    action TEXT,
    status VARCHAR(16),
    details JSONB,
    error TEXT
);
```

#### Advantages
- Centralized: Easy to search, aggregate, and correlate logs across agents
- Simpler management: Fewer databases to maintain, backup, and secure
- Scalable: PostgreSQL can handle logs from many agents
- Flexible queries: Filter by agent, workflow, status, etc.

### n8n as Logging Orchestrator
- All persistent, structured logs should be written to PostgreSQL by n8n workflows
- The controller should log to stdout and optionally a local file for debugging
- n8n workflows should include a "Postgres" node to log actions, status, errors, and details

#### Example n8n Postgres Node Mapping
- `agent`: e.g., `CentralBrain_Agent`
- `workflow`: e.g., `Backtest_Agent`  
- `action`: e.g., `run_backtest`
- `status`: e.g., `success` or `error`
- `details`: JSON object with relevant context
- `error`: error message if any

### Best Practices
- Use a flexible schema (JSONB for details) to accommodate evolving log formats
- Implement log rotation, partitioning, or archiving for large tables
- Restrict write access to logging tables; use roles/permissions
- Set up alerts for logging failures or anomalies
- Document all logging endpoints and schemas for maintainability

---

## Integration with Automation Stack

This orchestration prompt hub integrates with:

- **Controller**: Uses orchestration templates for agent workflow automation
- **n8n**: Leverages prompt templates for workflow creation and management
- **Freqtrade**: Applies specialized prompts for trading strategy automation
- **FreqAI**: Utilizes ML-specific prompts for model training and deployment
- **Unified Logging**: Centralizes observability across all orchestrated workflows

## Maintenance Guidelines

1. **Template Updates**: When system behavior changes, update relevant prompt templates here first
2. **Version Control**: Track prompt changes with meaningful commit messages  
3. **Testing**: Validate prompt templates by creating actual n8n workflows
4. **Documentation**: Keep examples current with system architecture changes
5. **Consolidation**: Avoid duplicating templates; merge and reference existing patterns
