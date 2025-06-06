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
