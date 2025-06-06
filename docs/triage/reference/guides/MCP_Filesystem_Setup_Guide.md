# Checklist: Using `mcp/filesystem:latest` with Docker AI Tools Extension in a WSL Environment

**WSL Environment Note:** All filesystem paths in this guide must be specified from the perspective of the WSL filesystem. Windows-style paths (e.g., `C:\\Users\\...`) will not work correctly. Use paths like `/mnt/c/Users/...` to access your Windows filesystem or `~/...` for your WSL home directory.

**Goal:** Enable filesystem tools (read, write, list, etc.) provided by the `mcp/filesystem:latest` Docker image, making them accessible via an MCP client (e.g., Claude Desktop, VS Code with Docker AI Extension) that is integrated with your Docker AI Tools extension.

**Understanding the Workflow:**
The `mcp/filesystem:latest` server is typically **managed dynamically** by the Docker AI Tools extension. When you call a filesystem tool:
1. Your MCP client sends the request to the Docker AI Tools extension (likely via its main MCP bridge, e.g., on host port `8811`).
2. The extension identifies the tool as belonging to `mcp/filesystem`.
3. It consults `mcp-metadata-cache.edn` and your `docker-prompts/config.yaml`.
4. It **automatically starts** an instance of `mcp/filesystem:latest`, configuring it with volume mounts based on the paths in your `config.yaml`.
5. The tool executes in this container, and results are returned.

You generally **do not need to manually run or bridge** the `mcp/filesystem:latest` container if using it through the Docker AI Tools extension.

**Last Updated:** $(Get-Date -Format 'yyyy-MM-dd')

---

## ☐ 1. Prerequisites & Preparation

*   **Docker Desktop Running:** Ensure Docker Desktop is running.
*   **Docker AI Tools Extension Running:** Verify the `docker_labs-ai-tools-for-devs-desktop-extension-service` is active. This is the service that orchestrates MCP tools, including `mcp/filesystem`. You've previously observed this on `localhost:8811` serving `mcp/docker`.
*   **`mcp/filesystem:latest` Image Pulled:**
    *   Command: `docker pull mcp/filesystem:latest`
    *   Expected: Image is downloaded or reported as up-to-date. (Status: __DONE__)
*   **`docker-prompts` Volume Exists:**
    *   Command: `docker volume ls --filter name=docker-prompts`
    *   Expected: Lists `docker-prompts`. (Status: __DONE__)
*   **`config.yaml` in `docker-prompts` Volume:**
    *   Ensure the `docker-prompts` volume contains a `config.yaml` file. **This is the master configuration for the Docker AI Tools extension.**
    *   This file **must** define the host filesystem paths you want `mcp/filesystem:latest` to access, [x]**structured within a `registry` format** that the Docker AI Tools extension service reads.
    *   [x] Correct `config.yaml` structure (should be at the equivalent of `C:\\ProgramData\\Docker\\volumes\\docker-prompts\\_data\\config.yaml` within your WSL Docker Desktop data root):
        ```yaml
        registry:
          filesystem:
            ref: github:docker/labs-ai-tools-for-devs?ref=main&path=prompts/mcp/filesystem.md
            config:
              filesystem:
                paths:
                  - "/mnt/c/Users/your_username/projects"
                  - "/home/your_username/projects" # Example for projects in WSL home
                  - "/mnt/c/ProgramData"
                  # Add other relevant WSL-accessible paths
          # Potentially other toolset configurations here under 'registry:'
        ```
    *   **Action:** Manually verify the content and structure of your `config.yaml` in the `docker-prompts` volume. **Ensure it uses the `registry:` format and WSL-style paths.** If it only contains a `filesystem:` block at the root, or has Windows paths, it is incorrect for the extension and needs to be replaced.
    *   (Status: __PENDING YOUR MANUAL VERIFICATION AND CORRECTION IF NEEDED__)

## ☐ 2. Configure Your MCP Client

*   Ensure your MCP client (e.g., Claude Desktop, VS Code with Docker AI extension, Cursor) is configured to communicate with the Docker AI Tools extension's MCP endpoint.
    *   This typically involves pointing your client to the address/port or socket provided by the Docker AI Tools extension.
    *   **For Cursor users:** If you have an `mcp.json` entry like `"MCP_DOCKER":{"command":"docker","args":["run","-l","mcp.client=cursor","--rm","-i","alpine/socat","STDIO","TCP:host.docker.internal:8811"]}`, this step is likely already complete, as it correctly targets the Docker AI Tools extension service.
    *   (Status: __PENDING YOUR CONFIGURATION & VERIFICATION__ - Potentially __DONE__ for Cursor users with the described `MCP_DOCKER` entry)
*   No separate configuration is usually needed for `mcp/filesystem` itself within the client if the Docker AI Tools extension handles it; the tools will be available under the `mcp/filesystem` server name (e.g., accessible via the `MCP_DOCKER` bridge).

## ☐ 3. Test Filesystem Tools via MCP Client

*   Once your MCP client is connected to the Docker AI Tools extension, attempt to use a filesystem tool.
*   **Example tool invocations (syntax may vary by client):**
    *   Directly if the client resolves `mcp/filesystem` through the extension's bridge:
        `@mcp/filesystem list_directory path="/mnt/c/Users/your_username/projects"`
    *   Explicitly via a bridge name (e.g., `MCP_DOCKER` in Cursor), if required by the client:
        `@MCP_DOCKER::mcp/filesystem.list_directory path="/mnt/c/Users/your_username/projects"`
        or sometimes with JSON arguments:
        `@MCP_DOCKER::mcp/filesystem.list_directory {"path": "/mnt/c/Users/your_username/projects"}`
    *   To read a file from a configured path (adjust prefix as needed):
        `@mcp/filesystem read_file path="/mnt/c/Users/your_username/projects/your_project/README.md"`
    *   To write a file (use with caution!, adjust prefix as needed):
        `@mcp/filesystem write_file path="/home/your_username/projects/test.txt" content="Hello from MCP"`
*   **Expected Outcome:**
    *   The command executes successfully, and you receive the expected output (e.g., file list, file content) or confirmation of action (e.g., file written).
    *   You might see the `mcp/filesystem:latest` container start and stop in `docker ps -a` if you monitor it during the tool call.
*   **Troubleshooting:**
    *   If errors occur, check:
        *   Logs from your MCP client.
        *   Logs from the Docker AI Tools extension service.
        *   Ensure `config.yaml` paths are absolutely correct and accessible by the Docker user.
        *   Ensure the paths you are trying to access in your tool calls are covered by the `paths` in `config.yaml`.
*   (Status: __PENDING YOUR TESTING__)

## ☐ 4. (Optional) Alternative: Manual Standalone Setup

*   If you wish to run `mcp/filesystem:latest` as a **standalone, persistent service independent of the Docker AI Tools extension**, you would:
    1.  Manually run the `mcp/filesystem:latest` container using `docker run`, exposing a **new, unused host port** (e.g., `-p 8812:8888`).
    2.  Ensure you correctly mount your `config.yaml` (or the directory containing it) into this manually run container.
    3.  Configure your MCP client with a **new, separate server entry** pointing to this new host port (e.g., `localhost:8812`).
*   This approach gives you more direct control but bypasses any integrated management by the Docker AI Tools extension. This guide primarily focuses on the extension-managed approach.

---

This checklist should help you verify that the `mcp/filesystem:latest` tools are usable through your Docker AI Tools extension. The key is the correct `config.yaml` and a properly configured MCP client. 