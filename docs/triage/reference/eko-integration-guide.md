# Eko Integration Guide

This document provides an in-depth guide for integrating **Eko**, a production-ready agent framework, into the existing `automation-stack` and `freqtrade` environments. It outlines architectural considerations, step-by-step instructions, code samples, best practices, and troubleshooting tips.

## Table of Contents

1. [Introduction](#introduction)
2. [Current Automation-Stack Overview](#current-automation-stack-overview)
3. [Eko Framework Overview](#eko-framework-overview)
4. [Integration Objectives](#integration-objectives)
5. [Architectural Integration Design](#architectural-integration-design)
6. [Step-by-Step Integration Instructions](#step-by-step-integration-instructions)

   * 6.1 [Prerequisites](#prerequisites)
   * 6.2 [Installing Eko SDK (Node.js)](#installing-eko-sdk-nodejs)
   * 6.3 [Integrating Eko via Node.js Service in FastAPI Controller](#integrating-eko-via-nodejs-service-in-fastapi-controller)
   * 6.4 [Embedding Eko into n8n Workflows](#embedding-eko-into-n8n-workflows)
   * 6.5 [Configuring Eko Tools and Hooks (Node.js)](#configuring-eko-tools-and-hooks-nodejs)
   * 6.6 [Integrating with Mem0 for Memory](#integrating-with-mem0-for-memory)
   * 6.7 [Exposing Eko Workflows as MCP Tools](#exposing-eko-workflows-as-mcp-tools)
   * 6.8 [Example: Web Interaction Automation (Conceptual)](#example-web-interaction-automation-conceptual)
7. [Best Practices and Tips](#best-practices-and-tips)
8. [Testing and Verification](#testing-and-verification)
9. [Troubleshooting](#troubleshooting)
10. [Conclusion](#conclusion)

---

## Introduction

As part of our ongoing effort to enhance the flexibility and intelligence of our automation framework, this guide details how to integrate **Eko**—a code-native, LLM-driven agent framework implemented primarily in **JavaScript**—into our existing services (`n8n`, `FastAPI Controller`, `Mem0`, and `freq-chat`). By leveraging Eko's hybrid natural‑language and code interface, built‑in tool support, hierarchical planning, and hook system, we can streamline dynamic, multi-step automations. **Note:** Eko is a JavaScript/Node.js library; integration with Python services like the FastAPI Controller requires interprocess communication, such as calling a local Node.js service or using a dedicated bridge.

## Current Automation-Stack Overview

Our automation-stack consists of several core components:

* **`freq-chat`**: Next.js‑based chat UI for end users citeturn1file0.
* **n8n**: Workflow orchestration platform for connecting services and APIs citeturn1file0.
* **FastAPI Controller**: Custom API bridge exposing `/execute` and `/notify` endpoints citeturn1file0.
* **Mem0**: Vector/graph memory service for persistent context citeturn1file0.
* **Traefik**: Reverse proxy for service routing and secure exposure citeturn1file0.

The `freqtrade` dev container provides algorithmic trading capabilities, backtesting, and FreqAI integration citeturn1file1. Core services are verified and configured as per our `03_Core_Services_Configuration_and_Verification.md` guide citeturn1file2. Cross‑stack interactions are orchestrated via n8n and the Controller, with Mem0 providing shared memory citeturn1file3.

## OpenRouter Configuration

To use OpenRouter's free models with Eko:

1. Get an API key from [OpenRouter.ai](https://openrouter.ai/)
2. Add to `.env`:
   ```bash
   OPENROUTER_API_KEY=your_key_here
   OPENROUTER_API_BASE=https://openrouter.ai/api/v1
   ```
3. Supported free models:
   - `tngtech/deepseek-r1t-chimera:free`
   - `deepseek/deepseek-r1:free` 
   - `deepseek/deepseek-prover-v2:free`
   - `meta-llama/llama-4-maverick:free`

## Eko Framework Overview

Eko is a **production-ready agent framework** that enables developers to:

* **Decompose natural‑language prompts** into executable workflows programmatically.
* **Blend code and language** via a JavaScript/TypeScript SDK.
* **Leverage built‑in tools** (e.g., web extraction, GUI automation, command execution) out of the box.
* **Implement hierarchical planning**: separate offline planning from runtime execution.
* **Use a hook system** for monitoring and intervention before/after steps.
* **Optimize web extraction** with VIEP, reducing HTML token usage by up to 99%.
* **Switch LLM providers** (ChatGPT, Claude, etc.) without reconfiguration ([fellou.ai](https://fellou.ai/eko/)).

## Integration Objectives

1. **Enable dynamic, LLM-driven task orchestration** within our stack.
2. **Reduce boilerplate** by auto‑generating multi-step workflows.
3. **Enhance reliability** via hierarchical planning and pre‑/post‑step hooks.
4. **Consolidate web and GUI automations** under Eko's tool suite.
5. **Maintain consistency** with existing APIs (Controller, n8n, Mem0).

## Architectural Integration Design

```mermaid
flowchart LR
  User[User via freq-chat]
  PythonController[FastAPI Controller (Python)]
  NodeEkoService[Eko Service (Node.js)]
  n8n[n8n Workflows]
  Mem0[Mem0 Service]
  Freqtrade[Freqtrade Dev Container]

  User -->|Chat Command| PythonController
  PythonController -->|HTTP Call| NodeEkoService
  NodeEkoService -->|Eko Execution| Mem0
  NodeEkoService -->|Eko Execution| Freqtrade
  NodeEkoService -->|Eko Execution| n8n
  NodeEkoService -->|Memory Ops (via Controller/n8n or Direct?) | Mem0
  n8n -->|API Calls| PythonController
  PythonController -->|Memory Ops| Mem0
  n8n -->|Memory Ops| Mem0
  PythonController -->|Trade Ops| Freqtrade

  %% Clarifications based on observed pattern and Eko docs:
  %% - Python Controller initiates Eko workflow by calling Node.js service.
  %% - Node.js Eko service performs Eko generation/execution.
  %% - Node.js Eko service might interact with Mem0, Freqtrade, or n8n directly OR
  %% - Node.js Eko service might return results to Python Controller for it to handle downstream interactions (Mem0/n8n/Freqtrade).
  %% - The current implementation in controller.py (Mem0 storage) suggests the latter for Mem0.
  %% - Simplified for diagram clarity, assuming Python Controller remains central orchestrator post-Eko execution.

  User -->|Chat Command| PythonController
  PythonController -->|HTTP Request with Prompt| NodeEkoService
  NodeEkoService -->|Eko Execution (using JS tools)|
  NodeEkoService -->|Results JSON| PythonController
  PythonController -->|Memory Storage| Mem0
  PythonController -->|Trigger Workflow| n8n
  n8n -->|API Calls| PythonController
  n8n -->|Memory Ops| Mem0 %% n8n can also talk to Mem0
  PythonController -->|Trade Ops| Freqtrade %% Python Controller can talk to Freqtrade API directly or via n8n
```
*   The **FastAPI Controller (Python)** acts as the primary gateway, receiving commands and orchestrating the workflow.
*   The **Eko Service (Node.js)** is a new component running the Eko JavaScript library. The Python Controller communicates with this service (e.g., via HTTP) to trigger Eko workflow generation and execution.
*   **Mem0**, **n8n**, and **Freqtrade** are interacted with by the Python Controller or potentially by the Node.js Eko Service, depending on the workflow step and tool implementation. The current Python Controller implementation assumes it handles Mem0 storage after getting results from the Node.js Eko service.

## Step-by-Step Integration Instructions

### 6.1 Prerequisites

* Node.js (>=16) and npm installed.
* Access to our `automation-stack` codebase.
* Valid API keys/config for LLM providers and Mem0.

### 6.2 Installing Eko SDK (Node.js)

Eko is a Node.js library. Install it in the directory where your Node.js Eko service will run (e.g., within the `controller/` directory if co-located).

```bash
cd automation-stack/controller # Or the directory of your Node.js Eko service
pnpm install @eko-ai/eko # Or npm install @eko-ai/eko
```

### 6.3 Integrating Eko via Node.js Service in FastAPI Controller

Eko is a JavaScript library and cannot be directly imported into Python. Instead, the Python FastAPI Controller will communicate with a separate Node.js service running Eko, typically via HTTP.

1.  **Create a Node.js Eko Service:** Set up a simple Node.js application (e.g., using Express.js) that initializes the Eko library and exposes an HTTP endpoint (e.g., `/run_eko`) to receive prompts, generate, and execute Eko workflows.

    *Example Conceptual `eko_service.js` (Node.js):*
    ```javascript
    import { Eko } from "@eko-ai/eko";
    import { loadTools } from "@eko-ai/eko/nodejs"; // Load environment-specific tools
    import express from 'express';
    import dotenv from 'dotenv';

    dotenv.config();

    // Initialize Eko and load tools
    Eko.tools = loadTools();
    const eko = new Eko({
      llm: process.env.EKO_LLM_PROVIDER || "claude", // e.g., "claude", "openai"
      apiKey: process.env.ANTHROPIC_API_KEY || process.env.OPENAI_API_KEY,
      modelName: process.env.EKO_MODEL_NAME || "claude-3-5-sonnet-20241022",
    });

    const app = express();
    const port = process.env.EKO_SERVICE_PORT || 3001;

    app.use(express.json());

    // Endpoint to run Eko workflows
    app.post('/run_eko', async (req, res) => {
      const { prompt } = req.body;
      if (!prompt) {
        return res.status(400).json({ error: 'Prompt is required' });
      }
      try {
        const workflow = await eko.generate(prompt);
        // const workflowJson = WorkflowParser.serialize(workflow); // Optional: to return plan JSON
        const result = await eko.execute(workflow);
        
        res.json({
          workflow_id: workflow.id, // Assuming workflow object has an id
          workflow_plan_json: JSON.stringify(workflow), // Sending plan JSON
          result: result
        });
      } catch (error) {
        console.error('Eko execution error:', error);
        res.status(500).json({ error: 'Failed to execute Eko workflow', details: error.message });
      }
    });

    app.listen(port, () => {
      console.log(`Eko Node.js service listening on port ${port}`);
    });
    ```

2.  **Update the FastAPI Controller (Python):** Modify `controller/controller.py` to make an HTTP POST request to the Node.js Eko service endpoint when `/api/v1/execute_eko` is called. Use `httpx` for the request.

    *Refer to the updated `controller/controller.py` for implementation details (specifically the `execute_eko` endpoint).* Ensure the `EKO_SERVICE_URL` environment variable is configured to point to your running Node.js Eko service (e.g., `http://localhost:3001/run_eko` or the Docker service name and port).

### 6.4 Embedding Eko into n8n Workflows

* **Custom HTTP Request**: Use an "HTTP Request" node to call `http://controller_mcp:8000/api/v1/execute_eko` with a JSON payload containing `{"prompt": "…"}`.
* **MCP Server Trigger**: Expose the above endpoint as a callable n8n tool.
* On response, parse `result` and pass to downstream nodes.

### 6.5 Configuring Eko Tools and Hooks (Node.js)

Custom tools and execution hooks for Eko are configured within the Node.js Eko service using the JavaScript SDK.

*   **Tool Configuration:** Register custom tools using `Eko.tools.register()` or similar methods provided by the JS SDK in your Node.js service's initialization.
    ```javascript
    import { Eko } from "@eko-ai/eko";
    import { loadTools } from "@eko-ai/eko/nodejs";
    
    // Load standard tools
    Eko.tools = loadTools();
    
    // Define and register a custom tool (example)
    const myCustomTool = {
      name: "myCustomPythonTool",
      description: "Calls a specific function in the Python controller.",
      inputSchema: { type: "object", properties: { param: { type: "string" } } },
      async run(input) {
        console.log(`Node.js tool executing myCustomPythonTool with input: ${JSON.stringify(input)}`);
        // Example: Make an HTTP call back to the Python controller if needed
        // const response = await fetch('http://controller_mcp:8000/api/my_python_function', { /* ... */ });
        return `Result from Node.js tool: ${input.param}`;
      }
    };
    Eko.tools.register(myCustomTool);
    
    const eko = new Eko({ /* ... */ });
    ```

*   **Hook Configuration:** Set up execution hooks (e.g., `beforeSubtask`, `afterToolUse`) during the Node.js Eko service initialization or before executing a specific workflow.
    ```javascript
    const result = await eko.execute(workflow, {
      hooks: {
        beforeSubtask: async (subtask, context) => {
          console.log(`Starting subtask: ${subtask.name}`);
          return true; // Proceed
        },
        afterToolUse: async (tool, context, output) => {
           console.log(`Finished tool ${tool.name} with output: ${JSON.stringify(output)}`);
        }
      }
    });
    ```

### 6.6 Integrating with Mem0 for Memory

* **Store workflow plans**: 
  ```python
  memory = Memory(url=os.getenv("MEM0_API_URL"))
  workflow_doc = workflow.to_json()
  memory.add(namespace="eko_plans", content=workflow_doc)
  ```
- **Retrieve and resume**: Query Mem0 by metadata to fetch and replay workflows.

### 6.7 Exposing Eko Workflows as MCP Tools
- In n8n, use the "MCP Server Trigger" node to expose selected Eko workflows.  
- Tools become callable by any AI or workflow agent via HTTP and can accept dynamic parameters.

### 6.8 Example: Web Interaction Automation (Conceptual)

This example illustrates how an Eko workflow, triggered via the Python controller and executed by the Node.js service, could perform a web scraping task.

*   **Python Controller receives prompt:** `POST /api/v1/execute_eko` with `{"prompt": "Scrape the latest price of BTC from coinmarketcap.com and store it in Mem0"}`.
*   **Python Controller calls Node.js Eko service:** Makes HTTP POST to `EKO_SERVICE_URL` with `{"prompt": "Scrape the latest price of BTC from coinmarketcap.com and store it in Mem0"}`.
*   **Node.js Eko Service:**
    *   Uses `eko.generate("Scrape the latest price...")` to create a workflow using its built-in web tools.
    *   Uses `eko.execute(workflow)` to run the steps (e.g., using `BrowserUse`, `ExtractContent`).
    *   Returns the result to the Python Controller.
*   **Python Controller:** Receives the result and stores it in Mem0 using the initialized Python `mem0_client`.

This flow demonstrates the separation of concerns: Python for orchestration and Mem0/Freqtrade interaction, and Node.js for Eko's core workflow execution and tool usage.

## Best Practices and Tips

* **Granular Prompts**: Break complex tasks into smaller prompts to improve workflow reliability.
* **Version Control**: Commit generated workflows JSON to Git for auditability.
* **Resource Limits**: Configure timeouts in Eko and n8n to prevent runaway executions.
* **Secure Hooks**: Validate inputs in hook callbacks to prevent injection.

## Testing and Verification

1. **Unit tests**: Write tests for `execute_eko` endpoint mocking Eko responses.
2. **Workflow tests**: Create sample n8n workflows calling Eko; verify expected node outputs.
3. **End-to-end**: From `freq-chat`, issue an automation command and trace through Controller → Eko → n8n → Mem0.

## Troubleshooting

* **SDK errors**: Check that your `ANTHROPIC_API_KEY` or equivalent is set and valid.
* **Workflow failures**: Inspect Controller logs and Eko hook logs.
* **Network issues**: Ensure `controller_mcp` and other services share `mcp-net`
