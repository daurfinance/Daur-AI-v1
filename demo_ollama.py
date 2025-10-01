#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: Демонстрация Ollama интеграции
Скрипт для тестирования работы с локальными LLM моделями

Версия: 1.1
Дата: 01.10.2025
"""

import sys
import os
import time
import logging

# Добавляем путь к модулям
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.ai.ollama_model import OllamaModelManager, OllamaConfig
from src.ai.enhanced_model_manager import EnhancedModelManager
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


def demo_ollama_direct():
    """Демонстрация прямой работы с Ollama"""
    print("\n" + "="*60)
    print("ДЕМОНСТРАЦИЯ ПРЯМОЙ РАБОТЫ С OLLAMA")
    print("="*60)
    
    try:
        # Создание Ollama менеджера
        config = OllamaConfig(
            host="http://localhost:11434",
            model="llama3.2",
            timeout=30
        )
        
        ollama = OllamaModelManager(config)
        
        # Проверка доступности
        if not ollama.is_available():
            print("❌ Ollama недоступна. Убедитесь что:")
            print("   1. Ollama установлена: curl -fsSL https://ollama.ai/install.sh | sh")
            print("   2. Ollama запущена: ollama serve")
            print("   3. Модель загружена: ollama pull llama3.2")
            return False
        
        print("✅ Ollama доступна")
        
        # Список моделей
        models = ollama.list_models()
        print(f"📋 Доступные модели: {models}")
        
        # Проверка наличия нужной модели
        if config.model not in models:
            print(f"📥 Модель {config.model} не найдена, пытаюсь загрузить...")
            if ollama.pull_model(config.model):
                print(f"✅ Модель {config.model} успешно загружена")
            else:
                print(f"❌ Не удалось загрузить модель {config.model}")
                return False
        
        # Тестирование генерации текста
        print("\n🧠 Тестирование генерации текста:")
        test_prompt = "Привет! Как дела?"
        response = ollama.generate_text(test_prompt)
        print(f"Промпт: {test_prompt}")
        print(f"Ответ: {response[:200]}...")
        
        # Тестирование парсинга команд
        print("\n🔍 Тестирование парсинга команд:")
        test_commands = [
            "создай файл test.txt с содержимым привет мир",
            "открой браузер firefox",
            "напечатай текст hello world"
        ]
        
        for command in test_commands:
            print(f"\nКоманда: '{command}'")
            actions = ollama.parse_command(command)
            print(f"Действия: {actions}")
        
        # Тестирование диалога
        print("\n💬 Тестирование диалогового режима:")
        context = []
        
        messages = [
            "Как тебя зовут?",
            "Что ты умеешь делать?",
            "Помоги мне создать файл"
        ]
        
        for message in messages:
            print(f"\nПользователь: {message}")
            response = ollama.chat(message, context)
            print(f"Ассистент: {response[:150]}...")
            
            # Добавляем в контекст
            context.append({
                "user": message,
                "assistant": response
            })
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка в демонстрации Ollama: {e}")
        import traceback
        traceback.print_exc()
        return False


def demo_enhanced_manager():
    """Демонстрация работы улучшенного менеджера"""
    print("\n" + "="*60)
    print("ДЕМОНСТРАЦИЯ УЛУЧШЕННОГО AI МЕНЕДЖЕРА")
    print("="*60)
    
    try:
        # Загрузка конфигурации
        config = load_config()
        
        # Создание улучшенного менеджера
        ai_manager = EnhancedModelManager(config)
        
        # Информация о доступных моделях
        available_models = ai_manager.get_available_models()
        print(f"📋 Доступные модели: {available_models}")
        
        model_info = ai_manager.get_model_info()
        print(f"🔧 Активная модель: {model_info}")
        
        # Тестирование парсинга команд
        print("\n🔍 Тестирование парсинга команд через Enhanced Manager:")
        test_commands = [
            "создай папку новый_проект",
            "открой текстовый редактор",
            "покажи список файлов в текущей директории",
            "удали файл старый.txt",
            "напиши в файл readme.md текст 'Это мой проект'"
        ]
        
        for command in test_commands:
            print(f"\nКоманда: '{command}'")
            try:
                actions = ai_manager.parse_command(command)
                for i, action in enumerate(actions, 1):
                    print(f"  Действие {i}: {action}")
            except Exception as e:
                print(f"  ❌ Ошибка: {e}")
        
        # Тестирование генерации текста
        print("\n🧠 Тестирование генерации текста:")
        prompts = [
            "Объясни что такое искусственный интеллект",
            "Как создать простой Python скрипт?",
            "Какие преимущества у локальных AI моделей?"
        ]
        
        for prompt in prompts:
            print(f"\nПромпт: {prompt}")
            try:
                response = ai_manager.generate_text(prompt)
                print(f"Ответ: {response[:200]}...")
            except Exception as e:
                print(f"❌ Ошибка: {e}")
        
        # Очистка ресурсов
        ai_manager.cleanup()
        print("\n✅ Enhanced Manager завершил работу корректно")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка в Enhanced Manager: {e}")
        import traceback
        traceback.print_exc()
        return False


def demo_agent_with_ollama():
    """Демонстрация работы агента с Ollama"""
    print("\n" + "="*60)
    print("ДЕМОНСТРАЦИЯ АГЕНТА С OLLAMA")
    print("="*60)
    
    try:
        from src.agent.core import DaurAgent
        
        # Загрузка конфигурации
        config = load_config()
        
        # Создание агента
        agent = DaurAgent(config, ui_mode="console", sandbox=True)
        print("✅ Агент с Ollama создан успешно")
        
        # Информация об AI модели
        if hasattr(agent.ai_manager, 'get_model_info'):
            model_info = agent.ai_manager.get_model_info()
            print(f"🔧 Информация о модели: {model_info}")
        
        # Тестирование команд
        test_commands = [
            "создай файл hello.py с кодом print('Hello, Ollama!')",
            "покажи список файлов",
            "открой браузер",
            "help"
        ]
        
        print("\n🎯 Тестирование команд через агента:")
        for command in test_commands:
            print(f"\nВыполнение: '{command}'")
            try:
                response = agent.handle_command(command)
                print(f"Ответ агента: {response}")
                time.sleep(1)
            except Exception as e:
                print(f"❌ Ошибка: {e}")
        
        # Очистка ресурсов
        agent.cleanup()
        print("\n✅ Агент завершил работу корректно")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка в работе агента: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Основная функция демонстрации"""
    print("ДЕМОНСТРАЦИЯ OLLAMA ИНТЕГРАЦИИ В DAUR-AI")
    print("Локальные LLM модели для автономного AI-агента")
    print("="*60)
    
    # Настройка логирования
    setup_demo_logging()
    
    success_count = 0
    total_tests = 3
    
    try:
        # Демонстрация прямой работы с Ollama
        if demo_ollama_direct():
            success_count += 1
        
        # Демонстрация Enhanced Manager
        if demo_enhanced_manager():
            success_count += 1
        
        # Демонстрация агента с Ollama
        if demo_agent_with_ollama():
            success_count += 1
        
        print("\n" + "="*60)
        print(f"РЕЗУЛЬТАТЫ ДЕМОНСТРАЦИИ: {success_count}/{total_tests} тестов прошли успешно")
        print("="*60)
        
        if success_count == total_tests:
            print("🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
            print("\nOllama интеграция работает корректно.")
            print("Daur-AI теперь может использовать локальные LLM модели!")
        elif success_count > 0:
            print("⚠️  ЧАСТИЧНЫЙ УСПЕХ")
            print("\nНекоторые компоненты работают, но есть проблемы.")
            print("Проверьте логи выше для диагностики.")
        else:
            print("❌ ВСЕ ТЕСТЫ ПРОВАЛИЛИСЬ")
            print("\nВозможные причины:")
            print("1. Ollama не установлена или не запущена")
            print("2. Модель не загружена")
            print("3. Проблемы с сетевым подключением")
        
        print("\n📚 Полезные команды:")
        print("  ollama serve                    # Запуск Ollama сервера")
        print("  ollama pull llama3.2           # Загрузка модели")
        print("  ollama list                    # Список моделей")
        print("  python3 src/main.py --ui console  # Запуск агента")
        
    except KeyboardInterrupt:
        print("\n\nДемонстрация прервана пользователем")
    except Exception as e:
        print(f"\n\nКритическая ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
