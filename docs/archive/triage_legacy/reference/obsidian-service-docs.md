# Obsidian & Project Documentation Integration Guide

**Status:** ✅ Rebuilt 2025-06-08

## Purpose

This guide outlines how to integrate project documentation from the `auto-stack` and `freqtrade` environments with a personal Obsidian vault. It covers methods for manual access and editing, as well as potential for automated interactions using MCP servers.

## Understanding Project Documentation Sources

The `auto-stack` project maintains documentation in two primary locations, accessible on the host machine and potentially shared into Docker containers via volume mounts:

*   **`auto-stack` Core Documentation:** Located in the `docs/` directory within the `auto-stack` project root (e.g., `~/projects/auto-stack/docs/` in a typical WSL setup). This includes general project information, service guides, and API contracts.
*   **`freqtrade` User Documentation:** Located in the `user_data/docs/` directory within the `freqtrade` project root (e.g., `~/projects/freqtrade/user_data/docs/`). This is the recommended place for user-specific Freqtrade strategies, notes, research, and configurations.

## Integrating Project Docs with Your Obsidian Vault (Manual Access)

The primary goal for manual integration is to allow users to conveniently view, edit, and manage project-related documentation within their preferred Obsidian vault.

### Recommended Approaches:

#### 1. Symbolic Links (Recommended for WSL Users)

This method links the project documentation directories directly into your Obsidian vault, allowing them to appear as regular folders within Obsidian.

**On your host machine (from a WSL terminal):**

*   **Linking `freqtrade` User Docs:**
    ```bash
    # Navigate to your Obsidian Vault's root directory (e.g., /mnt/c/Users/YourUser/MyObsidianVault)
    # cd C:\Users\glenn\FreqVault\FreqVault

    # Create a symbolic link to your Freqtrade user docs.
    # Adjust <PATH_TO_YOUR_FREQTRADE_PROJECT_ROOT_IN_WSL> accordingly.
    # Example: ~/projects/freqtrade
    ln -s <PATH_TO_YOUR_FREQTRADE_PROJECT_ROOT_IN_WSL>/user_data/docs FreqtradeUserDocs
    ```
    *(Replace `<PATH_TO_YOUR_FREQTRADE_PROJECT_ROOT_IN_WSL>` with the absolute WSL path to your `freqtrade` project, e.g., `/home/glenn/projects/freqtrade`)*

*   **Linking `automation-stack` Core Docs (Optional):**
    ```bash
    # Navigate to your Obsidian Vault's root directory
    # cd /path/to/your/MyObsidianVault

    # Create a symbolic link to the automation-stack docs.
    # Adjust <PATH_TO_YOUR_AUTOMATION_STACK_PROJECT_ROOT_IN_WSL> accordingly.
    # Example: ~/projects/auto-stack
    ln -s <PATH_TO_YOUR_AUTO_STACK_PROJECT_ROOT_IN_WSL>/docs AutomationStackCoreDocs
    ```
    *(Replace `<PATH_TO_YOUR_AUTO_STACK_PROJECT_ROOT_IN_WSL>` with the absolute WSL path to your `auto-stack` project, e.g., `/home/glenn/projects/auto-stack`)*

#### 2. Opening Directories as Vaults/Folders in Obsidian

Alternatively, most versions of Obsidian allow you to:
*   Open an existing directory as a new vault.
*   Add an existing directory to your current workspace or as a folder within an existing vault.

You can use this method to directly open `~/projects/auto-stack/docs/` or `~/projects/freqtrade/user_data/docs/` (using their WSL paths, accessible by Obsidian if it's aware of WSL filesystems, or their Windows equivalent paths like `\\wsl$\Ubuntu-24.04\home\glenn\projects\auto-stack\docs`).

## Automated/Programmatic Integration with Obsidian (Advanced)

For more advanced integration, such as automating note creation or updates from n8n workflows or Controller actions, the `auto-stack` can potentially leverage the `mcp/obsidian` MCP server.

*   **MCP Server:** `mcp/obsidian`
*   **Description:** This server interacts with an Obsidian vault through the **Obsidian REST API community plugin**. This plugin must be installed and configured within the target Obsidian vault.
*   **Relevance to `auto-stack`:**
    *   Enables programmatic interaction with your Obsidian notes.
    *   Allows services within the `automation-stack` (like n8n or the FastAPI Controller) to create, read, update, or delete notes, or search the vault.
*   **Potential Use Cases:**
    *   Automatically creating a new note in Obsidian when a Freqtrade strategy is developed or a significant backtest is completed.
    *   Updating a project status note in Obsidian from an n8n workflow.
    *   Allowing `freq-chat` (via the Controller) to search for relevant documentation within your Obsidian vault.
*   **Setup:** Requires installing and configuring the Obsidian REST API plugin in your vault and setting up the `mcp/obsidian` server to connect to it. Refer to the documentation for both the plugin and the MCP server.

## Optional User-Managed Setups

The following integrations are considered optional and are the user's responsibility to set up and maintain.

### 1. Integrating External Official Documentation

If you wish to keep local copies of official documentation for tools like n8n, Python, Docker, etc., within your Obsidian vault, you can clone their Git repositories directly into your vault.

**Example:**
```bash
# Inside your Obsidian vault directory
git clone https://github.com/n8n-io/n8n-docs.git _ExternalDocs/n8n_Official_Docs
git clone --depth 1 https://github.com/ollama/ollama.git _ExternalDocs/Ollama_Official_Docs_Mirror # For latest snapshot
```
You are responsible for keeping these cloned repositories updated (e.g., via `git pull`).

### 2. Obsidian Vault Sync

To synchronize your Obsidian vault across multiple devices or for backup, you can use various methods:
*   **Obsidian Sync:** The official paid service.
*   **Community Plugins:** Plugins like `Remotely Save` allow syncing to services like S3, Dropbox, OneDrive, etc.
*   **Cloud Storage Services:** Manually syncing your vault folder using services like Google Drive, iCloud, or Syncthing.

These are user-managed and not core features of the `auto-stack`.

## Key Takeaways

*   **Core Project Documentation:** Resides in `auto-stack/docs/` and `freqtrade/user_data/docs/`. These are accessible on the host filesystem.
*   **Manual Obsidian Integration:** Use symbolic links (WSL) or open directories directly in Obsidian for easy viewing and editing.
*   **Automated Obsidian Integration:** The `mcp/obsidian` server, combined with the Obsidian REST API plugin, offers powerful capabilities for programmatic interaction with your vault from `auto-stack` services. This is an advanced setup.
*   **User-Managed Options:** Cloning external documentation and vault synchronization are user-specific choices and responsibilities.
*   **Obsolete Practices:** References to Optuna or complex, unmaintained n8n git-sync workflows for core documentation are outdated. Focus on the methods described above.

---
This guide provides a foundation for integrating your Obsidian workflow with the `auto-stack` project. Choose the methods that best suit your needs, from simple manual access to advanced automation.
