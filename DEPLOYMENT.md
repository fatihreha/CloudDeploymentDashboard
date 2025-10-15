# Deployment Guide

This guide provides comprehensive instructions for deploying the Cloud Deployment Automation Dashboard in various environments.

## 📋 Prerequisites

### System Requirements
- **Operating System**: Linux (Ubuntu 20.04+), macOS, or Windows 10/11
- **RAM**: Minimum 4GB, Recommended 8GB+
- **Storage**: Minimum 20GB free space
- **Network**: Internet connection for downloading dependencies

### Software Dependencies
- **Docker**: Version 20.10+
- **Docker Compose**: Version 2.0+
- **Python**: Version 3.11+ (for local development)
- **Git**: Latest version
- **Node.js**: Version 18+ (optional, for frontend development)

### Installation Commands

#### Ubuntu/Debian
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Python and Git
sudo apt install python3 python3-pip python3-venv git -y

# Logout and login to apply Docker group changes
```

#### CentOS/RHEL
```bash
# Install Docker
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install docker-ce docker-ce-cli containerd.io -y
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Python and Git
sudo yum install python3 python3-pip git -y
```

#### macOS
```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Docker Desktop
brew install --cask docker

# Install Python and Git
brew install python git

# Start Docker Desktop application
open /Applications/Docker.app
```

#### Windows
```powershell
# Install Docker Desktop
# Download from: https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe

# Install Python
# Download from: https://www.python.org/downloads/windows/

# Install Git
# Download from: https://git-scm.com/download/win

# Verify installations
docker --version
python --version
git --version
```

## 🚀 Deployment Methods

### Method 1: Quick Start (Recommended)

#### 1. Clone Repository
```bash
git clone <repository-url>
cd cloud-deployment-dashboard
```

#### 2. Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit environment variables
nano .env
```

#### 3. Deploy with Docker Compose
```bash
# Development deployment
docker-compose up -d

# Production deployment with monitoring
docker-compose --profile production --profile monitoring up -d

# Check status
docker-compose ps
```

#### 4. Verify Deployment
```bash
# Check application health
curl http://localhost:5000/api/health-check

# View logs
docker-compose logs -f dashboard
```

### Method 2: Script-based Deployment

#### 1. Use Deployment Script
```bash
# Make script executable
chmod +x scripts/deploy.sh

# Development deployment
./scripts/deploy.sh

# Production deployment
./scripts/deploy.sh --production --build

# Clean deployment (removes existing containers)
./scripts/deploy.sh --clean --build --production
```

#### 2. Script Options
```bash
# Available options:
--build          # Build images before deployment
--production     # Use production configuration
--monitoring     # Enable monitoring stack
--clean          # Remove existing containers
--backup         # Create backup before deployment
--ssl            # Enable SSL/HTTPS
--help           # Show help message
```

### Method 3: Manual Deployment

#### 1. Build Application Image
```bash
# Build the main application
docker build -t dashboard:latest .

# Verify image
docker images | grep dashboard
```

#### 2. Start Dependencies
```bash
# Start PostgreSQL
docker run -d \
  --name dashboard-postgres \
  -e POSTGRES_DB=dashboard \
  -e POSTGRES_USER=dashboard_user \
  -e POSTGRES_PASSWORD=dashboard_password \
  -v postgres_data:/var/lib/postgresql/data \
  -p 5432:5432 \
  postgres:15

# Start Redis
docker run -d \
  --name dashboard-redis \
  -v redis_data:/data \
  -p 6379:6379 \
  redis:7-alpine

# Initialize database
docker exec -i dashboard-postgres psql -U dashboard_user -d dashboard < init.sql
```

#### 3. Start Application
```bash
# Run dashboard application
docker run -d \
  --name dashboard-app \
  --link dashboard-postgres:postgres \
  --link dashboard-redis:redis \
  -e DATABASE_URL=postgresql://dashboard_user:dashboard_password@postgres:5432/dashboard \
  -e REDIS_URL=redis://redis:6379/0 \
  -p 5000:5000 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  dashboard:latest
```

## 🌍 Environment-Specific Deployments

### Development Environment

#### Configuration
```yaml
# docker-compose.override.yml
version: '3.8'
services:
  dashboard:
    environment:
      - FLASK_ENV=development
      - FLASK_DEBUG=true
    volumes:
      - ./app:/app/app
      - ./static:/app/static
    ports:
      - "5000:5000"
      - "5678:5678"  # Debug port
```

#### Commands
```bash
# Start development environment
docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d

# Enable hot reload
docker-compose exec dashboard python -m flask run --host=0.0.0.0 --debug

# Access development tools
docker-compose exec dashboard bash
```

### Staging Environment

#### Configuration
```yaml
# docker-compose.staging.yml
version: '3.8'
services:
  dashboard:
    environment:
      - FLASK_ENV=staging
      - FLASK_DEBUG=false
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M
```

#### Commands
```bash
# Deploy to staging
docker-compose -f docker-compose.yml -f docker-compose.staging.yml up -d

# Run staging tests
./scripts/test-staging.sh

# Monitor staging deployment
docker-compose -f docker-compose.yml -f docker-compose.staging.yml logs -f
```

### Production Environment

#### Configuration
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  dashboard:
    environment:
      - FLASK_ENV=production
      - FLASK_DEBUG=false
    deploy:
      replicas: 3
      resources:
        limits:
          memory: 1G
          cpus: '1.0'
        reservations:
          memory: 512M
          cpus: '0.5'
    restart: unless-stopped
```

#### Commands
```bash
# Deploy to production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Enable monitoring
docker-compose --profile monitoring up -d

# Backup before deployment
./scripts/backup.sh --full

# Health check
./scripts/health-check.sh --production
```

## 🔧 Configuration Management

### Environment Variables

#### Required Variables
```env
# Application Configuration
FLASK_SECRET_KEY=your-super-secret-key-here
FLASK_ENV=production
FLASK_DEBUG=false

# Database Configuration
DATABASE_URL=postgresql://dashboard_user:strong_password@postgres:5432/dashboard
REDIS_URL=redis://redis:6379/0

# Docker Configuration
DOCKER_HOST=unix:///var/run/docker.sock

# Security Configuration
JWT_SECRET_KEY=your-jwt-secret-key
CORS_ORIGINS=https://yourdomain.com
```

#### Optional Variables
```env
# Monitoring Configuration
PROMETHEUS_URL=http://prometheus:9090
GRAFANA_URL=http://grafana:3000
GRAFANA_ADMIN_PASSWORD=secure_admin_password

# Email Configuration (for alerts)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Backup Configuration
BACKUP_SCHEDULE=0 2 * * *  # Daily at 2 AM
BACKUP_RETENTION_DAYS=30
S3_BACKUP_BUCKET=your-backup-bucket
```

### SSL/HTTPS Configuration

#### Generate SSL Certificates
```bash
# Using Let's Encrypt (recommended for production)
sudo apt install certbot
sudo certbot certonly --standalone -d yourdomain.com

# Using self-signed certificates (development only)
mkdir -p ssl
openssl req -x509 -newkey rsa:4096 -keyout ssl/key.pem -out ssl/cert.pem -days 365 -nodes
```

#### Configure Nginx for HTTPS
```nginx
# nginx-ssl.conf
server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /etc/ssl/certs/cert.pem;
    ssl_certificate_key /etc/ssl/private/key.pem;
    
    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    
    location / {
        proxy_pass http://dashboard:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 📊 Monitoring Setup

### Prometheus Configuration
```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'dashboard'
    static_configs:
      - targets: ['dashboard:5000']
    metrics_path: '/api/metrics'
    scrape_interval: 10s

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']

  - job_name: 'postgres-exporter'
    static_configs:
      - targets: ['postgres-exporter:9187']
```

### Grafana Dashboard Import
```bash
# Import pre-configured dashboards
curl -X POST \
  http://admin:admin@localhost:3000/api/dashboards/db \
  -H 'Content-Type: application/json' \
  -d @grafana/dashboard.json
```

### Alerting Rules
```yaml
# alerts.yml
groups:
  - name: dashboard_alerts
    rules:
      - alert: HighCPUUsage
        expr: cpu_usage_percent > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage detected"
          
      - alert: DatabaseDown
        expr: up{job="postgres-exporter"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Database is down"
```

## 🔄 CI/CD Integration

### GitHub Actions Setup

#### 1. Repository Secrets
```bash
# Add these secrets to your GitHub repository:
DOCKER_USERNAME=your-docker-username
DOCKER_PASSWORD=your-docker-password
PRODUCTION_HOST=your-production-server
PRODUCTION_USER=deploy-user
PRODUCTION_SSH_KEY=your-private-ssh-key
DATABASE_URL=your-production-database-url
```

#### 2. Workflow Configuration
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to production
        uses: appleboy/ssh-action@v0.1.5
        with:
          host: ${{ secrets.PRODUCTION_HOST }}
          username: ${{ secrets.PRODUCTION_USER }}
          key: ${{ secrets.PRODUCTION_SSH_KEY }}
          script: |
            cd /opt/dashboard
            git pull origin main
            docker-compose down
            docker-compose --profile production up -d
            ./scripts/health-check.sh --production
```

### GitLab CI/CD Setup
```yaml
# .gitlab-ci.yml
stages:
  - test
  - build
  - deploy

variables:
  DOCKER_DRIVER: overlay2

test:
  stage: test
  script:
    - python -m pytest tests/

build:
  stage: build
  script:
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA

deploy_production:
  stage: deploy
  script:
    - ssh deploy@$PRODUCTION_HOST "cd /opt/dashboard && ./scripts/deploy.sh --production"
  only:
    - main
```

## 🛠️ Maintenance & Operations

### Backup Procedures

#### Database Backup
```bash
# Manual backup
docker-compose exec postgres pg_dump -U dashboard_user dashboard > backup_$(date +%Y%m%d_%H%M%S).sql

# Automated backup script
#!/bin/bash
BACKUP_DIR="/opt/backups"
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec postgres pg_dump -U dashboard_user dashboard | gzip > $BACKUP_DIR/dashboard_$DATE.sql.gz

# Cleanup old backups (keep last 30 days)
find $BACKUP_DIR -name "dashboard_*.sql.gz" -mtime +30 -delete
```

#### Application Backup
```bash
# Backup application data
tar -czf dashboard_backup_$(date +%Y%m%d).tar.gz \
  docker-compose.yml \
  .env \
  nginx.conf \
  prometheus.yml \
  logs/ \
  data/
```

### Log Management

#### Log Rotation
```bash
# Configure logrotate
sudo tee /etc/logrotate.d/dashboard << EOF
/opt/dashboard/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 root root
    postrotate
        docker-compose restart dashboard
    endscript
}
EOF
```

#### Centralized Logging
```yaml
# docker-compose.logging.yml
version: '3.8'
services:
  dashboard:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
        
  elasticsearch:
    image: elasticsearch:7.17.0
    environment:
      - discovery.type=single-node
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data
      
  kibana:
    image: kibana:7.17.0
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch
```

### Performance Tuning

#### Database Optimization
```sql
-- PostgreSQL performance tuning
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
SELECT pg_reload_conf();
```

#### Application Optimization
```python
# app/config.py
class ProductionConfig:
    # Database connection pooling
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 20,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'max_overflow': 30
    }
    
    # Redis configuration
    REDIS_CONFIG = {
        'connection_pool_kwargs': {
            'max_connections': 50,
            'retry_on_timeout': True
        }
    }
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Container Won't Start
```bash
# Check container logs
docker-compose logs dashboard

# Check resource usage
docker stats

# Verify port availability
netstat -tulpn | grep :5000

# Solution: Usually port conflict or resource constraints
docker-compose down
docker system prune -f
docker-compose up -d
```

#### 2. Database Connection Failed
```bash
# Check PostgreSQL status
docker-compose ps postgres

# Test database connection
docker-compose exec postgres psql -U dashboard_user -d dashboard

# Check network connectivity
docker-compose exec dashboard ping postgres

# Solution: Verify credentials and network
docker-compose down
docker volume rm dashboard_postgres_data
docker-compose up -d
```

#### 3. High Memory Usage
```bash
# Check memory usage
docker stats --no-stream

# Identify memory leaks
docker-compose exec dashboard python -c "
import psutil
print(f'Memory: {psutil.virtual_memory().percent}%')
print(f'CPU: {psutil.cpu_percent()}%')
"

# Solution: Restart services or increase resources
docker-compose restart
# Or update docker-compose.yml with higher memory limits
```

#### 4. SSL Certificate Issues
```bash
# Check certificate validity
openssl x509 -in ssl/cert.pem -text -noout

# Verify certificate chain
openssl verify -CAfile ssl/ca.pem ssl/cert.pem

# Renew Let's Encrypt certificate
sudo certbot renew --dry-run
sudo certbot renew
```

### Health Check Commands
```bash
# Quick health check
curl -f http://localhost:5000/api/health-check || echo "Health check failed"

# Comprehensive system check
./scripts/health-check.sh --full --verbose

# Monitor continuously
watch -n 30 './scripts/health-check.sh --quick'
```

### Recovery Procedures

#### Application Recovery
```bash
# Stop all services
docker-compose down

# Clean up resources
docker system prune -f
docker volume prune -f

# Restore from backup
tar -xzf dashboard_backup_latest.tar.gz

# Restart services
docker-compose up -d

# Verify recovery
./scripts/health-check.sh --full
```

#### Database Recovery
```bash
# Stop application
docker-compose stop dashboard

# Restore database
gunzip -c backup_latest.sql.gz | docker-compose exec -T postgres psql -U dashboard_user -d dashboard

# Restart application
docker-compose start dashboard

# Verify data integrity
docker-compose exec postgres psql -U dashboard_user -d dashboard -c "SELECT COUNT(*) FROM deployments;"
```

## 📞 Support & Maintenance

### Monitoring Checklist
- [ ] Application health endpoints responding
- [ ] Database connectivity and performance
- [ ] Container resource usage within limits
- [ ] Log files not growing excessively
- [ ] SSL certificates not expiring soon
- [ ] Backup processes running successfully
- [ ] Security updates applied

### Regular Maintenance Tasks

#### Daily
- Check application health status
- Review error logs
- Monitor resource usage
- Verify backup completion

#### Weekly
- Update security patches
- Review performance metrics
- Clean up old logs and backups
- Test disaster recovery procedures

#### Monthly
- Update dependencies
- Review and update documentation
- Performance optimization review
- Security audit and penetration testing

### Emergency Contacts
- **System Administrator**: admin@company.com
- **DevOps Team**: devops@company.com
- **On-call Engineer**: +1-555-0123
- **Escalation Manager**: manager@company.com

---

For additional support, please refer to the main [README.md](README.md) or create an issue in the project repository.