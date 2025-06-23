# Known Integration Issues

## 🧠 Mem0 Search Fails
- BGE-small uses 768-dim embeddings
- Mem0 requests 1536-dim vectors
- Fix: Unify dimensionality between generator and vector store

## 🐍 TA-Lib Build Failure (Dev Env Only)
- `ta-lib` Python wheel fails to build on some machines
- Freqtrade binary includes it — no runtime impact
- Fix: Install system headers, or ignore in dev environment 