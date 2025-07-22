# 🗂 Documentation Index

Manually curated table of contents for the automation-stack documentation. This index covers all documentation categories and provides navigation for both canonical and legacy content.

## 📖 Quick Navigation

- [**Setup**](#setup) - Getting started and initial configuration
- [**Services**](#services) - Individual service documentation and tasklists
- [**Prompts**](#prompts) - AI prompt engineering and templates
- [**Reference**](#reference) - Technical reference and architecture docs
- [**Troubleshooting**](#troubleshooting) - Debugging guides and solutions
- [**Legacy Content**](#legacy-content) - Content pending migration
- [**Deprecated**](#deprecated) - Archived and superseded documentation

---

## Setup

Canonical setup documentation following the standardized workflow:

- [`00_MasterSetup.md`](../setup/00_MasterSetup.md) - Prerequisites and initial configuration
- [`01_Automation.md`](../setup/01_Automation.md) - Automation stack services setup  
- [`02_Trading.md`](../setup/02_Trading.md) - Freqtrade development environment
- [`03_Core_Services_Configuration_and_Verification.md`](../setup/03_Core_Services_Configuration_and_Verification.md) - Service verification procedures
- [`04_Cross_Stack_Integration_Guide.md`](../setup/04_Cross_Stack_Integration_Guide.md) - Integration testing
- [`05_Agent_Capabilities_and_Interaction.md`](../setup/05_Agent_Capabilities_and_Interaction.md) - Agent capabilities
- [`06_Developer_Tools.md`](../setup/06_Developer_Tools.md) - Development tooling
- [`index.md`](../setup/index.md) - Auto-generated setup navigation

### Legacy Setup Files (Pending Consolidation)
- [`01_Automation_Stack_Overview.md`](../setup/01_Automation_Stack_Overview.md) - ⚠️ Should be merged into 01_Automation.md
- [`freqtrade_installation.md`](../setup/freqtrade_installation.md) - ⚠️ Should be integrated into 02_Trading.md
- [`Freqtrade_Project_Checklist.md`](../setup/Freqtrade_Project_Checklist.md) - ⚠️ Should be integrated into 02_Trading.md

---

## Services

Canonical service documentation with standardized Tasklist.md structure:

### Core Services
- [`controller/Tasklist.md`](../services/controller/Tasklist.md) - FastAPI orchestration gateway
- [`mem0/Tasklist.md`](../services/mem0/Tasklist.md) - Memory management and RAG capabilities
- [`eko/Tasklist.md`](../services/eko/Tasklist.md) - AI agent service with Node.js implementation
- [`n8n/Tasklist.md`](../services/n8n/Tasklist.md) - Workflow automation platform
- [`freq-chat/Tasklist.md`](../services/freq-chat/Tasklist.md) - Next.js chat interface with Vercel deployment
- [`proxy/Tasklist.md`](../services/proxy/Tasklist.md) - OpenRouter API proxy service

---

## Prompts

AI prompt engineering resources organized by category:

- [`README.md`](../prompts/README.md) - Prompt library overview and usage guidelines
- [`intelligence/README.md`](../prompts/intelligence/README.md) - AI agent system prompts and templates
- [`orchestration/README.md`](../prompts/orchestration/README.md) - Multi-agent workflow and n8n integration prompts
- [`integration/README.md`](../prompts/integration/README.md) - Cross-service communication patterns
- [`debugging/README.md`](../prompts/debugging/README.md) - Diagnostic and troubleshooting prompts

---

## Reference

Technical reference documentation and architecture guides:

### Architecture & Integration
- [`Dual-Stack_Architecture.md`](./Dual-Stack_Architecture.md) - System architecture overview
- [`eko_integration_guide.md`](./eko_integration_guide.md) - EKO service integration patterns
- [`fresh-scaffold.md`](./fresh-scaffold.md) - Canonical project structure template
- [`fresh-start.md`](./fresh-start.md) - Documentation cleanup and migration status

### Technical References
- [`environment_variables.md`](./environment_variables.md) - Complete environment variable index
- [`mcp-tool-list.md`](./mcp-tool-list.md) - Available MCP tools for Cursor integration
- [`mcp_tools_reference.md`](./mcp_tools_reference.md) - MCP tool configuration and usage
- [`obsidian_service_docs.md`](./obsidian_service_docs.md) - Obsidian integration documentation

### Meta Documentation
- [`docs-update-history.md`](./docs-update-history.md) - Documentation change history
- [`docs-index.md`](./docs-index.md) - This comprehensive index
- [`agent-task.md`](./agent-task.md) - Agent task management patterns
- [`phase 5.md`](./phase 5.md) - Phase 5 standardization instructions

---

## Troubleshooting

Debugging guides and common issue resolution:

- [`TROUBLESHOOTING.md`](../troubleshooting/TROUBLESHOOTING.md) - General troubleshooting procedures
- [`legacy_memory_migration_cleanup.md`](../troubleshooting/legacy_memory_migration_cleanup.md) - Memory system migration issues
- [`vercel/troubleshooting.md`](../troubleshooting/vercel/troubleshooting.md) - Vercel deployment issues
- [`vercel/troubleshoot_mem0.md`](../troubleshooting/vercel/troubleshoot_mem0.md) - Mem0-Vercel integration issues

---

## Legacy Content

Documentation pending migration to canonical structure:

### EKO Service (→ services/eko/)
- [`eko/eko_AgentPrompt.md`](../eko/eko_AgentPrompt.md) - ⚠️ Migrate to services/eko/Tasklist.md
- [`eko/eko_Notes.md`](../eko/eko_Notes.md) - ⚠️ Migrate to services/eko/Tasklist.md  
- [`eko/eko_Tasklist.md`](../eko/eko_Tasklist.md) - ⚠️ Consolidate into services/eko/Tasklist.md
- [`eko/eko_Troubleshooting.md`](../eko/eko_Troubleshooting.md) - ⚠️ Migrate to troubleshooting/

### Mem0 Service (→ services/mem0/)
- [`mem0/Mem0_Integration_Guide.md`](../mem0/Mem0_Integration_Guide.md) - ⚠️ Migrate to services/mem0/Tasklist.md
- [`mem0/Mem0_Troubleshooting_Central.md`](../mem0/Mem0_Troubleshooting_Central.md) - ⚠️ Migrate to troubleshooting/

### n8n Service (→ services/n8n/)
- [`n8n/alternatives.md`](../n8n/alternatives.md) - n8n alternative solutions
- [`n8n/community-nodes.md`](../n8n/community-nodes.md) - Community node documentation
- [`n8n/n8nChat.md`](../n8n/n8nChat.md) - n8nChat integration guide
- [`n8n/webhookFlows.md`](../n8n/webhookFlows.md) - Webhook workflow patterns
- [`n8n/workflows/`](../n8n/workflows/) - Workflow documentation
- [`n8n/templates/`](../n8n/templates/) - Workflow template library
- [`n8n/prompt_library/`](../n8n/prompt_library/) - ⚠️ Migrate to prompts/orchestration/

### Intelligence (→ prompts/intelligence/)
- [`intelligence/agent.prompt.md`](../intelligence/agent.prompt.md) - ⚠️ Migrated to prompts/intelligence/README.md

### Vercel/freq-chat (→ services/freq-chat/)
- [`vercel/integration.md`](../vercel/integration.md) - ⚠️ Migrate to services/freq-chat/Tasklist.md
- [`vercel/setup.md`](../vercel/setup.md) - ⚠️ Migrate to services/freq-chat/Tasklist.md
- [`vercel/usage.md`](../vercel/usage.md) - ⚠️ Migrate to services/freq-chat/Tasklist.md
- [`vercel/nextjs_ai_chatbot_customization.md`](../vercel/nextjs_ai_chatbot_customization.md) - Customization guide

### Guides & Checklists (→ setup/)
- [`guides/MasterGameplan.md`](../guides/MasterGameplan.md) - ⚠️ Duplicate of setup content
- [`guides/MasterSetup.md`](../guides/MasterSetup.md) - ⚠️ Duplicate of setup/00_MasterSetup.md
- [`guides/freqtrade_installation.md`](../guides/freqtrade_installation.md) - Freqtrade setup guide
- [`guides/MCP_Filesystem_Setup_Guide.md`](../guides/MCP_Filesystem_Setup_Guide.md) - MCP filesystem guide
- [`checklists/AutomationChecklist.md`](../checklists/AutomationChecklist.md) - ⚠️ Integrate into service tasklists
- [`checklists/MasterSetup_Checklist.md`](../checklists/MasterSetup_Checklist.md) - ⚠️ Integrate into setup guides

---

## Deprecated

Archived documentation moved to prevent confusion:

See [`deprecated/DEPRECATION_MANIFEST.md`](../deprecated/DEPRECATION_MANIFEST.md) for complete list of deprecated files and migration rationale.

### Key Deprecated Content
- Old setup guides with duplicate content
- Scattered service documentation replaced by canonical Tasklist.md files  
- Outdated integration guides superseded by reference documentation
- Legacy tooling configurations moved to proper locations

---

## Root Documentation

High-level orientation and meta documentation:

- [`Agent-Orientation.md`](../Agent-Orientation.md) - Agent onboarding and orientation guide
- [`README_agent.md`](../README_agent.md) - Autonomous agent quick start guide
- [`TODO.md`](../TODO.md) - Outstanding tasks and feature requests

---

## Maintenance Procedures

### Updating Documentation Index

**Manual Update Checklist:**
- [ ] Review new files added to docs/ directory
- [ ] Check for files moved between categories  
- [ ] Update section links and descriptions
- [ ] Verify all links are functional
- [ ] Update legacy content migration status
- [ ] Add deprecation notices for superseded files

### Adding New Documentation

**Template for New Reference Docs:**
```markdown
# 📋 [Title]

[Brief description]

## [Main Content Sections]

---

*Last updated: [Date]*
*Part of: [Phase/Category]*
```

**Example Commit Message:**
```
docs(reference): add [filename] - [brief description]

- Added comprehensive [type] documentation
- Includes [key sections]
- Cross-referenced with [related docs]
- Part of Phase [X] standardization
```

### Future Maintenance Tasks

1. **Phase 6**: Complete legacy content migration
2. **Automated Index Generation**: Script to auto-update this index
3. **Link Validation**: Automated checking for broken internal links
4. **Content Auditing**: Regular review of outdated information
---

*Last updated: 2025-05-23 07:03 UTC+2*  
*Part of Phase 5: Reference Standardization*  
*Total files indexed: 150+ across all categories*
