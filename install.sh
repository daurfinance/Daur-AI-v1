#!/bin/bash

# Daur-AI Installation Script
# Автоматическая установка всех зависимостей и настройка системы

set -e

echo "🤖 Daur-AI Installation Script"
echo "=============================="

# Определяем ОС
OS="unknown"
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    OS="windows"
fi

echo "🔍 Обнаружена ОС: $OS"

# Проверяем Python
echo "🐍 Проверка Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 не найден. Установите Python 3.8+ и повторите попытку."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Python $PYTHON_VERSION найден"

# Проверяем Node.js
echo "📦 Проверка Node.js..."
if ! command -v node &> /dev/null; then
    echo "⚠️ Node.js не найден. Устанавливаем..."
    
    if [[ "$OS" == "linux" ]]; then
        curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
        sudo apt-get install -y nodejs
    elif [[ "$OS" == "macos" ]]; then
        if command -v brew &> /dev/null; then
            brew install node
        else
            echo "❌ Установите Homebrew или Node.js вручную"
            exit 1
        fi
    fi
else
    NODE_VERSION=$(node --version)
    echo "✅ Node.js $NODE_VERSION найден"
fi

# Проверяем npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm не найден"
    exit 1
fi

# Устанавливаем системные зависимости
echo "📚 Установка системных зависимостей..."

if [[ "$OS" == "linux" ]]; then
    echo "🐧 Установка для Linux..."
    
    # Обновляем пакеты
    sudo apt update
    
    # Основные зависимости
    sudo apt install -y \
        python3-pip \
        python3-venv \
        python3-dev \
        build-essential \
        tesseract-ocr \
        tesseract-ocr-rus \
        ffmpeg \
        git \
        curl \
        wget \
        unzip
    
    # Зависимости для GUI (если нужны)
    sudo apt install -y \
        python3-tk \
        xvfb \
        x11-utils \
        libgtk-3-dev \
        libwebkit2gtk-4.0-dev
        
elif [[ "$OS" == "macos" ]]; then
    echo "🍎 Установка для macOS..."
    
    if command -v brew &> /dev/null; then
        brew install tesseract tesseract-lang ffmpeg
    else
        echo "⚠️ Homebrew не найден. Некоторые зависимости могут отсутствовать."
    fi
fi

# Создаем виртуальное окружение
echo "🔧 Создание виртуального окружения..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Активируем виртуальное окружение
source venv/bin/activate

# Обновляем pip
pip install --upgrade pip

# Устанавливаем Python зависимости
echo "📦 Установка Python зависимостей..."
pip install -r requirements.txt

# Устанавливаем Ollama (если нужно)
echo "🧠 Проверка Ollama..."
if ! command -v ollama &> /dev/null; then
    echo "⚠️ Ollama не найдена. Устанавливаем..."
    curl -fsSL https://ollama.ai/install.sh | sh
    
    # Запускаем Ollama
    if [[ "$OS" == "linux" ]]; then
        sudo systemctl start ollama
        sudo systemctl enable ollama
    fi
    
    echo "📥 Загружаем базовую модель..."
    ollama pull llama3.2:1b
else
    echo "✅ Ollama уже установлена"
fi

# Устанавливаем Node.js зависимости
echo "📦 Установка Node.js зависимостей..."
npm install

# Устанавливаем зависимости для веб-панели
echo "🌐 Настройка веб-панели..."
cd daur-ai-advanced-panel
npm install
npm run build
cd ..

# Создаем конфигурационные файлы
echo "⚙️ Создание конфигурации..."

# Создаем директории
mkdir -p logs
mkdir -p temp
mkdir -p assets

# Создаем базовую конфигурацию Telegram
if [ ! -f "telegram_config.json" ]; then
    cat > telegram_config.json << EOF
{
    "telegram": {
        "bot_token": "",
        "allowed_users": [],
        "features": {
            "voice_recognition": true,
            "file_processing": true,
            "image_analysis": true
        }
    },
    "ai_agent": {
        "auto_start": true,
        "default_model": "ollama",
        "fallback_model": "simple"
    },
    "web_interface": {
        "enabled": true,
        "port": 8000,
        "auto_open": false
    },
    "logging": {
        "level": "INFO",
        "file": "logs/daur_ai.log"
    }
}
EOF
    echo "✅ Создан telegram_config.json"
fi

# Создаем скрипты запуска
echo "🚀 Создание скриптов запуска..."

# Скрипт для Linux/macOS
cat > start_daur_ai.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
python3 daur_ai_launcher.py
EOF

chmod +x start_daur_ai.sh

# Скрипт для Windows
cat > start_daur_ai.bat << 'EOF'
@echo off
cd /d "%~dp0"
call venv\Scripts\activate.bat
python daur_ai_launcher.py
pause
EOF

# Создаем desktop файл для Linux
if [[ "$OS" == "linux" ]]; then
    INSTALL_DIR=$(pwd)
    cat > daur-ai.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Daur-AI
Comment=Autonomous AI Agent with Computer Vision
Exec=$INSTALL_DIR/start_daur_ai.sh
Icon=$INSTALL_DIR/assets/icon.png
Terminal=false
Categories=Office;Development;
EOF
    
    # Устанавливаем desktop файл
    if [ -d "$HOME/.local/share/applications" ]; then
        cp daur-ai.desktop "$HOME/.local/share/applications/"
        echo "✅ Создан ярлык в меню приложений"
    fi
fi

# Проверяем установку
echo "🔍 Проверка установки..."

# Тестируем импорты Python
python3 -c "
try:
    import sys
    sys.path.append('src')
    from agent.integrated_ai_agent import IntegratedAIAgent
    from telegram.daur_ai_bot import DaurAITelegramBot
    print('✅ Python модули импортированы успешно')
except ImportError as e:
    print(f'❌ Ошибка импорта: {e}')
    exit(1)
"

echo ""
echo "🎉 Установка завершена успешно!"
echo "================================"
echo ""
echo "📋 Что дальше:"
echo "1. Отредактируйте telegram_config.json и укажите TELEGRAM_BOT_TOKEN"
echo "2. Запустите систему: ./start_daur_ai.sh (или start_daur_ai.bat на Windows)"
echo "3. Откройте веб-панель: http://localhost:5174"
echo ""
echo "📚 Документация:"
echo "   README.md - Полное руководство"
echo "   docs/ - Дополнительная документация"
echo ""
echo "🆘 Поддержка:"
echo "   GitHub: https://github.com/daurfinance/Daur-AI-v1"
echo "   Issues: https://github.com/daurfinance/Daur-AI-v1/issues"
echo ""
echo "🚀 Готово к использованию!"
