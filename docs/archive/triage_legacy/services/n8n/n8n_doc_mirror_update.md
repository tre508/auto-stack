## Status: ⏳ To Be Rebuilt

# n8n Workflow: Automated Update for Mirrored Documentation Repositories (Optional)

⚠️ **CONTEXT WARNING & OPTIONAL FEATURE:** This document describes an **optional, advanced n8n workflow** for automatically running `git pull` on external documentation repositories that a user might choose to clone **locally** (e.g., into a personal Obsidian vault or similar local directory structure). This is **NOT** part of the baseline `automation-stack` functionality for document management, which primarily relies on shared Docker volumes (e.g., `automation-stack/docs` and `freqtrade-user_data/docs` being mounted into relevant containers).

Implementing this workflow requires specific configurations not present in the default `automation-stack` setup, most notably:
1.  Manually mounting a host directory (your local vault/documentation collection) into the n8n container.
2.  Enabling the `N8N_ALLOW_EXEC=true` environment variable for the n8n service, which has security implications and should be done with caution.

<!-- TODO: Review and update this guide if this git-sync feature is desired. -->
<!-- TODO: Clearly state this is an optional workflow requiring extra setup and security considerations (`N8N_ALLOW_EXEC`, host volume mount). -->
<!-- TODO: Remove references to Optuna. -->
<!-- TODO: Verify command examples and paths assuming the necessary prerequisites are met. -->
<!-- TODO: Update references to outdated documents like MasterSetup.md and Remotely Save context. -->

This workflow uses n8n to automatically run `git pull` within subdirectories where a user has cloned external official documentation repositories. This helps keep local mirrors up-to-date.

**Note:** If you use a tool like Obsidian with a sync plugin (e.g., the community plugin `Remotely Save`), this n8n workflow would update the *local* files, and then your chosen sync plugin would handle uploading those changes to your cloud storage. The `Remotely Save` plugin, or any similar tool, is an optional user setup and not a core component of the `automation-stack`.

## Goal

Periodically update the content of user-cloned mirrored Git repositories located in a local directory structure that is made accessible to n8n (e.g., `YourLocalVault/n8n_Docs`, `YourLocalVault/OpenWebUI_Docs`).

## Prerequisites
⚠️ These prerequisites describe a non-default, user-initiated setup that goes beyond the baseline `automation-stack`.

*   n8n running and accessible (part of the `automation-stack`).
*   `git` installed and accessible in the n8n Docker container (the default n8n images usually include git).
*   The user has cloned official documentation repositories into subdirectories on the Docker host machine (e.g., `<YOUR_LOCAL_VAULT_HOST_PATH>/docs/OpenWebUI_Docs`). (This is a manual user action).
*   **Crucial Prerequisite 1: Host Volume Mount for n8n:** You **must** manually edit your `automation-stack/docker-compose.yml` file. Find the `n8n` service definition and add a volume mount that maps your host directory containing the cloned git repositories to a path inside the n8n container. For example:
    ```yaml
    services:
      n8n: # Or your n8n service name
        # ... other n8n service config ...
        volumes:
          - n8n_data:/home/node/.n8n
          - <YOUR_LOCAL_VAULT_HOST_PATH>:/host_vault # <-- ADD THIS LINE
        # ... other n8n service config ...
    ```
    Replace `<YOUR_LOCAL_VAULT_HOST_PATH>` with the actual absolute path on your Docker host (e.g., `/mnt/c/Users/YourUser/MyObsidianVault` or `~/MyObsidianVault`). After editing, restart n8n: `docker compose up -d --force-recreate n8n`.
*   **Crucial Prerequisite 2: Enable Command Execution in n8n:** You **must** manually edit your `automation-stack/docker-compose.yml` (or `.env` file if `N8N_ALLOW_EXEC` is sourced from there). For the n8n service, add/set the environment variable `N8N_ALLOW_EXEC=true`. **USE WITH CAUTION:** Understand the security implications of allowing n8n to execute arbitrary commands. This is not enabled by default for security reasons.
    ```yaml
    services:
      n8n: # Or your n8n service name
        # ... other n8n service config ...
        environment:
          - N8N_ALLOW_EXEC=true # <-- ADD OR ENSURE THIS IS SET
        # ... other n8n environment variables ...
    ```
    Restart n8n after making this change.

## n8n Workflow Setup

1.  **Create a New Workflow:** Log in to n8n and create a new, empty workflow.

2.  **Add Trigger (Cron):**
    *   Click the '+' button to add a node.
    *   Search for and select the **Cron** node.
    *   **Mode:** Set the desired schedule (e.g., `Every Day`).
    *   **Hour:** Choose a time (e.g., `3` for 3 AM).
    *   **Timezone:** Set your local timezone.

3.  **Add Execute Command Node(s):** ⚠️ Requires `N8N_ALLOW_EXEC=true` and the host vault volume mount (e.g., to `/host_vault`) as described in Prerequisites.
    *   Connect an **Execute Command** node after the Cron trigger.
    *   **Execute In:** `CurrentContainer` (since git is in the n8n container and we are accessing a mounted volume).
    *   **Command:** Use the *container path* (e.g., `/host_vault/...`) to navigate and pull. Choose one option:
        *   _Option A (Single Node):_ Chain commands with `&&`. If one fails, subsequent pulls are skipped.
          ```bash
          cd /host_vault/<SUBPATH_TO_OPENWEBUI_DOCS_REPO> && git pull && cd /host_vault/<SUBPATH_TO_N8N_DOCS_REPO> && git pull && cd /host_vault/<SUBPATH_TO_OLLAMA_DOCS_REPO> && git pull
          ```
        *   _Option B (Separate Nodes):_ Create a separate node for each command. Allows individual error handling.
            *   Node 1: `cd /host_vault/<SUBPATH_TO_OPENWEBUI_DOCS_REPO> && git pull`
            *   Node 2: `cd /host_vault/<SUBPATH_TO_N8N_DOCS_REPO> && git pull`
            *   Node 3: `cd /host_vault/<SUBPATH_TO_OLLAMA_DOCS_REPO> && git pull`
        *   **(Important:** Adjust `/host_vault/<SUBPATH_TO_...>` based on your actual local directory structure that you mounted into `/host_vault` in the n8n container, and the names of your cloned documentation directories, e.g., `OpenWebUI_Docs`, `n8n_Docs`, `Ollama_Docs` etc. For example, if your host path `<YOUR_LOCAL_VAULT_HOST_PATH>/official_docs/OpenWebUI_Docs` is cloned, and `<YOUR_LOCAL_VAULT_HOST_PATH>` is mounted to `/host_vault`, then the path in the command would be `/host_vault/official_docs/OpenWebUI_Docs`.)
    *   **User:** Ensure the user running n8n inside the container (usually `node`) has appropriate *permissions* to write to the mounted volume directories if git operations require it (though `git pull` primarily reads and updates, it might write to `.git` folder). This usually isn't an issue if the host directory permissions are reasonable.
    *   Connect Trigger -> Execute Command(s).

4.  **Optional: Add Error Handling / Notifications:**
    *   Configure the `Settings` tab of each `Execute Command` node to handle errors (e.g., `Continue on Fail`).
    *   Add **IF** nodes to check the exit code (`{{ $json.exitCode }}`) of the command nodes.
    *   Add notification nodes (e.g., Discord, Slack) to report success or failure.

5.  **Save and Activate:** Save your n8n workflow and ensure it's activated.

## Testing

You can manually trigger the workflow using the 'Play' button in the n8n editor. Check the execution log for each `Execute Command` node to ensure it runs successfully and pulls updates (if any). Verify the file modification dates within your local mirrored directories on the host machine.

## Important Notes

*   **Path Accessibility:** The key is the correct mapping of your host directory to the container path (e.g. `/host_vault`) and using that container path in your n8n `Execute Command` nodes.
*   **Security:** Reiterating: enabling `N8N_ALLOW_EXEC=true` has security implications. Ensure n8n is properly secured (e.g., strong basic auth, network isolation as configured in `compose-mcp.yml` via Traefik labels).
*   **Interaction with Local Sync Tools:** This n8n workflow updates the *local files on the host machine* (via the Docker volume mount). If you use a separate desktop application or plugin (like Obsidian's `Remotely Save`) to sync these local files to cloud storage, that tool will operate on the files updated by this n8n workflow. This n8n workflow itself does not perform cloud synchronization.

<!-- deprecated: All OpenWebUI_Docs references are obsolete. Use Vercel AI Chat for LLM documentation and workflow integration. (May 2025) --> 