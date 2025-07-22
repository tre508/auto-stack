# 💬 Freq-Chat Integration

## Overview

Freq-Chat provides a conversational interface for interacting with Freqtrade. It enables users to execute trades, run backtests, analyze performance, and manage strategies through natural language commands.

## Features

1. **Command Interface**
   - Execute trading commands
   - Run backtests
   - Analyze performance
   - Manage strategies

2. **Performance Visualization**
   - Trade history charts
   - Strategy performance metrics
   - Market analysis graphs

3. **Strategy Management**
   - Create and edit strategies
   - Parameter optimization
   - Performance tracking

## Command Examples

### Trading Commands

```
/trade start MyStrategy
/trade stop
/trade status
/balance
```

### Backtesting

```
/backtest MyStrategy 2024-01-01-20240627
/hyperopt MyStrategy --epochs 100
/analyze MyStrategy
```

### Strategy Management

```
/strategy list
/strategy create MyNewStrategy
/strategy edit MyStrategy
/strategy delete MyStrategy
```

## API Integration

### Command Handler

```typescript
interface CommandHandler {
    command: string;
    handler: (params: string[]) => Promise<void>;
}

const handlers: Record<string, CommandHandler> = {
    trade: async (params) => {
        const [action, strategy] = params;
        const response = await fetch('/api/trade', {
            method: 'POST',
            body: JSON.stringify({ action, strategy })
        });
        return response.json();
    },
    backtest: async (params) => {
        const [strategy, timerange] = params;
        const response = await fetch('/api/backtest', {
            method: 'POST',
            body: JSON.stringify({ strategy, timerange })
        });
        return response.json();
    }
};
```

### Performance Data

```typescript
interface TradeHistory {
    strategy: string;
    trades: Trade[];
    metrics: {
        profit: number;
        trades: number;
        winRate: number;
    };
}

async function getTradeHistory(strategy: string): Promise<TradeHistory> {
    const response = await fetch(`/api/trade-history?strategy=${strategy}`);
    return response.json();
}
```

## UI Components

### Command Input

```tsx
const CommandInput: React.FC = () => {
    const [command, setCommand] = useState('');
    
    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        const [cmd, ...params] = command.split(' ');
        await handlers[cmd]?.(params);
    };
    
    return (
        <form onSubmit={handleSubmit}>
            <input
                type="text"
                value={command}
                onChange={(e) => setCommand(e.target.value)}
                placeholder="/command params..."
            />
            <button type="submit">Send</button>
        </form>
    );
};
```

### Performance Chart

```tsx
const PerformanceChart: React.FC<{ strategy: string }> = ({ strategy }) => {
    const [data, setData] = useState<TradeHistory | null>(null);
    
    useEffect(() => {
        getTradeHistory(strategy).then(setData);
    }, [strategy]);
    
    return (
        <div className="chart">
            {/* Chart rendering logic */}
        </div>
    );
};
```

## Environment Setup

Required environment variables:

```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:3000
NEXT_PUBLIC_WS_URL=ws://localhost:3000

# Authentication
NEXTAUTH_URL=http://localhost:3001
NEXTAUTH_SECRET=your_secret

# Integration
CONTROLLER_URL=http://controller:3000
MEM0_URL=http://mem0:8080
```

## Development

### Local Setup

1. Install dependencies:

   ```bash
   pnpm install
   ```

2. Start development server:

   ```bash
   pnpm dev
   ```

3. Run tests:

   ```bash
   pnpm test
   ```

### Building for Production

```bash
# Build application
pnpm build

# Start production server
pnpm start
```

## Testing

### Unit Tests

```bash
# Run unit tests
pnpm test:unit

# Run with coverage
pnpm test:coverage
```

### Integration Tests

```bash
# Run integration tests
pnpm test:integration

# Run E2E tests
pnpm test:e2e
```

## Deployment

1. Build container:

   ```bash
   docker build -t freq-chat .
   ```

2. Run container:

   ```bash
   docker run -d \
       -p 3001:3001 \
       --name freq-chat \
       --network auto-stack-net \
       freq-chat
   ```

## Security

1. **Authentication**
   - NextAuth.js integration
   - JWT token validation
   - Role-based access

2. **API Security**
   - CORS configuration
   - Rate limiting
   - Input validation

## Monitoring

### Health Check

```bash
# Check application status
curl http://localhost:3001/api/health

# Check WebSocket connection
wscat -c ws://localhost:3001
```

### Logs

```bash
# View application logs
docker logs freq-chat

# Follow logs
docker logs -f freq-chat
```

## Troubleshooting

1. **API Connection Issues**

   ```bash
   # Check API health
   curl http://controller:3000/health
   
   # Test WebSocket
   websocat ws://localhost:3001/ws
   ```

2. **UI Problems**

   ```bash
   # Clear cache
   pnpm clean
   
   # Rebuild
   pnpm build
   ```

## Additional Resources

- [UI Documentation](docs/architecture/services/freq-chat/README.md)
- [API Reference](docs/API_Contracts.md)
- [Component Library](docs/architecture/services/freq-chat/components.md)

## ✔️ Routes Implemented

| Endpoint                | Purpose                         |
|-------------------------|----------------------------------|
| `/api/trade-history`    | Fetch trade data from Mem0       |
| `/api/recent-backtests` | Show list of recent runs         |
| `/api/backtest`         | Trigger a new backtest run       |

## 📝 Slash Commands (Planned)

- `/backtest <strategy> <timerange>`  
  → POST to `/api/backtest`, then follow-up with status polling
