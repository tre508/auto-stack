# 🔧 Environment Variables Reference

Complete index of all environment variables used across the automation-stack services.

## Global Configuration

### Core Infrastructure
- `DOMAIN` - Domain name for services (default: localhost)
- `TZ` - Timezone setting (default: Europe/Berlin)
- `NODE_ENV` - Node.js environment (development/production)
- `CI` - CI environment flag for builds and tests
- `PORT` - Default port fallback (varies by service)

## Service-Specific Variables

### Controller Service
- `CONTROLLER_PORT` - FastAPI controller port (default: 5050)
- `CONTROLLER_FREQCHAT_URL` - Controller base URL for freq-chat integration
- `CONTROLLER_API_KEY` - Optional API key for controller authentication
- `EKO_SERVICE_URL` - EKO service endpoint (default: http://localhost:3001/run_eko)
- `EKO_SERVICE_PORT` - EKO service port (default: 3001)

### Authentication & Security
- `API_JWT_SECRET` - JWT secret for API authentication
- `API_WS_TOKEN` - WebSocket authentication token
- `AUTH_SECRET` - NextAuth secret for freq-chat
- `NEXTAUTH_URL` - NextAuth callback URL
- `NEXTAUTH_SECRET` - NextAuth encryption secret

### n8n Workflow Automation
- `N8N_HOST` - n8n service hostname (default: n8n.localhost)
- `N8N_BASIC_AUTH_ACTIVE` - Enable/disable basic auth (default: false)
- `N8N_LICENSE_KEY` - n8n license key for enterprise features
- `N8N_API_KEY` - n8n API authentication key
- `N8N_WEBHOOK_URL` - n8n webhook endpoint for CentralBrain agent
- `N8N_FREQCHAT_WEBHOOK_URL` - n8n webhook for freq-chat triggers

### AI/LLM Integration
- `OPENAI_API_KEY` - OpenAI API key (often routed through OpenRouter)
- `OPENAI_BASE_URL` - Custom OpenAI base URL for proxying
- `ANTHROPIC_API_KEY` - Anthropic Claude API key
- `XAI_API_KEY` - xAI API key for Grok models
- `DEEPSEEK_API_KEY` - DeepSeek API key
- `OPENROUTER_API_KEY` - OpenRouter proxy API key

### OpenRouter Proxy Service
- `OPENROUTER_PROXY_HOST` - Hostname for Traefik routing (default: openrouter-proxy.localhost)
- `OPENROUTER_PROXY_INTERNAL_PORT` - Internal proxy port (default: 8000)
- `OPENROUTER_PROXY_LOG_LEVEL` - Proxy logging level (silent/error/warn/info/debug)
- `PROXY_PORT` - OpenRouter proxy port override
- `YOUR_SITE_URL` - Optional HTTP-Referer header for OpenRouter
- `YOUR_SITE_NAME` - Optional X-Title header for OpenRouter

### Memory & Vector Storage
- `MEM0_API_KEY` - Mem0 service API key
- `MEM0_API_URL` - Mem0 service base URL (default: http://localhost:7770)
- `MEM0_CONFIG_PATH` - Path to Mem0 configuration file (default: /app/config.yaml)
- `PINECONE_API_KEY` - Pinecone vector database API key

### Database Configuration
- `POSTGRES_URL` - Complete PostgreSQL connection string (freq-chat)
- `POSTGRES_HOST` - PostgreSQL hostname (default: postgres)
- `POSTGRES_DB` - Database name (default: automation_stack)
- `POSTGRES_USER` - Database username (default: automation_user)
- `POSTGRES_PASSWORD` - Database password
- `POSTGRES_PORT` - Database port (default: 5432)

### External Storage & Services
- `BLOB_READ_WRITE_TOKEN` - Vercel Blob storage token
- `REDIS_URL` - Redis connection string for caching
- `VERCEL_OIDC_TOKEN` - Vercel deployment authentication

### Trading & Exchange Integration
- `KRAKEN_API_KEY` - Kraken exchange API key
- `KRAKEN_API_SECRET` - Kraken exchange secret key

### Notifications
- `TELEGRAM_BOT_TOKEN` - Telegram bot token for alerts
- `TELEGRAM_CHAT_ID` - Telegram chat ID for notifications

### Legacy/Debug Variables
- `OPENWEBUI_AUTH` - OpenWebUI authentication control (disable)
- `VERCEL_CHAT_AUTH` - Vercel chat authentication control (disable)
- `DEBUG` - Debug logging control for various modules
- `DEBUG_FD` - Debug file descriptor
- `DEBUG_COLORS` - Debug color output control
- `NO_DEPRECATION` - Disable deprecation warnings
- `TRACE_DEPRECATION` - Enable deprecation stack traces
- `PLAYWRIGHT_TEST_BASE_URL` - Playwright testing base URL
- `PLAYWRIGHT` - Playwright environment flag

## Environment Files

### Service Locations
- `/.env` - Root environment (shared across services)
- `/controller/.env` - Controller-specific overrides
- `/freq-chat/.env.example` - Template for freq-chat
- `/freq-chat/.env.development.local` - Development configuration

### Template Structure
Based on the canonical scaffold structure:
```env
# Global
DOMAIN=localhost
TZ=Europe/Berlin

# Core Services
CONTROLLER_PORT=5050
N8N_HOST=n8n.localhost
MEM0_API_URL=http://localhost:7770

# AI/LLM
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
EKO_LLM_PROVIDER=claude

# Database
POSTGRES_HOST=postgres
POSTGRES_DB=automation_stack
POSTGRES_USER=automation_user
POSTGRES_PASSWORD=your_password_here
```

## Security Notes

### Sensitive Variables
The following variables contain sensitive information and should never be committed to version control:
- All API keys (`*_API_KEY`, `*_SECRET`)
- Database passwords (`POSTGRES_PASSWORD`)
- JWT secrets (`API_JWT_SECRET`, `AUTH_SECRET`)
- Authentication tokens (`*_TOKEN`)

### Environment Separation
- Use `.env.example` files as templates
- Maintain separate configurations for development/production
- Use proper secret management in production deployments

## Verification

To verify environment variable configuration:
```bash
# Check environment variables are loaded
docker-compose config

# Verify service-specific variables
docker exec <service> env | grep <PREFIX>

# Test database connectivity
docker exec controller python -c "import os; print(os.getenv('POSTGRES_URL'))"
```

---

*Last updated: 2025-05-23 07:02 UTC+2*
*Part of Phase 5: Reference Standardization*
