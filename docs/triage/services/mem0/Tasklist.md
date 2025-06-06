# Mem0 Service Tasklist

This document consolidates all Mem0 service-related documentation and tasks.

## Service Overview
Mem0 is a memory management service component in the automation stack.

---

## Key Objectives

This integration aims to fulfill the goals from `mem0_task_guide.md`:

-   **Re-establish Mem0 Integration**: Achieved by setting up Mem0 as a local Docker service.
-   **Docker Orchestration**: `compose-mcp.yml` manages the Mem0 and Qdrant services.
-   **API Endpoint Connectivity**: Endpoints `/status`, `/memory`, `/search` are available.
-   **Cross-Service Workflow Support**:
    -   `freq-chat`: Connects via its backend API routes.
    -   `n8n`: Connects via HTTP Request nodes.
    -   `controller`: Connects via `httpx` calls.
-   **LLM Context Injection Support**: `freq-chat` and n8n can use Mem0 for RAG.
-   **Validate Mem0**: Health checks and API tests are part of verification.

## API Endpoints

The Mem0 server exposes the following API endpoints (running on internal port 8000, exposed to host via `MEM0_HOST_PORT`):

-   **`GET /status`**: Health check.
-   **`POST /memory`**: Add new memories.
    -   Payload: `{"messages": [{"role": "user/assistant", "content": "..."}], "user_id": "some_user_id", "metadata": {"key": "value"}}`
-   **`POST /search`**: Search memories.
    -   Payload: `{"query": "search_term", "user_id": "some_user_id"}`

## Related Services
- **Controller**: FastAPI service that orchestrates memory operations
- **n8n**: Workflow automation service for stateful workflows
- **EKO**: AI agent service that uses memory for context
- **freq-chat**: Chat interface that provides conversational memory

## Cross-References
- [Controller Service Documentation](../controller/Tasklist.md)
- [n8n Service Documentation](../n8n/Tasklist.md)
- [EKO Service Documentation](../eko/Tasklist.md)
- [Full Integration Guide](../../mem0/Mem0_Integration_Guide.md)
- [Troubleshooting Guide](../../mem0/Mem0_Troubleshooting_Central.md)
