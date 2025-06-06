import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import logging
import httpx
import requests # Note: httpx is generally preferred for async, but requests is used for one endpoint. Consider standardizing.
from typing import Optional, Dict, Any

app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Environment Variables ---
# For existing Mem0 direct interaction (if still needed, or for other controller functions)
MEM0_SERVICE_BASE_URL = os.getenv("MEM0_API_URL") 
if not MEM0_SERVICE_BASE_URL:
    logger.info("MEM0_API_URL not set. Direct controller calls to Mem0 service might fail if used elsewhere.")

N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "http://n8n:5678/webhook/centralbrain_agent")
EKO_SERVICE_URL = os.getenv("EKO_SERVICE_URL", "http://localhost:3001/run_eko") # Eko service URL

# For Mem0 OpenAI Proxy functionality
HF_SPACE_EMBEDDER_ENDPOINT = os.getenv("HF_SPACE_EMBEDDER_ENDPOINT") # e.g., https://GleshenCOCO-bge-embedding-api.hf.space/v1/embeddings
OPENROUTER_PROXY_SERVICE_URL = os.getenv("OPENROUTER_PROXY_SERVICE_URL") # e.g., http://openrouter_proxy_mcp:8000/v1
CONTROLLER_OPENROUTER_API_KEY = os.getenv("CONTROLLER_OPENROUTER_API_KEY") # Actual OpenRouter API Key for the controller to use

if not HF_SPACE_EMBEDDER_ENDPOINT:
    logger.warning("HF_SPACE_EMBEDDER_ENDPOINT not set. Mem0 proxy for embeddings will fail.")
if not OPENROUTER_PROXY_SERVICE_URL:
    logger.warning("OPENROUTER_PROXY_SERVICE_URL not set. Mem0 proxy for LLM chat completions will fail.")
if not CONTROLLER_OPENROUTER_API_KEY:
    logger.warning("CONTROLLER_OPENROUTER_API_KEY not set. Mem0 proxy for LLM chat completions will fail (cannot authenticate with OpenRouter proxy).")


# --- Helper functions for direct Mem0 interaction (existing) ---
async def add_memory_to_mem0_service(messages: list, user_id: str, metadata: Optional[dict] = None):
    if not MEM0_SERVICE_BASE_URL:
        logger.error("Cannot add memory: MEM0_API_URL not configured for controller.")
        return False
    
    payload = {
        "messages": messages,
        "user_id": user_id,
        "metadata": metadata or {}
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{MEM0_SERVICE_BASE_URL}/memory", json=payload)
            response.raise_for_status()
            logger.info(f"Memory added to Mem0 service for user {user_id}. Response: {response.json()}")
            return True
    except httpx.RequestError as e:
        logger.error(f"Error calling Mem0 service /memory: {e}")
    except httpx.HTTPStatusError as e:
        logger.error(f"Mem0 service /memory returned error {e.response.status_code}: {e.response.text}")
    except Exception as e:
        logger.error(f"Unexpected error adding memory to Mem0 service: {e}")
    return False

async def search_memory_in_mem0_service(query: str, user_id: str):
    if not MEM0_SERVICE_BASE_URL:
        logger.error("Cannot search memory: MEM0_API_URL not configured for controller.")
        return None # Or raise exception

    payload = {"query": query, "user_id": user_id}
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{MEM0_SERVICE_BASE_URL}/search", json=payload)
            response.raise_for_status()
            logger.info(f"Search successful in Mem0 service for user {user_id}, query '{query}'.")
            return response.json()
    except httpx.RequestError as e:
        logger.error(f"Error calling Mem0 service /search: {e}")
    except httpx.HTTPStatusError as e:
        logger.error(f"Mem0 service /search returned error {e.response.status_code}: {e.response.text}")
    except Exception as e:
        logger.error(f"Unexpected error searching memory in Mem0 service: {e}")
    return None

@app.get("/status")
async def get_status():
    logger.info("Status endpoint was called.")
    return {"status": "Controller is running"}

@app.post("/execute")
async def execute_task(payload: dict):
    logger.info(f"Execute endpoint called with payload: {payload}")
    if not N8N_WEBHOOK_URL:
        logger.error("N8N_WEBHOOK_URL is not set.")
        raise HTTPException(status_code=500, detail="N8N_WEBHOOK_URL not configured")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(N8N_WEBHOOK_URL, json=payload)
            response.raise_for_status() # Raise an exception for bad status codes
            logger.info(f"Successfully forwarded payload to n8n. Response: {response.text}")
            return {"message": "Payload forwarded to n8n", "n8n_response": response.json()}
        except httpx.RequestError as e:
            logger.error(f"Error calling n8n webhook: {e}")
            raise HTTPException(status_code=502, detail=f"Error calling n8n webhook: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

@app.post("/api/v1/execute_eko")
async def execute_eko(payload: dict):
    logger.info(f"Execute_eko endpoint called with payload: {payload}")
    prompt = payload.get("prompt")
    if not prompt:
        logger.error("No prompt provided in payload for Eko execution.")
        raise HTTPException(status_code=400, detail="'prompt' is a required field in the payload.")

    if not EKO_SERVICE_URL:
        logger.error("EKO_SERVICE_URL is not set. Cannot execute Eko workflow.")
        raise HTTPException(status_code=500, detail="EKO_SERVICE_URL not configured.")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(EKO_SERVICE_URL, json={"prompt": prompt})
            response.raise_for_status()
            eko_result = response.json()
            workflow_id = eko_result.get("workflow_id")
            result_data = eko_result.get("result")

        # Store Eko plan and result in Mem0 via its service API
        if MEM0_SERVICE_BASE_URL: # Check if Mem0 integration is configured
            plan_content_str = eko_result.get("workflow_plan_json")
            if plan_content_str:
                # Mem0 expects a list of messages. Create a simple one for the plan.
                plan_messages = [{"role": "system", "content": f"Eko workflow plan: {plan_content_str}"}]
                await add_memory_to_mem0_service(
                    messages=plan_messages,
                    user_id="eko_controller_agent",
                    metadata={"type": "eko_plan", "prompt": prompt, "workflow_id": workflow_id}
                )
            
            if result_data is not None:
                result_messages = [{"role": "system", "content": f"Eko workflow result: {str(result_data)}"}]
                await add_memory_to_mem0_service(
                    messages=result_messages,
                    user_id="eko_controller_agent",
                    metadata={"type": "eko_result", "workflow_id": workflow_id}
                )
        else:
            logger.warning("MEM0_API_URL not set. Eko workflow data not stored in Mem0.")
        
        logger.info(f"Eko workflow executed successfully via Node.js service for prompt: {prompt}")
        return {"workflow_id": workflow_id, "result": result_data}
    except httpx.RequestError as e:
         logger.error(f"Error calling local Eko Node.js service: {e}")
         raise HTTPException(status_code=502, detail=f"Error calling Eko service: {e}")
    except httpx.HTTPStatusError as e:
         logger.error(f"Eko Node.js service returned error {e.response.status_code}: {e.response.text}")
         raise HTTPException(status_code=e.response.status_code, detail=f"Eko service error: {e.response.text}")
    except Exception as e:
        logger.error(f"An unexpected error occurred during Eko execution: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

@app.post("/notify")
async def notify_controller(payload: dict):
    logger.info(f"Notify endpoint called with payload: {payload}")
    # In a real scenario, this might trigger other actions or log notifications.
    return {"message": "Notification received", "received_payload": payload}

# Placeholder for a more sophisticated log tailing mechanism
LOG_FILE_PATH = "/app/controller.log" # Example path, ensure this is writable and configured

@app.get("/logs/tail")
async def get_logs_tail(lines: int = 50):
    logger.info(f"Log tail endpoint called for {lines} lines.")
    try:
        # This is a very basic example. For production, consider using a proper logging service 
        # or a library that handles file reading more robustly (e.g., watching for changes).
        if not os.path.exists(LOG_FILE_PATH):
            # Create an empty log file if it doesn't exist, or append to an existing one
            with open(LOG_FILE_PATH, 'a') as f:
                pass # Just create it
            logger.info(f"Log file {LOG_FILE_PATH} did not exist. Created an empty one.")
            return {"logs": "Log file was empty or just created."}

        with open(LOG_FILE_PATH, "r") as f:
            log_lines = f.readlines()
            # Simulate tailing by taking the last 'lines' lines
            tailed_lines = log_lines[-lines:]
        return {"logs": "".join(tailed_lines)}
    except Exception as e:
        logger.error(f"Error reading log file: {e}")
        raise HTTPException(status_code=500, detail=f"Error reading log file: {e}")

@app.post("/api/v1/trigger_bootstrap")
async def trigger_bootstrap():
    webhook_url = os.getenv("N8N_BOOTSTRAP_WEBHOOK")
    if not webhook_url:
        return {"error": "Missing N8N_BOOTSTRAP_WEBHOOK env var."}
    try:
        r = requests.post(webhook_url, json={})
        return {"status": "triggered", "n8n_response": r.text}
    except Exception as e:
        return {"status": "error", "details": str(e)}

# --- New Mem0 OpenAI Proxy Endpoints ---

@app.post("/mem0_openai_proxy/v1/embeddings")
async def proxy_mem0_embeddings(request: Request):
    """
    Proxies embedding requests from Mem0 to the Hugging Face Space.
    Mem0 sends its OPENAI_API_KEY (which should be the HF Token) in the Authorization header.
    """
    if not HF_SPACE_EMBEDDER_ENDPOINT:
        logger.error("HF_SPACE_EMBEDDER_ENDPOINT is not configured.")
        raise HTTPException(status_code=500, detail="Embedder proxy endpoint not configured")

    auth_header = request.headers.get("Authorization")
    if not auth_header:
        logger.warning("Missing Authorization header from Mem0 for embedding proxy.")
        # Depending on HF Space security, this might still work if the Space is public 
        # or if HF_SPACE_API_TOKEN is not set in the Space's app.py
        # For now, we'll proceed but log it. A stricter check might be needed.
        # raise HTTPException(status_code=401, detail="Missing Authorization header for embedding proxy")
    
    try:
        payload = await request.json()
        logger.info(f"Proxying embedding request to HF Space: {HF_SPACE_EMBEDDER_ENDPOINT} with payload: {payload}")
        
        async with httpx.AsyncClient() as client:
            headers_to_hf = {"Content-Type": "application/json"}
            if auth_header: # Forward the Authorization header from Mem0 to the HF Space
                headers_to_hf["Authorization"] = auth_header
            
            response_hf = await client.post(HF_SPACE_EMBEDDER_ENDPOINT, json=payload, headers=headers_to_hf)
            response_hf.raise_for_status()
            
            # Return the exact response from the HF Space API to Mem0
            return JSONResponse(content=response_hf.json(), status_code=response_hf.status_code)

    except httpx.RequestError as e:
        logger.error(f"Error requesting HF Space embedder endpoint {HF_SPACE_EMBEDDER_ENDPOINT}: {e}")
        raise HTTPException(status_code=502, detail=f"Error connecting to embedder service: {e}")
    except httpx.HTTPStatusError as e:
        logger.error(f"HF Space embedder endpoint {HF_SPACE_EMBEDDER_ENDPOINT} returned error {e.response.status_code}: {e.response.text}")
        # Forward the exact error if possible, or a generic one
        return JSONResponse(content=e.response.json(), status_code=e.response.status_code)
    except Exception as e:
        logger.error(f"Unexpected error in embedding proxy: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error in embedding proxy: {e}")

@app.post("/mem0_openai_proxy/v1/chat/completions")
async def proxy_mem0_chat_completions(request: Request):
    """
    Proxies chat completion requests from Mem0 to the OpenRouter Proxy service.
    The controller uses its own CONTROLLER_OPENROUTER_API_KEY to authenticate with the OpenRouter Proxy.
    The Authorization header from Mem0 (containing HF Token) is ignored for this route.
    """
    if not OPENROUTER_PROXY_SERVICE_URL or not CONTROLLER_OPENROUTER_API_KEY:
        logger.error("OpenRouter proxy URL or Controller's OpenRouter API key is not configured.")
        raise HTTPException(status_code=500, detail="LLM proxy not configured")

    try:
        payload = await request.json()
        logger.info(f"Proxying chat completion request to OpenRouter Proxy: {OPENROUTER_PROXY_SERVICE_URL}/chat/completions with payload: {payload}")

        # Prepare headers for the OpenRouter Proxy
        # The OpenRouter Proxy itself expects an Authorization: Bearer <OpenRouter Key>
        # but our local openrouter_proxy_mcp service injects this key.
        # So, we might not need to send an Auth header to openrouter_proxy_mcp if it's designed to work without one from internal services,
        # or it might expect a dummy one. Let's assume it doesn't need one from the controller for now,
        # as it's an internal service call. If it does, this needs adjustment.
        # The actual OPENROUTER_API_KEY is used by the openrouter_proxy_mcp service itself.
        
        headers_to_orp = {"Content-Type": "application/json"}
        # If your openrouter_proxy_mcp requires an auth token itself (even a dummy one), add it here.
        # For now, assuming direct call to the proxy which then uses CONTROLLER_OPENROUTER_API_KEY.
        # The CONTROLLER_OPENROUTER_API_KEY is for the proxy to talk to OpenRouter.ai, not for controller to talk to proxy.

        async with httpx.AsyncClient() as client:
            # The URL should be like http://openrouter_proxy_mcp:8000/v1/chat/completions
            # OPENROUTER_PROXY_SERVICE_URL is expected to be http://openrouter_proxy_mcp:8000/v1
            response_orp = await client.post(f"{OPENROUTER_PROXY_SERVICE_URL}/chat/completions", json=payload, headers=headers_to_orp)
            response_orp.raise_for_status()
            
            # Return the exact response from the OpenRouter Proxy to Mem0
            return JSONResponse(content=response_orp.json(), status_code=response_orp.status_code)

    except httpx.RequestError as e:
        logger.error(f"Error requesting OpenRouter Proxy chat/completions endpoint: {e}")
        raise HTTPException(status_code=502, detail=f"Error connecting to LLM service: {e}")
    except httpx.HTTPStatusError as e:
        logger.error(f"OpenRouter Proxy chat/completions endpoint returned error {e.response.status_code}: {e.response.text}")
        return JSONResponse(content=e.response.json(), status_code=e.response.status_code)
    except Exception as e:
        logger.error(f"Unexpected error in chat completions proxy: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error in chat completions proxy: {e}")


if __name__ == "__main__":
    # This part is for local debugging if you run controller.py directly
    # Uvicorn will run this when used in Docker as specified in the CMD
    import uvicorn
    # Respect PORT if set (e.g. by Dockerfile ENV), fallback to CONTROLLER_PORT, then to 5050
    port = int(os.getenv("PORT", os.getenv("CONTROLLER_PORT", "5050")))
    uvicorn.run(app, host="0.0.0.0", port=port)
