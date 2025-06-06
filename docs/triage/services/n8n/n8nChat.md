Overview
n8nChat brings AI assistance directly into the n8n workflow editor, removing the need to manually assemble nodes or recall node parameters from memory 
Chrome Web Store
. By describing your desired automation in natural language, n8nChat generates complete workflows, configures individual nodes, and can even debug or refactor existing automations on the fly 
n8nchat.com
.

Key Features
AI-Powered Workflow Generation
Natural Language Input: Simply type what you want to automate—e.g., "Send a Slack message when a new row is added to Google Sheets"—and n8nChat constructs the necessary nodes and connections for you 
Chrome Web Store
Product Hunt
.

Complete Node Creation: Generates fully configured HTTP request nodes, authentication credentials, data transformations, and more, eliminating boilerplate setup 
Product Hunt
.

Multi-Model Support
OpenAI, Claude, Gemini & Grok: n8nChat supports multiple LLM backends so you can choose your preferred provider or compare outputs 
Reddit
.

Bring Your Own API Key: For privacy and cost control, n8nChat runs inference through your own API keys rather than sending data to a third-party server 
n8n Community
.

Context Awareness
Installed Nodes Recognition: Knows which nodes (including custom ones) you have installed and how to configure them correctly in your workflows 
Reddit
.

Workflow Context: Analyzes your current workflow state—previous nodes, data formats, credentials—to generate seamless additions or modifications 
Chrome Web Store
.

Workflow Editing & Debugging
Edit Existing Workflows: Ask n8nChat to "optimize this workflow" or "add error handling" and it will refactor nodes and add branches automatically 
Product Hunt
.

Debug Assistance: Describe unexpected behavior and get suggestions for fixes, including parameter adjustments and additional nodes for logging or retries 
Product Hunt
.

Chat Interface Integration
Side-Panel Chat: n8nChat runs as a sidebar within the n8n editor, so you can interact with it without leaving your development environment 
Reddit
.

Embedded & Hosted Modes: For public-facing automations, you can embed an n8n Chat widget on any website or use the hosted chat interface managed by n8n 
n8n Docs
.

Installation & Setup
Chrome: Install from the Chrome Web Store by searching for "n8nChat" or via the direct link 
Chrome Web Store
.

Firefox: Add to Firefox through Mozilla Add-ons by downloading "n8nChat by Cameron Wills" 
Add-ons for Firefox (en-US)
.

API Key Configuration: Upon first launch, enter your OpenAI or other LLM API key in the extension settings. No other credentials are stored externally 
n8n Community
.

Connect to n8n: Point the extension to your n8n instance URL (cloud or self-hosted), and you're ready to start chatting 
Chrome Web Store
.

### Advanced Configuration: Using Self-Hosted LLMs / Proxies

n8nChat can be configured to work with your local `automation-stack`, including the `openrouter_proxy_mcp`, allowing you to leverage a wide range of models via OpenRouter.

**Using `openrouter_proxy_mcp` with n8nChat:**

1.  **Ensure `openrouter_proxy_mcp` is Running:** Verify that your `openrouter_proxy_mcp` service is operational and accessible via `http://openrouter-proxy.localhost/v1` (or your configured host).
2.  **n8nChat Extension Settings:**
    *   Open the n8nChat browser extension's settings/options page.
    *   Look for a field related to "API Endpoint," "Base URL," or specifically "OpenAI Base URL."
    *   Enter: `http://openrouter-proxy.localhost/v1`
    *   For the API Key, you can typically enter any non-empty string (e.g., "dummykey" or "none"), as the actual `OPENROUTER_API_KEY` is injected by your proxy service. Refer to the n8nChat extension's specific instructions if it has strict API key format requirements.
3.  **Connect to Your n8n Instance:** Ensure n8nChat is also configured with the URL of your self-hosted n8n instance (e.g., `http://n8n.localhost`).

With this setup, when n8nChat generates workflows or uses its AI features that require an LLM, it will route requests through your `openrouter_proxy_mcp` service.

**Interacting with n8n Workflows Exposed as Tools (MCP):**

n8n now includes "MCP Server Trigger" and "MCP Client" nodes. This allows for more advanced AI agent setups:
*   **MCP Server Trigger:** You can create an n8n workflow that performs a specific task (e.g., interacting with Freqtrade, querying a database) and expose it as a "tool" using the MCP Server Trigger.
*   **n8nChat as a Client:** While direct integration details would depend on n8nChat's evolving capabilities, conceptually, an AI assistant like n8nChat could be directed to use tools exposed by your n8n MCP Server.
*   **Workflows Calling LLMs via Proxy:** Workflows created or modified by n8nChat can themselves contain HTTP Request nodes or the "MCP Client" node configured to use your `openrouter_proxy_mcp` for their own LLM calls (e.g., for data summarization within the workflow).

This combination allows n8nChat to not only build standard workflows but also to potentially orchestrate more complex automations that leverage both your local proxy for LLM access and specialized tools exposed by your n8n workflows.

Usage & Workflow
Generate New Workflow: Invoke n8nChat in the sidebar, describe the task, and hit "Generate." Review the auto-created workflow and click "Save" to import into n8n.

Modify Existing Workflows: Select a workflow in the editor, activate n8nChat, and request changes or debugging tips in real time.

Chat Widgets: Use the Chat Trigger node to expose your AI-powered workflows as web-chat interfaces for end users 
n8n Docs
.

Roadmap & Updates
Future Integrations: Planned support for on-premise LLMs and document-centric AI nodes for knowledge-base summarization.

Plugin Ecosystem: Community-developed plugins for additional AI platforms and custom UI components are in beta 
n8n Community
.

Comparisons
Feature	n8nChat	Traditional n8n
Workflow Generation	AI-driven from natural language	Manual node-by-node setup
Model Support	OpenAI, Claude, Gemini, Grok, etc.	N/A
Context Awareness	Full awareness of installed nodes & data	User must configure all context manually
Debugging Assistance	Automated suggestions	Manual troubleshooting via logs only
Deployment Flexibility	Sidebar + embedded/hosted chat widgets	Workflow export + manual embedding

Conclusion
n8nChat revolutionizes how you build and maintain automations in n8n by harnessing AI to eliminate repetitive tasks, reduce errors, and accelerate development. Whether you're a no-code user or a seasoned automation engineer, n8nChat's natural-language interface, multi-model support, and deep workflow integration will supercharge your productivity and help you scale solutions faster.


https://addons.mozilla.org/en-US/firefox/addon/n8nchat/?utm_source=chatgpt.com

https://n8nchat.com/?utm_source=chatgpt.com

https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-langchain.chattrigger/?utm_source=chatgpt.com

https://community.n8n.io/t/n8n-chat-custom-ui/80511?utm_source=chatgpt.com