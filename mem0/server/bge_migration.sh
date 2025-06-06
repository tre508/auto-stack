#!/bin/bash

# Mem0 BGE Embeddings Migration Script
# This script handles the restart of Mem0 after migration to BAAI/bge-base-en-v1.5

echo "========================================"
echo "Mem0 BGE Embeddings Migration Assistant"
echo "========================================"

# Check if running in Docker environment
if [ -f /.dockerenv ]; then
    echo "[INFO] Running inside Docker container"
    DOCKER_MODE=true
else
    echo "[INFO] Running in host environment"
    DOCKER_MODE=false
fi

# Step 1: Verify configuration changes
echo -e "\n[STEP 1] Verifying configuration changes..."

if [ -f "config.yaml" ]; then
    if grep -q "BAAI/bge-base-en-v1.5" config.yaml; then
        echo "✅ config.yaml updated with BAAI/bge-base-en-v1.5"
    else
        echo "❌ config.yaml not updated with BAAI/bge-base-en-v1.5"
        echo "Please update embedder section in config.yaml first"
        exit 1
    fi
else
    echo "❌ config.yaml not found in current directory"
    echo "Run this script from the Mem0 server directory"
    exit 1
fi

# Step 2: Check Qdrant connectivity
echo -e "\n[STEP 2] Checking Qdrant connectivity..."
QDRANT_HOST="qdrant_mcp"
QDRANT_PORT=6333

if $DOCKER_MODE; then
    # Inside Docker, use internal network
    if curl -s "http://${QDRANT_HOST}:${QDRANT_PORT}/collections" > /dev/null; then
        echo "✅ Qdrant is accessible"
    else
        echo "❌ Cannot connect to Qdrant at ${QDRANT_HOST}:${QDRANT_PORT}"
        echo "Please ensure Qdrant service is running"
        exit 1
    fi
else
    # On host, check if Docker container is running
    if command -v docker > /dev/null; then
        if docker ps | grep -q qdrant_mcp; then
            echo "✅ Qdrant container is running"
        else
            echo "❌ Qdrant container (qdrant_mcp) not found or not running"
            echo "Please start the container first"
            exit 1
        fi
    else
        echo "⚠️ Docker not found, skipping container check"
    fi
fi

# Step 3: Restart Mem0
echo -e "\n[STEP 3] Restarting Mem0 service..."

if $DOCKER_MODE; then
    echo "When running in Docker, you need to restart the container from the host."
    echo "Exit this container and run: docker restart mem0_mcp"
else
    if command -v docker > /dev/null; then
        echo "Restarting Mem0 container..."
        docker restart mem0_mcp
        if [ $? -eq 0 ]; then
            echo "✅ Mem0 container restarted successfully"
        else
            echo "❌ Failed to restart Mem0 container"
            exit 1
        fi
    else
        echo "❌ Docker not found, cannot restart container"
        echo "Please restart Mem0 service manually"
        exit 1
    fi
fi

# Step 4: Post-restart verification
echo -e "\n[STEP 4] Post-restart verification..."
echo "Waiting for Mem0 to initialize (15 seconds)..."
sleep 15

# Check if Mem0 API is responding
if $DOCKER_MODE; then
    # Inside Docker, check loopback
    if curl -s "http://localhost:7860/api/health" > /dev/null; then
        echo "✅ Mem0 API is accessible"
    else
        echo "⚠️ Cannot reach Mem0 API - this may be normal if checking from inside container"
    fi
else
    # On host, check container
    MEM0_URL="http://localhost:7860/api/health"
    if curl -s "$MEM0_URL" > /dev/null; then
        echo "✅ Mem0 API is accessible"
    else
        echo "❌ Cannot reach Mem0 API at $MEM0_URL"
        echo "Please check the logs: docker logs mem0_mcp"
    fi
fi

# Step 5: Instructions for re-indexing
echo -e "\n[STEP 5] Re-indexing instructions"
echo "To re-index your memory with the new embeddings model:"
echo "1. Use the n8n workflow 'Delete Qdrant Collection' first"
echo "2. After deletion, re-insert memory entries through your usual methods"
echo "3. Verify search is working by using the 'Mem0 Search with BGE Prompt Wrapping' workflow"
echo -e "\nNote: The 'Set Query with BGE Prompt Wrapper' node in the search workflow is crucial for optimal performance with BGE embeddings"

echo -e "\n========================================"
echo "Migration Assistant Complete"
echo "========================================" 