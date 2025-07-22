# Mem0 BGE Embeddings Migration Guide

This guide provides step-by-step instructions for migrating your Mem0 instance to use the `BAAI/bge-base-en-v1.5` embedding model.

## 1. Configuration Files Updated

The following files have been updated:

### `mem0/server/config.yaml`

```yaml
# Embedder section updated to use BAAI/bge-base-en-v1.5
embedder:
  provider: "huggingface"
  config:
    model: "BAAI/bge-base-en-v1.5"

# Vector store section renamed from "vector_store" to "vectorstore"
# and "collection_name" changed to "collection"
vectorstore:
  provider: "qdrant"
  config:
    host: "qdrant_mcp"
    port: 6333
    collection: "mem0_autostack_collection"
```

### `.env`

Added HuggingFace cache paths for offline/cached mode:

```env
# =================================
# HuggingFace Cache Settings for Offline/Cached Mode
# =================================
HF_HOME=/data/.cache/huggingface
TRANSFORMERS_CACHE=/data/.cache/huggingface/transformers
```

## 2. New n8n Workflows Created

The following n8n workflows have been created:

### Delete Qdrant Collection Workflow

- **File**: `docs/services/n8n/templates/n8n_workflow_Delete_Qdrant_Collection.json`
- **Purpose**: Deletes the existing Qdrant collection to prepare for re-indexing with the new embedder
- **URL**: `http://qdrant_mcp:6333/collections/mem0_autostack_collection`
- **Method**: DELETE

### Mem0 Search with BGE Prompt Wrapping

- **File**: `docs/services/n8n/templates/n8n_workflow_Mem0_Search.json`
- **Purpose**: Demonstrates the proper query preprocessing for BGE embeddings
- **Key Feature**: Adds a `Set` node with query wrapping:
  ```
  "Represent this sentence for searching relevant passages: " + $json["query"]
  ```

### Mem0 Memory Event Logger (Optional)

- **File**: `docs/services/n8n/templates/n8n_workflow_Mem0_Memory_Logger.json`
- **Purpose**: Logs memory events to Postgres and creates file backups
- **Target Table**: `mem0_memory_events`

## 3. Migration Script

A migration script has been created at `mem0/server/bge_migration.sh` to assist with:
- Verifying configuration changes
- Checking Qdrant connectivity
- Restarting the Mem0 service
- Verifying the restart was successful
- Providing re-indexing instructions

**Windows Note**: The script needs to be made executable on Linux/Mac with `chmod +x mem0/server/bge_migration.sh`. On Windows, you can run it using WSL or follow the steps manually.

## 4. Implementation Steps

1. **Update Configuration Files**
   - The `config.yaml` and `.env` files have been updated as described above

2. **Import n8n Workflows**
   - Import the provided workflow templates into your n8n instance

3. **Delete Existing Qdrant Collection**
   - Run the "Delete Qdrant Collection" workflow in n8n
   - Alternatively, make a direct HTTP DELETE request to `http://qdrant_mcp:6333/collections/mem0_autostack_collection`

4. **Restart Mem0**
   - Restart the Mem0 service to load the new configuration:
     ```bash
     docker restart mem0_mcp
     ```

5. **Update Existing Search Workflows**
   - Add the query preprocessing step to all existing search workflows
   - Add the `Set` node before any search request with the wrapper:
     ```
     "Represent this sentence for searching relevant passages: " + $json["query"]
     ```

6. **Re-index Memory**
   - Re-insert all memory entries to generate new embeddings with the BGE model
   - This can be done through your usual memory insertion methods
   - Verify the collection is being recreated by checking Qdrant

## 5. Verification

1. **Check Qdrant Collection**
   - Verify the new collection exists with the correct dimension (768 for BGE model)
   - URL: `http://qdrant_mcp:6333/collections/mem0_autostack_collection`

2. **Test Search**
   - Use the "Mem0 Search with BGE Prompt Wrapping" workflow to test search functionality
   - Verify that search results are relevant and accurate

3. **Monitor Performance**
   - The BGE model should provide better semantic search results
   - If using the optional logging workflow, track search performance

## Troubleshooting

- **Mem0 Won't Start**: Check Docker logs with `docker logs mem0_mcp`
- **Missing Dependencies**: Ensure HuggingFace cache directories exist and are writable
- **Embedding Errors**: The BGE model requires more memory than the previous model, ensure sufficient resources
- **Search Not Working**: Verify the collection was recreated and that the query wrapper is being used

## Notes

- The BGE model uses 768-dimensional embeddings (vs. 384 for all-MiniLM-L6-v2)
- The first run may be slower as the model is downloaded and cached
- Using the query wrapper is essential for optimal performance with BGE models

## 6. Hugging Face Space Deployment Files for BGE Model

If you plan to deploy the BAAI/bge-base-en-v1.5 model as a standalone API service on Hugging Face Spaces, here are the recommended files. These should be placed at the root of your Hugging Face Space repository.

Refer to the [Hugging Face Space Setup Guide](docs/guides/huggingface_space_setup.md) for detailed steps on creating and configuring the Space.

### `README.md`

This `README.md` should be at the root of your Hugging Face Space repository.

```markdown
---
title: Bge Embedding Api
emoji: 🚀
colorFrom: purple
colorTo: indigo
sdk: docker
pinned: false
license: apache-2.0
app_port: 7860
short_description: High-speed dual-stack embedder via FastAPI & Docker
---

# BGE Embedding API Space

This Hugging Face Space provides a REST API for generating text embeddings using the `BAAI/bge-base-en-v1.5` model.

## API Endpoints

### POST /embed

Generates an embedding for the provided text. The input text will be automatically preprocessed with the BGE-specific prefix: "Represent this sentence for searching relevant passages: ".

**Request Body:**
```json
{
  "text": "Your sentence to embed."
}
```

**Response Body:**
```json
{
  "embedding": [0.123, ..., 0.456]
}
```
*The embedding is a 768-dimensional vector.*

**Example Usage (curl):**

For **public** Spaces:
```bash
curl -X POST "https://[your-space-subdomain].hf.space/embed" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, world!"}'
```

For **private** Spaces, you need to include an `Authorization` header with a Hugging Face User Access Token:
```bash
curl -X POST "https://[your-space-subdomain].hf.space/embed" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_HF_TOKEN" \
  -d '{"text": "Hello, world!"}'
```
*Replace `YOUR_HF_TOKEN` with your actual Hugging Face User Access Token (with `read` access).*

### GET /health

Returns the health status of the API.

**Response Body:**
```json
{
  "status": "healthy"
}
```

## Setup

This Space is built using Docker. The `Dockerfile` sets up a Python environment with FastAPI to serve the model.

- **Model**: `BAAI/bge-base-en-v1.5`
- **Framework**: FastAPI
- **Python Version**: 3.9

The model is downloaded and cached to `/tmp/hf_cache` within the container as defined in the `Dockerfile`.

If the Space is private, ensure you pass an `Authorization: Bearer YOUR_HF_TOKEN` header with your requests.
```

### `Dockerfile`

```dockerfile
# Use Python slim base image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Install curl for health checks (and other minimal tools if needed)
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Set environment variables for HF cache (use a writable directory like /tmp)
ENV HF_HOME=/tmp/huggingface_cache
ENV HF_HUB_CACHE=/tmp/huggingface_cache/hub
ENV TRANSFORMERS_CACHE=/tmp/huggingface_cache/transformers
ENV HF_DATASETS_CACHE=/tmp/huggingface_cache/datasets
# Create the cache directories and ensure they are world-writable
# This is crucial as the user running the app inside the Space might be non-root
RUN mkdir -p $HF_HOME $HF_HUB_CACHE $TRANSFORMERS_CACHE $HF_DATASETS_CACHE && \
    chmod -R 777 /tmp/huggingface_cache

# Copy and install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Optional: expose the port if testing locally
EXPOSE 7860

# Health check endpoint (optional for Docker environments that support it)
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:7860/health || exit 1

# Default command to run the API
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
```

### `app.py`

```python
from fastapi import FastAPI
from sentence_transformers import SentenceTransformer
from pydantic import BaseModel

app = FastAPI()
model = SentenceTransformer("BAAI/bge-base-en-v1.5")

class EmbedRequest(BaseModel):
    text: str

@app.post("/embed")
async def embed_text(request: EmbedRequest):
    # Apply BGE-specific query wrapping
    processed_text = f"Represent this sentence for searching relevant passages: {request.text}"
    embedding = model.encode(processed_text).tolist()
    return {"embedding": embedding}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

### `requirements.txt`

```
fastapi>=0.68.0
uvicorn>=0.15.0
sentence-transformers>=2.2.2
qdrant-client>=1.1.1
