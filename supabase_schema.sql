-- Cloud Deployment Dashboard - Supabase Schema
-- Bu dosya Supabase veritabanında gerekli tabloları oluşturur

-- Deployments tablosu
CREATE TABLE IF NOT EXISTS deployments (
    id VARCHAR(50) PRIMARY KEY,
    image VARCHAR(255) NOT NULL,
    action VARCHAR(50) NOT NULL,
    environment VARCHAR(50) DEFAULT 'development',
    port_mapping VARCHAR(100),
    env_vars TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    progress INTEGER DEFAULT 0,
    start_time TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    end_time TIMESTAMP WITH TIME ZONE,
    logs TEXT,
    created_by VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Health checks tablosu
CREATE TABLE IF NOT EXISTS health_checks (
    id SERIAL PRIMARY KEY,
    overall_status VARCHAR(50) NOT NULL,
    checks JSONB NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    duration_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- System metrics tablosu
CREATE TABLE IF NOT EXISTS system_metrics (
    id SERIAL PRIMARY KEY,
    cpu_usage DECIMAL(5,2),
    memory_usage DECIMAL(5,2),
    disk_usage DECIMAL(5,2),
    network_io JSONB,
    active_containers INTEGER DEFAULT 0,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Deployment logs tablosu
CREATE TABLE IF NOT EXISTS deployment_logs (
    id SERIAL PRIMARY KEY,
    deployment_id VARCHAR(50) REFERENCES deployments(id),
    log_level VARCHAR(20) DEFAULT 'INFO',
    message TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Containers tablosu
CREATE TABLE IF NOT EXISTS containers (
    id VARCHAR(100) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    image VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL,
    ports JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    deployment_id VARCHAR(50) REFERENCES deployments(id)
);

-- Performans için indeksler
CREATE INDEX IF NOT EXISTS idx_deployments_status ON deployments(status);
CREATE INDEX IF NOT EXISTS idx_deployments_created_at ON deployments(created_at);
CREATE INDEX IF NOT EXISTS idx_health_checks_timestamp ON health_checks(timestamp);
CREATE INDEX IF NOT EXISTS idx_system_metrics_timestamp ON system_metrics(timestamp);
CREATE INDEX IF NOT EXISTS idx_deployment_logs_deployment_id ON deployment_logs(deployment_id);
CREATE INDEX IF NOT EXISTS idx_deployment_logs_timestamp ON deployment_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_containers_status ON containers(status);

-- Örnek veriler
INSERT INTO deployments (id, image, action, environment, status, progress, start_time, end_time) VALUES
('demo-001', 'nginx:latest', 'deploy', 'development', 'completed', 100, NOW() - INTERVAL '2 hours', NOW() - INTERVAL '1 hour 45 minutes'),
('demo-002', 'redis:alpine', 'deploy', 'staging', 'completed', 100, NOW() - INTERVAL '1 hour', NOW() - INTERVAL '45 minutes'),
('demo-003', 'postgres:13', 'deploy', 'production', 'failed', 75, NOW() - INTERVAL '30 minutes', NOW() - INTERVAL '25 minutes'),
('demo-004', 'node:18-alpine', 'deploy', 'development', 'running', 60, NOW() - INTERVAL '10 minutes', NULL),
('demo-005', 'python:3.11-slim', 'deploy', 'staging', 'pending', 0, NOW() - INTERVAL '5 minutes', NULL)
ON CONFLICT (id) DO NOTHING;

-- Örnek health check verileri
INSERT INTO health_checks (overall_status, checks, duration_ms) VALUES
('healthy', '{"system": {"status": "healthy", "message": "System resources are normal"}, "database": {"status": "healthy", "message": "Database connection successful"}, "containers": {"status": "healthy", "message": "All containers running normally"}}', 250),
('warning', '{"system": {"status": "warning", "message": "High CPU usage detected"}, "database": {"status": "healthy", "message": "Database connection successful"}, "containers": {"status": "healthy", "message": "All containers running normally"}}', 180),
('healthy', '{"system": {"status": "healthy", "message": "System resources are normal"}, "database": {"status": "healthy", "message": "Database connection successful"}, "containers": {"status": "healthy", "message": "All containers running normally"}}', 200);

-- Örnek sistem metrikleri
INSERT INTO system_metrics (cpu_usage, memory_usage, disk_usage, network_io, active_containers) VALUES
(45.2, 67.8, 23.1, '{"bytes_sent": 1024000, "bytes_recv": 2048000}', 5),
(52.1, 71.3, 24.5, '{"bytes_sent": 1124000, "bytes_recv": 2148000}', 6),
(38.7, 65.2, 22.8, '{"bytes_sent": 924000, "bytes_recv": 1948000}', 4),
(41.3, 69.1, 23.7, '{"bytes_sent": 1024000, "bytes_recv": 2048000}', 5);

-- Örnek deployment log verileri
INSERT INTO deployment_logs (deployment_id, log_level, message) VALUES
('demo-001', 'INFO', 'Starting deployment process'),
('demo-001', 'INFO', 'Pulling image nginx:latest'),
('demo-001', 'INFO', 'Image pulled successfully'),
('demo-001', 'INFO', 'Creating container'),
('demo-001', 'INFO', 'Container started successfully'),
('demo-001', 'INFO', 'Deployment completed'),
('demo-002', 'INFO', 'Starting deployment process'),
('demo-002', 'INFO', 'Pulling image redis:alpine'),
('demo-002', 'INFO', 'Container started successfully'),
('demo-003', 'INFO', 'Starting deployment process'),
('demo-003', 'ERROR', 'Failed to pull image postgres:13'),
('demo-003', 'ERROR', 'Deployment failed'),
('demo-004', 'INFO', 'Starting deployment process'),
('demo-004', 'INFO', 'Pulling image node:18-alpine'),
('demo-004', 'INFO', 'Container creation in progress');

-- Örnek container verileri
INSERT INTO containers (id, name, image, status, ports, started_at, deployment_id) VALUES
('nginx-demo-001', 'nginx-demo', 'nginx:latest', 'running', '{"80/tcp": [{"HostPort": "8080"}]}', NOW() - INTERVAL '1 hour 45 minutes', 'demo-001'),
('redis-demo-002', 'redis-demo', 'redis:alpine', 'running', '{"6379/tcp": [{"HostPort": "6379"}]}', NOW() - INTERVAL '45 minutes', 'demo-002'),
('node-demo-004', 'node-demo', 'node:18-alpine', 'running', '{"3000/tcp": [{"HostPort": "3000"}]}', NOW() - INTERVAL '10 minutes', 'demo-004')
ON CONFLICT (id) DO NOTHING;

-- updated_at otomatik güncelleme fonksiyonu
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- updated_at otomatik güncelleme trigger'ı
CREATE TRIGGER update_deployments_updated_at BEFORE UPDATE ON deployments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Yaygın sorgular için view'lar
CREATE OR REPLACE VIEW deployment_summary AS
SELECT 
    status,
    COUNT(*) as count,
    ROUND(AVG(progress), 2) as avg_progress
FROM deployments 
GROUP BY status;

CREATE OR REPLACE VIEW recent_deployments AS
SELECT 
    id,
    image,
    action,
    environment,
    status,
    progress,
    start_time,
    end_time,
    EXTRACT(EPOCH FROM (COALESCE(end_time, NOW()) - start_time)) as duration
FROM deployments 
ORDER BY start_time DESC 
LIMIT 10;