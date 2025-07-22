# Debugging and Diagnostic Prompts

This directory contains prompts and templates for troubleshooting issues across the Automation Stack services.

## Purpose

Debugging prompts provide structured approaches to:

- **Service Diagnostics**: Health checks and status verification
- **Integration Issues**: Cross-service communication problems
- **Performance Analysis**: Bottleneck identification and optimization
- **Error Investigation**: Root cause analysis and resolution
- **Log Analysis**: Centralized logging and pattern detection

## Service-Specific Debugging

### Controller Service
```bash
# Health check
curl -f http://controller_auto:5050/health

# Check logs for errors
docker logs controller_auto --tail 100 | grep -i error

# Verify Flask endpoints
curl -X GET http://controller_auto:5050/cmd/status

# Test async processing
curl -X POST http://controller_auto:5050/cmd/test \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
```

### n8n Service
```bash
# Health check
curl -f http://n8n_auto:5678/healthz

# Check workflow execution status
curl -X GET http://n8n_auto:5678/api/v1/executions

# Verify webhook endpoints
curl -X POST http://n8n_auto:5678/webhook/test

# Check for failed workflows
docker logs n8n_auto --tail 100 | grep -i "execution.*failed"
```

### Freqtrade Service
```bash
# API health check
curl -f http://freqtrade_devcontainer:8080/api/v1/ping

# Check bot status
curl -H "Authorization: Bearer <token>" \
  http://freqtrade_devcontainer:8080/api/v1/status

# Verify strategy loading
curl -H "Authorization: Bearer <token>" \
  http://freqtrade_devcontainer:8080/api/v1/strategies

# Check recent trades
curl -H "Authorization: Bearer <token>" \
  http://freqtrade_devcontainer:8080/api/v1/trades
```

### Mem0 Service
```bash
# Health check
curl -f http://mem0_auto:8000/health

# Test memory operations
curl -X POST http://mem0_auto:8000/v1/memories \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "test"}], "user_id": "debug"}'

# Check memory retrieval
curl -X GET http://mem0_auto:8000/v1/memories?user_id=debug
```

## Network Diagnostics

### Docker Network Connectivity
```bash
# Inspect network configuration
docker network inspect auto-stack-net

# Test inter-container connectivity
docker exec controller_auto ping -c 3 n8n_auto
docker exec n8n_auto ping -c 3 freqtrade_devcontainer
docker exec controller_auto ping -c 3 mem0_auto

# Check port accessibility
docker exec controller_auto nc -zv n8n_auto 5678
docker exec n8n_auto nc -zv freqtrade_devcontainer 8080
```

### External Connectivity
```bash
# Test internet connectivity from containers
docker exec controller_auto curl -I https://httpbin.org/get
docker exec n8n_auto curl -I https://api.github.com

# Verify DNS resolution
docker exec controller_auto nslookup github.com
docker exec n8n_auto nslookup api.openai.com
```

## Database Diagnostics

### PostgreSQL Health
```sql
-- Connect and check basic functionality
psql -h postgres -U automation_user -d automation_stack -c "\l"

-- Check table status
SELECT 
    schemaname,
    tablename,
    n_tup_ins as inserts,
    n_tup_upd as updates,
    n_tup_del as deletes
FROM pg_stat_user_tables;

-- Verify log table structure
\d agent_logs

-- Check recent log entries
SELECT agent, workflow, action, status, timestamp 
FROM agent_logs 
ORDER BY timestamp DESC 
LIMIT 20;
```

### Log Analysis Queries
```sql
-- Find errors by service
SELECT agent, COUNT(*) as error_count
FROM agent_logs 
WHERE status = 'error' 
  AND timestamp > NOW() - INTERVAL '24 hours'
GROUP BY agent;

-- Identify frequent failures
SELECT action, COUNT(*) as failure_count
FROM agent_logs 
WHERE status = 'error'
  AND timestamp > NOW() - INTERVAL '1 week'
GROUP BY action
ORDER BY failure_count DESC;

-- Performance analysis
SELECT 
    agent,
    AVG(EXTRACT(EPOCH FROM (timestamp - LAG(timestamp) OVER (PARTITION BY agent ORDER BY timestamp)))) as avg_interval_seconds
FROM agent_logs 
WHERE timestamp > NOW() - INTERVAL '1 hour'
GROUP BY agent;
```

## Performance Diagnostics

### Container Resource Usage
```bash
# Check CPU and memory usage
docker stats --no-stream

# Detailed resource analysis
docker exec controller_auto top -bn1
docker exec n8n_auto ps aux

# Disk usage
docker exec controller_auto df -h
docker system df
```

### API Response Times
```bash
# Measure endpoint response times
time curl -s http://controller_auto:5050/health
time curl -s http://n8n_auto:5678/healthz
time curl -s http://freqtrade_devcontainer:8080/api/v1/ping

# Load testing with curl
for i in {1..10}; do
  time curl -s http://controller_auto:5050/cmd/status > /dev/null
done
```

## Common Issues and Solutions

### Issue: Service Unreachable
**Symptoms**: Connection refused, timeouts
**Diagnosis**:
```bash
# Check if container is running
docker ps | grep service_name

# Check container logs
docker logs service_name --tail 50

# Verify network connectivity
docker exec source_container ping target_container
```

**Solutions**:
- Restart failed containers
- Check Docker network configuration
- Verify service ports and bindings

### Issue: Authentication Failures
**Symptoms**: 401/403 errors, token invalid
**Diagnosis**:
```bash
# Check token generation
curl -u username:password -X POST http://service/api/v1/token/login

# Verify token format and expiration
echo "token" | base64 -d

# Check authentication logs
docker logs service_name | grep -i auth
```

**Solutions**:
- Regenerate authentication tokens
- Verify credentials in environment variables
- Check token expiration and refresh logic

### Issue: Workflow Execution Failures
**Symptoms**: n8n workflows failing, timeouts
**Diagnosis**:
```bash
# Check n8n execution logs
curl -X GET http://n8n_auto:5678/api/v1/executions?limit=10

# Check for resource constraints
docker exec n8n_auto ps aux | grep node

# Verify webhook endpoints
curl -X POST http://n8n_auto:5678/webhook/test -d '{"test": "data"}'
```

**Solutions**:
- Increase container resource limits
- Optimize workflow logic
- Add error handling nodes
- Check external API availability

### Issue: Memory/Storage Issues
**Symptoms**: Container crashes, disk full errors
**Diagnosis**:
```bash
# Check disk usage
docker system df
df -h

# Check memory usage
docker stats --no-stream
free -h

# Check for memory leaks
docker exec service_name ps aux --sort=-%mem | head
```

**Solutions**:
- Clean up unused Docker images/containers
- Implement log rotation
- Increase allocated resources
- Optimize memory usage in applications

## Automated Diagnostics

### Health Check Script
```bash
#!/bin/bash
# comprehensive-health-check.sh

echo "=== Automation Stack Health Check ==="

# Service availability
services=("controller_auto:5050" "n8n_auto:5678" "freqtrade_devcontainer:8080" "mem0_auto:8000")
for service in "${services[@]}"; do
    if curl -f -s "http://$service/health" > /dev/null 2>&1; then
        echo "✅ $service: HEALTHY"
    else
        echo "❌ $service: UNHEALTHY"
    fi
done

# Database connectivity
if psql -h postgres -U automation_user -d automation_stack -c "\q" > /dev/null 2>&1; then
    echo "✅ PostgreSQL: CONNECTED"
else
    echo "❌ PostgreSQL: CONNECTION FAILED"
fi

# Network connectivity
if docker exec controller_auto ping -c 1 n8n_auto > /dev/null 2>&1; then
    echo "✅ Network: CONNECTIVITY OK"
else
    echo "❌ Network: CONNECTIVITY ISSUES"
fi

echo "=== Health Check Complete ==="
```

### Log Analysis Script
```bash
#!/bin/bash
# analyze-recent-errors.sh

echo "=== Recent Error Analysis ==="

# Check for errors in last hour
psql -h postgres -U automation_user -d automation_stack -c "
SELECT 
    agent,
    action,
    error,
    timestamp
FROM agent_logs 
WHERE status = 'error' 
  AND timestamp > NOW() - INTERVAL '1 hour'
ORDER BY timestamp DESC;
"

# Check container logs for errors
for container in controller_auto n8n_auto freqtrade_devcontainer mem0_auto; do
    echo "--- $container recent errors ---"
    docker logs "$container" --since 1h 2>&1 | grep -i error | tail -5
done
```

## Maintenance and Monitoring

### Proactive Monitoring
- Set up health check alerts for all services
- Monitor disk usage and set cleanup policies
- Track API response times and set thresholds
- Implement log rotation and archival
- Monitor database performance and query times

### Regular Maintenance Tasks
```bash
# Weekly cleanup
docker system prune -f
docker volume prune -f

# Log table maintenance
psql -h postgres -U automation_user -d automation_stack -c "
DELETE FROM agent_logs 
WHERE timestamp < NOW() - INTERVAL '30 days';
"

# Backup important data
docker exec postgres pg_dump -U automation_user automation_stack > backup_$(date +%Y%m%d).sql
```

### Performance Optimization
- Regularly review slow queries and optimize
- Monitor memory usage patterns and adjust limits
- Profile API endpoints and optimize bottlenecks
- Review and optimize n8n workflow efficiency
- Implement caching where appropriate

## Escalation Procedures

### Critical Issues
1. **Service completely down**: Immediate restart, check logs, notify team
2. **Data corruption**: Stop services, restore from backup, investigate cause
3. **Security breach**: Isolate affected services, rotate credentials, audit logs

### Investigation Process
1. **Reproduce**: Document steps to reproduce the issue
2. **Isolate**: Identify which service/component is affected
3. **Analyze**: Check logs, metrics, and system state
4. **Fix**: Apply appropriate solution based on analysis
5. **Verify**: Confirm issue is resolved and monitor for recurrence
6. **Document**: Update debugging guides with new findings
