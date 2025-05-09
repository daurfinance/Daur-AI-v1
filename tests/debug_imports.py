#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from pathlib import Path

# Путь к корню проекта
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
print(f"Корень проекта: {project_root}")
sys.path.insert(0, project_root)

# Проверка доступа к модулям
try:
    from src.logger.logger import setup_logger
    print("Модуль src.logger.logger успешно импортирован")
except ImportError as e:
    print(f"Ошибка импорта src.logger.logger: {e}")

try:
    from tests.base import BaseTestCase
    print("Модуль tests.base успешно импортирован")
except ImportError as e:
    print(f"Ошибка импорта tests.base: {e}")

# Проверка содержимого путей импорта
print("\nПути импорта:")
for p in sys.path:
    print(f" - {p}")

# Проверка файловой структуры
print("\nПроверка структуры файлов в src/logger:")
logger_dir = os.path.join(project_root, "src", "logger")
if os.path.exists(logger_dir):
    print(f"Директория существует: {logger_dir}")
    files = os.listdir(logger_dir)
    print(f"Файлы в директории: {files}")
else:
    print(f"Директория не существует: {logger_dir}")

# Проверка файлов тестов
print("\nПроверка структуры файлов в tests:")
tests_dir = os.path.join(project_root, "tests")
if os.path.exists(tests_dir):
    print(f"Директория существует: {tests_dir}")
    files = os.listdir(tests_dir)
    print(f"Файлы в директории: {files}")
else:
    print(f"Директория не существует: {tests_dir}")
