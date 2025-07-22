# 🎯 Goal
Perform an intelligent audit and backup of the `~/projects/auto-stack` directory, with a focus on the `docs` subdirectory. Identify deprecated or outdated documentation and highlight files that need reintegration into a modern scaffold ("fresh-start.md"). Stop after this cleanup—do not begin the "fresh start" itself yet.

# 🛠 Stack & Context
- **Platform:** WSL 2 (Windows Subsystem for Linux)
- **Structure Insight:** Use `docs/reference/fresh-scaffold.md` as the canonical structure reference for an up-to-date scaffold.
- **System Blueprint:** Reference `docs/reference/Dual-Stack_Architecture.md` for accurate architectural context of the current system.
- **Knowledge Resources:** Use embedded prompt engineering intelligence from `docs/intelligence/agent.prompt.md` to augment decision-making.

# 📋 Task List
1. **Backup Phase** (SKIP-COMPLETED-DO NOT RUN)
   - Back up the **entire** `auto-stack` project, including `.env` and root files.
   - Store backups in a timestamped archive (`auto-stack_backup.zip`).

2. **Doc Clean-Up Phase**
   - Recursively scan `docs/` and subdirectories.
   - Flag outdated or deprecated files:
     - Files not listed in `fresh-scaffold.md`
     - Files inconsistent with service/module names defined in `Dual-Stack_Architecture.md`
   - Identify orphaned files (docs with no matching service/module).
   - Mark which files are superseded by newer equivalents or lack clear relevance.
   - Cross-reference with known agent-related docs (`Agent-Orientation.md`, `README_agent.md`) for preservation if relevant.

3. **Metadata Compilation**
   - Create a new file: `~/projects/auto-stack/docs/reference/fresh-start.md`
   - Populate with:
     - List of deprecated files (with rationale)
     - List of reintegratable content (and where they should migrate)
     - Suggestions on doc hierarchy improvements
     - Observations about stale workflows or integration gaps
     - TODO items or notes for a future "fresh-start" action

# ⛔ Constraints
- Do not delete any files. *move Deprecated files to the `docs/deprecated` folder*
- Do not initiate the "fresh-start" action.
- Do not modify existing `.env`, Docker, or integration settings.

# ✅ Output Format
- A completed `fresh-start.md` file with the following sections:
  - ## Deprecated Files
  - ## To Be Reintegrated
  - ## Observations
  - ## Suggested Structure Changes
  - ## Next Steps (placeholder)
