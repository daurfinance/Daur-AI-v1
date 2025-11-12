#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: Модуль планирования и управления задачами
Управление долгосрочными и рутинными задачами, планирование и мониторинг

Версия: 2.0
Дата: 25.10.2025
Автор: Manus AI
"""

import logging
import json
import time
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import heapq


class TaskPriority(Enum):
    """Приоритеты задач"""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4
    MINIMAL = 5


class TaskStatus(Enum):
    """Статусы задач"""
    PENDING = "pending"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RecurrenceType(Enum):
    """Типы повторений"""
    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"
    CUSTOM = "custom"


@dataclass
class Task:
    """Задача"""
    task_id: str
    title: str
    description: str = ""
    priority: TaskPriority = TaskPriority.NORMAL
    status: TaskStatus = TaskStatus.PENDING
    due_date: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    estimated_duration: int = 0  # в минутах
    actual_duration: int = 0  # в минутах
    subtasks: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    assigned_to: str = ""
    tags: List[str] = field(default_factory=list)
    attachments: List[str] = field(default_factory=list)
    notes: str = ""
    progress: int = 0  # 0-100
    error: Optional[str] = None


@dataclass
class RecurringTask:
    """Повторяющаяся задача"""
    task_id: str
    title: str
    description: str = ""
    priority: TaskPriority = TaskPriority.NORMAL
    recurrence_type: RecurrenceType = RecurrenceType.DAILY
    start_date: datetime = field(default_factory=datetime.now)
    end_date: Optional[datetime] = None
    interval: int = 1  # каждый N дней/недель/месяцев
    time_of_day: str = "09:00"  # HH:MM
    created_at: datetime = field(default_factory=datetime.now)
    enabled: bool = True
    next_occurrence: datetime = field(default_factory=datetime.now)


@dataclass
class Schedule:
    """График"""
    schedule_id: str
    name: str
    tasks: List[str] = field(default_factory=list)
    start_date: datetime = field(default_factory=datetime.now)
    end_date: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)


class TaskManager:
    """Менеджер задач"""
    
    def __init__(self):
        """Инициализация"""
        self.logger = logging.getLogger('daur_ai.task_manager')
        self.tasks: Dict[str, Task] = {}
        self.recurring_tasks: Dict[str, RecurringTask] = {}
        self.schedules: Dict[str, Schedule] = {}
        self.task_queue: List[Tuple[int, str]] = []  # Приоритетная очередь
    
    def create_task(self, task_id: str, title: str, description: str = "",
                   priority: TaskPriority = TaskPriority.NORMAL,
                   due_date: Optional[datetime] = None) -> Task:
        """
        Создать задачу
        
        Args:
            task_id: ID задачи
            title: Название
            description: Описание
            priority: Приоритет
            due_date: Срок выполнения
            
        Returns:
            Task: Объект задачи
        """
        task = Task(task_id, title, description, priority, due_date=due_date)
        self.tasks[task_id] = task
        
        # Добавляем в приоритетную очередь
        heapq.heappush(self.task_queue, (priority.value, task_id))
        
        self.logger.info(f"Задача создана: {task_id}")
        return task
    
    def create_recurring_task(self, task_id: str, title: str,
                             recurrence_type: RecurrenceType = RecurrenceType.DAILY,
                             description: str = "") -> RecurringTask:
        """
        Создать повторяющуюся задачу
        
        Args:
            task_id: ID задачи
            title: Название
            recurrence_type: Тип повторения
            description: Описание
            
        Returns:
            RecurringTask: Объект повторяющейся задачи
        """
        recurring_task = RecurringTask(task_id, title, description, recurrence_type=recurrence_type)
        self.recurring_tasks[task_id] = recurring_task
        self.logger.info(f"Повторяющаяся задача создана: {task_id}")
        return recurring_task
    
    def update_task_status(self, task_id: str, status: TaskStatus,
                          progress: int = 0, error: Optional[str] = None):
        """
        Обновить статус задачи
        
        Args:
            task_id: ID задачи
            status: Новый статус
            progress: Прогресс (0-100)
            error: Ошибка
        """
        if task_id not in self.tasks:
            self.logger.error(f"Задача не найдена: {task_id}")
            return
        
        task = self.tasks[task_id]
        task.status = status
        task.progress = progress
        
        if status == TaskStatus.RUNNING and not task.started_at:
            task.started_at = datetime.now()
        
        if status == TaskStatus.COMPLETED:
            task.completed_at = datetime.now()
            if task.started_at:
                task.actual_duration = int((task.completed_at - task.started_at).total_seconds() / 60)
        
        if error:
            task.error = error
        
        self.logger.info(f"Статус задачи обновлен: {task_id} -> {status.value}")
    
    def add_subtask(self, parent_task_id: str, subtask_id: str) -> bool:
        """
        Добавить подзадачу
        
        Args:
            parent_task_id: ID родительской задачи
            subtask_id: ID подзадачи
            
        Returns:
            bool: Успешность операции
        """
        if parent_task_id not in self.tasks:
            self.logger.error(f"Родительская задача не найдена: {parent_task_id}")
            return False
        
        if subtask_id not in self.tasks:
            self.logger.error(f"Подзадача не найдена: {subtask_id}")
            return False
        
        self.tasks[parent_task_id].subtasks.append(subtask_id)
        self.logger.info(f"Подзадача добавлена: {subtask_id} к {parent_task_id}")
        return True
    
    def add_dependency(self, task_id: str, dependency_id: str) -> bool:
        """
        Добавить зависимость
        
        Args:
            task_id: ID задачи
            dependency_id: ID зависимой задачи
            
        Returns:
            bool: Успешность операции
        """
        if task_id not in self.tasks:
            self.logger.error(f"Задача не найдена: {task_id}")
            return False
        
        if dependency_id not in self.tasks:
            self.logger.error(f"Зависимая задача не найдена: {dependency_id}")
            return False
        
        self.tasks[task_id].dependencies.append(dependency_id)
        self.logger.info(f"Зависимость добавлена: {task_id} зависит от {dependency_id}")
        return True
    
    def get_next_task(self) -> Optional[Task]:
        """
        Получить следующую задачу из очереди
        
        Returns:
            Optional[Task]: Следующая задача или None
        """
        while self.task_queue:
            _, task_id = heapq.heappop(self.task_queue)
            
            if task_id in self.tasks:
                task = self.tasks[task_id]
                if task.status == TaskStatus.PENDING:
                    return task
        
        return None
    
    def get_tasks_by_priority(self, priority: TaskPriority) -> List[Task]:
        """
        Получить задачи по приоритету
        
        Args:
            priority: Приоритет
            
        Returns:
            List[Task]: Список задач
        """
        return [task for task in self.tasks.values() if task.priority == priority]
    
    def get_overdue_tasks(self) -> List[Task]:
        """
        Получить просроченные задачи
        
        Returns:
            List[Task]: Список просроченных задач
        """
        now = datetime.now()
        return [
            task for task in self.tasks.values()
            if task.due_date and task.due_date < now and task.status != TaskStatus.COMPLETED
        ]
    
    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """
        Получить задачи по статусу
        
        Args:
            status: Статус
            
        Returns:
            List[Task]: Список задач
        """
        return [task for task in self.tasks.values() if task.status == status]
    
    def get_task_progress(self, task_id: str) -> Dict[str, Any]:
        """
        Получить прогресс задачи
        
        Args:
            task_id: ID задачи
            
        Returns:
            Dict: Информация о прогрессе
        """
        if task_id not in self.tasks:
            return {}
        
        task = self.tasks[task_id]
        
        subtask_progress = 0
        if task.subtasks:
            completed = sum(1 for st_id in task.subtasks if self.tasks[st_id].status == TaskStatus.COMPLETED)
            subtask_progress = (completed / len(task.subtasks)) * 100
        
        return {
            'task_id': task_id,
            'title': task.title,
            'status': task.status.value,
            'progress': task.progress,
            'subtask_progress': subtask_progress,
            'estimated_duration': task.estimated_duration,
            'actual_duration': task.actual_duration,
            'due_date': task.due_date.isoformat() if task.due_date else None
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Получить статус менеджера"""
        return {
            'total_tasks': len(self.tasks),
            'pending_tasks': len(self.get_tasks_by_status(TaskStatus.PENDING)),
            'running_tasks': len(self.get_tasks_by_status(TaskStatus.RUNNING)),
            'completed_tasks': len(self.get_tasks_by_status(TaskStatus.COMPLETED)),
            'failed_tasks': len(self.get_tasks_by_status(TaskStatus.FAILED)),
            'overdue_tasks': len(self.get_overdue_tasks()),
            'recurring_tasks': len(self.recurring_tasks)
        }


class ScheduleManager:
    """Менеджер графиков"""
    
    def __init__(self, task_manager: TaskManager):
        """
        Args:
            task_manager: Менеджер задач
        """
        self.task_manager = task_manager
        self.logger = logging.getLogger('daur_ai.schedule_manager')
        self.schedules: Dict[str, Schedule] = {}
    
    def create_schedule(self, schedule_id: str, name: str) -> Schedule:
        """
        Создать график
        
        Args:
            schedule_id: ID графика
            name: Имя
            
        Returns:
            Schedule: Объект графика
        """
        schedule = Schedule(schedule_id, name)
        self.schedules[schedule_id] = schedule
        self.logger.info(f"График создан: {schedule_id}")
        return schedule
    
    def add_task_to_schedule(self, schedule_id: str, task_id: str) -> bool:
        """
        Добавить задачу в график
        
        Args:
            schedule_id: ID графика
            task_id: ID задачи
            
        Returns:
            bool: Успешность операции
        """
        if schedule_id not in self.schedules:
            self.logger.error(f"График не найден: {schedule_id}")
            return False
        
        if task_id not in self.task_manager.tasks:
            self.logger.error(f"Задача не найдена: {task_id}")
            return False
        
        self.schedules[schedule_id].tasks.append(task_id)
        self.logger.info(f"Задача добавлена в график: {task_id}")
        return True
    
    def get_schedule_summary(self, schedule_id: str) -> Dict[str, Any]:
        """
        Получить сводку графика
        
        Args:
            schedule_id: ID графика
            
        Returns:
            Dict: Сводка графика
        """
        if schedule_id not in self.schedules:
            return {}
        
        schedule = self.schedules[schedule_id]
        tasks = [self.task_manager.tasks[task_id] for task_id in schedule.tasks if task_id in self.task_manager.tasks]
        
        completed = sum(1 for t in tasks if t.status == TaskStatus.COMPLETED)
        
        return {
            'schedule_id': schedule_id,
            'name': schedule.name,
            'total_tasks': len(tasks),
            'completed_tasks': completed,
            'progress': (completed / len(tasks) * 100) if tasks else 0,
            'start_date': schedule.start_date.isoformat(),
            'end_date': schedule.end_date.isoformat() if schedule.end_date else None
        }


class PlanningManager:
    """Менеджер планирования"""
    
    def __init__(self):
        """Инициализация"""
        self.task_manager = TaskManager()
        self.schedule_manager = ScheduleManager(self.task_manager)
        self.logger = logging.getLogger('daur_ai.planning_manager')
    
    def get_status(self) -> Dict[str, Any]:
        """Получить статус менеджера"""
        return {
            'tasks': self.task_manager.get_status(),
            'schedules': len(self.schedule_manager.schedules)
        }


# Глобальные экземпляры
_task_manager = None
_schedule_manager = None
_planning_manager = None


def get_task_manager() -> TaskManager:
    """Получить менеджер задач"""
    global _task_manager
    if _task_manager is None:
        _task_manager = TaskManager()
    return _task_manager


def get_schedule_manager() -> ScheduleManager:
    """Получить менеджер графиков"""
    global _schedule_manager
    if _schedule_manager is None:
        _schedule_manager = ScheduleManager(get_task_manager())
    return _schedule_manager


def get_planning_manager() -> PlanningManager:
    """Получить менеджер планирования"""
    global _planning_manager
    if _planning_manager is None:
        _planning_manager = PlanningManager()
    return _planning_manager

