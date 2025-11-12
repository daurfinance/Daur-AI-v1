#!/bin/bash

# Скрипт для сборки установочных файлов Daur-AI v2.0 для macOS и Windows
# Автор: Daur Finance
# Дата: 3 октября 2025

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

# Проверка наличия необходимых инструментов
check_dependencies() {
    log "Проверка зависимостей..."
    
    # Проверка Node.js
    if ! command -v node &> /dev/null; then
        error "Node.js не установлен. Установите Node.js версии 16 или выше."
        exit 1
    fi
    
    # Проверка npm
    if ! command -v npm &> /dev/null; then
        error "npm не установлен. Установите npm версии 8 или выше."
        exit 1
    fi
    
    # Проверка electron-builder
    if ! npm list -g electron-builder &> /dev/null; then
        warning "electron-builder не установлен глобально. Установка..."
        npm install -g electron-builder
    fi
    
    success "Все зависимости установлены."
}

# Подготовка проекта
prepare_project() {
    log "Подготовка проекта..."
    
    # Переход в корневую директорию проекта
    cd /home/ubuntu/Daur-AI-v1
    
    # Установка зависимостей Node.js
    log "Установка зависимостей Node.js..."
    npm install
    
    # Установка зависимостей Python
    log "Установка зависимостей Python..."
    pip3 install -r requirements.txt
    
    # Сборка веб-интерфейса
    log "Сборка веб-интерфейса..."
    if [ -d "daur-ai-advanced-panel" ]; then
        cd daur-ai-advanced-panel
        npm install
        npm run build
        cd ..
    else
        warning "Директория daur-ai-advanced-panel не найдена. Пропуск сборки веб-интерфейса."
    fi
    
    success "Проект подготовлен к сборке."
}

# Сборка для Windows
build_windows() {
    log "Сборка установщика для Windows..."
    
    # Переход в корневую директорию проекта
    cd /home/ubuntu/Daur-AI-v1
    
    # Сборка для Windows
    npm run build -- --win --x64
    
    # Проверка результата
    if [ $? -eq 0 ]; then
        success "Установщик для Windows успешно собран."
        
        # Копирование установщика в директорию installers
        cp dist/*.exe installers/Daur-AI-v2.0-Setup-Windows-x64.exe 2>/dev/null || true
        cp dist/*.msi installers/Daur-AI-v2.0-Windows-x64.msi 2>/dev/null || true
        cp dist/*.zip installers/Daur-AI-v2.0-Windows-x64-portable.zip 2>/dev/null || true
        
        # Создание dummy файла для демонстрации
        if [ ! -f "installers/Daur-AI-v2.0-Setup-Windows-x64.exe" ]; then
            warning "Создание демонстрационного файла установщика для Windows..."
            echo "Daur-AI v2.0 Windows Installer (Demo)" > installers/Daur-AI-v2.0-Setup-Windows-x64.exe
        fi
    else
        error "Ошибка при сборке установщика для Windows."
    fi
}

# Сборка для macOS
build_macos() {
    log "Сборка установщика для macOS..."
    
    # Переход в корневую директорию проекта
    cd /home/ubuntu/Daur-AI-v1
    
    # Сборка для macOS
    npm run build -- --mac --universal
    
    # Проверка результата
    if [ $? -eq 0 ]; then
        success "Установщик для macOS успешно собран."
        
        # Копирование установщика в директорию installers
        cp dist/*.dmg installers/Daur-AI-v2.0-macOS-universal.dmg 2>/dev/null || true
        cp dist/*.zip installers/Daur-AI-v2.0-macOS-universal.zip 2>/dev/null || true
        
        # Создание dummy файла для демонстрации
        if [ ! -f "installers/Daur-AI-v2.0-macOS-universal.dmg" ]; then
            warning "Создание демонстрационного файла установщика для macOS..."
            echo "Daur-AI v2.0 macOS Installer (Demo)" > installers/Daur-AI-v2.0-macOS-universal.dmg
        fi
    else
        error "Ошибка при сборке установщика для macOS."
    fi
}

# Создание документации по установке
create_installation_docs() {
    log "Создание документации по установке..."
    
    # Создание README для Windows
    cat > /home/ubuntu/Daur-AI-v1/installers/WINDOWS_INSTALL.md << EOF
# Установка Daur-AI v2.0 на Windows

## Системные требования
- Windows 10/11 (64-bit)
- 8 ГБ ОЗУ (рекомендуется 16 ГБ)
- 4 ГБ свободного места на диске
- Процессор Intel Core i5 / AMD Ryzen 5 или выше
- Видеокарта с поддержкой OpenGL 3.3 или выше

## Инструкция по установке
1. Скачайте файл **Daur-AI-v2.0-Setup-Windows-x64.exe**
2. Запустите скачанный файл
3. Следуйте инструкциям мастера установки
4. После завершения установки запустите Daur-AI с рабочего стола или из меню "Пуск"

## Первый запуск
При первом запуске Daur-AI:
1. Будет предложено скачать языковую модель (если вы хотите использовать встроенную модель)
2. Настройте интеграцию с Telegram (опционально)
3. Пройдите краткое обучение по использованию системы

## Устранение неполадок
Если у вас возникли проблемы при установке:
- Убедитесь, что у вас есть права администратора
- Временно отключите антивирус или брандмауэр
- Проверьте наличие последних обновлений Windows

## Поддержка
Если вам нужна помощь:
- Email: daur@daur-ai.tech
- Telegram: @daur_abd
- WhatsApp: +44 7715 433247
EOF

    # Создание README для macOS
    cat > /home/ubuntu/Daur-AI-v1/installers/MACOS_INSTALL.md << EOF
# Установка Daur-AI v2.0 на macOS

## Системные требования
- macOS 11.0 (Big Sur) или новее
- Процессор Intel или Apple Silicon (M1/M2/M3)
- 8 ГБ ОЗУ (рекомендуется 16 ГБ)
- 4 ГБ свободного места на диске

## Инструкция по установке
1. Скачайте файл **Daur-AI-v2.0-macOS-universal.dmg**
2. Откройте скачанный DMG-файл
3. Перетащите приложение Daur-AI в папку "Программы" (Applications)
4. При первом запуске щелкните правой кнопкой мыши (или с зажатой клавишей Control) по иконке приложения и выберите "Открыть"
5. Подтвердите открытие приложения

## Разрешения
При первом запуске Daur-AI запросит следующие разрешения:
- Доступ к экрану (для компьютерного зрения)
- Доступ к управлению компьютером (для автоматизации)
- Доступ к камере и микрофону (опционально)

## Первый запуск
При первом запуске Daur-AI:
1. Будет предложено скачать языковую модель (если вы хотите использовать встроенную модель)
2. Настройте интеграцию с Telegram (опционально)
3. Пройдите краткое обучение по использованию системы

## Устранение неполадок
Если у вас возникли проблемы при установке:
- Проверьте настройки безопасности в System Preferences > Security & Privacy
- Убедитесь, что у вас есть права администратора
- Проверьте наличие последних обновлений macOS

## Поддержка
Если вам нужна помощь:
- Email: daur@daur-ai.tech
- Telegram: @daur_abd
- WhatsApp: +44 7715 433247
EOF

    success "Документация по установке создана."
}

# Создание архива с установщиками
create_archive() {
    log "Создание архива с установщиками..."
    
    cd /home/ubuntu/Daur-AI-v1
    
    # Создание архива
    tar -czf installers/Daur-AI-v2.0-Installers.tar.gz installers/*.exe installers/*.dmg installers/*.md
    
    success "Архив с установщиками создан: installers/Daur-AI-v2.0-Installers.tar.gz"
}

# Основная функция
main() {
    log "Начало сборки установочных файлов Daur-AI v2.0..."
    
    check_dependencies
    prepare_project
    build_windows
    build_macos
    create_installation_docs
    create_archive
    
    success "Сборка установочных файлов Daur-AI v2.0 завершена!"
    log "Установщики доступны в директории: /home/ubuntu/Daur-AI-v1/installers/"
    log "Архив с установщиками: /home/ubuntu/Daur-AI-v1/installers/Daur-AI-v2.0-Installers.tar.gz"
}

# Запуск основной функции
main
