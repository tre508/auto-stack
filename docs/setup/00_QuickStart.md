# 🚀 Auto-Stack Quick Start Guide

> **Get your unified AI automation platform running in 15 minutes**

**Status:** Consolidated Setup Guide - Phase 3 Implementation  
**Created:** 2025-01-26  
**Last Updated:** 2025-07-21  

---

## 📋 Overview

The **auto-stack** project is a unified, modular, and robust platform for AI-driven automation and algorithmic trading. This guide provides everything needed to get started from a fresh environment.

### 🎯 Project Vision

- **Name:** auto-stack
- **Vision:** Unified platform for AI-driven automation and algorithmic trading
- **Core Objectives:**
  - **🧩 Modularity:** Independent, manageable services
  - **💾 Data Persistence:** Reliable storage with persistent Docker volumes
  - **📚 Clear Documentation:** Canonical, up-to-date documentation

---

## 🏗️ Core Services Architecture

### Primary Services

| Service | Role | Technology | Port | Status |
|---------|------|------------|------|--------|
| **🌐 Traefik** | Reverse Proxy & API Gateway | Go | 80, 443, 8081 | ✅ Active |
| **🔄 n8n** | Workflow Automation Engine | Node.js, TypeScript | 5678 | ✅ Active |
| **🎛️ Controller** | AI Orchestrator & Logic Router | Python, FastAPI | 5050 | ✅ Active |
| **🧠 Mem0** | Long-Term Memory Service | Python, FastAPI | 8000 | ✅ Active |
| **💬 freq-chat** | Primary User Interface | Next.js, React | 3001 | ✅ Active |

### Supporting Services

| Service | Role | Technology | Port | Status |
|---------|------|------------|------|--------|
| **🔍 Qdrant** | Vector Database for Embeddings | Rust | 6333-6334 | ✅ Active |
| **🐘 PostgreSQL** | Structured Logging Database | SQL | 5432 | ✅ Active |
| **🔗 OpenRouter Proxy** | LLM Gateway & Fallback Manager | Node.js | 8001 | ✅ Active |
| **🧠 BGE Embedding** | Text Embeddings Service | Python | 7861 | ✅ Active |
| **📈 Freqtrade** | Trading Bot & Backtester | Python | 8080 | 🚧 Future |

---

## ✅ Prerequisites

### System Requirements

| Requirement | Version/Notes | Installation Guide |
|-------------|---------------|-------------------|
| **🖥️ Operating System** | WSL 2 | Required for Docker Desktop integration |
| **🐳 Docker Desktop** | >= 25.0 | Install with WSL 2 integration, **reboot after installation** |
| **📦 Git** | Latest | Required for cloning repositories |
| **💻 VS Code or Cursor** | Latest | Must connect to WSL via "Remote - WSL" extension |
| **⚡ Hardware** | 16+ GB RAM | GPU recommended for local LLM performance |
| **🟢 Node.js** | >= 18 LTS | Install in WSL using `nvm` |
| **🐍 Python** | >= 3.8 | Install in WSL for local development |

### 🔑 API Keys (Optional but Recommended)

- **🔗 OpenRouter API Key** - For remote LLM access
- **🤖 OpenAI/Anthropic Keys** - For freq-chat enhanced features
- **🤗 Hugging Face Token** - For embedding services

---

## 🚀 Quick Setup Process

### Step 1: Project Structure Setup

> **⚠️ Important:** All setup must be performed from within WSL terminal.

```bash
# Create projects directory in WSL home
mkdir -p ~/projects
cd ~/projects

# Clone the auto-stack repository
git clone <your-auto-stack-repo-url> auto-stack
cd auto-stack
```

### Step 2: The "Focused Workflow" (Critical)

> **🎯 This is mandatory for stable development.** VS Code extensions and toolchains require proper workspace scoping.

#### ✅ Correct Procedure

1. **Launch WSL terminal**
2. **Navigate to project:** `cd ~/projects/auto-stack`
3. **Open in editor:** `code .`

#### ❌ Never Do This

- **Don't open the root folder directly in your editor**
- **Don't skip the WSL terminal step**

---

## ⚙️ Environment Configuration

### Step 3: Configure Environment Variables

```bash
# Copy and configure environment file
cp .env.example .env
nano .env  # Edit with your specific values
```

#### 🔑 Essential Environment Variables

```bash
# ==========================================
# Core API Keys
# ==========================================
OPENROUTER_API_KEY=<your_openrouter_key>
OPENAI_API_KEY=<your_openai_key>
HF_TOKEN=<your_huggingface_token>

# ==========================================
# Service Authentication
# ==========================================
CONTROLLER_API_KEY=<your_controller_secret>
N8N_BASIC_AUTH_USER=<n8n_username>
N8N_BASIC_AUTH_PASSWORD=<n8n_password>

# ==========================================
# Database Configuration
# ==========================================
POSTGRES_LOGGING_USER=autostack_logger
POSTGRES_LOGGING_PASSWORD=<secure_password>
POSTGRES_LOGGING_DB=autostack_logs

# ==========================================
# Service Hosts
# ==========================================
N8N_HOST=n8n.localhost
MEM0_HOST=mem0.localhost
```

### Step 4: Network Setup

```bash
# Docker network is auto-created, but verify:
docker network ls | grep auto-stack-net

# Create manually if needed:
docker network create auto-stack-net
```

---

## 🏃‍♂️ Service Startup

### Step 5: Start All Services

```bash
# From ~/projects/auto-stack directory

# Pull latest images (optional but recommended)
docker compose pull

# Start all services in detached mode
docker compose up -d

# Verify services are running
docker compose ps
```

### Step 6: Monitor Startup Progress

```bash
# Watch logs for all services
docker compose logs -f

# Check specific service logs
docker logs controller_auto
docker logs mem0_auto
docker logs n8n_auto
```

> **⏱️ Startup Time:** Initial startup takes 2-5 minutes. BGE embedding service may take up to 10 minutes to fully initialize.

---

## ✅ Verification & Testing

### Step 7: Service Health Check

Access these URLs to verify services are running:

| Service | URL | Expected Result |
|---------|-----|-----------------|
| **🌐 Traefik Dashboard** | `http://localhost:8081/dashboard/` | Management interface |
| **🔄 n8n** | `http://n8n.localhost` | Workflow interface |
| **🎛️ Controller API** | `http://controller.localhost/docs` | FastAPI documentation |
| **🧠 Mem0 API** | `http://mem0.localhost/status` | "Mem0 service is running" |
| **💬 freq-chat** | `http://localhost:3001` | Chat interface |
| **🔍 Qdrant** | `http://localhost:6333` | Qdrant dashboard |
| **🔗 OpenRouter Proxy** | `http://openrouter-proxy.localhost/healthz` | "OK" |

### Step 8: Integration Testing

#### 🔗 Controller ↔ n8n Integration

```bash
curl -X POST http://controller.localhost/execute \
  -H "Content-Type: application/json" \
  -d '{"message": "test integration"}'
```

#### 🧠 Mem0 Memory Operations

```bash
# Add a memory
curl -X POST http://localhost:8000/memory \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{
      "role": "user", 
      "content": "Test memory from setup"
    }], 
    "user_id": "setup_test"
  }'

# Search memories
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Test memory", 
    "user_id": "setup_test"
  }'
```

---

## 🔗 Key Integration Patterns

### For Freqtrade Developers

#### 🎛️ Execute Tasks via Controller

```bash
curl -X POST http://localhost:5050/api/v1/execute \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Analyze latest backtest results",
    "session_id": "freqtrade-session-123"
  }'
```

#### 💾 Store Data in Mem0

```bash
curl -X POST http://localhost:8000/v1/memories \
  -H "Content-Type: application/json" \
  -d '{
    "data": "Trade closed: BTC/USDT, Profit: 2.5%",
    "metadata": {
      "source": "freqtrade_strategy",
      "pair": "BTC/USDT",
      "profit_pct": 0.025
    },
    "user_id": "freqtrade_bot"
  }'
```

#### 🔄 Trigger n8n Automations

```bash
curl -X POST http://n8n.localhost/webhook/mem0-logger \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "trade_summary",
    "payload": {"pair": "ETH/USDT", "profit": "1.8%"}
  }'
```

---

## 🚨 Troubleshooting

### Common Issues & Solutions

#### 🐳 Docker Services Won't Start

- **✅ Check:** Docker Desktop is running with WSL2 integration
- **✅ Check:** Port conflicts: `netstat -tulpn | grep :8080`
- **🔄 Action:** Restart Docker Desktop

#### 🌐 Network Connectivity Issues

- **✅ Check:** `auto-stack-net` exists: `docker network ls`
- **✅ Check:** Traefik routing: Dashboard at `localhost:8081`
- **✅ Check:** Firewall settings

#### 🔑 Service Access Problems

- **✅ Check:** `.env` file contains all required variables
- **✅ Check:** Service logs: `docker logs <service_name>`
- **✅ Check:** Hostnames resolve: `ping n8n.localhost`

### 📊 Log Analysis Commands

```bash
# View all logs
docker compose logs -f

# View specific service
docker logs controller_auto -f

# Check Docker system status
docker system df
docker system events
```

### 🆘 Emergency Commands

```bash
# Stop all services
docker compose down

# Restart entire stack
docker compose down && docker compose up -d

# Check service status
docker compose ps

# Monitor specific service
docker compose logs -f [service_name]
```

---

## 🎯 Next Steps

After completing setup, explore these areas:

### 1. 🔧 Service Configuration

Review detailed service documentation for advanced configuration options.

### 2. 🔗 Integration Patterns

Explore cross-stack integration guides for building custom workflows.

### 3. 👨‍💻 Development Workflow

Set up your development environment for contributing to the project.

### 4. 📈 Freqtrade Setup

Configure trading environment and strategies (future feature).

### 5. 🚀 Advanced Features

Explore n8n workflows and automation capabilities.

---

## 🔧 Maintenance

### Regular Maintenance Tasks

```bash
# Update images and restart services
docker compose pull && docker compose up -d

# Clean unused Docker resources (use cautiously)
docker system prune -f

# Backup volume data
docker volume ls
docker volume inspect <volume_name>
```

### Environment Updates Process

1. **Stop services:** `docker compose down`
2. **Update code:** `git pull`
3. **Update images:** `docker compose pull`
4. **Update `.env` file** with new configurations
5. **Restart:** `docker compose up -d`
6. **Run verification checks**

---

## 📚 Documentation Status

### Consolidation Information

**This guide consolidates and replaces:**

- ❌ `00_MasterSetup.md` (deprecated)
- ❌ `new-stack-agent-guide.md` (deprecated)
- ❌ `auto-stack_guide.md` (deprecated)

### What's Next?

**Proceed to service-specific configuration and integration guides:**

- **[🏗️ Service Architecture](../architecture/services/README.md)**
- **[🔗 Integration Patterns](../architecture/integrations/README.md)**
- **[🔧 Operations Guide](../operations/troubleshooting/)**

---

**🎉 Congratulations!** Your auto-stack is now running and ready for AI-driven automation and algorithmic trading development!
