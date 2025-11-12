# Daur AI - Manual Installation for macOS

## 🍎 macOS Installation Guide (Apple Silicon & Intel)

### Prerequisites

- macOS 11.0 (Big Sur) or later
- Python 3.10 or 3.11 (Python 3.13 has compatibility issues)
- Homebrew (package manager)
- 10GB free disk space

---

## 📦 Step 1: Install Homebrew (if not installed)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

---

## 🐍 Step 2: Install Python 3.11

**Important:** Use Python 3.11, not 3.13 (compatibility issues with some packages)

```bash
# Install Python 3.11
brew install python@3.11

# Verify installation
python3.11 --version

# Create alias (optional)
echo 'alias python3=python3.11' >> ~/.zshrc
source ~/.zshrc
```

---

## 📥 Step 3: Clone Repository

```bash
cd ~
git clone https://github.com/daurfinance/Daur-AI-v1.git
cd Daur-AI-v1
```

---

## 🔧 Step 4: Install System Dependencies

```bash
# Install Tesseract OCR
brew install tesseract

# Install other dependencies
brew install opencv
```

---

## 🐍 Step 5: Create Virtual Environment

```bash
cd ~/Daur-AI-v1

# Create virtual environment with Python 3.11
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

---

## 📦 Step 6: Install Python Dependencies

```bash
# Install macOS-specific requirements
pip install -r requirements-macos.txt

# Install Playwright browsers
python3 -m playwright install chromium
```

---

## ⚙️ Step 7: Configure Environment

```bash
# Create .env file
cat > .env << 'ENVEOF'
# AI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Database
DB_PASSWORD=secure_password_123

# Application
DAUR_AI_LOG_LEVEL=INFO
DAUR_AI_HEADLESS=true

# Security
JWT_SECRET=78UlAKhEuTt6sQITAN_FhRv9VgbnIKZWwkLqOhH_tVE
ENCRYPTION_KEY=deT-De2LDRYJHFxacJkwJ8aS_dPmuD8aoKYuV-IQu2c
ENVEOF

# Edit and add your OpenAI API key
nano .env
```

---

## 🚀 Step 8: Run Daur AI

### Option A: Run Main Application

```bash
cd ~/Daur-AI-v1
source venv/bin/activate
python3 -m src.main
```

### Option B: Run Example Script

```bash
cd ~/Daur-AI-v1
source venv/bin/activate

# Create a simple test script
cat > test_daur.py << 'PYEOF'
#!/usr/bin/env python3
"""
Simple Daur AI test script
"""
import sys
sys.path.insert(0, '/Users/daxfinance/Daur-AI-v1')

from src.agent.core import AgentCore

def main():
    print("🤖 Initializing Daur AI...")
    
    agent = AgentCore()
    
    print("✅ Daur AI initialized successfully!")
    print(f"Agent ID: {agent.agent_id}")
    print(f"Status: {agent.status}")
    
    # Test a simple command
    print("\n📝 Testing command processing...")
    result = agent.process_command("Hello, Daur AI!")
    print(f"Result: {result}")

if __name__ == "__main__":
    main()
PYEOF

python3 test_daur.py
```

---

## 🐳 Alternative: Docker Installation

If you prefer Docker:

```bash
# Install Docker Desktop for Mac
# Download from: https://www.docker.com/products/docker-desktop

# After Docker is installed and running:
cd ~/Daur-AI-v1

# Create .env file (same as above)
nano .env

# Build and run
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f daur-ai
```

---

## 🔍 Troubleshooting

### Issue: Python 3.13 compatibility errors

**Solution:** Use Python 3.11 instead

```bash
brew install python@3.11
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements-macos.txt
```

### Issue: "onnxruntime-silicon not found"

**Solution:** This package is optional. Skip it or install standard onnxruntime:

```bash
pip install onnxruntime
```

### Issue: Tesseract not found

**Solution:** Install Tesseract OCR

```bash
brew install tesseract

# Verify installation
tesseract --version
```

### Issue: Permission denied for screen capture

**Solution:** Grant accessibility permissions

1. Open System Settings
2. Go to Privacy & Security → Accessibility
3. Add Terminal or your IDE to allowed apps

### Issue: Playwright browsers not working

**Solution:** Reinstall Playwright browsers

```bash
python3 -m playwright install --force chromium
```

---

## 📝 Usage Examples

### Example 1: Web Automation

```python
from src.browser.browser_automation import BrowserAutomation

browser = BrowserAutomation()
browser.navigate("https://example.com")
browser.click_element("button[type='submit']")
browser.close()
```

### Example 2: Screen Capture

```python
from src.vision.screen_capture import ScreenCapture

capture = ScreenCapture()
screenshot = capture.capture_screen()
capture.save_screenshot(screenshot, "screenshot.png")
```

### Example 3: AI Processing

```python
from src.ai.openai_client import OpenAIClient

ai = OpenAIClient()
response = ai.chat("Explain what Daur AI does")
print(response)
```

---

## 🔄 Updating

```bash
cd ~/Daur-AI-v1
git pull
source venv/bin/activate
pip install -r requirements-macos.txt --upgrade
```

---

## 🗑️ Uninstalling

```bash
# Remove virtual environment
rm -rf ~/Daur-AI-v1/venv

# Remove project
rm -rf ~/Daur-AI-v1

# Remove Docker containers (if used)
cd ~/Daur-AI-v1
docker-compose down -v
```

---

## 📞 Support

- **Documentation**: docs/INDEX.md
- **GitHub Issues**: https://github.com/daurfinance/Daur-AI-v1/issues
- **Quick Start**: docs/guides/quick-start.md

---

**Daur AI v2.0** - Enterprise Automation for macOS 🚀
