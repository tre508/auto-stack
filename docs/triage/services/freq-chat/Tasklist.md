# Freq-Chat Service Tasklist

This document consolidates all Freq-Chat service-related documentation and tasks.

## Service Overview
Freq-Chat is a Next.js-based chatbot interface service component deployed on Vercel that provides conversational AI capabilities and integrates with the automation stack services.

---

## Core Documentation Index

### Setup & Configuration
- **Setup Guide**: [Vercel Setup](../vercel/setup.md)
- **Integration Guide**: [Vercel Integration](../vercel/integration.md)
- **Usage Documentation**: [Vercel Usage](../vercel/usage.md)
- **Troubleshooting**: [Vercel Troubleshooting](../vercel/troubleshooting.md)

### Customization & Development
- **Next.js AI Chatbot Customization**: [Customization Guide](../vercel/nextjs_ai_chatbot_customization.md)
- **Project Structure**: Located at `freq-chat/` directory in automation stack

### Integration Documentation
- **Vercel Integration Files**: 
  - [Integration Overview](../vercel/integration/integration.md)
  - [Setup Instructions](../vercel/integration/setup.md)
  - [Usage Guide](../vercel/integration/usage.md)
  - [Updates & Changes](../vercel/integration/updates.md)
  - [Vercel Integration Details](../vercel/integration/Vercel-integration.md)

## Key Service Functions

### Chat Interface
- Real-time conversational AI interface
- Multi-model LLM support
- Context-aware conversations
- File upload and processing capabilities

### Automation Stack Integration
- **Controller Integration**: API calls to controller endpoints
- **Mem0 Integration**: Persistent conversation memory
- **n8n Integration**: Workflow triggers from chat interactions
- **EKO Integration**: AI agent task execution

### Deployment & Hosting
- **Platform**: Vercel serverless functions
- **Environment**: Production and development environments
- **Configuration**: Environment variables for service integration
- **Scaling**: Automatic scaling based on demand

## Configuration Requirements

### Environment Variables
- `OPENAI_API_KEY`: **Required for core chat functionality.** Set this to your **OpenRouter API Key**. The `@ai-sdk/openai` provider in Freq-Chat will use this.
- `OPENAI_BASE_URL`: **Required.** Set this to the URL of your `openrouter_proxy_mcp` service (e.g., `http://openrouter-proxy.localhost/v1` via Traefik, or `http://localhost:YOUR_PROXY_EXTERNAL_PORT/v1` if Freq-Chat runs on host and proxy is port-mapped).
- `DEFAULT_CHAT_MODEL_ID`: (Optional) Set this to your preferred default OpenRouter model ID (e.g., `"tngtech/deepseek-r1t-chimera:free"`). If not set, `providers.ts` has a fallback.
- `XAI_API_KEY` (or `GROK_API_KEY`): (Alternative) Key for xAI/Grok models, if `providers.ts` is reconfigured to use them.
- `ANTHROPIC_API_KEY`: (Alternative) For direct Anthropic Claude access if `providers.ts` is reconfigured.
- `MEM0_API_URL`: Mem0 service endpoint (e.g., `http://mem0_mcp:8000` or `http://localhost:YOUR_MEM0_PORT`).
- `MEM0_API_KEY`: (Optional) API key for Mem0 service. If set, Freq-Chat will send it as a Bearer token. The current self-hosted `mem0_mcp` does not require this; leave unset for `mem0_mcp`.
- `CONTROLLER_API_URL`: Controller service endpoint (e.g., `http://controller_mcp:5050` or `http://localhost:YOUR_CONTROLLER_PORT`).
- `N8N_FREQCHAT_WEBHOOK_URL`: The specific n8n webhook URL that Freq-Chat's backend will call to trigger workflows.
- `NEXTAUTH_URL`: Canonical URL for NextAuth.js (e.g., `http://localhost:3000` for local dev).
- `NEXTAUTH_SECRET`: Secret for NextAuth.js.
- `POSTGRES_URL`: Connection string for Freq-Chat's PostgreSQL database.

### Vercel Configuration
- **Build Command**: `pnpm build`
- **Output Directory**: `.next`
- **Install Command**: `pnpm install`
- **Framework**: Next.js
- **Node.js Version**: 18.x or later

### Local Development
- **Development Server**: `pnpm dev`
- **Port**: 3000 (default)
- **Environment File**: `.env.local`
- **Dependencies**: Node.js, pnpm

## API Endpoints

### Chat API
- **`/api/chat`**: Main chat endpoint for conversation handling
- **`/api/chat/mem0`**: Memory integration endpoint
- **`/api/chat/orchestration`**: Multi-service orchestration

### Integration APIs
- **`/api/orchestration/mem0`**: Mem0 service integration
- **`/api/orchestration/controller`**: Controller service integration
- **`/api/webhooks/n8n`**: n8n webhook handling

## Testing & Validation

### Local Testing
- Start development server: `pnpm dev`
- Access interface at `http://localhost:3000`
- Test chat functionality with various prompts
- Verify service integrations

### Production Testing
- Deploy to Vercel staging environment
- Test all service integrations
- Verify environment variable configuration
- Performance and load testing

## Integration Points

### Controller Service
- Executes complex automation tasks
- Handles MCP server communications
- Processes chat-triggered workflows

### Mem0 Service
- Stores conversation history and context
- Enables context-aware responses
- Supports retrieval-augmented generation (RAG)

### n8n Service
- Triggers automation workflows from chat
- Processes chat context through workflows
- Returns workflow results to chat interface

### EKO Service
- Executes AI agent tasks from chat commands
- Provides advanced reasoning capabilities
- Handles complex multi-step operations

## Related Services
- **Controller**: Central orchestration and MCP gateway
- **Mem0**: Conversation memory and context storage
- **n8n**: Workflow automation triggered by chat
- **EKO**: AI agent execution for complex tasks
- **Proxy**: API routing and authentication (if used)

## Cross-References
- [Controller Service Documentation](../controller/Tasklist.md)
- [Mem0 Service Documentation](../mem0/Tasklist.md)
- [n8n Service Documentation](../n8n/Tasklist.md)
- [EKO Service Documentation](../eko/Tasklist.md)
- [Proxy Service Documentation](../proxy/Tasklist.md)
