# Integrating MCP Tool Servers with OpenWebUI

This document explains the required architecture for integrating tool servers using the Model Context Protocol (MCP) with OpenWebUI.

## OpenWebUI's Preferred Standard: OpenAPI

OpenWebUI is designed to integrate external tools, functions, and pipelines primarily through the widely adopted **OpenAPI specification**. This standard allows for consistent, secure, and well-documented integration of RESTful services. The `open-webui/openapi-servers` repository provides reference implementations for common tools built directly using OpenAPI.

## MCP Integration Requires a Proxy

OpenWebUI **does not directly support** the MCP protocol for tool servers. The MCP protocol typically uses standard input/output (stdio) for communication, which poses security and compatibility challenges for web-based interfaces like OpenWebUI.

To use an MCP-based tool server with OpenWebUI, it **must** be exposed through an intermediary **OpenAPI-compliant proxy server**.

## The `mcpo` Bridge

The official and recommended solution provided by the OpenWebUI team for bridging MCP to OpenAPI is the `mcpo` proxy server, available at:

*   **GitHub:** [https://github.com/open-webui/mcpo](https://github.com/open-webui/mcpo)

**How `mcpo` works:**

1.  `mcpo` runs as a separate service (typically a Docker container).
2.  You configure `mcpo` with the command needed to run your target MCP server (or the URL if it's an SSE-based MCP server).
3.  `mcpo` starts your MCP server as a subprocess (or connects to the URL).
4.  `mcpo` automatically generates an OpenAPI specification for the MCP tool's capabilities.
5.  `mcpo` exposes a standard HTTP/REST API conforming to this OpenAPI spec, translating requests and responses between HTTP and the MCP server's stdio/SSE.

## Integration Steps

1.  **Deploy MCP Tool:** Ensure your target MCP tool server is running and accessible.
2.  **Deploy `mcpo` Proxy:**
    *   Run `mcpo` (e.g., using its Docker image: `ghcr.io/open-webui/mcpo:main`).
    *   Configure `mcpo` to point to your running MCP tool server command or URL. Example command from `mcpo` docs:
        ```bash
        docker run -d -p 8000:8000 --name mcpo-proxy \
          ghcr.io/open-webui/mcpo:main \
          --api-key "f9fea1615863ec7ca4c42192de516abaf187327d8c2b5b0b5400ef4f3a2a147b" \ # Optional, but recommended
          -- # Separator
          your_mcp_server_command --arg1 --arg2 # Command to run your MCP tool
        ```
    *   Ensure the `mcpo` container can network-reach your MCP tool if they are separate containers.
3.  **Configure OpenWebUI:**
    *   Go to OpenWebUI -> Admin Panel -> Settings -> Tools.
    *   Click "Add New Connection".
    *   Enter the URL of the running `mcpo` proxy service (e.g., `http://mcpo-proxy:8000` if running in the same Docker network, or `http://localhost:8000` if mapping the port).
    *   If you configured an API key for `mcpo`, enter it here.
    *   Save the connection.

OpenWebUI should now be able to discover and interact with the MCP tool via the `mcpo` OpenAPI proxy. 