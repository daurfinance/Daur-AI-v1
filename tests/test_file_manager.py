#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: Тесты менеджера файлов
Проверяет функциональность модуля управления файлами

Версия: 1.0
Дата: 09.05.2025
"""

import os
import shutil
import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path

from tests.base import BaseTestCase
from src.files.manager import FileManager


class TestFileManager(BaseTestCase):
    """
    Тесты для проверки работы менеджера файлов
    """
    
    def setUp(self):
        """Инициализация перед каждым тестом"""
        super().setUp()
        
        # Создание тестовой директории для файлов
        self.test_files_dir = self.test_dir / "test_files"
        os.makedirs(self.test_files_dir, exist_ok=True)
        
        # Инициализация менеджера файлов с тестовыми настройками
        self.file_manager = FileManager(
            allowed_extensions=[".txt", ".py", ".md", ".json"],
            restricted_paths=[str(self.test_dir / "restricted")]
        )
        
        # Создание директории с ограниченным доступом
        self.restricted_dir = self.test_dir / "restricted"
        os.makedirs(self.restricted_dir, exist_ok=True)
    
    def test_initialization(self):
        """Проверка инициализации менеджера файлов"""
        # Проверка настройки разрешенных расширений
        self.assertIn(".txt", self.file_manager.allowed_extensions)
        self.assertIn(".py", self.file_manager.allowed_extensions)
        
        # Проверка настройки запрещенных путей
        self.assertIn(str(self.restricted_dir), self.file_manager.restricted_paths)
    
    def test_path_validation(self):
        """Проверка валидации путей"""
        # Допустимый путь
        valid_path = self.test_files_dir / "test.txt"
        self.assertTrue(self.file_manager._is_path_allowed(str(valid_path)))
        
        # Недопустимый путь (запрещенная директория)
        invalid_path = self.restricted_dir / "test.txt"
        self.assertFalse(self.file_manager._is_path_allowed(str(invalid_path)))
        
        # Недопустимый путь (запрещенное расширение)
        invalid_ext_path = self.test_files_dir / "test.exe"
        self.assertFalse(self.file_manager._is_path_allowed(str(invalid_ext_path)))
    
    def test_file_create(self):
        """Проверка создания файла"""
        # Создание тестового файла
        test_file = self.test_files_dir / "create_test.txt"
        test_content = "Тестовое содержимое"
        
        result = self.file_manager.create_file(
            path=str(test_file),
            content=test_content
        )
        self.assertTrue(result)
        self.assertTrue(test_file.exists())
        
        # Проверка содержимого файла
        with open(test_file, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertEqual(content, test_content)
        
        # Попытка создания файла в запрещенной директории
        restricted_file = self.restricted_dir / "test.txt"
        result = self.file_manager.create_file(
            path=str(restricted_file),
            content=test_content
        )
        self.assertFalse(result)
        self.assertFalse(restricted_file.exists())
        
        # Попытка создания файла с запрещенным расширением
        invalid_file = self.test_files_dir / "test.exe"
        result = self.file_manager.create_file(
            path=str(invalid_file),
            content=test_content
        )
        self.assertFalse(result)
        self.assertFalse(invalid_file.exists())
    
    def test_file_read(self):
        """Проверка чтения файла"""
        # Создание тестового файла
        test_file = self.test_files_dir / "read_test.txt"
        test_content = "Содержимое для чтения"
        
        with open(test_file, "w", encoding="utf-8") as f:
            f.write(test_content)
        
        # Чтение файла
        result = self.file_manager.read_file(path=str(test_file))
        self.assertTrue(isinstance(result, dict))
        self.assertIn("content", result)
        self.assertEqual(result["content"], test_content)
        
        # Попытка чтения несуществующего файла
        non_existent_file = self.test_files_dir / "non_existent.txt"
        result = self.file_manager.read_file(path=str(non_existent_file))
        self.assertFalse(result)
        
        # Попытка чтения файла в запрещенной директории
        restricted_file = self.restricted_dir / "restricted.txt"
        with open(restricted_file, "w", encoding="utf-8") as f:
            f.write("Секретное содержимое")
            
        result = self.file_manager.read_file(path=str(restricted_file))
        self.assertFalse(result)
    
    def test_file_write(self):
        """Проверка записи в файл"""
        # Создание тестового файла
        test_file = self.test_files_dir / "write_test.txt"
        initial_content = "Начальное содержимое"
        
        with open(test_file, "w", encoding="utf-8") as f:
            f.write(initial_content)
        
        # Запись в файл (перезапись)
        new_content = "Новое содержимое"
        result = self.file_manager.write_file(
            path=str(test_file),
            content=new_content,
            append=False
        )
        self.assertTrue(result)
        
        # Проверка содержимого после перезаписи
        with open(test_file, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertEqual(content, new_content)
        
        # Запись в файл (добавление)
        append_content = "\nДобавленное содержимое"
        result = self.file_manager.write_file(
            path=str(test_file),
            content=append_content,
            append=True
        )
        self.assertTrue(result)
        
        # Проверка содержимого после добавления
        with open(test_file, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertEqual(content, new_content + append_content)
        
        # Попытка записи в файл в запрещенной директории
        restricted_file = self.restricted_dir / "write_test.txt"
        result = self.file_manager.write_file(
            path=str(restricted_file),
            content="Тестовое содержимое",
            append=False
        )
        self.assertFalse(result)
    
    def test_file_delete(self):
        """Проверка удаления файла"""
        # Создание тестового файла
        test_file = self.test_files_dir / "delete_test.txt"
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("Содержимое для удаления")
        
        self.assertTrue(test_file.exists())
        
        # Удаление файла
        result = self.file_manager.delete_file(path=str(test_file))
        self.assertTrue(result)
        self.assertFalse(test_file.exists())
        
        # Попытка удаления несуществующего файла
        result = self.file_manager.delete_file(path=str(test_file))
        self.assertFalse(result)
        
        # Попытка удаления файла в запрещенной директории
        restricted_file = self.restricted_dir / "restricted.txt"
        with open(restricted_file, "w", encoding="utf-8") as f:
            f.write("Содержимое для удаления")
            
        result = self.file_manager.delete_file(path=str(restricted_file))
        self.assertFalse(result)
        self.assertTrue(restricted_file.exists())
    
    def test_directory_operations(self):
        """Проверка операций с директориями"""
        # Создание директории
        test_subdir = self.test_files_dir / "test_subdir"
        result = self.file_manager.create_directory(path=str(test_subdir))
        self.assertTrue(result)
        self.assertTrue(test_subdir.exists())
        self.assertTrue(test_subdir.is_dir())
        
        # Создание файла в поддиректории
        test_file = test_subdir / "subdir_file.txt"
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("Файл в поддиректории")
        
        # Список директории
        result = self.file_manager.list_directory(path=str(self.test_files_dir))
        self.assertTrue(isinstance(result, dict))
        self.assertIn("files", result)
        self.assertIn("directories", result)
        
        # Проверка наличия нашей поддиректории в списке
        dir_found = False
        for dir_info in result["directories"]:
            if dir_info.get("name") == "test_subdir":
                dir_found = True
                break
        self.assertTrue(dir_found, "Поддиректория test_subdir не найдена в результате")
        
        # Список поддиректории
        result = self.file_manager.list_directory(path=str(test_subdir))
        self.assertTrue(isinstance(result, dict))
        self.assertIn("files", result)
        self.assertIn("subdir_file.txt", result["files"])
        
        # Удаление непустой директории (должно не удаляться без флага recursive)
        result = self.file_manager.delete_directory(
            path=str(test_subdir),
            recursive=False
        )
        self.assertFalse(result)
        self.assertTrue(test_subdir.exists())
        
        # Удаление директории с рекурсией
        result = self.file_manager.delete_directory(
            path=str(test_subdir),
            recursive=True
        )
        self.assertTrue(result)
        self.assertFalse(test_subdir.exists())
    
    def test_execute_action(self):
        """Проверка выполнения файловых действий через метод execute_action"""
        # Создание файла через execute_action
        create_action = {
            "action": "file_create",
            "path": str(self.test_files_dir / "action_test.txt"),
            "content": "Тест через execute_action"
        }
        result = self.file_manager.execute_action(create_action)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(create_action["path"]))
        
        # Чтение файла через execute_action
        read_action = {
            "action": "file_read",
            "path": create_action["path"]
        }
        result = self.file_manager.execute_action(read_action)
        self.assertTrue(isinstance(result, dict))
        self.assertIn("content", result)
        self.assertEqual(result["content"], create_action["content"])
        
        # Неизвестное действие
        unknown_action = {
            "action": "unknown_action",
            "path": create_action["path"]
        }
        result = self.file_manager.execute_action(unknown_action)
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
