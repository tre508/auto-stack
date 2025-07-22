#!/bin/bash

# PostgreSQL Memory System Monitor Script
# Usage: ./monitor_postgresql_memory.sh [check|stats|search|recent]

CONTAINER="postgres_logging_auto"
USER="autostack_logger"
DATABASE="n8n_memory"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to check if container is running
check_container() {
    if ! docker ps | grep -q "$CONTAINER"; then
        echo -e "${RED}❌ PostgreSQL container '$CONTAINER' is not running${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ PostgreSQL container is running${NC}"
}

# Function to check database connection
check_connection() {
    echo -e "${YELLOW}🔍 Checking database connection...${NC}"
    if docker exec "$CONTAINER" psql -U "$USER" -d "$DATABASE" -c "SELECT 1;" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Database connection successful${NC}"
    else
        echo -e "${RED}❌ Database connection failed${NC}"
        exit 1
    fi
}

# Function to show system statistics
show_stats() {
    echo -e "${YELLOW}📊 Memory System Statistics:${NC}"
    docker exec "$CONTAINER" psql -U "$USER" -d "$DATABASE" -c "
        SELECT 
            collection_name,
            document_count,
            ROUND(avg_content_length::numeric, 2) as avg_content_length,
            first_document,
            latest_document
        FROM memory_system_stats;
    "
}

# Function to test search functionality
test_search() {
    echo -e "${YELLOW}🔍 Testing search functionality...${NC}"
    docker exec "$CONTAINER" psql -U "$USER" -d "$DATABASE" -c "
        SELECT 
            LEFT(content, 50) || '...' as content_preview,
            ROUND(similarity_score::numeric, 4) as score,
            collection_name
        FROM search_documents_basic('AI assistant', 'centralbrain_docs', 3);
    "
}

# Function to show recent documents
show_recent() {
    echo -e "${YELLOW}📄 Recent documents:${NC}"
    docker exec "$CONTAINER" psql -U "$USER" -d "$DATABASE" -c "
        SELECT 
            LEFT(content, 60) || '...' as content_preview,
            collection_name,
            created_at
        FROM get_recent_documents('centralbrain_docs', 5);
    "
}

# Function to run full health check
full_check() {
    echo -e "${YELLOW}🏥 Running full health check...${NC}"
    echo ""
    check_container
    check_connection
    echo ""
    show_stats
    echo ""
    test_search
    echo ""
    show_recent
    echo ""
    echo -e "${GREEN}✅ Health check completed${NC}"
}

# Main script logic
case "${1:-check}" in
    "check")
        full_check
        ;;
    "stats")
        check_container
        check_connection
        show_stats
        ;;
    "search")
        check_container
        check_connection
        test_search
        ;;
    "recent")
        check_container
        check_connection
        show_recent
        ;;
    *)
        echo "Usage: $0 [check|stats|search|recent]"
        echo "  check  - Run full health check (default)"
        echo "  stats  - Show system statistics"
        echo "  search - Test search functionality"
        echo "  recent - Show recent documents"
        exit 1
        ;;
esac