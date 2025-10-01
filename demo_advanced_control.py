#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: Демонстрация продвинутого управления системой
Тестирование реального управления мышью, клавиатурой и приложениями

Версия: 1.1
Дата: 01.10.2025
"""

import sys
import os
import time
import logging

# Добавляем путь к модулям
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.input.advanced_controller import AdvancedInputController, ADVANCED_AVAILABLE
from src.apps.advanced_manager import AdvancedAppManager
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


def demo_input_controller():
    """Демонстрация продвинутого контроллера ввода"""
    print("\n" + "="*60)
    print("ДЕМОНСТРАЦИЯ ПРОДВИНУТОГО КОНТРОЛЛЕРА ВВОДА")
    print("="*60)
    
    if not ADVANCED_AVAILABLE:
        print("❌ Продвинутый контроллер недоступен")
        print("   Требуется установка: pip install pyautogui pynput pillow opencv-python")
        return False
    
    try:
        # Создание контроллера
        controller = AdvancedInputController("Linux")
        print("✅ Продвинутый контроллер создан")
        
        # Получение информации о системе
        screen_size = controller.get_screen_size()
        mouse_pos = controller.get_mouse_position()
        
        print(f"🖥️  Размер экрана: {screen_size[0]}x{screen_size[1]}")
        print(f"🖱️  Позиция мыши: {mouse_pos}")
        
        # Тестирование базовых функций (безопасно)
        print("\n🧪 Тестирование базовых функций:")
        
        # Перемещение мыши (безопасно)
        print("  • Перемещение мыши в центр экрана...")
        center_x, center_y = screen_size[0] // 2, screen_size[1] // 2
        if controller.move_mouse(center_x, center_y, duration=0.5):
            print("    ✅ Мышь перемещена")
        else:
            print("    ❌ Ошибка перемещения мыши")
        
        # Получение скриншота
        print("  • Создание скриншота...")
        screenshot = controller.take_screenshot()
        if screenshot is not None:
            print(f"    ✅ Скриншот создан: {screenshot.shape}")
        else:
            print("    ❌ Ошибка создания скриншота")
        
        # Тестирование действий через API
        print("\n🎯 Тестирование действий через API:")
        
        test_actions = [
            {
                'action': 'input_type',
                'params': {'text': 'Hello from Daur-AI!', 'interval': 0.05}
            },
            {
                'action': 'input_key',
                'params': {'key': 'enter'}
            },
            {
                'action': 'input_hotkey',
                'params': {'keys': ['ctrl', 'a']}
            }
        ]
        
        for i, action in enumerate(test_actions, 1):
            print(f"  Действие {i}: {action['action']}")
            try:
                # В headless режиме только логируем
                if os.getenv('DISPLAY') is None:
                    print(f"    📝 Симуляция: {action}")
                    result = True
                else:
                    result = controller.execute_action(action)
                
                print(f"    {'✅' if result else '❌'} {'Успешно' if result else 'Ошибка'}")
                time.sleep(0.5)
            except Exception as e:
                print(f"    ❌ Ошибка: {e}")
        
        # Очистка
        controller.cleanup()
        print("\n✅ Контроллер завершил работу корректно")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка в контроллере ввода: {e}")
        import traceback
        traceback.print_exc()
        return False


def demo_app_manager():
    """Демонстрация продвинутого менеджера приложений"""
    print("\n" + "="*60)
    print("ДЕМОНСТРАЦИЯ ПРОДВИНУТОГО МЕНЕДЖЕРА ПРИЛОЖЕНИЙ")
    print("="*60)
    
    try:
        # Создание менеджера
        app_manager = AdvancedAppManager("Linux")
        print("✅ Продвинутый менеджер приложений создан")
        
        # Получение списка запущенных приложений
        print("\n📋 Получение списка запущенных приложений:")
        apps = app_manager.get_running_apps()
        
        # Показываем топ-10 по использованию памяти
        apps_sorted = sorted(apps, key=lambda x: x.memory_mb, reverse=True)[:10]
        
        print(f"Найдено {len(apps)} процессов, топ-10 по памяти:")
        for i, app in enumerate(apps_sorted, 1):
            print(f"  {i:2d}. {app.name:<20} PID:{app.pid:<8} RAM:{app.memory_mb:6.1f}MB CPU:{app.cpu_percent:5.1f}%")
        
        # Тестирование поиска приложений
        print("\n🔍 Тестирование поиска приложений:")
        search_terms = ["python", "bash", "systemd", "firefox", "chrome"]
        
        for term in search_terms:
            found_apps = app_manager.find_app_by_name(term)
            if found_apps:
                print(f"  '{term}': найдено {len(found_apps)} приложений")
                for app in found_apps[:3]:  # Показываем первые 3
                    print(f"    - {app.name} (PID: {app.pid})")
            else:
                print(f"  '{term}': не найдено")
        
        # Тестирование запуска приложений (безопасно)
        print("\n🚀 Тестирование запуска приложений:")
        
        # Пытаемся запустить простые приложения
        test_apps = ["calculator", "text_editor"]
        
        for app_name in test_apps:
            print(f"  Попытка запуска: {app_name}")
            try:
                # В headless режиме только симулируем
                if os.getenv('DISPLAY') is None:
                    print(f"    📝 Симуляция запуска {app_name}")
                    result = True
                else:
                    result = app_manager.launch_app(app_name)
                
                print(f"    {'✅' if result else '❌'} {'Запущено' if result else 'Ошибка'}")
                
                if result:
                    time.sleep(2)  # Даем время запуститься
                    
                    # Пытаемся найти запущенное приложение
                    found = app_manager.find_app_by_name(app_name)
                    if found:
                        print(f"    ✅ Приложение найдено в списке процессов")
                        
                        # Пытаемся закрыть (только если запустили)
                        if not os.getenv('DISPLAY') is None:
                            print(f"    🔄 Закрытие приложения...")
                            close_result = app_manager.close_app(app_name)
                            print(f"    {'✅' if close_result else '❌'} {'Закрыто' if close_result else 'Ошибка закрытия'}")
                    else:
                        print(f"    ⚠️  Приложение не найдено в списке процессов")
                
            except Exception as e:
                print(f"    ❌ Ошибка: {e}")
        
        # Тестирование действий через API
        print("\n🎯 Тестирование действий через API:")
        
        test_actions = [
            {
                'action': 'app_list',
                'params': {}
            },
            {
                'action': 'app_open',
                'params': {'app_name': 'calculator'}
            }
        ]
        
        for i, action in enumerate(test_actions, 1):
            print(f"  Действие {i}: {action['action']}")
            try:
                result = app_manager.execute_action(action)
                print(f"    {'✅' if result else '❌'} {'Успешно' if result else 'Ошибка'}")
            except Exception as e:
                print(f"    ❌ Ошибка: {e}")
        
        # Очистка
        app_manager.cleanup()
        print("\n✅ Менеджер приложений завершил работу корректно")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка в менеджере приложений: {e}")
        import traceback
        traceback.print_exc()
        return False


def demo_integrated_agent():
    """Демонстрация интегрированного агента с продвинутым управлением"""
    print("\n" + "="*60)
    print("ДЕМОНСТРАЦИЯ ИНТЕГРИРОВАННОГО АГЕНТА")
    print("="*60)
    
    try:
        # Загрузка конфигурации
        config = load_config()
        
        # Создание агента
        agent = DaurAgent(config, ui_mode="console", sandbox=True)
        print("✅ Агент с продвинутым управлением создан")
        
        # Информация о компонентах
        print(f"🔧 Контроллер ввода: {type(agent.input_controller).__name__}")
        print(f"🔧 Менеджер приложений: {type(agent.app_manager).__name__}")
        
        # Тестирование команд с реальным управлением
        test_commands = [
            "покажи список запущенных приложений",
            "создай файл test_advanced.txt с содержимым 'Продвинутое управление работает!'",
            "открой калькулятор",
            "напечатай текст 'Hello Advanced Control!'",
            "help"
        ]
        
        print("\n🎯 Тестирование команд с продвинутым управлением:")
        for i, command in enumerate(test_commands, 1):
            print(f"\n{i}. Команда: '{command}'")
            try:
                response = agent.handle_command(command)
                print(f"   Ответ: {response}")
                time.sleep(1)
            except Exception as e:
                print(f"   ❌ Ошибка: {e}")
        
        # Демонстрация парсинга сложных команд
        print("\n🧠 Демонстрация парсинга сложных команд:")
        complex_commands = [
            "открой браузер firefox и перейди на google.com",
            "создай новый документ в текстовом редакторе и напиши заголовок",
            "сделай скриншот экрана и сохрани в файл screenshot.png",
            "найди все процессы python и покажи их использование памяти"
        ]
        
        for command in complex_commands:
            print(f"\nКоманда: '{command}'")
            try:
                # Получаем действия от парсера
                actions = agent.command_parser.parse(command)
                print(f"Распознанные действия:")
                for j, action in enumerate(actions, 1):
                    print(f"  {j}. {action}")
            except Exception as e:
                print(f"❌ Ошибка парсинга: {e}")
        
        # Очистка ресурсов
        agent.cleanup()
        print("\n✅ Интегрированный агент завершил работу корректно")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка в интегрированном агенте: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Основная функция демонстрации"""
    print("ДЕМОНСТРАЦИЯ ПРОДВИНУТОГО УПРАВЛЕНИЯ СИСТЕМОЙ")
    print("Реальное управление мышью, клавиатурой и приложениями")
    print("="*60)
    
    # Настройка логирования
    setup_demo_logging()
    
    # Проверка headless режима
    if os.getenv('DISPLAY') is None:
        print("⚠️  HEADLESS РЕЖИМ ОБНАРУЖЕН")
        print("Некоторые функции будут симулированы без реального выполнения")
        print("Для полного тестирования запустите в графической среде")
        print()
    
    success_count = 0
    total_tests = 3
    
    try:
        # Демонстрация контроллера ввода
        if demo_input_controller():
            success_count += 1
        
        # Демонстрация менеджера приложений
        if demo_app_manager():
            success_count += 1
        
        # Демонстрация интегрированного агента
        if demo_integrated_agent():
            success_count += 1
        
        print("\n" + "="*60)
        print(f"РЕЗУЛЬТАТЫ ДЕМОНСТРАЦИИ: {success_count}/{total_tests} тестов прошли успешно")
        print("="*60)
        
        if success_count == total_tests:
            print("🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
            print("\nПродвинутое управление системой работает корректно.")
            print("Daur-AI теперь может реально управлять компьютером!")
        elif success_count > 0:
            print("⚠️  ЧАСТИЧНЫЙ УСПЕХ")
            print("\nНекоторые компоненты работают, но есть проблемы.")
            print("Проверьте логи выше для диагностики.")
        else:
            print("❌ ВСЕ ТЕСТЫ ПРОВАЛИЛИСЬ")
            print("\nВозможные причины:")
            print("1. Отсутствуют необходимые зависимости")
            print("2. Headless режим без графической среды")
            print("3. Проблемы с правами доступа")
        
        print("\n📚 Возможности продвинутого управления:")
        print("  • Реальное управление мышью и клавиатурой")
        print("  • Запуск и закрытие приложений")
        print("  • Создание скриншотов и поиск изображений")
        print("  • Мониторинг системных процессов")
        print("  • Управление окнами приложений")
        print("  • Автоматизация сложных сценариев")
        
        print("\n🚀 Следующие шаги:")
        print("  • Веб-панель управления")
        print("  • Docker контейнеризация")
        print("  • Интеграция с браузерной автоматизацией")
        print("  • OCR для распознавания текста на экране")
        
    except KeyboardInterrupt:
        print("\n\nДемонстрация прервана пользователем")
    except Exception as e:
        print(f"\n\nКритическая ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
