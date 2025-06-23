# Controller API Endpoints

## 🧠 Key Endpoints

- `POST /notify` — Receives performance logs from n8n
- `GET /api/trade-history?run_id=...`
- `GET /api/recent-backtests?limit=...`
- `POST /api/backtest` — Triggered by chat UI

## Internal Flow

1. Trigger from n8n → Controller parses → stores in Mem0
2. Fetch from Freq-Chat → Controller queries Mem0 → returns formatted result 