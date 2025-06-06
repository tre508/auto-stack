# Potential MCP Tools for automation-stack & Freqtrade Project

This list is compiled from available information about Cursor MCP servers and focuses on tools that might be relevant for a dual-stack project involving backend development, automation, and data interaction. Free or developer-friendly tiers are prioritized.

## High Relevance

1.  **GitHub MCP Server**
    *   **Description:** Integrates with GitHub's issue tracking, allowing LLMs to interact with GitHub issues.
    *   **Potential Use:** Automating issue creation/updates, querying issue status from n8n or the controller.
    *   **Source:** [cursor.directory/mcp](https://cursor.directory/mcp)

2.  **Supabase MCP Server (via PostgREST)**
    *   **Description:** Allows LLMs to perform database queries and operations on Postgres databases via PostgREST.
    *   **Potential Use:** Direct database interaction for Freqtrade data analysis, managing application state if using PostgreSQL. Supabase offers a free tier.
    *   **Source:** [cursor.directory/mcp](https://cursor.directory/mcp)

3.  **Neon MCP Server**
    *   **Description:** Interact with the Neon serverless Postgres platform.
    *   **Potential Use:** Similar to Supabase, for direct interaction with a Neon PostgreSQL database. Neon offers a free tier.
    *   **Source:** [cursor.directory/mcp](https://cursor.directory/mcp)

4.  **Resend MCP Server**
    *   **Description:** Sends emails using Resend's API, allowing LLMs to compose and send emails.
    *   **Potential Use:** Notifications from n8n workflows or the controller (e.g., Freqtrade alerts, task summaries). Resend has a free tier.
    *   **Source:** [cursor.directory/mcp](https://cursor.directory/mcp)

5.  **Mailtrap Email Sending MCP Server**
    *   **Description:** Integrates with Mailtrap Email Platform for sending transactional emails.
    *   **Potential Use:** Similar to Resend, for sending email notifications. Mailtrap has free tiers for testing/low volume.
    *   **Source:** [cursor.directory/mcp](https://cursor.directory/mcp)

## Conditional Relevance (Depending on Specific Needs)

*   **Upstash MCP Server (Redis/Kafka/QStash)**
    *   **Description:** MCP Server for Upstash Developer APIs.
    *   **Potential Use:** If serverless data structures (like Redis caches) or messaging/queuing (Kafka, QStash) are needed for the automation stack or Freqtrade data pipelines. Upstash offers free tiers.
    *   **Source:** [cursor.directory/mcp](https://cursor.directory/mcp)

*   **Bucket MCP Server (Feature Flags/Remote Config)**
    *   **Description:** Add feature flags, manage company data, control feature access.
    *   **Potential Use:** More for application feature management if you build more complex user-facing aspects into your controller or other services.
    *   **Source:** [cursor.directory/mcp](https://cursor.directory/mcp)

## Note on Built-in Cursor Agent Tools

Remember that Cursor's agent already has powerful built-in tools for interacting with your local codebase and the web, which will be essential:
*   **Search:** Read File, List Directory, Codebase Search, Grep, File Search, Web Search.
*   **Edit:** Edit File, Delete File.
*   **Run:** Terminal Execution.

These will complement any external MCP tools you integrate.

---
Note: The Multi-Agent Documentation & Task Orchestration Hub is implemented as a set of n8n workflows and agent patterns, not a standalone MCP tool, but may leverage MCP nodes for orchestration. 