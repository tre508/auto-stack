# Freq-Chat Integration

## ✔️ Routes Implemented

| Endpoint                | Purpose                         |
|-------------------------|----------------------------------|
| `/api/trade-history`    | Fetch trade data from Mem0       |
| `/api/recent-backtests` | Show list of recent runs         |
| `/api/backtest`         | Trigger a new backtest run       |

## 📝 Slash Commands (Planned)

- `/backtest <strategy> <timerange>`  
  → POST to `/api/backtest`, then follow-up with status polling 