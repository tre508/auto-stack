# 🗂️ Docs Update Plan

**FINAL STATUS (as of 2025-05-13):**

- The stack now uses **Mem0** (with ChromaDB as vector store), **OpenRouter** (Gemini LLM), and **HuggingFace all-mpnet-base-v2** for embeddings.
- **OpenWebUI** and related docs/images have been fully removed.
- n8n, controller, and OpenRouter proxy are the main orchestrators.
- All legacy/obsolete files are marked for archival or have been replaced.
- Mem0 config is now loaded from file at runtime, supporting flexible backend swaps.
- The stack is fully open/free for both LLM and embeddings, with no paid API dependencies.
- See `config.yaml` and compose file for current architecture.

---

## ✅ Review Categories

- ✅ Still Valid: No changes needed except rephrasing or formatting
- ⏳ To Be Rebuilt: Structure stays but content needs modernization
- ❌ Obsolete Logic: Feature removed or tech deprecated, needs redesign

---

## 📁 Root Docs

| File Name             | Status        | Notes / TODOs                                                                 |
|----------------------|---------------|------------------------------------------------------------------------------|
| README_agent.md       | ⚠️ Blocked     | **NEEDS COMPLETE REWRITE.** Current version appears to have addressed removal of `.cursor` and old "host controller" references. Other TODOs remain: Update roles, new dir structure, new key files, new onboarding tasks, re-evaluate guiding rules & test instructions. **EDITING TOOL FAILED previously on larger updates.** Manual intervention likely required for full rewrite. |
| MasterSetup.md        | ⚠️ Archive & Replace | **MARKED FOR ARCHIVAL. DO NOT UPDATE FURTHER.** Contains extensive legacy context. Strategy is to replace with new, focused guides. Added prominent archival note to file. Original TODO: Major overhaul or break into smaller guides for current architecture. Refer to `README_agent.md` for current overview. |
| MasterSetup_Checklist.md | ⚠️ Deprecated     | **MARKED FOR ARCHIVAL.** Based on outdated `MasterSetup.md`. Added archival note to file. New checklists should be developed for the current architecture if needed. Original TODO: Rebuild or deprecate. |
| AutomationChecklist.md | ✅ Updated     | **CONTENT REBUILT.** File content appears largely up-to-date with current stack. Original TODOs for legacy refs seem addressed. Incremental updates are possible. Original status: `⚠️ Blocked` due to past full rewrite failures. |
| UserActionGuide.md    | ❌ Archived      | **MARKED FOR ARCHIVAL.** Almost entirely obsolete, tied to outdated `MasterSetup.md`. Added archival note to file. Original TODO: Archive or rewrite; decision is to archive. A new guide for the current stack may be needed separately. |
| TODO.md               | ✅ Replaced    | **REPLACED.** Original file moved to `depreciated/` by user. Superseded by the new `automation-stack/docs/TODO.md` (which is based on `setup/MasterGameplan.md`) and the detailed guides in `automation-stack/docs/setup/`. Original status: `⚠️ Archive & Replace`. |
| INDEX.md              | ✅ Rebuilt     | **REGENERATED & REPLACED.** New index created based on current `docs/` directory structure, excluding `OpenWebUI_Docs/`. Original status: `⚠️ Blocked`. |
| obsidian_service_docs.md | ✅ Updated     | **UPDATED.** Rewritten to reflect current doc sharing via Docker volumes (`/automation-stack/docs/`, `/freqtrade/user_data/docs/`). Removed Optuna references. Clarified distinction between core project doc access and optional user-managed Obsidian integrations (e.g., `Remotely Save`, external git clones). Original TODOs addressed. |
| proxy.md              | ✅ Updated     | **INTEGRATED & UPDATED.** Node.js OpenRouter proxy is now a containerized service (`openrouter_proxy_mcp`) in `compose-mcp.yml`. Document updated to reflect this, including setup via `.env`, Traefik routing, and usage as a managed service. Original TODOs addressed. |
| pipe_mcp.md           | ✅ Updated     | **UPDATED.** Emphasized its advanced/optional nature and that it's not a baseline feature. Stated that inclusion of `mcpo`/MCP tools is a pending decision. Advised users to consult official `mcpo` docs for up-to-date setup information. Original TODOs addressed. |

---

## 📁 `n8n/` Subdirectory

| File Name             | Status        | Notes / TODOs                                                                 |
|----------------------|---------------|------------------------------------------------------------------------------|
| webhookFlows.md       | ✅ Updated     | **NEW FILE CREATED.** Describes n8n webhook integration with `controller.py` (`/execute`, `/notify` endpoints) and general n8n webhook patterns. Addresses original TODO. |
| vaultSync.md          | ✅ Still Valid | Validate cron setup and file path logic for `/host_vault`                   |

---

## 📁 `deprecated/` Subdirectory

| File Name             | Status        | Notes / TODOs                                                                 |
|----------------------|---------------|------------------------------------------------------------------------------|
| cloudSetup.md         | ⚠️ Missing (directory not found) | Directory `automation-stack/docs/deprecated/` not found. Original status: ❌ Obsolete Logic. Original TODO: Was tied to Replit—replace with self-hosted Docker flow. |
| legacyNetworkMap.md   | ⚠️ Missing (directory not found) | Directory `automation-stack/docs/deprecated/` not found. Original status: ⏳ To Be Rebuilt. Original TODO: Update for new `mcp-net` topology and hostname-based routing. |
| agent_pipes.txt       | ⚠️ Missing (directory not found) | Directory `automation-stack/docs/deprecated/` not found. Original status: ⏳ To Be Rebuilt. Original TODO: Refactor as diagram showing webhook and container traffic. |

---

## 📁 n8n Docs (`automation-stack/docs/n8n/`)

| File Name                             | Status        | Notes / TODOs                                                                 |
|--------------------------------------|---------------|------------------------------------------------------------------------------|
| n8n_multi_agent_concepts.md          | ✅ Updated     | **UPDATED.** Examples updated for current stack (FastAPI controller, devcontainer Freqtrade, OpenWebUI+Ollama, Docker volumes). API interactions (esp. OpenWebUI via `/v1/chat/completions`) clarified. Legacy document references removed/updated. Original high-level concepts remain valid. |
| n8n_doc_mirror_update.md             | ✅ Updated     | **UPDATED.** Clarified optional nature, detailed non-default prerequisites (host mount, N8N_ALLOW_EXEC) with examples and security warnings. Removed Optuna references. Updated legacy refs. Placeholder paths in commands clarified. Contrasted with baseline volume sharing for docs. |
| n8n_cursor_freqtrade_integration.md | ❌ Obsolete Logic | **ANNOTATED.** Entirely based on old architecture (host controller, Pipe, `freqbot` service, etc.). TODO: Archive. Create new integration plan doc for current architecture. |
| n8n_freqtrade_webhook_ideas.md       | ✅ Updated     | **UPDATED.** Evaluated patterns for current stack, emphasizing API Polling as recommended. Detailed Freqtrade API config (enable, auth, network) and n8n workflow (JWT auth, polling) for `freqtrade_devcontainer:8080`. Updated DB monitoring and Log parsing with current stack specifics (shared volumes, networked DBs, N8N_ALLOW_EXEC). |
| n8nChat.md                           | ✅ New         | **NEW FILE.** Describes the n8nChat browser extension for AI-assisted n8n workflow development. Added by user. |

---

## 📁 Deprecated Docs (`automation-stack/docs/depreciated/`)

| Item                  | Status            | Notes / TODOs                                                                                                                               |
|-----------------------|-------------------|---------------------------------------------------------------------------------------------------------------------------------------------|
| (All files within)    | ❌ Deprecated     | Files in this directory are explicitly deprecated. While they might contain salvageable code snippets or concepts from previous iterations, they should **not** be treated as relevant to the current architecture without thorough review and adaptation. Assume all instructions, configurations, and workflows described within are obsolete. |

---

## 🧩 Next Steps

1. As you update each file, prepend a `## Status:` section with one of the three categories
2. Keep original content intact—strike through or annotate outdated parts instead of deleting
3. When all files are processed, mark this checklist complete and archive as `DocsUpdateHistory.md`

---

## Version Log: 2025-05-13

**Doc Sync Operation:**
- **Files Modified:**
  - docs/setup/Freqtrade_Project_Checklist.md
  - docs/setup/MasterGameplan.md
  - docs/Agent-Orientation.md
  - docs/AutomationChecklist.md
  - docs/README_agent.md
  - docs/TODO.md
- **Sections Updated:**
  - Agent orchestration and role descriptions (all files)
  - Unified logging requirements and verification steps
  - Modular, scalable multi-agent orchestration pattern references
  - Checklist and TODO items for agent presence, logging, and workflow testing
- **Summary:**
  - Synchronized all documentation to explicitly require CentralBrain_Agent, manager agents (FreqtradeManager, FreqAIManager, ResearchManager, UtilityManager), and sub-agents as the current model.
  - Updated all checklists, onboarding, and status sections to reference modular, scalable multi-agent orchestration and unified logging (see CentralBrain.md, UnifiedLogging.md).
  - Ensured cross-file consistency for agent roles, logging, and integration verification.
  - No legacy/obsolete content was reintroduced; all changes are idempotent and reflect the current system state.

---

## 2025-05-14: Documentation Sync & Workflow Template Generation

- **Phase 1:** Synchronized terminology, agent roles, node types, and trigger patterns across:
  - n8n_multi_agent_concepts.md
  - command-prompt-style-guide.md
  - n8nChat_prompt_templates.md
  - UnifiedLogging.md
  - n8n_freqtrade_webhook_ideas.md
  - webhookFlows.md
- **Phase 2:** Cross-checked and updated AgentHub.md and CentralBrainFlow.md for agent/role/diagram consistency.
- **Phase 3:** Planned and outlined high-quality n8n workflow .json templates for all referenced automations:
  - n8n_workflow_CentralBrain_Agent.json
  - n8n_workflow_FreqtradeSpecialist_Agent.json
  - n8n_workflow_Backtest_Agent.json
  - n8n_workflow_UnifiedLogging.json
  - n8n_workflow_Summarization_Agent.json
  - n8n_workflow_LLM_Research_Trigger.json
  - n8n_workflow_Docker_Health_Check.json
  - n8n_workflow_Git_Repo_Commit_Notifier.json
- All templates standardized on naming conventions and validated against latest n8n best practices.
- See MCP memory for detailed sync and planning logs.

---

## OpenWebUI Sunset — Replaced with Vercel AI Chat

- All references to OpenWebUI across code, documentation, and workflow templates have been removed, rewritten, or commented out.
- Vercel AI Chat is now the standard LLM/chat front-end for the automation-stack.
- All API endpoints, workflow nodes, and configuration variables updated to use Vercel AI Chat equivalents.
- Diagrams, prompt templates, and agent orchestration docs updated for the new system.
- Legacy OpenWebUI context preserved as comments where historically relevant.
- Removed legacy OpenWebUI support — migrated to Vercel AI Chat stack (May 2025).