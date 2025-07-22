#!/bin/bash

# Service Monitoring Script for freq-chat Auto-Stack
# Usage: ./monitor_services.sh [--continuous]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Service endpoints
declare -A SERVICES=(
    ["traefik"]="http://localhost:8081/api/rawdata"
    ["controller"]="http://localhost:5050/status"
    ["openrouter_proxy"]="http://localhost:8001/healthz"
    ["bge_embedding"]="http://localhost:7861/health"
    ["mem0"]="http://localhost:8000"
    ["freq_chat"]="http://localhost:3001"
    ["n8n_direct"]="http://localhost:5678"
    ["qdrant"]="http://localhost:6333/health"
    ["postgres"]="localhost:5432"
)

# Function to check HTTP endpoint
check_http_service() {
    local name=$1
    local url=$2
    local timeout=5
    
    if curl -s --max-time $timeout "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} $name: ${GREEN}HEALTHY${NC}"
        return 0
    else
        echo -e "${RED}✗${NC} $name: ${RED}UNHEALTHY${NC}"
        return 1
    fi
}

# Function to check PostgreSQL
check_postgres() {
    if docker exec freq-chat-postgres_logging_auto pg_isready -U postgres > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} postgres: ${GREEN}HEALTHY${NC}"
        return 0
    else
        echo -e "${RED}✗${NC} postgres: ${RED}UNHEALTHY${NC}"
        return 1
    fi
}

# Function to check Docker container status
check_container_status() {
    echo -e "\n${BLUE}=== Container Status ===${NC}"
    docker compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
}

# Function to check service health
check_service_health() {
    echo -e "\n${BLUE}=== Service Health Checks ===${NC}"
    
    local healthy=0
    local total=0
    
    for service in "${!SERVICES[@]}"; do
        total=$((total + 1))
        if [[ $service == "postgres" ]]; then
            if check_postgres; then
                healthy=$((healthy + 1))
            fi
        else
            if check_http_service "$service" "${SERVICES[$service]}"; then
                healthy=$((healthy + 1))
            fi
        fi
    done
    
    echo -e "\n${BLUE}Health Summary:${NC} $healthy/$total services healthy"
    
    if [[ $healthy -eq $total ]]; then
        echo -e "${GREEN}🎉 All services are healthy!${NC}"
    else
        echo -e "${YELLOW}⚠️  Some services need attention${NC}"
    fi
}

# Function to show resource usage
check_resource_usage() {
    echo -e "\n${BLUE}=== Resource Usage ===${NC}"
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"
}

# Function to show recent logs
show_recent_logs() {
    echo -e "\n${BLUE}=== Recent Service Logs ===${NC}"
    
    local services=("controller_auto" "n8n_auto" "mem0_auto" "freq_chat_auto")
    
    for service in "${services[@]}"; do
        echo -e "\n${YELLOW}--- $service ---${NC}"
        docker compose logs --tail=3 "$service" 2>/dev/null || echo "No logs available"
    done
}

# Function to check network connectivity
check_network_connectivity() {
    echo -e "\n${BLUE}=== Network Connectivity ===${NC}"
    
    # Check internal Docker network
    if docker network inspect freq-chat_auto-stack-net > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Docker network: ${GREEN}EXISTS${NC}"
    else
        echo -e "${RED}✗${NC} Docker network: ${RED}MISSING${NC}"
    fi
    
    # Check Traefik routes
    if curl -s http://localhost:8081/api/http/routers > /dev/null 2>&1; then
        local routes=$(curl -s http://localhost:8081/api/http/routers | jq -r 'keys[]' 2>/dev/null | wc -l)
        echo -e "${GREEN}✓${NC} Traefik routes: ${GREEN}$routes configured${NC}"
    else
        echo -e "${YELLOW}⚠${NC} Traefik routes: ${YELLOW}UNAVAILABLE${NC}"
    fi
}

# Function to test service endpoints
test_service_endpoints() {
    echo -e "\n${BLUE}=== Service Endpoint Tests ===${NC}"
    
    # Test controller API
    echo -n "Controller API: "
    if response=$(curl -s http://localhost:5050/status 2>/dev/null); then
        echo -e "${GREEN}✓ $response${NC}"
    else
        echo -e "${RED}✗ Failed${NC}"
    fi
    
    # Test BGE embedding
    echo -n "BGE Embedding: "
    if response=$(curl -s http://localhost:7861/health 2>/dev/null); then
        echo -e "${GREEN}✓ $response${NC}"
    else
        echo -e "${RED}✗ Failed${NC}"
    fi
    
    # Test OpenRouter proxy
    echo -n "OpenRouter Proxy: "
    if curl -s http://localhost:8001/healthz > /dev/null 2>&1; then
        echo -e "${GREEN}✓ OK${NC}"
    else
        echo -e "${RED}✗ Failed${NC}"
    fi
}

# Main monitoring function
run_monitoring() {
    clear
    echo -e "${BLUE}🔍 freq-chat Auto-Stack Service Monitor${NC}"
    echo -e "${BLUE}=====================================\n${NC}"
    echo "Timestamp: $(date)"
    
    check_container_status
    check_service_health
    check_network_connectivity
    test_service_endpoints
    check_resource_usage
    show_recent_logs
    
    echo -e "\n${BLUE}=== Access URLs ===${NC}"
    echo "🌐 Traefik Dashboard: http://localhost:8081"
    echo "🤖 Controller API: http://localhost:5050"
    echo "🔄 n8n (via Traefik): http://n8n.localhost"
    echo "💬 Freq Chat (via Traefik): http://chat.localhost"
    echo "🧠 Mem0 (via Traefik): http://mem0.localhost"
    echo "🔗 OpenRouter Proxy: http://localhost:8001"
    echo "🔍 Qdrant: http://localhost:6333"
    echo "🐘 PostgreSQL: localhost:5432"
}

# Continuous monitoring mode
continuous_monitoring() {
    while true; do
        run_monitoring
        echo -e "\n${YELLOW}Press Ctrl+C to stop monitoring...${NC}"
        echo -e "${YELLOW}Refreshing in 30 seconds...${NC}\n"
        sleep 30
    done
}

# Main script logic
if [[ $1 == "--continuous" ]]; then
    echo "Starting continuous monitoring..."
    continuous_monitoring
else
    run_monitoring
    echo -e "\n${BLUE}💡 Tip: Use './monitor_services.sh --continuous' for live monitoring${NC}"
fi