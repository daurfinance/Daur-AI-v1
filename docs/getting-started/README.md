# Getting Started with Daur AI

This directory contains guides to help you get started with Daur AI quickly and efficiently.

## Quick Start Guides

### General Quick Start
**[QUICK_START.md](QUICK_START.md)** - The fastest way to get Daur AI running on any platform. Follow this guide if you want to be up and running in under 10 minutes.

### Docker Quick Start
**[DOCKER_QUICK_START.md](DOCKER_QUICK_START.md)** - Get started with Daur AI using Docker containers. This is the recommended approach for development and testing environments.

## Platform-Specific Installation

### macOS Installation
**[MACOS_INSTALLATION_GUIDE.md](MACOS_INSTALLATION_GUIDE.md)** - Comprehensive installation guide for macOS users, including system requirements, permissions setup, and troubleshooting.

**[MACOS_APP_INSTALLATION_STEPS.md](MACOS_APP_INSTALLATION_STEPS.md)** - Step-by-step instructions for installing the Daur AI macOS application bundle.

**[MACOS_QUICK_REFERENCE.md](MACOS_QUICK_REFERENCE.md)** - Quick reference guide for macOS-specific features and commands.

## Recommended Path

**For New Users**:
1. Start with [QUICK_START.md](QUICK_START.md) to understand the basics
2. Choose your platform-specific guide (macOS, Windows, Linux)
3. Follow the installation steps carefully
4. Run your first task to verify the installation

**For Developers**:
1. Use [DOCKER_QUICK_START.md](DOCKER_QUICK_START.md) for a containerized environment
2. Review the [Architecture Overview](../../PROJECT_SUMMARY.md)
3. Explore the [API documentation](../api/)
4. Read the [Development Guide](../guides/)

**For Production Deployment**:
1. Review [System Requirements](../../README.md#requirements)
2. Follow platform-specific installation guide
3. Consult [Deployment Documentation](../deployment/)
4. Set up monitoring and logging

## System Requirements

Before installing Daur AI, ensure your system meets the minimum requirements:

**Hardware**:
- CPU: 4+ cores recommended
- RAM: 8GB minimum, 16GB recommended
- Storage: 10GB free space
- GPU: Optional, improves vision processing

**Operating Systems**:
- macOS 10.15+ (Catalina or later)
- Windows 10/11 (64-bit)
- Linux (Ubuntu 20.04+, Debian 10+, or equivalent)

**Software**:
- Python 3.8 or higher
- Node.js 14+ (for web panel)
- Docker (optional, for containerized deployment)

## Common Issues

**Permission Errors on macOS**: Daur AI requires accessibility permissions to control input devices. Go to System Preferences → Security & Privacy → Privacy → Accessibility and grant permissions.

**Display Issues on Linux**: For headless environments, install Xvfb for virtual display support: `sudo apt-get install xvfb`

**Network Connectivity**: Ensure your firewall allows Daur AI to access the internet for AI model downloads and updates.

## Next Steps

After completing installation:

1. **Verify Installation** - Run the test suite to ensure everything works correctly
2. **Configure Settings** - Customize Daur AI for your specific needs
3. **Run First Task** - Try a simple automation task to familiarize yourself with the system
4. **Explore Features** - Review the [User Guides](../guides/) to learn about advanced capabilities

## Additional Resources

- [Main Documentation Index](../INDEX.md)
- [API Reference](../api/)
- [Deployment Guides](../deployment/)
- [Troubleshooting](../guides/troubleshooting.md)

## Support

If you encounter issues during installation:

- Check the [Troubleshooting Guide](../guides/troubleshooting.md)
- Search [GitHub Issues](https://github.com/daurfinance/Daur-AI-v1/issues)
- Contact support at support@daur-ai.com

---

*Last Updated: 2025-11-12*

