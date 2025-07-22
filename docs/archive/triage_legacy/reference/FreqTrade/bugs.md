# 🐛 Known Issues & Solutions

## Environment Issues

### 1. Docker Network Connectivity

**Issue:** Services unable to communicate within Docker network.

**Solution:**

1. Verify network configuration:

   ```bash
   docker network ls
   docker network inspect auto-stack-net
   ```

2. Ensure services are on the same network:

   ```bash
   docker compose ps
   docker network connect auto-stack-net <container_name>
   ```

3. Check container DNS:

   ```bash
   docker exec freqtrade ping controller
   docker exec freqtrade ping mem0
   ```

### 2. Database Connection

**Issue:** Freqtrade fails to connect to PostgreSQL.

**Solution:**

1. Verify database configuration:

   ```bash
   psql $DB_URL -c "\l"
   ```

2. Check database logs:

   ```bash
   docker logs timescaledb
   ```

3. Reset database connection:

   ```bash
   docker compose restart timescaledb
   docker compose restart freqtrade
   ```

## API Integration

### 1. Controller Communication

**Issue:** HTTP 401/403 errors when accessing Controller API.

**Solution:**

1. Check JWT token:

   ```bash
   # Generate new token
   curl -X POST http://controller:3000/api/auth/token \
        -H "Content-Type: application/json" \
        -d '{"username":"freqtrade","password":"your_password"}'
   ```

2. Verify environment variables:

   ```bash
   docker exec freqtrade env | grep CONTROLLER
   ```

3. Test API connection:

   ```bash
   curl -H "Authorization: Bearer $TOKEN" \
        http://controller:3000/api/v1/status
   ```

### 2. Memory Service Integration

**Issue:** Failed to store or retrieve trading data.

**Solution:**

1. Check Mem0 service:

   ```bash
   curl http://mem0:8080/health
   ```

2. Verify vector store:

   ```bash
   curl http://qdrant:6333/collections
   ```

3. Test memory operations:

   ```bash
   # Store test data
   curl -X POST http://mem0:8080/memory \
        -H "Content-Type: application/json" \
        -d '{"messages":[{"role":"system","content":"test"}]}'
   
   # Query data
   curl http://mem0:8080/search?query=test
   ```

## Strategy Execution

### 1. Backtesting Errors

**Issue:** Backtesting fails with data loading errors.

**Solution:**

1. Check data directory:

   ```bash
   ls -l /freqtrade/user_data/data/
   ```

2. Download fresh data:

   ```bash
   freqtrade download-data --exchange binance --pairs BTC/USDT ETH/USDT
   ```

3. Verify data format:

   ```bash
   head -n 5 /freqtrade/user_data/data/*.json
   ```

### 2. Strategy Loading

**Issue:** Strategy not found or import errors.

**Solution:**

1. Check strategy location:

   ```bash
   ls -l /freqtrade/user_data/strategies/
   ```

2. Verify Python path:

   ```bash
   python -c "import sys; print(sys.path)"
   ```

3. Test strategy import:

   ```bash
   freqtrade test-pairlist -c config.json --strategy MyStrategy
   ```

## Performance Issues

### 1. Memory Usage

**Issue:** High memory consumption during backtesting.

**Solution:**

1. Monitor resources:

   ```bash
   docker stats freqtrade
   ```

2. Adjust batch size:

   ```json
   {
       "max_open_trades": 3,
       "batch_size": 10,
       "memory_size": "2G"
   }
   ```

3. Clean cache:

   ```bash
   rm -rf /freqtrade/user_data/cache/*
   ```

### 2. Database Performance

**Issue:** Slow database operations.

**Solution:**

1. Check database size:

   ```bash
   psql $DB_URL -c "SELECT pg_size_pretty(pg_database_size('freqtrade'));"
   ```

2. Optimize tables:

   ```sql
   VACUUM ANALYZE trades;
   VACUUM ANALYZE orders;
   ```

3. Monitor queries:

   ```sql
   SELECT * FROM pg_stat_activity WHERE datname = 'freqtrade';
   ```

## Logging & Monitoring

### 1. Log Management

**Issue:** Log files growing too large.

**Solution:**

1. Configure log rotation:

   ```json
   {
       "logfile": "/freqtrade/user_data/logs/freqtrade.log",
       "logformat": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
       "log_level": "INFO"
   }
   ```

2. Clean old logs:

   ```bash
   find /freqtrade/user_data/logs/ -name "*.log" -mtime +7 -delete
   ```

3. Monitor log size:

   ```bash
   du -h /freqtrade/user_data/logs/
   ```

### 2. Alert Configuration

**Issue:** Missing critical alerts.

**Solution:**

1. Check notification settings:

   ```json
   {
       "telegram": {
           "enabled": true,
           "token": "your_token",
           "chat_id": "your_chat_id"
       },
       "discord": {
           "enabled": true,
           "webhook_url": "your_webhook_url"
       }
   }
   ```

2. Test notifications:

   ```bash
   # Telegram
   curl -X POST https://api.telegram.org/bot$TOKEN/sendMessage \
        -d "chat_id=$CHAT_ID&text=Test"
   
   # Discord
   curl -X POST $DISCORD_WEBHOOK_URL \
        -H "Content-Type: application/json" \
        -d '{"content":"Test"}'
   ```

## Additional Resources

- [Freqtrade Troubleshooting](https://www.freqtrade.io/en/stable/troubleshooting/)
- [Docker Documentation](https://docs.docker.com/config/daemon/troubleshoot/)
- [PostgreSQL Tuning](https://wiki.postgresql.org/wiki/Tuning_Your_PostgreSQL_Server)

# Known Integration Issues

## 🧠 Mem0 Search Fails

- BGE-small uses 768-dim embeddings
- Mem0 requests 1536-dim vectors
- Fix: Unify dimensionality between generator and vector store

## 🐍 TA-Lib Build Failure (Dev Env Only)

- `ta-lib` Python wheel fails to build on some machines
- Freqtrade binary includes it — no runtime impact
- Fix: Install system headers, or ignore in dev environment
