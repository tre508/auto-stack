# Top 15 Recommended MCP Servers for `auto-stack`

This list identifies the top 15 Model Context Protocol (MCP) servers from the Docker Hub MCP catalog (`https://hub.docker.com/u/mcp`) that are deemed most relevant and potentially beneficial for the `auto-stack` project. The selection prioritizes tools that enhance automation, support core development workflows, integrate well with the existing stack (FastAPI, n8n, Freqtrade, Mem0, `freq-chat`), and are free or offer a significant free tier.

**Note:** Some fundamental tools like `mcp/docker`, `mcp/filesystem`, `mcp/fetch`, and `mcp/git` are already highlighted in the `docs/triage/reference/mcp-tools-reference.md` as active or reference tools for this project. Their inclusion or similar tools in this list re-confirms their critical importance.

---

1.  **GitHub MCP Server (`mcp/github-mcp-server`)**
    *   **Description:** Official GitHub MCP Server, by GitHub. Provides seamless integration with GitHub APIs, enabling AI assistants to interact with repositories, issues, pull requests, and more.
    *   **Relevance to `auto-stack`:** Essential for automating development workflows, managing code, tracking issues, and potentially integrating with CI/CD processes.
    *   **Potential Use Cases:** Automating issue creation from `freq-chat` bug reports, summarizing PR changes, fetching file contents from specific branches, triggering n8n workflows on GitHub events.
    *   **Source:** [https://hub.docker.com/r/mcp/github-mcp-server](https://hub.docker.com/r/mcp/github-mcp-server)

2.  **Git (`mcp/git`)**
    *   **Description:** Provides tools for Git repository interaction and automation.
    *   **Relevance to `auto-stack`:** Fundamental for version control. Allows agents to perform Git operations programmatically.
    *   **Potential Use Cases:** Automating commits for documentation updates, branching for new features, pulling latest changes, checking out specific commits for analysis.
    *   **Source:** [https://hub.docker.com/r/mcp/git](https://hub.docker.com/r/mcp/git)

3.  **Docker (`mcp/docker`)**
    *   **Description:** MCP smart gateway used by the AI Tool Catalog for interacting with Docker.
    *   **Relevance to `auto-stack`:** Critical for managing the containerized services of the `auto-stack` and `freqtrade` environments.
    *   **Potential Use Cases:** Automating service restarts, fetching container logs for debugging, checking container status, building images (as referenced in `mcp-tools-reference.md` as `MCP_DOCKER`).
    *   **Source:** [https://hub.docker.com/r/mcp/docker](https://hub.docker.com/r/mcp/docker)

4.  **Filesystem (`mcp/filesystem`)**
    *   **Description:** Enables local filesystem access with configurable allowed paths.
    *   **Relevance to `auto-stack`:** Essential for any task involving reading, writing, or managing files within the project workspace.
    *   **Potential Use Cases:** Reading configuration files, writing generated code or documentation, listing directory contents, searching for files (as referenced in `mcp-tools-reference.md`).
    *   **Source:** [https://hub.docker.com/r/mcp/filesystem](https://hub.docker.com/r/mcp/filesystem)

5.  **Fetch (`mcp/fetch`)**
    *   **Description:** Fetches a URL from the internet and extracts its contents as markdown.
    *   **Relevance to `auto-stack`:** Highly useful for Retrieval Augmented Generation (RAG), gathering external documentation, or getting context from web pages.
    *   **Potential Use Cases:** Fetching latest library documentation, getting news relevant to trading, providing context to LLMs from web sources (as referenced in `mcp-tools-reference.md`).
    *   **Source:** [https://hub.docker.com/r/mcp/fetch](https://hub.docker.com/r/mcp/fetch)

6.  **OpenAPI Schema (`mcp/openapi-schema`)**
    *   **Description:** Server for interacting with OpenAPI (Swagger) schemas.
    *   **Relevance to `auto-stack`:** Invaluable for understanding and interacting with the project's own FastAPI services (`controller_auto`, `mem0_auto`) and any other REST APIs.
    *   **Potential Use Cases:** Dynamically discovering API endpoints, understanding request/response structures, generating API client code snippets, validating API calls.
    *   **Source:** [https://hub.docker.com/r/mcp/openapi-schema](https://hub.docker.com/r/mcp/openapi-schema)

7.  **Playwright (`mcp/playwright`)**
    *   **Description:** Playwright MCP server for browser automation.
    *   **Relevance to `auto-stack`:** `freq-chat` uses Playwright for its E2E tests. This server can enable AI agents to perform browser-based tasks.
    *   **Potential Use Cases:** Automating E2E tests for `freq-chat`, scraping data from websites that require JavaScript, interacting with web UIs that lack APIs.
    *   **Source:** [https://hub.docker.com/r/mcp/playwright](https://hub.docker.com/r/mcp/playwright)

8.  **Tavily (`mcp/tavily`)**
    *   **Description:** Provides seamless interaction with Tavily Search API for AI-focused web search and extraction.
    *   **Relevance to `auto-stack`:** Excellent for providing LLMs with up-to-date information from the web, enhancing research and RAG capabilities.
    *   **Potential Use Cases:** Answering user queries in `freq-chat` that require current information, researching trading strategies, finding solutions to coding problems.
    *   **Source:** [https://hub.docker.com/r/mcp/tavily](https://hub.docker.com/r/mcp/tavily)

9.  **PostgreSQL (`mcp/postgres`)**
    *   **Description:** Connect with read-only access to PostgreSQL databases. Enables LLMs to inspect database schemas and query data.
    *   **Relevance to `auto-stack`:** The project uses PostgreSQL for unified logging (`postgres_logging_auto`). This server would allow agents to query these logs.
    *   **Potential Use Cases:** Analyzing agent activity logs, debugging n8n workflow executions by querying logs, providing summaries of logged events.
    *   **Source:** [https://hub.docker.com/r/mcp/postgres](https://hub.docker.com/r/mcp/postgres)

10. **Obsidian (`mcp/obsidian`)**
    *   **Description:** MCP server that interacts with Obsidian via the Obsidian REST API community plugin.
    *   **Relevance to `auto-stack`:** The project documentation mentions integrating project docs with Obsidian. This server would be key to automating documentation tasks.
    *   **Potential Use Cases:** Creating/updating notes in Obsidian based on completed tasks, searching the Obsidian vault for relevant information, linking project artifacts to documentation.
    *   **Source:** [https://hub.docker.com/r/mcp/obsidian](https://hub.docker.com/r/mcp/obsidian)

11. **Resend (`mcp/resend`)**
    *   **Description:** Sends emails directly using Resend's API.
    *   **Relevance to `auto-stack`:** Useful for sending automated notifications from various parts of the system. Resend has a free tier.
    *   **Potential Use Cases:** Notifying users of completed n8n workflows, sending alerts from Freqtrade (via controller/n8n), summarizing daily agent activities.
    *   **Source:** [https://hub.docker.com/r/mcp/resend](https://hub.docker.com/r/mcp/resend)

12. **Slack (`mcp/slack`)**
    *   **Description:** Interact with Slack Workspaces over the Slack API.
    *   **Relevance to `auto-stack`:** Facilitates automated communication with a development team or community via Slack.
    *   **Potential Use Cases:** Posting deployment notifications, sending alerts for critical errors, allowing `freq-chat` or agents to interact with Slack channels.
    *   **Source:** [https://hub.docker.com/r/mcp/slack](https://hub.docker.com/r/mcp/slack)

13. **Context7 (`mcp/context`)**
    *   **Description:** Context7 MCP Server provides up-to-date code documentation for LLMs and AI code editors.
    *   **Relevance to `auto-stack`:** Can significantly improve an AI agent's ability to understand and modify the project's codebase by providing relevant context.
    *   **Potential Use Cases:** Assisting with refactoring, explaining code sections, generating new code based on existing patterns.
    *   **Source:** [https://hub.docker.com/r/mcp/context](https://hub.docker.com/r/mcp/context)

14. **Node.js Code Sandbox (`mcp/node-code-sandbox`)**
    *   **Description:** A Node.js–based MCP server that spins up disposable Docker containers to execute JavaScript/TypeScript code safely.
    *   **Relevance to `auto-stack`:** Useful for running or testing JavaScript snippets, especially for n8n custom functions or `freq-chat` related logic, in an isolated environment.
    *   **Potential Use Cases:** Safely executing user-provided JS, testing n8n "Function" node code, running small JS utilities.
    *   **Source:** [https://hub.docker.com/r/mcp/node-code-sandbox](https://hub.docker.com/r/mcp/node-code-sandbox)

15. **Time (`mcp/time`)**
    *   **Description:** Provides time and timezone conversion capabilities.
    *   **Relevance to `auto-stack`:** A fundamental utility for tasks involving scheduling, logging with accurate timestamps, or handling data across different timezones.
    *   **Potential Use Cases:** Converting timestamps in logs, scheduling n8n workflows based on specific timezones, ensuring consistent time across services.
    *   **Source:** [https://hub.docker.com/r/mcp/time](https://hub.docker.com/r/mcp/time)

---
This list provides a strong starting point for extending the `auto-stack`'s capabilities with readily available MCP servers. Evaluation and integration should be done based on specific project needs and priorities.
