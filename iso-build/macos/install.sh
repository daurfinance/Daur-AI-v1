#!/bin/bash

# Daur-AI v2.0 Installer for macOS
# Created by Daur Finance
# Date: October 3, 2025

# Цвета для вывода
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Функция для вывода сообщений
log() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Заголовок
echo "====================================================="
echo "          Daur-AI v2.0 Installer for macOS           "
echo "====================================================="
echo ""

# Проверка системных требований
log "Checking system requirements..."

# Проверка версии macOS
OS_VERSION=$(sw_vers -productVersion)
if [[ $(echo $OS_VERSION | cut -d. -f1) -lt 11 ]]; then
    warning "Your macOS version ($OS_VERSION) is older than the recommended version (11.0+)."
    warning "Daur-AI may not work correctly on your system."
    read -p "Do you want to continue anyway? (y/n): " CONTINUE
    if [[ $CONTINUE != "y" && $CONTINUE != "Y" ]]; then
        error "Installation aborted."
        exit 1
    fi
else
    success "macOS version $OS_VERSION - Compatible"
fi

# Проверка наличия Python
if ! command -v python3 &> /dev/null; then
    error "Python 3 is not installed on your system."
    error "Please install Python 3.11 or newer from https://www.python.org/downloads/"
    error "After installing Python, run this installer again."
    open https://www.python.org/downloads/
    exit 1
else
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    success "Python $PYTHON_VERSION detected - Compatible"
fi

# Проверка наличия pip
if ! command -v pip3 &> /dev/null; then
    warning "pip3 is not installed. Installing pip..."
    python3 -m ensurepip --upgrade
    if [ $? -ne 0 ]; then
        error "Failed to install pip. Please install pip manually and run this installer again."
        exit 1
    fi
fi

# Создание директории установки
log "Creating installation directory..."
INSTALL_DIR="$HOME/Applications/Daur-AI"
mkdir -p "$INSTALL_DIR"

# Копирование файлов
log "Copying files..."
cp -r app/* "$INSTALL_DIR/"
mkdir -p "$INSTALL_DIR/docs"
cp -r docs/* "$INSTALL_DIR/docs/"
mkdir -p "$INSTALL_DIR/resources"
cp -r resources/* "$INSTALL_DIR/resources/"

# Установка зависимостей
log "Installing dependencies..."
pip3 install --upgrade pip
pip3 install -r "$INSTALL_DIR/requirements.txt"

# Создание приложения
log "Creating application bundle..."
APP_BUNDLE="$HOME/Applications/Daur-AI.app"
mkdir -p "$APP_BUNDLE/Contents/MacOS"
mkdir -p "$APP_BUNDLE/Contents/Resources"

# Создание Info.plist
cat > "$APP_BUNDLE/Contents/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>Daur-AI</string>
    <key>CFBundleIconFile</key>
    <string>AppIcon</string>
    <key>CFBundleIdentifier</key>
    <string>com.daurfinance.daur-ai</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>Daur-AI</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>2.0.0</string>
    <key>CFBundleVersion</key>
    <string>2.0.0</string>
    <key>LSMinimumSystemVersion</key>
    <string>11.0.0</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>NSPrincipalClass</key>
    <string>NSApplication</string>
</dict>
</plist>
EOF

# Создание исполняемого файла
cat > "$APP_BUNDLE/Contents/MacOS/Daur-AI" << EOF
#!/bin/bash
cd "$INSTALL_DIR"
python3 main.py
EOF

# Установка прав на исполнение
chmod +x "$APP_BUNDLE/Contents/MacOS/Daur-AI"

# Копирование иконки
cp "$INSTALL_DIR/resources/icon.icns" "$APP_BUNDLE/Contents/Resources/AppIcon.icns"

# Создание ссылки в Applications
ln -sf "$APP_BUNDLE" "/Applications/Daur-AI.app"

# Завершение установки
success "Installation completed successfully!"
echo ""
echo "====================================================="
echo "Daur-AI v2.0 has been installed to:"
echo "$INSTALL_DIR"
echo ""
echo "The application bundle is available at:"
echo "$APP_BUNDLE"
echo ""
echo "A link has been created in your Applications folder."
echo ""
echo "To launch Daur-AI, open the application from Launchpad"
echo "or run: open \"$APP_BUNDLE\""
echo ""
echo "For more information, see the documentation in:"
echo "$INSTALL_DIR/docs"
echo "====================================================="
echo ""

# Запрос на запуск приложения
read -p "Would you like to launch Daur-AI now? (y/n): " LAUNCH
if [[ $LAUNCH == "y" || $LAUNCH == "Y" ]]; then
    open "$APP_BUNDLE"
fi
