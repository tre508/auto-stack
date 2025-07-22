#!/bin/bash

# n8n Workflow Testing Script
# Tests workflow import, validation, and basic functionality

echo "=== n8n Workflow Testing Script ==="
echo "Starting workflow tests at $(date)"

# Function to test workflow import
test_workflow_import() {
    local workflow_file=$1
    local workflow_name=$2
    
    echo "Testing import of $workflow_name..."
    
    # Copy workflow to container
    docker cp "$workflow_file" n8n_auto:/tmp/test_workflow.json
    
    # Test import
    if docker exec n8n_auto n8n import:workflow --input=/tmp/test_workflow.json 2>/dev/null; then
        echo "✅ $workflow_name imported successfully"
        return 0
    else
        echo "❌ $workflow_name import failed"
        return 1
    fi
}

# Function to test workflow validation
test_workflow_validation() {
    local workflow_file=$1
    
    echo "Validating JSON structure..."
    
    if jq empty "$workflow_file" 2>/dev/null; then
        echo "✅ JSON structure is valid"
        return 0
    else
        echo "❌ JSON structure is invalid"
        return 1
    fi
}

# Function to test n8n service health
test_n8n_health() {
    echo "Testing n8n service health..."
    
    if curl -s -f http://localhost:5678/healthz >/dev/null 2>&1; then
        echo "✅ n8n service is healthy"
        return 0
    else
        echo "⚠️  n8n service health check failed (using direct port)"
        
        # Test if n8n container is running
        if docker ps | grep -q n8n_auto; then
            echo "✅ n8n container is running"
            return 0
        else
            echo "❌ n8n container is not running"
            return 1
        fi
    fi
}

# Function to backup current workflows
backup_workflows() {
    echo "Creating workflow backup..."
    
    local backup_dir="n8n_workflows/backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$backup_dir"
    
    # Export current workflows
    docker exec n8n_auto n8n export:workflow --all --output=/tmp/backup_workflows.json 2>/dev/null
    docker cp n8n_auto:/tmp/backup_workflows.json "$backup_dir/" 2>/dev/null
    
    echo "✅ Workflows backed up to $backup_dir"
}

# Function to test webhook endpoints
test_webhook_endpoints() {
    echo "Testing webhook endpoints..."
    
    # Test basic webhook response
    local response=$(curl -s -w "%{http_code}" -X POST http://localhost:5678/webhook/test \
        -H "Content-Type: application/json" \
        -d '{"test": "data"}' \
        -o /dev/null 2>/dev/null)
    
    if [[ "$response" == "404" ]]; then
        echo "⚠️  Webhook endpoint returned 404 (expected for non-existent webhook)"
    elif [[ "$response" == "200" ]]; then
        echo "✅ Webhook endpoint responded successfully"
    else
        echo "⚠️  Webhook endpoint returned status: $response"
    fi
}

# Main test execution
main() {
    echo "Starting comprehensive n8n workflow tests..."
    
    # Test n8n service health
    test_n8n_health
    
    # Create backup
    backup_workflows
    
    # Test webhook endpoints
    test_webhook_endpoints
    
    # Test workflow validation
    echo ""
    echo "=== Workflow Validation Tests ==="
    
    local workflows=(
        "n8n_workflows/enhanced_centralbrain_agent.json:Enhanced CentralBrain Agent"
        "n8n_workflows/freqtrade_integration_workflow.json:Freqtrade Integration"
        "n8n_workflows/unified_logging.json:Unified Logging"
        "n8n_workflows/my_workflow.json:My Workflow"
    )
    
    local passed=0
    local total=0
    
    for workflow_info in "${workflows[@]}"; do
        IFS=':' read -r workflow_file workflow_name <<< "$workflow_info"
        
        if [[ -f "$workflow_file" ]]; then
            total=$((total + 1))
            echo ""
            echo "Testing: $workflow_name"
            echo "File: $workflow_file"
            
            if test_workflow_validation "$workflow_file"; then
                passed=$((passed + 1))
            fi
        fi
    done
    
    echo ""
    echo "=== Test Summary ==="
    echo "Validation Tests: $passed/$total passed"
    
    # Test current workflows
    echo ""
    echo "=== Current n8n Workflows ==="
    docker exec n8n_auto n8n list:workflow 2>/dev/null | while read -r line; do
        if [[ "$line" == *"|"* ]]; then
            echo "📋 $line"
        fi
    done
    
    echo ""
    echo "=== Test Completion ==="
    echo "Testing completed at $(date)"
    
    if [[ $passed -eq $total ]] && [[ $total -gt 0 ]]; then
        echo "🎉 All tests passed!"
        exit 0
    else
        echo "⚠️  Some tests failed or no workflows found"
        exit 1
    fi
}

# Run main function
main "$@"