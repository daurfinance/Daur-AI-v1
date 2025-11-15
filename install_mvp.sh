#!/bin/bash
# Daur AI MVP Installation Script
# Installs all dependencies and sets up local LLM

set -e

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                                                           ║"
echo "║         🤖 Daur AI MVP Installation 🤖                    ║"
echo "║                                                           ║"
echo "║              100% Local LLM Solution                      ║"
echo "║                                                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Detect OS
OS="$(uname -s)"
echo "🖥️  Detected OS: $OS"
echo ""

# Check Python
echo "🐍 Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✅ Python $PYTHON_VERSION found"
echo ""

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements-mvp.txt
echo "✅ Python dependencies installed"
echo ""

# Install Tesseract OCR
echo "🔍 Installing Tesseract OCR..."
if [ "$OS" = "Darwin" ]; then
    # macOS
    if command -v brew &> /dev/null; then
        brew install tesseract
        echo "✅ Tesseract installed via Homebrew"
    else
        echo "⚠️  Homebrew not found. Please install Tesseract manually:"
        echo "   https://github.com/tesseract-ocr/tesseract"
    fi
elif [ "$OS" = "Linux" ]; then
    # Linux
    if command -v apt-get &> /dev/null; then
        sudo apt-get update
        sudo apt-get install -y tesseract-ocr
        echo "✅ Tesseract installed via apt"
    elif command -v yum &> /dev/null; then
        sudo yum install -y tesseract
        echo "✅ Tesseract installed via yum"
    else
        echo "⚠️  Package manager not found. Please install Tesseract manually."
    fi
else
    echo "⚠️  Please install Tesseract manually for your OS"
fi
echo ""

# Install Ollama
echo "🤖 Installing Ollama..."
if ! command -v ollama &> /dev/null; then
    if [ "$OS" = "Darwin" ]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install ollama
            echo "✅ Ollama installed via Homebrew"
        else
            echo "⚠️  Homebrew not found. Installing Ollama manually..."
            curl -fsSL https://ollama.com/install.sh | sh
        fi
    elif [ "$OS" = "Linux" ]; then
        # Linux
        curl -fsSL https://ollama.com/install.sh | sh
        echo "✅ Ollama installed"
    else
        echo "⚠️  Please install Ollama manually from https://ollama.com/download"
    fi
else
    echo "✅ Ollama already installed"
fi
echo ""

# Start Ollama server
echo "🚀 Starting Ollama server..."
if [ "$OS" = "Darwin" ]; then
    # macOS - start as background service
    brew services start ollama 2>/dev/null || ollama serve &
elif [ "$OS" = "Linux" ]; then
    # Linux - start in background
    nohup ollama serve > /dev/null 2>&1 &
fi

# Wait for Ollama to start
echo "⏳ Waiting for Ollama server to start..."
sleep 5

# Check if Ollama is running
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "✅ Ollama server is running"
else
    echo "⚠️  Ollama server may not be running. Please start it manually:"
    echo "   ollama serve"
fi
echo ""

# Download models
echo "⬇️  Downloading AI models (this may take 5-10 minutes)..."
echo ""

echo "📥 Downloading Llama 3.2 3B (main model)..."
ollama pull llama3.2:3b
echo "✅ Llama 3.2 3B downloaded"
echo ""

echo "📥 Downloading LLaVA (vision model)..."
ollama pull llava
echo "✅ LLaVA downloaded"
echo ""

echo "📥 Downloading CodeLlama 7B (coding model)..."
ollama pull codellama:7b
echo "✅ CodeLlama downloaded"
echo ""

# Verify installation
echo "🔍 Verifying installation..."
echo ""

# Check models
MODELS=$(ollama list | grep -E 'llama3.2:3b|llava|codellama:7b' | wc -l)
if [ "$MODELS" -ge 3 ]; then
    echo "✅ All models installed successfully"
else
    echo "⚠️  Some models may be missing. Run 'ollama list' to check."
fi
echo ""

# Installation complete
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                                                           ║"
echo "║              ✅ Installation Complete! ✅                 ║"
echo "║                                                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""
echo "🎉 Daur AI MVP is ready to use!"
echo ""
echo "To start the agent:"
echo "  python3 mvp_chat.py"
echo ""
echo "Or run a task directly:"
echo "  python3 -c 'from src.mvp import get_mvp_agent; import asyncio; asyncio.run(get_mvp_agent().execute_task(\"open Safari\"))'"
echo ""
echo "For help:"
echo "  python3 mvp_chat.py"
echo "  Then type: /help"
echo ""

