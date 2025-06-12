# n8n Workflow Automation Cheat Sheet

> **Project-Specific Setup:** For deploying n8n within this specific project environment, always refer to the `compose-mcp.yml` file detailed in **`MasterSetup.md`**. The Docker command below is for general reference.

## Quick Start

### Install and Run with npx
```bash
npx n8n
```

### Deploy with Docker
```bash
# Create a volume for persistent data
docker volume create n8n_data

# Run n8n
docker run -it --rm --name n8n -p 5678:5678 -v n8n_data:/home/node/.n8n docker.n8n.io/n8nio/n8n
```

Access the editor at http://localhost:5678

## Key Features

- **Code Flexibility**: Write JavaScript/Python, add npm packages, or use visual interface
- **AI Capabilities**: Build AI agent workflows with LangChain
- **Self-hosting**: Deploy on your own infrastructure or use cloud offering
- **Enterprise Features**: Advanced permissions, SSO, air-gapped deployments
- **Integrations**: 400+ pre-built integrations and 900+ templates

## Creating Workflows

1. Access the n8n editor at http://localhost:5678
2. Create a new workflow
3. Add nodes from the nodes panel
4. Configure node settings
5. Connect nodes by dragging from one node's output to another node's input
6. Save and activate your workflow

## JavaScript Code Example (Node Function)

```javascript
// Example of a Function node in n8n
// This transforms incoming data
const items = $input.all();
const results = [];

for (const item of items) {
  // Transform each item
  results.push({
    json: {
      transformedData: item.json.data.toUpperCase(),
      timestamp: new Date().toISOString()
    }
  });
}

return results;
```

## Common Integrations Usage

```javascript
// Example: HTTP Request node configuration
// This would be configured in the n8n UI
// For project-specific LLM calls, prefer using the OpenAI Chat Model node configured for the OpenWebUI gateway (see n8n_cursor_freqtrade_integration.md)
{
  "url": "https://api.example.com/data",
  "method": "POST",
  "authentication": "basicAuth",
  "username": "{{$credentials.example.username}}",
  "password": "{{$credentials.example.password}}",
  "headers": {
    "Content-Type": "application/json"
  },
  "body": {
    "query": "{{$json.searchTerm}}"
  }
}
```

## AI Workflow Example

```javascript
// LangChain node configuration example
// This would be set up in the n8n UI
// For project-specific LLM calls, prefer using the OpenAI Chat Model node configured for the OpenWebUI gateway (see n8n_cursor_freqtrade_integration.md)
{
  "operation": "llmChain",
  "prompt": "Answer the following question: {{$json.question}}",
  "model": "gpt-3.5-turbo",
  "temperature": 0.7
}
```

## Resources

- Documentation: [n8n.io/docs](https://n8n.io/docs)
- Integrations: 400+ available nodes
- Community Forum: [community.n8n.io](https://community.n8n.io)
- Templates: 900+ ready-to-use workflow templates

## License Notes

- Fair-code distributed under Sustainable Use License and Enterprise License
- Source code is always visible
- Self-hostable on your infrastructure
- Enterprise licenses available for additional features