from fastapi import FastAPI, Request, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel, Field
from typing import List, Union, Dict, Any
from sentence_transformers import SentenceTransformer
import os

# Configuration
# For secure token validation, set HF_SPACE_API_TOKEN in your Hugging Face Space secrets.
# This should be the same token your Mem0 service will use (e.g., your HF User Access Token).
EXPECTED_HF_TOKEN = os.environ.get("HF_SPACE_API_TOKEN") 

app = FastAPI(
    title="BGE Embedding API (OpenAI Compatible)",
    version="1.0.0",
    description="Generates embeddings using BAAI/bge-base-en-v1.5, compatible with OpenAI client requests."
)

# --- Authentication ---
API_KEY_NAME = "Authorization"
api_key_header_auth = APIKeyHeader(name=API_KEY_NAME, auto_error=False) # auto_error=False to handle manually

async def get_api_key(api_key_header: str = Security(api_key_header_auth)):
    if api_key_header is None:
        # This allows requests if EXPECTED_HF_TOKEN is not set (e.g. for public testing or if auth is handled upstream)
        # However, if EXPECTED_HF_TOKEN is set, a token MUST be provided.
        if EXPECTED_HF_TOKEN:
            raise HTTPException(status_code=403, detail="Not authenticated: Authorization header missing")
        return None # No token provided, but not strictly required if EXPECTED_HF_TOKEN is not set

    if not api_key_header.startswith("Bearer "):
        raise HTTPException(status_code=403, detail="Invalid Authorization header format. Must be Bearer token.")
    
    token = api_key_header.split(" ")[1]

    if EXPECTED_HF_TOKEN and token != EXPECTED_HF_TOKEN:
        print(f"Token mismatch. Expected: '{EXPECTED_HF_TOKEN[:5]}...', Got: '{token[:5]}...'") # Log for debugging
        raise HTTPException(status_code=403, detail="Invalid API Key/Token")
    return token

# --- Model Loading ---
sbert_model = SentenceTransformer("BAAI/bge-base-en-v1.5")

# --- Pydantic Models for OpenAI Compatibility ---
class OpenAIEmbeddingRequest(BaseModel):
    input: Union[str, List[str]]
    model: str = Field(...) # Made this simpler to satisfy Pylance, will add metadata back if this passes

class EmbeddingObject(BaseModel):
    object: str = "embedding"
    embedding: List[float]
    index: int

class UsageData(BaseModel):
    prompt_tokens: int = 0 
    total_tokens: int = 0

class OpenAIEmbeddingResponse(BaseModel):
    object: str = "list"
    data: List[EmbeddingObject]
    model: str 
    usage: UsageData


# --- API Endpoints ---
@app.post("/v1/embeddings", response_model=OpenAIEmbeddingResponse)
async def create_embeddings(
    request_body: OpenAIEmbeddingRequest, 
    # If EXPECTED_HF_TOKEN is set in Space secrets, this will enforce token validation.
    # If not set, api_key will be None, and access is permitted (less secure).
    api_key: str = Security(get_api_key) 
):
    input_texts = [request_body.input] if isinstance(request_body.input, str) else request_body.input
    
    embeddings_data = []
    total_prompt_tokens = 0
    for i, text in enumerate(input_texts):
        # BGE-specific prefix for search-related embeddings
        processed_text = f"Represent this sentence for searching relevant passages: {text}"
        total_prompt_tokens += len(processed_text.split()) # Simple token count
        
        embedding_vector = sbert_model.encode(processed_text).tolist()
        embeddings_data.append(EmbeddingObject(embedding=embedding_vector, index=i))

    usage = UsageData(prompt_tokens=total_prompt_tokens, total_tokens=total_prompt_tokens)

    return OpenAIEmbeddingResponse(
        data=embeddings_data,
        model=request_body.model, 
        usage=usage
    )

@app.get("/health", summary="Health Check")
async def health_check():
    return {"status": "healthy", "model_name": "BAAI/bge-base-en-v1.5"}

@app.get("/")
async def root():
    return {
        "message": "BGE Embedding API (OpenAI Compatible) is running.",
        "docs_url": "/docs",
        "model_name": "BAAI/bge-base-en-v1.5",
        "endpoints": {
            "embeddings": "/v1/embeddings (POST)",
            "health_check": "/health (GET)"
        }
    }

# Note: To make token authentication mandatory, ensure HF_SPACE_API_TOKEN is set 
# in your Hugging Face Space secrets. If it's not set, the API will be accessible 
# without a token for easier public testing if needed, but this is not recommended for private data.
