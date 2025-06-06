# Prompt Engineering Hub

This directory centralizes all prompt-related documentation and templates for the Automation Stack project.

## Directory Structure

- **`intelligence/`** - Core agent prompts and system instructions
- **`orchestration/`** - n8n workflow prompts and templates  
- **`integration/`** - Cross-service integration prompts
- **`debugging/`** - Diagnostic and troubleshooting prompts

## Purpose

The `prompts/` directory serves as the canonical location for:

- System prompts used by AI agents
- Template prompts for workflow automation
- Integration guidelines between services
- Best practices for prompt engineering

## Best Practices

### Prompt Structure
- Use clear, descriptive headers
- Include context and constraints
- Specify expected outputs
- Document prompt versioning

### Maintenance
- Update prompts when system behavior changes
- Test prompt modifications in isolation
- Document changes in relevant README files
- Archive deprecated prompts rather than deleting

### Integration Guidelines
- Reference prompts by canonical path
- Use consistent formatting across services
- Maintain backwards compatibility when possible
- Include usage examples in documentation

## Cross-Service Integration

This prompt hub integrates with:
- **Controller**: Uses intelligence prompts for agent tasking
- **n8n**: Leverages orchestration templates for workflow automation
- **Mem0**: Utilizes integration prompts for memory management
- **Freqtrade**: Applies debugging prompts for strategy analysis

## Maintenance Tips

1. **Centralized Updates**: When system behavior changes, update relevant prompts here first
2. **Version Control**: Track prompt changes with meaningful commit messages
3. **Testing**: Validate prompt changes across affected services
4. **Documentation**: Keep README files current with structural changes
