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
