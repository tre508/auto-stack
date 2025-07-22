# n8n Enhanced Workflows Activation Guide

## Overview
This guide provides step-by-step instructions for activating the enhanced n8n workflows created by the AI agent.

## Prerequisites
- n8n instance running at http://localhost:5678
- PostgreSQL database accessible
- Required API credentials configured

## Workflow Activation Steps

### 1. Access n8n Interface
1. Open your web browser
2. Navigate to http://localhost:5678
3. Log in to your n8n instance

### 2. Import Workflows (if not already imported)
If workflows are not visible in the UI:
1. Click "Import from File" or use the "+" button
2. Copy and paste the JSON content from:
   - `enhanced_centralbrain_agent.json`
   - `freqtrade_integration_workflow.json`

### 3. Configure Credentials

#### PostgreSQL Database Credential
1. Go to Settings → Credentials
2. Click "Create New Credential"
3. Select "Postgres"
4. Configure with these settings:
   - Name: "Postgres account"
   - Host: postgres (or your PostgreSQL host)
   - Port: 5432
   - Database: n8n_db
   - User: n8n_user
   - Password: n8n_password
5. Test connection and save

#### Freqtrade API Credential (if using Freqtrade)
1. Create new credential
2. Select "HTTP Header Auth"
3. Configure:
   - Name: "Freqtrade API"
   - Header Name: Authorization
   - Header Value: Bearer YOUR_FREQTRADE_API_KEY

#### Controller API Credential
1. Create new credential
2. Select "HTTP Header Auth" 
3. Configure:
   - Name: "Controller API"
   - Header Name: Authorization
   - Header Value: Bearer YOUR_CONTROLLER_API_KEY

### 4. Update Workflow Configurations

#### Enhanced CentralBrain Agent
1. Open the "Enhanced CentralBrain Agent" workflow
2. Click on each HTTP Request node
3. Update the URL if needed (default: http://localhost:8000)
4. Assign the appropriate credentials
5. Update PostgreSQL nodes with the "Postgres account" credential

#### Freqtrade Integration Workflow  
1. Open the "Freqtrade Integration Workflow"
2. Update HTTP Request nodes with Freqtrade API URL
3. Assign "Freqtrade API" credentials to HTTP nodes
4. Update PostgreSQL logging node with "Postgres account" credential

### 5. Activate Workflows
1. Open each workflow
2. Click the toggle switch in the top-right corner to activate
3. Verify the status shows "Active"

### 6. Test Webhook Endpoints

#### Enhanced CentralBrain Agent
```bash
curl -X POST http://localhost:5678/webhook/enhanced-central-brain \
  -H "Content-Type: application/json" \
  -d '{
    "chatInput": "test command",
    "userId": "test-user",
    "sessionId": "test-session"
  }'
```

#### Freqtrade Integration
```bash
curl -X POST http://localhost:5678/webhook/freqtrade-integration \
  -H "Content-Type: application/json" \
  -d '{
    "command": "status bot",
    "userId": "test-user",
    "sessionId": "test-session"
  }'
```

## Environment Variables
Set these environment variables in your n8n container:

```bash
FREQTRADE_URL=http://localhost:8080
FREQTRADE_API_KEY=your_freqtrade_api_key
CONTROLLER_URL=http://localhost:8000
CONTROLLER_API_KEY=your_controller_api_key
POSTGRES_HOST=postgres
POSTGRES_USER=n8n_user
POSTGRES_PASSWORD=n8n_password
```

## Database Setup
Execute the SQL schema in `database_schema.sql` to create required tables:

```bash
psql -h localhost -U n8n_user -d n8n_db -f database_schema.sql
```

## Troubleshooting

### Workflow Not Activating
- Check all credentials are properly configured
- Verify database connectivity
- Ensure all required environment variables are set

### Webhook Returns 404
- Verify workflow is activated (toggle switch is ON)
- Check webhook path matches exactly
- Ensure n8n service is running

### Database Connection Errors
- Verify PostgreSQL is running and accessible
- Check credentials and connection parameters
- Test connection from n8n container

### API Integration Errors
- Verify API endpoints are reachable
- Check API credentials and tokens
- Review API documentation for correct endpoints

## Monitoring and Logs
- Check n8n execution logs in the UI
- Monitor database tables for logged activities
- Use the test scripts to validate functionality

## Support
For issues or questions:
1. Check n8n documentation: https://docs.n8n.io
2. Review workflow execution logs
3. Validate JSON structure with provided test scripts
