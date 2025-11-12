# Daur-AI v2.0 - Docker Deployment Guide

## Quick Start (5 minutes)

### 1. Build Docker Image

```bash
# Navigate to project directory
cd /home/ubuntu/Daur-AI-v1

# Build Docker image
docker build -t daur-ai:latest .

# Verify image was created
docker images | grep daur-ai
```

### 2. Run Container

```bash
# Simple run (development)
docker run -p 5000:5000 daur-ai:latest

# Run with volumes (production)
docker run -d \
  --name daur-ai-container \
  -p 5000:5000 \
  -p 8000:8000 \
  -p 9090:9090 \
  -v /data:/app/data \
  -v /logs:/app/logs \
  -e FLASK_ENV=production \
  daur-ai:latest

# Check logs
docker logs -f daur-ai-container
```

### 3. Access Services

- **API Server:** http://localhost:5000
- **Health Check:** http://localhost:5000/api/v2/health
- **Prometheus:** http://localhost:9090

---

## Full Stack Deployment (Docker Compose)

### 1. Start Full Stack

```bash
# Start all services
docker-compose up -d

# View services
docker-compose ps

# View logs
docker-compose logs -f api
```

### 2. Services Included

| Service | Port | Purpose |
|---------|------|---------|
| API | 5000 | Daur-AI REST API |
| PostgreSQL | 5432 | Database |
| Redis | 6379 | Caching |
| Prometheus | 9090 | Metrics |
| Grafana | 3000 | Dashboards |
| Nginx | 80/443 | Reverse Proxy |

### 3. Access Services

```bash
# API
curl http://localhost:5000/api/v2/health

# Grafana (admin/admin)
http://localhost:3000

# Prometheus
http://localhost:9090
```

### 4. Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

---

## Production Deployment

### 1. Prepare Environment

```bash
# Create .env file
cat > .env << EOF
DATABASE_URL=postgresql://daur:password@postgres:5432/daur_ai
REDIS_URL=redis://redis:6379
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
EOF

# Create directories
mkdir -p data logs ssl
```

### 2. Configure SSL/TLS

```bash
# Generate self-signed certificate
openssl req -x509 -newkey rsa:4096 -nodes \
  -out ssl/cert.pem -keyout ssl/key.pem -days 365

# Or use Let's Encrypt
certbot certonly --standalone -d your-domain.com
```

### 3. Configure Nginx

```bash
cat > nginx.conf << 'EOF'
upstream daur_api {
    server api:5000;
}

server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://daur_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
EOF
```

### 4. Deploy

```bash
# Build and start
docker-compose -f docker-compose.yml up -d

# Verify all services are running
docker-compose ps

# Check health
curl http://localhost/api/v2/health
```

---

## Monitoring & Maintenance

### 1. View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api

# Last 100 lines
docker-compose logs --tail=100 api
```

### 2. Database Backup

```bash
# Backup PostgreSQL
docker exec daur-ai-postgres pg_dump -U daur daur_ai > backup.sql

# Restore
docker exec -i daur-ai-postgres psql -U daur daur_ai < backup.sql
```

### 3. Monitor Resources

```bash
# CPU, Memory, Network
docker stats daur-ai-api

# Detailed info
docker inspect daur-ai-api
```

### 4. Update Application

```bash
# Rebuild image
docker-compose build --no-cache

# Restart services
docker-compose up -d

# Verify
docker-compose ps
```

---

## Troubleshooting

### Port Already in Use

```bash
# Find process using port
lsof -i :5000

# Kill process
kill -9 <PID>

# Or use different port
docker run -p 5001:5000 daur-ai:latest
```

### Container Won't Start

```bash
# Check logs
docker logs daur-ai-container

# Check image
docker inspect daur-ai:latest

# Rebuild
docker build --no-cache -t daur-ai:latest .
```

### Database Connection Error

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check connection
docker exec daur-ai-postgres psql -U daur -d daur_ai -c "SELECT 1"

# Restart database
docker-compose restart postgres
```

### Out of Disk Space

```bash
# Clean up unused images
docker image prune -a

# Clean up volumes
docker volume prune

# Check disk usage
docker system df
```

---

## Performance Optimization

### 1. Resource Limits

```yaml
# In docker-compose.yml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

### 2. Caching Strategy

```bash
# Enable Redis caching
docker-compose up -d redis

# Configure in app
export REDIS_URL=redis://redis:6379
```

### 3. Database Optimization

```bash
# Create indexes
docker exec daur-ai-postgres psql -U daur daur_ai << EOF
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_logs_timestamp ON logs(timestamp);
EOF
```

---

## Security Best Practices

### 1. Use Secrets

```bash
# Create secret file
echo "your-secret-key" | docker secret create api_secret -

# Use in compose
secrets:
  api_secret:
    external: true
```

### 2. Network Isolation

```bash
# Use custom network
docker network create daur-network
docker-compose --network daur-network up -d
```

### 3. Image Scanning

```bash
# Scan for vulnerabilities
docker scan daur-ai:latest

# Use minimal base image
# FROM python:3.11-slim  (already done)
```

### 4. Access Control

```bash
# Restrict ports
docker run -p 127.0.0.1:5000:5000 daur-ai:latest

# Use firewall
ufw allow 5000/tcp
```

---

## Deployment to Cloud

### AWS ECS

```bash
# Push to ECR
aws ecr get-login-password | docker login --username AWS --password-stdin <account>.dkr.ecr.<region>.amazonaws.com
docker tag daur-ai:latest <account>.dkr.ecr.<region>.amazonaws.com/daur-ai:latest
docker push <account>.dkr.ecr.<region>.amazonaws.com/daur-ai:latest
```

### Google Cloud Run

```bash
# Build and push
gcloud builds submit --tag gcr.io/<project>/daur-ai

# Deploy
gcloud run deploy daur-ai --image gcr.io/<project>/daur-ai --platform managed
```

### Azure Container Instances

```bash
# Build and push
az acr build --registry <registry> --image daur-ai:latest .

# Deploy
az container create --resource-group <group> --name daur-ai --image <registry>.azurecr.io/daur-ai:latest
```

---

## Monitoring with Prometheus & Grafana

### 1. Configure Prometheus

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'daur-ai'
    static_configs:
      - targets: ['api:5000']
```

### 2. Add Grafana Dashboard

```bash
# Access Grafana
http://localhost:3000

# Login: admin/admin
# Add Prometheus data source: http://prometheus:9090
# Import dashboard
```

---

## Summary

✅ **Docker Image:** Single file with all dependencies  
✅ **Docker Compose:** Full stack with all services  
✅ **Production Ready:** SSL, monitoring, backups  
✅ **Scalable:** Easy to scale with orchestration  
✅ **Secure:** Best practices implemented  

**Your Daur-AI v2.0 is now ready for production deployment!**

---

## Quick Commands Reference

```bash
# Build
docker build -t daur-ai:latest .

# Run
docker run -p 5000:5000 daur-ai:latest

# Compose
docker-compose up -d
docker-compose down

# Logs
docker logs -f <container>
docker-compose logs -f

# Exec
docker exec -it <container> bash
docker-compose exec api bash

# Clean
docker system prune -a
docker volume prune
```

---

*Last Updated: October 25, 2025*
*Daur-AI v2.0 - Production Ready*

