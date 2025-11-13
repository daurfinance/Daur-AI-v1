#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur AI Intelligent Agent - Demonstration Examples
Shows how the AI agent understands and executes natural language commands
"""

import asyncio
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ai.intelligent_agent import IntelligentAgent


async def demo_simple_commands():
    """Demonstrate simple command execution"""
    
    print("\n" + "="*60)
    print("Demo 1: Simple Commands")
    print("="*60 + "\n")
    
    agent = IntelligentAgent()
    
    commands = [
        "Открой Калькулятор",
        "Открой Finder",
        "Сделай скриншот и сохрани как demo1.png"
    ]
    
    for i, command in enumerate(commands, 1):
        print(f"\n[{i}/{len(commands)}] Команда: {command}")
        print("-" * 60)
        
        result = await agent.process_command(command)
        
        if result['success']:
            print(f"✓ Успех!")
            print(f"  Цель: {result['plan']['goal']}")
            print(f"  Действий: {len(result['plan']['actions'])}")
            print(f"  Выполнено: {result['result']['successful_steps']}/{result['result']['total_steps']}")
        else:
            print(f"✗ Ошибка: {result['error']}")
        
        await asyncio.sleep(2)


async def demo_complex_automation():
    """Demonstrate complex multi-step automation"""
    
    print("\n" + "="*60)
    print("Demo 2: Complex Automation")
    print("="*60 + "\n")
    
    agent = IntelligentAgent()
    
    command = "Открой Safari, перейди на google.com и найди 'AI automation'"
    
    print(f"Команда: {command}")
    print("-" * 60)
    print("\n🤔 Агент думает и планирует...\n")
    
    result = await agent.process_command(command)
    
    if result['success']:
        print("✓ План создан!")
        print(f"\nЦель: {result['plan']['goal']}")
        print(f"Рассуждение: {result['plan']['reasoning']}")
        print(f"\nШаги выполнения:")
        
        for i, action in enumerate(result['plan']['actions'], 1):
            print(f"\n{i}. {action['description']}")
            print(f"   Тип: {action['type']}")
            print(f"   Почему: {action['reasoning']}")
        
        print(f"\n📊 Результат выполнения:")
        print(f"  Всего шагов: {result['result']['total_steps']}")
        print(f"  Успешно: {result['result']['successful_steps']}")
        print(f"  Неудачно: {result['result']['failed_steps']}")
        
        print(f"\n✓ Автоматизация завершена!")
    else:
        print(f"✗ Ошибка: {result['error']}")


async def demo_planning_and_reasoning():
    """Demonstrate AI planning and reasoning capabilities"""
    
    print("\n" + "="*60)
    print("Demo 3: AI Planning & Reasoning")
    print("="*60 + "\n")
    
    agent = IntelligentAgent()
    
    command = "Создай папку 'AI Projects' в Finder и сделай скриншот"
    
    print(f"Команда: {command}")
    print("-" * 60)
    
    # Show understanding phase
    print("\n🧠 Фаза 1: Понимание команды...")
    understanding = await agent._understand_command(command)
    print(f"  Намерение: {understanding['intent']}")
    print(f"  Цель: {understanding['target']}")
    print(f"  Сложность: {understanding['complexity']}")
    print(f"  Требует планирования: {understanding['requires_planning']}")
    
    # Show planning phase
    print("\n📋 Фаза 2: Создание плана...")
    plan = await agent._create_plan(command, understanding)
    print(f"  Цель плана: {plan.goal}")
    print(f"  Рассуждение: {plan.reasoning}")
    print(f"  Оценка времени: {plan.estimated_time}s")
    print(f"  Количество действий: {len(plan.actions)}")
    
    print("\n  Детальный план:")
    for i, action in enumerate(plan.actions, 1):
        print(f"\n  Шаг {i}:")
        print(f"    Действие: {action.description}")
        print(f"    Тип: {action.type}")
        print(f"    Параметры: {action.parameters}")
        print(f"    Рассуждение: {action.reasoning}")
    
    # Execute
    print("\n⚡ Фаза 3: Выполнение...")
    result = await agent._execute_plan(plan)
    
    print(f"\n📊 Результаты:")
    print(f"  Всего шагов: {result['total_steps']}")
    print(f"  Успешно: {result['successful_steps']}")
    print(f"  Неудачно: {result['failed_steps']}")
    
    print("\n✓ Демонстрация завершена!")


async def demo_interactive_chat():
    """Demonstrate interactive chat capabilities"""
    
    print("\n" + "="*60)
    print("Demo 4: Interactive Chat")
    print("="*60 + "\n")
    
    agent = IntelligentAgent()
    
    interactions = [
        "Что ты умеешь делать?",
        "Открой Калькулятор",
        "Как создать папку?",
        "Создай папку 'Test' в Finder"
    ]
    
    for i, message in enumerate(interactions, 1):
        print(f"\n[{i}/{len(interactions)}] Пользователь: {message}")
        print("-" * 60)
        
        response = await agent.chat(message)
        
        print(f"🤖 Daur AI: {response}")
        
        await asyncio.sleep(2)


async def main():
    """Run all demonstrations"""
    
    print("\n" + "="*60)
    print("🤖 Daur AI - Intelligent Agent Demonstration")
    print("="*60)
    print("\nЭтот агент понимает естественный язык, планирует действия")
    print("и автоматически управляет вашим MacBook!")
    print("\n⚠️  Убедитесь что OPENAI_API_KEY установлен")
    print("\nНачинаем демонстрацию через 3 секунды...")
    
    await asyncio.sleep(3)
    
    try:
        # Run demos
        await demo_simple_commands()
        await asyncio.sleep(2)
        
        await demo_complex_automation()
        await asyncio.sleep(2)
        
        await demo_planning_and_reasoning()
        await asyncio.sleep(2)
        
        await demo_interactive_chat()
        
        print("\n" + "="*60)
        print("✓ Все демонстрации завершены!")
        print("="*60)
        print("\nТеперь попробуйте сами:")
        print("  python3 daur_chat.py")
        print()
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

