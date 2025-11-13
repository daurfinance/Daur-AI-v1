#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: Универсальный автономный ИИ-агент
Точка входа в приложение

Версия: 1.0
Дата: 09.05.2025
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Добавляем текущую директорию в путь импорта
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agent.core import DaurAgent
from src.logger.logger import setup_logger
from src.config.settings import load_config, DEFAULT_CONFIG_PATH


def parse_arguments():
    """Парсинг аргументов командной строки"""
    parser = argparse.ArgumentParser(description="Daur-AI: Универсальный автономный ИИ-агент")
    parser.add_argument("--config", type=str, default=DEFAULT_CONFIG_PATH,
                        help=f"Путь к файлу конфигурации (по умолчанию: {DEFAULT_CONFIG_PATH})")
    parser.add_argument("--train", action="store_true",
                        help="Запуск обучения модели на основе логов")
    parser.add_argument("--export-logs", type=str,
                        help="Экспорт логов в CSV формат по указанному пути")
    parser.add_argument("--sandbox", action="store_true",
                        help="Запуск в песочнице (для тестирования опасных команд)")
    parser.add_argument("--debug", action="store_true",
                        help="Включить режим отладки (подробное логирование)")
    parser.add_argument("--ui", choices=["console", "gui"], default="console",
                        help="Тип интерфейса (console или gui)")
    return parser.parse_args()


def main():
    """Основная точка входа в приложение"""
    # Парсинг аргументов
    args = parse_arguments()
    
    # Настройка логирования
    log_level = logging.DEBUG if args.debug else logging.INFO
    setup_logger(log_level)
    logger = logging.getLogger("daur_ai")
    
    try:
        # Загрузка конфигурации
        config = load_config(args.config)
        
        # Обработка специальных команд
        if args.train:
            from src.ai.trainer import train_model
            logger.info("Запуск обучения модели на основе логов")
            train_model(config)
            return
        
        if args.export_logs:
            from src.logger.exporter import export_logs_to_csv
            logger.info(f"Экспорт логов в CSV: {args.export_logs}")
            export_logs_to_csv(config["log_path"], args.export_logs)
            return
            
        # Создание и запуск агента
        agent = DaurAgent(config)
        
        # Start agent
        agent.start()
        
        # Keep running until interrupted
        logger.info("Daur AI запущен. Нажмите Ctrl+C для остановки.")
        try:
            agent.stop_event.wait()
        except KeyboardInterrupt:
            logger.info("Остановка агента...")
            agent.stop()
        
    except KeyboardInterrupt:
        logger.info("Программа остановлена пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}", exc_info=True)
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
