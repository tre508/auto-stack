# n8n MCP Client Tool Configuration Guide
*Connecting to Docker MCP Servers from Cursor*

## Overview

This guide explains how to configure n8n's **MCP Client Tool node** to connect to the same Docker MCP servers currently running in your Cursor IDE setup. The key difference is that n8n requires **SSE (Server-Sent Events) endpoints** rather than the direct command-line interface that Cursor uses.

## Understanding the Architecture Difference

### Cursor MCP Configuration (Current Setup)
- **Transport**: stdio (command-line interface)
- **Method**: Direct Docker container execution with `--rm` flag
- **Connection**: `docker run --rm -i mcp/server-name`

### n8n MCP Client Tool Requirements  
- **Transport**: SSE (Server-Sent Events) over HTTP
- **Method**: HTTP endpoints that expose MCP server tools
- **Connection**: `http://localhost:port/mcp` or `https://server.com/sse`

## Current Docker MCP Servers in Cursor

From your `.cursor/mcp.json` configuration:

```json
{
  "mcpServers": {
    "desktop-commander": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "--network", "host", "--cap-add", "SYS_PTRACE", 
               "-v", "/home/gleshen:/home/gleshen", "-v", "/tmp:/tmp", "mcp/desktop-commander"]
    },
    "fetch": {
      "command": "docker", 
      "args": ["run", "--rm", "-i", "mcp/fetch"]
    },
    "puppeteer": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "mcp/puppeteer"]
    },
    "sequential-thinking": {
      "command": "docker", 
      "args": ["run", "--rm", "-i", "mcp/sequentialthinking"]
    },
    "time": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "mcp/time"]
    },
    "memory": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "mcp/memory"]
    }
  }
}
```

## Required Modifications for n8n Integration

### Step 1: Create Persistent HTTP MCP Server Containers

Instead of ephemeral `--rm` containers, we need persistent containers with HTTP endpoints:

```bash
# Stop any existing MCP containers
docker stop $(docker ps -q --filter "ancestor=mcp/fetch") 2>/dev/null || true
docker stop $(docker ps -q --filter "ancestor=mcp/puppeteer") 2>/dev/null || true
docker stop $(docker ps -q --filter "ancestor=mcp/desktop-commander") 2>/dev/null || true

# Create persistent MCP servers with HTTP endpoints
docker run -d --name mcp-fetch-sse \
  -p 8081:8080 \
  --restart unless-stopped \
  mcp/fetch --transport sse --port 8080

docker run -d --name mcp-puppeteer-sse \
  -p 8082:8080 \
  --restart unless-stopped \
  mcp/puppeteer --transport sse --port 8080

docker run -d --name mcp-desktop-commander-sse \
  -p 8083:8080 \
  --network host \
  --cap-add SYS_PTRACE \
  -v "/home/gleshen:/home/gleshen" \
  -v "/tmp:/tmp" \
  --restart unless-stopped \
  mcp/desktop-commander --transport sse --port 8080

docker run -d --name mcp-time-sse \
  -p 8084:8080 \
  --restart unless-stopped \
  mcp/time --transport sse --port 8080

docker run -d --name mcp-memory-sse \
  -p 8085:8080 \
  --restart unless-stopped \
  mcp/memory --transport sse --port 8080

docker run -d --name mcp-sequential-thinking-sse \
  -p 8086:8080 \
  --restart unless-stopped \
  mcp/sequentialthinking --transport sse --port 8080
```

### Step 2: Verify HTTP Endpoints

Test that SSE endpoints are accessible:

```bash
# Test each MCP server endpoint
curl http://localhost:8081/mcp  # fetch
curl http://localhost:8082/mcp  # puppeteer  
curl http://localhost:8083/mcp  # desktop-commander
curl http://localhost:8084/mcp  # time
curl http://localhost:8085/mcp  # memory
curl http://localhost:8086/mcp  # sequential-thinking
```

Expected response should include MCP protocol information and available tools.

## n8n MCP Client Tool Configuration

### Node Parameters for Each MCP Server

#### 1. Fetch MCP Server
- **SSE Endpoint**: `http://localhost:8081/mcp`
- **Authentication**: None
- **Tools to Include**: All

#### 2. Puppeteer MCP Server  
- **SSE Endpoint**: `http://localhost:8082/mcp`
- **Authentication**: None
- **Tools to Include**: All

#### 3. Desktop Commander MCP Server
- **SSE Endpoint**: `http://localhost:8083/mcp`
- **Authentication**: None  
- **Tools to Include**: All
- **Note**: Requires host network access for file operations

#### 4. Time MCP Server
- **SSE Endpoint**: `http://localhost:8084/mcp`
- **Authentication**: None
- **Tools to Include**: All

#### 5. Memory MCP Server
- **SSE Endpoint**: `http://localhost:8085/mcp`
- **Authentication**: None
- **Tools to Include**: All

#### 6. Sequential Thinking MCP Server
- **SSE Endpoint**: `http://localhost:8086/mcp`
- **Authentication**: None
- **Tools to Include**: All

## n8n Workflow Configuration

### Community Package Installation

First, install the MCP client node package:

```bash
# Enable community node tool usage
export N8N_COMMUNITY_PACKAGES_ALLOW_TOOL_USAGE=true

# Install the MCP client node (if using community package)
npm install n8n-nodes-mcp
```

### Environment Variables for n8n

Add to your n8n environment configuration:

```env
# Enable community nodes as AI Agent tools
N8N_COMMUNITY_PACKAGES_ALLOW_TOOL_USAGE=true

# Optional: Add any required API keys for MCP servers
MCP_FETCH_API_KEY=your-api-key-if-needed
MCP_PUPPETEER_API_KEY=your-api-key-if-needed
```

### Docker Compose Configuration for n8n

```yaml
version: '3.8'

services:
  n8n:
    image: n8nio/n8n:latest
    ports:
      - "5678:5678"
    environment:
      - N8N_COMMUNITY_PACKAGES_ALLOW_TOOL_USAGE=true
      - N8N_HOST=0.0.0.0
      - N8N_PORT=5678
      - N8N_PROTOCOL=http
    volumes:
      - ~/.n8n:/home/node/.n8n
      - /var/run/docker.sock:/var/run/docker.sock  # For Docker access
    networks:
      - n8n-network
    depends_on:
      - mcp-fetch
      - mcp-puppeteer
      - mcp-desktop-commander

  # MCP Server containers with SSE endpoints
  mcp-fetch:
    image: mcp/fetch
    ports:
      - "8081:8080"
    command: ["--transport", "sse", "--port", "8080"]
    restart: unless-stopped
    networks:
      - n8n-network

  mcp-puppeteer:
    image: mcp/puppeteer  
    ports:
      - "8082:8080"
    command: ["--transport", "sse", "--port", "8080"]
    restart: unless-stopped
    networks:
      - n8n-network

  mcp-desktop-commander:
    image: mcp/desktop-commander
    ports:
      - "8083:8080"
    command: ["--transport", "sse", "--port", "8080"] 
    volumes:
      - "/home/gleshen:/home/gleshen"
      - "/tmp:/tmp"
    cap_add:
      - SYS_PTRACE
    network_mode: host
    restart: unless-stopped

networks:
  n8n-network:
    driver: bridge
```

## Authentication Configuration

### No Authentication Required (Default)
Most Docker MCP servers don't require authentication for local development:

```
Authentication: None
```

### Bearer Token (If Required)
If your MCP servers are configured with API key authentication:

```
Authentication: Bearer Token
Token: your-api-key-here
```

### Custom Headers (Advanced)
For custom authentication schemes:

```
Authentication: Generic Header
Header Name: X-API-Key
Header Value: your-api-key-here
```

## Troubleshooting

### Common Issues

#### 1. "SSE Endpoint Not Accessible"
**Symptoms**: Connection timeout or 404 error
**Solution**:
```bash
# Check if containers are running
docker ps | grep mcp

# Check container logs
docker logs mcp-fetch-sse

# Test endpoint directly
curl -v http://localhost:8081/mcp
```

#### 2. "No Tools Available" 
**Symptoms**: MCP Client Tool shows 0 tools
**Solution**:
```bash
# Verify MCP server is responding correctly
curl -H "Accept: text/event-stream" http://localhost:8081/mcp

# Check if server supports SSE transport
docker exec mcp-fetch-sse /app/server --help
```

#### 3. "Desktop Commander File Access Denied"
**Symptoms**: File operations fail with permission errors  
**Solution**:
```bash
# Ensure proper volume mounts and permissions
docker run --rm -v "/home/gleshen:/home/gleshen" mcp/desktop-commander ls -la /home/gleshen
```

#### 4. "Port Conflicts"
**Symptoms**: Cannot bind to port 8081-8086
**Solution**:
```bash
# Check what's using the ports
netstat -tlnp | grep :808

# Stop conflicting services or use different ports
docker run -p 9081:8080 mcp/fetch --transport sse --port 8080
```

### Verification Commands

```bash
# Check all MCP server endpoints
for port in 8081 8082 8083 8084 8085 8086; do
  echo "Testing port $port:"
  curl -s http://localhost:$port/mcp | head -3
  echo "---"
done

# List all running MCP containers
docker ps --filter "name=mcp-*-sse" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Check n8n can access the network
docker exec n8n-container curl http://mcp-fetch:8080/mcp
```
## Security Considerations

### Network Isolation
- Use Docker networks to isolate MCP servers
- Only expose necessary ports to host system
- Consider using reverse proxy for production

### Authentication
- Enable authentication for production deployments
- Use environment variables for API keys
- Implement rate limiting on MCP endpoints

### File System Access
- Limit Desktop Commander volume mounts to necessary directories (ie ~/projects/*)
- Use read-only mounts where possible
- Monitor file system access logs

## Integration Examples

### Basic n8n Workflow with MCP Tools

1. **HTTP Request Trigger** → Starts workflow
2. **MCP Client Tool (Fetch)** → Scrapes web content  
3. **MCP Client Tool (Memory)** → Stores information
4. **MCP Client Tool (Desktop Commander)** → Saves to file
5. **HTTP Response** → Returns result

### AI Agent Configuration

```json
{
  "aiAgent": {
    "model": "gpt-4",
    "tools": [
      {
        "type": "mcp-client",
        "endpoint": "http://localhost:8081/mcp",
        "name": "web-fetch"
      },
      {
        "type": "mcp-client", 
        "endpoint": "http://localhost:8082/mcp",
        "name": "browser-automation"
      }
    ]
  }
}
```

## Maintaining Consistency with Cursor

To keep both n8n and Cursor MCP servers synchronized:

### Dual Configuration Script

```bash
#!/bin/bash
# deploy-mcp-servers.sh

# Start SSE servers for n8n
docker-compose -f docker-compose-mcp.yml up -d

# Verify Cursor MCP still works with stdio
npx @modelcontextprotocol/inspector stdio docker run --rm -i mcp/fetch

echo "Both n8n SSE and Cursor stdio MCP servers are now running"
```

### Monitoring Script

```bash
#!/bin/bash
# check-mcp-health.sh

echo "=== Cursor MCP Health (stdio) ==="
for server in fetch puppeteer desktop-commander; do
  echo "Testing $server..."
  timeout 5 docker run --rm -i mcp/$server --version || echo "FAILED"
done

echo "=== n8n MCP Health (SSE) ==="
for port in 8081 8082 8083 8084 8085 8086; do
  echo "Testing port $port..."
  curl -m 5 -s http://localhost:$port/mcp >/dev/null && echo "OK" || echo "FAILED"
done
```

## Context7 MCP Server Integration

### Special Case: Context7 Documentation Server

Your Context7 server is already running with HTTP transport, making it n8n-compatible:

```bash
# Context7 is already running at:
http://localhost:8080/mcp

# n8n Configuration:
# SSE Endpoint: http://localhost:8080/mcp
# Authentication: None
# Tools to Include: All (Documentation search and retrieval)
```

## Manual Tasks Required

⚠️ **The following tasks require manual intervention and cannot be automated:**

### 1. **Docker Image Compatibility Verification**
**You must manually check:**
- Whether MCP Docker images support `--transport sse` flag
- If SSE endpoints are properly implemented in each image
- Test each container with SSE transport before configuring n8n

```bash
# Test if images support SSE transport
docker run --rm mcp/fetch --help | grep -i sse
docker run --rm mcp/puppeteer --help | grep -i transport
```

### 2. **Network Configuration**
**Manual setup required:**
- Configure firewall rules for ports 8081-8086
- Set up reverse proxy if accessing from external networks
- Configure Docker Desktop networking for host access

### 3. **n8n Installation and Setup**
**You must manually:**
- Install n8n on your system or via Docker
- Configure n8n environment variables
- Install community MCP node packages
- Set up n8n authentication and security

### 4. **Authentication Token Management**
**Security tasks:**
- Generate API keys for MCP servers (if required)
- Configure bearer tokens or custom headers
- Set up secure storage for authentication credentials

### 5. **Production Deployment**
**System administration tasks:**
- Configure SSL/TLS certificates for HTTPS endpoints
- Set up monitoring and logging for MCP servers
- Implement backup and recovery procedures
- Configure resource limits and scaling

## Alternative Implementation: MCP Bridge Service

If direct SSE support is not available in the Docker MCP images, create a bridge service:

### Bridge Service Implementation

```javascript
// mcp-bridge-server.js
const express = require('express');
const { spawn } = require('child_process');
const app = express();

// Bridge stdio MCP to SSE
app.get('/mcp/:server', (req, res) => {
  const serverName = req.params.server;
  
  res.writeHead(200, {
    'Content-Type': 'text/event-stream',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Access-Control-Allow-Origin': '*'
  });

  // Spawn MCP server container
  const mcpProcess = spawn('docker', [
    'run', '--rm', '-i', `mcp/${serverName}`
  ]);

  // Bridge stdio to SSE
  mcpProcess.stdout.on('data', (data) => {
    res.write(`data: ${data}\n\n`);
  });

  mcpProcess.on('close', () => {
    res.end();
  });

  req.on('close', () => {
    mcpProcess.kill();
  });
});

app.listen(8080, () => {
  console.log('MCP Bridge Server running on port 8080');
});
```

### Bridge Service Docker Configuration

```dockerfile
# Dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package.json mcp-bridge-server.js ./
RUN npm install express
EXPOSE 8080
CMD ["node", "mcp-bridge-server.js"]
```

```bash
# Build and run bridge service
docker build -t mcp-bridge .
docker run -d -p 8080:8080 -v /var/run/docker.sock:/var/run/docker.sock mcp-bridge
```

## References and Documentation

### External Resources
- **n8n MCP Client Tool Documentation**: [n8n Docs](https://docs.n8n.io/integrations/builtin/cluster-nodes/sub-nodes/n8n-nodes-langchain.toolmcp/)
- **Model Context Protocol Specification**: [MCP Spec](https://modelcontextprotocol.io/)
- **Docker MCP Server Images**: [Docker Hub](https://hub.docker.com/u/mcp)
- **MCP Client CLI Examples**: [GitHub](https://github.com/adhikasp/mcp-client-cli)

### Your Current Documentation
- **Cursor MCP Setup**: `docs/MCP/Cursor_MCP_Setup_Guide.md`
- **Docker Troubleshooting**: `docs/MCP/Docker_MCP_Troubleshooting.md`
- **MCP Status Report**: `docs/MCP/MCP_Troubleshooting_Status.md`
- **Desktop Commander Testing**: `docs/MCP/Desktop_Commander_Test_Protocol.md`

### Your Current Configuration
- **Cursor MCP Config**: `/home/gleshen/.cursor/mcp.json`
- **System Info**: `system-info-20250623-0735/`
- **Docker Configuration**: `docs/MCP/Docker-info.md`

---

## Summary

This guide provides a complete pathway to configure n8n's MCP Client Tool to connect to your existing Docker MCP servers. The key difference is the transport layer:

- **Cursor uses stdio transport** (direct command execution)
- **n8n requires SSE transport** (HTTP Server-Sent Events)

The solution involves either:
1. **Running MCP servers with SSE transport** (if supported)
2. **Creating a bridge service** to convert stdio to SSE
3. **Using the existing Context7 server** (already HTTP-compatible)

**Next Steps:**
1. Test Docker MCP images for SSE support
2. Deploy persistent MCP containers with HTTP endpoints
3. Configure n8n MCP Client Tool nodes with the provided endpoints
4. Test integration and troubleshoot as needed

*Configuration Guide Created: January 2025*  
*Compatible with: n8n v1.x, Docker MCP Toolkit, Cursor IDE*  
*Status: Ready for implementation*  
*Based on research from: fetch, puppeteer, and context7 MCP servers*