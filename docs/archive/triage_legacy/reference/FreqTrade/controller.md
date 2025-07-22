# 🎮 Controller API Integration

## Overview

The Controller service provides a REST API interface for managing Freqtrade operations. It handles command execution, status monitoring, and integration with other services in the automation stack.

## API Endpoints

### Status & Health

```
GET /api/v1/status
```

Returns the current status of Freqtrade and Controller service.

### Command Execution

```
POST /api/v1/execute
Content-Type: application/json

{
    "command": "backtest",
    "strategy": "MyStrategy",
    "timerange": "20230101-20240101"
}
```

Supported commands:

- `backtest`: Run backtesting
- `hyperopt`: Run hyperparameter optimization
- `trade`: Start/stop trading
- `status`: Get trading status
- `balance`: Get account balance
- `whitelist`: Update pair whitelist
- `blacklist`: Update pair blacklist

### Memory Integration

```
POST /api/v1/notify
Content-Type: application/json

{
    "type": "backtest_result",
    "data": {
        "strategy": "MyStrategy",
        "metrics": {
            "profit": 12.5,
            "trades": 100
        }
    }
}
```

Stores trading results and performance metrics in Mem0 service.

## Authentication

All API endpoints require JWT authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

## Error Handling

The API uses standard HTTP status codes:

- 200: Success
- 400: Bad request
- 401: Unauthorized
- 404: Not found
- 500: Internal server error

Error responses include detailed messages:

```json
{
    "error": "Invalid strategy name",
    "details": "Strategy 'MyStrategy' not found in user_data/strategies/"
}
```

## Integration Example

### Python Client

```python
import requests
import json

class FreqtradeClient:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
    
    def execute_command(self, command, **params):
        url = f"{self.base_url}/api/v1/execute"
        data = {
            "command": command,
            **params
        }
        response = requests.post(url, headers=self.headers, json=data)
        return response.json()
    
    def get_status(self):
        url = f"{self.base_url}/api/v1/status"
        response = requests.get(url, headers=self.headers)
        return response.json()
```

### JavaScript/TypeScript Client

```typescript
interface FreqtradeCommand {
    command: string;
    [key: string]: any;
}

class FreqtradeClient {
    private baseUrl: string;
    private headers: Record<string, string>;

    constructor(baseUrl: string, token: string) {
        this.baseUrl = baseUrl;
        this.headers = {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        };
    }

    async executeCommand(command: FreqtradeCommand): Promise<any> {
        const response = await fetch(`${this.baseUrl}/api/v1/execute`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify(command)
        });
        return response.json();
    }

    async getStatus(): Promise<any> {
        const response = await fetch(`${this.baseUrl}/api/v1/status`, {
            headers: this.headers
        });
        return response.json();
    }
}
```

## Environment Configuration

Required environment variables:

```bash
# Controller Configuration
CONTROLLER_HOST=0.0.0.0
CONTROLLER_PORT=3000
JWT_SECRET=your_secret_key

# Freqtrade Integration
FREQTRADE_URL=http://freqtrade:8080
FREQTRADE_USERNAME=freqtrade
FREQTRADE_PASSWORD=your_password

# Memory Service
MEM0_URL=http://mem0:8080
```

## Security Considerations

1. **API Authentication**
   - Use strong JWT secrets
   - Rotate tokens regularly
   - Implement rate limiting

2. **Network Security**
   - Use HTTPS in production
   - Configure proper CORS settings
   - Restrict access to trusted IPs

3. **Error Handling**
   - Sanitize error messages
   - Log security events
   - Monitor failed authentication attempts

## Monitoring & Logging

The Controller service logs all API requests and responses. Log format:

```json
{
    "timestamp": "2024-06-27T10:00:00Z",
    "level": "INFO",
    "method": "POST",
    "path": "/api/v1/execute",
    "status": 200,
    "duration_ms": 150,
    "client_ip": "10.0.0.1"
}
```

## Development & Testing

1. **Local Testing**

   ```bash
   # Start the Controller service
   python controller.py
   
   # Test the API
   curl -H "Authorization: Bearer $JWT_TOKEN" \
        http://localhost:3000/api/v1/status
   ```

2. **Integration Testing**

   ```bash
   # Run test suite
   pytest tests/test_controller.py
   
   # Test with mock Freqtrade
   FREQTRADE_URL=http://mock:8080 pytest tests/
   ```

## Troubleshooting

1. **Connection Issues**

   ```bash
   # Check service health
   curl http://controller:3000/health
   
   # Verify network connectivity
   ping freqtrade
   ping mem0
   ```

2. **Authentication Problems**

   ```bash
   # Generate new JWT token
   python -c "import jwt; print(jwt.encode({'sub': 'test'}, 'secret'))"
   
   # Test token
   curl -H "Authorization: Bearer $TOKEN" \
        http://controller:3000/api/v1/status
   ```

## Additional Resources

- [API Documentation](docs/API_Contracts.md)
- [Integration Guide](docs/architecture/integrations/README.md)
- [Security Guidelines](docs/operations/security.md)
