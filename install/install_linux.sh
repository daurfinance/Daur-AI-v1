#!/bin/bash

# Daur-AI: Скрипт установки для Linux
# Версия: 1.0
# Дата: 09.05.2025

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Проверка привилегий суперпользователя
if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}Ошибка: этот скрипт требует привилегий суперпользователя.${NC}"
  echo "Пожалуйста, запустите с использованием sudo."
  exit 1
fi

# Получение директории скрипта
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}====================================================${NC}"
echo -e "${BLUE}       Установка Daur-AI для Linux                  ${NC}"
echo -e "${BLUE}====================================================${NC}"

# Проверка Python
echo -e "${YELLOW}Проверка Python...${NC}"
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
else
    echo -e "${RED}Python не найден. Пожалуйста, установите Python 3.8 или выше.${NC}"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD -c 'import sys; print(sys.version_info.major, sys.version_info.minor)')
read -r PYTHON_MAJOR PYTHON_MINOR <<< "$PYTHON_VERSION"

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    echo -e "${RED}Требуется Python 3.8 или выше. Найдена версия $PYTHON_MAJOR.$PYTHON_MINOR${NC}"
    exit 1
fi

echo -e "${GREEN}Python $PYTHON_MAJOR.$PYTHON_MINOR найден.${NC}"

# Проверка виртуального окружения
echo -e "${YELLOW}Создание виртуального окружения...${NC}"
VENV_DIR="/opt/daur-ai/venv"
$PYTHON_CMD -m venv "$VENV_DIR" || {
    echo -e "${RED}Не удалось создать виртуальное окружение.${NC}"
    echo "Пожалуйста, убедитесь, что у вас установлен пакет python3-venv:"
    echo "sudo apt-get install python3-venv"
    exit 1
}

# Активация виртуального окружения
source "$VENV_DIR/bin/activate" || {
    echo -e "${RED}Не удалось активировать виртуальное окружение.${NC}"
    exit 1
}

# Установка требуемых пакетов
echo -e "${YELLOW}Установка зависимостей...${NC}"
pip install --upgrade pip wheel setuptools
pip install -r "$PROJECT_DIR/requirements.txt" || {
    echo -e "${RED}Не удалось установить зависимости.${NC}"
    exit 1
}

# Копирование файлов проекта
echo -e "${YELLOW}Копирование файлов Daur-AI...${NC}"
INSTALL_DIR="/opt/daur-ai"
mkdir -p "$INSTALL_DIR"
cp -r "$PROJECT_DIR/src" "$INSTALL_DIR/"
cp -r "$PROJECT_DIR/config" "$INSTALL_DIR/"
cp -r "$PROJECT_DIR/docs" "$INSTALL_DIR/"
cp "$PROJECT_DIR/LICENSE" "$INSTALL_DIR/"
cp "$PROJECT_DIR/README.md" "$INSTALL_DIR/"

# Создание директорий для логов и моделей
mkdir -p "$INSTALL_DIR/logs"
mkdir -p "$INSTALL_DIR/models"
chmod -R 755 "$INSTALL_DIR"

# Создание исполняемого скрипта
echo -e "${YELLOW}Создание исполняемого файла...${NC}"
cat > /usr/local/bin/daur-ai << 'EOF'
#!/bin/bash
source /opt/daur-ai/venv/bin/activate
python /opt/daur-ai/src/main.py "$@"
EOF

chmod +x /usr/local/bin/daur-ai

# Создание .desktop файла
echo -e "${YELLOW}Создание ярлыка в меню приложений...${NC}"
cat > /usr/share/applications/daur-ai.desktop << 'EOF'
[Desktop Entry]
Type=Application
Name=Daur-AI
GenericName=ИИ-агент
Comment=Универсальный автономный ИИ-агент
Exec=daur-ai
Terminal=true
Categories=Utility;AI;Productivity;
EOF

# Информация о завершении
echo -e "${GREEN}====================================================${NC}"
echo -e "${GREEN}Установка Daur-AI завершена успешно!${NC}"
echo -e "${GREEN}====================================================${NC}"
echo -e "Вы можете запустить Daur-AI следующими способами:"
echo -e "1. Через терминал: ${BLUE}daur-ai${NC}"
echo -e "2. Через меню приложений (Утилиты > Daur-AI)"
echo -e ""
echo -e "Документация доступна в директории: ${BLUE}/opt/daur-ai/docs${NC}"
echo -e "${GREEN}====================================================${NC}"

exit 0
