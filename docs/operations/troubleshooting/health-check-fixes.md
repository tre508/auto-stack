# 🏥 Health Check Fixes

## Current Issues Identified

Based on the monitoring results, we have several services showing as "unhealthy":

- `controller_auto` - Responding to `/status` but health check failing
- `n8n_auto` - Missing `/healthz` endpoint
- `openrouter_proxy_auto` - Missing `/healthz` endpoint  
- `eko_service_auto` - Missing `/health` endpoint

## Immediate Fixes

### 1. Fix Eko Service Health Endpoint

**Problem:** Eko service is missing the `/health` endpoint that the health check is trying to access.

**Current Status:**

```bash
# This fails:
curl -f http://localhost:3001/health
# Returns: curl: (7) Failed to connect to localhost port 3001: Connection refused
```

**Solution:** Add health endpoint to `controller/eko_service.js`:

```javascript
// Add this to eko_service.js
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

### 2. Fix OpenRouter Proxy Health Endpoint

**Problem:** OpenRouter proxy is missing the `/healthz` endpoint.

**Current Status:**

```bash
# This works:
curl -f http://localhost:8001/  # Returns: OK

# This fails:
curl -f http://localhost:8001/healthz
```

**Solution:** Add health endpoint to `openrouter_proxy/server.js`:

```javascript
// Add this to server.js
app.get('/healthz', (req, res) => {
    res.status(200).json({ 
        status: 'healthy',
        service: 'openrouter_proxy',
        timestamp: new Date().toISOString(),
        uptime: process.uptime()
    });
});

app.get('/health', (req, res) => {
    res.status(200).json({ 
        status: 'healthy',
        service: 'openrouter_proxy',
        timestamp: new Date().toISOString(),
        uptime: process.uptime()
    });
});
```

### 3. Fix n8n Health Check

**Problem:** n8n health check is looking for `/healthz` but n8n might use a different endpoint.

**Current Status:**

```bash
# Check what n8n actually provides:
curl -f http://localhost:5678/healthz  # Fails
curl -f http://localhost:5678/health   # Check if this works
curl -f http://localhost:5678/         # This should work
```

**Solution:** Update docker-compose.yml health check for n8n:

```yaml
# Change from:
healthcheck:
  test: [ "CMD", "curl", "-f", "http://localhost:5678/healthz" ]

# To:
healthcheck:
  test: [ "CMD", "curl", "-f", "http://localhost:5678/" ]
  interval: 30s
  timeout: 30s
  retries: 5
  start_period: 120s
```

### 4. Fix Controller Health Check

**Problem:** Controller responds to `/status` but health check might be timing out.

**Current Status:**

```bash
# This works:
curl -f http://localhost:5050/status
# Returns: {"status":"Controller is running"}
```

**Solution:** Increase health check timeout in docker-compose.yml:

```yaml
# Update controller health check:
healthcheck:
  test: [ "CMD", "curl", "-f", "http://localhost:5050/status" ]
  interval: 30s
  timeout: 30s  # Increased from 10s
  retries: 5    # Increased from 3
  start_period: 60s  # Increased from 40s
```

## Implementation Steps

### Step 1: Update Service Files

```bash
# 1. Update Eko Service
# Edit controller/eko_service.js and add health endpoints

# 2. Update OpenRouter Proxy  
# Edit openrouter_proxy/server.js and add health endpoints

# 3. Update docker-compose.yml
# Fix health check configurations
```

### Step 2: Rebuild Affected Services

```bash
# Rebuild only the services that need updates
docker compose build eko_service_auto openrouter_proxy_auto

# Restart services with new health checks
docker compose up -d eko_service_auto openrouter_proxy_auto

# Update docker-compose.yml and restart n8n and controller
docker compose up -d n8n_auto controller_auto
```

### Step 3: Verify Fixes

```bash
# Wait for services to start
sleep 60

# Check health endpoints directly
curl -f http://localhost:3001/health    # eko_service
curl -f http://localhost:8001/healthz   # openrouter_proxy
curl -f http://localhost:5678/          # n8n
curl -f http://localhost:5050/status    # controller

# Check Docker health status
docker compose ps

# Run full monitoring
./monitor_services.sh
```

## Expected Results

After implementing these fixes:

```bash
# All services should show as healthy:
NAME                    STATUS
controller_auto         Up X minutes (healthy)
eko_service_auto        Up X minutes (healthy)  
n8n_auto                Up X minutes (healthy)
openrouter_proxy_auto   Up X minutes (healthy)
```

## Verification Commands

```bash
# Test all health endpoints
echo "Testing health endpoints..."
curl -s http://localhost:3001/health | jq .status
curl -s http://localhost:8001/healthz | jq .status  
curl -s http://localhost:5678/ | head -1
curl -s http://localhost:5050/status | jq .status

# Check Docker health status
docker compose ps | grep -E "(healthy|unhealthy)"

# Full system health check
./monitor_services.sh | grep -A 20 "Service Health Checks"
```

## Rollback Plan

If issues occur:

```bash
# Stop affected services
docker compose stop eko_service_auto openrouter_proxy_auto n8n_auto controller_auto

# Revert changes to service files
git checkout HEAD -- controller/eko_service.js openrouter_proxy/server.js docker-compose.yml

# Restart services
docker compose up -d eko_service_auto openrouter_proxy_auto n8n_auto controller_auto
```

---

*This guide addresses the specific health check failures identified in the current auto-stack deployment.*
