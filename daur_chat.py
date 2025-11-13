#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur AI - Interactive Chat Interface
Natural language commands to control your MacBook
"""

import asyncio
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.ai.intelligent_agent import IntelligentAgent


async def main():
    """Main chat interface"""
    
    print("="*60)
    print("🤖 Daur AI - Умный Агент Автоматизации")
    print("="*60)
    print()
    print("Я могу управлять вашим MacBook через естественный язык!")
    print()
    print("Примеры команд:")
    print("  • Открой Safari и найди информацию об AI")
    print("  • Создай папку 'Мои Проекты' в Finder")
    print("  • Открой Калькулятор и вычисли 25*4")
    print("  • Сделай скриншот экрана")
    print("  • Открой Notes и напиши 'Привет мир'")
    print()
    print("Команды:")
    print("  /help - Показать помощь")
    print("  /quit - Выход")
    print("="*60)
    print()
    
    # Check API key
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Ошибка: OPENAI_API_KEY не установлен")
        print()
        print("Установите API ключ:")
        print("  export OPENAI_API_KEY='your-key-here'")
        print()
        print("Или создайте файл .env с:")
        print("  OPENAI_API_KEY=your-key-here")
        return
    
    try:
        # Initialize agent
        print("🔄 Инициализация агента...")
        agent = IntelligentAgent()
        print("✅ Агент готов!")
        print()
        
        # Chat loop
        while True:
            try:
                # Get user input
                user_input = input("Вы: ").strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.startswith('/'):
                    if user_input == '/quit':
                        print("\n👋 До свидания!")
                        break
                    elif user_input == '/help':
                        print_help()
                        continue
                    else:
                        print(f"❌ Неизвестная команда: {user_input}")
                        continue
                
                # Process command
                print()
                print("🤔 Думаю...")
                
                response = await agent.chat(user_input)
                
                print()
                print(f"🤖 Daur AI: {response}")
                print()
                
            except KeyboardInterrupt:
                print("\n\n👋 До свидания!")
                break
            except Exception as e:
                print(f"\n❌ Ошибка: {e}")
                print()
    
    except Exception as e:
        print(f"❌ Ошибка инициализации: {e}")
        return


def print_help():
    """Print help message"""
    print()
    print("="*60)
    print("📚 Помощь - Daur AI")
    print("="*60)
    print()
    print("Я понимаю естественный язык и могу:")
    print()
    print("1. Открывать приложения:")
    print("   • Открой Safari")
    print("   • Запусти Калькулятор")
    print("   • Открой Finder")
    print()
    print("2. Автоматизировать задачи:")
    print("   • Открой Safari и найди 'AI automation'")
    print("   • Создай папку 'Проекты' в Finder")
    print("   • Открой Notes и напиши 'Список дел'")
    print()
    print("3. Управлять компьютером:")
    print("   • Сделай скриншот")
    print("   • Открой Spotlight")
    print("   • Создай новую вкладку в браузере")
    print()
    print("4. Отвечать на вопросы:")
    print("   • Что ты умеешь?")
    print("   • Как создать папку?")
    print("   • Помоги мне автоматизировать задачу")
    print()
    print("Команды:")
    print("  /help - Эта справка")
    print("  /quit - Выход")
    print("="*60)
    print()


if __name__ == "__main__":
    asyncio.run(main())

