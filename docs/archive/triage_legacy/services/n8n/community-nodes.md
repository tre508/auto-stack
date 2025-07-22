# n8n Community Nodes: Integration & Usage Summary

---

## 1. n8n-nodes-neo4j
**Repository:** [GitHub](https://github.com/Kurea/n8n-nodes-neo4j)  
**NPM:** [n8n-nodes-neo4j](https://www.npmjs.com/package/n8n-nodes-neo4j)

### Overview
Provides nodes for connecting n8n workflows to Neo4j graph databases. Enables running Cypher queries, reading/writing nodes and relationships, and automating graph data flows.

### Installation
```bash
npm install n8n-nodes-neo4j
```
- Restart n8n after installation.

### Configuration
- Add Neo4j credentials (bolt URL, username, password).
- Configure node to run Cypher queries or trigger on graph events.

### Supported Operations
- Execute Cypher queries (read/write)
- Trigger workflows on graph changes (if supported by node version)

### Best Practices & Caveats
- Ensure Neo4j is accessible from the n8n instance.
- Use parameterized queries for security.
- Some versions may lack advanced triggers or error handling—test thoroughly.

---

## 2. n8n-nodes-mcp (MCP Client Node)
**Repository:** [GitHub](https://github.com/nerding-io/n8n-nodes-mcp)  
**NPM:** [n8n-nodes-mcp](https://www.npmjs.com/package/n8n-nodes-mcp)

### Overview
Lets n8n interact with Model Context Protocol (MCP) servers, enabling workflows to access AI tools, resources, and prompts via MCP. Supports both STDIO and SSE transports.

### Installation
```bash
npm install n8n-nodes-mcp
```
- Set `N8N_COMMUNITY_PACKAGES_ALLOW_TOOL_USAGE=true` in your environment (required for tool usage in AI Agent nodes).
- Restart n8n after installation.

### Configuration
- Add MCP Client credentials:
  - **STDIO:** Command, arguments, environment variables for MCP server
  - **SSE:** SSE URL, optional headers
- Configure node for operations: Execute Tool, List Tools, List Prompts, etc.

### Supported Operations
- Execute Tool (with parameters)
- List Tools
- List Prompts
- Read Resource
- Get Prompt

### Best Practices & Caveats
- For Docker: pass MCP environment variables via `docker-compose.yml`.
- Ensure MCP servers are reachable and compatible (v1.0+).
- Node must be enabled as a tool for AI Agent workflows.
- Some MCP nodes (e.g., n8n-nodes-langchain) are known to have compatibility issues—prefer n8n-nodes-mcp for MCP integration.

---

## 3. n8n-nodes-chatwoot
**Repository:** [GitHub](https://github.com/sufficit/n8n-nodes-chatwoot)  
**NPM:** [n8n-nodes-chatwoot](https://www.npmjs.com/package/n8n-nodes-chatwoot)

### Overview
Integrates Chatwoot (open-source customer engagement platform) with n8n workflows. Enables sending/receiving messages, managing contacts, and automating support flows.

### Installation
```bash
npm install n8n-nodes-chatwoot
```
- Restart n8n after installation.

### Configuration
- Add Chatwoot API credentials (API key, account URL).
- Configure node for desired operation (send message, fetch conversations, etc).

### Supported Operations
- Send message
- Fetch conversations
- Manage contacts

### Best Practices & Caveats
- Ensure API credentials have correct permissions.
- Test with a staging Chatwoot instance before production use.
- Node is tested on n8n > v0.210; check compatibility with your version.

---

**Note:** Always review the latest documentation and GitHub issues for each node before production deployment. Community nodes may have breaking changes or require manual updates after n8n upgrades.