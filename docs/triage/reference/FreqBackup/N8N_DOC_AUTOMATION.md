# N8N Documentation Automation Proposal for Auto-Stack

This document outlines a proposed n8n workflow for automating parts of the documentation management process within the `auto-stack` project. It adapts concepts from the legacy `obsidian_service_docs.md` and aligns with the existing documentation structure and guidelines (e.g., `00_MasterSetup.md`, `AutomationChecklist.md`).

## 1. Goals

*   Streamline the process of updating and integrating new documentation.
*   Ensure consistency in documentation structure and linking.
*   Reduce manual effort in maintaining master documentation files.
*   Provide a clear audit trail for documentation changes via git.

## 2. Proposed N8N Workflow: "Docs Sync & Index"

This workflow would monitor a specific directory for new or updated markdown files and then process them.

**Trigger:**
*   **Type:** Filesystem Trigger (or Webhook if preferred for manual triggering via a script/UI).
*   **Path to Watch:** A designated "drafts" or "staging" subdirectory within `docs/`, e.g., `docs/staging/` or `docs/triage/new_contributions/`.
*   **Events:** Watch for `create` and `update` events for `*.md` files.

**Workflow Steps:**

1.  **Receive File Event:**
    *   Get the path and filename of the new/updated markdown file.

2.  **(Optional) Validate/Lint Markdown:**
    *   **Node:** Execute Command
    *   **Command:** Run a markdown linter (e.g., `markdownlint-cli`) against the file.
    *   **Action on Failure:** Log error, send notification, and halt processing for this file.

3.  **Extract Metadata (Optional but Recommended):**
    *   **Node:** Code (JavaScript) or HTTP Request (if a microservice for parsing frontmatter exists).
    *   **Logic:** Parse YAML frontmatter from the markdown file (e.g., `title`, `category`, `tags`, `related_docs`). This metadata can be used for more intelligent processing.
    *   If no frontmatter, use filename or heuristics to determine category.

4.  **Determine Target Directory:**
    *   **Node:** Switch or If
    *   **Logic:** Based on metadata (e.g., `category`) or file path conventions, determine the correct final subdirectory within `docs/` (e.g., `docs/triage/services/`, `docs/triage/integrations/`).
    *   **Default:** Move to a general review area if category is unclear.

5.  **Move File to Target Directory:**
    *   **Node:** Move File
    *   **Action:** Move the processed markdown file from the staging/drafts area to its determined target directory. Overwrite if an older version exists (or implement versioning).

6.  **Update Master Index/Documentation Files:**
    *   This is a critical step and may involve multiple sub-steps or parallel branches.
    *   **Target Files:**
        *   `docs/triage/00_MasterSetup.md`
        *   `docs/triage/AutomationChecklist.md`
        *   Relevant sub-index files (e.g., `docs/triage/reference/index.md`)
    *   **Logic for each target file:**
        *   **Node:** Read File (to get current content of the master doc).
        *   **Node:** Code (JavaScript) or Set
            *   **Logic:** Append or insert a link/reference to the new/updated document in the appropriate section. This might involve regex, string manipulation, or marker-based insertion (e.g., `<!-- DOCS_HOOK:services -->`).
            *   Ensure formatting consistency.
        *   **Node:** Write File (to save the updated master doc).

7.  **Git Commit and Push:**
    *   **Node:** Execute Command
    *   **Commands:**
        *   `git add .` (or `git add <specific_file_paths>`)
        *   `git commit -m "docs: Auto-update - Added/Updated [filename] and relevant indexes"`
        *   `git push` (ensure credentials/SSH keys are configured for the n8n execution environment)

8.  **Notification:**
    *   **Node:** (e.g., Email, Discord, Slack, Mattermost - depending on `auto-stack` communication tools)
    *   **Message:** "Documentation updated: [filename] has been processed and integrated. Relevant indexes updated. Git commit: [commit_hash]."

## 3. Configuration and Setup

*   **N8N Credentials:**
    *   Git credentials (SSH key or token).
    *   Notification service credentials.
*   **Environment Variables:**
    *   Paths for staging, target directories.
    *   Git repository path.
*   **File Structure Conventions:**
    *   Define clear conventions for naming files and using frontmatter to aid automated processing.

## 4. Considerations & Enhancements

*   **Error Handling:** Implement robust error handling at each step (e.g., file not found, git command fails, API errors).
*   **Idempotency:** Design the workflow to be idempotent where possible (e.g., re-running on an already processed file doesn't cause issues).
*   **Dry Run Mode:** Implement a "dry run" parameter for testing the workflow without making actual file changes or git commits.
*   **Manual Approval Step:** For critical documentation, an optional manual approval step (e.g., via an email link or a specific n8n node) could be inserted before committing to git.
*   **Conflict Resolution:** Git conflicts are a potential issue. The workflow should ideally not attempt complex merges. Simpler strategies involve failing on conflict and notifying an admin.
*   **Integration with `pipe_mcp.md` concepts:** If the `auto-stack` uses an agent for documentation tasks, this n8n workflow could be triggered by the agent or could notify the agent upon completion.

## 5. Alignment with `doc-engineering-guidelines.mdc`

*   **Avoid Duplication:** The workflow helps by centralizing the addition of new docs and updating master files, reducing the chance of manual duplication errors.
*   **Master File Updates:** Steps are explicitly included to update `MasterSetup.md` and `AutomationChecklist.md`.
*   **Heading Consistency:** While this workflow doesn't enforce heading consistency *within* a document, it ensures the document is placed and linked correctly. Linting (Step 2) could be extended for this.

This proposed n8n workflow provides a starting point for automating documentation management in `auto-stack`. It can be implemented iteratively, starting with core functionality and adding enhancements over time.
