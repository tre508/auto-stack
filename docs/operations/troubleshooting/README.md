# 🔧 Auto-Stack Troubleshooting Guide

## 📋 Quick Reference

### Emergency Commands

```bash
# Stop all services
docker compose down --remove-orphans

# Full system reset
docker compose down --remove-orphans --volumes
docker system prune -f --volumes
docker compose up --build -d

# Check service status
docker compose ps
./monitor_services.sh

# View logs for specific service
docker compose logs <service_name> --tail=20 -f
```

### Health Check Status

- ✅ **Healthy**: Service is fully operational
- ⚠️ **Unhealthy**: Service is running but health checks are failing
- ❌ **Exited**: Service has stopped or crashed
- 🔄 **Starting**: Service is in startup phase

---

## 🚨 Common Issues & Solutions

### 1. Health Check Failures

#### Problem: Services show as "unhealthy" despite running

**Symptoms:**

- `docker compose ps` shows "(unhealthy)" status
- Services appear to be running but health checks fail
- Monitor script shows mixed health results

**Root Causes & Solutions:**

##### A. Health Check Endpoint Missing

```bash
# Check if health endpoint exists
curl -f http://localhost:5678/healthz  # n8n
curl -f http://localhost:8000/healthz  # openrouter_proxy
curl -f http://localhost:3001/health   # eko_service
```

**Solution:** Add missing health endpoints to services:

```javascript
// For Node.js services (eko_service.js, openrouter_proxy)
app.get('/health', (req, res) => {
    res.status(200).json({ status: 'healthy', timestamp: new Date().toISOString() });
});

app.get('/healthz', (req, res) => {
    res.status(200).json({ status: 'healthy', timestamp: new Date().toISOString() });
});
```

##### B. Health Check Timeout Issues

**Current Config:**

```yaml
healthcheck:
  test: [ "CMD", "curl", "-f", "http://localhost:5678/healthz" ]
  interval: 30s
  timeout: 15s
  retries: 3
  start_period: 60s
```

**Solution:** Increase timeout and start_period:

```yaml
healthcheck:
  test: [ "CMD", "curl", "-f", "http://localhost:5678/healthz" ]
  interval: 30s
  timeout: 30s
  retries: 5
  start_period: 120s
```

### 2. PostgreSQL Connection Issues

#### Problem: "role 'postgres' does not exist"

**Symptoms:**

```
FATAL: role "postgres" does not exist
```

**Root Cause:** PostgreSQL container not properly initialized with user credentials

**Solution:**

```bash
# 1. Stop PostgreSQL container
docker compose stop postgres_logging_auto

# 2. Remove PostgreSQL volume (WARNING: This deletes data)
docker volume rm freq-chat_postgres_data || true
sudo rm -rf /storage/docker-volumes/pg_logs_data/*

# 3. Recreate with proper environment variables
docker compose up postgres_logging_auto -d

# 4. Verify connection
docker compose exec postgres_logging_auto psql -U autostack_logger -d autostack_logs -c "SELECT version();"
```

**Environment Variables Check:**

```bash
# Verify these are set in .env
grep -E "POSTGRES_LOGGING_" .env
```

### 3. Service Startup Sequence Issues

#### Problem: Services fail due to dependency not ready

**Symptoms:**

- Services exit with connection errors
- Intermittent startup failures
- Health checks pass but services can't connect

**Solution: Implement Proper Wait Strategies**

##### A. Add wait-for-it script

```bash
# Download wait-for-it.sh
curl -o wait-for-it.sh https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh
chmod +x wait-for-it.sh
```

##### B. Update Dockerfile with wait logic

```dockerfile
# Example for controller service
FROM python:3.11-slim
COPY wait-for-it.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/wait-for-it.sh

# Update CMD to wait for dependencies
CMD ["wait-for-it.sh", "postgres_logging_auto:5432", "--", "wait-for-it.sh", "mem0_auto:8000", "--", "uvicorn", "controller:app", "--host", "0.0.0.0", "--port", "5050"]
```

### 4. Network Connectivity Issues

#### Problem: Services can't communicate internally

**Symptoms:**

- "Connection refused" errors in logs
- Services can't reach each other
- External access works but internal doesn't

**Diagnosis:**

```bash
# Check network exists
docker network ls | grep auto-stack-net

# Inspect network configuration
docker network inspect auto-stack-net

# Test connectivity between containers
docker compose exec controller_auto ping mem0_auto
docker compose exec controller_auto curl -f http://mem0_auto:8000
```

**Solution:**

```bash
# Recreate network
docker network rm auto-stack-net
docker network create auto-stack-net
docker compose up -d
```

### 5. Resource Exhaustion

#### Problem: Services crash due to memory/CPU limits

**Symptoms:**

- Containers get killed (OOMKilled)
- High memory usage in monitor script
- Services become unresponsive

**Diagnosis:**

```bash
# Check resource usage
docker stats --no-stream
./monitor_services.sh

# Check for OOMKilled containers
docker compose ps -a | grep -E "(Exited|OOMKilled)"
```

**Solution: Adjust Resource Limits**

```yaml
# In docker-compose.yml
deploy:
  resources:
    limits:
      memory: 2G  # Increase from 1G
      cpus: '1.0'
    reservations:
      memory: 512M
```

### 6. Environment Variable Issues

#### Problem: Services fail due to missing/incorrect environment variables

**Symptoms:**

- Services start but don't function correctly
- Authentication failures
- Connection errors to external APIs

**Diagnosis:**

```bash
# Check environment variables in running container
docker compose exec controller_auto env | grep -E "(API|URL|KEY)"

# Verify .env files exist and are readable
ls -la .env */.*env
```

**Solution:**

```bash
# Validate all required environment variables
./scripts/validate_env.sh  # Create this script

# Template for validation script
#!/bin/bash
required_vars=(
    "OPENROUTER_API_KEY"
    "HF_TOKEN"
    "POSTGRES_LOGGING_USER"
    "POSTGRES_LOGGING_PASSWORD"
    "POSTGRES_LOGGING_DB"
)

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Missing required variable: $var"
        exit 1
    else
        echo "✅ $var is set"
    fi
done
```

---

## 🔍 Diagnostic Commands

### Service Health Checks

```bash
# Quick health overview
./monitor_services.sh

# Detailed service status
docker compose ps -a

# Check specific service logs
docker compose logs controller_auto --tail=50 -f
docker compose logs n8n_auto --tail=50 -f
docker compose logs postgres_logging_auto --tail=50 -f

# Test API endpoints
curl -s http://localhost:5050/status | jq .
curl -s http://localhost:8000/ | jq .
curl -s http://localhost:7861/health | jq .
```

### Network Diagnostics

```bash
# Check network connectivity
docker network inspect auto-stack-net

# Test internal service communication
docker compose exec controller_auto curl -f http://mem0_auto:8000/
docker compose exec controller_auto curl -f http://openrouter_proxy_auto:8000/healthz

# Check port bindings
netstat -tulpn | grep -E "(5050|5678|8000|8001|3001|6333|5432)"
```

### Resource Monitoring

```bash
# Real-time resource usage
docker stats

# Disk usage
df -h
docker system df

# Check Docker daemon logs
journalctl -u docker.service --tail=50
```

---

## 🛠️ Service-Specific Troubleshooting

### Controller Service

**Common Issues:**

- Health check failures despite responding to `/status`
- Memory service connection errors
- API authentication issues

**Debug Steps:**

```bash
# Check controller logs
docker compose logs controller_auto --tail=20

# Test controller endpoints
curl -X GET http://localhost:5050/status
curl -X GET http://localhost:5050/api/v1/health

# Check environment variables
docker compose exec controller_auto env | grep -E "(MEM0|OPENROUTER|HF_)"
```

### n8n Service

**Common Issues:**

- Webhook URL configuration
- Database connection problems
- License/authentication issues

**Debug Steps:**

```bash
# Check n8n logs
docker compose logs n8n_auto --tail=20

# Access n8n directly
curl -f http://localhost:5678/healthz

# Check n8n configuration
docker compose exec n8n_auto cat /home/node/.n8n/config
```

### PostgreSQL Service

**Common Issues:**

- User/role creation failures
- Volume mounting problems
- Connection authentication

**Debug Steps:**

```bash
# Check PostgreSQL logs
docker compose logs postgres_logging_auto --tail=20

# Connect to PostgreSQL
docker compose exec postgres_logging_auto psql -U autostack_logger -d autostack_logs

# Check database status
docker compose exec postgres_logging_auto pg_isready -U autostack_logger
```

### Mem0 Service

**Common Issues:**

- Qdrant connection failures
- Embedding service unavailable
- Configuration file issues

**Debug Steps:**

```bash
# Check mem0 logs
docker compose logs mem0_auto --tail=20

# Test mem0 endpoints
curl -X GET http://localhost:8000/
curl -X POST http://localhost:8000/v1/memories -H "Content-Type: application/json" -d '{"messages": [{"role": "user", "content": "test"}]}'

# Check mem0 configuration
docker compose exec mem0_auto cat /app/config.yaml
```

---

## 📊 Monitoring & Maintenance

### Daily Health Checks

```bash
# Morning health check routine
./monitor_services.sh
docker compose ps
docker system df

# Check for any crashed containers
docker compose ps -a | grep -v "Up"
```

### Weekly Maintenance

```bash
# Clean up unused resources
docker system prune -f

# Update service images
docker compose pull
docker compose up -d

# Backup critical data
./scripts/backup_data.sh
```

### Log Rotation

```bash
# Limit Docker log sizes
# Add to docker-compose.yml:
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

---

## 🚀 Performance Optimization

### Resource Tuning

```yaml
# Optimized resource allocation
deploy:
  resources:
    limits:
      memory: 2G
      cpus: '1.0'
    reservations:
      memory: 512M
      cpus: '0.25'
```

### Startup Optimization

```bash
# Staggered startup to reduce resource spikes
docker compose up -d postgres_logging_auto qdrant_auto
sleep 30
docker compose up -d mem0_auto bge_embedding_auto
sleep 30
docker compose up -d controller_auto n8n_auto
sleep 15
docker compose up -d freq_chat_auto openrouter_proxy_auto eko_service_auto traefik_auto
```

---

## 📞 Emergency Procedures

### Complete System Recovery

```bash
#!/bin/bash
# emergency_recovery.sh

echo "🚨 Starting emergency recovery..."

# Stop all services
docker compose down --remove-orphans

# Clean up resources
docker system prune -f --volumes

# Recreate network
docker network rm auto-stack-net 2>/dev/null || true
docker network create auto-stack-net

# Rebuild and restart
docker compose up --build -d

# Wait for services to start
sleep 60

# Run health check
./monitor_services.sh

echo "✅ Emergency recovery complete"
```

### Data Recovery

```bash
# Backup before recovery
sudo cp -r /home/gleshen/docker-volumes /backup/docker-volumes-$(date +%Y%m%d)
sudo cp -r /storage/docker-volumes /backup/storage-volumes-$(date +%Y%m%d)

# Restore from backup
sudo cp -r /backup/docker-volumes-YYYYMMDD/* /home/gleshen/docker-volumes/
sudo cp -r /backup/storage-volumes-YYYYMMDD/* /storage/docker-volumes/
```

---

## 📋 Troubleshooting Checklist

### Before Reporting Issues

- [ ] Checked service logs: `docker compose logs <service>`
- [ ] Verified environment variables are set
- [ ] Confirmed Docker daemon is running
- [ ] Checked available disk space: `df -h`
- [ ] Verified network connectivity between services
- [ ] Attempted service restart: `docker compose restart <service>`
- [ ] Checked for resource exhaustion: `docker stats`
- [ ] Reviewed recent changes to configuration files

### Information to Collect

- [ ] Output of `docker compose ps`
- [ ] Output of `./monitor_services.sh`
- [ ] Relevant service logs
- [ ] System resource usage
- [ ] Recent configuration changes
- [ ] Error messages and timestamps

---

## 🔗 Additional Resources

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Auto-Stack Architecture Guide](../architecture/services/README.md)
- [Service Configuration Reference](../setup/00_QuickStart.md)
- [Integration Patterns](../architecture/integrations/README.md)

---

*Last Updated: $(date)*
*Auto-Stack Version: 1.0*
