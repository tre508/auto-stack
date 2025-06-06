# Agent Task: Comprehensive Mem0 and PostgreSQL Integration Guide

**Objective:**
Your primary goal is to thoroughly investigate, plan, and document the complete setup and integration of the Mem0 service and a PostgreSQL database (for unified logging) within the `automation-stack` project. The final output will be a comprehensive markdown guide named `mem0_server_guide.md` to be placed in the `docs/guides/` directory. This guide should enable another developer or agent to replicate the setup.

**Phase 1: Context Gathering & Research**

1.  **Internal Documentation Review:**
    *   Familiarize yourself with the `automation-stack` by reviewing the following key documents at the root of the `docs/` directory:
        *   `Agent-Orientation.md`
        *   `README_agent.md`
        *   `AutomationChecklist.md`
        *   `TODO.md`
        *   `configplan.md`
    *   Thoroughly review all files and subdirectories within `docs/services/mem0/` and the entire `mem0/` directory at the project root. Pay close attention to:
        *   `docs/mem0/Mem0_Integration_Guide.md` (even if incomplete)
        *   `docs/mem0/Mem0_Troubleshooting_Central.md`
        *   `mem0/server/app.py` (for API endpoint understanding)
        *   `mem0/server/config.yaml` (for default configurations)
        *   `mem0/server/Dockerfile`
        *   `mem0/README.md`
    *   Review `compose-mcp.yml` to understand the current Docker service definitions for `mem0` and `qdrant` (and `postgres` if it exists, or how it *should* exist).
    *   Review `docs/services/n8n/prompt_library/UnifiedLogging.md` for the unified logging strategy.

2.  **External Research - Mem0 Official Documentation:**
    *   **Goal:** Gain a deep understanding of Mem0's architecture, setup, configuration, dependencies, and best practices for self-hosting.
    *   **Method:** Use your browsing tool to visit the official Mem0 GitHub repository (likely `mem0ai/mem0` or similar) and any official Mem0 documentation websites or readmes.
    *   **Focus Areas during Browsing (visit at least 15 relevant pages/sections):**
        *   Installation and setup for self-hosting (Docker is preferred).
        *   Core dependencies (e.g., Python version, specific libraries).
        *   Vector database options (e.g., Qdrant, ChromaDB) and their setup with Mem0. Note if Qdrant is the default or a common choice.
        *   Configuration options in `config.yaml` (or equivalent).
        *   API endpoints and usage.
        *   Environment variables required or recommended.
        *   Data persistence strategies (how to ensure memory is saved).
        *   LLM and embedding model configuration (how to point LLM to OpenRouter proxy, and how to use local embedders like SentenceTransformers, e.g., `all-MiniLM-L6-v2`).
        *   Setting up Mem0 as an MCP server (if official documentation covers this, or if it's inherently MCP-compatible).
        *   **Vercel AI SDK Integration:** Specifically research how Mem0 integrates with the Vercel AI SDK (see `https://docs.mem0.ai/integrations/vercel-ai-sdk`) for use in applications like `freq-chat`.
        *   Troubleshooting common setup issues.
        *   Community discussions or issues related to self-hosting or specific integrations.

**Phase 2: Planning & Guide Creation**

Based on your research, formulate a detailed, step-by-step plan and document it in `docs/guides/mem0_server_guide.md`. This guide should cover:

1.  **Introduction:**
    *   Brief overview of Mem0's role in the `automation-stack`.
    *   Brief overview of the PostgreSQL database's role for unified logging.

2.  **Prerequisites:**
    *   List all software, tools, and accounts needed (e.g., Docker, Docker Compose, Git, Python, access to `.env` file).

3.  **PostgreSQL Setup for Unified Logging:**
    *   **Docker Compose Configuration:** Provide the correct service definition for PostgreSQL in `compose-mcp.yml` (e.g., using `postgres:latest` image).
        *   Ensure it uses environment variables from the root `.env` file for `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`.
        *   Configure persistent volume for data (e.g., `pgdata_mcp`).
        *   Ensure it's on the `mcp-net` network.
    *   **Initialization:** Explain how the database and user are automatically created on the first run.
    *   **Table Creation:** Provide the SQL `CREATE TABLE` statement for the `agent_logs` table (as per `docs/services/n8n/prompt_library/UnifiedLogging.md`). Include instructions on how to connect to the DB (e.g., via `docker exec psql`) to run this command.

4.  **Mem0 Service Setup (Self-Hosted):**
    *   **Vector Database Choice & Setup (Qdrant Preferred):**
        *   Explain why Qdrant is suitable (if confirmed by research).
        *   Provide the correct `qdrant_mcp` service definition for `compose-mcp.yml`.
            *   Image (e.g., `qdrant/qdrant:latest`).
            *   Ports (e.g., map host 6335 to container 6333, host 6336 to container 6334).
            *   Persistent volume for data (e.g., `qdrant_data_mcp`).
            *   Network (`mcp-net`).
    *   **Mem0 Docker Compose Configuration:**
        *   Provide the complete and corrected `mem0_mcp` service definition for `compose-mcp.yml`.
        *   Specify the correct `build` context and `Dockerfile`.
        *   List all necessary environment variables (e.g., `OPENROUTER_API_KEY`, `OPENAI_BASE_URL` for OpenRouter proxy, `MEM0_CONFIG_PATH`, `PORT`).
            *   **Prioritize using `OPENROUTER_API_KEY` and the `openrouter_proxy_mcp` service (`http://openrouter_proxy_mcp:8000/v1`) for LLM models if Mem0 supports OpenAI-compatible endpoints.** Detail how to configure this in Mem0's `config.yaml`.
            *   For embeddings, detail configuration for local `sentence_transformer` models.
        *   Define persistent volume for Mem0 data (e.g., `mem0_data_mcp`).
        *   Ensure it depends on the vector database service (e.g., `qdrant_mcp`) and `openrouter_proxy_mcp`.
        *   Network (`mcp-net`).
    *   **Mem0 `config.yaml` Configuration (`mem0/server/config.yaml`):**
        *   Provide a complete, working example of `config.yaml`.
        *   Detail how to configure the chosen vector database (Qdrant connection URL: `http://qdrant_mcp:6333`).
        *   Detail LLM configuration (pointing to OpenRouter proxy via "openai" provider).
        *   Detail embedder configuration (using local "sentence_transformer" provider, e.g., with "all-MiniLM-L6-v2", to avoid proxy issues with embeddings endpoints).
        *   Explain data persistence settings.
    *   **Building and Running:** Instructions on how to build and run the Mem0 service using `docker-compose`.

5.  **Mem0 MCP Server Setup (If Applicable):**
    *   If Mem0 can act as an MCP server directly, or if a separate MCP wrapper/adapter is needed, detail the setup steps.
    *   Explain how MCP clients would connect to it.

6.  **Integration Verification:**
    *   **Controller & Mem0:** How to test the controller's ability to connect to and use Mem0.
    *   **n8n & Mem0:** Example n8n workflow snippet to test adding/searching memory via Mem0's API.
    *   **`freq-chat` & Mem0:** How `freq-chat` (as a Vercel AI SDK application) should be configured (env vars, API clients) to use the self-hosted Mem0 service, leveraging any specific Vercel AI SDK integration points if applicable.
    *   **Postgres Logging:** How to verify that n8n (or other services) can log to the `agent_logs` table in PostgreSQL.

7.  **Troubleshooting:**
    *   Common issues and their resolutions for both Mem0 and PostgreSQL setup, including `.env` parsing issues and embedding endpoint problems.

**Agent Operational Guidelines:**

*   **Autonomy:** Strive to complete these research and documentation tasks autonomously. Use your available tools (reading files, browsing) to find answers.
*   **Problem Solving:** If you encounter an issue (e.g., conflicting information, missing dependency), first try to resolve it by re-consulting the documentation or searching for solutions online.
*   **Asking for Help:** Only ask the user for clarification or assistance if you've exhausted your self-help resources or if a decision requires user input (e.g., choosing between multiple valid configuration options where preference matters).
*   **Iterative Documentation:** You can write the `mem0_server_guide.md` iteratively as you discover information.
*   **Clarity and Detail:** The final guide must be clear, accurate, and detailed enough for another person to follow.
*   **Local/Free Preference:** Always prioritize configurations that utilize local self-hosting and free tiers of any external services, aligning with the project's current setup.

**Final Deliverable:**
The `docs/guides/mem0_server_guide.md` file containing the comprehensive setup and integration plan.
