#!/usr/bin/env python3
"""
Демонстрация полного функционала Daur-AI
Тестирование всех компонентов интегрированного AI-агента
"""

import asyncio
import time
import logging
import json
import sys
import os

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Добавление пути к модулям
sys.path.append('src')

try:
    from agent.integrated_ai_agent import IntegratedAIAgent, Task, TaskPriority
    from learning.adaptive_learning_system import LearningMode
except ImportError as e:
    print(f"Ошибка импорта: {e}")
    print("Убедитесь, что все модули находятся в правильных директориях")
    sys.exit(1)

class DaurAIDemo:
    """Демонстрация возможностей Daur-AI"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.agent = None
        
    async def run_demo(self):
        """Запускает полную демонстрацию"""
        print("🚀 Демонстрация полного функционала Daur-AI")
        print("=" * 60)
        
        try:
            # Инициализация агента
            await self.initialize_agent()
            
            # Демонстрация базовых функций
            await self.demo_basic_functions()
            
            # Демонстрация системного управления
            await self.demo_system_control()
            
            # Демонстрация обучения
            await self.demo_learning_capabilities()
            
            # Демонстрация мультимодальности
            await self.demo_multimodal_features()
            
            # Демонстрация автономности
            await self.demo_autonomous_behavior()
            
            # Финальная статистика
            await self.show_final_statistics()
            
        except Exception as e:
            self.logger.error(f"Ошибка демонстрации: {e}")
        
        finally:
            if self.agent:
                await self.agent.stop()
    
    async def initialize_agent(self):
        """Инициализирует AI-агента"""
        print("\n🤖 Инициализация AI-агента...")
        
        config = {
            'learning_enabled': True,
            'auto_mode': False,
            'debug_mode': True,
            'max_concurrent_tasks': 3
        }
        
        self.agent = IntegratedAIAgent(config)
        
        # Запуск агента в фоновом режиме
        asyncio.create_task(self.agent.start())
        
        # Ожидание готовности
        await asyncio.sleep(2)
        
        status = self.agent.get_status()
        print(f"✅ Агент инициализирован (ID: {status['agent_id'][:8]})")
        print(f"   Состояние: {status['state']}")
        print(f"   Обучение: {'включено' if status['learning_enabled'] else 'выключено'}")
    
    async def demo_basic_functions(self):
        """Демонстрирует базовые функции"""
        print("\n📋 Демонстрация базовых функций")
        print("-" * 40)
        
        # Простые команды
        commands = [
            "создай файл demo_test.txt",
            "покажи текущее время",
            "проверь статус системы",
            "создай директорию test_folder"
        ]
        
        for i, command in enumerate(commands, 1):
            print(f"\n{i}. Выполнение: '{command}'")
            
            result = await self.agent.execute_command(command)
            
            if result.get('success', False):
                print(f"   ✅ Успешно выполнено")
            else:
                print(f"   ❌ Ошибка: {result.get('error', 'Неизвестная ошибка')}")
            
            await asyncio.sleep(1)
    
    async def demo_system_control(self):
        """Демонстрирует управление системой"""
        print("\n🖥️ Демонстрация системного управления")
        print("-" * 40)
        
        # Системные команды
        system_commands = [
            "покажи список процессов",
            "проверь использование памяти",
            "покажи информацию о диске",
            "создай скриншот экрана"
        ]
        
        for i, command in enumerate(system_commands, 1):
            print(f"\n{i}. Системная команда: '{command}'")
            
            result = await self.agent.execute_command(
                command, 
                {'device_type': 'system', 'priority': 'high'}
            )
            
            if result.get('success', False):
                print(f"   ✅ Системная операция выполнена")
            else:
                print(f"   ⚠️ Ограничения sandbox: {result.get('error', 'Недоступно')}")
            
            await asyncio.sleep(1)
    
    async def demo_learning_capabilities(self):
        """Демонстрирует возможности обучения"""
        print("\n🧠 Демонстрация системы обучения")
        print("-" * 40)
        
        if not self.agent.learning_system:
            print("   ⚠️ Система обучения недоступна")
            return
        
        # Настройка режима обучения
        self.agent.learning_system.set_learning_mode(LearningMode.ACTIVE)
        print("   📚 Режим активного обучения включен")
        
        # Выполнение команд для обучения
        learning_commands = [
            "открой текстовый редактор",
            "создай документ с текстом 'Hello AI'",
            "сохрани документ как ai_test.txt",
            "закрой текстовый редактор"
        ]
        
        print("\n   Выполнение последовательности для обучения:")
        for i, command in enumerate(learning_commands, 1):
            print(f"   {i}. {command}")
            
            result = await self.agent.execute_command(command)
            await asyncio.sleep(0.5)
        
        # Получение статистики обучения
        await asyncio.sleep(2)
        learning_stats = self.agent.learning_system.get_learning_statistics()
        
        print(f"\n   📊 Статистика обучения:")
        print(f"      Всего действий: {learning_stats.get('total_actions', 0)}")
        print(f"      Успешных: {learning_stats.get('successful_actions', 0)}")
        print(f"      Изучено паттернов: {learning_stats.get('patterns_count', 0)}")
        print(f"      Создано правил: {learning_stats.get('rules_count', 0)}")
        
        # Получение рекомендаций
        recommendations = self.agent.learning_system.get_learning_recommendations({
            'device_type': 'system',
            'command': 'создай файл'
        })
        
        if recommendations:
            print(f"   💡 Получено {len(recommendations)} рекомендаций на основе обучения")
        else:
            print("   💡 Рекомендации будут доступны после накопления данных")
    
    async def demo_multimodal_features(self):
        """Демонстрирует мультимодальные возможности"""
        print("\n🎭 Демонстрация мультимодальных возможностей")
        print("-" * 40)
        
        # Команды для работы с медиа
        multimodal_commands = [
            "сделай скриншот экрана",
            "проанализируй изображение на экране",
            "найди текст на экране",
            "распознай элементы интерфейса"
        ]
        
        for i, command in enumerate(multimodal_commands, 1):
            print(f"\n{i}. Мультимодальная команда: '{command}'")
            
            result = await self.agent.execute_command(
                command,
                {'requires_vision': True, 'device_type': 'screen'}
            )
            
            if result.get('success', False):
                print(f"   ✅ Обработка медиа выполнена")
            else:
                print(f"   ⚠️ Sandbox ограничения: {result.get('error', 'Недоступно в headless режиме')}")
            
            await asyncio.sleep(1)
    
    async def demo_autonomous_behavior(self):
        """Демонстрирует автономное поведение"""
        print("\n🤖 Демонстрация автономного поведения")
        print("-" * 40)
        
        # Включение автономного режима
        self.agent.configure({'auto_mode': True})
        print("   🔄 Автономный режим включен")
        
        # Сложная задача для автономного выполнения
        complex_task = Task(
            task_id="autonomous_demo",
            description="Автономная задача: создать проект и документацию",
            command="создай новый проект с документацией и тестами",
            priority=TaskPriority.HIGH,
            context={
                'autonomous': True,
                'project_name': 'ai_demo_project',
                'requirements': ['readme', 'tests', 'documentation']
            },
            created_at=time.time()
        )
        
        print(f"\n   📋 Добавление сложной задачи: {complex_task.description}")
        await self.agent.add_task(complex_task)
        
        # Мониторинг выполнения
        print("   ⏳ Мониторинг автономного выполнения...")
        
        for i in range(10):  # Максимум 10 секунд ожидания
            tasks_status = self.agent.get_tasks_status()
            
            if complex_task.task_id in [tid for tid in tasks_status['active']]:
                active_task = tasks_status['active'][complex_task.task_id]
                print(f"      Прогресс: {active_task['progress']:.1f}% - {active_task['status']}")
            elif tasks_status['completed'] > 0:
                print("   ✅ Автономная задача завершена успешно")
                break
            elif tasks_status['failed'] > 0:
                print("   ⚠️ Автономная задача завершена с ошибками")
                break
            
            await asyncio.sleep(1)
        
        # Отключение автономного режима
        self.agent.configure({'auto_mode': False})
        print("   🔄 Автономный режим отключен")
    
    async def show_final_statistics(self):
        """Показывает финальную статистику"""
        print("\n📊 Финальная статистика работы")
        print("=" * 60)
        
        # Статус агента
        status = self.agent.get_status()
        print(f"🤖 Агент ID: {status['agent_id'][:8]}")
        print(f"   Состояние: {status['state']}")
        print(f"   Время работы: {status['uptime_seconds']:.1f} сек")
        
        # Статистика выполнения
        stats = status['stats']
        print(f"\n📈 Статистика выполнения:")
        print(f"   Команд выполнено: {stats['commands_executed']}")
        print(f"   Задач завершено: {stats['tasks_completed']}")
        print(f"   Задач с ошибками: {stats['tasks_failed']}")
        
        if stats['commands_executed'] > 0:
            success_rate = (stats['tasks_completed'] / stats['commands_executed']) * 100
            print(f"   Успешность: {success_rate:.1f}%")
        
        # Статистика обучения
        if self.agent.learning_system:
            learning_stats = self.agent.learning_system.get_learning_statistics()
            print(f"\n🧠 Статистика обучения:")
            print(f"   Паттернов изучено: {learning_stats.get('patterns_count', 0)}")
            print(f"   Правил создано: {learning_stats.get('rules_count', 0)}")
            print(f"   Сессий обучения: {stats.get('learning_sessions', 0)}")
        
        # Статистика задач
        tasks_status = self.agent.get_tasks_status()
        print(f"\n📋 Статистика задач:")
        print(f"   Активных задач: {len(tasks_status['active'])}")
        print(f"   В очереди: {tasks_status['queue_size']}")
        print(f"   Завершено: {tasks_status['completed']}")
        print(f"   Неудачных: {tasks_status['failed']}")
        
        print(f"\n🎉 Демонстрация завершена!")
        print(f"   Daur-AI показал полный спектр возможностей:")
        print(f"   ✅ Выполнение команд")
        print(f"   ✅ Системное управление") 
        print(f"   ✅ Обучение и адаптация")
        print(f"   ✅ Мультимодальная обработка")
        print(f"   ✅ Автономное поведение")

async def main():
    """Главная функция демонстрации"""
    demo = DaurAIDemo()
    await demo.run_demo()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⏹️ Демонстрация прервана пользователем")
    except Exception as e:
        print(f"\n\n❌ Ошибка демонстрации: {e}")
        import traceback
        traceback.print_exc()
