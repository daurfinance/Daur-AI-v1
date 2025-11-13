#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur AI - Dynamic Agent Chat Interface
Simple screenshot → decide → execute loop
Based on OpenAI Computer Use architecture
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load .env file if exists
env_file = project_root / ".env"
if env_file.exists():
    print(f"Loading environment from {env_file}")
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value

from src.ai.dynamic_agent import DynamicAgent


def print_banner():
    """Print welcome banner."""
    print("=" * 60)
    print("🤖 Daur AI - Dynamic Agent (Stage 2)")
    print("=" * 60)
    print()
    print("Простая архитектура: screenshot → decide → execute → repeat")
    print("Модель решает следующее действие динамически!")
    print()
    print("Примеры команд:")
    print("  • Открой Safari")
    print("  • Создай папку 'Test' на рабочем столе")
    print("  • Открой Калькулятор")
    print("  • Сделай скриншот")
    print()
    print("Команды:")
    print("  /help - Показать помощь")
    print("  /quit - Выход")
    print("=" * 60)
    print()


async def main():
    """Main chat loop."""
    # Check API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ Ошибка: OPENAI_API_KEY не установлен")
        print()
        print("Установите API ключ:")
        print("  export OPENAI_API_KEY='your-key-here'")
        print()
        print("Или создайте файл .env с:")
        print("  OPENAI_API_KEY=your-key-here")
        return
    
    # Print banner
    print_banner()
    
    # Initialize agent
    print("🔄 Инициализация агента...")
    try:
        agent = DynamicAgent(api_key=api_key)
        print("✅ Агент готов!")
        print()
    except Exception as e:
        import traceback
        print(f"❌ Ошибка инициализации: {e}")
        print("\nПолный traceback:")
        traceback.print_exc()
        return
    
    # Chat loop
    while True:
        try:
            # Get user input
            user_input = input("Вы: ").strip()
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input == '/quit':
                print("\nДо свидания! 👋")
                break
            
            if user_input == '/help':
                print("\n📚 Помощь:")
                print("  • Просто напишите что вы хотите сделать")
                print("  • Агент будет решать действия динамически")
                print("  • Каждое действие основано на текущем скриншоте")
                print("  • /quit - выход из программы")
                print()
                continue
            
            # Execute command
            print()
            result = await agent.execute_command(user_input)
            
            # Show result
            print()
            if result['success']:
                print("🤖 Daur AI: ✅ Выполнено!")
            else:
                print("🤖 Daur AI: ⚠️ Выполнено частично")
            
            print(f"   Действий: {result['actions_taken']}")
            print(f"   Успешных: {result['actions_successful']}")
            print()
        
        except KeyboardInterrupt:
            print("\n\nДо свидания! 👋")
            break
        
        except Exception as e:
            print(f"\n❌ Ошибка: {e}")
            print()


if __name__ == "__main__":
    asyncio.run(main())

