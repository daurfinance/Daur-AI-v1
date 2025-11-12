# Daur AI v2.0 - Complete Installation Guide

**Version**: 2.0.0  
**Last Updated**: 2025-11-12  
**Estimated Time**: 30-45 minutes

---

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Pre-Installation Checklist](#pre-installation-checklist)
3. [Installation Methods](#installation-methods)
4. [Step-by-Step Installation](#step-by-step-installation)
5. [Configuration](#configuration)
6. [Verification](#verification)
7. [Troubleshooting](#troubleshooting)
8. [Post-Installation](#post-installation)

---

## System Requirements

### Minimum Requirements

| Component | Requirement |
|-----------|-------------|
| **Operating System** | Ubuntu 22.04 LTS or later |
| **Python** | 3.8 or higher |
| **RAM** | 4GB minimum |
| **Disk Space** | 10GB free space |
| **Display** | X11 or Wayland display server |
| **Internet** | Required for installation and AI features |

### Recommended Requirements

| Component | Recommendation |
|-----------|----------------|
| **Operating System** | Ubuntu 22.04 LTS |
| **Python** | 3.10 or higher |
| **RAM** | 8GB or more |
| **Disk Space** | 20GB free space |
| **CPU** | 4 cores or more |
| **GPU** | Optional, for accelerated vision processing |

### Supported Platforms

- ✅ **Ubuntu 22.04 LTS** (Primary)
- ✅ **Ubuntu 20.04 LTS** (Supported)
- ⚠️ **Debian 11+** (Community tested)
- ⚠️ **Other Linux** (May require adjustments)
- ❌ **Windows** (Not officially supported)
- ❌ **macOS** (Not officially supported)

---

## Pre-Installation Checklist

Before beginning installation, ensure you have:

- [ ] System meets minimum requirements
- [ ] Root/sudo access to the system
- [ ] Stable internet connection
- [ ] OpenAI API key (or other AI provider credentials)
- [ ] Basic command line knowledge
- [ ] Text editor installed (nano, vim, or other)

### Obtain API Keys

**OpenAI** (Recommended):
1. Visit https://platform.openai.com
2. Create account or sign in
3. Navigate to API Keys section
4. Create new API key
5. Save key securely (you won't see it again)

**Anthropic Claude** (Optional):
1. Visit https://console.anthropic.com
2. Create account
3. Generate API key
4. Save key securely

**Ollama** (Optional, for local LLMs):
- No API key needed
- Requires Ollama installation (see Ollama documentation)

---

## Installation Methods

### Method 1: Docker Installation (Recommended)

**Advantages**:
- Fastest setup
- Isolated environment
- Consistent across systems
- Easy updates and rollback

**Best for**: Production deployments, quick testing

### Method 2: Manual Installation

**Advantages**:
- Full control over installation
- Better for development
- Easier debugging

**Best for**: Development, customization

### Method 3: Development Installation

**Advantages**:
- Editable installation
- Hot reload support
- Full development tools

**Best for**: Contributing, development

---

## Step-by-Step Installation

### Method 1: Docker Installation

#### Step 1: Install Docker

```bash
# Update package index
sudo apt-get update

# Install prerequisites
sudo apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Set up stable repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io

# Verify installation
sudo docker run hello-world
```

#### Step 2: Install Docker Compose

```bash
# Download Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Apply executable permissions
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker-compose --version
```

#### Step 3: Clone Repository

```bash
# Clone Daur AI repository
git clone https://github.com/daurfinance/Daur-AI-v1.git

# Navigate to directory
cd Daur-AI-v1
```

#### Step 4: Configure Environment

```bash
# Create environment file
cat > .env << 'EOF'
# AI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Database
DB_PASSWORD=your_secure_database_password

# Application
DAUR_AI_LOG_LEVEL=INFO
DAUR_AI_HEADLESS=true

# Security
JWT_SECRET=your_random_jwt_secret_here
ENCRYPTION_KEY=your_random_encryption_key_here
EOF

# Edit with your actual values
nano .env
```

**Generate secure secrets**:

```bash
# Generate JWT secret
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate encryption key
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

#### Step 5: Build and Run

```bash
# Build Docker images
docker-compose build

# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f daur-ai
```

#### Step 6: Verify Installation

```bash
# Check if services are running
docker-compose ps

# Test health endpoint
curl http://localhost:8000/health

# Access logs
docker-compose logs daur-ai
```

---

### Method 2: Manual Installation

#### Step 1: Install System Dependencies

```bash
# Update package lists
sudo apt-get update

# Install Python and development tools
sudo apt-get install -y \
    python3.10 \
    python3.10-dev \
    python3-pip \
    python3-venv \
    build-essential

# Install X11 and GUI dependencies
sudo apt-get install -y \
    xvfb \
    x11-utils \
    libx11-dev \
    libxtst-dev \
    libxkbcommon-x11-0

# Install OCR dependencies
sudo apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-rus \
    libtesseract-dev

# Install image processing libraries
sudo apt-get install -y \
    libopencv-dev \
    python3-opencv \
    scrot

# Install additional tools
sudo apt-get install -y \
    wget \
    curl \
    git \
    unzip
```

#### Step 2: Clone Repository

```bash
# Clone repository
git clone https://github.com/daurfinance/Daur-AI-v1.git

# Navigate to directory
cd Daur-AI-v1
```

#### Step 3: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel
```

#### Step 4: Install Python Dependencies

```bash
# Install requirements
pip install -r requirements.txt

# Verify installation
pip list
```

#### Step 5: Install Playwright Browsers

```bash
# Install Playwright browsers
python3 -m playwright install chromium

# Install system dependencies for Playwright
python3 -m playwright install-deps
```

#### Step 6: Configure Application

```bash
# Copy example configuration
cp config.example.json config.json

# Edit configuration
nano config.json
```

**Minimal config.json**:

```json
{
  "ai": {
    "provider": "openai",
    "model": "gpt-4",
    "api_key": "your_openai_api_key_here"
  },
  "vision": {
    "ocr_enabled": true,
    "ocr_language": "eng"
  },
  "browser": {
    "headless": false
  },
  "logging": {
    "level": "INFO",
    "file": "logs/daur_ai.log"
  }
}
```

#### Step 7: Set Environment Variables

```bash
# Add to ~/.bashrc or ~/.zshrc
echo 'export OPENAI_API_KEY="your_api_key_here"' >> ~/.bashrc
echo 'export DAUR_AI_LOG_LEVEL="INFO"' >> ~/.bashrc

# Reload shell configuration
source ~/.bashrc
```

#### Step 8: Create Required Directories

```bash
# Create directories
mkdir -p logs data config

# Set permissions
chmod 755 logs data config
```

#### Step 9: Initialize Database (Optional)

```bash
# Install PostgreSQL
sudo apt-get install -y postgresql postgresql-contrib

# Start PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres psql << EOF
CREATE DATABASE daur_ai;
CREATE USER daur WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE daur_ai TO daur;
\q
EOF

# Set database URL
echo 'export DATABASE_URL="postgresql://daur:your_secure_password@localhost/daur_ai"' >> ~/.bashrc
source ~/.bashrc
```

#### Step 10: Run Application

```bash
# Activate virtual environment
source venv/bin/activate

# Run application
python3 -m src.main

# Or run with Xvfb (headless)
xvfb-run python3 -m src.main
```

---

### Method 3: Development Installation

#### Step 1-3: Same as Manual Installation

Follow Steps 1-3 from Manual Installation.

#### Step 4: Install Development Dependencies

```bash
# Install requirements with development tools
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Or install individual dev tools
pip install pytest pytest-cov pytest-asyncio
pip install flake8 pylint black mypy
pip install ipython jupyter
```

#### Step 5: Install in Editable Mode

```bash
# Install package in editable mode
pip install -e .
```

#### Step 6: Set Up Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run on all files
pre-commit run --all-files
```

#### Step 7: Configure IDE

**VS Code** (.vscode/settings.json):

```json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests"],
  "editor.formatOnSave": true
}
```

**PyCharm**:
- Set Python interpreter to venv/bin/python
- Enable pytest as test runner
- Configure Black as code formatter

---

## Configuration

### Essential Configuration

#### 1. AI Provider Configuration

**OpenAI**:
```json
{
  "ai": {
    "provider": "openai",
    "model": "gpt-4",
    "api_key": "sk-...",
    "temperature": 0.7,
    "max_tokens": 2000
  }
}
```

**Anthropic Claude**:
```json
{
  "ai": {
    "provider": "anthropic",
    "model": "claude-3-opus-20240229",
    "api_key": "sk-ant-...",
    "temperature": 0.7,
    "max_tokens": 2000
  }
}
```

**Ollama (Local)**:
```json
{
  "ai": {
    "provider": "ollama",
    "model": "llama2",
    "base_url": "http://localhost:11434",
    "temperature": 0.7
  }
}
```

#### 2. Vision Configuration

```json
{
  "vision": {
    "ocr_enabled": true,
    "ocr_language": "eng",
    "ocr_confidence_threshold": 0.6,
    "screenshot_format": "png",
    "use_gpu": false
  }
}
```

#### 3. Browser Configuration

```json
{
  "browser": {
    "type": "chromium",
    "headless": false,
    "viewport_width": 1920,
    "viewport_height": 1080,
    "timeout": 30000,
    "user_agent": "Mozilla/5.0..."
  }
}
```

#### 4. Logging Configuration

```json
{
  "logging": {
    "level": "INFO",
    "file": "logs/daur_ai.log",
    "max_size_mb": 100,
    "backup_count": 5,
    "json_format": false
  }
}
```

### Advanced Configuration

#### Security Settings

```json
{
  "security": {
    "enable_rbac": true,
    "enable_mfa": false,
    "password_min_length": 12,
    "session_timeout_minutes": 60,
    "max_login_attempts": 5
  }
}
```

#### Performance Settings

```json
{
  "performance": {
    "max_workers": 4,
    "cache_enabled": true,
    "cache_ttl_seconds": 3600,
    "batch_size": 10
  }
}
```

---

## Verification

### Basic Verification

```bash
# Check Python version
python3 --version

# Check if modules import correctly
python3 -c "from src.agent.core import DaurAgent; print('✅ Agent Core OK')"
python3 -c "from src.browser.browser_automation import BrowserAutomation; print('✅ Browser OK')"
python3 -c "from src.vision.screen_analyzer import ScreenAnalyzer; print('✅ Vision OK')"

# Check Playwright
python3 -m playwright --version

# Check Tesseract
tesseract --version
```

### Run Test Suite

```bash
# Activate virtual environment
source venv/bin/activate

# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test
pytest tests/test_billing.py -v
```

### Test Basic Functionality

Create test script `test_installation.py`:

```python
#!/usr/bin/env python3
"""Test basic Daur AI functionality."""

import sys
sys.path.insert(0, '/home/ubuntu/Daur-AI-v1')

def test_imports():
    """Test that all critical modules can be imported."""
    try:
        from src.agent.core import DaurAgent
        from src.browser.browser_automation import BrowserAutomation
        from src.input.input_controller import InputController
        from src.vision.screen_analyzer import ScreenAnalyzer
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_configuration():
    """Test configuration loading."""
    try:
        from src.config.app_config import get_config
        config = get_config()
        print(f"✅ Configuration loaded: {config.ai.model_name}")
        return True
    except Exception as e:
        print(f"❌ Configuration failed: {e}")
        return False

def test_logging():
    """Test logging system."""
    try:
        from src.config.logging_config import setup_logging, get_logger
        setup_logging()
        logger = get_logger(__name__)
        logger.info("Test log message")
        print("✅ Logging system working")
        return True
    except Exception as e:
        print(f"❌ Logging failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing Daur AI Installation...\n")
    
    tests = [
        ("Imports", test_imports),
        ("Configuration", test_configuration),
        ("Logging", test_logging)
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\nTesting {name}...")
        results.append(test_func())
    
    print("\n" + "="*50)
    print(f"Results: {sum(results)}/{len(results)} tests passed")
    
    if all(results):
        print("✅ Installation verified successfully!")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Check errors above.")
        sys.exit(1)
```

Run test:

```bash
python3 test_installation.py
```

---

## Troubleshooting

### Common Issues

#### Issue: ModuleNotFoundError

**Solution**:
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt

# Check Python path
python3 -c "import sys; print(sys.path)"
```

#### Issue: Display errors (Cannot open display :0)

**Solution**:
```bash
# Use Xvfb
xvfb-run python3 -m src.main

# Or set headless mode in config
# browser.headless = true
```

#### Issue: Playwright browser not found

**Solution**:
```bash
# Reinstall browsers
python3 -m playwright install chromium
python3 -m playwright install-deps
```

#### Issue: Tesseract not found

**Solution**:
```bash
# Install Tesseract
sudo apt-get install tesseract-ocr tesseract-ocr-eng

# Verify installation
tesseract --version
which tesseract
```

#### Issue: Permission denied

**Solution**:
```bash
# Fix permissions
chmod +x venv/bin/*
chmod 755 logs data config

# Add user to required groups
sudo usermod -a -G input $USER
# Log out and log back in
```

---

## Post-Installation

### Security Hardening

```bash
# Set proper file permissions
chmod 600 config.json
chmod 600 .env
chmod 700 logs

# Restrict access to sensitive directories
sudo chown -R $USER:$USER /home/ubuntu/Daur-AI-v1
chmod 755 /home/ubuntu/Daur-AI-v1
```

### Set Up Systemd Service (Optional)

Create `/etc/systemd/system/daur-ai.service`:

```ini
[Unit]
Description=Daur AI Automation Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/Daur-AI-v1
Environment="PATH=/home/ubuntu/Daur-AI-v1/venv/bin"
ExecStart=/home/ubuntu/Daur-AI-v1/venv/bin/python3 -m src.main
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable daur-ai
sudo systemctl start daur-ai
sudo systemctl status daur-ai
```

### Set Up Log Rotation

Create `/etc/logrotate.d/daur-ai`:

```
/home/ubuntu/Daur-AI-v1/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0644 ubuntu ubuntu
}
```

### Enable Monitoring

```bash
# Install monitoring tools
pip install prometheus-client

# Configure metrics endpoint
# Add to config.json:
{
  "monitoring": {
    "enabled": true,
    "port": 9090
  }
}
```

### Backup Configuration

```bash
# Create backup script
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/home/ubuntu/daur-ai-backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup configuration
tar czf $BACKUP_DIR/config_$DATE.tar.gz config.json .env

# Backup database
docker-compose exec -T postgres pg_dump -U daur daur_ai > $BACKUP_DIR/db_$DATE.sql

# Keep only last 7 backups
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete

echo "Backup completed: $DATE"
EOF

chmod +x backup.sh

# Add to crontab for daily backups
crontab -e
# Add line:
# 0 2 * * * /home/ubuntu/Daur-AI-v1/backup.sh
```

---

## Next Steps

After successful installation:

1. **Read Documentation**: Review [Quick Start Guide](docs/guides/quick-start.md)
2. **Try Examples**: Run example scripts in `examples/` directory
3. **Configure Automation**: Set up your first automation task
4. **Join Community**: Participate in GitHub Discussions
5. **Report Issues**: Submit bug reports or feature requests

---

## Getting Help

- **Documentation**: [docs/INDEX.md](docs/INDEX.md)
- **Troubleshooting**: [docs/guides/troubleshooting.md](docs/guides/troubleshooting.md)
- **GitHub Issues**: https://github.com/daurfinance/Daur-AI-v1/issues
- **Community**: https://github.com/daurfinance/Daur-AI-v1/discussions

---

**Installation Complete!** 🎉

You are now ready to use Daur AI v2.0 for enterprise automation.

---

**Last Updated**: 2025-11-12  
**Version**: 2.0.0  
**Author**: Manus AI

