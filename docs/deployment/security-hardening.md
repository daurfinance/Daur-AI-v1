# Security Hardening Guide

**Version**: 2.0  
**Last Updated**: 2025-11-12

---

## Overview

This guide provides comprehensive security hardening recommendations for Daur AI deployments. Following these practices will significantly improve the security posture of your installation.

---

## Table of Contents

1. [Authentication and Authorization](#authentication-and-authorization)
2. [API Security](#api-security)
3. [Data Encryption](#data-encryption)
4. [Network Security](#network-security)
5. [Secrets Management](#secrets-management)
6. [Audit Logging](#audit-logging)
7. [Dependency Security](#dependency-security)
8. [Container Security](#container-security)

---

## Authentication and Authorization

### Implement Strong Authentication

```python
from src.system.security import AuthenticationManager

# Configure authentication
auth_manager = AuthenticationManager({
    "password_min_length": 12,
    "require_uppercase": True,
    "require_lowercase": True,
    "require_numbers": True,
    "require_special_chars": True,
    "password_expiry_days": 90,
    "max_login_attempts": 5,
    "lockout_duration_minutes": 30
})

# Use strong password hashing
from src.system.password_utils import hash_password, verify_password

hashed = hash_password("user_password")  # Uses Argon2
is_valid = verify_password("user_password", hashed)
```

### Role-Based Access Control (RBAC)

```python
from src.system.rbac import RBACManager

# Initialize RBAC
rbac = RBACManager()

# Define roles
rbac.create_role("admin", permissions=[
    "user.create", "user.delete", "user.update",
    "system.configure", "system.restart"
])

rbac.create_role("operator", permissions=[
    "automation.run", "automation.view",
    "report.generate"
])

rbac.create_role("viewer", permissions=[
    "automation.view", "report.view"
])

# Assign roles to users
rbac.assign_role("user@example.com", "operator")

# Check permissions
if rbac.has_permission("user@example.com", "automation.run"):
    # Allow operation
    pass
```

### Multi-Factor Authentication (MFA)

```python
from src.system.mfa import MFAManager

mfa = MFAManager()

# Generate MFA secret for user
secret = mfa.generate_secret("user@example.com")
qr_code = mfa.generate_qr_code(secret)

# Verify MFA token
token = "123456"  # From authenticator app
is_valid = mfa.verify_token("user@example.com", token)
```

---

## API Security

### API Key Management

```python
from src.system.api_key_manager import APIKeyManager

api_key_manager = APIKeyManager()

# Generate API key with permissions
api_key = api_key_manager.create_key(
    user_id="user123",
    permissions=["automation.run", "report.view"],
    expiry_days=90
)

# Validate API key
is_valid, permissions = api_key_manager.validate_key(api_key)
```

### Rate Limiting

```python
from src.system.rate_limiter import RateLimiter

# Configure rate limiting
rate_limiter = RateLimiter({
    "requests_per_minute": 60,
    "requests_per_hour": 1000,
    "requests_per_day": 10000
})

# Apply rate limiting
@rate_limiter.limit("60/minute")
async def api_endpoint(request):
    return {"status": "success"}
```

### Input Validation

```python
from pydantic import BaseModel, validator, EmailStr

class UserInput(BaseModel):
    email: EmailStr
    username: str
    age: int
    
    @validator('username')
    def username_alphanumeric(cls, v):
        assert v.isalnum(), 'must be alphanumeric'
        assert len(v) >= 3, 'must be at least 3 characters'
        return v
    
    @validator('age')
    def age_valid(cls, v):
        assert 0 < v < 150, 'must be realistic age'
        return v

# Use in API
def create_user(data: dict):
    validated = UserInput(**data)
    # Proceed with validated data
```

---

## Data Encryption

### Encryption at Rest

```python
from src.system.encryption import DataEncryption

# Initialize encryption
encryption = DataEncryption(key=os.environ['ENCRYPTION_KEY'])

# Encrypt sensitive data
sensitive_data = "user_password"
encrypted = encryption.encrypt(sensitive_data)

# Decrypt when needed
decrypted = encryption.decrypt(encrypted)

# Encrypt files
encryption.encrypt_file("sensitive_data.json", "sensitive_data.enc")
encryption.decrypt_file("sensitive_data.enc", "sensitive_data.json")
```

### Encryption in Transit

```python
# Use TLS/SSL for all communications
import ssl

# Configure SSL context
ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ssl_context.load_cert_chain('cert.pem', 'key.pem')

# Use with web server
from fastapi import FastAPI
import uvicorn

app = FastAPI()

uvicorn.run(
    app,
    host="0.0.0.0",
    port=8443,
    ssl_keyfile="key.pem",
    ssl_certfile="cert.pem"
)
```

### Database Encryption

```python
# Encrypt sensitive database columns
from sqlalchemy import Column, String
from sqlalchemy_utils import EncryptedType
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    email = Column(String)
    password = Column(EncryptedType(String, os.environ['DB_ENCRYPTION_KEY'], AesEngine, 'pkcs5'))
    api_key = Column(EncryptedType(String, os.environ['DB_ENCRYPTION_KEY'], AesEngine, 'pkcs5'))
```

---

## Network Security

### Firewall Configuration

```bash
# Configure UFW firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTPS
sudo ufw allow 443/tcp

# Allow application port
sudo ufw allow 8000/tcp

# Enable firewall
sudo ufw enable
```

### Network Segmentation

```yaml
# docker-compose.yml with network segmentation
version: '3.8'

services:
  daur-ai:
    networks:
      - frontend
      - backend
  
  postgres:
    networks:
      - backend  # Not exposed to frontend
  
  nginx:
    networks:
      - frontend  # Only frontend access

networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true  # No external access
```

### Reverse Proxy with Nginx

```nginx
# /etc/nginx/sites-available/daur-ai
server {
    listen 443 ssl http2;
    server_name daur-ai.example.com;
    
    ssl_certificate /etc/ssl/certs/daur-ai.crt;
    ssl_certificate_key /etc/ssl/private/daur-ai.key;
    
    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req zone=api_limit burst=20 nodelay;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## Secrets Management

### Environment Variables

```bash
# Use secure environment variable management
# Never commit secrets to version control

# .gitignore
.env
.env.local
.env.production
secrets/
*.key
*.pem
```

### Secrets Management Tools

```python
# Use HashiCorp Vault for secrets
import hvac

client = hvac.Client(url='http://vault:8200')
client.token = os.environ['VAULT_TOKEN']

# Read secret
secret = client.secrets.kv.v2.read_secret_version(path='daur-ai/config')
api_key = secret['data']['data']['api_key']

# Write secret
client.secrets.kv.v2.create_or_update_secret(
    path='daur-ai/config',
    secret={'api_key': 'new_key_value'}
)
```

### Rotate Credentials Regularly

```python
from src.system.credential_rotation import CredentialRotator

rotator = CredentialRotator()

# Rotate API keys every 90 days
rotator.schedule_rotation(
    credential_type="api_key",
    rotation_days=90,
    notification_email="admin@example.com"
)

# Rotate database passwords
rotator.rotate_database_password(
    database="daur_ai",
    notify=True
)
```

---

## Audit Logging

### Comprehensive Logging

```python
from src.config.logging_config import setup_logging, get_logger

# Setup security logging
setup_logging(
    log_level='INFO',
    security_log=True,
    audit_log=True
)

logger = get_logger(__name__)

# Log security events
logger.security_event(
    event_type="login_attempt",
    user="user@example.com",
    ip_address="192.168.1.100",
    success=True
)

logger.security_event(
    event_type="permission_denied",
    user="user@example.com",
    resource="system.configure",
    ip_address="192.168.1.100"
)

# Log audit trail
logger.audit(
    action="user_created",
    user="admin@example.com",
    target="newuser@example.com",
    details={"role": "operator"}
)
```

### Log Monitoring

```python
# Monitor logs for security incidents
from src.system.log_monitor import LogMonitor

monitor = LogMonitor()

# Alert on failed login attempts
monitor.add_rule(
    name="failed_login_threshold",
    pattern="login_attempt.*success=False",
    threshold=5,
    window_minutes=10,
    action="send_alert",
    alert_email="security@example.com"
)

# Alert on privilege escalation attempts
monitor.add_rule(
    name="privilege_escalation",
    pattern="permission_denied.*system\.",
    threshold=3,
    window_minutes=5,
    action="lock_account"
)
```

---

## Dependency Security

### Scan Dependencies

```bash
# Install security scanning tools
pip install safety bandit

# Check for known vulnerabilities
safety check

# Scan code for security issues
bandit -r src/ -f json -o security-report.json

# Update dependencies regularly
pip list --outdated
pip install --upgrade package_name
```

### Dependency Pinning

```txt
# requirements.txt - Pin exact versions
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
sqlalchemy==2.0.23

# Use hash checking for extra security
fastapi==0.104.1 \
    --hash=sha256:abc123...
```

---

## Container Security

### Secure Dockerfile

```dockerfile
FROM ubuntu:22.04

# Run as non-root user
RUN useradd -m -u 1000 daur && \
    chown -R daur:daur /app

# Set file permissions
RUN chmod 755 /app && \
    chmod 644 /app/*.py

USER daur

# Use specific versions
RUN pip install --no-cache-dir \
    fastapi==0.104.1 \
    uvicorn==0.24.0

# Remove unnecessary packages
RUN apt-get remove --purge -y \
    build-essential \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:8000/health || exit 1
```

### Container Scanning

```bash
# Scan Docker images for vulnerabilities
docker scan daur-ai:latest

# Use Trivy for comprehensive scanning
trivy image daur-ai:latest

# Scan for secrets in images
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image --severity HIGH,CRITICAL daur-ai:latest
```

---

## Security Checklist

- [ ] Strong password policy enforced
- [ ] Multi-factor authentication enabled
- [ ] Role-based access control implemented
- [ ] API keys rotated regularly
- [ ] Rate limiting configured
- [ ] Input validation on all endpoints
- [ ] Data encrypted at rest
- [ ] TLS/SSL enabled for all connections
- [ ] Database credentials encrypted
- [ ] Firewall configured
- [ ] Network segmentation implemented
- [ ] Reverse proxy with security headers
- [ ] Secrets stored securely (not in code)
- [ ] Audit logging enabled
- [ ] Log monitoring configured
- [ ] Dependencies scanned for vulnerabilities
- [ ] Dependencies pinned to specific versions
- [ ] Container images scanned
- [ ] Running as non-root user
- [ ] Regular security updates applied

---

**Last Updated**: 2025-11-12  
**Version**: 2.0  
**Author**: Manus AI

