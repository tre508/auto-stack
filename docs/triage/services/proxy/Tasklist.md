# Proxy Service Tasklist

This document consolidates all Proxy service-related documentation and tasks.

## Service Overview
Proxy is an optional service component that handles API routing, authentication, and load balancing for external API providers in the automation stack. Currently, the main proxy implementation is the OpenRouter proxy for LLM API access.

---

## Key Service Functions

### API Gateway & Routing
- **OpenRouter Proxy**: Routes LLM requests to OpenRouter.ai API
- **Authentication Management**: Handles API key authentication for external services
- **Load Balancing**: Distributes requests across multiple API endpoints
- **Rate Limiting**: Manages API rate limits and quotas

### Service Implementations

#### OpenRouter Proxy (`openrouter_proxy_mcp`)
- **Purpose**: Provides unified interface to OpenRouter.ai's model marketplace
- **Location**: `openrouter_proxy/` directory
- **Technology**: Node.js/Express.js service
- **Port**: Configurable (typically 3001)

## Configuration Requirements

### Environment Variables
- **`OPENROUTER_API_KEY`**: API key for OpenRouter.ai access
- **`OPENROUTER_API_BASE`**: Base URL for OpenRouter API (typically `https://openrouter.ai/api/v1`)
- **`PROXY_PORT`**: Service port configuration
- **`ALLOWED_ORIGINS`**: CORS configuration for allowed origins

### Docker Configuration
- **Service Name**: `openrouter_proxy_mcp`
- **Build Context**: `./openrouter_proxy` directory
- **Network**: `mcp-net` for internal service communication
- **Port Mapping**: Maps internal port to configurable host port

### Dependencies
- **Express.js**: Web framework for proxy service
- **HTTP Proxy Middleware**: For request forwarding
- **CORS**: Cross-origin resource sharing handling

## Service Integrations

### n8n Integration
- **HTTP Request Nodes**: n8n workflows can use proxy for LLM API calls
- **Model Access**: Provides access to wide range of OpenRouter models
- **Configuration**: n8n HTTP Request nodes configured to use proxy endpoint

### freq-chat Integration
- **LLM Provider**: freq-chat can route LLM requests through proxy
- **Model Selection**: Access to multiple model providers via single endpoint
- **Environment Configuration**: `OPENROUTER_API_BASE` points to proxy service

### Controller Integration
- **API Proxy**: Controller can use proxy for LLM operations
- **Service Discovery**: Controller configured with proxy endpoint URL
- **Authentication**: Proxy handles external API authentication

## API Endpoints

### OpenRouter Proxy
- **`/v1/chat/completions`**: Chat completion endpoint compatible with OpenAI API
- **`/v1/models`**: List available models from OpenRouter
- **`/health`**: Health check endpoint
- **`/status`**: Service status and configuration

## Testing & Validation

### Health Checks
- **Proxy Status**: `GET /health` or `/status` endpoint
- **Service Logs**: `docker logs openrouter_proxy_mcp`
- **API Connectivity**: Test external API access through proxy

### Integration Testing
- **Model List**: Test `/v1/models` endpoint for available models
- **Chat Completion**: Test `/v1/chat/completions` with sample request
- **Authentication**: Verify API key handling and forwarding
- **CORS**: Test cross-origin requests if applicable

### Service Connectivity
- **Internal Network**: Accessible via Docker service name
- **External Access**: May be exposed via Traefik routing
- **Port Configuration**: Verify correct port mapping

## Monitoring & Logging

### Request Logging
- **Access Logs**: Log all incoming requests with timestamps
- **Error Logging**: Log failed requests and error details
- **Rate Limit Monitoring**: Track rate limit usage and remaining quotas

### Performance Metrics
- **Response Times**: Monitor proxy response latency
- **Success Rates**: Track successful vs failed requests
- **Usage Statistics**: Monitor API usage patterns and costs

## Security Considerations

### API Key Management
- **Environment Variables**: Store API keys securely in environment variables
- **No Logging**: Ensure API keys are not logged in request/response logs
- **Rotation**: Support for API key rotation without service restart

### Access Control
- **CORS Configuration**: Properly configure allowed origins
- **Rate Limiting**: Implement client-side rate limiting if needed
- **Request Validation**: Validate incoming requests before forwarding

## Related Services
- **n8n**: Uses proxy for LLM API calls in workflows
- **freq-chat**: May route LLM requests through proxy for model diversity
- **Controller**: Uses proxy for LLM operations when needed
- **External APIs**: OpenRouter.ai and other LLM providers

## Cross-References
- [n8n Service Documentation](../n8n/Tasklist.md)
- [freq-chat Service Documentation](../freq-chat/Tasklist.md)
- [Controller Service Documentation](../controller/Tasklist.md)
- [OpenRouter Proxy Documentation](../../deprecated/proxy.md) (if exists)
