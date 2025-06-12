# Cross-Service Integration Prompts

This directory contains prompts and templates for integrating services across the Automation Stack.

## Purpose

Integration prompts facilitate seamless communication and data flow between:

- **Controller ↔ n8n**: Workflow orchestration and command execution
- **Controller ↔ Freqtrade**: Trading strategy automation and API integration  
- **n8n ↔ Freqtrade**: Direct workflow-to-trading automation
- **Mem0 ↔ All Services**: Memory persistence and retrieval
- **Vercel AI Chat ↔ Stack**: Frontend integration and user interaction

## Integration Patterns

### API Authentication
```bash
# Freqtrade API authentication pattern
curl -u freqtrader:SuperSecurePassword -X POST http://freqtrade_devcontainer:8080/api/v1/token/login

# Use returned JWT for subsequent requests
curl -H "Authorization: Bearer <access_token>" http://freqtrade_devcontainer:8080/api/v1/status
```

### Cross-Container Communication
```bash
# Network connectivity testing
docker network inspect auto-stack-net
ping -c 2 controller_auto
ping -c 2 n8n_auto
```

### Webhook Integration
```json
{
  "trigger": "webhook",
  "method": "POST", 
  "endpoint": "/api/v1/execute",
  "auth": "jwt",
  "payload": {
    "command": "string",
    "parameters": "object"
  }
}
```

## Service-Specific Integration

### Controller Integration
- Exposes Flask endpoints under `/cmd/*`
- Logs all inbound requests
- Validates incoming `chatInput`
- Emits `status` pings every 2s during processing

### n8n Integration  
- Uses HTTP Request nodes for service communication
- Implements webhook triggers for external integration
- Provides structured JSON responses
- Integrates with unified logging via Postgres nodes

### Freqtrade Integration
- API-first integration with JWT authentication
- Docker container communication via service names
- CLI command execution for backtesting and optimization
- Strategy file analysis and parameter extraction

### Mem0 Integration
- Memory persistence across service interactions
- Context retrieval for enhanced decision making
- Cross-session state management
- Integration with AI chat interfaces

## Best Practices

### Error Handling
- Always include try-catch blocks in integration code
- Log integration failures with context
- Implement retry logic with exponential backoff
- Provide meaningful error messages for debugging

### Authentication
- Use environment variables for credentials
- Implement token refresh mechanisms
- Validate authentication before processing requests
- Log authentication attempts and failures

### Data Format Standardization
```json
{
  "status": "success|error|pending",
  "message": "Human readable description",
  "data": "Response payload",
  "timestamp": "ISO 8601 timestamp",
  "service": "originating service name"
}
```

### Network Configuration
- Services communicate via Docker network `auto-stack-net`
- Use service names for internal communication
- External endpoints exposed via Traefik proxy
- Health checks implemented for all services

## Troubleshooting Integration Issues

### Common Problems
1. **Network connectivity**: Check Docker network configuration
2. **Authentication failures**: Verify credentials and token validity
3. **Service unavailability**: Check container status and logs
4. **Data format mismatches**: Validate JSON schema compliance

### Diagnostic Commands
```bash
# Check service health
curl -f http://controller_auto:5050/health
curl -f http://n8n_auto:5678/healthz

# Verify network connectivity
docker exec n8n_auto ping -c 2 controller_auto
docker exec controller_auto ping -c 2 freqtrade_devcontainer

# Check service logs
docker logs controller_auto --tail 50
docker logs n8n_auto --tail 50
```

## Integration Testing

### Test Scenarios
1. **End-to-end workflow**: User request → AI Chat → Controller → n8n → Freqtrade → Response
2. **Memory persistence**: Store context in Mem0 → Retrieve in subsequent interactions
3. **Error propagation**: Service failure → Error handling → User notification
4. **Authentication flow**: Token generation → Service access → Token refresh

### Validation Steps
1. Verify service-to-service communication
2. Test authentication mechanisms
3. Validate data format consistency
4. Check error handling and logging
5. Confirm response time requirements

## Maintenance Guidelines

1. **Documentation**: Keep integration patterns up-to-date
2. **Monitoring**: Set up alerts for integration failures
3. **Testing**: Regular integration test execution
4. **Versioning**: Track API changes across services
5. **Security**: Regular credential rotation and access review
