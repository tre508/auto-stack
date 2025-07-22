# n8n MCP Integration Documentation

This directory contains comprehensive documentation and tools for integrating your existing Cursor MCP servers with n8n's MCP Client Tool nodes.

## Files Overview

### 📖 Documentation
- **`n8n_MCP_Client_Configuration_Guide.md`** - Complete configuration guide for n8n MCP Client Tool
- **`README.md`** - This overview file

### 🐳 Docker Configuration  
- **`docker-compose-mcp-n8n.yml`** - Docker Compose file for SSE-compatible MCP servers

### 🚀 Setup Scripts
- **`setup-n8n-mcp-integration.sh`** - Automated setup script for n8n MCP integration

## Quick Start

### 1. Run the Setup Script
```bash
cd /home/gleshen/projects/troubleshoot/docs/triage/services/n8n
./setup-n8n-mcp-integration.sh
```

### 2. Access n8n
- Open http://localhost:5678 in your browser
- Install the community MCP node package: `n8n-nodes-mcp`

### 3. Configure MCP Client Tool Nodes
Use these endpoints in your n8n MCP Client Tool nodes:

| MCP Server | SSE Endpoint | Authentication |
|------------|--------------|----------------|
| **Fetch** | `http://localhost:8081/mcp` | None |
| **Puppeteer** | `http://localhost:8082/mcp` | None |
| **Desktop Commander** | `http://localhost:8083/mcp` | None |
| **Time** | `http://localhost:8084/mcp` | None |
| **Memory** | `http://localhost:8085/mcp` | None |
| **Sequential Thinking** | `http://localhost:8086/mcp` | None |

## Key Features

- **SSE Transport**: n8n requires Server-Sent Events endpoints
- **Dual Compatibility**: Works alongside your existing Cursor MCP setup
- **Persistent Containers**: Long-running MCP servers for n8n integration
- **No Authentication**: Ready for local development

## Research Sources

Created using fetch, context7, and puppeteer MCP servers to analyze n8n documentation.

---
*Created: January 2025* 