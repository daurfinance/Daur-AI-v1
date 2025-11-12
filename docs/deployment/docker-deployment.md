# Docker Deployment Guide

**Version**: 2.0  
**Last Updated**: 2025-11-12

---

## Overview

This guide covers deploying Daur AI using Docker containers for production environments. Docker provides consistent, isolated environments that simplify deployment and scaling.

---

## Prerequisites

- Docker 20.10 or later
- Docker Compose 1.29 or later
- 4GB RAM minimum
- 10GB disk space

---

## Quick Start

### 1. Build Docker Image

```bash
# Clone repository
git clone https://github.com/daurfinance/Daur-AI-v1.git
cd Daur-AI-v1

# Build image
docker build -t daur-ai:latest .
```

### 2. Run Container

```bash
# Run with default settings
docker run -d \
  --name daur-ai \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -e OPENAI_API_KEY=your_api_key \
  daur-ai:latest

# Check logs
docker logs -f daur-ai
```

---

## Dockerfile

Create `Dockerfile` in project root:

```dockerfile
FROM ubuntu:22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV DISPLAY=:99

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    xvfb \
    scrot \
    tesseract-ocr \
    tesseract-ocr-eng \
    libx11-dev \
    libxtst-dev \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN python3 -m playwright install chromium
RUN python3 -m playwright install-deps

# Copy application code
COPY . .

# Create data directory
RUN mkdir -p /app/data /app/logs

# Expose port
EXPOSE 8000

# Start Xvfb and application
CMD Xvfb :99 -screen 0 1920x1080x24 & \
    python3 -m src.main
```

---

## Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  daur-ai:
    build: .
    container_name: daur-ai
    restart: unless-stopped
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./config:/app/config
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - DAUR_AI_LOG_LEVEL=INFO
      - DISPLAY=:99
    networks:
      - daur-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    image: redis:7-alpine
    container_name: daur-redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    networks:
      - daur-network

  postgres:
    image: postgres:15-alpine
    container_name: daur-postgres
    restart: unless-stopped
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_DB=daur_ai
      - POSTGRES_USER=daur
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - daur-network

networks:
  daur-network:
    driver: bridge

volumes:
  redis-data:
  postgres-data:
```

---

## Environment Variables

Create `.env` file:

```bash
# AI Configuration
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here

# Database
DB_HOST=postgres
DB_PORT=5432
DB_NAME=daur_ai
DB_USER=daur
DB_PASSWORD=your_secure_password

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# Application
DAUR_AI_LOG_LEVEL=INFO
DAUR_AI_HEADLESS=true
DAUR_AI_PORT=8000

# Security
JWT_SECRET=your_jwt_secret_here
ENCRYPTION_KEY=your_encryption_key_here
```

---

## Deployment Commands

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f daur-ai

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up -d --build

# Scale workers
docker-compose up -d --scale daur-ai=3

# Execute command in container
docker-compose exec daur-ai python3 -m src.cli status
```

---

## Production Best Practices

### 1. Resource Limits

```yaml
services:
  daur-ai:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
```

### 2. Health Checks

```python
# src/api/health.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "2.0",
        "timestamp": datetime.now().isoformat()
    }
```

### 3. Logging

```yaml
services:
  daur-ai:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### 4. Security

```dockerfile
# Run as non-root user
RUN useradd -m -u 1000 daur && chown -R daur:daur /app
USER daur
```

---

## Monitoring

### Prometheus Metrics

```yaml
services:
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

---

## Backup and Recovery

```bash
# Backup data
docker run --rm \
  -v daur-ai_postgres-data:/data \
  -v $(pwd)/backups:/backup \
  alpine tar czf /backup/postgres-backup-$(date +%Y%m%d).tar.gz /data

# Restore data
docker run --rm \
  -v daur-ai_postgres-data:/data \
  -v $(pwd)/backups:/backup \
  alpine tar xzf /backup/postgres-backup-20251112.tar.gz -C /
```

---

**Last Updated**: 2025-11-12  
**Version**: 2.0  
**Author**: Manus AI
