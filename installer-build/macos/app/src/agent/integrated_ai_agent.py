"""
Интегрированный AI-агент с полным функционалом
Объединяет все компоненты системы в единого автономного агента
"""

import asyncio
import time
import logging
import json
import uuid
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from enum import Enum
import threading

# Импорт всех компонентов системы
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

try:
    from ai.autonomous_planner import AutonomousPlanner
    from ai.multimodal_manager import MultimodalManager
    from devices.device_controller import DeviceController
    from learning.adaptive_learning_system import AdaptiveLearningSystem, ActionResult, LearningMode
    from parser.enhanced_command_parser import EnhancedCommandParser
    from executor.command_executor import CommandExecutor
except ImportError as e:
    logging.warning(f"Некоторые компоненты недоступны: {e}")

# Определение DeviceType локально если не импортирован
try:
    from devices.device_controller import DeviceType
except ImportError:
    from enum import Enum
    class DeviceType(Enum):
        SYSTEM = "system"
        SCREEN = "screen"
        KEYBOARD = "keyboard"
        MOUSE = "mouse"
        CAMERA = "camera"
        MICROPHONE = "microphone"
        BROWSER = "browser"

class AgentState(Enum):
    """Состояния агента"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    LEARNING = "learning"

class TaskPriority(Enum):
    """Приоритеты задач"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4
    EMERGENCY = 5

@dataclass
class Task:
    """Задача для выполнения"""
    task_id: str
    description: str
    command: str
    priority: TaskPriority
    context: Dict
    created_at: float
    deadline: Optional[float] = None
    dependencies: List[str] = None
    progress: float = 0.0
    status: str = "pending"
    result: Optional[Dict] = None

class IntegratedAIAgent:
    """Интегрированный AI-агент с полным функционалом"""
    
    def __init__(self, config: Dict = None):
        self.logger = logging.getLogger(__name__)
        
        # Конфигурация
        self.config = config or {}
        
        # Состояние агента
        self.state = AgentState.STOPPED
        self.agent_id = str(uuid.uuid4())
        self.start_time = None
        
        # Компоненты системы
        self.planner = None
        self.multimodal_manager = None
        self.device_controller = None
        self.learning_system = None
        self.command_parser = None
        self.command_executor = None
        
        # Управление задачами
        self.task_queue = asyncio.PriorityQueue()
        self.active_tasks = {}
        self.completed_tasks = {}
        self.failed_tasks = {}
        
        # Контекст и память
        self.working_memory = {}
        self.long_term_memory = {}
        self.current_context = {}
        
        # Статистика
        self.stats = {
            'tasks_completed': 0,
            'tasks_failed': 0,
            'commands_executed': 0,
            'learning_sessions': 0,
            'uptime_seconds': 0,
            'devices_controlled': 0,
            'patterns_learned': 0
        }
        
        # Настройки
        self.max_concurrent_tasks = 5
        self.learning_enabled = True
        self.auto_mode = False
        self.debug_mode = False
        
        # Блокировки для многопоточности
        self.state_lock = threading.Lock()
        self.task_lock = threading.Lock()
        
        # Инициализация
        self._initialize_components()
    
    def _initialize_components(self):
        """Инициализирует все компоненты системы"""
        try:
            self.logger.info("Инициализация компонентов AI-агента...")
            
            # Планировщик задач
            try:
                self.planner = AutonomousPlanner()
                self.logger.info("Автономный планировщик инициализирован")
            except Exception as e:
                self.logger.warning(f"Не удалось инициализировать планировщик: {e}")
            
            # Мультимодальный менеджер
            try:
                self.multimodal_manager = MultimodalManager()
                self.logger.info("Мультимодальный менеджер инициализирован")
            except Exception as e:
                self.logger.warning(f"Не удалось инициализировать мультимодальный менеджер: {e}")
            
            # Контроллер устройств
            try:
                self.device_controller = DeviceController()
                self.logger.info("Контроллер устройств инициализирован")
            except Exception as e:
                self.logger.warning(f"Не удалось инициализировать контроллер устройств: {e}")
            
            # Система обучения
            try:
                self.learning_system = AdaptiveLearningSystem()
                if self.learning_enabled:
                    self.learning_system.set_learning_mode(LearningMode.ACTIVE)
                self.logger.info("Система обучения инициализирована")
            except Exception as e:
                self.logger.warning(f"Не удалось инициализировать систему обучения: {e}")
            
            # Парсер команд
            try:
                self.command_parser = EnhancedCommandParser()
                self.logger.info("Парсер команд инициализирован")
            except Exception as e:
                self.logger.warning(f"Не удалось инициализировать парсер команд: {e}")
            
            # Исполнитель команд
            try:
                self.command_executor = CommandExecutor()
                self.logger.info("Исполнитель команд инициализирован")
            except Exception as e:
                self.logger.warning(f"Не удалось инициализировать исполнитель команд: {e}")
            
            self.logger.info("Все компоненты AI-агента инициализированы")
            
        except Exception as e:
            self.logger.error(f"Ошибка инициализации компонентов: {e}")
            self.state = AgentState.ERROR
    
    async def start(self):
        """Запускает AI-агента"""
        try:
            with self.state_lock:
                if self.state != AgentState.STOPPED:
                    raise ValueError(f"Агент не может быть запущен в состоянии {self.state.value}")
                
                self.state = AgentState.STARTING
                self.start_time = time.time()
            
            self.logger.info("Запуск AI-агента...")
            
            # Проверка готовности компонентов
            await self._check_components_health()
            
            # Запуск основного цикла
            self.state = AgentState.RUNNING
            
            # Создание задач для основных циклов
            tasks = [
                asyncio.create_task(self._main_execution_loop()),
                asyncio.create_task(self._monitoring_loop()),
                asyncio.create_task(self._learning_loop())
            ]
            
            self.logger.info(f"AI-агент запущен (ID: {self.agent_id})")
            
            # Ожидание завершения всех задач
            await asyncio.gather(*tasks, return_exceptions=True)
            
        except Exception as e:
            self.logger.error(f"Ошибка запуска агента: {e}")
            self.state = AgentState.ERROR
            raise
    
    async def stop(self):
        """Останавливает AI-агента"""
        try:
            with self.state_lock:
                if self.state == AgentState.STOPPED:
                    return
                
                self.logger.info("Остановка AI-агента...")
                self.state = AgentState.STOPPED
            
            # Завершение активных задач
            await self._cleanup_active_tasks()
            
            # Сохранение состояния
            await self._save_state()
            
            # Очистка ресурсов
            await self._cleanup_resources()
            
            self.logger.info("AI-агент остановлен")
            
        except Exception as e:
            self.logger.error(f"Ошибка остановки агента: {e}")
    
    async def pause(self):
        """Приостанавливает работу агента"""
        try:
            with self.state_lock:
                if self.state == AgentState.RUNNING:
                    self.state = AgentState.PAUSED
                    self.logger.info("AI-агент приостановлен")
                
        except Exception as e:
            self.logger.error(f"Ошибка приостановки агента: {e}")
    
    async def resume(self):
        """Возобновляет работу агента"""
        try:
            with self.state_lock:
                if self.state == AgentState.PAUSED:
                    self.state = AgentState.RUNNING
                    self.logger.info("Работа AI-агента возобновлена")
                
        except Exception as e:
            self.logger.error(f"Ошибка возобновления работы агента: {e}")
    
    async def execute_command(self, command: str, context: Dict = None) -> Dict:
        """Выполняет команду"""
        try:
            # Создание задачи
            task = Task(
                task_id=str(uuid.uuid4()),
                description=f"Выполнение команды: {command}",
                command=command,
                priority=TaskPriority.NORMAL,
                context=context or {},
                created_at=time.time()
            )
            
            # Добавление в очередь
            await self.add_task(task)
            
            # Ожидание выполнения
            return await self._wait_for_task_completion(task.task_id)
            
        except Exception as e:
            self.logger.error(f"Ошибка выполнения команды: {e}")
            return {'success': False, 'error': str(e)}
    
    async def add_task(self, task: Task):
        """Добавляет задачу в очередь"""
        try:
            with self.task_lock:
                # Приоритетная очередь (меньшее число = выше приоритет)
                priority = -task.priority.value
                await self.task_queue.put((priority, task.created_at, task))
                
                self.logger.info(f"Задача добавлена: {task.description}")
            
        except Exception as e:
            self.logger.error(f"Ошибка добавления задачи: {e}")
    
    async def _main_execution_loop(self):
        """Основной цикл выполнения задач"""
        try:
            while self.state in [AgentState.RUNNING, AgentState.PAUSED]:
                try:
                    if self.state == AgentState.PAUSED:
                        await asyncio.sleep(1)
                        continue
                    
                    # Получение задачи из очереди
                    try:
                        priority, created_at, task = await asyncio.wait_for(
                            self.task_queue.get(), timeout=1.0
                        )
                    except asyncio.TimeoutError:
                        continue
                    
                    # Проверка лимита одновременных задач
                    if len(self.active_tasks) >= self.max_concurrent_tasks:
                        # Возврат задачи в очередь
                        await self.task_queue.put((priority, created_at, task))
                        await asyncio.sleep(0.1)
                        continue
                    
                    # Выполнение задачи
                    self.active_tasks[task.task_id] = task
                    asyncio.create_task(self._execute_task(task))
                    
                except Exception as e:
                    self.logger.error(f"Ошибка в основном цикле выполнения: {e}")
                    await asyncio.sleep(1)
            
        except Exception as e:
            self.logger.error(f"Критическая ошибка в основном цикле: {e}")
            self.state = AgentState.ERROR
    
    async def _execute_task(self, task: Task):
        """Выполняет отдельную задачу"""
        start_time = time.time()
        
        try:
            self.logger.info(f"Начало выполнения задачи: {task.description}")
            task.status = "running"
            
            # Парсинг команды
            if self.command_parser:
                parsed_command = await self._parse_command(task.command, task.context)
            else:
                parsed_command = {'action': 'unknown', 'parameters': {}}
            
            # Планирование выполнения
            if self.planner:
                execution_plan = await self._create_execution_plan(parsed_command, task.context)
            else:
                execution_plan = [parsed_command]
            
            # Выполнение плана
            result = await self._execute_plan(execution_plan, task)
            
            # Обновление прогресса
            task.progress = 100.0
            task.status = "completed" if result.get('success', False) else "failed"
            task.result = result
            
            # Запись результата для обучения
            if self.learning_system:
                action_result = ActionResult(
                    action_id=task.task_id,
                    command=task.command,
                    device_type=parsed_command.get('device_type', 'unknown'),
                    parameters=parsed_command.get('parameters', {}),
                    success=result.get('success', False),
                    execution_time=time.time() - start_time,
                    error_message=result.get('error'),
                    confidence_score=result.get('confidence', 0.0),
                    timestamp=time.time()
                )
                
                self.learning_system.record_action_result(action_result)
            
            # Обновление статистики
            if result.get('success', False):
                self.stats['tasks_completed'] += 1
            else:
                self.stats['tasks_failed'] += 1
            
            self.stats['commands_executed'] += 1
            
            # Перемещение в соответствующий список
            if task.status == "completed":
                self.completed_tasks[task.task_id] = task
            else:
                self.failed_tasks[task.task_id] = task
            
            self.logger.info(f"Задача завершена: {task.description} ({task.status})")
            
        except Exception as e:
            self.logger.error(f"Ошибка выполнения задачи {task.task_id}: {e}")
            task.status = "failed"
            task.result = {'success': False, 'error': str(e)}
            self.failed_tasks[task.task_id] = task
            self.stats['tasks_failed'] += 1
            
        finally:
            # Удаление из активных задач
            if task.task_id in self.active_tasks:
                del self.active_tasks[task.task_id]
    
    async def _parse_command(self, command: str, context: Dict) -> Dict:
        """Парсит команду"""
        try:
            if self.command_parser:
                return await self.command_parser.parse_command(command, context)
            else:
                # Базовый парсинг
                return {
                    'action': 'execute',
                    'command': command,
                    'device_type': 'system',
                    'parameters': {'raw_command': command}
                }
            
        except Exception as e:
            self.logger.error(f"Ошибка парсинга команды: {e}")
            return {'action': 'error', 'error': str(e)}
    
    async def _create_execution_plan(self, parsed_command: Dict, context: Dict) -> List[Dict]:
        """Создает план выполнения"""
        try:
            if self.planner:
                return await self.planner.create_plan(parsed_command, context)
            else:
                return [parsed_command]
            
        except Exception as e:
            self.logger.error(f"Ошибка создания плана выполнения: {e}")
            return [parsed_command]
    
    async def _execute_plan(self, plan: List[Dict], task: Task) -> Dict:
        """Выполняет план действий"""
        try:
            results = []
            
            for i, step in enumerate(plan):
                # Обновление прогресса
                task.progress = (i / len(plan)) * 100
                
                # Выполнение шага
                step_result = await self._execute_step(step, task.context)
                results.append(step_result)
                
                # Проверка на ошибку
                if not step_result.get('success', False):
                    return {
                        'success': False,
                        'error': step_result.get('error', 'Неизвестная ошибка'),
                        'step_results': results
                    }
            
            return {
                'success': True,
                'step_results': results,
                'message': 'План выполнен успешно'
            }
            
        except Exception as e:
            self.logger.error(f"Ошибка выполнения плана: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _execute_step(self, step: Dict, context: Dict) -> Dict:
        """Выполняет отдельный шаг плана"""
        try:
            action = step.get('action', 'unknown')
            device_type_str = step.get('device_type', 'system')
            parameters = step.get('parameters', {})
            
            # Конвертация строки в DeviceType
            try:
                device_type = DeviceType(device_type_str)
            except ValueError:
                return {'success': False, 'error': f'Неизвестный тип устройства: {device_type_str}'}
            
            # Выполнение через контроллер устройств
            if self.device_controller:
                result = await self.device_controller.execute_command(device_type, action, parameters)
                return result
            
            # Альтернативное выполнение через исполнитель команд
            elif self.command_executor:
                command = step.get('command', '')
                result = await self.command_executor.execute(command, parameters)
                return result
            
            else:
                return {'success': False, 'error': 'Нет доступных исполнителей'}
            
        except Exception as e:
            self.logger.error(f"Ошибка выполнения шага: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _monitoring_loop(self):
        """Цикл мониторинга системы"""
        try:
            while self.state in [AgentState.RUNNING, AgentState.PAUSED]:
                try:
                    # Обновление статистики времени работы
                    if self.start_time:
                        self.stats['uptime_seconds'] = time.time() - self.start_time
                    
                    # Мониторинг устройств
                    if self.device_controller:
                        health_status = await self.device_controller.health_check()
                        if not health_status.get('overall_healthy', False):
                            self.logger.warning("Обнаружены проблемы с устройствами")
                    
                    # Мониторинг очереди задач
                    queue_size = self.task_queue.qsize()
                    if queue_size > 100:
                        self.logger.warning(f"Большая очередь задач: {queue_size}")
                    
                    # Мониторинг памяти
                    if len(self.working_memory) > 1000:
                        self._cleanup_working_memory()
                    
                    await asyncio.sleep(10)  # Мониторинг каждые 10 секунд
                    
                except Exception as e:
                    self.logger.error(f"Ошибка в цикле мониторинга: {e}")
                    await asyncio.sleep(5)
            
        except Exception as e:
            self.logger.error(f"Критическая ошибка в цикле мониторинга: {e}")
    
    async def _learning_loop(self):
        """Цикл обучения и адаптации"""
        try:
            while self.state in [AgentState.RUNNING, AgentState.PAUSED]:
                try:
                    if self.state == AgentState.PAUSED or not self.learning_enabled:
                        await asyncio.sleep(30)
                        continue
                    
                    if self.learning_system:
                        # Получение рекомендаций для улучшения
                        recommendations = self.learning_system.get_learning_recommendations(
                            self.current_context
                        )
                        
                        # Применение рекомендаций
                        if recommendations:
                            await self._apply_learning_recommendations(recommendations)
                        
                        # Обновление статистики обучения
                        learning_stats = self.learning_system.get_learning_statistics()
                        self.stats['patterns_learned'] = learning_stats.get('patterns_count', 0)
                        self.stats['learning_sessions'] += 1
                    
                    await asyncio.sleep(60)  # Обучение каждую минуту
                    
                except Exception as e:
                    self.logger.error(f"Ошибка в цикле обучения: {e}")
                    await asyncio.sleep(30)
            
        except Exception as e:
            self.logger.error(f"Критическая ошибка в цикле обучения: {e}")
    
    async def _apply_learning_recommendations(self, recommendations: List[Dict]):
        """Применяет рекомендации обучения"""
        try:
            for recommendation in recommendations[:3]:  # Топ-3 рекомендации
                if recommendation['confidence'] > 0.8:
                    # Создание задачи на основе рекомендации
                    recommended_actions = recommendation.get('recommended_actions', [])
                    
                    for action in recommended_actions:
                        if isinstance(action, dict) and 'command' in action:
                            task = Task(
                                task_id=str(uuid.uuid4()),
                                description=f"Рекомендованное действие: {action['command']}",
                                command=action['command'],
                                priority=TaskPriority.LOW,
                                context={'source': 'learning_recommendation'},
                                created_at=time.time()
                            )
                            
                            await self.add_task(task)
            
        except Exception as e:
            self.logger.error(f"Ошибка применения рекомендаций обучения: {e}")
    
    async def _wait_for_task_completion(self, task_id: str, timeout: float = 60.0) -> Dict:
        """Ожидает завершения задачи"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # Проверка в завершенных задачах
            if task_id in self.completed_tasks:
                return self.completed_tasks[task_id].result
            
            # Проверка в неудачных задачах
            if task_id in self.failed_tasks:
                return self.failed_tasks[task_id].result
            
            await asyncio.sleep(0.1)
        
        return {'success': False, 'error': 'Timeout waiting for task completion'}
    
    async def _check_components_health(self):
        """Проверяет здоровье всех компонентов"""
        try:
            health_issues = []
            
            # Проверка устройств
            if self.device_controller:
                device_health = await self.device_controller.health_check()
                if not device_health.get('overall_healthy', False):
                    health_issues.append("Проблемы с устройствами")
            
            # Проверка системы обучения
            if self.learning_system:
                learning_stats = self.learning_system.get_learning_statistics()
                if not learning_stats:
                    health_issues.append("Проблемы с системой обучения")
            
            if health_issues:
                self.logger.warning(f"Обнаружены проблемы: {', '.join(health_issues)}")
            else:
                self.logger.info("Все компоненты работают нормально")
            
        except Exception as e:
            self.logger.error(f"Ошибка проверки здоровья компонентов: {e}")
    
    def _cleanup_working_memory(self):
        """Очищает рабочую память"""
        try:
            # Перемещение старых данных в долговременную память
            current_time = time.time()
            
            items_to_remove = []
            for key, value in self.working_memory.items():
                if isinstance(value, dict) and 'timestamp' in value:
                    if current_time - value['timestamp'] > 3600:  # Старше часа
                        self.long_term_memory[key] = value
                        items_to_remove.append(key)
            
            for key in items_to_remove:
                del self.working_memory[key]
            
            self.logger.info(f"Очищена рабочая память: {len(items_to_remove)} элементов")
            
        except Exception as e:
            self.logger.error(f"Ошибка очистки рабочей памяти: {e}")
    
    async def _cleanup_active_tasks(self):
        """Завершает активные задачи"""
        try:
            for task_id, task in list(self.active_tasks.items()):
                task.status = "cancelled"
                task.result = {'success': False, 'error': 'Agent shutdown'}
                self.failed_tasks[task_id] = task
            
            self.active_tasks.clear()
            
        except Exception as e:
            self.logger.error(f"Ошибка завершения активных задач: {e}")
    
    async def _save_state(self):
        """Сохраняет состояние агента"""
        try:
            state_data = {
                'agent_id': self.agent_id,
                'stats': self.stats,
                'config': self.config,
                'completed_tasks_count': len(self.completed_tasks),
                'failed_tasks_count': len(self.failed_tasks),
                'timestamp': time.time()
            }
            
            # Сохранение в файл
            with open(f'agent_state_{self.agent_id}.json', 'w') as f:
                json.dump(state_data, f, indent=2)
            
            self.logger.info("Состояние агента сохранено")
            
        except Exception as e:
            self.logger.error(f"Ошибка сохранения состояния: {e}")
    
    async def _cleanup_resources(self):
        """Очищает ресурсы"""
        try:
            # Очистка контроллера устройств
            if self.device_controller:
                await self.device_controller.cleanup()
            
            # Очистка других компонентов
            self.working_memory.clear()
            self.current_context.clear()
            
            self.logger.info("Ресурсы очищены")
            
        except Exception as e:
            self.logger.error(f"Ошибка очистки ресурсов: {e}")
    
    def get_status(self) -> Dict:
        """Возвращает текущий статус агента"""
        return {
            'agent_id': self.agent_id,
            'state': self.state.value,
            'uptime_seconds': self.stats['uptime_seconds'],
            'active_tasks': len(self.active_tasks),
            'queue_size': self.task_queue.qsize(),
            'stats': dict(self.stats),
            'learning_enabled': self.learning_enabled,
            'auto_mode': self.auto_mode,
            'debug_mode': self.debug_mode
        }
    
    def get_tasks_status(self) -> Dict:
        """Возвращает статус задач"""
        return {
            'active': {tid: {'description': task.description, 'progress': task.progress, 'status': task.status} 
                      for tid, task in self.active_tasks.items()},
            'completed': len(self.completed_tasks),
            'failed': len(self.failed_tasks),
            'queue_size': self.task_queue.qsize()
        }
    
    def configure(self, config: Dict):
        """Настраивает агента"""
        try:
            self.config.update(config)
            
            # Применение настроек
            if 'learning_enabled' in config:
                self.learning_enabled = config['learning_enabled']
                if self.learning_system:
                    self.learning_system.enable_learning(self.learning_enabled)
            
            if 'auto_mode' in config:
                self.auto_mode = config['auto_mode']
            
            if 'debug_mode' in config:
                self.debug_mode = config['debug_mode']
            
            if 'max_concurrent_tasks' in config:
                self.max_concurrent_tasks = config['max_concurrent_tasks']
            
            self.logger.info("Конфигурация агента обновлена")
            
        except Exception as e:
            self.logger.error(f"Ошибка настройки агента: {e}")
