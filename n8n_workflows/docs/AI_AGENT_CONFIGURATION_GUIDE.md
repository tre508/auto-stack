# AI Agent Configuration Guide for Enhanced CentralBrain Agent

## Current Workflow Analysis

Your workflow has been restructured effectively! The AI Agent now sits between "Check for Processing Errors" and the routing logic, which is a smart design. Here's how to configure it properly:

## Current Issues to Fix

### 1. **AI Agent Node Type**

- Currently: `@n8n/n8n-nodes-langchain.agent` (deprecated)
- Should be: `@n8n/n8n-nodes-langchain.toolsAgent` (modern)

### 2. **Missing Tools Configuration**

The AI Agent needs tools to make intelligent routing decisions.

### 3. **Output Parser Configuration**

Need to configure output parser for structured decision-making.

## Recommended Configuration

### Step 1: Update AI Agent Node Type

Replace the current AI Agent node configuration:

```json
{
  "parameters": {
    "hasOutputParser": true,
    "options": {}
  },
  "type": "@n8n/n8n-nodes-langchain.agent",
  "typeVersion": 2
}
```

With:

```json
{
  "parameters": {
    "promptType": "define",
    "text": "=You are an intelligent routing agent for the auto-stack trading system. \n\nAnalyze the user's request and determine the appropriate action:\n\nUser Request: {{ $json.chatInput }}\nUser ID: {{ $json.userId }}\nSession ID: {{ $json.sessionId }}\nDetected Command Type: {{ $json.commandType }}\n\nBased on the request, you should:\n1. If it's a specific command (freqtrade:, docs:, market:, notification:), route it to the Enhanced Command Router\n2. If there's an error in processing, route it to Error Response Handler\n3. If it's a general query, provide a helpful response and send it directly to the final response\n\nAlways respond with clear, actionable information.",
    "options": {
      "systemMessage": "You are a helpful AI assistant for a trading automation system. Analyze requests and route them appropriately or provide direct assistance for general queries."
    }
  },
  "type": "@n8n/n8n-nodes-langchain.toolsAgent",
  "typeVersion": 1
}
```

### Step 2: Add Output Parser Node

Add a **JSON Output Parser** node after the AI Agent to structure its decisions:

**Node Configuration:**

- **Type**: `@n8n/n8n-nodes-langchain.outputParserStructured`
- **Name**: "AI Agent Output Parser"
- **Position**: Between AI Agent and routing logic

**Parameters:**

```json
{
  "schemaType": "json",
  "jsonSchema": {
    "type": "object",
    "properties": {
      "action": {
        "type": "string",
        "enum": ["route_to_command_router", "send_error_response", "send_direct_response"],
        "description": "The action to take based on the analysis"
      },
      "reasoning": {
        "type": "string",
        "description": "Brief explanation of why this action was chosen"
      },
      "response": {
        "type": "string",
        "description": "Direct response for general queries"
      },
      "commandType": {
        "type": "string",
        "description": "Confirmed command type if routing to command router"
      }
    },
    "required": ["action", "reasoning"]
  }
}
```

### Step 3: Add Tool Nodes (Optional but Recommended)

Add these tool nodes to enhance the AI Agent's capabilities:

#### A. **Command Classifier Tool**

```json
{
  "parameters": {
    "name": "classify_command",
    "description": "Classify user input into command types",
    "code": "function classifyCommand(input) {\n  const chatInput = input.chatInput.toLowerCase();\n  \n  if (chatInput.startsWith('freqtrade:')) return 'freqtrade';\n  if (chatInput.startsWith('docs:')) return 'documentation';\n  if (chatInput.startsWith('market:')) return 'market';\n  if (chatInput.startsWith('notification:')) return 'notification';\n  \n  // Advanced classification for non-prefixed commands\n  if (chatInput.includes('trade') || chatInput.includes('balance') || chatInput.includes('profit')) {\n    return 'freqtrade';\n  }\n  if (chatInput.includes('search') || chatInput.includes('documentation') || chatInput.includes('help')) {\n    return 'documentation';\n  }\n  if (chatInput.includes('price') || chatInput.includes('market') || chatInput.includes('chart')) {\n    return 'market';\n  }\n  \n  return 'general';\n}",
    "inputSchema": {
      "type": "object",
      "properties": {
        "chatInput": {"type": "string"}
      }
    }
  },
  "type": "@n8n/n8n-nodes-langchain.toolCode",
  "name": "Command Classifier Tool"
}
```

#### B. **Context Validator Tool**

```json
{
  "parameters": {
    "name": "validate_context",
    "description": "Validate if the request has sufficient context",
    "code": "function validateContext(input) {\n  const { chatInput, userId, sessionId } = input;\n  \n  const issues = [];\n  if (!chatInput || chatInput.trim().length < 3) {\n    issues.push('Input too short or empty');\n  }\n  if (!userId) {\n    issues.push('Missing user identification');\n  }\n  if (!sessionId) {\n    issues.push('Missing session identification');\n  }\n  \n  return {\n    isValid: issues.length === 0,\n    issues: issues,\n    confidence: issues.length === 0 ? 1.0 : Math.max(0.1, 1.0 - (issues.length * 0.3))\n  };\n}",
    "inputSchema": {
      "type": "object",
      "properties": {
        "chatInput": {"type": "string"},
        "userId": {"type": "string"},
        "sessionId": {"type": "string"}
      }
    }
  },
  "type": "@n8n/n8n-nodes-langchain.toolCode",
  "name": "Context Validator Tool"
}
```

### Step 4: Update Connections

**Current Flow:**

```
Check for Processing Errors → AI Agent → [Multiple outputs]
```

**Recommended Flow:**

```
Check for Processing Errors → AI Agent → Output Parser → Switch Node → [Routing Logic]
```

**Connection Updates:**

1. **AI Agent** connects to **Output Parser**
2. **Output Parser** connects to a new **Switch Node**
3. **Switch Node** routes based on `action` field:
   - `route_to_command_router` → Enhanced Command Router
   - `send_error_response` → Error Response Handler  
   - `send_direct_response` → Send Enhanced Response

### Step 5: Add Intelligent Switch Node

Add a **Switch Node** after the Output Parser:

```json
{
  "parameters": {
    "rules": {
      "values": [
        {
          "conditions": {
            "conditions": [
              {
                "leftValue": "={{ $json.action }}",
                "rightValue": "route_to_command_router",
                "operator": {
                  "type": "string",
                  "operation": "equals"
                }
              }
            ]
          },
          "renameOutput": true,
          "outputKey": "command_router"
        },
        {
          "conditions": {
            "conditions": [
              {
                "leftValue": "={{ $json.action }}",
                "rightValue": "send_error_response",
                "operator": {
                  "type": "string",
                  "operation": "equals"
                }
              }
            ]
          },
          "renameOutput": true,
          "outputKey": "error_handler"
        },
        {
          "conditions": {
            "conditions": [
              {
                "leftValue": "={{ $json.action }}",
                "rightValue": "send_direct_response",
                "operator": {
                  "type": "string",
                  "operation": "equals"
                }
              }
            ]
          },
          "renameOutput": true,
          "outputKey": "direct_response"
        }
      ]
    }
  },
  "name": "AI Decision Router",
  "type": "n8n-nodes-base.switch"
}
```

## Implementation Steps

### Phase 1: Basic Fix

1. Update AI Agent node type to `toolsAgent`
2. Configure proper prompt and system message
3. Test basic functionality

### Phase 2: Add Output Parser

1. Add JSON Output Parser node
2. Configure structured output schema
3. Update connections

### Phase 3: Add Tools (Optional)

1. Add Command Classifier Tool
2. Add Context Validator Tool
3. Connect tools to AI Agent

### Phase 4: Intelligent Routing

1. Add AI Decision Router switch node
2. Update all connections
3. Test complete flow

## Expected Benefits

1. **Intelligent Routing**: AI makes smart decisions about request handling
2. **Error Recovery**: Better error handling and user feedback
3. **Flexibility**: Can handle both structured commands and natural language
4. **Maintainability**: Clear separation of concerns
5. **Extensibility**: Easy to add new command types or tools

## Testing Scenarios

After implementation, test these scenarios:

1. **Structured Commands**: `freqtrade:status`, `docs:search term`
2. **Natural Language**: "What's my trading balance?", "Help me understand the system"
3. **Error Cases**: Invalid input, missing parameters
4. **Edge Cases**: Empty input, very long input, special characters

## Monitoring and Debugging

Enable these for troubleshooting:

- Verbose logging on AI Agent
- Output inspection on Output Parser
- Connection tracing on Switch Node
- Error logging on all tool nodes

This configuration will make your AI Agent much more intelligent and capable of handling complex routing decisions while maintaining the workflow's efficiency.

================================
# AI Agent Architecture: 

Current setup and recommended organizational adjustments.

## 🖥️ Current Setup: Node & Relation Web

**Main Node:**  
`AI Agent`

**Directly Connected Nodes:**

| Node Name                           | Relation to AI Agent   |
|--------------------------------------|------------------------|
| Answer questions with a vector store | Tool                   |
| Simple Memory                       | Memory                 |
| Calculator                          | Tool                   |
| Structured Output Parser            | Output Parser          |
| Insert rows in a table in Postgres  | Tool                   |
| MCP Client                          | Tool                   |
| HTTP Request                        | Tool                   |

**Sub-Nodes:**
- `Answer questions with a vector store` → `Postgres PGVector Store` → `OpenAI Chat Model`

## 🔗 Simplified Relation Web Diagram

```plaintext
[Parent/Input Node]
      |
      v
[AI Agent]
   /   |   \   \   \   \   \
  /    |    \   \   \   \   \
[Answer questions with a vector store]  [Simple Memory]  [Calculator]  [Structured Output Parser]  [Insert rows in a table in Postgres]  [MCP Client]  [HTTP Request]
      |
      v
[Postgres PGVector Store]
      |
      v
[OpenAI Chat Model]
```

## 🛠️ Organizational Recommendations & Adjustments

**1. Modularity & Separation of Concerns**
- Ensure each node is a self-contained module with a clear interface.
- Separate planning, tool usage, and memory management.

**2. Memory Management**
- Implement both short-term (session) and long-term (vector store) memory.
- Review the `Simple Memory` node for robustness and sharing capabilities.

**3. Tool Orchestration & Documentation**
- Document each tool’s purpose, parameters, and usage patterns.
- Consider abstraction layers for easier orchestration and future tool additions.

**4. Dynamic Routing & Human-in-the-Loop**
- Add a routing/condition node for dynamic workflow branching.
- Optionally, insert a human-in-the-loop node for tasks needing oversight.

**5. Monitoring & Metrics**
- Add logging/monitoring nodes to track usage, errors, and performance.
- Define KPIs for each tool and the overall agent.

**6. Scalability & Integration**
- Design for easy addition of new tools, memory types, or agents.
- Audit integration points for compatibility and upgrade needs.

## 📋 Recommendations Table

| Recommendation            | Purpose/Action                                      |
|---------------------------|-----------------------------------------------------|
| Modularity                | Self-contained nodes, clear interfaces              |
| Memory Management         | Short-term & long-term memory                       |
| Tool Orchestration        | Documentation, abstraction, order                   |
| Dynamic Routing           | Workflow branching, conditional logic               |
| Monitoring & Metrics      | Logging, tracking, debugging                        |
| Scalability & Integration | Easy expansion, integration audit                   |
| Human-in-the-Loop         | Safety, approvals, oversight                        |

## 🏁 Next Steps

```bash
# 1. Review current node connections as per the diagram above.
# 2. Refactor nodes for modularity and clear interfaces.
# 3. Enhance memory nodes for both session and persistent storage.
# 4. Add routing/condition node for dynamic tool invocation.
# 5. Integrate logging/monitoring for all nodes.
# 6. Document all tools and memory modules.
# 7. (Optional) Insert human-in-the-loop node for critical tasks.
# 8. Audit integration points for scalability.
```

> **Tip:** Use this document as a blueprint for refactoring and scaling the AI agent setup in Cursor IDE.  
> For Markdown formatting, see [Markdown Guide][1][2][3][5][7][8].

[1]: https://www.markdownguide.org/basic-syntax/
[2]: https://docs.github.com/github/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax
[3]: https://docs.skillable.com/docs/creating-instructions-with-markdown-syntax
[5]: https://docs.document360.com/docs/markdown-basics
[7]: https://www.markdownguide.org/extended-syntax/
[8]: https://github.com/adam-p/markdown-here/wiki/markdown-cheatsheet

[1] https://www.markdownguide.org/basic-syntax/
[2] https://docs.github.com/github/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax
[3] https://docs.skillable.com/docs/creating-instructions-with-markdown-syntax
[4] https://stackoverflow.com/questions/20303826/how-to-highlight-bash-shell-commands-in-markdown
[5] https://docs.document360.com/docs/markdown-basics
[6] https://google.github.io/styleguide/docguide/style.html
[7] https://www.markdownguide.org/extended-syntax/
[8] https://github.com/adam-p/markdown-here/wiki/markdown-cheatsheet
