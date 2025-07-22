-- PostgreSQL Memory System Setup for Enhanced CentralBrain Agent
-- Run this script in your PostgreSQL database to set up the vector store

-- Enable pgvector extension (required for vector operations)
CREATE EXTENSION IF NOT EXISTS vector;

-- Create documents vector store table
CREATE TABLE IF NOT EXISTS documents_vector_store (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    collection_name VARCHAR(255) NOT NULL DEFAULT 'centralbrain_docs',
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    embedding vector(768), -- 768 dimensions for sentence-transformers/all-MiniLM-L6-v2
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for faster similarity search using IVFFlat
CREATE INDEX IF NOT EXISTS documents_vector_store_embedding_idx 
ON documents_vector_store USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100);

-- Create index for collection filtering
CREATE INDEX IF NOT EXISTS documents_vector_store_collection_idx 
ON documents_vector_store (collection_name);

-- Create index for metadata filtering (GIN index for JSONB)
CREATE INDEX IF NOT EXISTS documents_vector_store_metadata_idx 
ON documents_vector_store USING gin (metadata);

-- Create index for timestamp queries
CREATE INDEX IF NOT EXISTS documents_vector_store_created_at_idx 
ON documents_vector_store (created_at);

-- Add trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_documents_vector_store_updated_at 
    BEFORE UPDATE ON documents_vector_store 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create a view for easy monitoring
CREATE OR REPLACE VIEW vector_store_stats AS
SELECT 
    collection_name,
    COUNT(*) as document_count,
    AVG(array_length(embedding::float[], 1)) as avg_vector_dimension,
    MIN(created_at) as first_document,
    MAX(created_at) as latest_document,
    COUNT(DISTINCT (metadata->>'source')) as unique_sources,
    COUNT(DISTINCT (metadata->>'type')) as unique_types
FROM documents_vector_store 
GROUP BY collection_name;

-- Insert sample data for testing (optional)
INSERT INTO documents_vector_store (content, metadata, collection_name) VALUES
('Freqtrade is a cryptocurrency trading bot that supports backtesting and live trading with multiple exchanges.', 
 '{"source": "freqtrade_docs", "type": "documentation", "category": "overview"}', 
 'centralbrain_docs'),
('The Enhanced CentralBrain Agent is an AI-powered system that routes commands and provides intelligent responses for trading operations.', 
 '{"source": "centralbrain_system", "type": "documentation", "category": "system"}', 
 'centralbrain_docs'),
('PostgreSQL with pgvector extension provides efficient vector storage and similarity search capabilities for AI applications.', 
 '{"source": "technical_docs", "type": "documentation", "category": "database"}', 
 'centralbrain_docs')
ON CONFLICT DO NOTHING;

-- Grant necessary permissions (adjust user as needed)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON documents_vector_store TO your_n8n_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO your_n8n_user;

-- Display setup completion message
SELECT 'PostgreSQL Vector Memory System setup completed successfully!' as status,
       COUNT(*) as sample_documents_inserted
FROM documents_vector_store 
WHERE collection_name = 'centralbrain_docs'; 