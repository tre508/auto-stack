# n8n Workflows: FreqTrade Integration

## ✅ Activated Workflows

| Workflow Name                  | Purpose                               |
|-------------------------------|----------------------------------------|
| Freqtrade_Task_Runner.json    | Main task dispatcher for strategy runs |
| Backtest_Agent.json           | Handles backtest execution and logs    |
| Freqtrade_Log_Monitor.json    | Watches logs for key events            |
| NotificationAgent.json        | Sends alerts based on triggers         |
| PerformanceMonitoring_Agent.json | Tracks metrics and forwards to Mem0 |

## Notes
- All workflows are set to `active: true`
- Use the n8n UI or API to verify import integrity and schema compliance 