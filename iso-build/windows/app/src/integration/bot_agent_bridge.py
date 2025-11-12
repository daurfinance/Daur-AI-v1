"""
Мост между Telegram ботом и AI агентом
Обеспечивает интеграцию и синхронизацию между компонентами
"""

import asyncio
import json
import logging
import threading
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import queue
import uuid

# Импорты проекта
try:
    from agent.integrated_ai_agent import IntegratedAIAgent, Task, TaskPriority
except ImportError:
    IntegratedAIAgent = None
    Task = None
    TaskPriority = None

try:
    from telegram.daur_ai_bot import DaurAITelegramBot
except ImportError:
    DaurAITelegramBot = None

try:
    from config.settings import Settings
except ImportError as e:
    logging.warning(f"Не удалось импортировать модули: {e}")
    Settings = None

class TaskStatus(Enum):
    """Статусы задач"""
    PENDING = "pending"
    RUNNING = "running" 
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class BridgeTask:
    """Задача в системе моста"""
    id: str
    description: str
    user_id: str
    telegram_chat_id: int
    priority: TaskPriority
    status: TaskStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    progress: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Конвертация в словарь"""
        data = asdict(self)
        # Конвертируем datetime в строки
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
            elif isinstance(value, Enum):
                data[key] = value.value
        return data

class BotAgentBridge:
    """Мост между Telegram ботом и AI агентом"""
    
    def __init__(self, config_path: str = None):
        self.logger = logging.getLogger(__name__)
        
        # Компоненты системы
        self.ai_agent: Optional[IntegratedAIAgent] = None
        self.telegram_bot: Optional[DaurAITelegramBot] = None
        
        # Управление задачами
        self.tasks: Dict[str, BridgeTask] = {}
        self.task_queue = queue.Queue()
        self.active_tasks: Dict[str, threading.Thread] = {}
        
        # Callbacks для уведомлений
        self.task_callbacks: Dict[str, List[Callable]] = {
            'on_task_start': [],
            'on_task_progress': [],
            'on_task_complete': [],
            'on_task_error': []
        }
        
        # Статистика
        self.stats = {
            'total_tasks': 0,
            'completed_tasks': 0,
            'failed_tasks': 0,
            'active_tasks': 0,
            'uptime_start': datetime.now()
        }
        
        # Флаги состояния
        self.is_running = False
        self.worker_thread = None
        
        # Загружаем конфигурацию
        self.config = self.load_config(config_path)
        
    def load_config(self, config_path: str = None) -> Dict[str, Any]:
        """Загрузка конфигурации"""
        default_config = {
            'max_concurrent_tasks': 3,
            'task_timeout': 300,
            'auto_cleanup_hours': 24,
            'notification_enabled': True,
            'progress_updates': True
        }
        
        if config_path:
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                    default_config.update(file_config.get('bridge', {}))
            except Exception as e:
                self.logger.warning(f"Не удалось загрузить конфиг: {e}")
        
        return default_config
    
    async def initialize(self):
        """Инициализация моста"""
        try:
            self.logger.info("Инициализация BotAgentBridge...")
            
            # Инициализируем AI агента
            if not self.ai_agent:
                self.ai_agent = IntegratedAIAgent()
                await self.ai_agent.initialize()
                self.logger.info("AI агент инициализирован")
            
            # Запускаем рабочий поток
            self.is_running = True
            self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
            self.worker_thread.start()
            
            self.logger.info("BotAgentBridge успешно инициализирован")
            
        except Exception as e:
            self.logger.error(f"Ошибка инициализации моста: {e}")
            raise
    
    def set_telegram_bot(self, bot: DaurAITelegramBot):
        """Установка Telegram бота"""
        self.telegram_bot = bot
        self.logger.info("Telegram бот подключен к мосту")
    
    async def submit_task(self, description: str, user_id: str, chat_id: int, 
                         priority: TaskPriority = TaskPriority.MEDIUM) -> str:
        """Отправка задачи на выполнение"""
        try:
            # Создаем задачу
            task_id = str(uuid.uuid4())
            task = BridgeTask(
                id=task_id,
                description=description,
                user_id=user_id,
                telegram_chat_id=chat_id,
                priority=priority,
                status=TaskStatus.PENDING,
                created_at=datetime.now()
            )
            
            # Сохраняем задачу
            self.tasks[task_id] = task
            
            # Добавляем в очередь
            self.task_queue.put(task_id)
            
            # Обновляем статистику
            self.stats['total_tasks'] += 1
            
            # Уведомляем о создании задачи
            await self._notify_task_event('on_task_start', task)
            
            self.logger.info(f"Задача {task_id} добавлена в очередь: {description}")
            return task_id
            
        except Exception as e:
            self.logger.error(f"Ошибка создания задачи: {e}")
            raise
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Получение статуса задачи"""
        task = self.tasks.get(task_id)
        if task:
            return task.to_dict()
        return None
    
    def get_user_tasks(self, user_id: str) -> List[Dict[str, Any]]:
        """Получение задач пользователя"""
        user_tasks = []
        for task in self.tasks.values():
            if task.user_id == user_id:
                user_tasks.append(task.to_dict())
        
        # Сортируем по времени создания
        user_tasks.sort(key=lambda x: x['created_at'], reverse=True)
        return user_tasks
    
    def cancel_task(self, task_id: str) -> bool:
        """Отмена задачи"""
        task = self.tasks.get(task_id)
        if not task:
            return False
        
        if task.status in [TaskStatus.PENDING, TaskStatus.RUNNING]:
            task.status = TaskStatus.CANCELLED
            task.completed_at = datetime.now()
            
            # Останавливаем активную задачу
            if task_id in self.active_tasks:
                # В реальной реализации здесь должна быть логика остановки
                pass
            
            self.logger.info(f"Задача {task_id} отменена")
            return True
        
        return False
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Получение статистики системы"""
        uptime = datetime.now() - self.stats['uptime_start']
        
        return {
            'total_tasks': self.stats['total_tasks'],
            'completed_tasks': self.stats['completed_tasks'],
            'failed_tasks': self.stats['failed_tasks'],
            'active_tasks': len(self.active_tasks),
            'pending_tasks': self.task_queue.qsize(),
            'uptime_seconds': int(uptime.total_seconds()),
            'agent_status': 'active' if self.ai_agent else 'inactive',
            'bot_status': 'active' if self.telegram_bot else 'inactive'
        }
    
    def _worker_loop(self):
        """Основной рабочий цикл"""
        self.logger.info("Запущен рабочий поток моста")
        
        while self.is_running:
            try:
                # Получаем задачу из очереди (с таймаутом)
                try:
                    task_id = self.task_queue.get(timeout=1.0)
                except queue.Empty:
                    continue
                
                # Проверяем лимит одновременных задач
                if len(self.active_tasks) >= self.config['max_concurrent_tasks']:
                    # Возвращаем задачу в очередь
                    self.task_queue.put(task_id)
                    continue
                
                # Запускаем выполнение задачи
                task_thread = threading.Thread(
                    target=self._execute_task,
                    args=(task_id,),
                    daemon=True
                )
                
                self.active_tasks[task_id] = task_thread
                task_thread.start()
                
            except Exception as e:
                self.logger.error(f"Ошибка в рабочем цикле: {e}")
        
        self.logger.info("Рабочий поток моста остановлен")
    
    def _execute_task(self, task_id: str):
        """Выполнение задачи"""
        task = self.tasks.get(task_id)
        if not task:
            return
        
        try:
            self.logger.info(f"Начинаем выполнение задачи {task_id}")
            
            # Обновляем статус
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.now()
            self.stats['active_tasks'] += 1
            
            # Уведомляем о начале выполнения
            asyncio.run(self._notify_task_event('on_task_start', task))
            
            # Выполняем задачу через AI агента
            if self.ai_agent:
                # Создаем задачу для агента
                agent_task = Task(
                    description=task.description,
                    priority=task.priority,
                    user_id=task.user_id
                )
                
                # Выполняем (синхронно в отдельном потоке)
                result = asyncio.run(self.ai_agent.execute_task(agent_task))
                
                # Сохраняем результат
                task.result = result
                task.status = TaskStatus.COMPLETED
                task.progress = 100.0
                
                self.stats['completed_tasks'] += 1
                
                # Уведомляем о завершении
                asyncio.run(self._notify_task_event('on_task_complete', task))
                
            else:
                raise Exception("AI агент недоступен")
            
        except Exception as e:
            self.logger.error(f"Ошибка выполнения задачи {task_id}: {e}")
            
            task.status = TaskStatus.FAILED
            task.error = str(e)
            self.stats['failed_tasks'] += 1
            
            # Уведомляем об ошибке
            asyncio.run(self._notify_task_event('on_task_error', task))
        
        finally:
            # Завершаем задачу
            task.completed_at = datetime.now()
            self.stats['active_tasks'] -= 1
            
            # Удаляем из активных задач
            if task_id in self.active_tasks:
                del self.active_tasks[task_id]
            
            self.logger.info(f"Задача {task_id} завершена со статусом {task.status.value}")
    
    async def _notify_task_event(self, event_type: str, task: BridgeTask):
        """Уведомление о событии задачи"""
        try:
            # Вызываем зарегистрированные callbacks
            for callback in self.task_callbacks.get(event_type, []):
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(task)
                    else:
                        callback(task)
                except Exception as e:
                    self.logger.error(f"Ошибка в callback {event_type}: {e}")
            
            # Отправляем уведомление в Telegram
            if self.telegram_bot and self.config.get('notification_enabled', True):
                await self._send_telegram_notification(event_type, task)
                
        except Exception as e:
            self.logger.error(f"Ошибка уведомления о событии {event_type}: {e}")
    
    async def _send_telegram_notification(self, event_type: str, task: BridgeTask):
        """Отправка уведомления в Telegram"""
        try:
            if event_type == 'on_task_start':
                message = f"🚀 **Задача запущена**\n\n📝 {task.description}\n⏰ {task.created_at.strftime('%H:%M:%S')}"
            
            elif event_type == 'on_task_complete':
                message = f"✅ **Задача выполнена**\n\n📝 {task.description}\n⏱️ Время выполнения: {self._get_execution_time(task)}"
                
                if task.result and task.result.get('message'):
                    message += f"\n\n📋 **Результат:**\n{task.result['message']}"
            
            elif event_type == 'on_task_error':
                message = f"❌ **Ошибка выполнения**\n\n📝 {task.description}\n🚫 {task.error}"
            
            else:
                return
            
            # Отправляем сообщение (здесь нужна интеграция с Telegram API)
            # В реальной реализации используется bot.send_message()
            self.logger.info(f"Telegram уведомление: {message}")
            
        except Exception as e:
            self.logger.error(f"Ошибка отправки Telegram уведомления: {e}")
    
    def _get_execution_time(self, task: BridgeTask) -> str:
        """Получение времени выполнения задачи"""
        if task.started_at and task.completed_at:
            duration = task.completed_at - task.started_at
            seconds = int(duration.total_seconds())
            
            if seconds < 60:
                return f"{seconds} сек"
            elif seconds < 3600:
                minutes = seconds // 60
                return f"{minutes} мин {seconds % 60} сек"
            else:
                hours = seconds // 3600
                minutes = (seconds % 3600) // 60
                return f"{hours} ч {minutes} мин"
        
        return "N/A"
    
    def register_callback(self, event_type: str, callback: Callable):
        """Регистрация callback для событий"""
        if event_type in self.task_callbacks:
            self.task_callbacks[event_type].append(callback)
    
    def cleanup_old_tasks(self, hours: int = 24):
        """Очистка старых задач"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        tasks_to_remove = []
        for task_id, task in self.tasks.items():
            if (task.completed_at and task.completed_at < cutoff_time and 
                task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]):
                tasks_to_remove.append(task_id)
        
        for task_id in tasks_to_remove:
            del self.tasks[task_id]
        
        if tasks_to_remove:
            self.logger.info(f"Очищено {len(tasks_to_remove)} старых задач")
    
    def shutdown(self):
        """Остановка моста"""
        self.logger.info("Остановка BotAgentBridge...")
        
        self.is_running = False
        
        # Ждем завершения рабочего потока
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=5.0)
        
        # Отменяем активные задачи
        for task_id in list(self.active_tasks.keys()):
            self.cancel_task(task_id)
        
        self.logger.info("BotAgentBridge остановлен")


# Глобальный экземпляр моста
_bridge_instance: Optional[BotAgentBridge] = None

def get_bridge() -> BotAgentBridge:
    """Получение глобального экземпляра моста"""
    global _bridge_instance
    if _bridge_instance is None:
        _bridge_instance = BotAgentBridge()
    return _bridge_instance

def initialize_bridge(config_path: str = None) -> BotAgentBridge:
    """Инициализация глобального моста"""
    global _bridge_instance
    _bridge_instance = BotAgentBridge(config_path)
    return _bridge_instance
