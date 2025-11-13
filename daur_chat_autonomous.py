#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur AI - Autonomous Chat Interface
Natural language commands to control your MacBook with full autonomy
"""

import asyncio
import sys
import os
from pathlib import Path

# Load .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not installed, try manual loading
    env_file = Path(__file__).parent / '.env'
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.ai.autonomous_agent import AutonomousAgent


async def main():
    """Main chat loop."""
    
    # Print banner
    print("=" * 60)
    print("🤖 Daur AI - Автономный Агент")
    print("=" * 60)
    print()
    print("Я полностью автономный AI агент с возможностями:")
    print("  • 🔍 Анализ системы и установленных приложений")
    print("  • 👁️ Компьютерное зрение (вижу экран)")
    print("  • 🧠 Адаптивное планирование")
    print("  • ✅ Проверка результатов через vision")
    print("  • 🔄 Самокоррекция при ошибках")
    print()
    print("Примеры команд:")
    print("  • Открой Safari и найди информацию об AI")
    print("  • Создай папку 'Мои Проекты' в Finder")
    print("  • Открой Калькулятор и вычисли 25*4")
    print("  • Сделай скриншот экрана")
    print()
    print("Команды:")
    print("  /help - Показать помощь")
    print("  /quit - Выход")
    print("=" * 60)
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
    
    # Initialize agent
    try:
        agent = AutonomousAgent()
        await agent.initialize()
        print()
    except Exception as e:
        print(f"❌ Ошибка инициализации: {e}")
        return
    
    # Chat loop
    while True:
        try:
            # Get user input
            user_input = input("\nВы: ").strip()
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input.lower() in ['/quit', '/exit', 'quit', 'exit']:
                print("\n👋 До свидания!")
                break
            
            if user_input.lower() in ['/help', 'help']:
                print("\n📚 Помощь:")
                print("  • Говорите естественным языком")
                print("  • Я вижу экран и адаптируюсь к ситуации")
                print("  • Проверяю результаты и исправляю ошибки")
                print("  • /quit - выход")
                continue
            
            # Process message
            print("\n🤔 Думаю...")
            response = await agent.chat(user_input)
            print(f"\n🤖 Daur AI: {response}")
        
        except KeyboardInterrupt:
            print("\n\n👋 До свидания!")
            break
        except Exception as e:
            print(f"\n❌ Ошибка: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 До свидания!")

