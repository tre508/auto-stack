# Controller Service Tasklist

This document consolidates all Controller service-related documentation and tasks.

## Service Overview
Controller is the central FastAPI-based orchestration service component that acts as the programmable interface and gateway for AI agents and other services to perform actions across the automation stack.

---

## Key Service Functions

### API Gateway & Orchestration
- **Central API Server**: FastAPI-based service exposing RESTful endpoints
- **Service Orchestration**: Coordinates interactions between n8n, Mem0, Freqtrade, and other stack components
- **Task Execution**: Handles complex automation workflows and task delegation
- **Status Monitoring**: Provides health checks and status endpoints for stack services

### Core API Endpoints

#### Primary Endpoints
- **`POST /api/v1/execute`**: Central execution endpoint for triggering n8n workflows
  - Receives JSON payload and forwards to configured `N8N_WEBHOOK_URL`
  - Primary mechanism for external services to trigger n8n workflows via controller
- **`POST /api/v1/notify`**: Notification endpoint for receiving status updates
  - Allows n8n workflows and other services to send notifications to controller
  - Currently logs notifications with potential for future action triggers
- **`GET /api/v1/status`**: Health check and service status endpoint
- **`GET /docs`**: Auto-generated OpenAPI documentation (Swagger UI)

#### MCP Integration Endpoints
- **`/mcp/cursor/*`**: Model Context Protocol endpoints for Cursor IDE integration
  - Acts as gateway for Cursor to interact with Mem0 and other services
  - Handles memory operations (add, search, retrieve) via MCP format
  - Translates Cursor requests into appropriate service calls

#### Freqtrade Integration
- **Freqtrade API Proxy**: Endpoints for interacting with Freqtrade API
  - Handles JWT authentication with Freqtrade
  - Token management and renewal
  - Status, ping, and trading operation endpoints

### Service Integrations

#### n8n Integration
- **Webhook Forwarding**: `/execute` endpoint forwards payloads to n8n master webhook
- **Notification Handling**: Receives workflow completion status via `/notify`
- **HTTP Communication**: All communication via internal Docker network
- **Configuration**: Requires `N8N_WEBHOOK_URL` environment variable

#### Mem0 Integration
- **HTTP Client Integration**: Uses `httpx` for Mem0 API calls (not direct `mem0ai` package)
- **Memory Operations**: Add, search, and retrieve memories via Mem0 service API
- **MCP Gateway**: Exposes Mem0 functionality to Cursor via MCP endpoints
- **Configuration**: Requires `MEM0_API_URL` pointing to Mem0 service

#### Freqtrade Integration
- **API Communication**: HTTP requests to Freqtrade API endpoints
- **Authentication**: JWT token management for protected Freqtrade APIs
- **Operations**: Status checks, trade data, configuration management
- **Network Access**: Connects via Docker network to `freqtrade_devcontainer:8080`

#### EKO Integration
- **Node.js Service Proxy**: Calls EKO service via HTTP for AI agent workflows
- **Task Execution**: Routes AI agent requests to EKO service endpoint
- **Environment**: Requires `EKO_SERVICE_URL` configuration

## Configuration Requirements

### Environment Variables
- **`CONTROLLER_PORT`**: Service port (configurable, typically 5050 or 8000)
- **`N8N_WEBHOOK_URL`**: Master n8n webhook URL for forwarding execute requests
- **`MEM0_API_URL`**: Mem0 service endpoint (e.g., `http://mem0:8000`)
- **`EKO_SERVICE_URL`**: EKO service endpoint (e.g., `http://eko_service:3001`)
- **`FREQTRADE_API_URL`**: Freqtrade API base URL
- **`FREQTRADE_USERNAME`**: Freqtrade API authentication username
- **`FREQTRADE_PASSWORD`**: Freqtrade API authentication password

### Docker Configuration
- **Service Name**: `controller_mcp` (or `controller`)
- **Build Context**: `./controller` directory
- **Network**: `mcp-net` for internal service communication
- **Port Mapping**: Configurable via `CONTROLLER_PORT` environment variable
- **Dependencies**: `mem0`, `n8n_mcp`, and other stack services

### Dependencies
- **FastAPI**: Web framework for API endpoints
- **Uvicorn**: ASGI server for FastAPI application
- **httpx**: HTTP client for service-to-service communication
- **Pydantic**: Data validation and serialization

## Workflow Patterns

### n8n Workflow Triggering
1. External service/user calls `POST /api/v1/execute` with JSON payload
2. Controller receives request and validates payload
3. Controller forwards payload to configured `N8N_WEBHOOK_URL`
4. Target n8n workflow processes the payload and executes tasks
5. Optional: n8n workflow calls `POST /api/v1/notify` upon completion

### Mem0 Memory Operations
1. Cursor/external service calls MCP endpoint (e.g., `/mcp/cursor/add_memory`)
2. Controller translates MCP request to Mem0 API format
3. Controller makes HTTP request to Mem0 service
4. Controller translates Mem0 response back to MCP format
5. Response returned to calling service

### Freqtrade Operations
1. Service calls Freqtrade-related endpoint on controller
2. Controller handles JWT authentication with Freqtrade API
3. Controller makes authenticated request to Freqtrade
4. Controller processes and returns Freqtrade response

## Testing & Validation

### Health Checks
- **Controller Status**: `GET /api/v1/status`
- **Service Logs**: `docker logs controller_mcp`
- **OpenAPI Docs**: Access `/docs` endpoint for API documentation

### Integration Testing
- **n8n Communication**: Test `/execute` endpoint with sample payload
- **Mem0 Integration**: Test MCP endpoints for memory operations
- **Freqtrade API**: Test authentication and basic API calls
- **Network Connectivity**: Verify Docker network communication

### Service Connectivity
- **Internal Network**: Services accessible via Docker service names
- **External Access**: Available via Traefik routing (e.g., `http://controller.localhost`)
- **Port Configuration**: Verify correct port mapping and exposure

## Related Services
- **n8n**: Primary workflow automation service triggered by controller
- **Mem0**: Memory service accessed via controller MCP gateway
- **EKO**: AI agent service for complex reasoning tasks
- **freq-chat**: Chat interface that calls controller API endpoints
- **Freqtrade**: Trading bot accessed via controller proxy

## Cross-References
- [n8n Webhook Integration Guide](../../n8n/webhookFlows.md)
- [n8n Service Documentation](../n8n/Tasklist.md)
- [Mem0 Service Documentation](../mem0/Tasklist.md)
- [EKO Service Documentation](../eko/Tasklist.md)
- [freq-chat Service Documentation](../freq-chat/Tasklist.md)
- [Freqtrade Integration Checklist](../../setup/Freqtrade_Project_Checklist.md)
