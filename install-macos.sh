#!/bin/bash

###############################################################################
# Daur AI v2.0 - Automated Installer for macOS
# This script automatically installs Daur AI with GUI configuration interface
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
INSTALL_DIR="$HOME/Daur-AI-v1"
CONFIG_UI_PORT=3000
DAUR_AI_PORT=8000

###############################################################################
# Helper Functions
###############################################################################

print_header() {
    echo ""
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC}          ${GREEN}Daur AI v2.0 - Automated Installer${NC}           ${BLUE}║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_step() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} ${GREEN}➜${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

check_command() {
    if command -v $1 &> /dev/null; then
        return 0
    else
        return 1
    fi
}

###############################################################################
# Pre-installation Checks
###############################################################################

check_macos() {
    print_step "Checking macOS version..."
    
    if [[ "$OSTYPE" != "darwin"* ]]; then
        print_error "This installer is for macOS only!"
        exit 1
    fi
    
    macos_version=$(sw_vers -productVersion)
    print_success "macOS $macos_version detected"
}

check_architecture() {
    print_step "Detecting system architecture..."
    
    arch=$(uname -m)
    if [[ "$arch" == "arm64" ]]; then
        print_success "Apple Silicon (M1/M2/M3) detected"
        ARCH="arm64"
    elif [[ "$arch" == "x86_64" ]]; then
        print_success "Intel Mac detected"
        ARCH="x86_64"
    else
        print_error "Unsupported architecture: $arch"
        exit 1
    fi
}

check_disk_space() {
    print_step "Checking available disk space..."
    
    available_space=$(df -h "$HOME" | awk 'NR==2 {print $4}' | sed 's/G//')
    
    if (( $(echo "$available_space < 10" | bc -l) )); then
        print_error "Insufficient disk space. Need at least 10GB free."
        exit 1
    fi
    
    print_success "${available_space}GB available"
}

###############################################################################
# Docker Installation
###############################################################################

install_docker() {
    print_step "Checking Docker installation..."
    
    if check_command docker && check_command docker-compose; then
        docker_version=$(docker --version | awk '{print $3}' | sed 's/,//')
        print_success "Docker $docker_version already installed"
        return 0
    fi
    
    print_warning "Docker not found. Installing Docker Desktop..."
    
    # Download Docker Desktop
    if [[ "$ARCH" == "arm64" ]]; then
        DOCKER_URL="https://desktop.docker.com/mac/main/arm64/Docker.dmg"
    else
        DOCKER_URL="https://desktop.docker.com/mac/main/amd64/Docker.dmg"
    fi
    
    print_step "Downloading Docker Desktop..."
    curl -L "$DOCKER_URL" -o /tmp/Docker.dmg
    
    print_step "Mounting Docker.dmg..."
    hdiutil attach /tmp/Docker.dmg
    
    print_step "Installing Docker..."
    cp -R /Volumes/Docker/Docker.app /Applications/
    
    print_step "Unmounting Docker.dmg..."
    hdiutil detach /Volumes/Docker
    
    rm /tmp/Docker.dmg
    
    print_success "Docker Desktop installed"
    print_warning "Please start Docker Desktop from Applications and wait for it to start"
    print_warning "Press Enter when Docker is running (you'll see whale icon in menu bar)..."
    read
    
    # Wait for Docker to start
    print_step "Waiting for Docker to start..."
    timeout=60
    elapsed=0
    while ! docker info &> /dev/null; do
        sleep 2
        elapsed=$((elapsed + 2))
        if [ $elapsed -ge $timeout ]; then
            print_error "Docker failed to start within $timeout seconds"
            exit 1
        fi
        echo -n "."
    done
    echo ""
    
    print_success "Docker is running"
}

###############################################################################
# Python Installation
###############################################################################

install_python() {
    print_step "Checking Python installation..."
    
    if check_command python3; then
        python_version=$(python3 --version | awk '{print $2}')
        print_success "Python $python_version already installed"
        return 0
    fi
    
    print_warning "Python not found. Installing via Homebrew..."
    
    # Install Homebrew if needed
    if ! check_command brew; then
        print_step "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        
        # Add Homebrew to PATH
        if [[ "$ARCH" == "arm64" ]]; then
            echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
            eval "$(/opt/homebrew/bin/brew shellenv)"
        else
            echo 'eval "$(/usr/local/bin/brew shellenv)"' >> ~/.zprofile
            eval "$(/usr/local/bin/brew shellenv)"
        fi
    fi
    
    print_step "Installing Python..."
    brew install python@3.10
    
    print_success "Python installed"
}

###############################################################################
# Project Setup
###############################################################################

setup_project() {
    print_step "Setting up Daur AI project..."
    
    if [ -d "$INSTALL_DIR" ]; then
        print_warning "Installation directory already exists"
        echo -n "Do you want to update? (y/n): "
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            cd "$INSTALL_DIR"
            git pull
        fi
    else
        print_step "Cloning repository..."
        git clone https://github.com/daurfinance/Daur-AI-v1.git "$INSTALL_DIR"
    fi
    
    cd "$INSTALL_DIR"
    print_success "Project setup complete"
}

###############################################################################
# Configuration UI Setup
###############################################################################

setup_config_ui() {
    print_step "Setting up configuration UI..."
    
    # Create config UI directory
    mkdir -p "$INSTALL_DIR/config-ui"
    
    # Create Python Flask app for configuration
    cat > "$INSTALL_DIR/config-ui/app.py" << 'PYEOF'
#!/usr/bin/env python3
"""
Daur AI Configuration UI
Web-based interface for managing .env configuration
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import secrets
import subprocess
import json

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

INSTALL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_FILE = os.path.join(INSTALL_DIR, '.env')

def read_env():
    """Read current .env configuration"""
    config = {}
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    config[key] = value
    return config

def write_env(config):
    """Write configuration to .env file"""
    with open(ENV_FILE, 'w') as f:
        f.write("# Daur AI Configuration\n")
        f.write("# Generated by Configuration UI\n\n")
        
        f.write("# AI Configuration\n")
        f.write(f"OPENAI_API_KEY={config.get('OPENAI_API_KEY', '')}\n")
        f.write(f"ANTHROPIC_API_KEY={config.get('ANTHROPIC_API_KEY', '')}\n\n")
        
        f.write("# Database\n")
        f.write(f"DB_PASSWORD={config.get('DB_PASSWORD', 'changeme')}\n\n")
        
        f.write("# Application\n")
        f.write(f"DAUR_AI_LOG_LEVEL={config.get('DAUR_AI_LOG_LEVEL', 'INFO')}\n")
        f.write(f"DAUR_AI_HEADLESS={config.get('DAUR_AI_HEADLESS', 'true')}\n\n")
        
        f.write("# Security\n")
        f.write(f"JWT_SECRET={config.get('JWT_SECRET', '')}\n")
        f.write(f"ENCRYPTION_KEY={config.get('ENCRYPTION_KEY', '')}\n")

def get_docker_status():
    """Check if Docker containers are running"""
    try:
        result = subprocess.run(
            ['docker-compose', 'ps', '--format', 'json'],
            cwd=INSTALL_DIR,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            containers = json.loads(result.stdout) if result.stdout else []
            return {'running': True, 'containers': containers}
    except:
        pass
    return {'running': False, 'containers': []}

@app.route('/')
def index():
    """Main configuration page"""
    config = read_env()
    docker_status = get_docker_status()
    return render_template('index.html', config=config, docker_status=docker_status)

@app.route('/save', methods=['POST'])
def save_config():
    """Save configuration"""
    config = {
        'OPENAI_API_KEY': request.form.get('openai_key', ''),
        'ANTHROPIC_API_KEY': request.form.get('anthropic_key', ''),
        'DB_PASSWORD': request.form.get('db_password', 'changeme'),
        'DAUR_AI_LOG_LEVEL': request.form.get('log_level', 'INFO'),
        'DAUR_AI_HEADLESS': request.form.get('headless', 'true'),
        'JWT_SECRET': request.form.get('jwt_secret', ''),
        'ENCRYPTION_KEY': request.form.get('encryption_key', ''),
    }
    
    write_env(config)
    return jsonify({'success': True, 'message': 'Configuration saved successfully'})

@app.route('/generate-secrets', methods=['POST'])
def generate_secrets():
    """Generate new security secrets"""
    jwt_secret = secrets.token_urlsafe(32)
    encryption_key = secrets.token_urlsafe(32)
    return jsonify({
        'jwt_secret': jwt_secret,
        'encryption_key': encryption_key
    })

@app.route('/docker/<action>', methods=['POST'])
def docker_action(action):
    """Control Docker containers"""
    try:
        if action == 'start':
            subprocess.run(['docker-compose', 'up', '-d'], cwd=INSTALL_DIR, check=True)
            return jsonify({'success': True, 'message': 'Containers started'})
        elif action == 'stop':
            subprocess.run(['docker-compose', 'stop'], cwd=INSTALL_DIR, check=True)
            return jsonify({'success': True, 'message': 'Containers stopped'})
        elif action == 'restart':
            subprocess.run(['docker-compose', 'restart'], cwd=INSTALL_DIR, check=True)
            return jsonify({'success': True, 'message': 'Containers restarted'})
        elif action == 'logs':
            result = subprocess.run(
                ['docker-compose', 'logs', '--tail=100'],
                cwd=INSTALL_DIR,
                capture_output=True,
                text=True
            )
            return jsonify({'success': True, 'logs': result.stdout})
    except subprocess.CalledProcessError as e:
        return jsonify({'success': False, 'message': str(e)})
    
    return jsonify({'success': False, 'message': 'Unknown action'})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=3000, debug=False)
PYEOF

    chmod +x "$INSTALL_DIR/config-ui/app.py"
    
    # Create HTML template
    mkdir -p "$INSTALL_DIR/config-ui/templates"
    
    cat > "$INSTALL_DIR/config-ui/templates/index.html" << 'HTMLEOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Daur AI Configuration</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 32px;
            margin-bottom: 10px;
        }
        
        .header p {
            opacity: 0.9;
            font-size: 16px;
        }
        
        .content {
            padding: 40px;
        }
        
        .status {
            background: #f7fafc;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 30px;
            border-left: 4px solid #667eea;
        }
        
        .status.running {
            border-left-color: #48bb78;
            background: #f0fff4;
        }
        
        .status.stopped {
            border-left-color: #f56565;
            background: #fff5f5;
        }
        
        .form-group {
            margin-bottom: 25px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #2d3748;
        }
        
        .form-group input, .form-group select {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        
        .form-group input:focus, .form-group select:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .form-group small {
            display: block;
            margin-top: 5px;
            color: #718096;
            font-size: 12px;
        }
        
        .button-group {
            display: flex;
            gap: 10px;
            margin-top: 30px;
        }
        
        .btn {
            flex: 1;
            padding: 15px 30px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4);
        }
        
        .btn-secondary {
            background: #e2e8f0;
            color: #2d3748;
        }
        
        .btn-secondary:hover {
            background: #cbd5e0;
        }
        
        .btn-success {
            background: #48bb78;
            color: white;
        }
        
        .btn-danger {
            background: #f56565;
            color: white;
        }
        
        .section-title {
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 20px;
            color: #2d3748;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 10px;
        }
        
        .alert {
            padding: 15px 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            display: none;
        }
        
        .alert.success {
            background: #c6f6d5;
            color: #22543d;
            border-left: 4px solid #48bb78;
        }
        
        .alert.error {
            background: #fed7d7;
            color: #742a2a;
            border-left: 4px solid #f56565;
        }
        
        .logs {
            background: #1a202c;
            color: #e2e8f0;
            padding: 20px;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            max-height: 300px;
            overflow-y: auto;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Daur AI Configuration</h1>
            <p>Manage your Daur AI installation settings</p>
        </div>
        
        <div class="content">
            <div id="alert" class="alert"></div>
            
            <!-- Docker Status -->
            <div class="status {% if docker_status.running %}running{% else %}stopped{% endif %}">
                <h3>Docker Status: {% if docker_status.running %}🟢 Running{% else %}🔴 Stopped{% endif %}</h3>
                <div class="button-group" style="margin-top: 15px;">
                    <button class="btn btn-success" onclick="dockerAction('start')">Start</button>
                    <button class="btn btn-danger" onclick="dockerAction('stop')">Stop</button>
                    <button class="btn btn-secondary" onclick="dockerAction('restart')">Restart</button>
                    <button class="btn btn-secondary" onclick="showLogs()">View Logs</button>
                </div>
            </div>
            
            <!-- Configuration Form -->
            <form id="configForm">
                <div class="section-title">🔑 AI Provider Configuration</div>
                
                <div class="form-group">
                    <label for="openai_key">OpenAI API Key</label>
                    <input type="password" id="openai_key" name="openai_key" value="{{ config.get('OPENAI_API_KEY', '') }}" placeholder="sk-proj-...">
                    <small>Get your API key from https://platform.openai.com</small>
                </div>
                
                <div class="form-group">
                    <label for="anthropic_key">Anthropic API Key (Optional)</label>
                    <input type="password" id="anthropic_key" name="anthropic_key" value="{{ config.get('ANTHROPIC_API_KEY', '') }}" placeholder="sk-ant-...">
                    <small>For Claude AI support</small>
                </div>
                
                <div class="section-title">🗄️ Database Configuration</div>
                
                <div class="form-group">
                    <label for="db_password">Database Password</label>
                    <input type="password" id="db_password" name="db_password" value="{{ config.get('DB_PASSWORD', 'changeme') }}">
                    <small>Choose a strong password for PostgreSQL</small>
                </div>
                
                <div class="section-title">⚙️ Application Settings</div>
                
                <div class="form-group">
                    <label for="log_level">Log Level</label>
                    <select id="log_level" name="log_level">
                        <option value="DEBUG" {% if config.get('DAUR_AI_LOG_LEVEL') == 'DEBUG' %}selected{% endif %}>DEBUG</option>
                        <option value="INFO" {% if config.get('DAUR_AI_LOG_LEVEL') == 'INFO' or not config.get('DAUR_AI_LOG_LEVEL') %}selected{% endif %}>INFO</option>
                        <option value="WARNING" {% if config.get('DAUR_AI_LOG_LEVEL') == 'WARNING' %}selected{% endif %}>WARNING</option>
                        <option value="ERROR" {% if config.get('DAUR_AI_LOG_LEVEL') == 'ERROR' %}selected{% endif %}>ERROR</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="headless">Headless Mode</label>
                    <select id="headless" name="headless">
                        <option value="true" {% if config.get('DAUR_AI_HEADLESS') == 'true' or not config.get('DAUR_AI_HEADLESS') %}selected{% endif %}>Enabled (Recommended)</option>
                        <option value="false" {% if config.get('DAUR_AI_HEADLESS') == 'false' %}selected{% endif %}>Disabled</option>
                    </select>
                    <small>Run browser automation without visible windows</small>
                </div>
                
                <div class="section-title">🔐 Security Settings</div>
                
                <div class="form-group">
                    <label for="jwt_secret">JWT Secret</label>
                    <input type="password" id="jwt_secret" name="jwt_secret" value="{{ config.get('JWT_SECRET', '') }}">
                    <small>Secret key for JWT token generation</small>
                </div>
                
                <div class="form-group">
                    <label for="encryption_key">Encryption Key</label>
                    <input type="password" id="encryption_key" name="encryption_key" value="{{ config.get('ENCRYPTION_KEY', '') }}">
                    <small>Key for data encryption</small>
                </div>
                
                <button type="button" class="btn btn-secondary" onclick="generateSecrets()" style="width: 100%; margin-bottom: 20px;">
                    🔄 Generate New Security Keys
                </button>
                
                <div class="button-group">
                    <button type="submit" class="btn btn-primary">💾 Save Configuration</button>
                    <button type="button" class="btn btn-secondary" onclick="location.reload()">↻ Reset</button>
                </div>
            </form>
            
            <!-- Logs Section -->
            <div id="logsSection" style="display: none; margin-top: 30px;">
                <div class="section-title">📋 Docker Logs</div>
                <div id="logs" class="logs">Loading logs...</div>
                <button class="btn btn-secondary" onclick="hideLog()" style="margin-top: 10px; width: 100%;">Close Logs</button>
            </div>
        </div>
    </div>
    
    <script>
        function showAlert(message, type) {
            const alert = document.getElementById('alert');
            alert.textContent = message;
            alert.className = 'alert ' + type;
            alert.style.display = 'block';
            setTimeout(() => {
                alert.style.display = 'none';
            }, 5000);
        }
        
        document.getElementById('configForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            
            try {
                const response = await fetch('/save', {
                    method: 'POST',
                    body: formData
                });
                const data = await response.json();
                
                if (data.success) {
                    showAlert('✅ Configuration saved successfully!', 'success');
                } else {
                    showAlert('❌ Failed to save configuration', 'error');
                }
            } catch (error) {
                showAlert('❌ Error: ' + error.message, 'error');
            }
        });
        
        async function generateSecrets() {
            try {
                const response = await fetch('/generate-secrets', { method: 'POST' });
                const data = await response.json();
                
                document.getElementById('jwt_secret').value = data.jwt_secret;
                document.getElementById('encryption_key').value = data.encryption_key;
                
                showAlert('✅ New security keys generated!', 'success');
            } catch (error) {
                showAlert('❌ Error generating keys: ' + error.message, 'error');
            }
        }
        
        async function dockerAction(action) {
            try {
                const response = await fetch(`/docker/${action}`, { method: 'POST' });
                const data = await response.json();
                
                if (data.success) {
                    showAlert('✅ ' + data.message, 'success');
                    setTimeout(() => location.reload(), 2000);
                } else {
                    showAlert('❌ ' + data.message, 'error');
                }
            } catch (error) {
                showAlert('❌ Error: ' + error.message, 'error');
            }
        }
        
        async function showLogs() {
            document.getElementById('logsSection').style.display = 'block';
            
            try {
                const response = await fetch('/docker/logs', { method: 'POST' });
                const data = await response.json();
                
                if (data.success) {
                    document.getElementById('logs').textContent = data.logs;
                } else {
                    document.getElementById('logs').textContent = 'Failed to load logs';
                }
            } catch (error) {
                document.getElementById('logs').textContent = 'Error: ' + error.message;
            }
        }
        
        function hideLog() {
            document.getElementById('logsSection').style.display = 'none';
        }
    </script>
</body>
</html>
HTMLEOF

    # Install Flask
    print_step "Installing Flask..."
    python3 -m pip install --quiet flask
    
    print_success "Configuration UI setup complete"
}

###############################################################################
# Launch Configuration UI
###############################################################################

launch_config_ui() {
    print_step "Launching configuration UI..."
    
    cd "$INSTALL_DIR/config-ui"
    
    # Start Flask app in background
    python3 app.py &
    CONFIG_UI_PID=$!
    
    # Wait for server to start
    sleep 3
    
    # Open browser
    print_success "Opening configuration UI in browser..."
    open "http://127.0.0.1:$CONFIG_UI_PORT"
    
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║${NC}  Configuration UI is running at:                          ${GREEN}║${NC}"
    echo -e "${GREEN}║${NC}  ${BLUE}http://127.0.0.1:$CONFIG_UI_PORT${NC}                                   ${GREEN}║${NC}"
    echo -e "${GREEN}║${NC}                                                            ${GREEN}║${NC}"
    echo -e "${GREEN}║${NC}  Press Ctrl+C to stop the configuration UI                ${GREEN}║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    # Wait for user to finish configuration
    wait $CONFIG_UI_PID
}

###############################################################################
# Create Launch Script
###############################################################################

create_launch_script() {
    print_step "Creating launch script..."
    
    cat > "$INSTALL_DIR/launch-config-ui.sh" << 'LAUNCHEOF'
#!/bin/bash
cd "$(dirname "$0")/config-ui"
python3 app.py &
sleep 2
open "http://127.0.0.1:3000"
wait
LAUNCHEOF

    chmod +x "$INSTALL_DIR/launch-config-ui.sh"
    
    # Create macOS app
    mkdir -p "$HOME/Applications/Daur AI.app/Contents/MacOS"
    
    cat > "$HOME/Applications/Daur AI.app/Contents/MacOS/Daur AI" << APPEOF
#!/bin/bash
cd "$INSTALL_DIR"
./launch-config-ui.sh
APPEOF

    chmod +x "$HOME/Applications/Daur AI.app/Contents/MacOS/Daur AI"
    
    # Create Info.plist
    mkdir -p "$HOME/Applications/Daur AI.app/Contents"
    cat > "$HOME/Applications/Daur AI.app/Contents/Info.plist" << 'PLISTEOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>Daur AI</string>
    <key>CFBundleIdentifier</key>
    <string>com.daurfinance.daur-ai</string>
    <key>CFBundleName</key>
    <string>Daur AI</string>
    <key>CFBundleVersion</key>
    <string>2.0.0</string>
    <key>CFBundleShortVersionString</key>
    <string>2.0.0</string>
</dict>
</plist>
PLISTEOF

    print_success "Launch script created"
    print_success "Daur AI.app created in ~/Applications/"
}

###############################################################################
# Main Installation Flow
###############################################################################

main() {
    print_header
    
    # Pre-installation checks
    check_macos
    check_architecture
    check_disk_space
    
    # Install dependencies
    install_docker
    install_python
    
    # Setup project
    setup_project
    
    # Setup configuration UI
    setup_config_ui
    
    # Create launch script
    create_launch_script
    
    # Final message
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║${NC}          ${BLUE}Installation Complete!${NC}                         ${GREEN}║${NC}"
    echo -e "${GREEN}╠════════════════════════════════════════════════════════════╣${NC}"
    echo -e "${GREEN}║${NC}                                                            ${GREEN}║${NC}"
    echo -e "${GREEN}║${NC}  Daur AI has been successfully installed!                 ${GREEN}║${NC}"
    echo -e "${GREEN}║${NC}                                                            ${GREEN}║${NC}"
    echo -e "${GREEN}║${NC}  You can now:                                              ${GREEN}║${NC}"
    echo -e "${GREEN}║${NC}  1. Open 'Daur AI' app from ~/Applications/               ${GREEN}║${NC}"
    echo -e "${GREEN}║${NC}  2. Or run: $INSTALL_DIR/launch-config-ui.sh              ${GREEN}║${NC}"
    echo -e "${GREEN}║${NC}                                                            ${GREEN}║${NC}"
    echo -e "${GREEN}║${NC}  The configuration UI will open in your browser           ${GREEN}║${NC}"
    echo -e "${GREEN}║${NC}  where you can:                                            ${GREEN}║${NC}"
    echo -e "${GREEN}║${NC}  - Configure API keys                                      ${GREEN}║${NC}"
    echo -e "${GREEN}║${NC}  - Manage Docker containers                                ${GREEN}║${NC}"
    echo -e "${GREEN}║${NC}  - View logs                                               ${GREEN}║${NC}"
    echo -e "${GREEN}║${NC}  - Monitor status                                          ${GREEN}║${NC}"
    echo -e "${GREEN}║${NC}                                                            ${GREEN}║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    # Ask if user wants to launch now
    echo -n "Launch configuration UI now? (y/n): "
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        launch_config_ui
    fi
}

# Run main installation
main

