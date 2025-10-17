-- Azure PostgreSQL Flexible Server Setup
-- Cloud Deployment Dashboard - Database Migration

-- Create database (if not exists)
CREATE DATABASE IF NOT EXISTS cloud_deployment_dashboard;

-- Use the database
\c cloud_deployment_dashboard;

-- Create deployments table
CREATE TABLE IF NOT EXISTS deployments (
    id SERIAL PRIMARY KEY,
    service_name VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    platform VARCHAR(100) NOT NULL,
    url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    logs TEXT,
    environment VARCHAR(50) DEFAULT 'production',
    branch VARCHAR(100) DEFAULT 'main',
    commit_hash VARCHAR(40),
    build_time INTEGER DEFAULT 0,
    health_status VARCHAR(20) DEFAULT 'unknown'
);

-- Create services table
CREATE TABLE IF NOT EXISTS services (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    repository_url TEXT,
    platform VARCHAR(100) NOT NULL,
    status VARCHAR(50) DEFAULT 'inactive',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    config JSONB DEFAULT '{}',
    last_deployment_id INTEGER REFERENCES deployments(id)
);

-- Create deployment_logs table for detailed logging
CREATE TABLE IF NOT EXISTS deployment_logs (
    id SERIAL PRIMARY KEY,
    deployment_id INTEGER NOT NULL REFERENCES deployments(id) ON DELETE CASCADE,
    level VARCHAR(20) NOT NULL DEFAULT 'info',
    message TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    source VARCHAR(100)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_deployments_service_name ON deployments(service_name);
CREATE INDEX IF NOT EXISTS idx_deployments_status ON deployments(status);
CREATE INDEX IF NOT EXISTS idx_deployments_created_at ON deployments(created_at);
CREATE INDEX IF NOT EXISTS idx_services_name ON services(name);
CREATE INDEX IF NOT EXISTS idx_services_platform ON services(platform);
CREATE INDEX IF NOT EXISTS idx_deployment_logs_deployment_id ON deployment_logs(deployment_id);
CREATE INDEX IF NOT EXISTS idx_deployment_logs_timestamp ON deployment_logs(timestamp);

-- Insert sample data for testing
INSERT INTO services (name, description, repository_url, platform, status, config) VALUES
('cloud-dashboard', 'Cloud Deployment Dashboard', 'https://github.com/user/cloud-dashboard', 'azure', 'active', '{"auto_deploy": true, "environment": "production"}'),
('api-service', 'Backend API Service', 'https://github.com/user/api-service', 'azure', 'inactive', '{"auto_deploy": false, "environment": "staging"}')
ON CONFLICT (name) DO NOTHING;

-- Insert sample deployment
INSERT INTO deployments (service_name, status, platform, url, logs, environment, branch, commit_hash, build_time, health_status) VALUES
('cloud-dashboard', 'success', 'azure', 'https://cloud-deployment-dashboard.azurewebsites.net', 'Deployment completed successfully', 'production', 'main', 'abc123def456', 120, 'healthy')
ON CONFLICT DO NOTHING;

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers to automatically update updated_at
CREATE TRIGGER update_deployments_updated_at BEFORE UPDATE ON deployments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_services_updated_at BEFORE UPDATE ON services
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions (adjust as needed for your Azure setup)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO your_azure_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO your_azure_user;