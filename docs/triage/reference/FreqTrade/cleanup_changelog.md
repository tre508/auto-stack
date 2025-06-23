# FreqTrade Reference Directory Cleanup Changelog

**Date:** 2025-01-16  
**Objective:** Clean up and organize the FreqTrade reference directory, removing duplicates and outdated files.

## Files Moved to `docs/deprecated/FreqTrade/`

### Duplicate/Backup Folders
- **`strategies - Copy/`** - Reason: Duplicate backup folder containing strategy files
  - Contents: KrakenFreqAI_auto_stack.py, KrakenFreqAI.json, sample_strategy.py, KrakenFreqAI.py, MinimalFreqAIStrategy.py
- **`models - Copy/`** - Reason: Duplicate backup folder containing model files
  - Contents: RagsToRichesRLModel/ subdirectory
- **`freqaimodels - Copy/`** - Reason: Duplicate backup folder containing FreqAI model files
  - Contents: RagsToRichesRLModel.py, MinimalFreqAIModel.py, run_params.json

### Outdated Configuration Files
- **`config-planB.json`** - Reason: Alternative/outdated configuration file
- **`Origional-config.json`** - Reason: Backup configuration with typo in filename, appears outdated

### Legacy Documentation
- **`PLAN_B_STRATEGY_GUIDE.md`** - Reason: Legacy strategy guide, superseded by current documentation
- **`RL_RagsToRiches_Plan.md`** - Reason: Legacy RL plan, marked as deprecated within the file content

### Non-FreqTrade Specific Files
- **`cursor_chat.md`** - Reason: General development documentation, not FreqTrade-specific
- **`obsidian_service_docs.md`** - Reason: Duplicate of file in parent reference directory
- **`pipe_mcp.md`** - Reason: General MCP documentation, not FreqTrade-specific

## Files Moved to `docs/triage/reference/n8n/`

### n8n Documentation
- **`N8N_DOC_AUTOMATION.md`** → `docs/triage/reference/n8n/N8N_DOC_AUTOMATION.md`
  - Reason: n8n-specific documentation belongs in n8n reference directory
- **`API-Cheet-sheets/n8n.md`** → `docs/triage/reference/n8n/n8n_cheat_sheet.md`
  - Reason: n8n cheat sheet belongs in n8n reference directory, renamed for clarity

### Directories Removed
- **`API-Cheet-sheets/`** - Reason: Empty after moving n8n.md, directory removed

## Files Retained in `docs/triage/reference/FreqTrade/`

### Active Configuration
- **`config_KrakenFreqAI_auto_stack.json`** - Reason: Current active FreqTrade configuration file

## Summary

**Total files processed:** 12 files + 3 directories  
**Files moved to deprecated:** 9 files + 3 directories  
**Files relocated to appropriate directories:** 2 files  
**Files retained:** 1 file  

## Result

The FreqTrade reference directory is now clean and organized with:
- Only the current active configuration file remaining
- All duplicate/backup folders moved to deprecated
- All outdated documentation archived
- n8n-specific documentation properly relocated
- Clear separation between active and historical content

## Next Steps

1. Review the deprecated files periodically and remove if no longer needed
2. Ensure the retained config file is kept up-to-date with active FreqTrade setup
3. Consider creating proper FreqTrade documentation structure if more current files are added 