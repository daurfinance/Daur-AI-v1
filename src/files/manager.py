#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: Менеджер файлов
Отвечает за операции с файлами и директориями

Версия: 1.0
Дата: 09.05.2025
"""

import os
import sys
import shutil
import logging
import pathlib
import tempfile
from typing import List, Dict, Union, Optional


class FileManager:
    """
    Менеджер файловых операций
    Отвечает за безопасное создание, чтение, запись и удаление файлов
    """
    
    def __init__(self, allowed_extensions=None, restricted_paths=None):
        """
        Инициализация менеджера файлов
        
        Args:
            allowed_extensions (list): Разрешенные расширения файлов
            restricted_paths (list): Запрещенные пути
        """
        self.logger = logging.getLogger('daur_ai.files')
        
        # Настройка разрешенных расширений
        self.allowed_extensions = allowed_extensions or [
            # Код
            ".py", ".js", ".html", ".css", ".jsx", ".ts", ".tsx", 
            # Данные
            ".csv", ".json", ".txt", ".md", ".xml", ".yaml", ".yml",
            # Документы
            ".docx", ".xlsx", ".pdf", ".rtf",
            # Изображения
            ".jpg", ".jpeg", ".png", ".gif", ".svg",
            # Конфигурация
            ".ini", ".cfg", ".conf", ".config", ".env"
        ]
        
        # Настройка запрещенных путей
        self.restricted_paths = restricted_paths or self._get_default_restricted_paths()
        
        self.logger.info("Менеджер файлов инициализирован")
        self.logger.debug(f"Разрешенные расширения: {', '.join(self.allowed_extensions)}")
    
    def _get_default_restricted_paths(self) -> List[str]:
        """
        Получение списка запрещенных путей по умолчанию
        
        Returns:
            List[str]: Список запрещенных путей
        """
        # Основные системные пути, которые не следует изменять
        if sys.platform == "win32":
            return [
                "C:\\Windows", 
                "C:\\Program Files", 
                "C:\\Program Files (x86)",
                "C:\\ProgramData"
            ]
        elif sys.platform == "darwin":
            return [
                "/System", 
                "/Library", 
                "/bin", 
                "/sbin", 
                "/usr"
            ]
        else:  # Linux и другие Unix-подобные
            return [
                "/bin", 
                "/sbin", 
                "/usr/bin", 
                "/usr/sbin", 
                "/etc", 
                "/var", 
                "/boot"
            ]
    
    def _is_path_allowed(self, path: str) -> bool:
        """
        Проверка допустимости пути
        
        Args:
            path (str): Путь для проверки
            
        Returns:
            bool: True если путь допустим, иначе False
        """
        path = os.path.abspath(path)
        
        # Проверка запрещенных путей
        for restricted in self.restricted_paths:
            if path.startswith(restricted):
                self.logger.warning(f"Попытка доступа к запрещенному пути: {path}")
                return False
        
        # Проверка расширения для файлов
        if os.path.isfile(path) or "." in os.path.basename(path):
            ext = os.path.splitext(path)[1].lower()
            if ext not in self.allowed_extensions:
                self.logger.warning(f"Попытка доступа к файлу с запрещенным расширением: {path}")
                return False
        
        return True
    
    def execute_action(self, action: Dict) -> Union[bool, Dict]:
        """
        Выполнение файловой операции
        
        Args:
            action (dict): Словарь с описанием операции
                {
                    "action": "file_create",
                    "path": "/path/to/file.txt",
                    "content": "Hello, world!"
                }
        
        Returns:
            bool or dict: Результат выполнения операции
        """
        action_type = action.get("action", "").lower()
        
        try:
            # Проверка наличия пути
            if "path" not in action and action_type != "file_list_dir":
                self.logger.error("Отсутствует обязательный параметр 'path'")
                return False
            
            # Операции с файлами
            if action_type == "file_create":
                return self.create_file(
                    path=action.get("path"),
                    content=action.get("content", "")
                )
            
            elif action_type == "file_read":
                return self.read_file(
                    path=action.get("path")
                )
            
            elif action_type == "file_write":
                return self.write_file(
                    path=action.get("path"),
                    content=action.get("content", ""),
                    append=action.get("append", False)
                )
            
            elif action_type == "file_delete":
                return self.delete_file(
                    path=action.get("path")
                )
            
            elif action_type == "file_copy":
                return self.copy_file(
                    source=action.get("source"),
                    destination=action.get("destination")
                )
            
            elif action_type == "file_move":
                return self.move_file(
                    source=action.get("source"),
                    destination=action.get("destination")
                )
            
            elif action_type == "file_rename":
                return self.rename_file(
                    path=action.get("path"),
                    new_name=action.get("new_name")
                )
            
            # Операции с директориями
            elif action_type == "file_create_dir":
                return self.create_directory(
                    path=action.get("path")
                )
            
            elif action_type == "file_delete_dir":
                return self.delete_directory(
                    path=action.get("path"),
                    recursive=action.get("recursive", False)
                )
            
            elif action_type == "file_list_dir":
                return self.list_directory(
                    path=action.get("path", os.getcwd())
                )
            
            else:
                self.logger.warning(f"Неизвестная файловая операция: {action_type}")
                return False
            
        except Exception as e:
            self.logger.error(f"Ошибка при выполнении файловой операции {action_type}: {e}", exc_info=True)
            return False
    
    def create_file(self, path: str, content: str = "") -> bool:
        """
        Создание файла с содержимым
        
        Args:
            path (str): Путь к файлу
            content (str): Содержимое файла
            
        Returns:
            bool: Результат операции
        """
        try:
            # Проверка допустимости пути
            if not self._is_path_allowed(path):
                return False
            
            # Создание директорий при необходимости
            directory = os.path.dirname(path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
            
            # Запись в файл
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.logger.info(f"Создан файл: {path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка создания файла {path}: {e}")
            return False
    
    def read_file(self, path: str) -> Union[Dict, bool]:
        """
        Чтение содержимого файла
        
        Args:
            path (str): Путь к файлу
            
        Returns:
            dict or bool: Содержимое файла или False в случае ошибки
        """
        try:
            # Проверка допустимости пути
            if not self._is_path_allowed(path):
                return False
            
            # Проверка существования файла
            if not os.path.exists(path):
                self.logger.error(f"Файл не существует: {path}")
                return False
            
            # Проверка, что это файл, а не директория
            if not os.path.isfile(path):
                self.logger.error(f"Указанный путь не является файлом: {path}")
                return False
            
            # Чтение файла
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.logger.info(f"Прочитан файл: {path}")
            return {
                "path": path,
                "content": content,
                "size": os.path.getsize(path),
                "modified": os.path.getmtime(path)
            }
            
        except Exception as e:
            self.logger.error(f"Ошибка чтения файла {path}: {e}")
            return False
    
    def write_file(self, path: str, content: str, append: bool = False) -> bool:
        """
        Запись в файл
        
        Args:
            path (str): Путь к файлу
            content (str): Содержимое для записи
            append (bool): Дописать в конец файла вместо перезаписи
            
        Returns:
            bool: Результат операции
        """
        try:
            # Проверка допустимости пути
            if not self._is_path_allowed(path):
                return False
            
            # Создание директорий при необходимости
            directory = os.path.dirname(path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
            
            # Запись в файл
            mode = 'a' if append else 'w'
            with open(path, mode, encoding='utf-8') as f:
                f.write(content)
            
            action = "Дописан" if append else "Записан"
            self.logger.info(f"{action} файл: {path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка записи в файл {path}: {e}")
            return False
    
    def delete_file(self, path: str) -> bool:
        """
        Удаление файла
        
        Args:
            path (str): Путь к удаляемому файлу
            
        Returns:
            bool: Результат операции
        """
        try:
            # Проверка допустимости пути
            if not self._is_path_allowed(path):
                return False
            
            # Проверка существования файла
            if not os.path.exists(path):
                self.logger.error(f"Файл не существует: {path}")
                return False
            
            # Проверка, что это файл, а не директория
            if not os.path.isfile(path):
                self.logger.error(f"Указанный путь не является файлом: {path}")
                return False
            
            # Удаление файла
            os.remove(path)
            
            self.logger.info(f"Удален файл: {path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка удаления файла {path}: {e}")
            return False
    
    def copy_file(self, source: str, destination: str) -> bool:
        """
        Копирование файла
        
        Args:
            source (str): Путь к исходному файлу
            destination (str): Путь к месту назначения
            
        Returns:
            bool: Результат операции
        """
        try:
            # Проверка допустимости путей
            if not self._is_path_allowed(source) or not self._is_path_allowed(destination):
                return False
            
            # Проверка существования исходного файла
            if not os.path.exists(source):
                self.logger.error(f"Исходный файл не существует: {source}")
                return False
            
            # Создание директорий назначения при необходимости
            dest_dir = os.path.dirname(destination)
            if dest_dir and not os.path.exists(dest_dir):
                os.makedirs(dest_dir, exist_ok=True)
            
            # Копирование файла
            shutil.copy2(source, destination)
            
            self.logger.info(f"Скопирован файл: {source} -> {destination}")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка копирования файла {source} в {destination}: {e}")
            return False
    
    def move_file(self, source: str, destination: str) -> bool:
        """
        Перемещение файла
        
        Args:
            source (str): Путь к исходному файлу
            destination (str): Путь к месту назначения
            
        Returns:
            bool: Результат операции
        """
        try:
            # Проверка допустимости путей
            if not self._is_path_allowed(source) or not self._is_path_allowed(destination):
                return False
            
            # Проверка существования исходного файла
            if not os.path.exists(source):
                self.logger.error(f"Исходный файл не существует: {source}")
                return False
            
            # Создание директорий назначения при необходимости
            dest_dir = os.path.dirname(destination)
            if dest_dir and not os.path.exists(dest_dir):
                os.makedirs(dest_dir, exist_ok=True)
            
            # Перемещение файла
            shutil.move(source, destination)
            
            self.logger.info(f"Перемещен файл: {source} -> {destination}")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка перемещения файла {source} в {destination}: {e}")
            return False
    
    def rename_file(self, path: str, new_name: str) -> bool:
        """
        Переименование файла
        
        Args:
            path (str): Путь к файлу
            new_name (str): Новое имя (без пути)
            
        Returns:
            bool: Результат операции
        """
        try:
            # Проверка допустимости пути
            if not self._is_path_allowed(path):
                return False
            
            # Проверка существования файла
            if not os.path.exists(path):
                self.logger.error(f"Файл не существует: {path}")
                return False
            
            # Формирование пути с новым именем
            directory = os.path.dirname(path)
            new_path = os.path.join(directory, new_name)
            
            # Проверка допустимости нового пути
            if not self._is_path_allowed(new_path):
                return False
            
            # Переименование файла
            os.rename(path, new_path)
            
            self.logger.info(f"Переименован файл: {path} -> {new_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка переименования файла {path} в {new_name}: {e}")
            return False
    
    def create_directory(self, path: str) -> bool:
        """
        Создание директории
        
        Args:
            path (str): Путь к директории
            
        Returns:
            bool: Результат операции
        """
        try:
            # Проверка допустимости пути
            if not self._is_path_allowed(path):
                return False
            
            # Создание директории
            os.makedirs(path, exist_ok=True)
            
            self.logger.info(f"Создана директория: {path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка создания директории {path}: {e}")
            return False
    
    def delete_directory(self, path: str, recursive: bool = False) -> bool:
        """
        Удаление директории
        
        Args:
            path (str): Путь к директории
            recursive (bool): Рекурсивное удаление содержимого
            
        Returns:
            bool: Результат операции
        """
        try:
            # Проверка допустимости пути
            if not self._is_path_allowed(path):
                return False
            
            # Проверка существования директории
            if not os.path.exists(path):
                self.logger.error(f"Директория не существует: {path}")
                return False
            
            # Проверка, что это директория
            if not os.path.isdir(path):
                self.logger.error(f"Указанный путь не является директорией: {path}")
                return False
            
            # Удаление директории
            if recursive:
                shutil.rmtree(path)
            else:
                os.rmdir(path)  # Только для пустых директорий
            
            self.logger.info(f"Удалена директория: {path} (рекурсивно: {recursive})")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка удаления директории {path}: {e}")
            return False
    
    def list_directory(self, path: str) -> Union[Dict, bool]:
        """
        Получение списка файлов в директории
        
        Args:
            path (str): Путь к директории
            
        Returns:
            dict or bool: Список файлов или False в случае ошибки
        """
        try:
            # Проверка допустимости пути
            if not self._is_path_allowed(path):
                return False
            
            # Абсолютный путь
            abs_path = os.path.abspath(path)
            
            # Проверка существования директории
            if not os.path.exists(abs_path):
                self.logger.error(f"Директория не существует: {abs_path}")
                return False
            
            # Проверка, что это директория
            if not os.path.isdir(abs_path):
                self.logger.error(f"Указанный путь не является директорией: {abs_path}")
                return False
            
            # Получение списка файлов и директорий
            items = os.listdir(abs_path)
            
            files = []
            directories = []
            
            for item in items:
                item_path = os.path.join(abs_path, item)
                if os.path.isdir(item_path):
                    directories.append({
                        "name": item,
                        "path": item_path,
                        "type": "directory",
                        "modified": os.path.getmtime(item_path)
                    })
                else:
                    files.append({
                        "name": item,
                        "path": item_path,
                        "type": "file",
                        "size": os.path.getsize(item_path),
                        "extension": os.path.splitext(item)[1].lower(),
                        "modified": os.path.getmtime(item_path)
                    })
            
            self.logger.info(f"Получен список файлов: {abs_path}")
            return {
                "path": abs_path,
                "directories": directories,
                "files": files
            }
            
        except Exception as e:
            self.logger.error(f"Ошибка получения списка файлов в {path}: {e}")
            return False
