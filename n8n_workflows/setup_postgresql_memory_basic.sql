-- PostgreSQL Memory System Setup for n8n (Basic Version without pgvector)
-- This script creates a basic document storage system that n8n can use

-- Create documents table without vector embeddings (basic version)
CREATE TABLE IF NOT EXISTS documents_vector_store (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    collection_name VARCHAR(255) DEFAULT 'default',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_documents_collection ON documents_vector_store(collection_name);
CREATE INDEX IF NOT EXISTS idx_documents_created_at ON documents_vector_store(created_at);
CREATE INDEX IF NOT EXISTS idx_documents_metadata ON documents_vector_store USING GIN(metadata);

-- Create full-text search index for content
CREATE INDEX IF NOT EXISTS idx_documents_content_fts ON documents_vector_store USING GIN(to_tsvector('english', content));

-- Function to search documents by text similarity (basic version)
CREATE OR REPLACE FUNCTION search_documents_basic(
    search_query TEXT,
    collection_filter VARCHAR(255) DEFAULT NULL,
    limit_count INTEGER DEFAULT 5
)
RETURNS TABLE (
    id UUID,
    content TEXT,
    metadata JSONB,
    collection_name VARCHAR(255),
    similarity_score REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        d.id,
        d.content,
        d.metadata,
        d.collection_name,
        ts_rank(to_tsvector('english', d.content), plainto_tsquery('english', search_query)) AS similarity_score
    FROM documents_vector_store d
    WHERE 
        (collection_filter IS NULL OR d.collection_name = collection_filter)
        AND to_tsvector('english', d.content) @@ plainto_tsquery('english', search_query)
    ORDER BY similarity_score DESC
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;

-- Function to get recent documents
CREATE OR REPLACE FUNCTION get_recent_documents(
    collection_filter VARCHAR(255) DEFAULT NULL,
    limit_count INTEGER DEFAULT 10
)
RETURNS TABLE (
    id UUID,
    content TEXT,
    metadata JSONB,
    collection_name VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        d.id,
        d.content,
        d.metadata,
        d.collection_name,
        d.created_at
    FROM documents_vector_store d
    WHERE (collection_filter IS NULL OR d.collection_name = collection_filter)
    ORDER BY d.created_at DESC
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;

-- Insert sample data for testing
INSERT INTO documents_vector_store (content, metadata, collection_name) VALUES
('Welcome to the CentralBrain Agent system. This is a comprehensive AI assistant.', '{"type": "welcome", "category": "system"}', 'centralbrain_docs'),
('The agent can help with various tasks including data analysis, code generation, and automation.', '{"type": "capability", "category": "features"}', 'centralbrain_docs'),
('To use the system effectively, provide clear and specific instructions.', '{"type": "instruction", "category": "usage"}', 'centralbrain_docs');

-- Create view for monitoring
CREATE OR REPLACE VIEW memory_system_stats AS
SELECT 
    collection_name,
    COUNT(*) as document_count,
    AVG(LENGTH(content)) as avg_content_length,
    MIN(created_at) as first_document,
    MAX(created_at) as latest_document
FROM documents_vector_store 
GROUP BY collection_name;

-- Grant permissions
GRANT ALL PRIVILEGES ON documents_vector_store TO autostack_logger;
GRANT ALL PRIVILEGES ON memory_system_stats TO autostack_logger;

-- Display setup completion message
SELECT 'PostgreSQL Memory System (Basic) setup completed successfully!' as status;
SELECT 'Tables created: documents_vector_store' as tables_info;
SELECT 'Functions created: search_documents_basic, get_recent_documents' as functions_info;
SELECT 'Views created: memory_system_stats' as views_info;

-- Show sample data
SELECT 'Sample documents inserted:' as sample_info;
SELECT content, collection_name FROM documents_vector_store LIMIT 3;