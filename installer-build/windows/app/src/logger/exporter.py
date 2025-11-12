#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: Утилита экспорта логов
Экспортирует логи в CSV формат

Версия: 1.0
Дата: 09.05.2025
"""

import os
import re
import csv
import logging
from datetime import datetime
from pathlib import Path


def export_logs_to_csv(log_dir, output_path):
    """
    Экспорт логов в CSV формат
    
    Args:
        log_dir (str): Путь к директории с логами
        output_path (str): Путь к выходному CSV файлу
    
    Returns:
        bool: True в случае успеха, False в случае ошибки
    """
    logger = logging.getLogger('daur_ai')
    
    try:
        # Проверка существования директории с логами
        if not os.path.exists(log_dir):
            logger.error(f"Директория логов не существует: {log_dir}")
            return False
        
        # Получение списка файлов логов
        log_files = [f for f in os.listdir(log_dir) 
                    if os.path.isfile(os.path.join(log_dir, f)) 
                    and f.startswith('daur_ai_log_') and f.endswith('.log')]
        
        if not log_files:
            logger.warning(f"Файлы логов не найдены в {log_dir}")
            return False
        
        logger.info(f"Найдено {len(log_files)} файлов логов для экспорта")
        
        # Создание директории для выходного файла при необходимости
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        # Запись в CSV
        row_count = 0
        with open(output_path, 'w', newline='', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file)
            # Запись заголовков
            csv_writer.writerow(['timestamp', 'command', 'action', 'result', 'error'])
            
            # Обработка каждого файла
            for log_file in sorted(log_files):
                log_path = os.path.join(log_dir, log_file)
                logger.debug(f"Обработка лога: {log_path}")
                
                with open(log_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            # Парсинг строки лога
                            match = re.match(r'\[(.+?)\] Команда: (.+?) \| Действие: (.+?) \| Результат: (.+?)(?:\s\|\sОшибка: (.+))?$', line.strip())
                            if match:
                                timestamp, command, action, result, error = match.groups()
                                csv_writer.writerow([timestamp, command, action, result, error or ''])
                                row_count += 1
                        except Exception as e:
                            logger.debug(f"Ошибка при парсинге строки: {e}")
                            continue
        
        logger.info(f"Экспортировано {row_count} строк логов в {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Ошибка экспорта логов: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    # Пример использования при прямом запуске
    import argparse
    
    parser = argparse.ArgumentParser(description="Экспорт логов Daur-AI в CSV формат")
    parser.add_argument("--log-dir", type=str, default=None, 
                        help="Директория с логами (по умолчанию: ~/.daur_ai/logs)")
    parser.add_argument("--output", type=str, required=True, 
                        help="Путь для сохранения CSV файла")
    args = parser.parse_args()
    
    # Определение директории логов
    if not args.log_dir:
        home_dir = str(Path.home())
        log_dir = os.path.join(home_dir, '.daur_ai', 'logs')
    else:
        log_dir = args.log_dir
    
    # Настройка логирования
    logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
    
    # Экспорт логов
    success = export_logs_to_csv(log_dir, args.output)
    if success:
        print(f"Логи успешно экспортированы в {args.output}")
    else:
        print("Ошибка экспорта логов")
        exit(1)
