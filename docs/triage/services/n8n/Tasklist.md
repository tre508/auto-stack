# n8n Service Tasklist

This document consolidates all n8n service-related documentation and tasks.

## Service Overview
n8n is a workflow automation service component in the automation stack that enables visual workflow creation and automation across multiple services and APIs.

---

## Core Documentation Index

### Workflow Templates
- **Agent Workflows**: 
  - [CentralBrain Agent](../../n8n/templates/CentralBrain_Agent.json)
  - [Freqtrade Specialist Agent](../../n8n/templates/n8n_workflow_FreqtradeSpecialist_Agent.json)
  - [Backtest Agent](../../n8n/templates/n8n_workflow_Backtest_Agent.json)
  - [Summarization Agent](../../n8n/templates/n8n_workflow_Summarization_Agent.json)
- **System Workflows**:
  - [Docker Health Check](../../n8n/templates/n8n_workflow_Docker_Health_Check.json)
  - [Git Repo Commit Notifier](../../n8n/templates/n8n_workflow_Git_Repo_Commit_Notifier.json)
  - [Unified Logging](../../n8n/templates/n8n_workflow_UnifiedLogging.json)
- **Trading Workflows**:
  - [Freqtrade Task Runner](../../n8n/templates/Freqtrade_Task_Runner.json)
  - [Freqtrade Log Monitor](../../n8n/templates/Freqtrade_Log_Monitor.json)
  - [Stock Analysis](../../n8n/templates/Stock_Analysis.json)

### Workflow Bundles
- **CentralBrain Bundle**:
  - [CentralBrain Master](../../n8n/templates/centralbrain_bundle/CentralBrain_Master.json)
  - [LLM Parser Agent](../../n8n/templates/centralbrain_bundle/LLM_ParserAgent.json)
  - [Notification Agent](../../n8n/templates/centralbrain_bundle/NotificationAgent.json)

### Documentation & Guides
- **Core Concepts**:
  - [n8n Multi-Agent Concepts](../../n8n/n8n_multi_agent_concepts.md)
  - [Webhook Flows](../../n8n/webhookFlows.md)
  - [Freqtrade Webhook Ideas](../../n8n/n8n_freqtrade_webhook_ideas.md)
- **AI Integration**:
  - [n8nChat Integration](../../n8n/n8nChat.md)
  - [Guide to Building Agents](../../n8n/prompt_library/guide-to-building-agents.md)
  - [Command Prompt Style Guide](../../n8n/prompt_library/command-prompt-style-guide.md)
- **System Integration**:
  - [Doc Mirror Update](../../n8n/n8n_doc_mirror_update.md)
  - [Alternatives Documentation](../../n8n/alternatives.md)
  - [Community Nodes](../../n8n/community-nodes.md)

### Workflow Architecture
- **AgentHub**: [AgentHub Documentation](../../n8n/workflows/AgentHub.md)
- **CentralBrain Flow**: [CentralBrain Flow Documentation](../../n8n/workflows/CentralBrainFlow.md)
- **Superflow Orchestration**: [Superflow Orchestration Map](../../n8n/workflows/Superflow-Orchestration-Map.md)

### Prompt Library
- **Agent Templates**:
  - [CentralBrain Agent Prompts](../../n8n/prompt_library/CentralBrain.md)
  - [n8nChat Prompt Templates](../../n8n/prompt_library/n8nChat_prompt_templates.md)
- **System Prompts**:
  - [Unified Logging](../../n8n/prompt_library/UnifiedLogging.md)

## Key Service Functions

### Workflow Automation
- Visual workflow designer for complex automation
- HTTP webhook triggers for external integrations
- Database operations and data transformation
- API integrations with external services

### Agent Orchestration
- Multi-agent workflow coordination
- LLM integration for intelligent task processing
- Context sharing between workflow steps
- Dynamic workflow branching based on conditions

### System Integration
- Docker container health monitoring
- Git repository event handling
- File system operations and synchronization
- Email and notification services

## Integration Points

### Controller Service
- Receives workflow triggers via HTTP endpoints
- Processes controller tasks through n8n workflows
- Handles MCP server communications

### Mem0 Service
- Stores and retrieves workflow context
- Enables persistent memory across workflow runs
- Supports RAG operations for enhanced decision making

### EKO Service
- Executes AI agent tasks within workflows
- Provides LLM capabilities for complex reasoning
- Handles tool integration and external API calls

### freq-chat Service
- Triggers conversational workflows
- Processes chat context through n8n pipelines
- Enables chat-driven automation

## Configuration Requirements

### Environment Variables
- `N8N_BASIC_AUTH_ACTIVE`: Enable/disable basic authentication
- `N8N_BASIC_AUTH_USER`: Basic auth username
- `N8N_BASIC_AUTH_PASSWORD`: Basic auth password
- `WEBHOOK_URL`: Base URL for webhook endpoints
- `N8N_EDITOR_BASE_URL`: Editor interface URL

### Docker Configuration
- Service runs on port 5678 (configurable)
- Requires persistent storage for workflows and data
- Network access to other automation stack services
- SSL/TLS configuration for production use

## Related Services
- **Controller**: Orchestrates n8n workflow execution
- **Mem0**: Provides persistent memory and context storage
- **EKO**: AI agent service for intelligent task processing
- **freq-chat**: Chat interface that triggers n8n workflows

## Cross-References
- [Controller Service Documentation](../controller/Tasklist.md)
- [Mem0 Service Documentation](../mem0/Tasklist.md)
- [EKO Service Documentation](../eko/Tasklist.md)
- [freq-chat Service Documentation](../freq-chat/Tasklist.md)
