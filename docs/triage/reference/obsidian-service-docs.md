## Status: ⏳ To Be Rebuilt

# Obsidian & Project Documentation Integration Guide

⚠️ **LEGACY CONTEXT / PARTIALLY OUTDATED:** This guide discusses integrating project documentation and personal notes into an Obsidian vault. While local knowledge management with Obsidian is a valid approach, this document requires updates to align with the current `automation-stack` architecture and how documentation is accessed.

<!-- TODO: Review and update this guide. -->
<!-- TODO: Clarify how current shared documentation (via Docker volumes in `automation-stack/docs` and `freqtrade/user_data/docs`) can be best accessed or integrated with a user's Obsidian setup on the host. -->
<!-- TODO: Remove references to Optuna. -->
<!-- TODO: Clearly distinguish between core stack features (like shared Docker volumes) and optional user-managed integrations (like `Remotely Save` or direct git cloning into a personal vault). -->

## Understanding Documentation Access in This Project

The `automation-stack` and the integrated `freqtrade` environment provide documentation primarily through shared Docker volumes. This means directories from the host machine are mounted into the relevant containers, and also accessible directly on your host system.

*   **`automation-stack` Documentation:** Located in `/automation-stack/docs/` on your host machine. This includes this guide, `n8n` documentation, etc.
*   **`freqtrade` User Documentation:** Located in `/freqtrade/user_data/docs/` on your host machine. This is the recommended place for your personal Freqtrade strategies, notes, and related documentation.

## Integrating Project Docs with Your Obsidian Vault

You can integrate these project-provided documentation sources into your personal Obsidian vault using symbolic links or by directly opening them in Obsidian.

### Goal: Access Project Docs in Obsidian

*   Access and edit your personal Freqtrade notes (from `freqtrade/user_data/docs/`) within Obsidian.
*   View `automation-stack` documentation (like `n8n` docs) within Obsidian.

### Recommended Approach: Symbolic Links (or Direct Opening)

#### 1. Linking Your Personal `freqtrade/user_data/docs/`

This allows you to manage your Freqtrade strategies, configurations, and notes directly within your Obsidian vault.

**On your host machine (from a WSL or other Bash terminal):**

```bash
# Navigate to your Obsidian Vault's root directory (e.g., in /mnt/c/Users/...)
# cd /path/to/your/MyObsidianVault

# Create a symbolic link to your Freqtrade user docs
# Adjust <PATH_TO_YOUR_FREQTRADE_PROJECT_ROOT> accordingly
# Example: ~/projects/freqtrade
ln -s /path/to/your/freqtrade/user_data/docs MyFreqtradeUserDocs
```
Replace `/path/to/your/freqtrade` with the absolute path to the root of your `freqtrade` project directory within the WSL filesystem.

#### 2. Linking `automation-stack/docs/` (Optional)

If you want to browse the general `automation-stack` documentation (like `n8n` docs, etc.) directly within your vault:

```bash
# Navigate to your Obsidian Vault's root directory
# cd /path/to/your/MyObsidianVault

# Create a symbolic link to the automation-stack docs
# Adjust <PATH_TO_YOUR_AUTOMATION_STACK_PROJECT_ROOT> accordingly
# Example: ~/projects/auto-stack
ln -s /path/to/your/auto-stack/docs AutomationStackDocs
```
Replace `/path/to/your/auto-stack` with the absolute path to your `automation-stack` project directory within the WSL filesystem.

**Alternative:** Instead of symbolic links, you can often open these directories as existing vaults or add them to your Obsidian workspace, depending on your Obsidian version and preferences.

## Optional: Integrating External Official Documentation

The `automation-stack` already includes some mirrored documentation (e.g., in `automation-stack/docs/n8n_Docs`). If you wish to maintain your own local clones of other official documentation for software like n8n or Ollama *within your personal Obsidian vault*, you can do so using `git`.

**This is an optional, user-managed setup.**

### Example: Cloning External Docs into Your Vault

Inside your Obsidian vault folder (e.g., `MyObsidianVault/`):

```bash
# Example: Clone official n8n docs (read-only)
git clone https://github.com/n8n-io/n8n-docs.git n8n_Official_Docs_Mirror
# Example: Clone official Ollama docs (read-only)
git clone https://github.com/ollama/ollama.git Ollama_Official_Docs_Mirror
```
You can add `--depth 1` to `git clone` for a faster initial download (latest snapshot only).

### Keeping External Clones Updated (User-Managed)

If you choose to clone external repositories into your vault, you are responsible for keeping them updated. This can be done manually or via your own scripts.

```bash
# Example: Manual update for one of your cloned repos
# cd path/to/your/MyObsidianVault/n8n_Official_Docs_Mirror
# git pull
```
The n8n workflow mentioned in previous versions of this document (`n8n_doc_mirror_update.md`) for automating `git pull` is an advanced, optional feature that you would need to set up and manage yourself if desired. It is not a core component of the `automation-stack`.

## Optional: Obsidian Vault Sync (e.g., `Remotely Save`)

Synchronizing your Obsidian vault (including its configuration, plugins, and content) across multiple devices or for backup purposes is a common user requirement. Plugins like `Remotely Save` can be used for this.

**This is an optional, user-managed setup and not a core feature of the `automation-stack`.**

If you choose to use such plugins:
*   Follow the specific plugin's documentation for setup (e.g., configuring with S3, OneDrive, etc.).
*   Be aware that `MasterSetup.md`, which previously contained notes on `Remotely Save`, is outdated and marked for archival.

## Key Takeaways for Documentation & Obsidian

*   **Core Project Docs:** Accessed via shared Docker volumes, available on your host at `/automation-stack/docs/` and `/freqtrade/user_data/docs/`.
*   **Obsidian Integration:** Use symbolic links or open these host directories directly in Obsidian.
*   **External Docs & Sync:** Cloning other repositories or using cloud sync plugins for your vault are **optional, user-managed activities.**
*   **Obsolete References:** Mentions of Optuna, older `Remotely Save` instructions in `MasterSetup.md`, or complex n8n git-sync workflows for core documentation are no longer current.

---
*Previous content below might be heavily outdated and is kept for historical reference during rewrite.*
<!-- The original content of the file can be preserved below this line if needed, or removed if fully superseded. -->
<!-- For this update, we are largely replacing the old content. -->

## 🧠 Optional: Use n8n to auto-sync + update index notes
(Combine this with the `git pull` workflow from Step 3)
⚠️ This is an advanced, optional feature based on a custom n8n workflow.

Set up an n8n cron job (`n8n_doc_mirror_update.md`):

*   Pull all official repos weekly/daily.
*   (Optional) After pulls, use n8n nodes (e.g., Read File, Function, Write File) to create or update a master index note (`_Index.md`) with links or summaries of changes.


✅ Final Tips
Name each folder in your vault with a Docs suffix to avoid namespace clashes.

Add an _Index.md to each docs repo if it doesn\'t exist for faster navigation inside Obsidian.

If your vault gets big, use a tagging convention like #n8n, #VercelChat, #freqtrade, etc.
