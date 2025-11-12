# Daur-AI v2.0 - Docker Quick Start Guide

## 🚀 Build and Run in 5 Minutes

### Step 1: Build Docker Image

```bash
# Navigate to project directory
cd /home/ubuntu/Daur-AI-v1

# Option A: Using build script (recommended)
./build-docker.sh daur-ai latest

# Option B: Using docker build directly
docker build -t daur-ai:latest .
```

### Step 2: Run Container

```bash
# Simple run (development)
docker run -p 5000:5000 daur-ai:latest

# Or run in background
docker run -d -p 5000:5000 --name daur-ai daur-ai:latest

# Check logs
docker logs -f daur-ai
```

### Step 3: Test API

```bash
# Health check
curl http://localhost:5000/api/v2/health

# Get hardware status
curl http://localhost:5000/api/v2/status
```

---

## 🐳 Full Stack with Docker Compose

### Step 1: Start All Services

```bash
# Start the full stack
docker-compose up -d

# View all services
docker-compose ps
```

### Step 2: Access Services

| Service | URL | Credentials |
|---------|-----|-------------|
| API | http://localhost:5000 | - |
| Grafana | http://localhost:3000 | admin/admin |
| Prometheus | http://localhost:9090 | - |
| PostgreSQL | localhost:5432 | daur/daur_secure_password_123 |
| Redis | localhost:6379 | - |

### Step 3: Test Full Stack

```bash
# API health
curl http://localhost:5000/api/v2/health

# Database connection
docker-compose exec postgres psql -U daur -d daur_ai -c "SELECT 1"

# Redis connection
docker-compose exec redis redis-cli ping

# View logs
docker-compose logs -f api
```

### Step 4: Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

---

## 📦 What's Included

### Single Container (daur-ai:latest)
- Python 3.11 runtime
- All Python dependencies
- Daur-AI v2.0 application
- REST API server
- All 19 modules (input, vision, hardware, security, etc.)

### Full Stack (docker-compose)
- **API Container** - Daur-AI application
- **PostgreSQL** - Production database
- **Redis** - Caching layer
- **Prometheus** - Metrics collection
- **Grafana** - Visualization dashboards
- **Nginx** - Reverse proxy

---

## 🔧 Common Commands

### Build
```bash
# Build image
docker build -t daur-ai:latest .

# Build without cache
docker build --no-cache -t daur-ai:latest .

# Build with build script
./build-docker.sh daur-ai latest
```

### Run
```bash
# Run container
docker run -p 5000:5000 daur-ai:latest

# Run with name
docker run -d --name daur-ai -p 5000:5000 daur-ai:latest

# Run with environment variables
docker run -e FLASK_ENV=production -p 5000:5000 daur-ai:latest

# Run with volume mount
docker run -v /data:/app/data -p 5000:5000 daur-ai:latest
```

### Manage
```bash
# List containers
docker ps -a

# Stop container
docker stop daur-ai

# Start container
docker start daur-ai

# Remove container
docker rm daur-ai

# View logs
docker logs -f daur-ai

# Execute command in container
docker exec -it daur-ai bash
```

### Compose
```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Execute command
docker-compose exec api bash

# Rebuild
docker-compose build --no-cache
```

---

## 🐛 Troubleshooting

### Container Won't Start
```bash
# Check logs
docker logs daur-ai

# Check image
docker inspect daur-ai:latest

# Rebuild image
docker build --no-cache -t daur-ai:latest .
```

### Port Already in Use
```bash
# Find process using port
lsof -i :5000

# Kill process
kill -9 <PID>

# Or use different port
docker run -p 5001:5000 daur-ai:latest
```

### API Not Responding
```bash
# Check if container is running
docker ps | grep daur-ai

# Check container health
docker inspect --format='{{.State.Health.Status}}' daur-ai

# Restart container
docker restart daur-ai
```

### Database Connection Error
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check connection
docker-compose exec postgres psql -U daur -d daur_ai -c "SELECT 1"

# View PostgreSQL logs
docker-compose logs postgres
```

---

## 📊 Monitoring

### View Metrics
```bash
# CPU and Memory usage
docker stats daur-ai

# Container info
docker inspect daur-ai

# Network info
docker network inspect daur-network
```

### View Logs
```bash
# All logs
docker logs daur-ai

# Last 100 lines
docker logs --tail=100 daur-ai

# Follow logs
docker logs -f daur-ai

# With timestamps
docker logs -t daur-ai
```

### Health Check
```bash
# API health
curl http://localhost:5000/api/v2/health

# Database health
docker-compose exec postgres pg_isready -U daur

# Redis health
docker-compose exec redis redis-cli ping
```

---

## 🔐 Security

### Run as Non-Root
```bash
# Already configured in Dockerfile
# Container runs as 'daur' user (UID 1000)
docker run daur-ai:latest
```

### Use Environment Variables
```bash
# Create .env file
cat > .env << EOF
DATABASE_URL=postgresql://daur:password@postgres:5432/daur_ai
REDIS_URL=redis://redis:6379
FLASK_ENV=production
EOF

# Use in docker-compose
docker-compose --env-file .env up -d
```

### Network Isolation
```bash
# Create custom network
docker network create daur-network

# Run on custom network
docker run --network daur-network -p 5000:5000 daur-ai:latest
```

---

## 📈 Performance

### Resource Limits
```bash
# Run with memory limit
docker run -m 2g -p 5000:5000 daur-ai:latest

# Run with CPU limit
docker run --cpus 2 -p 5000:5000 daur-ai:latest

# Both limits
docker run -m 2g --cpus 2 -p 5000:5000 daur-ai:latest
```

### Optimize Image Size
```bash
# Current image size
docker images daur-ai

# Use multi-stage build (already in Dockerfile)
# Reduces image size significantly
```

---

## 🚢 Production Deployment

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
gcloud run deploy daur-ai --image gcr.io/<project>/daur-ai
```

### Docker Hub
```bash
# Tag image
docker tag daur-ai:latest <username>/daur-ai:latest

# Login to Docker Hub
docker login

# Push
docker push <username>/daur-ai:latest
```

---

## ✅ Verification Checklist

After starting the container, verify:

- [ ] Container is running: `docker ps | grep daur-ai`
- [ ] API is responding: `curl http://localhost:5000/api/v2/health`
- [ ] Database is connected: `docker-compose exec postgres psql -U daur -d daur_ai -c "SELECT 1"`
- [ ] Redis is working: `docker-compose exec redis redis-cli ping`
- [ ] Logs show no errors: `docker logs daur-ai`
- [ ] All services are healthy: `docker-compose ps`

---

## 📚 Additional Resources

- **Dockerfile:** `/home/ubuntu/Daur-AI-v1/Dockerfile`
- **Docker Compose:** `/home/ubuntu/Daur-AI-v1/docker-compose.yml`
- **Full Guide:** `/home/ubuntu/Daur-AI-v1/DOCKER_DEPLOYMENT_GUIDE.md`
- **Build Script:** `/home/ubuntu/Daur-AI-v1/build-docker.sh`

---

## 🎉 You're Ready!

Your Daur-AI v2.0 is now containerized and ready for deployment!

**Next Steps:**
1. Build the image: `./build-docker.sh`
2. Run the container: `docker run -p 5000:5000 daur-ai:latest`
3. Access the API: `http://localhost:5000`
4. Deploy to production: Use `docker-compose up -d`

---

*Last Updated: October 25, 2025*
*Daur-AI v2.0 - Production Ready*

