# 🧠 Mem0 Service Integration

## Overview

The Mem0 service provides persistent memory storage for trading performance, strategy analysis, and historical data. It integrates with Freqtrade through the Controller API and n8n workflows.

## Core Features

1. **Performance Tracking**
   - Store backtesting results
   - Track live trading performance
   - Monitor strategy metrics

2. **Historical Data**
   - Trade history
   - Market analysis
   - Strategy evolution

3. **Knowledge Base**
   - Trading patterns
   - Market conditions
   - Strategy insights

## API Integration

### Store Trading Results

```python
import requests
import json

def store_backtest_result(strategy_name, metrics):
    url = "http://mem0:8080/memory"
    data = {
        "messages": [{
            "role": "system",
            "content": f"Backtest results for {strategy_name}: {json.dumps(metrics)}"
        }],
        "metadata": {
            "type": "backtest",
            "strategy": strategy_name,
            "timestamp": "2024-06-27T10:00:00Z"
        }
    }
    response = requests.post(url, json=data)
    return response.json()
```

### Query Trading History

```python
def get_strategy_history(strategy_name):
    url = "http://mem0:8080/search"
    params = {
        "query": f"strategy:{strategy_name}",
        "type": "backtest"
    }
    response = requests.get(url, params=params)
    return response.json()
```

## Data Structure

### Memory Format

```json
{
    "messages": [
        {
            "role": "system",
            "content": "Trading performance data"
        }
    ],
    "metadata": {
        "type": "backtest|live|analysis",
        "strategy": "strategy_name",
        "timestamp": "ISO-8601 timestamp",
        "metrics": {
            "profit": 0.0,
            "trades": 0,
            "win_rate": 0.0
        }
    }
}
```

### Search Queries

```python
# Search by strategy
query = "strategy:MyStrategy"

# Search by date range
query = "timestamp:[2024-01-01 TO 2024-06-27]"

# Search by performance
query = "profit:>10.0"

# Combined search
query = "strategy:MyStrategy AND profit:>10.0"
```

## Integration Workflow

1. **Backtest Results**

   ```mermaid
   graph LR
       A[Freqtrade] --> B[Controller]
       B --> C[Mem0]
       C --> D[Vector Store]
   ```

2. **Live Trading**

   ```mermaid
   graph LR
       A[Freqtrade] --> B[n8n]
       B --> C[Controller]
       C --> D[Mem0]
   ```

## Environment Setup

Required environment variables:

```bash
# Mem0 Service
MEM0_HOST=0.0.0.0
MEM0_PORT=8080
QDRANT_URL=http://qdrant:6333

# Integration
CONTROLLER_URL=http://controller:3000
N8N_WEBHOOK_URL=http://n8n:5678/webhook/mem0
```

## Security

1. **Authentication**
   - API key authentication
   - JWT token validation
   - Role-based access control

2. **Data Protection**
   - Encrypted storage
   - Secure communication
   - Regular backups

## Monitoring

### Health Check

```bash
# Check service status
curl http://mem0:8080/health

# Check vector store
curl http://mem0:8080/vectors/status
```

### Metrics

```bash
# Get service metrics
curl http://mem0:8080/metrics

# Check memory usage
curl http://mem0:8080/stats
```

## Development

### Local Setup

1. Start services:

   ```bash
   docker compose up -d mem0 qdrant
   ```

2. Configure environment:

   ```bash
   export MEM0_URL=http://localhost:8080
   export QDRANT_URL=http://localhost:6333
   ```

3. Run tests:

   ```bash
   pytest tests/test_mem0.py
   ```

### Integration Testing

1. Test Controller integration:

   ```bash
   curl -X POST http://controller:3000/api/v1/notify \
        -H "Content-Type: application/json" \
        -d '{"type":"backtest","data":{"strategy":"test"}}'
   ```

2. Verify storage:

   ```bash
   curl http://mem0:8080/search?query=strategy:test
   ```

## Troubleshooting

1. **Connection Issues**

   ```bash
   # Check network
   ping mem0
   ping qdrant
   
   # Check logs
   docker logs mem0
   ```

2. **Data Issues**

   ```bash
   # Verify vector store
   curl http://qdrant:6333/collections
   
   # Check memory status
   curl http://mem0:8080/status
   ```

## Maintenance

1. **Backup**

   ```bash
   # Backup vectors
   curl -X POST http://mem0:8080/backup
   
   # Export memories
   curl http://mem0:8080/export > backup.json
   ```

2. **Cleanup**

   ```bash
   # Remove old data
   curl -X DELETE http://mem0:8080/cleanup?older_than=30d
   
   # Optimize storage
   curl -X POST http://mem0:8080/optimize
   ```

## Additional Resources

- [Mem0 Documentation](docs/architecture/services/mem0/README.md)
- [API Reference](docs/API_Contracts.md)
- [Integration Guide](docs/architecture/integrations/README.md)
