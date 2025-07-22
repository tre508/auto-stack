# 🧠 prompt-library/n8nChat_prompt_templates.md

## Prompt Template: Create Doc Mirror Cron Job

---

**Goal:** Schedule a daily update to git mirror docs inside an Obsidian vault mounted in Docker.

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

## Prompt Template: Strategy Backtest Pipeline

---

**Goal:** Build a webhook-triggered workflow that runs a Freqtrade backtest and returns metrics.

```txt
Build a webhook-triggered n8n workflow that:

- Accepts a POST request with a `strategy_name` field
- Runs a Freqtrade backtest using that strategy name
- Extracts key metrics: win rate, profit %, max drawdown
- Responds with a formatted JSON payload

Steps:
1. Webhook Trigger node (POST)
2. Set node to capture `strategy_name`
3. Execute Command node running `docker exec freqtrade freqtrade backtesting --strategy <strategy_name>`
4. Function node to parse CLI output
5. Respond to Webhook node

Document each node with a description. Validate strategy name format.
```

## Prompt Template: Vercel AI Chat Summarizer

---

**Goal:** Route a user message through an LLM to summarize strategy notes.

```txt
Create a webhook-triggered n8n workflow that:

- Accepts input text from a user via webhook (field: `notes`)
- Sends it to Vercel AI Chat via the VercelChat Node (model: `llama3` or as configured)
- Uses the prompt: "Summarize these strategy notes for clarity and future reference."
- Returns the LLM's response in the webhook

Steps:
1. Webhook Trigger (POST)
2. Set Node (map `notes` to input)
3. VercelChat Node (base URL: `http://vercel-chat.localhost/api/llm`, model: `llama3`)
4. Set Node (map response)
5. Respond to Webhook

Make sure credentials and base URL are filled correctly. Label each node.
```

## Prompt Template: FreqAI Hyperopt Runner

---

**Goal:** Automate Hyperopt runs using strategy and config file names as input.

```txt
Build a webhook-driven workflow to:

- Accept POST data with `strategy` and `config` fields
- Run `freqtrade hyperopt` with those parameters via Docker
- Capture output stats (best ROI, drawdown, Sharpe, etc.)
- Respond with summarized metrics

Nodes:
1. Webhook Trigger (POST)
2. Set Node (extract input values)
3. Execute Command: `docker exec freqtrade freqtrade hyperopt --strategy <strategy> --config <config>`
4. Function Node: Parse and reduce output
5. Respond to Webhook with JSON object

Ensure Docker paths are valid and output fields are parsed cleanly.
```

## Prompt Template: LLM Research Trigger

---

**Goal:** Perform a one-off LLM-powered research query via @web.

```txt
Create a webhook-triggered workflow that:

- Accepts a `query` string from the request
- Calls OpenWebUI with the system prompt: "Use the @web tool to answer: {{ query }}"
- Waits for completion and returns the result

Nodes:
1. Webhook Trigger (POST)
2. Set Node to hold the incoming `query`
3. OpenAI Chat Node via OpenWebUI
4. Set Node to capture response
5. Respond to Webhook with full message

Make sure `@web` tool is referenced explicitly in the prompt.
```

## Prompt Template: Strategy Explainer via LLM

---

**Goal:** Explain a trading strategy's logic in plain language.

```txt
Create a workflow that:

- Accepts a POST request with raw strategy Python code as input
- Sends it to OpenWebUI for summarization
- Uses the system prompt: "Explain this Freqtrade strategy's logic step by step"
- Returns a markdown-formatted breakdown

Steps:
1. Webhook Trigger
2. Set Node (extract `strategy_code`)
3. OpenAI Chat Node (base URL: OpenWebUI, model: `llama3`)
4. Set Node (format markdown)
5. Webhook Response node

Test with real strategies like `KrakenFreqAIStrategy.py`.
```

## Prompt Template: Docker Container Health Check

---

**Goal:** Schedule a daily check for critical Docker containers and send a notification if any are down.

```txt
Create a scheduled n8n workflow that:

- Runs daily at 7:00 AM.
- Checks the status of Docker containers named "n8n_mcp", "openwebui_mcp", and "traefik_mcp".
- If any of these containers are not in a "running" state (or similar, depending on `docker ps` output), it sends an alert.
- The alert should list the down containers.

Use these node steps:
1. Schedule Trigger node.
2. Multiple "Execute Command" nodes (one for each container check using `docker ps --filter "name=^CONTAINER_NAME$" --filter "status=running" --format "{{.Names}}"` to see if it's running, or a more detailed status check).
3. Function Node to parse the statuses, identify non-running containers (e.g., if the command output for a normally running container is empty), and format an alert message.
4. IF Node to check if there are any down containers based on the Function Node's output.
5. HTTP Request Node (as a placeholder for an alert, e.g., to a webhook.site URL or a custom alert endpoint) to send the alert message if the IF condition is met.

Set node descriptions for each step. Ensure the command correctly captures container status. If a container is expected to be running, its absence in a "running" filter implies it's down or in an error state.
```

## Prompt Template: Git Repo New Commit Notifier

---

**Goal:** Monitor a specific branch of a Git repository for new commits and notify.

```txt
Build a scheduled n8n workflow that:

- Runs every hour.
- Checks for the latest commit hash on the "main" branch of the "https://github.com/user/automation-stack.git" repository.
- If the latest commit hash is different from the one checked previously, it sends a notification with the new commit hash.
- Stores the last checked commit hash to avoid duplicate notifications (e.g., using n8n's static data feature in a Set node or a simple local file/database).

Node Steps:
1. Schedule Trigger node.
2. Execute Command node to get the latest commit hash from the remote repository (e.g., `git ls-remote https://github.com/user/automation-stack.git refs/heads/main | cut -f1`).
3. Set Node to retrieve the previously stored commit hash (e.g., `{{ $env.STATIC_DATA.lastCommitHash || '' }}`).
4. IF Node to compare the current commit hash with the stored one (e.g., `{{ $json.currentCommitHash !== $json.previousCommitHash }}`).
5. If different (new commit):
    a. HTTP Request Node (as a placeholder for notification, e.g., to a webhook.site URL) to send the new commit hash.
    b. Set Node to update the stored commit hash in n8n's static workflow data (e.g., set `STATIC_DATA.lastCommitHash` to `{{ $json.currentCommitHash }}`).
6. End node or a Set node to finalize.

Label all nodes clearly. The `git` command needs to be executable by the n8n instance (e.g., git installed on the host or in the n8n Docker container).
```

## Prompt Template: Log File Pattern Matcher & Alerter

---

**Goal:** Monitor a log file for specific error patterns and send an alert if new occurrences are found.

```txt
Create a scheduled n8n workflow that:

- Runs every 15 minutes.
- Reads the last N lines (e.g., 50 lines) of a log file located at "/var/log/my_app/error.log" (assume this path is accessible to n8n, e.g., via a mounted volume or `docker exec` into another container).
- Searches for lines containing the pattern "CRITICAL ERROR" or "FATAL EXCEPTION".
- If new matching lines are found since the last check (to avoid re-alerting for the same errors), it sends an alert with these lines.

Consider these Node Steps:
1. Schedule Trigger node.
2. Execute Command node to read the log file (e.g., `tail -n 50 /var/log/my_app/error.log`). If n8n can't directly access the file, use `docker exec <container_name> tail -n 50 /path/inside/container/error.log`.
3. Function Node to:
    a. Filter lines matching the specified error patterns (e.g., using JavaScript string methods or regex).
    b. Retrieve a timestamp or a list of hashes of previously processed error lines from n8n's static data.
    c. Identify only the *new* error lines that haven't been processed.
    d. Update the stored timestamp/hashes with the latest processed errors.
4. IF Node to check if new critical errors were found by the Function Node.
5. HTTP Request Node (placeholder for alerting, e.g., to a webhook.site or email node) to send the new error lines if the IF condition is met.
6. End node.

Describe each node clearly. The mechanism for tracking processed lines (e.g., storing timestamps of log entries or hashes of error messages) is crucial for avoiding duplicate alerts.
```

## Prompt Template: Multi-Agent Documentation & Task Orchestration Hub (Updated)

---

**Overall System Goal:**
Create a scalable, modular multi-agent system for intelligent documentation management, Freqtrade/FreqAI automation, and research, orchestrated by a central coordinating agent ("CentralBrain_Agent"). The system uses a multi-manager pattern to distribute responsibilities and avoid overloading any single agent.

---

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

---

### n8nChat Prompt Engineering Best Practices
- Be explicit about agent roles and workflow boundaries.
- Specify trigger node (Webhook, Schedule, etc.), required/optional inputs, and output format.
- Describe main logic and delegation to sub-agents via HTTP Request nodes.
- Include error handling, logging, and status reporting.
- Encourage modularity and separation of concerns.

---

### Example n8nChat Prompts for Each Agent

#### CentralBrain_Agent (Orchestrator)
```txt
Create the initial part of an n8n workflow called 'CentralBrain_Agent':
- Add a Webhook node (POST, receives JSON commands from OpenWebUI).
- Add a Set node to parse and extract the 'command' field from the incoming request.
```

#### CentralBrain_Agent (Orchestrator)
```txt
Continue building the 'CentralBrain_Agent' workflow:
- Add a Switch node to route based on the 'command' field.
- For each route, add an HTTP Request node to call the appropriate manager agent (FreqtradeManager, FreqAIManager, ResearchManager, UtilityManager).
```

#### CentralBrain_Agent (Orchestrator)
```txt
Add to the 'CentralBrain_Agent' workflow:
- After receiving responses from manager agents, aggregate the results.
- Add a Set node to format the output as { status, message, data }.
- Add a Respond to Webhook node to return the response to the user.
- Add logging for all actions and errors.
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

#### FreqAIManager_Agent
```txt
Create an n8n workflow called 'FreqAIManager_Agent' to manage all FreqAI/ML sub-agents.
- Trigger: HTTP Request node (receives JSON with {command, parameters}).
- Use a Switch node to route to the correct sub-agent (ModelTrainer, RL, FeatureEngineering, OutlierDetection).
- Each sub-agent is called via HTTP Request node.
- Aggregate and return results to CentralBrain_Agent.
- Log all actions and errors.
```

#### ResearchManager_Agent
```txt
Create an n8n workflow called 'ResearchManager_Agent' to manage all research and market intelligence sub-agents.
- Trigger: HTTP Request node (receives JSON with {command, parameters}).
- Use a Switch node to route to the correct sub-agent (SentimentAnalysis, NewsAggregator, MarketMonitor, OrderflowAnalysis).
- Each sub-agent is called via HTTP Request node.
- Aggregate and return results to CentralBrain_Agent.
- Log all actions and errors.
```

#### UtilityManager_Agent (optional)
```txt
Create an n8n workflow called 'UtilityManager_Agent' to manage utility sub-agents.
- Trigger: HTTP Request node (receives JSON with {command, parameters}).
- Use a Switch node to route to the correct sub-agent (DataDownload, ModelPersistence, SQLAnalysis, Notification).
- Each sub-agent is called via HTTP Request node.
- Aggregate and return results to CentralBrain_Agent.
- Log all actions and errors.
```

#### Example Sub-Agent (Backtest_Agent)
```txt
Create an n8n workflow called 'Backtest_Agent' for running historical backtests on trading strategies.
- Trigger: HTTP Request node (receives JSON with {strategy, timerange, config}).
- Run the Freqtrade backtesting command using the Execute Command node.
- Parse the results and return a summary (PnL, Sharpe, drawdown) as JSON.
- Handle errors and report status to the calling manager agent.
```

---

### Implementation Notes
- Each agent should be a modular n8n workflow, triggered via HTTP Request nodes from its parent manager or the CentralBrain_Agent.
- Use clear, structured JSON for all inter-agent communication.
- Log all actions, errors, and status updates for observability.
- Use n8n's built-in memory or external storage for stateful operations if needed.

---

**For full prompt templates and detailed workflow breakdowns, see CentralBrain.md in the prompt_library.**
