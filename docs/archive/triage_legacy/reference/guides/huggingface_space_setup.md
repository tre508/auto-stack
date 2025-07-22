# Hugging Face Space Setup Guide for BAAI/bge-base-en-v1.5 Embedding Model

## Space Creation

1. Go to [Hugging Face Spaces](https://huggingface.co/spaces) and click "Create new Space"
2. Configure with these settings:
   - **Name**: `bge-embedding-api`
   - **SDK**: Docker
   - **Template**: Blank
   - **Hardware**: CPU basic
   - **Visibility**: Private (recommended)

## Implementation Files

### Dockerfile
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

### requirements.txt
```
fastapi>=0.68.0
uvicorn>=0.15.0
sentence-transformers>=2.2.2
qdrant-client>=1.1.1
```

### app.py
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

## Deployment Steps

1. Push these files to your Space repository (Dockerfile, app.py, requirements.txt).
2. The `Dockerfile` sets `HF_HOME` and `TRANSFORMERS_CACHE` to `/tmp/hf_cache`. If you need to override these in the Space's "Secrets and variables" settings, ensure they point to a writable path (e.g., `/tmp/some_other_cache_dir`). Otherwise, no explicit environment variable configuration for cache paths is needed in the Space settings.
3. Wait for the build to complete (typically 2-5 minutes).

## Testing Your API

**Note on Authentication for Private Spaces:** If your Space is set to "Private", you will need to include an `Authorization` header with a Hugging Face User Access Token (with `read` access). You can generate a token from your Hugging Face account settings.

### Curl Example
```bash
# For Public Spaces:
curl -X POST "https://GleshenCOCO-bge-embedding-api.hf.space/embed" \
  -H "Content-Type: application/json" \
  -d '{"text": "sample query"}'

# For Private Spaces (replace YOUR_HF_TOKEN):
curl -X POST "https://GleshenCOCO-bge-embedding-api.hf.space/embed" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_HF_TOKEN" \
  -d '{"text": "sample query"}'
```

### Python Example
```python
import requests

space_url = "https://GleshenCOCO-bge-embedding-api.hf.space/embed"
headers = {"Content-Type": "application/json"}

# For Private Spaces, add your token:
# headers["Authorization"] = "Bearer YOUR_HF_TOKEN"

response = requests.post(
    space_url,
    json={"text": "sample query"},
    headers=headers
)
print(response.json())
```

## Integration with Existing System

To connect with your Mem0/Qdrant setup:
1. Update your `mem0/server/config.yaml` embedder section.
   If your Space is **public**:
   ```yaml
   embedder:
     provider: "custom" # Or "openai" if your custom endpoint mimics it
     config:
       model: "BAAI/bge-base-en-v1.5" # Informational, actual model is on the Space
       endpoint: "https://GleshenCOCO-bge-embedding-api.hf.space/embed"
       # For OpenAI provider type, you might need to specify api_key if your custom endpoint expects it,
       # even if it's a dummy value for a public endpoint.
       # api_key: "dummy_key_if_needed" 
   ```
   If your Space is **private**, you'll need to ensure your Mem0 service (or the HTTP client it uses) can send the Authorization header.
   The `custom` provider in Mem0 might not directly support adding custom headers like `Authorization`.
   You might need to:
     a. Use a proxy that adds the token.
     b. Modify Mem0's HTTP client logic if possible (advanced).
     c. Consider making the Space public if security allows and it's only accessed by Mem0.
     d. If Mem0's `openai` provider type is used and it allows setting `api_key`, and your Space API can be modified to accept the token via `api_key` (e.g. in a query param or a different header that Mem0 *can* send), that could be a workaround.

   A common way Mem0 handles custom embedders is via the `openai` provider type, pointing `OPENAI_BASE_URL` to your custom service and `OPENAI_API_KEY` to a token if the service expects it.
   If your Space API is adapted to accept the HF token as `OPENAI_API_KEY` (e.g. by reading `Authorization: Bearer <value_of_OPENAI_API_KEY>`), you could configure Mem0 like this:
   ```yaml
   embedder:
     provider: "openai" # This tells Mem0 to use its OpenAI client logic
     config:
       model: "BAAI/bge-base-en-v1.5" # This will be sent in the request body
       # temperature: 0 # Optional, might be ignored by your Space
   ```
   And in your `.env` or Docker environment for Mem0:
   ```env
   OPENAI_API_KEY="YOUR_HF_TOKEN"
   OPENAI_BASE_URL="https://GleshenCOCO-bge-embedding-api.hf.space/v1" # Note: OpenAI provider usually expects /v1 path
   ```
   Your FastAPI app on the Space would need to be adjusted to handle requests at `/v1/embeddings` and read the token from the `Authorization` header, which the OpenAI client sends using `OPENAI_API_KEY`.

   **Recommended approach for private Space with current Mem0:**
   The simplest way if Mem0's `custom` provider doesn't support headers is to make the Space API expect the token in a way Mem0 *can* send it, or use an intermediary proxy. Given the `app.py` provided, it doesn't currently handle authentication.

   For now, the guide assumes a public Space or that you will handle authentication outside of Mem0's direct configuration if the Space is private and Mem0's `custom` provider lacks header support. The `config.yaml` example below is for a public Space or one where auth is handled by an intermediary:
   ```yaml
   embedder:
     provider: "custom"
     config:
       endpoint: "https://GleshenCOCO-bge-embedding-api.hf.space/embed"
   ```

## Managing Your Space with Git

Your Hugging Face Space is a Git repository. You can manage its files and configuration locally (e.g., from your WSL terminal) and push changes to update the live Space.

1.  **Prerequisites in WSL/Local Terminal**:
    *   **Git**: Ensure Git is installed. For Debian/Ubuntu-based WSL: `sudo apt update && sudo apt install git -y`
    *   **Hugging Face CLI**: Install the `huggingface-hub` Python library, which includes the command-line interface: `pip install -U huggingface-hub`

2.  **Authenticate with Hugging Face CLI (for Git)**:
    *   Run the login command in your terminal:
        ```bash
        huggingface-cli login
        ```
    *   This will prompt you for a Hugging Face User Access Token. Generate a token from your [Hugging Face account settings](https://huggingface.co/settings/tokens) (ensure it has `write` permissions if you intend to push to new repositories or manage access).
    *   Pasting the token will log you in. Crucially, this command also configures Git to use your token for authenticating HTTPS operations with Hugging Face, allowing you to `git clone`, `git pull`, and `git push` to private Spaces and repositories seamlessly.
    *   **Note on SSH Keys**: Using `huggingface-cli login` (which uses HTTPS and tokens) means you do **not** need to set up SSH keys for Git access to your Space. SSH is an alternative authentication method that you can set up separately if preferred, but it's not required if using the token-based HTTPS method.

3.  **Clone Your Space**:
    *   Using HTTPS (recommended if you've used `huggingface-cli login`):
        ```bash
        git clone https://huggingface.co/spaces/GleshenCOCO/bge-embedding-api
        ```
    *   If you have set up SSH keys with Hugging Face and prefer to use SSH, the clone URL would be:
        ```bash
        # git clone git@huggingface.co:spaces/GleshenCOCO/bge-embedding-api.git
        ```
    *Note: If you used `huggingface-cli login`, Git will automatically use your token for HTTPS authentication. If you haven't, and the Space is private, you might be prompted for credentials for HTTPS, or your SSH setup would be used if cloning via SSH.*

4.  **Navigate to Directory**: `cd bge-embedding-api`
5.  **Edit Files**:
    *   Modify `Dockerfile`, `app.py`, `requirements.txt` as needed.
    *   **Configure Metadata**: Edit the `README.md` file. Space settings like title, SDK type, port, license, etc., are defined in a YAML frontmatter block at the top of this file. For example:
        ```yaml
        ---
        title: Bge Embedding Api
        emoji: 🚀
        colorFrom: purple
        colorTo: indigo
        sdk: docker
        pinned: false
        license: apache-2.0
        app_port: 7860 # Ensure this matches the port your app listens on (e.g., 7860 for Uvicorn)
        short_description: High-speed dual-stack embedder via FastAPI & Docker
        ---

        # BGE Embedding API Space
        (Rest of your README content...)
        ```
6.  **Commit and Push Changes**:
    ```bash
    git add .
    git commit -m "Describe your changes"
    git push
    ```
    Pushing to the `main` branch (or the configured production branch) will trigger a rebuild and redeployment of your Space on Hugging Face.
7.  **Local Docker Testing (Recommended)**:
    *   If you have Docker installed locally (e.g., Docker Desktop with WSL integration), you can build and test your Space's Docker image before pushing:
        ```bash
        docker build -t my-bge-space .
        docker run -p 7860:7860 my-bge-space
        ```
    *   This helps catch issues with your `Dockerfile` or application code early.

## Performance Notes
- First request may take 10-20s while model loads
- Expect ~300ms latency per embedding request
- Max payload size: 10MB (HF Spaces limit)
