# Cloud Deployment Automation Dashboard

A comprehensive DevOps dashboard for automating cloud deployments with real-time monitoring, health checks, and container management capabilities.

## 🚀 Features

### Core Functionality
- **Deployment Automation**: Deploy, manage, and monitor containerized applications
- **Real-time Monitoring**: Live system metrics, resource usage, and performance tracking
- **Health Checks**: Comprehensive system health monitoring with automated alerts
- **Container Management**: Docker container lifecycle management and statistics
- **Log Streaming**: Real-time log viewing and historical log analysis
- **Multi-environment Support**: Development, staging, and production environments

### Technical Capabilities
- **RESTful API**: Complete API for all dashboard operations
- **WebSocket Integration**: Real-time updates and live data streaming
- **Database Integration**: PostgreSQL for persistent data storage
- **Caching Layer**: Redis for improved performance
- **Reverse Proxy**: Nginx for load balancing and SSL termination
- **Monitoring Stack**: Prometheus and Grafana integration
- **CI/CD Pipeline**: GitHub Actions for automated testing and deployment

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Database      │
│   (Bootstrap)   │◄──►│   (Flask)       │◄──►│   (PostgreSQL)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         └──────────────►│     Redis       │◄─────────────┘
                        │   (Caching)     │
                        └─────────────────┘
                                 │
                        ┌─────────────────┐
                        │     Nginx       │
                        │ (Reverse Proxy) │
                        └─────────────────┘
```

## 📋 Prerequisites

- **Python 3.13+**
- **Docker & Docker Compose**
- **Git**
- **Node.js** (for development)

## 🛠️ Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd cloud-deployment-dashboard
```

### 2. Environment Setup

#### Option A: Local Development
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

#### Option B: Docker Development

##### 🐳 **Temel Geliştirme Ortamı**
```bash
# Sadece temel servisler (Flask + Redis + PostgreSQL)
docker-compose up dashboard redis postgres

# Arka planda çalıştır
docker-compose up -d dashboard redis postgres

# Logları takip et
docker-compose logs -f dashboard
```

##### 🌐 **Production Simülasyonu (Nginx ile)**
```bash
# Nginx reverse proxy ile
docker-compose --profile production up

# Arka planda çalıştır
docker-compose --profile production up -d

# Nginx logları
docker-compose logs -f nginx
```

##### 📊 **Monitoring Stack (Prometheus + Grafana)**
```bash
# Monitoring servisleri ekle
docker-compose --profile monitoring up

# Sadece monitoring servislerini başlat
docker-compose up prometheus grafana

# Monitoring logları
docker-compose logs -f prometheus grafana
```

##### 🚀 **Tam Production Ortamı**
```bash
# Tüm servisler (Nginx + Monitoring)
docker-compose --profile production --profile monitoring up

# Arka planda tam stack
docker-compose --profile production --profile monitoring up -d

# Tüm servisleri yeniden başlat
docker-compose --profile production --profile monitoring restart

# Belirli servisi yeniden başlat
docker-compose restart dashboard
```

##### 🔧 **Geliştirme Komutları**
```bash
# Servisleri durdur
docker-compose down

# Volumes ile birlikte temizle
docker-compose down -v

# Images ile birlikte temizle
docker-compose down --rmi all

# Yeniden build et
docker-compose build --no-cache

# Belirli servisi build et
docker-compose build dashboard

# Container'a bağlan
docker-compose exec dashboard bash
docker-compose exec postgres psql -U dashboard_user -d dashboard
docker-compose exec redis redis-cli
```

### 3. Production Deployment

#### 🌐 **Google Cloud Platform (GCP)**
```bash
# GCP'ye deploy et (GitHub Actions ile otomatik)
git add .
git commit -m "Deploy to GCP"
git push origin main

# Manuel GCP deployment
gcloud run deploy dashboard \
  --image gcr.io/PROJECT_ID/dashboard:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

# GCP logs
gcloud logs tail --service=dashboard
```

#### 🐳 **Local Production Test**
```bash
# Production ortamını test et
docker-compose --profile production --profile monitoring up -d

# Health check
curl http://localhost/api/health-check

# Monitoring check
curl http://localhost:9090/api/v1/query?query=up
```

## 🔧 Configuration

### 🔑 **Environment Variables**
`.env` dosyasını oluşturun:

```env
# Flask Configuration
FLASK_ENV=production
FLASK_SECRET_KEY=your-super-secret-key-here
FLASK_DEBUG=False

# Supabase Configuration (Gerekli!)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# Database Configuration
DATABASE_URL=postgresql://dashboard_user:dashboard_password@postgres:5432/dashboard
REDIS_URL=redis://redis:6379/0

# Docker Configuration
DOCKER_HOST=unix:///var/run/docker.sock

# Monitoring Configuration
PROMETHEUS_URL=http://prometheus:9090
GRAFANA_URL=http://grafana:3000

# Telegram Bot Configuration (Opsiyonel)
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_CHAT_ID=your-chat-id

# GCP Configuration (Production için)
GOOGLE_CLOUD_PROJECT_ID=your-project-id
GOOGLE_CLOUD_SA_KEY=base64-encoded-service-account-key

# Security Configuration
JWT_SECRET_KEY=your-jwt-secret-here
CORS_ORIGINS=http://localhost:3000,http://localhost:5000,http://localhost:80
```

### 📋 **Hızlı Kurulum Checklist**
```bash
# 1. Environment dosyasını kopyala
cp .env.example .env

# 2. Supabase bilgilerini ekle (.env dosyasına)
# SUPABASE_URL=https://your-project.supabase.co
# SUPABASE_ANON_KEY=your-anon-key

# 3. Temel stack'i başlat
docker-compose up dashboard redis postgres

# 4. Tarayıcıda test et
# http://localhost:5000

# 5. Production test (Nginx + Monitoring)
docker-compose --profile production --profile monitoring up -d
```

### Database Setup
The database is automatically initialized with sample data when using Docker Compose. For manual setup:

```bash
# Connect to PostgreSQL
psql -h localhost -U dashboard_user -d dashboard

# Run initialization script
\i init.sql
```

## 📊 Usage

### 🌐 **Dashboard Access**

#### 🐳 **Temel Stack** (`docker-compose up dashboard redis postgres`)
- **Ana Dashboard**: http://localhost:5000
- **API Dokümantasyonu**: http://localhost:5000/api/docs
- **Health Check**: http://localhost:5000/api/health-check
- **Database**: PostgreSQL (localhost:5432)
- **Cache**: Redis (localhost:6379)

#### 🌐 **Production Stack** (`--profile production`)
- **Nginx (Ana Giriş)**: http://localhost:80
- **Dashboard (Direkt)**: http://localhost:5000
- **SSL Termination**: Nginx üzerinden
- **Load Balancing**: Nginx reverse proxy

#### 📊 **Monitoring Stack** (`--profile monitoring`)
- **Grafana Dashboard**: http://localhost:3000 (admin/admin)
- **Prometheus Metrics**: http://localhost:9090
- **Prometheus Targets**: http://localhost:9090/targets
- **Grafana Datasources**: Prometheus otomatik bağlı

#### 🚀 **Tam Stack** (`--profile production --profile monitoring`)
- **Ana Giriş**: http://localhost:80 (Nginx)
- **Monitoring**: http://localhost:3000 (Grafana)
- **Metrics**: http://localhost:9090 (Prometheus)
- **API**: http://localhost:80/api/ (Nginx üzerinden)

### 🔍 **Health Check Endpoints**
```bash
# Temel health check
curl http://localhost:5000/api/health-check

# Nginx üzerinden
curl http://localhost:80/api/health-check

# Detaylı sistem bilgisi
curl http://localhost:5000/api/system-info

# Database bağlantı testi
curl http://localhost:5000/api/db-health
```

### API Endpoints

#### Deployment Management
```bash
# Deploy a new container
POST /api/deploy
{
  "action": "deploy",
  "image": "nginx:latest",
  "environment": "development",
  "port_mapping": "80:8080",
  "env_vars": {"ENV": "dev"}
}

# Get deployment status
GET /api/deployment-status/{job_id}

# Get deployment history
GET /api/deployments

# Rerun deployment
POST /api/deployments/{job_id}/rerun
```

#### Monitoring & Health
```bash
# System status
GET /api/status

# Health check
GET /api/health-check
POST /api/health-check

# Container information
GET /api/containers

# System metrics
GET /api/deployment-metrics
```

#### Logs & Streaming
```bash
# Get logs
GET /api/logs
GET /api/logs/{job_id}

# Stream logs (WebSocket)
WS /socket.io/
```

### Automation Scripts

#### Deployment Script
```bash
# Basic deployment
./scripts/deploy.sh

# Build and deploy
./scripts/deploy.sh --build

# Production deployment
./scripts/deploy.sh --production

# Clean deployment
./scripts/deploy.sh --clean --build
```

#### Health Check Script
```bash
# Quick health check
./scripts/health-check.sh --quick

# Full health check
./scripts/health-check.sh --full

# Continuous monitoring
./scripts/health-check.sh --continuous
```

## 🧪 Testing

### Unit Tests
```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=app

# Run specific test file
python -m pytest tests/test_deployment_service.py
```

### API Testing
```bash
# Test API endpoints
curl -X GET http://localhost:5000/api/status
curl -X POST http://localhost:5000/api/health-check

# Load testing
ab -n 1000 -c 10 http://localhost:5000/api/status
```

### Integration Tests
```bash
# Test Docker deployment
docker-compose -f docker-compose.test.yml up --abort-on-container-exit

# Test health checks
./scripts/health-check.sh --full
```

## 🔍 Monitoring & Observability

### Metrics Collection
- **System Metrics**: CPU, Memory, Disk, Network usage
- **Application Metrics**: Request rates, response times, error rates
- **Container Metrics**: Container status, resource usage, logs
- **Business Metrics**: Deployment success rates, failure analysis

### Alerting
- **Health Check Failures**: Automatic alerts for system issues
- **Resource Thresholds**: CPU/Memory usage alerts
- **Deployment Failures**: Failed deployment notifications
- **Performance Degradation**: Response time and error rate alerts

### Dashboards
- **System Overview**: Real-time system health and metrics
- **Deployment Tracking**: Deployment history and success rates
- **Container Management**: Container status and resource usage
- **Log Analysis**: Centralized log viewing and search

## 🚀 CI/CD Pipeline

### GitHub Actions Workflow
The project includes a comprehensive CI/CD pipeline:

1. **Code Quality**: Linting, formatting, and security checks
2. **Testing**: Unit tests, integration tests, and coverage reports
3. **Building**: Docker image building and pushing
4. **Deployment**: Automated deployment to staging/production
5. **Monitoring**: Post-deployment health checks and performance tests

### Pipeline Stages
```yaml
# .github/workflows/ci-cd.yml
- Code Quality & Testing (Python 3.11, 3.12, 3.13)
- Security Scanning (Trivy, Bandit)
- Docker Build & Push
- Deploy to Staging
- Deploy to Production
- Performance Testing
- Cleanup
```

## 🔒 Security

### Security Features
- **Input Validation**: All API inputs are validated and sanitized
- **Authentication**: JWT-based authentication (ready for implementation)
- **Authorization**: Role-based access control
- **HTTPS**: SSL/TLS encryption for all communications
- **Container Security**: Non-root user, minimal base images
- **Network Security**: Isolated Docker networks, firewall rules

### Security Best Practices
- Regular security updates and vulnerability scanning
- Secrets management with environment variables
- Rate limiting and DDoS protection
- Audit logging for all operations
- Secure Docker socket access

## 🔧 **Troubleshooting**

### 🐳 **Docker Sorunları**
```bash
# Container'lar çalışıyor mu?
docker-compose ps

# Logları kontrol et
docker-compose logs dashboard
docker-compose logs nginx
docker-compose logs postgres

# Container'a bağlan ve debug et
docker-compose exec dashboard bash
docker-compose exec postgres psql -U dashboard_user -d dashboard

# Port çakışması
netstat -tulpn | grep :5000
netstat -tulpn | grep :80

# Docker temizliği
docker system prune -a
docker volume prune
```

### 🌐 **Network Sorunları**
```bash
# Nginx konfigürasyonu test et
docker-compose exec nginx nginx -t

# Network bağlantısı test et
docker-compose exec dashboard ping postgres
docker-compose exec dashboard ping redis

# Port erişimi test et
curl -I http://localhost:5000/api/health-check
curl -I http://localhost:80/api/health-check
```

### 📊 **Database Sorunları**
```bash
# PostgreSQL bağlantısı test et
docker-compose exec postgres pg_isready -U dashboard_user

# Database'e bağlan
docker-compose exec postgres psql -U dashboard_user -d dashboard

# Redis bağlantısı test et
docker-compose exec redis redis-cli ping

# Database migration
docker-compose exec dashboard python -c "from app import db; db.create_all()"
```

### 🔍 **Monitoring Sorunları**
```bash
# Prometheus targets kontrol et
curl http://localhost:9090/api/v1/targets

# Grafana datasource test et
curl http://localhost:3000/api/health

# Metrics endpoint test et
curl http://localhost:5000/metrics
```

### ⚡ **Performance Sorunları**
```bash
# Container resource kullanımı
docker stats

# Disk kullanımı
docker system df

# Memory kullanımı
docker-compose exec dashboard free -h

# CPU kullanımı
docker-compose exec dashboard top
```

### 🚨 **Yaygın Hatalar ve Çözümleri**

#### Port 5000 zaten kullanımda
```bash
# Çakışan process'i bul
netstat -tulpn | grep :5000
# veya
lsof -i :5000

# Process'i sonlandır
kill -9 <PID>
```

#### Database bağlantı hatası
```bash
# PostgreSQL servisini yeniden başlat
docker-compose restart postgres

# Database'i yeniden oluştur
docker-compose down -v
docker-compose up postgres
```

#### Nginx 502 Bad Gateway
```bash
# Dashboard servisinin çalıştığını kontrol et
docker-compose ps dashboard

# Nginx konfigürasyonunu test et
docker-compose exec nginx nginx -t

# Nginx'i yeniden başlat
docker-compose restart nginx
```

## 📈 Performance

### Optimization Features
- **Caching**: Redis caching for frequently accessed data
- **Database Optimization**: Indexed queries and connection pooling
- **Static File Serving**: Nginx for efficient static content delivery
- **Compression**: Gzip compression for reduced bandwidth
- **Load Balancing**: Nginx upstream configuration

### Performance Metrics
- **Response Times**: < 200ms for API endpoints
- **Throughput**: 1000+ requests per second
- **Resource Usage**: < 512MB RAM, < 50% CPU
- **Availability**: 99.9% uptime target

## 🛠️ Development

### Project Structure
```
cloud-deployment-dashboard/
├── app/                    # Flask application
│   ├── __init__.py        # App factory
│   ├── routes.py          # API routes
│   ├── models/            # Data models
│   ├── services/          # Business logic
│   ├── static/            # Static files (CSS, JS)
│   └── templates/         # HTML templates
├── scripts/               # Automation scripts
│   ├── deploy.sh         # Deployment script
│   └── health-check.sh   # Health check script
├── tests/                 # Test files
├── .github/workflows/     # CI/CD pipelines
├── docker-compose.yml     # Docker services
├── Dockerfile            # Application container
├── requirements.txt      # Python dependencies
├── nginx.conf           # Nginx configuration
├── prometheus.yml       # Monitoring configuration
└── init.sql            # Database initialization
```

### Development Workflow
1. **Feature Development**: Create feature branch from `develop`
2. **Testing**: Run local tests and ensure all pass
3. **Code Review**: Submit pull request for review
4. **Integration**: Merge to `develop` branch
5. **Staging**: Deploy to staging environment
6. **Production**: Merge to `main` for production deployment

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📚 Documentation

### API Documentation
- **OpenAPI/Swagger**: Available at `/api/docs`
- **Postman Collection**: Import from `docs/postman_collection.json`
- **API Reference**: Detailed endpoint documentation

### Architecture Documentation
- **System Design**: High-level architecture overview
- **Database Schema**: Entity relationship diagrams
- **Deployment Guide**: Step-by-step deployment instructions
- **Troubleshooting**: Common issues and solutions

## 🐛 Troubleshooting

### Common Issues

#### Application Won't Start
```bash
# Check logs
docker-compose logs dashboard

# Verify dependencies
pip check

# Check port availability
netstat -tulpn | grep :5000
```

#### Database Connection Issues
```bash
# Check PostgreSQL status
docker-compose ps postgres

# Test connection
docker-compose exec postgres psql -U dashboard_user -d dashboard

# Reset database
docker-compose down -v
docker-compose up postgres
```

#### Performance Issues
```bash
# Check resource usage
docker stats

# Monitor application metrics
curl http://localhost:5000/api/status

# Check logs for errors
docker-compose logs -f dashboard
```

### Health Check Commands
```bash
# Quick system check
./scripts/health-check.sh --quick

# Full diagnostic
./scripts/health-check.sh --full --verbose

# Continuous monitoring
./scripts/health-check.sh --continuous --interval 30
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Support

For support and questions:
- **Issues**: GitHub Issues for bug reports and feature requests
- **Documentation**: Check the `/docs` directory for detailed guides
- **Community**: Join our Discord/Slack for discussions

## 🎯 Roadmap

### Upcoming Features
- [ ] Kubernetes integration
- [ ] Multi-cloud support (AWS, Azure, GCP)
- [ ] Advanced alerting and notification system
- [ ] User management and authentication
- [ ] Custom dashboard widgets
- [ ] API rate limiting and quotas
- [ ] Backup and disaster recovery
- [ ] Advanced security features

### Version History
- **v1.0.0**: Initial release with core features
- **v1.1.0**: Added monitoring and health checks
- **v1.2.0**: Docker containerization and CI/CD
- **v1.3.0**: Real-time features and WebSocket support

---

**Built with ❤️ for DevOps automation and cloud deployment management.**