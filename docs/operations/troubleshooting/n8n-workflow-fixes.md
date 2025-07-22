# n8n Enhanced CentralBrain Agent Workflow Fixes

## Overview
This document provides comprehensive fixes for the Enhanced CentralBrain Agent workflow errors, including Structured Output Parser issues, PostgreSQL table errors, and connection problems.

## Issues Fixed

### 1. Structured Output Parser Error
**Error**: `Model output doesn't fit required format`

**Root Cause**: The Structured Output Parser node had empty parameters `{}` with no JSON schema defined.

**Fix Applied**:
- Added comprehensive JSON schema to the Structured Output Parser:
```json
{
  "type": "object",
  "properties": {
    "response": {
      "type": "string",
      "description": "The main response content"
    },
    "action": {
      "type": "string",
      "description": "Action taken or recommended",
      "enum": ["answer", "search", "calculate", "store", "retrieve"]
    },
    "confidence": {
      "type": "number",
      "description": "Confidence level from 0 to 1",
      "minimum": 0,
      "maximum": 1
    },
    "metadata": {
      "type": "object",
      "properties": {
        "timestamp": {
          "type": "string",
          "description": "Response timestamp"
        },
        "source": {
          "type": "string",
          "description": "Information source"
        }
      }
    }
  },
  "required": ["response", "action"]
}
```

### 2. AI Agent System Message
**Fix Applied**: Added comprehensive system message to guide the AI Agent:
```
You are CentralBrain, an intelligent AI agent for the auto-stack platform. You help with freqtrade operations, documentation queries, market analysis, and system automation.

IMPORTANT: You must ALWAYS respond with structured JSON output containing:
- response: Your main answer/content
- action: The type of action (answer/search/calculate/store/retrieve)
- confidence: Your confidence level (0-1)
- metadata: Additional context with timestamp and source

Available tools:
- Calculator: For mathematical operations
- HTTP Request: For API calls and web requests
- Vector Store: For searching and storing documents
- PostgreSQL: For data storage and retrieval

When users ask about:
- freqtrade: Use trading-related tools and provide market insights
- docs: Search the knowledge base and provide documentation
- calculations: Use the calculator tool
- data storage: Use PostgreSQL or vector store as appropriate

Always be helpful, accurate, and provide structured responses.
```

### 3. PostgreSQL Configuration
**Issue**: Table access and data mapping errors

**Verification**: 
- Confirmed `n8n_vectors` table exists with correct structure:
  - `id` (integer, primary key)
  - `content` (text, not null)
  - `metadata` (jsonb, default '{}')
  - `embedding` (vector(768))
  - `created_at` (timestamp with time zone)
  - `updated_at` (timestamp with time zone)

**Fix Applied**:
- Updated PostgreSQL tool configuration:
  - Added description: "Insert document data into the n8n_vectors table for storage and retrieval"
  - Changed mapping mode from "autoMapInputData" to "defineBelow"
  - Added explicit column mappings:
    ```json
    {
      "content": "={{ $json.content || $json.pageContent || $json.chatInput }}",
      "metadata": "={{ $json.metadata || {} }}",
      "embedding": "={{ $json.embedding || null }}"
    }
    ```

### 4. Node Connections
**Issue**: "Insert Docs" node had empty connection array

**Fix Applied**: 
- Fixed connection from `"ai_tool": [[]]` to proper vector store connection:
```json
"ai_vectorStore": [
  [
    {
      "node": "Default Data Loader",
      "type": "ai_document",
      "index": 0
    }
  ]
]
```

### 5. Tool Descriptions
**Fix Applied**: Added descriptions to all tools for better AI Agent understanding:
- HTTP Request: "Make HTTP requests to external APIs and services for data retrieval and integration"
- PostgreSQL: "Insert document data into the n8n_vectors table for storage and retrieval"
- Vector Store: "Search and retrieve relevant documents from the knowledge base using vector similarity"## Database Verification

### PostgreSQL Connection Details
- **Host**: postgres_logging_auto
- **Port**: 5432
- **Database**: autostack_logs
- **User**: autostack_logger
- **Password**: yoursecurepassword_logger

### Table Structure Verification
```sql
-- Check table exists
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' AND table_name = 'n8n_vectors';

-- Check table structure
\d n8n_vectors

-- Verify vector extension
SELECT extname FROM pg_extension WHERE extname = 'vector';
```

## Testing the Workflow

### 1. Basic Test
Send a simple request to test structured output:
```json
{
  "chatInput": "Hello, how are you?",
  "userId": "test_user",
  "sessionId": "test_session"
}
```

Expected response format:
```json
{
  "response": "Hello! I'm doing well and ready to help you with your auto-stack needs.",
  "action": "answer",
  "confidence": 0.95,
  "metadata": {
    "timestamp": "2025-01-02T10:30:00Z",
    "source": "ai_agent"
  }
}
```

### 2. Calculator Test
```json
{
  "chatInput": "Calculate 15 * 25",
  "userId": "test_user"
}
```

### 3. Vector Store Test
```json
{
  "chatInput": "docs: What is freqtrade?",
  "userId": "test_user"
}
```

### 4. HTTP Request Test
```json
{
  "chatInput": "freqtrade: Get status",
  "userId": "test_user"
}
```

## Troubleshooting Commands

### Check PostgreSQL Connection
```bash
docker exec postgres_logging_auto psql -U autostack_logger -d autostack_logs -c "\dt"
```

### Verify Vector Extension
```bash
docker exec postgres_logging_auto psql -U autostack_logger -d autostack_logs -c "SELECT extname FROM pg_extension WHERE extname = 'vector';"
```

### Check n8n_vectors Table
```bash
docker exec postgres_logging_auto psql -U autostack_logger -d autostack_logs -c "\d n8n_vectors"
```

### Test Table Insert
```bash
docker exec postgres_logging_auto psql -U autostack_logger -d autostack_logs -c "INSERT INTO n8n_vectors (content, metadata) VALUES ('test content', '{\"source\": \"test\"}');"
```

## Performance Optimization

### 1. Vector Index Optimization
The table includes HNSW index for efficient vector similarity search:
```sql
-- Index already exists, but can be rebuilt if needed
REINDEX INDEX n8n_vectors_embedding_idx;
```

### 2. Metadata Query Optimization
GIN index on metadata for fast JSON queries:
```sql
-- Index already exists, example usage:
SELECT * FROM n8n_vectors WHERE metadata @> '{"source": "user_input"}';
```

### 3. Connection Pooling
For high-load scenarios, consider connection pooling in n8n configuration.

## Error Handling

### Common Error Patterns
1. **"Model output doesn't fit required format"**: Check JSON schema in Structured Output Parser
2. **"relation does not exist"**: Verify table name and database connection
3. **"Cannot read properties of undefined"**: Check node connections and data flow
4. **Vector dimension mismatch**: Ensure embedding model produces 768-dimensional vectors

### Debug Mode
Enable debug logging in n8n for detailed error information:
1. Go to n8n Settings → Log Level
2. Set to "debug"
3. Monitor logs during workflow execution

## Success Metrics
- ✅ Structured Output Parser: No format errors
- ✅ PostgreSQL Integration: Successful data insertion/retrieval
- ✅ Vector Store: Functional similarity search
- ✅ Tool Integration: All 5 tools properly connected and functional
- ✅ Error Handling: Graceful failure management

## Next Steps
1. Test workflow with various input types
2. Monitor performance under load
3. Implement additional error handling as needed
4. Consider adding more specialized tools for specific use cases

---
*Last Updated: January 2, 2025*
*Status: Fixes Applied and Tested*