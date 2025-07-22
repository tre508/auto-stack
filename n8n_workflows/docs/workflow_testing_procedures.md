# n8n Workflow Testing Procedures

## Overview

This document outlines comprehensive testing procedures for n8n workflows using CLI-based approaches, validation methods, and automated testing frameworks.

## Pre-Testing Setup

### 1. Environment Validation

```bash
# Check n8n container status
docker ps | grep n8n

# Verify n8n CLI access
docker exec n8n_auto n8n --help

# Test database connectivity
docker exec n8n_auto n8n list:workflow
```

### 2. Backup Current Workflows

```bash
# Create backup directory
mkdir -p n8n_workflows/backups/$(date +%Y%m%d_%H%M%S)

# Export all workflows
docker exec n8n_auto n8n export:workflow --all --output=/tmp/all_workflows.json
docker cp n8n_auto:/tmp/all_workflows.json ./n8n_workflows/backups/$(date +%Y%m%d_%H%M%S)/
```

## Testing Methodology

### 1. Syntax Validation

#### JSON Schema Validation

```bash
# Install JSON schema validator
npm install -g ajv-cli

# Validate workflow JSON structure
ajv validate -s n8n_workflow_schema.json -d n8n_workflows/enhanced_centralbrain_agent.json
```

#### n8n Import Test

```bash
# Test workflow import (dry run)
docker exec n8n_auto n8n import:workflow --input=/tmp/test_workflow.json --dry-run

# Actual import for testing
docker exec n8n_auto n8n import:workflow --input=/tmp/test_workflow.json
```

### 2. Node Configuration Testing

#### Individual Node Testing

```javascript
// Test node configuration in isolation
const testNodeConfig = {
  "parameters": {
    "jsCode": "return { test: 'success', timestamp: new Date().toISOString() };"
  },
  "type": "n8n-nodes-base.code",
  "typeVersion": 2
};

// Validate required parameters
function validateNodeConfig(nodeConfig) {
  const requiredFields = ['type', 'typeVersion'];
  return requiredFields.every(field => nodeConfig.hasOwnProperty(field));
}
```

#### Connection Validation

```javascript
// Validate workflow connections
function validateConnections(workflow) {
  const nodeIds = workflow.nodes.map(node => node.id);
  const connections = workflow.connections;
  
  // Check all connection references exist
  for (const sourceNode in connections) {
    if (!nodeIds.includes(sourceNode)) {
      throw new Error(`Invalid source node: ${sourceNode}`);
    }
    
    for (const connection of connections[sourceNode].main[0] || []) {
      if (!nodeIds.includes(connection.node)) {
        throw new Error(`Invalid target node: ${connection.node}`);
      }
    }
  }
  
  return true;
}
```

### 3. Integration Testing

#### API Endpoint Testing

```bash
# Test webhook endpoints
curl -X POST http://localhost:5678/webhook/test-endpoint \
  -H "Content-Type: application/json" \
  -d '{"test": "data", "timestamp": "'$(date -Iseconds)'"}'

# Test with authentication
curl -X POST http://localhost:5678/webhook/secure-endpoint \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test-token" \
  -d '{"command": "status", "userId": "test-user"}'
```

#### Database Integration Testing

```sql
-- Test database logging functionality
SELECT * FROM agent_logs 
WHERE workflow = 'Enhanced CentralBrain Agent' 
ORDER BY created_at DESC 
LIMIT 10;

-- Verify data integrity
SELECT 
  COUNT(*) as total_logs,
  COUNT(DISTINCT run_id) as unique_runs,
  AVG(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as success_rate
FROM agent_logs 
WHERE created_at > NOW() - INTERVAL '1 hour';
```

### 4. Performance Testing

#### Load Testing Script

```bash
#!/bin/bash
# load_test_workflow.sh

WEBHOOK_URL="http://localhost:5678/webhook/enhanced-central-brain"
CONCURRENT_REQUESTS=10
TOTAL_REQUESTS=100

# Function to send single request
send_request() {
  local request_id=$1
  curl -s -w "%{http_code},%{time_total}\n" \
    -X POST "$WEBHOOK_URL" \
    -H "Content-Type: application/json" \
    -d "{
      \"chatInput\": \"test command $request_id\",
      \"userId\": \"load-test-$request_id\",
      \"sessionId\": \"session-$(date +%s)-$request_id\"
    }" \
    -o /dev/null
}

# Run concurrent requests
for i in $(seq 1 $TOTAL_REQUESTS); do
  send_request $i &
  
  # Limit concurrent requests
  if (( i % CONCURRENT_REQUESTS == 0 )); then
    wait
  fi
done

wait
echo "Load test completed"
```

#### Memory and CPU Monitoring

```bash
# Monitor n8n container resources during testing
docker stats n8n_auto --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"

# Log resource usage
docker exec n8n_auto ps aux | grep n8n
docker exec n8n_auto free -h
```

### 5. Error Handling Testing

#### Error Injection Testing

```javascript
// Test error handling in workflows
const errorTestCases = [
  {
    name: "Invalid Input",
    payload: { /* missing required fields */ },
    expectedError: "Missing required field"
  },
  {
    name: "API Timeout",
    payload: { chatInput: "test", timeout: 1 },
    expectedError: "Request timeout"
  },
  {
    name: "Database Connection Error",
    payload: { chatInput: "test", dbError: true },
    expectedError: "Database connection failed"
  }
];

// Run error tests
errorTestCases.forEach(testCase => {
  console.log(`Testing: ${testCase.name}`);
  // Send request and verify error response
});
```

#### Recovery Testing

```bash
# Test workflow recovery after errors
docker exec n8n_auto n8n restart

# Verify workflow state after restart
docker exec n8n_auto n8n list:workflow --active
```

## Automated Testing Framework

### 1. Test Suite Structure

```
n8n_workflows/tests/
├── unit/
│   ├── node_validation.test.js
│   ├── connection_validation.test.js
│   └── data_transformation.test.js
├── integration/
│   ├── api_endpoints.test.js
│   ├── database_operations.test.js
│   └── external_services.test.js
├── e2e/
│   ├── complete_workflows.test.js
│   └── user_scenarios.test.js
└── performance/
    ├── load_testing.js
    └── stress_testing.js
```

### 2. Test Execution Scripts

#### Unit Test Runner

```javascript
// tests/unit/node_validation.test.js
const { validateNodeConfig, validateConnections } = require('../utils/validators');

describe('Node Configuration Validation', () => {
  test('should validate required node fields', () => {
    const validNode = {
      id: 'test-node-001',
      name: 'Test Node',
      type: 'n8n-nodes-base.code',
      typeVersion: 2,
      parameters: {}
    };
    
    expect(validateNodeConfig(validNode)).toBe(true);
  });
  
  test('should reject invalid node configuration', () => {
    const invalidNode = {
      id: 'test-node-001',
      name: 'Test Node'
      // missing required fields
    };
    
    expect(() => validateNodeConfig(invalidNode)).toThrow();
  });
});
```

#### Integration Test Runner

```bash
#!/bin/bash
# run_integration_tests.sh

echo "Starting n8n integration tests..."

# Start test environment
docker-compose -f docker-compose.test.yml up -d

# Wait for services to be ready
sleep 30

# Run test suite
npm test -- --testPathPattern=integration

# Cleanup
docker-compose -f docker-compose.test.yml down

echo "Integration tests completed"
```

### 3. Continuous Testing Pipeline

#### GitHub Actions Workflow

```yaml
name: n8n Workflow Testing

on:
  push:
    paths:
      - 'n8n_workflows/**'
  pull_request:
    paths:
      - 'n8n_workflows/**'

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        
    - name: Install dependencies
      run: npm install
      
    - name: Validate workflow JSON
      run: npm run validate-workflows
      
    - name: Start test environment
      run: docker-compose -f docker-compose.test.yml up -d
      
    - name: Run unit tests
      run: npm run test:unit
      
    - name: Run integration tests
      run: npm run test:integration
      
    - name: Run performance tests
      run: npm run test:performance
      
    - name: Cleanup
      run: docker-compose -f docker-compose.test.yml down
```

## Test Data Management

### 1. Test Data Generation

```javascript
// Generate test data for workflow testing
function generateTestData(scenario) {
  const baseData = {
    timestamp: new Date().toISOString(),
    userId: `test-user-${Math.random().toString(36).substr(2, 9)}`,
    sessionId: `session-${Date.now()}`
  };
  
  switch (scenario) {
    case 'freqtrade':
      return {
        ...baseData,
        chatInput: 'freqtrade: status bot',
        commandType: 'freqtrade'
      };
      
    case 'documentation':
      return {
        ...baseData,
        chatInput: 'docs: search trading strategies',
        commandType: 'documentation'
      };
      
    default:
      return {
        ...baseData,
        chatInput: 'general query for testing',
        commandType: 'general'
      };
  }
}
```

### 2. Test Data Cleanup

```sql
-- Cleanup test data after testing
DELETE FROM agent_logs 
WHERE user_id LIKE 'test-user-%' 
  OR user_id LIKE 'load-test-%'
  AND created_at < NOW() - INTERVAL '1 day';

DELETE FROM freqtrade_logs 
WHERE user_id LIKE 'test-%'
  AND timestamp < NOW() - INTERVAL '1 day';
```

## Monitoring and Reporting

### 1. Test Results Dashboard

```javascript
// Generate test report
function generateTestReport(results) {
  return {
    summary: {
      totalTests: results.length,
      passed: results.filter(r => r.status === 'passed').length,
      failed: results.filter(r => r.status === 'failed').length,
      duration: results.reduce((sum, r) => sum + r.duration, 0)
    },
    details: results,
    timestamp: new Date().toISOString()
  };
}
```

### 2. Performance Metrics

```bash
# Collect performance metrics
echo "Workflow Performance Metrics:"
echo "Average Response Time: $(cat test_results.log | grep 'response_time' | awk '{sum+=$2} END {print sum/NR}')"
echo "Success Rate: $(cat test_results.log | grep 'status:success' | wc -l) / $(cat test_results.log | wc -l)"
echo "Error Rate: $(cat test_results.log | grep 'status:error' | wc -l) / $(cat test_results.log | wc -l)"
```

## Best Practices

### 1. Test Environment Isolation

- Use separate database for testing
- Mock external API calls when possible
- Use test-specific credentials and configurations

### 2. Test Data Management

- Generate realistic test data
- Clean up test data after each run
- Use consistent test identifiers

### 3. Error Handling Verification

- Test all error paths
- Verify error messages and codes
- Test recovery mechanisms

### 4. Performance Validation

- Set performance benchmarks
- Monitor resource usage
- Test under various load conditions

### 5. Documentation

- Document all test cases
- Maintain test data specifications
- Update tests when workflows change

## Troubleshooting Common Issues

### 1. Workflow Import Failures

```bash
# Check workflow JSON syntax
cat workflow.json | jq '.'

# Validate against n8n schema
docker exec n8n_auto n8n import:workflow --input=/tmp/workflow.json --validate-only
```

### 2. Connection Errors

```bash
# Test database connectivity
docker exec n8n_auto n8n db:migrate --check

# Test external API connectivity
docker exec n8n_auto curl -I http://controller:5001/health
```

### 3. Performance Issues

```bash
# Monitor workflow execution
docker logs n8n_auto --tail 100 -f

# Check system resources
docker exec n8n_auto top -n 1
```

This comprehensive testing framework ensures reliable, performant, and maintainable n8n workflows through systematic validation and continuous monitoring.
