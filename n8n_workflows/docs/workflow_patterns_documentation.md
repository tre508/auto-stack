# n8n Workflow Patterns and Templates Documentation

## Overview
This document provides comprehensive patterns, templates, and best practices for building robust, scalable, and maintainable n8n workflows in the auto-stack trading system.

## Core Workflow Patterns

### 1. Command Router Pattern

#### Description
Routes incoming requests to appropriate handlers based on command type or content analysis.

#### Use Cases
- Multi-purpose API endpoints
- Command-based chat interfaces
- Service orchestration

#### Implementation
```json
{
  "name": "Command Router Node",
  "type": "n8n-nodes-base.switch",
  "parameters": {
    "rules": {
      "values": [
        {
          "conditions": {
            "conditions": [
              {
                "leftValue": "={{ $json.commandType }}",
                "rightValue": "freqtrade",
                "operator": {
                  "type": "string",
                  "operation": "equals"
                }
              }
            ]
          },
          "renameOutput": true,
          "outputKey": "freqtrade"
        }
      ]
    },
    "options": {
      "fallbackOutput": "general"
    }
  }
}
```

#### Best Practices
- Always include fallback handling
- Use descriptive output keys
- Validate input before routing
- Log routing decisions for debugging

### 2. Error Handling Pattern

#### Description
Comprehensive error handling with graceful degradation and notification systems.

#### Implementation
```json
{
  "name": "Error Handler",
  "type": "n8n-nodes-base.code",
  "parameters": {
    "jsCode": "const input = $input.first().json;\nconst errors = $input.all().filter(item => item.json.error);\n\nif (errors.length > 0) {\n  return {\n    status: 'error',\n    errors: errors.map(e => ({\n      source: e.node,\n      message: e.json.error.message,\n      timestamp: new Date().toISOString()\n    })),\n    recoverable: errors.every(e => e.json.error.recoverable !== false)\n  };\n}\n\nreturn {\n  status: 'success',\n  data: input\n};"
  },
  "continueOnFail": true,
  "onError": "continueErrorOutput"
}
```

#### Error Categories
1. **Recoverable Errors**: Network timeouts, temporary API failures
2. **System Errors**: Database connection issues, configuration problems
3. **User Errors**: Invalid input, authentication failures
4. **Critical Errors**: System crashes, data corruption

### 3. Monitoring and Logging Pattern

#### Description
Comprehensive logging and monitoring for workflow observability.

#### Implementation
```json
{
  "name": "Monitoring Logger",
  "type": "n8n-nodes-base.postgres",
  "parameters": {
    "operation": "insert",
    "table": "workflow_logs",
    "columns": {
      "mappingMode": "defineBelow",
      "value": {
        "workflow_name": "{{ $workflow.name }}",
        "execution_id": "{{ $execution.id }}",
        "node_name": "{{ $node.name }}",
        "timestamp": "{{ new Date().toISOString() }}",
        "status": "{{ $json.status || 'unknown' }}",
        "duration_ms": "{{ $json.duration || 0 }}",
        "input_data": "{{ JSON.stringify($input.first().json) }}",
        "output_data": "{{ JSON.stringify($json) }}",
        "user_id": "{{ $json.userId || 'system' }}",
        "session_id": "{{ $json.sessionId || 'none' }}"
      }
    }
  },
  "continueOnFail": true
}
```

## Best Practices Summary

### 1. Workflow Design
- Use descriptive node names
- Implement comprehensive error handling
- Add monitoring and logging
- Design for scalability
- Document workflow purpose and usage

### 2. Performance Optimization
- Implement caching where appropriate
- Use batch processing for bulk operations
- Optimize database queries
- Monitor resource usage
- Implement circuit breakers for external services

### 3. Security Considerations
- Validate and sanitize all inputs
- Implement proper authentication
- Use environment variables for sensitive data
- Log security events
- Regular security audits

### 4. Maintenance and Operations
- Version control workflow definitions
- Implement automated testing
- Monitor workflow performance
- Regular backup procedures
- Documentation updates

This comprehensive documentation provides the foundation for building robust, scalable, and maintainable n8n workflows in the auto-stack trading system.