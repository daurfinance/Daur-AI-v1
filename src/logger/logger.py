#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: Модуль логирования
Отвечает за регистрацию действий агента и ошибок

Версия: 1.0
Дата: 09.05.2025
"""

import os
import json
import logging
import logging.handlers
from datetime import datetime
from pathlib import Path

# Пытаемся импортировать Fernet для шифрования, но не требуем его для базовой функциональности
try:
    from cryptography.fernet import Fernet
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False
    print("WARNING: cryptography module not found, secure logging will be disabled")


class SecureHandler(logging.StreamHandler):
    """Обработчик логов с шифрованием"""
    
    def __init__(self, encrypt_key=None):
        super().__init__()
        self.encrypt_key = encrypt_key
        self.cipher = None
        
        # Проверяем наличие модуля cryptography
        if not HAS_CRYPTO:
            return
            
        if encrypt_key:
            try:
                self.cipher = Fernet(encrypt_key)
            except Exception:
                self.cipher = None
    
    def emit(self, record):
        if self.cipher and hasattr(record, 'msg'):
            if isinstance(record.msg, str):
                # Шифрование сообщения
                try:
                    encrypted_msg = self.cipher.encrypt(record.msg.encode('utf-8'))
                    record.msg = f"[ENCRYPTED] {encrypted_msg.decode('utf-8')}"
                except Exception as e:
                    # Если ошибка шифрования, продолжаем без шифрования
                    record.msg = f"[ENCRYPTION FAILED] {record.msg}"
        
        super().emit(record)


def get_log_file_path():
    """Получение пути к текущему файлу лога"""
    home_dir = str(Path.home())
    log_dir = os.path.join(home_dir, '.daur_ai', 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    date_str = datetime.now().strftime('%Y%m%d')
    log_file = os.path.join(log_dir, f"daur_ai_log_{date_str}.log")
    
    return log_file


def setup_logger(log_level=logging.INFO, encrypt_logs=False, log_file=None):
    """Настройка логгера"""
    # Определение пути к файлу лога
    if not log_file:
        log_file = get_log_file_path()
    
    # Создание шифровального ключа
    encrypt_key = None
    if encrypt_logs and HAS_CRYPTO:
        key_file = os.path.join(os.path.dirname(log_file), 'log_key')
        if os.path.exists(key_file):
            try:
                with open(key_file, 'rb') as f:
                    encrypt_key = f.read()
            except Exception:
                # В случае проблем с чтением ключа
                encrypt_key = None
        else:
            try:
                encrypt_key = Fernet.generate_key()
                with open(key_file, 'wb') as f:
                    f.write(encrypt_key)
            except Exception:
                # В случае проблем с созданием ключа
                encrypt_key = None
    
    # Настройка основного логгера
    logger = logging.getLogger('daur_ai')
    logger.setLevel(log_level)
    logger.handlers = []  # Очистка существующих обработчиков
    
    # Консольный обработчик
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_format = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # Файловый обработчик
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8'
    )
    file_handler.setLevel(log_level)
    file_format = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)
    
    # Обработчик с шифрованием (для чувствительных данных)
    if encrypt_logs and encrypt_key:
        secure_handler = SecureHandler(encrypt_key=encrypt_key)
        secure_handler.setLevel(log_level)
        secure_format = logging.Formatter('%(asctime)s [SECURE] %(message)s')
        secure_handler.setFormatter(secure_format)
        logger.addHandler(secure_handler)
    
    return logger


class ActionLogger:
    """Логгер действий агента"""
    
    def __init__(self, log_path, encrypt=False):
        self.logger = logging.getLogger('daur_ai.actions')
        self.log_path = log_path
        
        # Создание каталога логов при необходимости
        os.makedirs(log_path, exist_ok=True)
        
        # Определение текущего файла лога
        self.date_str = datetime.now().strftime('%Y%m%d')
        self.log_file = os.path.join(log_path, f"daur_ai_log_{self.date_str}.log")
        
        # Настройка записи логов
        self._setup_handler(encrypt)
    
    def _setup_handler(self, encrypt):
        """Настройка обработчика файловых логов"""
        handler = logging.FileHandler(self.log_file, encoding='utf-8')
        formatter = logging.Formatter('[%(asctime)s] %(message)s')
        handler.setFormatter(formatter)
        self.logger.handlers = []
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False  # Запрет на передачу сообщений родительским логгерам
    
    def log_action(self, command, action, result, error=None):
        """Запись действия в лог"""
        try:
            # Преобразование действия в JSON, если это не строка
            if not isinstance(action, str):
                action = json.dumps(action, ensure_ascii=False)
            
            # Формирование сообщения лога
            log_parts = [
                f"Команда: {command}",
                f"Действие: {action}",
                f"Результат: {'success' if error is None else 'failure'}"
            ]
            
            # Добавление информации об ошибке
            if error:
                log_parts.append(f"Ошибка: {error}")
            
            # Запись в лог
            self.logger.info(" | ".join(log_parts))
            
            return True
        
        except Exception as e:
            # В случае ошибки записи в лог
            print(f"Ошибка записи в лог: {e}")
            return False


class LogExporter:
    """Класс для экспорта логов в CSV формат"""
    
    def __init__(self, log_path):
        self.log_path = log_path
    
    def export_to_csv(self, output_path):
        """Экспорт логов в CSV формат"""
        import csv
        import re
        
        # Получение списка файлов логов
        log_files = [f for f in os.listdir(self.log_path) 
                    if os.path.isfile(os.path.join(self.log_path, f)) 
                    and f.startswith('daur_ai_log_') and f.endswith('.log')]
        
        # Запись в CSV
        with open(output_path, 'w', newline='', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file)
            # Запись заголовков
            csv_writer.writerow(['timestamp', 'command', 'action', 'result', 'error'])
            
            # Обработка каждого файла
            for log_file in sorted(log_files):
                with open(os.path.join(self.log_path, log_file), 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            # Парсинг строки лога
                            match = re.match(r'\[(.+?)\] Команда: (.+?) \| Действие: (.+?) \| Результат: (.+?)(?:\s\|\sОшибка: (.+))?$', line.strip())
                            if match:
                                timestamp, command, action, result, error = match.groups()
                                csv_writer.writerow([timestamp, command, action, result, error or ''])
                        except Exception:
                            continue
        
        return True
