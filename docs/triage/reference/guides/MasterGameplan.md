# Master Gameplan

**Version:** 1.0
**Date:** 2025-05-11

## 1. Overall Project Vision & Mission

*   **Vision Statement:** (A long-term, aspirational goal for the project)
*   **Mission Statement:** (The current primary objective and purpose of the project)
*   **Core Values/Principles:** (Guiding principles for development and operation)

## 2. Key Strategic Goals (Next 3-6 days)

1. **Complete Cross-Stack Integration Validation**
   - Verify bi-directional API communication between Freqtrade and automation-stack (n8n, FastAPI Controller) using real test workflows.
   - Document all integration points and update troubleshooting guides with any new findings.

2. **Deploy and Test Modular Multi-Agent Orchestration**
   - Ensure CentralBrain_Agent, manager agents (FreqtradeManager, FreqAIManager, ResearchManager, UtilityManager), and sub-agents are running, discoverable, and able to trigger/aggregate tasks via HTTP webhooks.
   - Validate agent handoff, error handling, and fallback logic in at least two real-world scenarios.

3. **Enforce Unified Logging Across All Agents**
   - Confirm all agents log to the unified PostgreSQL table with the correct `agent` field and schema (see UnifiedLogging.md).
   - Run log aggregation and reporting queries to verify data integrity and completeness.

4. **Synchronize and Audit Project Documentation**
   - Ensure all onboarding, checklist, and architecture docs reflect the current agent model, logging, and integration patterns.
   - Run DocsSyncAudit_MCP and SummarizeDocs_MCP to flag and resolve any documentation drift.

5. **Validate End-to-End Automated Workflows**
   - Execute at least one full workflow from VercelAI Chatbot → CentralBrain_Agent → Freqtrade API → logging/reporting, and document the results.
   - Capture and resolve any edge cases or integration failures.

6. **Prepare for Next-Phase Expansion**
   - Identify and document any blockers or technical debt that could impact scaling, security, or maintainability in the next sprint.
   - Propose at least two improvements or optimizations for agent orchestration or cross-stack communication.

## 3. Current System Architecture Focus

*   **Primary Stacks:** `automation-stack`, `freqtrade` (Dev Container)
*   **Key Services Under Active Development/Refinement:** (e.g., FastAPI Controller, specific n8n workflows, new FreqAI models)
*   **Integration Points of Focus:** (e.g., Controller-Freqtrade API link, n8n-LLM interaction for reporting)
*   **Multi-Agent Documentation & Task Orchestration Hub:** Implementation and refinement of agent orchestration workflows (CentralBrain_Agent, DocAgent, FreqtradeSpecialist_Agent) for intelligent documentation management and automation.

## 4. Technology Stack & Standards

*   **Core Technologies:** Docker, Docker Compose, Python (FastAPI, Freqtrade), Node.js (n8n, VercelAI Chatbot), Traefik.
*   **Coding Standards/Linters:** (e.g., Black, Flake8 for Python; Prettier for JS/Markdown)
*   **Documentation Standards:** (e.g., Markdown format, use of `DocsUpdatePlan.md` for tracking, target audience for new docs)
*   **Version Control:** Git (with specific branching strategy if any, e.g., GitFlow, feature branches)

## 5. Key Stakeholders & Roles (Optional)

*   **Project Lead/Owner:**
*   **Lead Developer(s):**
*   **AI Agent(s):** (Responsibilities outlined in `05_Agent_Capabilities_and_Interaction.md`)
    *   Multi-agent hierarchy: CentralBrain_Agent, manager agents (FreqtradeManager, FreqAIManager, ResearchManager, UtilityManager), DocAgent(s), FreqtradeSpecialist_Agent, and specialized sub-agents for modular, scalable automation and documentation (see CentralBrain.md).
*   **Users/Testers:**

## 6. Risk Assessment & Mitigation (Optional)

| Risk ID | Description of Risk | Likelihood (H/M/L) | Impact (H/M/L) | Mitigation Strategy |
|---|---|---|---|---|
| R001  |                     |                    |                |                     |
| R002  |                     |                    |                |                     |

## 7. Communication Plan (Optional)

*   **Regular Updates:** (e.g., Daily stand-ups, weekly summaries)
*   **Documentation:** Primary source of truth for system state and plans.
*   **Issue Tracking:** (e.g., GitHub Issues, specific project management tool)

## 8. Future Roadmap Ideas (Post 6 Months - Long Term)

(Brainstorming section for features or capabilities not in the immediate strategic goals)

*   [Idea 1]
*   Multi-Agent Documentation & Task Orchestration Hub for scalable, intelligent automation and documentation processing.
*   [Idea 2]
*   [Idea 3]

## 9. Current Status, TODOs, and Fresh Start Guide

### A. Current automation-stack Status (see AutomationChecklist.md for live status)
- Core services (Traefik, n8n, Controller, OpenRouter Proxy) are rebuilt and routed via Traefik.
- FastAPI Controller exposes /execute and /notify endpoints for n8n integration (see webhookFlows.md).
- Multi-agent orchestration (CentralBrain_Agent, manager agents (FreqtradeManager, FreqAIManager, ResearchManager, UtilityManager), sub-agents) is defined and partially implemented (see CentralBrain.md).
- Unified logging schema (PostgreSQL, agent field) is designed and being implemented for all agents (see UnifiedLogging.md).
- Cross-stack integration (Controller <-> Freqtrade API, n8n <-> Controller) is in progress; see checklist for verification steps.

### B. Key TODOs (see TODO.md and AutomationChecklist.md for full lists)
- [ ] Complete verification of all core services and endpoints (AutomationChecklist.md)
- [ ] Implement and test unified logging for all agents (UnifiedLogging.md)
- [ ] Finalize and verify modular, multi-agent orchestration workflows (CentralBrain.md, n8nChat_prompt_templates.md)
- [ ] Test and document FastAPI Controller/n8n integration (/execute, /notify) (webhookFlows.md)
- [ ] Complete Freqtrade devcontainer setup and integration (see below)

### C. How to Start Over Fresh with Freqtrade Stack & Integrate with automation-stack

1. **Remove old containers/volumes if needed:**
   - `docker compose down -v` in both automation-stack and freqtrade directories.
   - Optionally prune unused Docker resources: `docker system prune -af` (CAUTION: removes all stopped containers/images).
2. **Rebuild automation-stack:**
   - `cd automation-stack`
   - `docker compose up -d --build`
   - Verify all services via Traefik dashboard and AutomationChecklist.md.
3. **Start fresh Freqtrade devcontainer:**
   - Open `freqtrade/` in VS Code.
   - Use "Reopen in Container" (Dev Containers extension) or run `docker compose up -d` if using standalone Docker Compose.
   - Confirm Freqtrade UI/API is accessible (http://localhost:8080) and CLI works in container terminal.
   - Ensure `user_data` is mounted and persists configs/strategies.
4. **Connect Freqtrade to automation-stack:**
   - Ensure Freqtrade container joins the shared Docker network (e.g., `mcp-net`) if API access from automation-stack is required (see docker-compose.yml and devcontainer.json).
   - Test Controller <-> Freqtrade API calls (see AutomationChecklist.md, webhookFlows.md).
5. **Verify integration and logging:**
   - Run n8n workflows that interact with Controller and Freqtrade.
   - Confirm logs are written to unified PostgreSQL table with correct agent field (UnifiedLogging.md).
6. **Update documentation and checklists:**
   - Mark completed steps in AutomationChecklist.md and TODO.md.
   - Update any onboarding/setup docs as needed.

**References:**
- AutomationChecklist.md (live status)
- TODO.md (actionable tasks)
- webhookFlows.md (integration guide)
- UnifiedLogging.md (logging schema)
- CentralBrain.md (agent orchestration)
- 02_Freqtrade_Dev_Environment_Setup.md (freqtrade setup)
- 03_Core_Services_Configuration_and_Verification.md (verification)

---

*This document should be reviewed and updated regularly (e.g., monthly or quarterly) to reflect project progress and evolving goals.* 