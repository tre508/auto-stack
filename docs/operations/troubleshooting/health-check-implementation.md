# 🔧 Health Check Implementation Guide

## Root Cause Analysis

The health check failures are caused by **missing tools in containers**, not missing endpoints:

### Findings

- ✅ **n8n**: Has `wget` and `nc` available, healthz endpoint works
- ✅ **OpenRouter Proxy**: Endpoint works, but no `wget` or `curl` in container  
- ✅ **Eko Service**: Has `wget` available, but missing health endpoint
- ✅ **Controller**: Has Python/requests available, `/status` endpoint works

## Immediate Fixes Required

### 1. Fix n8n Health Check

**Current Issue:** Using `curl` which doesn't exist in container
**Solution:** Use `wget` instead

```yaml
# Current (BROKEN):
healthcheck:
  test: [ "CMD", "curl", "-f", "http://localhost:5678/healthz" ]

# Fixed:
healthcheck:
  test: [ "CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost:5678/healthz" ]
  interval: 30s
  timeout: 30s
  retries: 5
  start_period: 120s
```

### 2. Fix OpenRouter Proxy Health Check  

**Current Issue:** Using `curl` which doesn't exist in container
**Solution:** Use Node.js built-in HTTP check

```yaml
# Current (BROKEN):
healthcheck:
  test: [ "CMD", "curl", "-f", "http://localhost:8000/healthz" ]

# Fixed:
healthcheck:
  test: [ "CMD", "node", "-e", "require('http').get('http://localhost:8000/', (res) => process.exit(res.statusCode === 200 ? 0 : 1)).on('error', () => process.exit(1))" ]
  interval: 30s
  timeout: 30s
  retries: 5
  start_period: 60s
```

### 3. Fix Eko Service Health Check

**Current Issue:** Using `curl` and missing health endpoint
**Solution:** Use `wget` and add health endpoint

**Step A:** Add health endpoint to `controller/eko_service.js`:

```javascript
// Add these routes to eko_service.js
app.get('/health', (req, res) => {
    res.status(200).json({ 
        status: 'healthy',
        service: 'eko_service',
        timestamp: new Date().toISOString(),
        uptime: process.uptime()
    });
});

app.get('/healthz', (req, res) => {
    res.status(200).json({ 
        status: 'healthy',
        service: 'eko_service', 
        timestamp: new Date().toISOString(),
        uptime: process.uptime()
    });
});
```

**Step B:** Update health check in docker-compose.yml:

```yaml
# Current (BROKEN):
healthcheck:
  test: [ "CMD", "curl", "-f", "http://localhost:3001/health" ]

# Fixed:
healthcheck:
  test: [ "CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost:3001/health" ]
  interval: 30s
  timeout: 30s
  retries: 5
  start_period: 60s
```

### 4. Fix Controller Health Check

**Current Issue:** Using `curl` which doesn't exist in container  
**Solution:** Use Python requests or wget

```yaml
# Current (BROKEN):
healthcheck:
  test: [ "CMD", "curl", "-f", "http://localhost:5050/status" ]

# Fixed (using Python):
healthcheck:
  test: [ "CMD", "python", "-c", "import requests; exit(0 if requests.get('http://localhost:5050/status').status_code == 200 else 1)" ]
  interval: 30s
  timeout: 30s
  retries: 5
  start_period: 60s
```

## Implementation Steps

### Step 1: Update Eko Service Code

```bash
# Edit the eko service file
nano controller/eko_service.js

# Add the health endpoints (see code above)
```

### Step 2: Update docker-compose.yml

```bash
# Create backup
cp docker-compose.yml docker-compose.yml.backup

# Update health checks (see configurations above)
nano docker-compose.yml
```

### Step 3: Rebuild and Restart Services

```bash
# Rebuild eko service (it has code changes)
docker compose build eko_service_auto

# Restart all services with updated health checks
docker compose up -d

# Wait for health checks to stabilize
sleep 120

# Verify health status
docker compose ps
```

### Step 4: Verify Fixes

```bash
# Test health endpoints directly
wget --quiet --tries=1 --spider http://localhost:5678/healthz && echo "✅ n8n OK"
wget --quiet --tries=1 --spider http://localhost:3001/health && echo "✅ Eko OK"
curl -s http://localhost:8001/ | grep -q "OK" && echo "✅ OpenRouter OK"
curl -s http://localhost:5050/status | grep -q "running" && echo "✅ Controller OK"

# Check Docker health status
docker compose ps | grep -E "(healthy|unhealthy)"
```

## Complete docker-compose.yml Health Check Section

```yaml
services:
  n8n_auto:
    # ... other config ...
    healthcheck:
      test: [ "CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost:5678/healthz" ]
      interval: 30s
      timeout: 30s
      retries: 5
      start_period: 120s

  controller_auto:
    # ... other config ...
    healthcheck:
      test: [ "CMD", "python", "-c", "import requests; exit(0 if requests.get('http://localhost:5050/status').status_code == 200 else 1)" ]
      interval: 30s
      timeout: 30s
      retries: 5
      start_period: 60s

  eko_service_auto:
    # ... other config ...
    healthcheck:
      test: [ "CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost:3001/health" ]
      interval: 30s
      timeout: 30s
      retries: 5
      start_period: 60s

  openrouter_proxy_auto:
    # ... other config ...
    healthcheck:
      test: [ "CMD", "node", "-e", "require('http').get('http://localhost:8000/', (res) => process.exit(res.statusCode === 200 ? 0 : 1)).on('error', () => process.exit(1))" ]
      interval: 30s
      timeout: 30s
      retries: 5
      start_period: 60s
```

## Alternative Health Check Methods

### For containers without wget/curl

```yaml
# Using netcat (nc) to check if port is open
healthcheck:
  test: [ "CMD", "nc", "-z", "localhost", "8000" ]

# Using Node.js for HTTP check
healthcheck:
  test: [ "CMD", "node", "-e", "require('http').get('http://localhost:8000/', (res) => process.exit(res.statusCode === 200 ? 0 : 1)).on('error', () => process.exit(1))" ]

# Using Python for HTTP check  
healthcheck:
  test: [ "CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/'); exit(0)" ]
```

## Verification Script

Create `scripts/verify_health_checks.sh`:

```bash
#!/bin/bash
echo "🔍 Verifying health check implementations..."

services=("n8n_auto" "controller_auto" "eko_service_auto" "openrouter_proxy_auto")

for service in "${services[@]}"; do
    echo "Testing $service..."
    
    # Get health check command from Docker
    health_cmd=$(docker inspect $service | jq -r '.[0].Config.Healthcheck.Test | join(" ")')
    echo "Health check: $health_cmd"
    
    # Check if container is healthy
    status=$(docker compose ps $service | grep -E "(healthy|unhealthy)" | awk '{print $4}')
    echo "Status: $status"
    
    if [[ "$status" == *"healthy"* ]]; then
        echo "✅ $service is healthy"
    else
        echo "❌ $service is unhealthy"
        echo "Recent logs:"
        docker compose logs $service --tail=5
    fi
    echo "---"
done

echo "🎉 Health check verification complete"
```

## Expected Results

After implementing these fixes:

```bash
$ docker compose ps
NAME                    STATUS
controller_auto         Up X minutes (healthy)
eko_service_auto        Up X minutes (healthy)
n8n_auto                Up X minutes (healthy)  
openrouter_proxy_auto   Up X minutes (healthy)
# ... other services
```

```bash
$ ./monitor_services.sh | grep "Service Health Checks" -A 10
=== Service Health Checks ===
✓ n8n_direct: HEALTHY
✓ openrouter_proxy: HEALTHY
✓ controller: HEALTHY
✓ eko_service: HEALTHY
# ... other services

Health Summary: X/X services healthy
✅ All services are operational
```

---

*This implementation guide addresses the actual root cause of health check failures: missing tools in containers rather than missing endpoints.*
