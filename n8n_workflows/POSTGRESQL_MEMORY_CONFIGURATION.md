# PostgreSQL Memory Input/Fetch System Configuration Guide

## Current System Analysis

Your AI Agent now has a sophisticated vector store setup with three PGVector nodes:

### 🗄️ **Current Vector Store Nodes**

| Node Name | Mode | Purpose | Issues Found |
|-----------|------|---------|--------------|
| `Postgres PGVector Store` | retrieve-as-tool | AI Agent tool for retrieval | ✅ Properly configured |
| `retrieve docs Postgres PGVector Store` | retrieve | Direct retrieval | ⚠️ Missing configuration |
| `Insert Docs` | insert | Document insertion | ⚠️ Missing table configuration |

### 🔧 **Required Fixes**

## 1. Complete PGVector Store Configurations

### A. **retrieve docs Postgres PGVector Store** - Missing Parameters

```json
{
  "parameters": {
    "tableName": "documents_vector_store",
    "collectionName": "centralbrain_docs",
    "options": {
      "queryName": "similarity_search",
      "topK": 5,
      "scoreThreshold": 0.7
    }
  },
  "type": "@n8n/n8n-nodes-langchain.vectorStorePGVector",
  "typeVersion": 1.3,
  "name": "retrieve docs Postgres PGVector Store",
  "credentials": {
    "postgres": {
      "id": "RRJmkcRaHXZBMhKB",
      "name": "Postgres account"
    }
  }
}
```

### B. **Insert Docs** - Missing Table Configuration

```json
{
  "parameters": {
    "mode": "insert",
    "tableName": "documents_vector_store",
    "collectionName": "centralbrain_docs",
    "options": {
      "batchSize": 100,
      "vectorDimensions": 768
    }
  },
  "type": "@n8n/n8n-nodes-langchain.vectorStorePGVector",
  "typeVersion": 1.3,
  "name": "Insert Docs",
  "credentials": {
    "postgres": {
      "id": "RRJmkcRaHXZBMhKB",
      "name": "Postgres account"
    }
  }
}
```

### C. **Postgres PGVector Store (Tool)** - Enhanced Configuration

```json
{
  "parameters": {
    "mode": "retrieve-as-tool",
    "tableName": "documents_vector_store",
    "collectionName": "centralbrain_docs",
    "toolName": "search_knowledge_base",
    "toolDescription": "Search the knowledge base for relevant information about trading, documentation, and system operations",
    "options": {
      "topK": 3,
      "scoreThreshold": 0.6
    }
  },
  "type": "@n8n/n8n-nodes-langchain.vectorStorePGVector",
  "typeVersion": 1.3,
  "name": "Postgres PGVector Store",
  "credentials": {
    "postgres": {
      "id": "RRJmkcRaHXZBMhKB",
      "name": "Postgres account"
    }
  }
}
```

## 2. HuggingFace Embeddings Configuration

### **Current Issue**: Missing model specification

```json
{
  "parameters": {
    "model": "sentence-transformers/all-MiniLM-L6-v2",
    "options": {
      "maxRetries": 3,
      "timeout": 30000
    }
  },
  "type": "@n8n/n8n-nodes-langchain.embeddingsHuggingFaceInference",
  "typeVersion": 1,
  "name": "Embeddings HuggingFace Inference",
  "credentials": {
    "huggingFaceApi": {
      "id": "75SQAZjBBBocdyz5",
      "name": "HuggingFaceApi account"
    }
  }
}
```

## 3. Database Schema Setup

### **Required PostgreSQL Tables**

Run these SQL commands in your PostgreSQL database:

```sql
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create documents vector store table
CREATE TABLE IF NOT EXISTS documents_vector_store (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    collection_name VARCHAR(255) NOT NULL DEFAULT 'centralbrain_docs',
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    embedding vector(768),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for faster similarity search
CREATE INDEX IF NOT EXISTS documents_vector_store_embedding_idx 
ON documents_vector_store USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100);

-- Create index for collection filtering
CREATE INDEX IF NOT EXISTS documents_vector_store_collection_idx 
ON documents_vector_store (collection_name);

-- Create index for metadata filtering
CREATE INDEX IF NOT EXISTS documents_vector_store_metadata_idx 
ON documents_vector_store USING gin (metadata);
```

## 4. Default Data Loader Configuration

### **Enhanced Configuration for Multiple Data Sources**

```json
{
  "parameters": {
    "jsonMode": "expressionData",
    "jsonData": "={{ $json }}",
    "options": {
      "textSplitter": {
        "chunkSize": 1000,
        "chunkOverlap": 200
      },
      "metadata": {
        "source": "={{ $json.source || 'centralbrain_system' }}",
        "timestamp": "={{ new Date().toISOString() }}",
        "type": "={{ $json.type || 'documentation' }}"
      }
    }
  },
  "type": "@n8n/n8n-nodes-langchain.documentDefaultDataLoader",
  "typeVersion": 1.1,
  "name": "Default Data Loader"
}
```

## 5. Complete Memory System Architecture

### **Memory Flow Diagram**

```
Input Documents → Default Data Loader → Insert Docs (PGVector)
                                            ↓
AI Agent ← Answer questions (Tool) ← retrieve docs PGVector Store
    ↓
Postgres PGVector Store (Tool) → Search Knowledge Base
```

### **Memory Types Integration**

1. **Short-term Memory**: `Simple Memory` (session-based, 10 interactions)
2. **Long-term Memory**: `PGVector Store` (persistent vector embeddings)
3. **Contextual Memory**: `Answer questions with vector store` (context-aware retrieval)

## 6. Testing and Validation

### **Test Scenarios**

1. **Document Insertion Test**:

   ```json
   {
     "content": "Freqtrade is a trading bot that supports backtesting and live trading",
     "source": "freqtrade_docs",
     "type": "documentation"
   }
   ```

2. **Knowledge Retrieval Test**:
   - Query: "How do I configure Freqtrade?"
   - Expected: Relevant documentation from vector store

3. **Memory Persistence Test**:
   - Verify vectors are stored in PostgreSQL
   - Check embedding quality and retrieval accuracy

## 7. Performance Optimization

### **Recommended Settings**

- **Vector Dimensions**: 768 (matches sentence-transformers/all-MiniLM-L6-v2)
- **Top K Results**: 3-5 for tools, 5-10 for direct retrieval
- **Score Threshold**: 0.6-0.7 for relevant results
- **Batch Size**: 100 for bulk insertions

### **Monitoring Queries**

```sql
-- Check vector store status
SELECT 
    collection_name,
    COUNT(*) as document_count,
    AVG(array_length(embedding::float[], 1)) as avg_vector_dimension
FROM documents_vector_store 
GROUP BY collection_name;

-- Monitor recent insertions
SELECT content, metadata, created_at 
FROM documents_vector_store 
WHERE created_at > NOW() - INTERVAL '1 hour'
ORDER BY created_at DESC;
```

## 8. Troubleshooting Common Issues

### **Issue 1**: HuggingFace credential errors

- **Solution**: Create new HF token with proper permissions
- **Test**: `curl -H "Authorization: Bearer YOUR_TOKEN" https://huggingface.co/api/whoami`

### **Issue 2**: Vector dimension mismatch

- **Solution**: Ensure embedding model outputs 768 dimensions
- **Check**: Verify `sentence-transformers/all-MiniLM-L6-v2` model

### **Issue 3**: PostgreSQL connection issues

- **Solution**: Verify pgvector extension and table creation
- **Test**: Run schema setup SQL commands

### **Issue 4**: Poor retrieval quality

- **Solution**: Adjust score threshold and topK values
- **Monitor**: Check embedding similarity scores

## 9. Next Steps

1. **Apply configurations** to the three PGVector nodes
2. **Run database schema** setup commands
3. **Test document insertion** with sample data
4. **Verify retrieval quality** with test queries
5. **Monitor performance** and adjust parameters

This configuration will give you a robust, scalable PostgreSQL-based memory system for your AI Agent!
