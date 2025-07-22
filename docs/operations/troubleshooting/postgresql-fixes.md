# 🐘 PostgreSQL Troubleshooting

## Current Issue: "role 'postgres' does not exist"

**Problem:** PostgreSQL container is failing with authentication errors:

```
FATAL: role "postgres" does not exist
```

**Root Cause:** The PostgreSQL container is not properly initialized with the correct user credentials from the environment variables.

## Diagnosis

### Check Current Status

```bash
# Check PostgreSQL logs
docker compose logs postgres_logging_auto --tail=20

# Check if container is running
docker compose ps postgres_logging_auto

# Check environment variables
docker compose exec postgres_logging_auto env | grep POSTGRES
```

### Expected vs Actual Configuration

**Expected Configuration (from .env):**

```bash
POSTGRES_LOGGING_USER=autostack_logger
POSTGRES_LOGGING_PASSWORD=yoursecurepassword_logger  
POSTGRES_LOGGING_DB=autostack_logs
```

**Health Check Issue:**

```bash
# Current health check fails:
docker compose exec postgres_logging_auto pg_isready -U postgres

# Should use correct user:
docker compose exec postgres_logging_auto pg_isready -U autostack_logger
```

## Solution 1: Fix Health Check Configuration

**Problem:** Health check is using wrong username.

**Current docker-compose.yml:**

```yaml
healthcheck:
  test: [ "CMD-SHELL", "pg_isready -U postgres" ]
```

**Fix:** Update to use correct username:

```yaml
healthcheck:
  test: [ "CMD-SHELL", "pg_isready -U ${POSTGRES_LOGGING_USER:-autostack_logger}" ]
  interval: 30s
  timeout: 10s
  retries: 5
  start_period: 60s
```

## Solution 2: Reinitialize PostgreSQL Container

### Step 1: Stop and Clean PostgreSQL

```bash
# Stop PostgreSQL container
docker compose stop postgres_logging_auto

# Remove container (keeps volume data)
docker compose rm -f postgres_logging_auto

# Optional: Remove volume data (WARNING: This deletes all data)
sudo rm -rf /storage/docker-volumes/pg_logs_data/*
```

### Step 2: Verify Environment Variables

```bash
# Check that these variables are set in .env
grep -E "POSTGRES_LOGGING_" .env

# Should show:
# POSTGRES_LOGGING_USER=autostack_logger
# POSTGRES_LOGGING_PASSWORD=yoursecurepassword_logger
# POSTGRES_LOGGING_DB=autostack_logs
```

### Step 3: Update docker-compose.yml

Add explicit environment mapping:

```yaml
postgres_logging_auto:
  image: postgres:15
  container_name: postgres_logging_auto
  restart: unless-stopped
  environment:
    - POSTGRES_USER=${POSTGRES_LOGGING_USER}
    - POSTGRES_PASSWORD=${POSTGRES_LOGGING_PASSWORD}
    - POSTGRES_DB=${POSTGRES_LOGGING_DB}
    - PGDATA=/var/lib/postgresql/data/pgdata
  env_file:
    - ./.env
  healthcheck:
    test: [ "CMD-SHELL", "pg_isready -U ${POSTGRES_LOGGING_USER:-autostack_logger} -d ${POSTGRES_LOGGING_DB:-autostack_logs}" ]
    interval: 30s
    timeout: 10s
    retries: 5
    start_period: 60s
```

### Step 4: Recreate Container

```bash
# Recreate PostgreSQL container with correct configuration
docker compose up -d postgres_logging_auto

# Wait for initialization
sleep 30

# Check logs for successful startup
docker compose logs postgres_logging_auto --tail=10
```

### Step 5: Verify Connection

```bash
# Test connection with correct credentials
docker compose exec postgres_logging_auto psql -U autostack_logger -d autostack_logs -c "SELECT version();"

# Check health status
docker compose exec postgres_logging_auto pg_isready -U autostack_logger -d autostack_logs

# Verify container health
docker compose ps postgres_logging_auto
```

## Solution 3: Alternative Health Check

If the above doesn't work, use a more robust health check:

```yaml
healthcheck:
  test: [ "CMD-SHELL", "pg_isready -h localhost -p 5432 -U ${POSTGRES_LOGGING_USER:-autostack_logger} -d ${POSTGRES_LOGGING_DB:-autostack_logs}" ]
  interval: 30s
  timeout: 15s
  retries: 5
  start_period: 90s
```

## Verification Steps

### 1. Check Container Status

```bash
# Should show (healthy) status
docker compose ps postgres_logging_auto
```

### 2. Test Database Connection

```bash
# Connect to database
docker compose exec postgres_logging_auto psql -U autostack_logger -d autostack_logs

# Inside psql:
\l                    # List databases
\du                   # List users
SELECT version();     # Check PostgreSQL version
\q                    # Quit
```

### 3. Test from Other Services

```bash
# Test connection from freq-chat service
docker compose exec freq_chat_auto psql -h postgres_logging_auto -U autostack_logger -d autostack_logs -c "SELECT 1;"
```

### 4. Monitor Health

```bash
# Run monitoring script
./monitor_services.sh | grep -A 5 "postgres"

# Should show:
# ✓ postgres: HEALTHY
```

## Troubleshooting Persistent Issues

### Issue: Container Keeps Failing

```bash
# Check detailed logs
docker compose logs postgres_logging_auto --tail=50

# Check volume permissions
ls -la /storage/docker-volumes/pg_logs_data/

# Fix permissions if needed
sudo chown -R 999:999 /storage/docker-volumes/pg_logs_data/
```

### Issue: Database Not Created

```bash
# Check if database exists
docker compose exec postgres_logging_auto psql -U autostack_logger -l

# Create database if missing
docker compose exec postgres_logging_auto createdb -U autostack_logger autostack_logs
```

### Issue: Environment Variables Not Loading

```bash
# Debug environment variable loading
docker compose config | grep -A 10 postgres_logging_auto

# Check if .env file is readable
ls -la .env
cat .env | grep POSTGRES_LOGGING_
```

## Complete Recovery Script

Create `scripts/fix_postgresql.sh`:

```bash
#!/bin/bash
echo "🔧 Fixing PostgreSQL configuration..."

# Stop PostgreSQL
docker compose stop postgres_logging_auto

# Remove container (keeps data)
docker compose rm -f postgres_logging_auto

# Verify environment variables
echo "Checking environment variables..."
if [ -z "$POSTGRES_LOGGING_USER" ]; then
    echo "❌ POSTGRES_LOGGING_USER not set"
    exit 1
fi

echo "✅ Environment variables verified"

# Update docker-compose.yml health check
echo "Updating health check configuration..."

# Recreate container
docker compose up -d postgres_logging_auto

# Wait for startup
echo "Waiting for PostgreSQL to start..."
sleep 60

# Test connection
echo "Testing connection..."
docker compose exec postgres_logging_auto pg_isready -U autostack_logger -d autostack_logs

if [ $? -eq 0 ]; then
    echo "✅ PostgreSQL is healthy"
else
    echo "❌ PostgreSQL connection failed"
    docker compose logs postgres_logging_auto --tail=20
    exit 1
fi

echo "🎉 PostgreSQL fix complete"
```

## Prevention

### 1. Environment Variable Validation

Add to startup scripts:

```bash
# Validate required PostgreSQL variables
required_pg_vars=(
    "POSTGRES_LOGGING_USER"
    "POSTGRES_LOGGING_PASSWORD"
    "POSTGRES_LOGGING_DB"
)

for var in "${required_pg_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Missing PostgreSQL variable: $var"
        exit 1
    fi
done
```

### 2. Health Check Monitoring

```bash
# Add to daily monitoring
if ! docker compose exec postgres_logging_auto pg_isready -U autostack_logger; then
    echo "⚠️ PostgreSQL health check failed"
    # Send alert or restart service
fi
```

---

*This guide specifically addresses the "role 'postgres' does not exist" error in the auto-stack PostgreSQL deployment.*
