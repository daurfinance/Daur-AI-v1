#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: Демонстрационный скрипт
Скрипт для демонстрации возможностей Daur-AI

Версия: 1.0
Дата: 01.10.2025
"""

import sys
import os
import time
import logging

# Добавляем путь к модулям
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.agent.core import DaurAgent
from src.config.settings import load_config


def setup_demo_logging():
    """Настройка логирования для демонстрации"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def demo_command_parsing():
    """Демонстрация парсинга команд"""
    print("\n" + "="*60)
    print("ДЕМОНСТРАЦИЯ ПАРСИНГА КОМАНД")
    print("="*60)
    
    # Импорт AI модели
    from src.ai.simple_model import SimpleAIModel
    
    model = SimpleAIModel()
    
    # Тестовые команды
    test_commands = [
        "создай файл test.txt",
        "открой браузер",
        "напечатай привет мир",
        "покажи список файлов",
        "создай папку новая_папка",
        "удали файл старый.txt",
        "закрой приложение notepad"
    ]
    
    for command in test_commands:
        print(f"\nКоманда: '{command}'")
        actions = model.parse_command(command)
        for i, action in enumerate(actions, 1):
            print(f"  Действие {i}: {action}")
        response = model.generate_response(command, actions)
        print(f"  Ответ: {response}")


def demo_agent_initialization():
    """Демонстрация инициализации агента"""
    print("\n" + "="*60)
    print("ДЕМОНСТРАЦИЯ ИНИЦИАЛИЗАЦИИ АГЕНТА")
    print("="*60)
    
    try:
        # Загрузка конфигурации
        config = load_config()
        print("✓ Конфигурация загружена")
        
        # Создание агента
        agent = DaurAgent(config, ui_mode="console", sandbox=True)
        print("✓ Агент создан успешно")
        
        # Тестирование обработки команд
        test_commands = [
            "создай файл demo.txt с содержимым Привет от Daur-AI",
            "покажи список файлов",
            "help"
        ]
        
        print("\nТестирование обработки команд:")
        for command in test_commands:
            print(f"\nОбработка команды: '{command}'")
            response = agent.handle_command(command)
            print(f"Ответ агента: {response}")
            time.sleep(0.5)
        
        # Очистка ресурсов
        agent.cleanup()
        print("\n✓ Агент завершил работу корректно")
        
    except Exception as e:
        print(f"✗ Ошибка при инициализации агента: {e}")
        import traceback
        traceback.print_exc()


def demo_file_operations():
    """Демонстрация файловых операций"""
    print("\n" + "="*60)
    print("ДЕМОНСТРАЦИЯ ФАЙЛОВЫХ ОПЕРАЦИЙ")
    print("="*60)
    
    try:
        from src.files.manager import FileManager
        
        # Создание менеджера файлов
        file_manager = FileManager(
            allowed_extensions=[".txt", ".py", ".md"],
            restricted_paths=["/etc", "/bin"]
        )
        print("✓ Менеджер файлов создан")
        
        # Тестовые операции
        test_actions = [
            {
                'action': 'file_create',
                'params': {
                    'filename': 'demo_test.txt',
                    'content': 'Это тестовый файл, созданный Daur-AI'
                }
            },
            {
                'action': 'file_read',
                'params': {
                    'filename': 'demo_test.txt'
                }
            },
            {
                'action': 'file_list',
                'params': {
                    'directory': '.'
                }
            }
        ]
        
        for action in test_actions:
            print(f"\nВыполнение: {action['action']}")
            try:
                result = file_manager.execute_action(action)
                print(f"Результат: {'✓ Успешно' if result else '✗ Ошибка'}")
            except Exception as e:
                print(f"✗ Ошибка: {e}")
        
    except Exception as e:
        print(f"✗ Ошибка в файловых операциях: {e}")


def demo_input_simulation():
    """Демонстрация симуляции ввода"""
    print("\n" + "="*60)
    print("ДЕМОНСТРАЦИЯ СИМУЛЯЦИИ ВВОДА")
    print("="*60)
    
    try:
        from src.input.simple_controller import SimpleInputController
        
        # Создание контроллера
        controller = SimpleInputController("Linux")
        print("✓ Контроллер ввода создан")
        
        # Тестовые действия
        test_actions = [
            {
                'action': 'input_click',
                'params': {'target': 'кнопка OK'}
            },
            {
                'action': 'input_type',
                'params': {'text': 'Привет от Daur-AI!'}
            },
            {
                'action': 'input_key',
                'params': {'key': 'Enter'}
            }
        ]
        
        for action in test_actions:
            print(f"\nВыполнение: {action['action']}")
            result = controller.execute_action(action)
            print(f"Результат: {'✓ Успешно' if result else '✗ Ошибка'}")
            time.sleep(0.5)
        
        # Получение информации о системе
        mouse_pos = controller.get_mouse_position()
        screen_size = controller.get_screen_size()
        print(f"\nИнформация о системе:")
        print(f"  Позиция мыши: {mouse_pos}")
        print(f"  Размер экрана: {screen_size}")
        
    except Exception as e:
        print(f"✗ Ошибка в симуляции ввода: {e}")


def main():
    """Основная функция демонстрации"""
    print("ДЕМОНСТРАЦИЯ DAUR-AI v1.0")
    print("Универсальный автономный ИИ-агент")
    print("="*60)
    
    # Настройка логирования
    setup_demo_logging()
    
    # Запуск демонстраций
    try:
        demo_command_parsing()
        demo_file_operations()
        demo_input_simulation()
        demo_agent_initialization()
        
        print("\n" + "="*60)
        print("ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА УСПЕШНО")
        print("="*60)
        print("\nДля запуска полной версии используйте:")
        print("  python3 src/main.py --ui console")
        print("  python3 src/main.py --ui gui")
        print("\nДля установки используйте:")
        print("  pip install -e .")
        print("  pip install -e .[full]  # с полными зависимостями")
        
    except KeyboardInterrupt:
        print("\n\nДемонстрация прервана пользователем")
    except Exception as e:
        print(f"\n\nОшибка во время демонстрации: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
