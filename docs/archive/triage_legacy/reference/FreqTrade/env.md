# 🔧 Freqtrade Environment Configuration

## System Requirements

- Ubuntu Native Host (20.04 LTS or newer)
- Docker Engine 24.0+
- Docker Compose 2.20+
- VS Code with Dev Containers extension
- Git 2.34+
- 8GB RAM minimum (16GB recommended)
- 50GB free disk space

## Environment Variables

Create a `.env` file in your Freqtrade project root with the following structure:

```bash
# Core Configuration
FREQTRADE_MODE=live  # Options: live, dry
EXCHANGE=kraken      # Options: binance, kraken, kucoin
STAKE_CURRENCY=USDT  # Trading currency
MAX_OPEN_TRADES=3    # Maximum concurrent trades

# API Configuration
EXCHANGE_KEY=your_exchange_key
EXCHANGE_SECRET=your_exchange_secret
TELEGRAM_TOKEN=your_telegram_token  # Optional
TELEGRAM_CHAT_ID=your_chat_id      # Optional

# Integration Points
CONTROLLER_URL=http://controller:3000
MEM0_URL=http://mem0:8080
N8N_WEBHOOK_URL=http://n8n:5678/webhook/freqtrade

# Database Configuration
DB_URL=postgresql://freqtrade:freqtrade@timescaledb:5432/freqtrade
QDRANT_URL=http://qdrant:6333

# Logging & Monitoring
LOG_LEVEL=info  # Options: debug, info, warning, error
ENABLE_METRICS=true
```

## Docker Configuration

The Dev Container configuration is defined in `.devcontainer/devcontainer.json`:

```json
{
  "name": "Freqtrade Development",
  "dockerComposeFile": [
    "../docker-compose.yml"
  ],
  "service": "freqtrade",
  "workspaceFolder": "/freqtrade",
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python",
        "ms-python.vscode-pylance"
      ]
    }
  },
  "remoteUser": "freqtrade"
}
```

## Network Configuration

Ensure your `docker-compose.yml` includes the following network configuration:

```yaml
services:
  freqtrade:
    networks:
      - auto-stack-net
      - default

networks:
  auto-stack-net:
    external: true
  default:
    driver: bridge
```

## Directory Structure

```
freqtrade/
├── .env                    # Environment variables
├── docker-compose.yml      # Docker configuration
├── user_data/
│   ├── config.json        # Trading configuration
│   ├── strategies/        # Trading strategies
│   └── hyperopts/         # Hyperopt configurations
└── .devcontainer/
    └── devcontainer.json  # Dev Container settings
```

## Configuration Files

### 1. Trading Configuration (`user_data/config.json`)

```json
{{
    "$schema": "https://schema.freqtrade.io/schema.json",
    "bot_name": "KrakenFreqAI_auto_stack",
    "strategy": "KrakenFreqAI_auto_stack",
    "stake_currency": "BTC",
    "stake_amount": 0.001,
    "max_open_trades": 5,
    "tradable_balance_ratio": 0.99,
    "dry_run": true,
    "dry_run_wallet": 0.0015,
    "cancel_open_orders_on_exit": false,
    "trading_mode": "spot",
    "unfilledtimeout": {
        "entry": 5,
        "exit": 5,
        "exit_timeout_count": 0,
        "unit": "minutes"
    },
    "entry_pricing": {
        "use_order_book": false,
        "order_book_top": 1
    },
    "exit_pricing": {
        "use_order_book": false,
        "order_book_top": 1
    },
    "exchange": {
        "name": "kraken",
        "key": "${KRAKEN_API_KEY}",
        "secret": "${KRAKEN_API_SECRET}",
        "ccxt_config": {
            "enableRateLimit": true
        },
        "ccxt_async_config": {
            "enableRateLimit": true,
            "rateLimit": 3100
        },
        "pair_whitelist": [
            "ADA/BTC",
            "XRP/BTC",
            "DOT/BTC",
            "LINK/BTC",
            "XLM/BTC",
            "ALGO/BTC",
            "UNI/BTC",
            "SOL/BTC"
        ]
    },
    "pairlists": [
        {
            "method": "StaticPairList"
        }
    ],
    "api_server": {
        "enabled": true,
        "listen_ip_address": "0.0.0.0",
        "listen_port": 8080,
        "verbosity": "error",
        "enable_openapi": true,
        "jwt_secret_key": "${API_JWT_SECRET:-your_jwt_secret_fallback}",
        "ws_token": "${API_WS_TOKEN:-your_ws_token_fallback}",
        "CORS_origins": [],
        "username": "${FREQTRADE_API_USERNAME:-your_api_user}",
        "password": "${FREQTRADE_API_PASSWORD:-a_very_secure_password}"
    },
    "freqai": {
        "enabled": true,
        "identifier": "KrakenFreqAI_auto_stack",
        "train_period_days": 30,
        "backtest_period_days": 7,
        "live_retrain_hours": 6,
        "feature_parameters": {
            "include_timeframes": [
                "5m",
                "15m",
                "1h"
            ],
            "indicator_periods_candles": [
                10,
                20,
                50
            ],
            "label_period_candles": 24,
            "include_corr_pairlist": [
                "ADA/BTC",
                "XRP/BTC",
                "DOT/BTC",
                "LINK/BTC",
                "XLM/BTC",
                "ALGO/BTC",
                "UNI/BTC",
                "SOL/BTC"
            ]
        },
        "data_split_parameters": {
            "test_size": 0.2
        },
        "model_training_parameters": {}
    },
    "logger": {
        "loglevel": "info",
        "logfile": "user_data/logs/freqtrade.log"
    },
    "internals": {
        "process_throttle_secs": 5
    }
}
```

### 2. Strategy Configuration

Place your strategy files in `user_data/strategies/`. Example structure:

```python
from freqtrade.strategy import IStrategy, DecimalParameter
from pandas import DataFrame

class MyAwesomeStrategy(IStrategy):
    minimal_roi = {
        "0": 0.10
    }
    stoploss = -0.05
    timeframe = '5m'
    
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Your indicator logic here
        return dataframe
    
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Your entry logic here
        return dataframe
    
    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Your exit logic here
        return dataframe
```

## Integration Verification

Run these commands inside the dev container to verify your setup:

```bash
# Check Freqtrade status
freqtrade status

# Test exchange connection
freqtrade test-pairlist

# Verify database connection
freqtrade create-userdir --userdir user_data

# Test strategy
freqtrade backtesting --strategy MyAwesomeStrategy --timerange 20230101-20240101
```

## Troubleshooting

1. **Container Access Issues**

   ```bash
   # Check container status
   docker ps
   
   # View container logs
   docker logs freqtrade
   ```

2. **Database Connection**

   ```bash
   # Test database connection
   psql $DB_URL -c "SELECT 1"
   ```

3. **Network Connectivity**

   ```bash
   # Test service connectivity
   curl $CONTROLLER_URL/health
   curl $MEM0_URL/health
   ```

## Security Notes

1. Never commit `.env` files containing secrets
2. Use environment variables for sensitive data
3. Regularly rotate API keys
4. Monitor container logs for suspicious activity
5. Keep all services updated with security patches

## Maintenance

1. Regular Updates

   ```bash
   # Update containers
   docker compose pull
   docker compose up -d
   ```

2. Backup Strategy

   ```bash
   # Backup user_data
   tar -czf backup.tar.gz user_data/
   ```

3. Log Rotation

   ```bash
   # Check log size
   du -h /freqtrade/user_data/logs/
   ```

## Additional Resources

- [Freqtrade Documentation](https://www.freqtrade.io/en/stable/)
- [Docker Documentation](https://docs.docker.com/)
- [VS Code Dev Containers](https://code.visualstudio.com/docs/remote/containers)

# .env Keys Required (Per Service)

## 🧪 FreqTrade

- FREQTRADE_API_KEY
- FREQTRADE_API_SECRET

## 🧠 Mem0

- MEM0_MODEL_DIM=768  # Should match BGE-small
- MEM0_HOST

## 🔄 Controller

- CONTROLLER_PORT
- POSTGRES_URI

## 🧭 n8n

- N8N_HOST
- N8N_BASIC_AUTH

## 💬 Freq-Chat

- OPENAI_API_KEY
- OPENROUTER_API_KEY
