# Auto-Stack Service Architecture

**Status:** Consolidated Service Documentation - Phase 3 Implementation  
**Created:** 2025-01-26  
**Purpose:** Unified service architecture and API reference

## Architecture Overview

The auto-stack consists of interconnected microservices that provide AI-driven automation, memory management, workflow orchestration, and trading capabilities.

### Service Interaction Map

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│  freq-chat  │────│  Controller  │────│     n8n     │
│   (UI)      │    │ (Orchestrator)│    │ (Workflows) │
└─────────────┘    └──────────────┘    └─────────────┘
       │                   │                   │
       │                   │                   │
       ▼                   ▼                   ▼
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│    Mem0     │◄───│     EKO      │    │   Traefik   │
│ (Memory)    │    │ (AI Agent)   │    │  (Proxy)    │
└─────────────┘    └──────────────┘    └─────────────┘
       │                                       │
       ▼                                       ▼
┌─────────────┐                        ┌─────────────┐
│   Qdrant    │                        │ OpenRouter  │
│ (Vector DB) │                        │   Proxy     │
└─────────────┘                        └─────────────┘
```

## Core Services

### Controller Service

**Role:** Central orchestration and API gateway  
**Technology:** Python, FastAPI  
**Port:** 3000 (internal), 5050 (external)

#### Key Functions
- **API Gateway**: Central REST API for all service interactions
- **Service Orchestration**: Coordinates between n8n, Mem0, Freqtrade
- **Task Execution**: Handles complex automation workflows
- **MCP Integration**: Model Context Protocol gateway for Cursor IDE

#### Core API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|----------|
| `/api/v1/execute` | POST | Trigger n8n workflows |
| `/api/v1/notify` | POST | Receive status updates |
| `/api/v1/status` | GET | Health check |
| `/docs` | GET | OpenAPI documentation |
| `/mcp/cursor/*` | * | MCP integration endpoints |

#### Configuration
```bash
# Environment Variables
CONTROLLER_PORT=5050
N8N_WEBHOOK_URL=http://n8n_auto:5678/webhook/controller-master
MEM0_API_URL=http://mem0_auto:8000
EKO_SERVICE_URL=http://eko_service:3001
FREQTRADE_API_URL=http://freqtrade:8080
```

#### Integration Patterns
- **n8n**: Forwards payloads to configured webhook URL
- **Mem0**: HTTP client for memory operations (not direct package)
- **Freqtrade**: JWT authentication and API proxy
- **EKO**: Task routing for AI agent workflows

### Mem0 Service

**Role:** Memory management and persistence  
**Technology:** Python, FastAPI  
**Port:** 8000 (internal), configurable (external)

#### Key Functions
- **Memory Storage**: Add, search, and retrieve memories
- **Context Management**: Persistent context across sessions
- **RAG Support**: Retrieval-augmented generation capabilities
- **Vector Operations**: Integration with Qdrant for embeddings

#### Core API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|----------|
| `/status` | GET | Health check |
| `/memory` | POST | Add new memories |
| `/search` | POST | Search existing memories |

#### Configuration
```bash
# Environment Variables
MEM0_HOST_PORT=8000
OPENAI_API_KEY=<HF_TOKEN>  # For embeddings
OPENAI_BASE_URL=http://controller_auto:5050/mem0_openai_proxy/v1
QDRANT_HOST=qdrant_auto
QDRANT_PORT=6333
```

#### Data Formats
```json
// Add Memory
{
  "messages": [{
    "role": "user",
    "content": "Memory content"
  }],
  "user_id": "user_identifier",
  "metadata": {"key": "value"}
}

// Search Memory
{
  "query": "search_term",
  "user_id": "user_identifier"
}
```

### n8n Service

**Role:** Visual workflow automation  
**Technology:** Node.js, TypeScript  
**Port:** 5678

#### Key Functions
- **Workflow Designer**: Visual workflow creation interface
- **Agent Orchestration**: Multi-agent workflow coordination
- **System Integration**: Docker, Git, file system operations
- **Webhook Processing**: HTTP triggers for external integrations

#### Workflow Categories

**Agent Workflows:**
- CentralBrain Agent
- Freqtrade Specialist Agent
- Backtest Agent
- Summarization Agent

**System Workflows:**
- Docker Health Check
- Git Repo Commit Notifier
- Unified Logging

**Trading Workflows:**
- Freqtrade Task Runner
- Freqtrade Log Monitor
- Stock Analysis

#### Configuration
```bash
# Environment Variables
N8N_BASIC_AUTH_ACTIVE=true
N8N_BASIC_AUTH_USER=<username>
N8N_BASIC_AUTH_PASSWORD=<password>
WEBHOOK_URL=http://n8n.localhost
N8N_EDITOR_BASE_URL=http://n8n.localhost
```

### freq-chat Service

**Role:** User interface and chat experience  
**Technology:** Next.js, React  
**Port:** 3001

#### Key Functions
- **Chat Interface**: Real-time conversational AI
- **Multi-model Support**: Multiple LLM providers
- **File Processing**: Upload and document handling
- **Context Awareness**: Persistent conversation memory

#### Core API Routes

| Route | Purpose |
|-------|----------|
| `/api/chat` | Main chat endpoint |
| `/api/chat/mem0` | Memory integration |
| `/api/orchestration/controller` | Controller integration |
| `/api/webhooks/n8n` | n8n webhook handling |

#### Configuration
```bash
# Environment Variables
OPENAI_API_KEY=<OPENROUTER_API_KEY>
OPENAI_BASE_URL=http://openrouter-proxy.localhost/v1
MEM0_API_URL=http://mem0_auto:8000
CONTROLLER_API_URL=http://controller_auto:5050
N8N_FREQCHAT_WEBHOOK_URL=http://n8n.localhost/webhook/freqchat
NEXTAUTH_URL=http://localhost:3001
NEXTAUTH_SECRET=<secret>
```

## Supporting Services

### Qdrant (Vector Database)

**Role:** Vector storage for embeddings  
**Technology:** Rust  
**Port:** 6333

- Stores vector embeddings for Mem0
- Provides similarity search capabilities
- Persistent storage for vector data

### PostgreSQL (Logging Database)

**Role:** Structured data storage  
**Technology:** SQL  
**Port:** 5432

- Stores structured logs and audit data
- Provides relational data capabilities
- Persistent storage for operational data

### Traefik (Reverse Proxy)

**Role:** API gateway and routing  
**Technology:** Go  
**Ports:** 80, 443, 8080

- Routes requests to appropriate services
- SSL termination and load balancing
- Service discovery and health checks

### OpenRouter Proxy

**Role:** LLM API gateway  
**Technology:** Node.js  
**Port:** 8001

- Proxies requests to external LLM providers
- API key management and rate limiting
- Fallback and retry logic

## Service Communication Patterns

### HTTP REST APIs
- Primary communication method between services
- JSON payloads for data exchange
- Standard HTTP status codes for responses

### Docker Network
- All services connected via `auto-stack-net`
- Service discovery via container names
- Internal communication on standard ports

### Webhook Integration
- n8n workflows triggered via webhooks
- Event-driven communication patterns
- Asynchronous processing capabilities

### Environment Variable Configuration
- Centralized configuration via `.env` files
- Service-specific overrides supported
- Hierarchical configuration loading

## Health Monitoring

### Health Check Endpoints

| Service | Endpoint | Expected Response |
|---------|----------|-------------------|
| Controller | `GET /api/v1/status` | `{"status": "ok"}` |
| Mem0 | `GET /status` | `{"status": "ok"}` |
| freq-chat | `GET /api/health` | `{"status": "healthy"}` |
| Qdrant | `GET /` | Qdrant dashboard |
| Traefik | `GET /ping` | `"OK"` |

### Service Dependencies

```
Controller depends on: Mem0, n8n, EKO
Mem0 depends on: Qdrant
freq-chat depends on: Controller, Mem0, n8n
n8n depends on: Controller, Mem0
```

### Monitoring Commands

```bash
# Check all service status
docker compose ps

# View service logs
docker logs controller_auto -f
docker logs mem0_auto -f
docker logs n8n_auto -f

# Test service connectivity
curl http://controller.localhost/api/v1/status
curl http://mem0.localhost/status
curl http://n8n.localhost/healthz
```

## Development Workflow

### Local Development Setup

1. **Environment Preparation**
   ```bash
   cd ~/projects/auto-stack
   cp .env.example .env
   # Edit .env with your configuration
   ```

2. **Service Startup**
   ```bash
   docker compose up -d
   docker compose logs -f
   ```

3. **Verification**
   ```bash
   # Test Controller
   curl -X POST http://localhost:5050/api/v1/execute \
     -H "Content-Type: application/json" \
     -d '{"message": "test"}'
   
   # Test Mem0
   curl -X GET http://localhost:8000/status
   
   # Test freq-chat
   open http://localhost:3001
   ```

### Service-Specific Development

**Controller Development:**
```bash
cd controller/
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn controller:app --reload
```

**freq-chat Development:**
```bash
cd freq-chat/
npm install
npm run dev
```

**Mem0 Development:**
```bash
cd mem0/
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload
```

## Integration Testing

### End-to-End Workflow Test

```bash
# 1. Add memory via Controller
curl -X POST http://localhost:5050/mcp/cursor/add_memory \
  -H "Content-Type: application/json" \
  -d '{"content": "Test integration", "user_id": "test"}'

# 2. Search memory via Mem0
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "Test integration", "user_id": "test"}'

# 3. Trigger n8n workflow via Controller
curl -X POST http://localhost:5050/api/v1/execute \
  -H "Content-Type: application/json" \
  -d '{"task": "Test workflow execution"}'

# 4. Test freq-chat integration
# Open http://localhost:3001 and send test message
```

### Service Integration Matrix

| From/To | Controller | Mem0 | n8n | freq-chat | EKO |
|---------|------------|------|-----|-----------|-----|
| **Controller** | - | ✓ HTTP | ✓ Webhook | ✓ API | ✓ HTTP |
| **Mem0** | ✓ Callback | - | ✓ HTTP | ✓ API | ✓ HTTP |
| **n8n** | ✓ Webhook | ✓ HTTP | - | ✓ Webhook | ✓ HTTP |
| **freq-chat** | ✓ API | ✓ API | ✓ Webhook | - | ✓ API |
| **EKO** | ✓ Callback | ✓ HTTP | ✓ HTTP | ✓ API | - |

---

**Documentation Status:** This document consolidates and replaces:
- `archive/triage_legacy/services/*/Tasklist.md` files (7 service documents)
- Service-specific documentation scattered across folders
- Integration patterns from multiple guides

**Next:** Proceed to [Integration Patterns](../integrations/README.md) and [Quick Start Setup](../../setup/00_QuickStart.md).