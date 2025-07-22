# Auto-Stack Integration Guide

**Status:** Consolidated Integration Documentation - Phase 3 Implementation  
**Created:** 2025-01-26  
**Purpose:** Unified integration patterns and API contracts

## Integration Architecture Overview

The auto-stack employs a layered integration architecture where services communicate through well-defined API contracts and event-driven patterns.

### Integration Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  freq-chat  │  │     n8n     │  │  Freqtrade  │        │
│  │    (UI)     │  │ (Workflows) │  │  (Trading)  │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                  Orchestration Layer                        │
│              ┌─────────────────────────┐                    │
│              │      Controller         │                    │
│              │   (API Gateway &        │                    │
│              │   Orchestrator)         │                    │
│              └─────────────────────────┘                    │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                   Service Layer                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │    Mem0     │  │     EKO     │  │   Traefik   │        │
│  │  (Memory)   │  │ (AI Agent)  │  │   (Proxy)   │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                 Infrastructure Layer                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Qdrant    │  │ PostgreSQL  │  │ OpenRouter  │        │
│  │ (Vector DB) │  │  (Logging)  │  │   Proxy     │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

## Core Integration Patterns

### 1. HTTP REST API Communication

**Primary Pattern:** Synchronous request-response communication

#### Request Format
```json
{
  "method": "POST",
  "headers": {
    "Content-Type": "application/json",
    "Authorization": "Bearer <token>"
  },
  "body": {
    "action": "execute_task",
    "parameters": {...},
    "session_id": "unique_identifier"
  }
}
```

#### Response Format
```json
{
  "status": "success|error",
  "data": {...},
  "message": "Human readable message",
  "timestamp": "2025-01-26T20:00:00Z",
  "request_id": "unique_identifier"
}
```

### 2. Webhook Event-Driven Communication

**Pattern:** Asynchronous event notification

#### Webhook Payload
```json
{
  "event_type": "task_completed",
  "source_service": "n8n",
  "target_service": "controller",
  "payload": {
    "task_id": "uuid",
    "status": "completed",
    "result": {...}
  },
  "timestamp": "2025-01-26T20:00:00Z"
}
```

### 3. Memory-Mediated Communication

**Pattern:** Persistent state sharing via Mem0

#### Memory Storage
```json
{
  "messages": [{
    "role": "system",
    "content": "Task execution context"
  }],
  "user_id": "service_identifier",
  "metadata": {
    "task_type": "integration",
    "source_service": "controller",
    "timestamp": "2025-01-26T20:00:00Z"
  }
}
```

## Service Integration Specifications

### Controller ↔ n8n Integration

**Communication Method:** HTTP Webhooks  
**Authentication:** API Key  
**Data Format:** JSON

#### Controller → n8n (Workflow Triggering)

**Endpoint:** `POST /webhook/controller-master-workflow`

```bash
curl -X POST http://n8n_auto:5678/webhook/controller-master-workflow \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Execute complex automation",
    "parameters": {
      "strategy": "analysis",
      "target": "freqtrade"
    },
    "session_id": "ctrl-session-123"
  }'
```

#### n8n → Controller (Status Notification)

**Endpoint:** `POST /api/v1/notify`

```bash
curl -X POST http://controller_auto:5050/api/v1/notify \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_id": "n8n-workflow-456",
    "status": "completed",
    "result": {...},
    "timestamp": "2025-01-26T20:00:00Z"
  }'
```

### Controller ↔ Mem0 Integration

**Communication Method:** HTTP REST API  
**Authentication:** None (internal network)  
**Data Format:** JSON

#### Memory Operations via Controller

**Add Memory:**
```bash
curl -X POST http://controller_auto:5050/mcp/cursor/add_memory \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Integration test completed successfully",
    "user_id": "controller_service",
    "metadata": {
      "type": "integration_result",
      "timestamp": "2025-01-26T20:00:00Z"
    }
  }'
```

**Search Memory:**
```bash
curl -X POST http://controller_auto:5050/mcp/cursor/search_memory \
  -H "Content-Type: application/json" \
  -d '{
    "query": "integration test results",
    "user_id": "controller_service",
    "limit": 10
  }'
```

### freq-chat ↔ Controller Integration

**Communication Method:** HTTP REST API  
**Authentication:** API Key  
**Data Format:** JSON

#### Chat Message Processing

**Endpoint:** `POST /api/v1/chat/completions`

```bash
curl -X POST http://controller_auto:5050/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <api_key>" \
  -d '{
    "messages": [{
      "role": "user",
      "content": "Analyze the latest trading performance"
    }],
    "session_id": "chat-session-789",
    "model": "gpt-4"
  }'
```

#### Task Execution via freq-chat

**Endpoint:** `POST /api/v1/execute`

```bash
curl -X POST http://controller_auto:5050/api/v1/execute \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Generate trading report for last 30 days",
    "session_id": "chat-task-101",
    "parameters": {
      "timeframe": "30d",
      "format": "summary"
    }
  }'
```

## Freqtrade Integration Patterns

### Controller ↔ Freqtrade Integration

**Communication Method:** HTTP REST API with JWT Authentication  
**Network:** Docker internal network  
**Data Format:** JSON

#### Authentication Flow

1. **Get JWT Token:**
```bash
curl -X POST http://freqtrade_devcontainer:8080/api/v1/token/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "freqtrade_user",
    "password": "freqtrade_password"
  }'
```

2. **Use Token for API Calls:**
```bash
TOKEN="<received_access_token>"
curl -H "Authorization: Bearer $TOKEN" \
  http://freqtrade_devcontainer:8080/api/v1/status
```

#### Key Freqtrade API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|----------|
| `/api/v1/ping` | GET | Health check |
| `/api/v1/status` | GET | Bot status |
| `/api/v1/trades` | GET | Trade history |
| `/api/v1/profit` | GET | Profit summary |
| `/api/v1/performance` | GET | Performance metrics |
| `/api/v1/balance` | GET | Account balance |

### n8n ↔ Freqtrade Integration

**Communication Methods:**
1. **Direct API Calls:** HTTP Request nodes
2. **CLI Command Execution:** Execute Command nodes
3. **Via Controller:** Indirect through Controller API

#### Direct API Integration Example

**n8n Workflow Steps:**
1. **Authentication Node:**
   - HTTP Request to `/api/v1/token/login`
   - Store token in workflow context

2. **Data Retrieval Node:**
   - HTTP Request with Bearer token
   - Parse JSON response

3. **Processing Node:**
   - Transform data format
   - Apply business logic

4. **Action Node:**
   - Store results in Mem0
   - Send notifications
   - Trigger other workflows

#### CLI Command Execution Example

**Backtest Execution Workflow:**
```json
{
  "command": "freqtrade backtesting",
  "parameters": [
    "--strategy", "{{ $json.strategy_name }}",
    "--timerange", "{{ $json.timerange }}",
    "--config", "user_data/config.json",
    "--export", "trades"
  ]
}
```

### Mem0 ↔ Freqtrade Integration (Indirect)

**Pattern:** Mediated through Controller or n8n workflows  
**Purpose:** Store and retrieve Freqtrade-related context

#### Freqtrade Data Storage Patterns

**Trade Summary Storage:**
```json
{
  "messages": [{
    "role": "system",
    "content": "Trade completed: BTC/USDT, Profit: 2.5%, Duration: 4h"
  }],
  "user_id": "freqtrade_bot",
  "metadata": {
    "type": "trade_result",
    "pair": "BTC/USDT",
    "profit_pct": 0.025,
    "duration_hours": 4,
    "strategy": "SuperTrendV1",
    "timestamp": "2025-01-26T20:00:00Z"
  }
}
```

**Backtest Results Storage:**
```json
{
  "messages": [{
    "role": "system",
    "content": "Backtest completed for SuperTrendV1: 15.7% profit, 8% max drawdown, 75 trades"
  }],
  "user_id": "freqtrade_backtester",
  "metadata": {
    "type": "backtest_result",
    "strategy": "SuperTrendV1",
    "timerange": "20230101-20230630",
    "total_profit_pct": 15.7,
    "max_drawdown_pct": 8.0,
    "total_trades": 75,
    "timestamp": "2025-01-26T20:00:00Z"
  }
}
```

## Configuration Management

### Environment Variable Hierarchy

**Root `.env` (Shared Variables):**
```bash
# API Keys
OPENROUTER_API_KEY=<key>
OPENAI_API_KEY=<key>
HF_TOKEN=<token>

# Service URLs
CONTROLLER_API_URL=http://controller_auto:5050
MEM0_API_URL=http://mem0_auto:8000
N8N_WEBHOOK_URL=http://n8n_auto:5678/webhook

# Database Configuration
POSTGRES_LOGGING_USER=autostack_logger
POSTGRES_LOGGING_PASSWORD=<password>
POSTGRES_LOGGING_DB=autostack_logs
```

**Service-Specific Configuration:**

*Controller (`controller/.env`):*
```bash
CONTROLLER_PORT=5050
FREQTRADE_API_URL=http://freqtrade_devcontainer:8080
FREQTRADE_USERNAME=<username>
FREQTRADE_PASSWORD=<password>
```

*freq-chat (`freq-chat/.env.development.local`):*
```bash
OPENAI_BASE_URL=http://openrouter-proxy.localhost/v1
NEXTAUTH_URL=http://localhost:3001
NEXTAUTH_SECRET=<secret>
```

### Network Configuration

**Docker Network:** `auto-stack-net`

**Service Discovery:**
- Services communicate using container names
- Internal ports used for inter-service communication
- External ports exposed only when needed

**Example Service Endpoints:**
```bash
# Internal network endpoints
http://controller_auto:5050
http://mem0_auto:8000
http://n8n_auto:5678
http://freqtrade_devcontainer:8080

# External access via Traefik
http://controller.localhost
http://mem0.localhost
http://n8n.localhost
http://freqtrade.localhost
```

## Error Handling and Resilience

### Retry Patterns

**Exponential Backoff:**
```python
import time
import random

def retry_with_backoff(func, max_retries=3, base_delay=1):
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
            time.sleep(delay)
```

### Circuit Breaker Pattern

```python
class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func):
        if self.state == 'OPEN':
            if time.time() - self.last_failure_time > self.timeout:
                self.state = 'HALF_OPEN'
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func()
            if self.state == 'HALF_OPEN':
                self.state = 'CLOSED'
                self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.failure_count >= self.failure_threshold:
                self.state = 'OPEN'
            raise e
```

### Health Check Implementation

**Service Health Check Endpoint:**
```python
from fastapi import FastAPI
from datetime import datetime

app = FastAPI()

@app.get("/health")
async def health_check():
    # Check dependencies
    dependencies = {
        "mem0": check_mem0_health(),
        "n8n": check_n8n_health(),
        "database": check_database_health()
    }
    
    all_healthy = all(dependencies.values())
    
    return {
        "status": "healthy" if all_healthy else "unhealthy",
        "timestamp": datetime.utcnow().isoformat(),
        "dependencies": dependencies
    }
```

## Testing Integration Patterns

### End-to-End Integration Test

```bash
#!/bin/bash
# integration_test.sh

echo "Testing Controller → n8n → Mem0 integration..."

# 1. Trigger workflow via Controller
echo "Step 1: Triggering n8n workflow via Controller"
RESPONSE=$(curl -s -X POST http://localhost:5050/api/v1/execute \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Store integration test result",
    "session_id": "integration-test-001"
  }')

echo "Controller response: $RESPONSE"

# 2. Wait for workflow completion
echo "Step 2: Waiting for workflow completion..."
sleep 5

# 3. Verify data in Mem0
echo "Step 3: Checking Mem0 for stored data"
MEMORY_RESPONSE=$(curl -s -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "integration test result",
    "user_id": "controller_service"
  }')

echo "Mem0 search response: $MEMORY_RESPONSE"

# 4. Validate results
if echo "$MEMORY_RESPONSE" | grep -q "integration test"; then
    echo "✅ Integration test PASSED"
    exit 0
else
    echo "❌ Integration test FAILED"
    exit 1
fi
```

### Service Integration Matrix Testing

| Test | From | To | Method | Expected Result |
|------|------|----|---------|--------------------|
| T1 | freq-chat | Controller | HTTP API | 200 OK with task execution |
| T2 | Controller | n8n | Webhook | Workflow triggered |
| T3 | n8n | Mem0 | HTTP API | Memory stored |
| T4 | Controller | Freqtrade | HTTP API + JWT | Authentication successful |
| T5 | n8n | Freqtrade | CLI Command | Backtest executed |

## Monitoring and Observability

### Integration Metrics

**Key Performance Indicators:**
- Request/response latency between services
- Success/failure rates for each integration
- Authentication token refresh frequency
- Webhook delivery success rates
- Memory storage/retrieval performance

**Monitoring Commands:**
```bash
# Check service connectivity
docker exec controller_auto curl -f http://mem0_auto:8000/status
docker exec n8n_auto curl -f http://controller_auto:5050/api/v1/status

# Monitor webhook deliveries
docker logs n8n_auto | grep "webhook"
docker logs controller_auto | grep "execute"

# Check authentication status
docker logs controller_auto | grep "freqtrade.*auth"
```

### Integration Debugging

**Debug Checklist:**
1. ✅ Network connectivity between services
2. ✅ Environment variables properly configured
3. ✅ Authentication tokens valid and refreshed
4. ✅ API endpoints responding correctly
5. ✅ Webhook URLs accessible
6. ✅ Data formats matching expected schemas
7. ✅ Error handling functioning properly

---

**Documentation Status:** This guide consolidates and replaces:
- `archive/triage_legacy/integrations/freqtrade_*.md` files (5 integration guides)
- Cross-stack integration documentation  
- Service-specific integration patterns

**Next:** Proceed to [Service Architecture](../services/README.md) and [Quick Start Setup](../../setup/00_QuickStart.md).