# 🤖 Freqtrade Integration Guide

## Overview

This directory contains documentation for integrating Freqtrade with the automation stack. The integration enables automated trading, backtesting, and strategy optimization through a unified interface.

## Key Components

1. **Controller Integration** (`controller.md`)
   - FastAPI endpoints for Freqtrade communication
   - Authentication and security setup
   - Command execution and monitoring

2. **Memory Service Integration** (`mem0.md`)
   - Strategy performance tracking
   - Historical data persistence
   - Knowledge base integration

3. **Chat Interface** (`freq-chat.md`)
   - Interactive trading commands
   - Performance visualization
   - Strategy management

4. **Workflow Automation** (`workflows.md`)
   - n8n workflow templates
   - Automated backtesting
   - Performance monitoring

## Environment Setup

The Freqtrade environment runs in a Docker container managed through VS Code Dev Containers. This ensures consistent development and deployment across all environments.

### Prerequisites

- Ubuntu Native Host
- Docker Engine
- Docker Compose
- VS Code with Dev Containers extension
- Git

### Quick Start

1. Clone the repository:

   ```bash
   git clone https://github.com/your-org/freqtrade.git
   cd freqtrade
   ```

2. Open in VS Code:

   ```bash
   code .
   ```

3. When prompted, click "Reopen in Container" or use Command Palette (Ctrl+Shift+P):
   - Select "Dev Containers: Reopen in Container"

4. The container will build and start automatically, installing all dependencies.

## Configuration

1. Environment Variables
   - Copy `.env.example` to `.env`
   - Configure API keys and endpoints
   - Set up database connections

2. Trading Configuration
   - Edit `user_data/config.json`
   - Configure exchange API credentials
   - Set trading parameters

3. Strategy Setup
   - Place strategies in `user_data/strategies/`
   - Configure strategy-specific parameters
   - Test with backtesting before live deployment

## Integration Testing

1. Verify Controller Communication

   ```bash
   curl http://controller:3000/api/v1/status
   ```

2. Test Memory Service

   ```bash
   curl http://mem0:8080/health
   ```

3. Validate n8n Workflows
   - Access n8n interface at `http://localhost:5678`
   - Test Freqtrade-related workflows
   - Verify webhook triggers

## Troubleshooting

Common issues and solutions are documented in `bugs.md`. For environment-specific issues, refer to `env.md`.

## Documentation Structure

- `controller.md` - Controller service integration
- `mem0.md` - Memory service integration
- `freq-chat.md` - Chat interface documentation
- `workflows.md` - n8n workflow documentation
- `env.md` - Environment setup guide
- `bugs.md` - Known issues and solutions

## Additional Resources

- [Official Freqtrade Documentation](https://www.freqtrade.io/en/stable/)
- [Docker Documentation](https://docs.docker.com/)
- [VS Code Dev Containers](https://code.visualstudio.com/docs/remote/containers)

## Support

For issues related to:

- Freqtrade setup: Check `env.md`
- Integration problems: See `bugs.md`
- Workflow automation: Refer to `workflows.md`
- Strategy development: Review `freq-chat.md`
