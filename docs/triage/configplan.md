# Environment Configuration Plan

This document outlines the environment variables and configuration settings required or used by services within the `automation-stack` monorepo.

## Instructions

- Review each section for your relevant services.
- Ensure all **required** variables are set in your local `.env` files or deployment environment.
- Update placeholder values for secrets and API keys.
- Use the checklist to track configuration status.

## Legend

- `[R]` - Required
- `[O]` - Optional
- `[S]` - Secret / API Key
- `[P]` - File Path (potentially requiring MCP access)

---

## Global / Root Configuration

- [ ] Placeholder for global variables

## Service: Controller

- [✅] `CONTROLLER_PORT` [R] - Port for the controller service.
- [✅] `N8N_WEBHOOK_URL` [R] - Webhook URL for n8n integration. (Default: `http://n8n:5678/webhook/centralbrain_agent`)
- [✅] `EKO_SERVICE_URL` [R] - URL for the Eko service (internal, e.g., `http://eko_service_auto:3001/run_eko` or `http://localhost:3001/run_eko`).
- [✅] `MEM0_API_URL` [R] - URL for direct Mem0 API access if used by controller for non-proxied functions (e.g., `http://mem0_auto:8000`).
- [ ] `LOG_FILE_PATH` [P] - Path for controller logs (internal to container, e.g., `/app/controller.log`).
- [ ] `CONTROLLER_API_KEY` [S] - Optional API key to secure controller endpoints if accessed by other services like Freq-Chat.
- [🚧] `HF_SPACE_EMBEDDER_ENDPOINT` [R] - URL for the Hugging Face Space embedder API (e.g., `https://YourUser-YourSpace.hf.space/v1/embeddings`). Used by the Mem0 proxy endpoint in the controller.
- [🚧] `OPENROUTER_PROXY_SERVICE_URL` [R] - Internal URL for the OpenRouter Proxy service (e.g., `http://openrouter_proxy_auto:8000/v1`). Used by the Mem0 proxy endpoint in the controller.
- [🚧] `CONTROLLER_OPENROUTER_API_KEY` [S] - The OpenRouter API key that the controller will use when proxying LLM requests for Mem0 to the OpenRouter Proxy service. This should be your actual OpenRouter key.

## Service: Controller (Freqtrade Integration - as per docs)

- [ ] `FREQTRADE_API_URL` [R] - Base URL for the Freqtrade API.
- [ ] `FREQTRADE_USERNAME` [S] - Username for Freqtrade API authentication.
- [ ] `FREQTRADE_PASSWORD` [S] - Password for Freqtrade API authentication.

## Service: Eko (within Controller context)

- [ ] `ANTHROPIC_API_KEY` [S] - API Key for Anthropic.
- [ ] `OPENAI_API_KEY` [S] - API Key for OpenAI.
- [ ] `EKO_LLM_PROVIDER` [O] - LLM provider for Eko (e.g., `anthropic`, `openai`).
- [ ] `EKO_MODEL_NAME` [O] - Specific model name for the chosen LLM provider.
- [ ] `EKO_SERVICE_PORT` [R] - Port for the Eko service (internal, e.g., `3001`).

## Service: Freq-Chat

- [ ] `NODE_ENV` [O] - Environment mode (`development`, `production`).
- [ ] `AUTH_SECRET` [S] - Secret key for NextAuth session encryption.
- [ ] `NEXTAUTH_URL` [R] - The canonical URL of your Freq-Chat deployment (e.g., `http://localhost:3000` for local dev).
- [✅] `POSTGRES_URL` [S] - Connection URL for the PostgreSQL database. For local development, this is now configured for `freqchat_db` user and database (e.g., `postgresql://freqchat_user:your_password@localhost:5432/freqchat_db`).
- [ ] `OPENAI_API_KEY` [S] - **Required.** Set to your **OpenRouter API Key**. The `@ai-sdk/openai` provider in Freq-Chat will use this.
- [ ] `OPENAI_BASE_URL` [R] - **Required.** Set to the URL of your `openrouter_proxy_auto` service (e.g., `http://openrouter-proxy.localhost/v1` or `http://localhost:YOUR_PROXY_EXTERNAL_PORT/v1`).
- [ ] `DEFAULT_CHAT_MODEL_ID` [O] - Optional. Default OpenRouter model ID for Freq-Chat (e.g., "tngtech/deepseek-r1t-chimera:free").
- [ ] `XAI_API_KEY` / `GROK_API_KEY` [S] - (Alternative) API key if using xAI/Grok models directly.
- [ ] `ANTHROPIC_API_KEY` [S] - (Alternative) API key if using Anthropic directly in Freq-Chat.
- [ ] `COHERE_API_KEY` [S] - (Alternative) API key if using Cohere directly in Freq-Chat.
- [ ] `CONTROLLER_API_URL` [R] - URL that Freq-Chat uses to reach the Controller service (e.g., `http://localhost:YOUR_CONTROLLER_PORT` or `http://controller_auto:5050`).
- [ ] `CONTROLLER_API_KEY` [S] - API key Freq-Chat uses to authenticate with the Controller service (optional, if controller expects `X-API-Key`).
- [ ] `MEM0_API_URL` [R] - URL that Freq-Chat uses to reach the self-hosted Mem0 service (e.g., `http://localhost:YOUR_MEM0_PORT` or `http://mem0_auto:8000`). (Standardized from `SELF_HOSTED_MEM0_API_URL`).
- [ ] `MEM0_API_KEY` [S] - (Optional) API key for Mem0 service if Freq-Chat is configured to send one and Mem0 expects it. Current self-hosted Mem0 does not.
- [ ] `N8N_FREQCHAT_WEBHOOK_URL` [R] - The specific n8n webhook URL Freq-Chat's backend calls.
- [ ] `PLAYWRIGHT_TEST_BASE_URL` [O] - Base URL for Playwright tests.
- [ ] `PLAYWRIGHT` [O] - Flag for Playwright environment.
- [ ] `CI_PLAYWRIGHT` [O] - Flag for Playwright CI environment.

## Service: Mem0 (`mem0_auto`)

- [✅] `MEM0_HOST_PORT` [R] - Host port mapped to Mem0 container's internal port (e.g., `7860` in `.env`).
- [✅] `PORT` [R] - Internal port the Mem0 FastAPI server listens on inside the container (e.g., `8000`, set in `docker-compose.yml` or Dockerfile).
- [✅] `MEM0_API_HOST` [R] - Host for Mem0 API to listen on inside container (typically `0.0.0.0`).
- [🚧] `OPENAI_API_KEY` [S] - For Mem0 service: This should be set to your **Hugging Face Token** (e.g., `hf_YourToken...`). Mem0 will send this as a Bearer token. The controller's `/mem0_openai_proxy/v1/embeddings` endpoint will receive this and forward it to the HF Space.
- [🚧] `OPENAI_BASE_URL` [R] - For Mem0 service: This must point to the controller's proxy base URL (e.g., `http://controller_auto:5050/mem0_openai_proxy/v1`).
- [✅] `MEM0_CONFIG_PATH` [P] - Path to Mem0 `config.yaml` inside the container (e.g., `/app/config.yaml`). (Note: `config.yaml` sets `provider: "openai"` for both LLM and embedder).

## Service: Qdrant (`qdrant_auto`)

- Typically configured via its own configuration files or command-line arguments, not extensively via environment variables in `docker-compose.yml` for basic setup. Persistent storage is managed via Docker volumes.

## Service: PostgreSQL (Unified Logging - `postgres_logging_auto`)

- [ ] `POSTGRES_LOGGING_USER` [R] - Username for the logging database (e.g., `autostack_logger` in `.env`).
- [ ] `POSTGRES_LOGGING_PASSWORD` [S] - Password for the logging database user (in `.env`).
- [ ] `POSTGRES_LOGGING_DB` [R] - Name of the logging database (e.g., `autostack_logs` in `.env`).
- [ ] `POSTGRES_LOGGING_PORT` [R] - Host port mapped to PostgreSQL container's port 5432 (e.g., `5433` in `.env`).

## Service: OpenRouter Proxy

- [ ] `OPENROUTER_API_KEY` [S] - API Key for OpenRouter.
- [ ] `OPENROUTER_PROXY_HOST` [R] - Hostname for the OpenRouter proxy service (e.g., `openrouter.localhost`).
- [ ] `OPENROUTER_PROXY_INTERNAL_PORT` [R] - Internal port for the OpenRouter proxy (e.g., `8000`).
- [ ] `OPENROUTER_PROXY_LOG_LEVEL` [O] - Log level for the proxy (e.g., `info`, `debug`).
- [ ] `YOUR_SITE_URL` [O] - (Optional, commented out in compose file) Your site URL for OpenRouter.
- [ ] `YOUR_SITE_NAME` [O] - (Optional, commented out in compose file) Your site name for OpenRouter.

## Service: n8n

- [ ] `N8N_BASIC_AUTH_ACTIVE` [O] - Enable/disable basic authentication for n8n (e.g., `true`).
- [ ] `N8N_HOST` [R] - Hostname for n8n (e.g., `n8n.localhost`).
- [ ] `N8N_WEBHOOK_URL` [R] - Publicly accessible webhook URL for n8n.
- [ ] `N8N_API_KEY` [S] - API key for n8n.
- [ ] `N8N_LICENSE_KEY` [S] - License key for n8n enterprise features (optional).
- [ ] `DB_TYPE` [R] - Database type (fixed to `sqlite` in compose).
- [ ] `DB_SQLITE_DATABASE` [P] - Path to SQLite DB file within n8n container (e.g., `/home/node/.n8n/database.sqlite`).
- [ ] `N8N_SECURE_COOKIE` [R] - Secure cookie setting (fixed to `false` in compose, review for production).

## Other Services / Tools

- [ ] Placeholder for other services

## Discrepancies between existing .env files and .env.example

**Root .env / controller/.env vs. .env.example:**

**Present in actual .env, Missing or Different in `.env.example` (needs adding/clarification):**

- [ ] `OPENWEBUI_AUTH` [O] - Related to OpenWebUI, purpose unclear in current context.
- [ ] `KRAKEN_API_KEY` [S] - API key for Kraken exchange.
- [ ] `KRAKEN_API_SECRET` [S] - API secret for Kraken exchange.
- [ ] `TELEGRAM_BOT_TOKEN` [S] - Token for a Telegram bot.
- [ ] `TELEGRAM_CHAT_ID` [S] - Chat ID for Telegram notifications.
- [ ] `API_JWT_SECRET` [S] - JWT secret, potentially for a custom API/service not yet detailed.
- [ ] `API_WS_TOKEN` [S] - WebSocket token, similar to JWT secret.
- [ ] `DEEPSEEK_API_KEY` [S] - API key for Deepseek.
- [ ] `PINECONE_API_KEY` [S] - API key for Pinecone vector database.
- [ ] `POSTGRES_HOST` [R] - (Legacy/General) Consider standardizing to `POSTGRES_LOGGING_HOST` if this refers to the logging DB.
- [ ] `POSTGRES_DB` [R] - (Legacy/General) Consider standardizing to `POSTGRES_LOGGING_DB`.
- [ ] `POSTGRES_USER` [R] - (Legacy/General) Consider standardizing to `POSTGRES_LOGGING_USER`.
- [ ] `POSTGRES_PASSWORD` [S] - (Legacy/General) Consider standardizing to `POSTGRES_LOGGING_PASSWORD`.
- [ ] `POSTGRES_PORT` [R] - (Legacy/General) Consider standardizing to `POSTGRES_LOGGING_PORT`.
- [ ] `VERCEL_CHAT_AUTH` [O] - Related to Vercel chat auth, purpose unclear.

**Notes on .env findings:**

- The root `.env` and `controller/.env` appear to be identical. This is good for local Eko service testing if it loads a local `.env`.
- The actual `.env` may have multiple `OPENAI_API_KEY` entries. For the self-hosted Mem0 service, it should use the `OPENROUTER_API_KEY` (passed as `OPENAI_API_KEY` to its container) and `OPENAI_BASE_URL` pointing to the `openrouter_proxy_auto` service.
- The self-hosted Mem0 server does not use a `MEM0_API_KEY` for its own authentication; client access to its REST API is unauthenticated by default in the provided `mem0/server/app.py`.
- `pgdata/.env` (for a generic postgres service) does not exist, which is normal. The new `postgres_logging_auto` service uses variables like `POSTGRES_LOGGING_USER` from the root `.env`.
