import logging
import os
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
from typing import List, Dict, Any
import yaml # For loading config.yaml

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Initialize mem0_client and attach to app.state
MEM0_CONFIG_FILE_PATH = os.getenv("MEM0_CONFIG_PATH", "/app/config.yaml")
logger.info(f"MEM0_CONFIG_FILE_PATH is set to: {MEM0_CONFIG_FILE_PATH}")

try:
    from mem0 import Memory # Correct import for OSS self-hosted
    
    logger.info(f"Checking for config file existence at: {MEM0_CONFIG_FILE_PATH}")
    config_exists = os.path.exists(MEM0_CONFIG_FILE_PATH)
    logger.info(f"Config file exists: {config_exists}")

    if config_exists:
        logger.info(f"Attempting to load Mem0 configuration from: {MEM0_CONFIG_FILE_PATH}")
        with open(MEM0_CONFIG_FILE_PATH, 'r') as f:
            config_dict = yaml.safe_load(f)
        logger.info(f"Loaded config_dict: {config_dict}")
        
        logger.info(f"OPENAI_API_KEY from env for Mem0 init: {os.getenv('OPENAI_API_KEY')}")
        logger.info(f"OPENAI_BASE_URL from env for Mem0 init: {os.getenv('OPENAI_BASE_URL')}")

        app.state.mem0_client = Memory.from_config(config_dict) # Attach to app.state
        logger.info(f"Mem0 client initialized and attached to app.state using configuration from {MEM0_CONFIG_FILE_PATH}.")
    else:
        logger.error(f"CRITICAL: Mem0 configuration file not found at {MEM0_CONFIG_FILE_PATH}. Cannot initialize Mem0 client.")
        app.state.mem0_client = None # Ensure it's None on app.state
        raise FileNotFoundError(f"CRITICAL: Mem0 configuration file not found at {MEM0_CONFIG_FILE_PATH}. Aborting.")

except ImportError:
    logger.error("Failed to import Memory from mem0. Ensure 'mem0ai' pip package is installed and 'mem0' module is available.")
    app.state.mem0_client = None # Explicitly set to None on import error
    raise # Re-raise import error to make it obvious
except Exception as e:
    logger.error(f"Failed to initialize Mem0 client and attach to app.state (path: {MEM0_CONFIG_FILE_PATH}): {e}")
    app.state.mem0_client = None # Explicitly set to None on other init errors
    raise # Re-raise other init errors


class Message(BaseModel):
    role: str
    content: str

class MemoryAddPayload(BaseModel):
    messages: List[Message]
    user_id: str
    metadata: dict | None = None

@app.post("/memory")
async def add_memory(payload: MemoryAddPayload, request: Request):
    logger.info(f"[/memory] endpoint called with payload: {payload.model_dump_json()}")
    client = request.app.state.mem0_client # Get client from app.state
    if not client:
        logger.error("[/memory] Mem0 client not initialized on app.state.")
        raise HTTPException(status_code=500, detail="Mem0 client not initialized. Mem0 functionality is unavailable.")

    try:
        # Convert Pydantic Message objects to dicts for mem0.add()
        messages_as_dicts = [message.model_dump() for message in payload.messages]
        client.add(
            messages_as_dicts, # Pass the list of dicts
            user_id=payload.user_id,
            metadata=payload.metadata or {}
        )
        logger.info("[/memory] Memory saved successfully.")
        return {"status": "memory saved"}
    except Exception as e:
        logger.error(f"[/memory] Failed to save memory: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save memory: {e}")


class MemorySearchPayload(BaseModel):
    query: str
    user_id: str
    # Add other potential search parameters like filters, limit, threshold if needed later

@app.post("/search")
async def search_memory(payload: MemorySearchPayload, request: Request):
    logger.info(f"[/search] endpoint called with payload: {payload.model_dump_json()}")
    client = request.app.state.mem0_client # Get client from app.state
    if not client:
        logger.error("[/search] Mem0 client not initialized on app.state.")
        raise HTTPException(status_code=500, detail="Mem0 client not initialized. Mem0 functionality is unavailable.")

    try:
        results = client.search(
            query=payload.query,
            user_id=payload.user_id
            # Pass other search parameters if added to payload model
        )
        logger.info(f"[/search] Memory search completed. Returned {len(results)} results.")
        return results # mem0_client.search is expected to return a list or similar structure
    except Exception as e:
        logger.error(f"[/search] Failed to search memory: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to search memory: {e}")


# Add DELETE endpoint (optional for MVP, but good to include the structure)
# class MemoryDeletePayload(BaseModel):
#     memory_id: str | None = None
#     user_id: str | None = None # To delete all for a user

# @app.delete("/memory")
# async def delete_memory(payload: MemoryDeletePayload):
#     logger.info(f"[/memory DELETE] endpoint called with payload: {payload.model_dump_json()}")
#     if not mem0_client:
#         logger.error("[/memory DELETE] Mem0 client not initialized.")
#         raise HTTPException(status_code=500, detail="Mem0 client not initialized. Mem0 functionality is unavailable.")

#     try:
#         if payload.memory_id:
#             mem0_client.delete(payload.memory_id)
#             logger.info(f"[/memory DELETE] Deleted memory ID: {payload.memory_id}")
#             return {"status": f"Memory ID {payload.memory_id} deleted"}
#         elif payload.user_id:
#              mem0_client.delete_all(user_id=payload.user_id)
#              logger.info(f"[/memory DELETE] Deleted all memories for user: {payload.user_id}")
#              return {"status": f"All memories for user {payload.user_id} deleted"}
#         else:
#             raise HTTPException(status_code=400, detail="Either memory_id or user_id must be provided for deletion.")
#     except Exception as e:
#         logger.error(f"[/memory DELETE] Failed to delete memory: {e}")
#         raise HTTPException(status_code=500, detail=f"Failed to delete memory: {e}")


@app.get("/status")
async def get_status(request: Request):
    logger.info("[/status] endpoint called.")
    client = request.app.state.mem0_client # Get client from app.state
    if not client:
         logger.error("[/status] Mem0 client not initialized on app.state.")
         raise HTTPException(status_code=500, detail="Mem0 client not initialized. Check server logs.")
    
    try:
        # Perform a lightweight search operation as a health check
        # This assumes that if the client is initialized and can search (even if no results), it's healthy
        client.search(query="_health_check_", user_id="_health_check_user_", limit=1)
        logger.info("[/status] Mem0 client health check (search) successful.")
        return {"status": "Mem0 service is running and client is healthy"}
    except Exception as e:
        logger.error(f"[/status] Mem0 client health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Mem0 client health check failed: {e}")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port) 