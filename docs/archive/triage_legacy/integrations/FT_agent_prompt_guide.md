# Freqtrade Integration: AI Agent Prompting Guide

This guide provides tips and examples for prompting an AI agent that has access to the Freqtrade integration documentation suite. These documents are intended to be placed in `freqtrade/user_data/docs/setup/` for an agent operating within the Freqtrade environment, or in `docs/integrations/` for an agent operating in the `automation-stack`.

The primary Freqtrade integration documents are:
*   `FT_int_guide.md` (Master Integration Guide)
*   `freqtrade_controller.md` (Controller Service Integration)
*   `freqtrade_n8n.md` (n8n Service Integration)
*   `freqtrade_mem0.md` (Mem0 Service Integration - Indirect)

## General Prompting Tips for Freqtrade Integration

1.  **Be Specific About Your Goal:** Clearly state what you want the agent to do or what information you need regarding Freqtrade integration.
    *   *Instead of:* "Tell me about Freqtrade."
    *   *Try:* "Explain how the FastAPI Controller authenticates with the Freqtrade API, referencing `freqtrade_controller.md`."

2.  **Reference Specific Documents:** When possible, guide the agent to the relevant document(s). This helps it focus its knowledge retrieval.
    *   "According to `FT_int_guide.md`, what are the primary methods for n8n to interact with Freqtrade?"
    *   "Using `freqtrade_n8n.md` as a reference, outline the steps for an n8n workflow to poll the Freqtrade API for new trades."

3.  **Ask About Configuration:**
    *   "What Freqtrade `user_data/config.json` settings are crucial for API integration, as per `FT_int_guide.md`?"
    *   "What environment variables does the FastAPI Controller need to connect to Freqtrade, based on `freqtrade_controller.md`?"

4.  **Inquire About Workflows and Processes:**
    *   "Describe the multi-agent orchestration pattern for Freqtrade tasks involving n8n, using `FT_int_guide.md` and `freqtrade_n8n.md`."
    *   "How can an n8n workflow execute a Freqtrade CLI command like backtesting, based on `freqtrade_n8n.md`?"

5.  **Troubleshooting Prompts:**
    *   "I'm getting a 401 Unauthorized error when my n8n workflow tries to call the Freqtrade API. What troubleshooting steps are suggested in `freqtrade_n8n.md` and `FT_int_guide.md`?"
    *   "The FastAPI Controller can't connect to Freqtrade. What should I check, according to `freqtrade_controller.md`?"

6.  **Clarify Service Roles:**
    *   "What is the role of the FastAPI Controller in Freqtrade integration, as detailed in `freqtrade_controller.md`?"
    *   "How does Mem0 support Freqtrade-related operations, according to `freqtrade_mem0.md`?"

## Example Prompts

### Understanding Architecture & Setup

*   "Summarize the dual-stack architecture for Freqtrade integration from `FT_int_guide.md`."
*   "What are the key Freqtrade-side configuration requirements for enabling API access, based on `FT_int_guide.md`?"
*   "Explain the network configuration needed for the `automation-stack` to communicate with the Freqtrade container, referencing `FT_int_guide.md`."

### Controller Integration

*   "Detail the Freqtrade API authentication flow handled by the FastAPI Controller, as per `freqtrade_controller.md`."
*   "What are the necessary environment variables for the Controller to integrate with Freqtrade, according to `freqtrade_controller.md`?"
*   "If the Controller fails to call a Freqtrade API endpoint, what troubleshooting steps does `freqtrade_controller.md` recommend?"

### n8n Integration

*   "Describe the recommended method for n8n to retrieve data from Freqtrade, based on `freqtrade_n8n.md`."
*   "How can an n8n workflow execute a Freqtrade CLI command for backtesting? Reference `freqtrade_n8n.md`."
*   "What n8n-side configurations are needed for Freqtrade API polling, as per `freqtrade_n8n.md` (e.g., credentials, `N8N_ALLOW_EXEC`)?"
*   "Explain the multi-agent orchestration pattern using n8n for Freqtrade tasks, referencing `freqtrade_n8n.md` and `FT_int_guide.md`."

### Mem0 Integration (Indirect)

*   "Clarify how Mem0 is involved with Freqtrade operations, using `freqtrade_mem0.md`. Does Freqtrade directly call Mem0?"
*   "Provide an example scenario from `freqtrade_mem0.md` where Mem0 stores results of a Freqtrade operation performed by n8n."

### Troubleshooting Specific Issues

*   "My n8n workflow's 'Execute Command' node is failing when trying to run a `freqtrade` command. What should I check based on the troubleshooting section in `freqtrade_n8n.md`?"
*   "Freqtrade API is returning 401 errors to the FastAPI Controller. What are the common causes and solutions listed in `freqtrade_controller.md` or `FT_int_guide.md`?"

## Using the Guides for Task Execution (Agent within Freqtrade Environment)

If you are an AI agent operating within the `freqtrade/user_data/` directory, these guides (once placed in `docs/setup/`) can help you:

*   **Configure Freqtrade for API access:**
    *   *Prompt:* "Using `FT_int_guide.md` (located in my `docs/setup/` directory), guide me through configuring `user_data/config.json` to enable the API server with username 'agent_user' and password 'secure_password_123'. Ensure you specify all necessary fields like `jwt_secret_key`."
*   **Verify Network Setup (Conceptual - agent cannot run `docker` commands directly):**
    *   *Prompt:* "Based on `FT_int_guide.md`, what Docker network should my Freqtrade container be on to allow the `automation-stack` (running externally) to access my API?"
*   **Understand how external services will interact with your Freqtrade instance:**
    *   *Prompt:* "If an external n8n workflow wants to poll my Freqtrade API for trades, what authentication method will it use, and what Freqtrade configuration is essential on my end? Refer to `FT_int_guide.md` and `freqtrade_n8n.md` in my `docs/setup/`."

By providing clear, context-aware prompts and referencing these specialized documents, you can leverage an AI agent more effectively for understanding, configuring, and troubleshooting Freqtrade integrations.
