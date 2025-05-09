#!/bin/bash

# Daur-AI: Скрипт удаления для Linux
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

echo -e "${BLUE}====================================================${NC}"
echo -e "${BLUE}       Удаление Daur-AI                             ${NC}"
echo -e "${BLUE}====================================================${NC}"

# Запрос подтверждения
read -p "Вы действительно хотите удалить Daur-AI? Все данные будут потеряны [y/N]: " confirm
if [[ "$confirm" != [yY] ]]; then
    echo -e "${YELLOW}Операция отменена.${NC}"
    exit 0
fi

# Проверка сохранения пользовательских данных
SAVE_USER_DATA=false
read -p "Сохранить пользовательские данные (логи и настройки)? [y/N]: " save_data
if [[ "$save_data" == [yY] ]]; then
    SAVE_USER_DATA=true
    echo -e "${YELLOW}Пользовательские данные будут сохранены.${NC}"
fi

# Удаление исполняемого файла
echo -e "${YELLOW}Удаление исполняемого файла...${NC}"
if [ -f /usr/local/bin/daur-ai ]; then
    rm /usr/local/bin/daur-ai
    echo -e "${GREEN}Исполняемый файл удален.${NC}"
else
    echo -e "${YELLOW}Исполняемый файл не найден.${NC}"
fi

# Удаление записи из меню приложений
echo -e "${YELLOW}Удаление ярлыка из меню приложений...${NC}"
if [ -f /usr/share/applications/daur-ai.desktop ]; then
    rm /usr/share/applications/daur-ai.desktop
    echo -e "${GREEN}Ярлык удален.${NC}"
else
    echo -e "${YELLOW}Ярлык не найден.${NC}"
fi

# Удаление директории установки
echo -e "${YELLOW}Удаление файлов программы...${NC}"
INSTALL_DIR="/opt/daur-ai"

# Бэкап пользовательских данных
if [ "$SAVE_USER_DATA" = true ] && [ -d "$INSTALL_DIR" ]; then
    BACKUP_DIR="$HOME/daur-ai-backup-$(date +%Y%m%d%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    # Копирование логов и конфигурации
    if [ -d "$INSTALL_DIR/logs" ]; then
        cp -r "$INSTALL_DIR/logs" "$BACKUP_DIR/"
    fi
    
    if [ -d "$INSTALL_DIR/config" ]; then
        cp -r "$INSTALL_DIR/config" "$BACKUP_DIR/"
    fi
    
    echo -e "${GREEN}Пользовательские данные сохранены в $BACKUP_DIR${NC}"
fi

# Удаление директории установки
if [ -d "$INSTALL_DIR" ]; then
    rm -rf "$INSTALL_DIR"
    echo -e "${GREEN}Файлы программы удалены.${NC}"
else
    echo -e "${YELLOW}Директория программы не найдена.${NC}"
fi

# Проверка наличия пользовательских настроек в домашней директории
USER_CONFIG_DIR="$HOME/.daur_ai"
if [ -d "$USER_CONFIG_DIR" ]; then
    if [ "$SAVE_USER_DATA" = true ]; then
        if [ ! -d "$BACKUP_DIR" ]; then
            BACKUP_DIR="$HOME/daur-ai-backup-$(date +%Y%m%d%H%M%S)"
            mkdir -p "$BACKUP_DIR"
        fi
        cp -r "$USER_CONFIG_DIR" "$BACKUP_DIR/.daur_ai"
        echo -e "${GREEN}Пользовательские настройки сохранены в $BACKUP_DIR/.daur_ai${NC}"
    fi
    
    read -p "Удалить пользовательские настройки из $USER_CONFIG_DIR? [y/N]: " remove_config
    if [[ "$remove_config" == [yY] ]]; then
        rm -rf "$USER_CONFIG_DIR"
        echo -e "${GREEN}Пользовательские настройки удалены.${NC}"
    else
        echo -e "${YELLOW}Пользовательские настройки сохранены.${NC}"
    fi
fi

# Информация о завершении
echo -e "${GREEN}====================================================${NC}"
echo -e "${GREEN}Удаление Daur-AI завершено успешно!${NC}"
echo -e "${GREEN}====================================================${NC}"

exit 0
