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

# Create the primary cache directories in /tmp and ensure they are world-writable
RUN mkdir -p $HF_HOME $HF_HUB_CACHE $TRANSFORMERS_CACHE $HF_DATASETS_CACHE && \
    chmod -R 777 /tmp/huggingface_cache

# ALSO attempt to create and permission the /data/.cache path structure
# This is a fallback in case some part of the library defaults to /data
# It's better if it uses /tmp, but this might prevent the /data permission error.
RUN mkdir -p /data/.cache/huggingface/transformers && \
    chmod -R 777 /data || echo "Could not chmod /data, continuing..." && \
    chmod -R 777 /data/.cache || echo "Could not chmod /data/.cache, continuing..."

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
