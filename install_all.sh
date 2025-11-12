#!/bin/bash
# Complete Daur-AI Installation

set -e

echo "🚀 Daur-AI v2.0 Installation"
echo "============================"

# Detect OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
    echo "✓ Linux detected"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
    echo "✓ macOS detected"
else
    echo "❌ Unsupported OS"
    exit 1
fi

# Check Python
python3 --version || { echo "❌ Python 3 required"; exit 1; }

# Create venv
[ -d "venv" ] || python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install dependencies
pip install -r requirements.txt

# Platform-specific
if [ "$OS" == "macos" ]; then
    pip install pyobjc-framework-Cocoa
elif [ "$OS" == "linux" ]; then
    pip install python-xlib
fi

# Install Daur-AI
pip install -e .

echo "✅ Installation complete!"
echo ""
echo "Run:  source venv/bin/activate && python run_demo.py"
