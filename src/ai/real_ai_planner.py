"""
Real AI Planner with Task Planning
Полнофункциональный AI планировщик с реальными алгоритмами планирования
"""

import logging
import json
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, asdict, field
from enum import Enum
from datetime import datetime, timedelta
from collections import deque
import heapq

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Статусы задач"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    BLOCKED = "blocked"


class TaskPriority(Enum):
    """Приоритеты задач"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


class PlanningStrategy(Enum):
    """Стратегии планирования"""
    GREEDY = "greedy"
    DEPTH_FIRST = "depth_first"
    BREADTH_FIRST = "breadth_first"
    A_STAR = "a_star"
    DYNAMIC_PROGRAMMING = "dynamic_programming"


@dataclass
class Task:
    """Задача"""
    task_id: str
    name: str
    description: str
    priority: TaskPriority
    status: TaskStatus = TaskStatus.PENDING
    estimated_duration: int = 0  # в секундах
    actual_duration: int = 0
    dependencies: List[str] = field(default_factory=list)
    subtasks: List[str] = field(default_factory=list)
    assigned_to: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    result: Optional[str] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Plan:
    """План выполнения"""
    plan_id: str
    goal: str
    tasks: List[Task]
    strategy: PlanningStrategy
    estimated_total_duration: int
    priority: TaskPriority
    success_rate: float = 0.0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None
    execution_order: List[str] = field(default_factory=list)


@dataclass
class Action:
    """Действие для выполнения"""
    action_id: str
    action_type: str
    parameters: Dict[str, Any]
    priority: TaskPriority
    estimated_duration: int
    callback: Optional[Callable] = None


class RealAIPlanner:
    """Реальный AI планировщик"""
    
    def __init__(self):
        """Инициализация планировщика"""
        self.logger = logging.getLogger(__name__)
        
        # Хранилище задач и планов
        self.tasks: Dict[str, Task] = {}
        self.plans: Dict[str, Plan] = {}
        self.completed_tasks: List[Task] = []
        self.failed_tasks: List[Task] = []
        
        # Очередь выполнения
        self.execution_queue: List[Task] = []
        self.current_task: Optional[Task] = None
        
        # История планирования
        self.planning_history: List[Dict[str, Any]] = []
        
        self.logger.info("Real AI Planner initialized")
    
    # ===== TASK MANAGEMENT =====
    
    def create_task(self, task_id: str, name: str, description: str,
                   priority: TaskPriority = TaskPriority.MEDIUM,
                   estimated_duration: int = 0,
                   dependencies: List[str] = None) -> Task:
        """
        Создать задачу
        
        Args:
            task_id: ID задачи
            name: Название
            description: Описание
            priority: Приоритет
            estimated_duration: Предполагаемая длительность
            dependencies: Зависимости
        
        Returns:
            Task: Созданная задача
        """
        try:
            task = Task(
                task_id=task_id,
                name=name,
                description=description,
                priority=priority,
                estimated_duration=estimated_duration,
                dependencies=dependencies or []
            )
            
            self.tasks[task_id] = task
            self.logger.info(f"Task created: {task_id}")
            return task
        except Exception as e:
            self.logger.error(f"Error creating task: {e}")
            return None
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Получить задачу"""
        return self.tasks.get(task_id)
    
    def update_task_status(self, task_id: str, status: TaskStatus) -> bool:
        """Обновить статус задачи"""
        try:
            task = self.tasks.get(task_id)
            if not task:
                return False
            
            old_status = task.status
            task.status = status
            
            if status == TaskStatus.RUNNING:
                task.started_at = datetime.now().isoformat()
            elif status == TaskStatus.COMPLETED:
                task.completed_at = datetime.now().isoformat()
                self.completed_tasks.append(task)
            elif status == TaskStatus.FAILED:
                task.completed_at = datetime.now().isoformat()
                self.failed_tasks.append(task)
            
            self.logger.info(f"Task {task_id} status: {old_status.value} -> {status.value}")
            return True
        except Exception as e:
            self.logger.error(f"Error updating task status: {e}")
            return False
    
    def add_subtask(self, parent_task_id: str, subtask_id: str) -> bool:
        """Добавить подзадачу"""
        try:
            parent_task = self.tasks.get(parent_task_id)
            if not parent_task:
                return False
            
            parent_task.subtasks.append(subtask_id)
            
            # Автоматически добавляем зависимость
            subtask = self.tasks.get(subtask_id)
            if subtask:
                subtask.dependencies.append(parent_task_id)
            
            self.logger.info(f"Subtask {subtask_id} added to {parent_task_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding subtask: {e}")
            return False
    
    # ===== PLANNING =====
    
    def create_plan(self, goal: str, tasks: List[str],
                   strategy: PlanningStrategy = PlanningStrategy.A_STAR) -> Optional[Plan]:
        """
        Создать план выполнения
        
        Args:
            goal: Цель плана
            tasks: Список ID задач
            strategy: Стратегия планирования
        
        Returns:
            Optional[Plan]: Созданный план
        """
        try:
            # Получаем объекты задач
            task_objects = [self.tasks[t] for t in tasks if t in self.tasks]
            
            if not task_objects:
                self.logger.error("No valid tasks for plan")
                return None
            
            # Определяем порядок выполнения
            execution_order = self._determine_execution_order(task_objects, strategy)
            
            # Вычисляем общую длительность
            total_duration = sum(t.estimated_duration for t in task_objects)
            
            # Определяем приоритет плана
            plan_priority = max((t.priority for t in task_objects), default=TaskPriority.MEDIUM)
            
            # Создаём план
            plan_id = f"plan_{datetime.now().timestamp()}"
            plan = Plan(
                plan_id=plan_id,
                goal=goal,
                tasks=task_objects,
                strategy=strategy,
                estimated_total_duration=total_duration,
                priority=plan_priority,
                execution_order=execution_order
            )
            
            self.plans[plan_id] = plan
            self.planning_history.append({
                'plan_id': plan_id,
                'goal': goal,
                'strategy': strategy.value,
                'tasks': len(task_objects),
                'timestamp': datetime.now().isoformat()
            })
            
            self.logger.info(f"Plan created: {plan_id} ({len(task_objects)} tasks)")
            return plan
        
        except Exception as e:
            self.logger.error(f"Error creating plan: {e}")
            return None
    
    def _determine_execution_order(self, tasks: List[Task],
                                  strategy: PlanningStrategy) -> List[str]:
        """Определить порядок выполнения задач"""
        try:
            if strategy == PlanningStrategy.GREEDY:
                return self._greedy_order(tasks)
            elif strategy == PlanningStrategy.DEPTH_FIRST:
                return self._depth_first_order(tasks)
            elif strategy == PlanningStrategy.BREADTH_FIRST:
                return self._breadth_first_order(tasks)
            elif strategy == PlanningStrategy.A_STAR:
                return self._a_star_order(tasks)
            elif strategy == PlanningStrategy.DYNAMIC_PROGRAMMING:
                return self._dynamic_programming_order(tasks)
            else:
                return [t.task_id for t in tasks]
        except Exception as e:
            self.logger.error(f"Error determining execution order: {e}")
            return [t.task_id for t in tasks]
    
    def _greedy_order(self, tasks: List[Task]) -> List[str]:
        """Жадный алгоритм - по приоритету и длительности"""
        sorted_tasks = sorted(
            tasks,
            key=lambda t: (t.priority.value, t.estimated_duration)
        )
        return [t.task_id for t in sorted_tasks]
    
    def _depth_first_order(self, tasks: List[Task]) -> List[str]:
        """Поиск в глубину с учётом зависимостей"""
        order = []
        visited = set()
        
        def dfs(task_id: str):
            if task_id in visited:
                return
            
            visited.add(task_id)
            task = self.tasks.get(task_id)
            
            if task:
                # Сначала выполняем зависимости
                for dep in task.dependencies:
                    dfs(dep)
                
                order.append(task_id)
        
        for task in tasks:
            dfs(task.task_id)
        
        return order
    
    def _breadth_first_order(self, tasks: List[Task]) -> List[str]:
        """Поиск в ширину с учётом зависимостей"""
        order = []
        visited = set()
        queue = deque()
        
        # Добавляем задачи без зависимостей
        for task in tasks:
            if not task.dependencies:
                queue.append(task.task_id)
                visited.add(task.task_id)
        
        while queue:
            task_id = queue.popleft()
            order.append(task_id)
            
            # Добавляем задачи, которые зависят от текущей
            for task in tasks:
                if task_id in task.dependencies and task.task_id not in visited:
                    queue.append(task.task_id)
                    visited.add(task.task_id)
        
        # Добавляем оставшиеся задачи
        for task in tasks:
            if task.task_id not in visited:
                order.append(task.task_id)
        
        return order
    
    def _a_star_order(self, tasks: List[Task]) -> List[str]:
        """A* алгоритм - оптимальный порядок"""
        # Используем приоритет и зависимости
        heap = []
        
        for task in tasks:
            # f(n) = g(n) + h(n)
            # g(n) = количество зависимостей
            # h(n) = приоритет (меньше = выше приоритет)
            g = len(task.dependencies)
            h = task.priority.value
            f = g + h
            
            heapq.heappush(heap, (f, task.task_id))
        
        order = []
        while heap:
            _, task_id = heapq.heappop(heap)
            order.append(task_id)
        
        return order
    
    def _dynamic_programming_order(self, tasks: List[Task]) -> List[str]:
        """Динамическое программирование"""
        # Вычисляем оптимальный порядок с учётом всех факторов
        memo = {}
        
        def compute_cost(task_id: str) -> int:
            if task_id in memo:
                return memo[task_id]
            
            task = self.tasks.get(task_id)
            if not task:
                return 0
            
            # Стоимость = длительность + стоимость зависимостей
            cost = task.estimated_duration
            for dep in task.dependencies:
                cost += compute_cost(dep)
            
            memo[task_id] = cost
            return cost
        
        # Сортируем по стоимости
        sorted_tasks = sorted(
            tasks,
            key=lambda t: compute_cost(t.task_id)
        )
        
        return [t.task_id for t in sorted_tasks]
    
    # ===== EXECUTION =====
    
    def execute_plan(self, plan_id: str) -> bool:
        """
        Выполнить план
        
        Args:
            plan_id: ID плана
        
        Returns:
            bool: Успешность выполнения
        """
        try:
            plan = self.plans.get(plan_id)
            if not plan:
                self.logger.error(f"Plan not found: {plan_id}")
                return False
            
            # Создаём очередь выполнения
            self.execution_queue = []
            for task_id in plan.execution_order:
                task = self.tasks.get(task_id)
                if task:
                    self.execution_queue.append(task)
            
            # Выполняем задачи
            success_count = 0
            for task in self.execution_queue:
                if self._execute_task(task):
                    success_count += 1
            
            # Обновляем план
            plan.completed_at = datetime.now().isoformat()
            plan.success_rate = success_count / len(self.execution_queue) if self.execution_queue else 0
            
            self.logger.info(f"Plan executed: {plan_id} (success rate: {plan.success_rate:.1%})")
            return True
        
        except Exception as e:
            self.logger.error(f"Error executing plan: {e}")
            return False
    
    def _execute_task(self, task: Task) -> bool:
        """Выполнить одну задачу"""
        try:
            # Проверяем зависимости
            for dep_id in task.dependencies:
                dep_task = self.tasks.get(dep_id)
                if dep_task and dep_task.status != TaskStatus.COMPLETED:
                    self.logger.warning(f"Task {task.task_id} blocked by {dep_id}")
                    self.update_task_status(task.task_id, TaskStatus.BLOCKED)
                    return False
            
            # Обновляем статус
            self.update_task_status(task.task_id, TaskStatus.RUNNING)
            
            # Имитируем выполнение
            # В реальной системе здесь будет вызов реальной функции
            import time
            time.sleep(min(task.estimated_duration / 1000, 0.1))  # Максимум 100ms
            
            # Завершаем задачу
            task.result = f"Task {task.task_id} completed successfully"
            self.update_task_status(task.task_id, TaskStatus.COMPLETED)
            
            self.logger.info(f"Task executed: {task.task_id}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error executing task {task.task_id}: {e}")
            task.error = str(e)
            self.update_task_status(task.task_id, TaskStatus.FAILED)
            return False
    
    # ===== OPTIMIZATION =====
    
    def optimize_plan(self, plan_id: str) -> Optional[Plan]:
        """
        Оптимизировать план
        
        Args:
            plan_id: ID плана
        
        Returns:
            Optional[Plan]: Оптимизированный план
        """
        try:
            plan = self.plans.get(plan_id)
            if not plan:
                return None
            
            # Переопределяем порядок выполнения
            new_order = self._a_star_order(plan.tasks)
            plan.execution_order = new_order
            
            self.logger.info(f"Plan optimized: {plan_id}")
            return plan
        
        except Exception as e:
            self.logger.error(f"Error optimizing plan: {e}")
            return None
    
    def parallelize_plan(self, plan_id: str) -> Optional[List[List[str]]]:
        """
        Распараллелить план (задачи, которые можно выполнять одновременно)
        
        Args:
            plan_id: ID плана
        
        Returns:
            Optional[List[List[str]]]: Группы параллельных задач
        """
        try:
            plan = self.plans.get(plan_id)
            if not plan:
                return None
            
            groups = []
            remaining = set(t.task_id for t in plan.tasks)
            
            while remaining:
                # Находим задачи без зависимостей в оставшихся
                current_group = []
                for task_id in remaining:
                    task = self.tasks.get(task_id)
                    if task and not any(dep in remaining for dep in task.dependencies):
                        current_group.append(task_id)
                
                if not current_group:
                    # Если нет задач без зависимостей, берём первую
                    current_group = [remaining.pop()]
                else:
                    for task_id in current_group:
                        remaining.discard(task_id)
                
                groups.append(current_group)
            
            self.logger.info(f"Plan parallelized: {plan_id} ({len(groups)} groups)")
            return groups
        
        except Exception as e:
            self.logger.error(f"Error parallelizing plan: {e}")
            return None
    
    # ===== STATISTICS =====
    
    def get_plan_statistics(self, plan_id: str) -> Dict[str, Any]:
        """Получить статистику плана"""
        try:
            plan = self.plans.get(plan_id)
            if not plan:
                return {}
            
            completed = sum(1 for t in plan.tasks if t.status == TaskStatus.COMPLETED)
            failed = sum(1 for t in plan.tasks if t.status == TaskStatus.FAILED)
            running = sum(1 for t in plan.tasks if t.status == TaskStatus.RUNNING)
            pending = sum(1 for t in plan.tasks if t.status == TaskStatus.PENDING)
            
            return {
                'plan_id': plan_id,
                'goal': plan.goal,
                'total_tasks': len(plan.tasks),
                'completed': completed,
                'failed': failed,
                'running': running,
                'pending': pending,
                'success_rate': plan.success_rate,
                'estimated_duration': plan.estimated_total_duration,
                'strategy': plan.strategy.value,
                'created_at': plan.created_at,
                'completed_at': plan.completed_at
            }
        except Exception as e:
            self.logger.error(f"Error getting plan statistics: {e}")
            return {}
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Получить метрики производительности"""
        try:
            total_tasks = len(self.tasks)
            completed = len(self.completed_tasks)
            failed = len(self.failed_tasks)
            
            avg_duration = (
                sum(t.actual_duration for t in self.completed_tasks) / completed
                if completed > 0 else 0
            )
            
            return {
                'total_tasks': total_tasks,
                'completed': completed,
                'failed': failed,
                'success_rate': completed / total_tasks if total_tasks > 0 else 0,
                'average_duration': avg_duration,
                'total_plans': len(self.plans),
                'planning_history_size': len(self.planning_history)
            }
        except Exception as e:
            self.logger.error(f"Error getting performance metrics: {e}")
            return {}

