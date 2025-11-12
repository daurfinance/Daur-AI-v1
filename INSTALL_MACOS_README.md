# Daur AI - Automated Installer for macOS

## 🚀 One-Command Installation

```bash
curl -fsSL https://raw.githubusercontent.com/daurfinance/Daur-AI-v1/main/install-macos.sh | bash
```

Or download and run manually:

```bash
# Download installer
curl -O https://raw.githubusercontent.com/daurfinance/Daur-AI-v1/main/install-macos.sh

# Make executable
chmod +x install-macos.sh

# Run installer
./install-macos.sh
```

## ✨ What This Installer Does

1. **Checks System Requirements**
   - Verifies macOS version
   - Detects architecture (Apple Silicon or Intel)
   - Checks available disk space

2. **Installs Dependencies**
   - Docker Desktop (if not installed)
   - Python 3.10+ (via Homebrew)
   - Flask for web UI

3. **Sets Up Daur AI**
   - Clones repository
   - Creates configuration UI
   - Builds Docker images

4. **Creates GUI Application**
   - Installs "Daur AI.app" in ~/Applications/
   - Creates launch script
   - Opens web-based configuration interface

## 🎨 Configuration UI Features

After installation, you'll have access to a beautiful web interface at `http://127.0.0.1:3000` with:

- **🔑 API Key Management** - Configure OpenAI, Anthropic keys
- **⚙️ Application Settings** - Log level, headless mode, etc.
- **🔐 Security Configuration** - Generate and manage secrets
- **🐳 Docker Control** - Start/stop/restart containers
- **📋 Log Viewer** - Real-time container logs
- **📊 Status Dashboard** - Monitor system health

## 📱 Using the App

### Launch from Applications

1. Open Finder
2. Go to ~/Applications/
3. Double-click "Daur AI.app"
4. Configuration UI opens in browser automatically

### Launch from Terminal

```bash
~/Daur-AI-v1/launch-config-ui.sh
```

## 📖 Next Steps

1. **Configure API Keys** - Add your OpenAI API key in the UI
2. **Start Containers** - Click "Start" in Docker Control section
3. **Verify Installation** - Check logs for successful startup
4. **Read Documentation** - See docs/guides/quick-start.md

## 🆘 Troubleshooting

### Docker Not Starting

```bash
# Check if Docker Desktop is running
docker info

# If not, start Docker Desktop from Applications
open -a Docker
```

### Port Already in Use

```bash
# Check what's using port 3000
lsof -i :3000

# Kill the process or change port in config-ui/app.py
```

### Permission Denied

```bash
# Fix permissions
chmod +x ~/Daur-AI-v1/install-macos.sh
chmod +x ~/Daur-AI-v1/launch-config-ui.sh
```

## 🔄 Updating

```bash
cd ~/Daur-AI-v1
git pull
docker-compose build
docker-compose up -d
```

## 🗑️ Uninstalling

```bash
# Stop containers
cd ~/Daur-AI-v1
docker-compose down -v

# Remove installation
rm -rf ~/Daur-AI-v1
rm -rf ~/Applications/Daur\ AI.app
```

## 📞 Support

- **Documentation**: docs/INDEX.md
- **GitHub Issues**: https://github.com/daurfinance/Daur-AI-v1/issues
- **Installation Guide**: INSTALLATION_GUIDE.md

---

**Daur AI v2.0** - Enterprise Automation Made Easy 🚀
