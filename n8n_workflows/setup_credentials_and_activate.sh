#!/bin/bash

# n8n Enhanced Workflows Setup and Activation Script
# Configures credentials and provides activation instructions

echo "=== n8n Enhanced Workflows Setup ==="
echo "Setting up credentials and activation instructions"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    local status=$1
    local message=$2
    case $status in
        "SUCCESS") echo -e "${GREEN}✅ $message${NC}" ;;
        "ERROR") echo -e "${RED}❌ $message${NC}" ;;
        "WARNING") echo -e "${YELLOW}⚠️  $message${NC}" ;;
        "INFO") echo -e "${BLUE}ℹ️  $message${NC}" ;;
    esac
}

# Create PostgreSQL credentials
setup_postgres_credentials() {
    print_status "INFO" "Setting up PostgreSQL credentials..."
    
    cat > n8n_workflows/credentials/postgres_credentials.json << 'EOF'
{
    "name": "Postgres account",
    "type": "postgres",
    "data": {
        "host": "postgres",
        "port": 5432,
        "database": "n8n_db",
        "user": "n8n_user",
        "password": "n8n_password",
        "allowUnauthorizedCerts": false,
        "ssl": "disable"
    }
}
EOF
    
    print_status "SUCCESS" "PostgreSQL credentials template created"
}

# Create HTTP credentials for APIs
setup_http_credentials() {
    print_status "INFO" "Setting up HTTP API credentials..."
    
    cat > n8n_workflows/credentials/freqtrade_api_credentials.json << 'EOF'
{
    "name": "Freqtrade API",
    "type": "httpHeaderAuth",
    "data": {
        "name": "Authorization",
        "value": "Bearer YOUR_FREQTRADE_API_KEY_HERE"
    }
}
EOF
    
    cat > n8n_workflows/credentials/controller_api_credentials.json << 'EOF'
{
    "name": "Controller API",
    "type": "httpHeaderAuth", 
    "data": {
        "name": "Authorization",
        "value": "Bearer YOUR_CONTROLLER_API_KEY_HERE"
    }
}
EOF
    
    print_status "SUCCESS" "HTTP API credentials templates created"
}

# Create environment variables template
create_env_template() {
    print_status "INFO" "Creating environment variables template..."
    
    cat > n8n_workflows/env_variables_template.env << 'EOF'
# n8n Enhanced Workflows Environment Variables
# Copy this file to .env and update with your actual values

# Database Configuration
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=n8n_db
POSTGRES_USER=n8n_user
POSTGRES_PASSWORD=n8n_password

# Freqtrade Configuration
FREQTRADE_URL=http://localhost:8080
FREQTRADE_API_KEY=your_freqtrade_api_key

# Controller Configuration
CONTROLLER_URL=http://localhost:8000
CONTROLLER_API_KEY=your_controller_api_key

# n8n Configuration
N8N_WEBHOOK_URL=http://localhost:5678
N8N_SECURE_COOKIE=false
N8N_ENFORCE_SETTINGS_FILE_PERMISSIONS=false
N8N_RUNNERS_ENABLED=true

# Logging Configuration
LOG_LEVEL=info
LOG_FORMAT=json
EOF
    
    print_status "SUCCESS" "Environment variables template created"
}

# Create database schema
create_database_schema() {
    print_status "INFO" "Creating database schema for workflow logging..."
    
    cat > n8n_workflows/database_schema.sql << 'EOF'
-- Database schema for n8n enhanced workflows logging

-- Enhanced CentralBrain Agent logs
CREATE TABLE IF NOT EXISTS centralbrain_logs (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    session_id VARCHAR(255) NOT NULL,
    command TEXT NOT NULL,
    command_type VARCHAR(50),
    success BOOLEAN DEFAULT false,
    response_data JSONB,
    error_data JSONB,
    execution_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Freqtrade integration logs
CREATE TABLE IF NOT EXISTS freqtrade_logs (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    session_id VARCHAR(255) NOT NULL,
    command TEXT NOT NULL,
    action VARCHAR(50),
    success BOOLEAN DEFAULT false,
    analysis TEXT,
    recommendations JSONB,
    raw_data JSONB,
    error JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- General workflow execution logs
CREATE TABLE IF NOT EXISTS workflow_execution_logs (
    id SERIAL PRIMARY KEY,
    workflow_id VARCHAR(255) NOT NULL,
    workflow_name VARCHAR(255) NOT NULL,
    execution_id VARCHAR(255),
    user_id VARCHAR(255),
    session_id VARCHAR(255),
    status VARCHAR(50) NOT NULL,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    duration_ms INTEGER,
    input_data JSONB,
    output_data JSONB,
    error_data JSONB,
    metadata JSONB
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_centralbrain_user_session ON centralbrain_logs(user_id, session_id);
CREATE INDEX IF NOT EXISTS idx_centralbrain_created_at ON centralbrain_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_freqtrade_user_session ON freqtrade_logs(user_id, session_id);
CREATE INDEX IF NOT EXISTS idx_freqtrade_created_at ON freqtrade_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_workflow_execution_workflow_id ON workflow_execution_logs(workflow_id);
CREATE INDEX IF NOT EXISTS idx_workflow_execution_created_at ON workflow_execution_logs(start_time);
EOF
    
    print_status "SUCCESS" "Database schema created"
}

# Generate activation instructions
generate_activation_instructions() {
    print_status "INFO" "Generating workflow activation instructions..."
    
    cat > n8n_workflows/ACTIVATION_INSTRUCTIONS.md << 'EOF'
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
EOF
    
    print_status "SUCCESS" "Activation instructions generated"
}

# Create directory structure
create_directory_structure() {
    print_status "INFO" "Creating directory structure..."
    
    mkdir -p n8n_workflows/credentials
    mkdir -p n8n_workflows/test_reports
    mkdir -p n8n_workflows/backups
    mkdir -p n8n_workflows/docs
    
    print_status "SUCCESS" "Directory structure created"
}

# Main execution
main() {
    print_status "INFO" "Starting n8n enhanced workflows setup..."
    echo ""
    
    create_directory_structure
    setup_postgres_credentials
    setup_http_credentials
    create_env_template
    create_database_schema
    generate_activation_instructions
    
    echo ""
    print_status "SUCCESS" "Setup completed!"
    echo ""
    echo "=== Next Steps ==="
    echo "1. Review and update credentials in n8n_workflows/credentials/"
    echo "2. Set environment variables using env_variables_template.env"
    echo "3. Execute database_schema.sql in your PostgreSQL instance"
    echo "4. Follow ACTIVATION_INSTRUCTIONS.md to activate workflows"
    echo "5. Test using the provided test scripts"
    echo ""
    echo "=== Files Created ==="
    echo "📁 n8n_workflows/credentials/ - Credential templates"
    echo "📄 n8n_workflows/env_variables_template.env - Environment variables"
    echo "📄 n8n_workflows/database_schema.sql - Database schema"
    echo "📄 n8n_workflows/ACTIVATION_INSTRUCTIONS.md - Activation guide"
}

# Run main function
main "$@" 