# 🔄 Switching Mem0 Embedder to `BAAI/bge-base-en-v1.5`

This guide walks you through updating your self-hosted Mem0 stack to use a high-quality, free local embedding model.

---

## 1. Update `config.yaml`

Replace your `config.yaml` embedder section with:

```yaml
embedder:
  provider: "huggingface"
  config:
    model: "BAAI/bge-base-en-v1.5"

vectorstore:
  provider: "qdrant"
  config:
    host: "qdrant_mcp"
    port: 6333
    collection: "mem0_autostack_collection"
```

---

## 2. Update `.env`

Append this to `.env` if you're running HuggingFace in cached/offline mode:

```env
# Ensure your Docker/.env file includes this if you run HuggingFace offline cache or need tokens
HF_HOME=/data/.cache/huggingface
TRANSFORMERS_CACHE=/data/.cache/huggingface/transformers
```

---

## 3. Delete Existing Qdrant Collection

1. Open n8n and create a new workflow named "Delete Qdrant Collection".
2. Add a `HTTP Request` node:
   - **Name**: `Delete Qdrant Collection`
   - **Method**: DELETE
   - **URL**: `http://qdrant_mcp:6333/collections/mem0_autostack_collection`
   - **Options > Full Response**: false
   - **Continue On Fail**: true (optional)
3. Trigger manually or from a button node.

> This will reset your vector DB so Mem0 can recreate it with the new embedding model (768-dim).

---

## 4. Add Prompt Wrapping in Search Queries

Add a `Set` node before the 'Search Memory in Mem0' node:
- Field Name: `query`
- Value (Expression):
  {{ "Represent this sentence for searching relevant passages: " + $json["query"] }}
This improves embedding quality with BAAI/bge models.

---

## Additional Notes

- After making the config changes, **restart Mem0** to reinitialize the vector store.
- You must **re-insert your memory** using the updated model before using search.
- Optionally add a logging node in n8n to save all memory events to Postgres or filesystem.

---

## Recommended Model Resources
- [BAAI/bge-base-en-v1.5 on HuggingFace](https://huggingface.co/BAAI/bge-base-en-v1.5)
- [Qdrant Collection Management API](https://qdrant.tech/documentation/concepts/collections/)