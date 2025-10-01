#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: Модуль конфигурации
Содержит функции для работы с конфигурацией приложения

Версия: 1.0
Дата: 09.05.2025
"""

import os
import json
import platform
from pathlib import Path

# Определение домашнего каталога пользователя на разных платформах
HOME_DIR = str(Path.home())
CONFIG_DIR = os.path.join(HOME_DIR, '.daur_ai')
DEFAULT_CONFIG_PATH = os.path.join(CONFIG_DIR, 'config.json')

# Значения по умолчанию
DEFAULT_CONFIG = {
    "model_path": os.path.join(CONFIG_DIR, "models", "distilbert"),
    "log_path": os.path.join(CONFIG_DIR, "logs"),
    "input_mode": "console",
    "encrypt_logs": False,
    "os_platform": platform.system(),
    
    # AI модели конфигурация
    "ai_models": {
        "ollama_host": "http://localhost:11434",
        "ollama_model": "llama3.2",
        "ollama_timeout": 30,
        "openai_model": "gpt-3.5-turbo",
        "openai_timeout": 30,
        "max_tokens": 1000,
        "temperature": 0.7
    },
    "ui_settings": {
        "console": {
            "prompt": "Daur-AI> ",
            "history_size": 100
        },
        "gui": {
            "theme": "dark",
            "window_size": "800x600"
        }
    },
    "sandbox_mode": {
        "enabled": False,
        "docker_image": "daur-ai-sandbox:latest"
    },
    "advanced": {
        "retry_attempts": 3,
        "model_inference_timeout": 5,
        "action_timeout": 10,
        "mouse_movement_speed": 0.5
    },
    "file_operations": {
        "allowed_extensions": [
            ".py", ".js", ".html", ".css", ".csv", 
            ".json", ".txt", ".docx", ".xlsx"
        ],
        "restricted_paths": [
            "/System", "/Windows", "/boot"
        ]
    }
}


def ensure_config_dir():
    """Проверка и создание конфигурационной директории"""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    os.makedirs(os.path.join(CONFIG_DIR, "models"), exist_ok=True)
    os.makedirs(os.path.join(CONFIG_DIR, "logs"), exist_ok=True)


def create_default_config():
    """Создание конфигурации по умолчанию"""
    ensure_config_dir()
    
    if not os.path.exists(DEFAULT_CONFIG_PATH):
        with open(DEFAULT_CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
        
        print(f"Создана конфигурация по умолчанию: {DEFAULT_CONFIG_PATH}")
    
    return DEFAULT_CONFIG


def load_config(config_path=None):
    """Загрузка конфигурации из файла"""
    if not config_path:
        config_path = DEFAULT_CONFIG_PATH
    
    # Проверка существования файла конфигурации
    if not os.path.exists(config_path):
        return create_default_config()
    
    # Загрузка существующей конфигурации
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Проверка наличия необходимых ключей и добавление отсутствующих
        for key, value in DEFAULT_CONFIG.items():
            if key not in config:
                config[key] = value
        
        return config
    
    except Exception as e:
        print(f"Ошибка загрузки конфигурации: {e}")
        return create_default_config()


def save_config(config, config_path=None):
    """Сохранение конфигурации в файл"""
    if not config_path:
        config_path = DEFAULT_CONFIG_PATH
    
    ensure_config_dir()
    
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
        return True
    except Exception as e:
        print(f"Ошибка сохранения конфигурации: {e}")
        return False
