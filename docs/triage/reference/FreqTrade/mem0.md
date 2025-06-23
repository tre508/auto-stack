# Mem0: Storage & Embedding Notes

## 🔧 Current State

- Stores performance logs via `add_memory_to_mem0_service(...)`
- Data insertion confirmed working via logs

## ❗Known Issue

- Embedding mismatch: BGE-small (768-dim) vs Mem0 expected 1536-dim
- Search failures are caused by this dimensionality conflict

## To Fix
- Check Mem0 model config or wrapper
- Either reduce Mem0 expectation or match a higher-dim embedding model 