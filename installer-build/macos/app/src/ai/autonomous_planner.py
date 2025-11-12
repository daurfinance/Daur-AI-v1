"""
Автономный AI планировщик
Планирование, выполнение и самообучение агента
"""

import asyncio
import time
import logging
import json
import uuid
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import traceback

# Импорт компонентов системы
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

try:
    from .enhanced_model_manager import EnhancedModelManager
    from .multimodal_manager import MultimodalAIManager
except ImportError:
    EnhancedModelManager = None
    MultimodalAIManager = None

class TaskStatus(Enum):
    """Статусы задач"""
    PENDING = "pending"
    PLANNING = "planning"
    EXECUTING = "executing"
    DEBUGGING = "debugging"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class StepStatus(Enum):
    """Статусы шагов"""
    PENDING = "pending"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class TaskStep:
    """Шаг выполнения задачи"""
    id: str
    description: str
    action_type: str  # 'system', 'browser', 'file', 'input', 'analysis'
    parameters: Dict[str, Any]
    dependencies: List[str]  # ID шагов-зависимостей
    status: StepStatus = StepStatus.PENDING
    result: Optional[Dict] = None
    error: Optional[str] = None
    execution_time: float = 0.0
    retry_count: int = 0
    max_retries: int = 3

@dataclass
class Task:
    """Задача для выполнения"""
    id: str
    description: str
    user_input: str
    priority: int = 1  # 1-5, где 5 - высший приоритет
    status: TaskStatus = TaskStatus.PENDING
    steps: List[TaskStep] = None
    result: Optional[Dict] = None
    error: Optional[str] = None
    created_at: float = 0.0
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    feedback: Optional[Dict] = None
    learning_data: Optional[Dict] = None

class AutonomousPlanner:
    """Автономный планировщик AI агента"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # AI компоненты
        self.ai_manager = EnhancedModelManager() if EnhancedModelManager else None
        self.multimodal_manager = MultimodalAIManager() if MultimodalAIManager else None
        
        # Очереди задач
        self.task_queue = []
        self.active_tasks = {}
        self.completed_tasks = {}
        
        # Исполнители действий
        self.action_executors = {}
        
        # База знаний и опыт
        self.knowledge_base = {
            'successful_patterns': [],
            'failed_patterns': [],
            'optimization_rules': [],
            'device_capabilities': {},
            'user_preferences': {}
        }
        
        # Статистика
        self.stats = {
            'tasks_completed': 0,
            'tasks_failed': 0,
            'steps_executed': 0,
            'learning_iterations': 0,
            'success_rate': 0.0
        }
        
        # Настройки
        self.max_concurrent_tasks = 3
        self.max_planning_iterations = 5
        self.feedback_learning_enabled = True
        
        # Инициализация
        self._initialize()
    
    def _initialize(self):
        """Инициализация планировщика"""
        try:
            # Регистрация исполнителей действий
            self._register_action_executors()
            
            # Загрузка базы знаний
            self._load_knowledge_base()
            
            self.logger.info("Автономный планировщик инициализирован")
            
        except Exception as e:
            self.logger.error(f"Ошибка инициализации планировщика: {e}")
    
    def _register_action_executors(self):
        """Регистрирует исполнителей действий"""
        try:
            # Системные действия
            self.action_executors['system'] = self._execute_system_action
            
            # Браузерные действия
            self.action_executors['browser'] = self._execute_browser_action
            
            # Файловые операции
            self.action_executors['file'] = self._execute_file_action
            
            # Ввод и управление
            self.action_executors['input'] = self._execute_input_action
            
            # Анализ и обработка
            self.action_executors['analysis'] = self._execute_analysis_action
            
            # Мультимедиа операции
            self.action_executors['media'] = self._execute_media_action
            
            self.logger.info(f"Зарегистрировано {len(self.action_executors)} исполнителей действий")
            
        except Exception as e:
            self.logger.error(f"Ошибка регистрации исполнителей: {e}")
    
    async def create_task(self, user_input: str, priority: int = 1) -> str:
        """
        Создает новую задачу
        
        Args:
            user_input: Пользовательский ввод
            priority: Приоритет задачи (1-5)
            
        Returns:
            ID созданной задачи
        """
        try:
            task_id = str(uuid.uuid4())
            
            # Анализ пользовательского ввода
            description = await self._analyze_user_input(user_input)
            
            # Создание задачи
            task = Task(
                id=task_id,
                description=description,
                user_input=user_input,
                priority=priority,
                created_at=time.time(),
                steps=[]
            )
            
            # Добавление в очередь
            self.task_queue.append(task)
            
            # Сортировка по приоритету
            self.task_queue.sort(key=lambda t: t.priority, reverse=True)
            
            self.logger.info(f"Создана задача {task_id}: {description}")
            
            return task_id
            
        except Exception as e:
            self.logger.error(f"Ошибка создания задачи: {e}")
            return ""
    
    async def _analyze_user_input(self, user_input: str) -> str:
        """Анализирует пользовательский ввод"""
        try:
            if self.ai_manager:
                analysis_prompt = f"""
                Проанализируй пользовательский запрос и создай краткое описание задачи:
                
                Запрос: "{user_input}"
                
                Верни только краткое описание задачи (1-2 предложения).
                """
                
                response = await asyncio.to_thread(self.ai_manager.generate_response, analysis_prompt)
                return response if response else user_input
            
            return user_input
            
        except Exception as e:
            self.logger.error(f"Ошибка анализа ввода: {e}")
            return user_input
    
    async def plan_task(self, task_id: str) -> bool:
        """
        Создает план выполнения задачи
        
        Args:
            task_id: ID задачи
            
        Returns:
            Успешность планирования
        """
        try:
            task = self._get_task(task_id)
            if not task:
                return False
            
            task.status = TaskStatus.PLANNING
            task.started_at = time.time()
            
            self.logger.info(f"Начало планирования задачи {task_id}")
            
            # Создание плана с помощью AI
            plan = await self._create_execution_plan(task)
            
            if plan:
                task.steps = plan
                task.status = TaskStatus.PENDING
                
                self.logger.info(f"План для задачи {task_id} создан: {len(plan)} шагов")
                return True
            
            else:
                task.status = TaskStatus.FAILED
                task.error = "Не удалось создать план выполнения"
                return False
            
        except Exception as e:
            self.logger.error(f"Ошибка планирования задачи {task_id}: {e}")
            task = self._get_task(task_id)
            if task:
                task.status = TaskStatus.FAILED
                task.error = str(e)
            return False
    
    async def _create_execution_plan(self, task: Task) -> List[TaskStep]:
        """Создает план выполнения задачи"""
        try:
            if not self.ai_manager:
                return self._create_fallback_plan(task)
            
            # Анализ задачи и создание плана
            planning_prompt = f"""
            Создай детальный план выполнения задачи:
            
            Задача: {task.description}
            Пользовательский ввод: {task.user_input}
            
            Доступные типы действий:
            - system: системные операции (запуск программ, управление процессами)
            - browser: браузерные операции (навигация, клики, ввод текста)
            - file: файловые операции (создание, чтение, запись файлов)
            - input: управление вводом (мышь, клавиатура, скриншоты)
            - analysis: анализ данных (OCR, распознавание изображений)
            - media: мультимедиа операции (обработка изображений, видео, аудио)
            
            Верни план в формате JSON:
            {{
                "steps": [
                    {{
                        "id": "step_1",
                        "description": "Описание шага",
                        "action_type": "system|browser|file|input|analysis|media",
                        "parameters": {{"param1": "value1"}},
                        "dependencies": []
                    }}
                ]
            }}
            
            Создай логичную последовательность шагов для выполнения задачи.
            """
            
            response = await asyncio.to_thread(self.ai_manager.generate_response, planning_prompt)
            
            if response:
                # Парсинг JSON ответа
                plan_data = self._parse_plan_response(response)
                
                if plan_data:
                    steps = []
                    for step_data in plan_data.get('steps', []):
                        step = TaskStep(
                            id=step_data.get('id', f"step_{len(steps)+1}"),
                            description=step_data.get('description', ''),
                            action_type=step_data.get('action_type', 'system'),
                            parameters=step_data.get('parameters', {}),
                            dependencies=step_data.get('dependencies', [])
                        )
                        steps.append(step)
                    
                    return steps
            
            # Fallback план
            return self._create_fallback_plan(task)
            
        except Exception as e:
            self.logger.error(f"Ошибка создания плана: {e}")
            return self._create_fallback_plan(task)
    
    def _parse_plan_response(self, response: str) -> Optional[Dict]:
        """Парсит ответ AI с планом"""
        try:
            # Поиск JSON в ответе
            import re
            
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                return json.loads(json_str)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Ошибка парсинга плана: {e}")
            return None
    
    def _create_fallback_plan(self, task: Task) -> List[TaskStep]:
        """Создает базовый план выполнения"""
        try:
            # Простой план на основе ключевых слов
            user_input = task.user_input.lower()
            steps = []
            
            if 'файл' in user_input or 'создай' in user_input:
                steps.append(TaskStep(
                    id="step_1",
                    description="Создание файла",
                    action_type="file",
                    parameters={"action": "create", "content": task.user_input},
                    dependencies=[]
                ))
            
            elif 'браузер' in user_input or 'сайт' in user_input:
                steps.append(TaskStep(
                    id="step_1",
                    description="Открытие браузера",
                    action_type="browser",
                    parameters={"action": "navigate", "url": "https://google.com"},
                    dependencies=[]
                ))
            
            elif 'скриншот' in user_input:
                steps.append(TaskStep(
                    id="step_1",
                    description="Создание скриншота",
                    action_type="input",
                    parameters={"action": "screenshot"},
                    dependencies=[]
                ))
            
            else:
                # Общий системный шаг
                steps.append(TaskStep(
                    id="step_1",
                    description="Выполнение системной команды",
                    action_type="system",
                    parameters={"command": task.user_input},
                    dependencies=[]
                ))
            
            return steps
            
        except Exception as e:
            self.logger.error(f"Ошибка создания fallback плана: {e}")
            return []
    
    async def execute_task(self, task_id: str) -> bool:
        """
        Выполняет задачу
        
        Args:
            task_id: ID задачи
            
        Returns:
            Успешность выполнения
        """
        try:
            task = self._get_task(task_id)
            if not task or not task.steps:
                return False
            
            task.status = TaskStatus.EXECUTING
            self.active_tasks[task_id] = task
            
            self.logger.info(f"Начало выполнения задачи {task_id}")
            
            # Выполнение шагов
            success = await self._execute_steps(task)
            
            if success:
                task.status = TaskStatus.COMPLETED
                task.completed_at = time.time()
                self.stats['tasks_completed'] += 1
                
                # Обучение на успешном выполнении
                await self._learn_from_success(task)
                
            else:
                task.status = TaskStatus.FAILED
                self.stats['tasks_failed'] += 1
                
                # Попытка отладки и исправления
                if await self._debug_and_retry(task):
                    task.status = TaskStatus.COMPLETED
                    task.completed_at = time.time()
                    self.stats['tasks_completed'] += 1
                else:
                    # Обучение на неудаче
                    await self._learn_from_failure(task)
            
            # Перемещение в завершенные задачи
            self.completed_tasks[task_id] = task
            if task_id in self.active_tasks:
                del self.active_tasks[task_id]
            
            # Обновление статистики
            self._update_success_rate()
            
            return task.status == TaskStatus.COMPLETED
            
        except Exception as e:
            self.logger.error(f"Ошибка выполнения задачи {task_id}: {e}")
            task = self._get_task(task_id)
            if task:
                task.status = TaskStatus.FAILED
                task.error = str(e)
            return False
    
    async def _execute_steps(self, task: Task) -> bool:
        """Выполняет шаги задачи"""
        try:
            # Создание графа зависимостей
            dependency_graph = self._build_dependency_graph(task.steps)
            
            # Выполнение шагов в правильном порядке
            executed_steps = set()
            
            while len(executed_steps) < len(task.steps):
                # Поиск шагов, готовых к выполнению
                ready_steps = []
                
                for step in task.steps:
                    if (step.id not in executed_steps and 
                        step.status == StepStatus.PENDING and
                        all(dep in executed_steps for dep in step.dependencies)):
                        ready_steps.append(step)
                
                if not ready_steps:
                    # Нет готовых шагов - возможно циклическая зависимость
                    self.logger.error("Обнаружена циклическая зависимость или заблокированные шаги")
                    return False
                
                # Выполнение готовых шагов
                for step in ready_steps:
                    success = await self._execute_step(step)
                    executed_steps.add(step.id)
                    
                    if not success and step.retry_count >= step.max_retries:
                        self.logger.error(f"Шаг {step.id} не удалось выполнить после {step.max_retries} попыток")
                        return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка выполнения шагов: {e}")
            return False
    
    def _build_dependency_graph(self, steps: List[TaskStep]) -> Dict:
        """Строит граф зависимостей шагов"""
        try:
            graph = {}
            
            for step in steps:
                graph[step.id] = {
                    'step': step,
                    'dependencies': step.dependencies,
                    'dependents': []
                }
            
            # Построение обратных связей
            for step_id, node in graph.items():
                for dep_id in node['dependencies']:
                    if dep_id in graph:
                        graph[dep_id]['dependents'].append(step_id)
            
            return graph
            
        except Exception as e:
            self.logger.error(f"Ошибка построения графа зависимостей: {e}")
            return {}
    
    async def _execute_step(self, step: TaskStep) -> bool:
        """Выполняет отдельный шаг"""
        try:
            step.status = StepStatus.EXECUTING
            start_time = time.time()
            
            self.logger.info(f"Выполнение шага {step.id}: {step.description}")
            
            # Получение исполнителя
            executor = self.action_executors.get(step.action_type)
            
            if not executor:
                step.status = StepStatus.FAILED
                step.error = f"Неизвестный тип действия: {step.action_type}"
                return False
            
            # Выполнение действия
            result = await executor(step.parameters)
            
            step.execution_time = time.time() - start_time
            self.stats['steps_executed'] += 1
            
            if result and result.get('success', False):
                step.status = StepStatus.COMPLETED
                step.result = result
                
                self.logger.info(f"Шаг {step.id} выполнен успешно за {step.execution_time:.2f}с")
                return True
            
            else:
                step.status = StepStatus.FAILED
                step.error = result.get('error', 'Неизвестная ошибка') if result else 'Нет результата'
                step.retry_count += 1
                
                self.logger.warning(f"Шаг {step.id} не выполнен: {step.error}")
                
                # Повторная попытка если возможно
                if step.retry_count < step.max_retries:
                    await asyncio.sleep(1)  # Пауза перед повтором
                    step.status = StepStatus.PENDING
                    return await self._execute_step(step)
                
                return False
            
        except Exception as e:
            step.status = StepStatus.FAILED
            step.error = str(e)
            step.execution_time = time.time() - start_time
            
            self.logger.error(f"Ошибка выполнения шага {step.id}: {e}")
            return False
    
    # Исполнители действий
    async def _execute_system_action(self, parameters: Dict) -> Dict:
        """Выполняет системное действие"""
        try:
            action = parameters.get('action', 'command')
            
            if action == 'command':
                command = parameters.get('command', '')
                # Здесь должна быть интеграция с системным контроллером
                return {'success': True, 'output': f'Выполнена команда: {command}'}
            
            return {'success': False, 'error': f'Неизвестное системное действие: {action}'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _execute_browser_action(self, parameters: Dict) -> Dict:
        """Выполняет браузерное действие"""
        try:
            action = parameters.get('action', 'navigate')
            
            if action == 'navigate':
                url = parameters.get('url', 'https://google.com')
                # Здесь должна быть интеграция с браузерным контроллером
                return {'success': True, 'url': url}
            
            return {'success': False, 'error': f'Неизвестное браузерное действие: {action}'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _execute_file_action(self, parameters: Dict) -> Dict:
        """Выполняет файловое действие"""
        try:
            action = parameters.get('action', 'create')
            
            if action == 'create':
                filename = parameters.get('filename', 'test.txt')
                content = parameters.get('content', 'Hello World')
                
                # Создание файла
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                return {'success': True, 'filename': filename, 'size': len(content)}
            
            return {'success': False, 'error': f'Неизвестное файловое действие: {action}'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _execute_input_action(self, parameters: Dict) -> Dict:
        """Выполняет действие ввода"""
        try:
            action = parameters.get('action', 'screenshot')
            
            if action == 'screenshot':
                # Здесь должна быть интеграция с контроллером ввода
                return {'success': True, 'screenshot': 'screenshot_taken'}
            
            return {'success': False, 'error': f'Неизвестное действие ввода: {action}'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _execute_analysis_action(self, parameters: Dict) -> Dict:
        """Выполняет действие анализа"""
        try:
            action = parameters.get('action', 'ocr')
            
            if action == 'ocr':
                # Здесь должна быть интеграция с OCR движком
                return {'success': True, 'text': 'Распознанный текст'}
            
            return {'success': False, 'error': f'Неизвестное действие анализа: {action}'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _execute_media_action(self, parameters: Dict) -> Dict:
        """Выполняет мультимедийное действие"""
        try:
            action = parameters.get('action', 'analyze_image')
            
            if action == 'analyze_image':
                # Здесь должна быть интеграция с мультимодальным менеджером
                return {'success': True, 'analysis': 'Анализ изображения'}
            
            return {'success': False, 'error': f'Неизвестное мультимедийное действие: {action}'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _debug_and_retry(self, task: Task) -> bool:
        """Отладка и повторная попытка выполнения"""
        try:
            task.status = TaskStatus.DEBUGGING
            
            self.logger.info(f"Начало отладки задачи {task.id}")
            
            # Анализ ошибок
            failed_steps = [step for step in task.steps if step.status == StepStatus.FAILED]
            
            if not failed_steps:
                return True
            
            # Попытка исправления ошибок с помощью AI
            if self.ai_manager:
                for step in failed_steps:
                    fix_result = await self._fix_step_with_ai(step, task)
                    
                    if fix_result:
                        # Повторная попытка выполнения
                        step.status = StepStatus.PENDING
                        step.retry_count = 0
                        
                        success = await self._execute_step(step)
                        if not success:
                            return False
            
            return all(step.status == StepStatus.COMPLETED for step in task.steps)
            
        except Exception as e:
            self.logger.error(f"Ошибка отладки задачи {task.id}: {e}")
            return False
    
    async def _fix_step_with_ai(self, step: TaskStep, task: Task) -> bool:
        """Исправляет шаг с помощью AI"""
        try:
            if not self.ai_manager:
                return False
            
            fix_prompt = f"""
            Исправь ошибку в шаге выполнения задачи:
            
            Задача: {task.description}
            Шаг: {step.description}
            Тип действия: {step.action_type}
            Параметры: {json.dumps(step.parameters, ensure_ascii=False)}
            Ошибка: {step.error}
            
            Предложи исправленные параметры в формате JSON:
            {{"parameters": {{"param1": "new_value"}}}}
            """
            
            response = await asyncio.to_thread(self.ai_manager.generate_response, fix_prompt)
            
            if response:
                # Парсинг исправлений
                fix_data = self._parse_plan_response(response)
                
                if fix_data and 'parameters' in fix_data:
                    step.parameters.update(fix_data['parameters'])
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Ошибка исправления шага: {e}")
            return False
    
    async def _learn_from_success(self, task: Task):
        """Обучение на успешном выполнении"""
        try:
            if not self.feedback_learning_enabled:
                return
            
            # Сохранение успешного паттерна
            pattern = {
                'task_type': task.description,
                'user_input': task.user_input,
                'steps': [asdict(step) for step in task.steps],
                'execution_time': task.completed_at - task.started_at,
                'success': True,
                'timestamp': time.time()
            }
            
            self.knowledge_base['successful_patterns'].append(pattern)
            
            # Ограничение размера базы знаний
            if len(self.knowledge_base['successful_patterns']) > 1000:
                self.knowledge_base['successful_patterns'] = \
                    self.knowledge_base['successful_patterns'][-1000:]
            
            self.stats['learning_iterations'] += 1
            
            self.logger.info(f"Сохранен успешный паттерн для задачи {task.id}")
            
        except Exception as e:
            self.logger.error(f"Ошибка обучения на успехе: {e}")
    
    async def _learn_from_failure(self, task: Task):
        """Обучение на неудаче"""
        try:
            if not self.feedback_learning_enabled:
                return
            
            # Сохранение неудачного паттерна
            pattern = {
                'task_type': task.description,
                'user_input': task.user_input,
                'steps': [asdict(step) for step in task.steps],
                'error': task.error,
                'failed_steps': [asdict(step) for step in task.steps if step.status == StepStatus.FAILED],
                'success': False,
                'timestamp': time.time()
            }
            
            self.knowledge_base['failed_patterns'].append(pattern)
            
            # Ограничение размера базы знаний
            if len(self.knowledge_base['failed_patterns']) > 500:
                self.knowledge_base['failed_patterns'] = \
                    self.knowledge_base['failed_patterns'][-500:]
            
            self.stats['learning_iterations'] += 1
            
            self.logger.info(f"Сохранен неудачный паттерн для задачи {task.id}")
            
        except Exception as e:
            self.logger.error(f"Ошибка обучения на неудаче: {e}")
    
    def _update_success_rate(self):
        """Обновляет статистику успешности"""
        total_tasks = self.stats['tasks_completed'] + self.stats['tasks_failed']
        if total_tasks > 0:
            self.stats['success_rate'] = self.stats['tasks_completed'] / total_tasks
    
    def _get_task(self, task_id: str) -> Optional[Task]:
        """Получает задачу по ID"""
        # Поиск в активных задачах
        if task_id in self.active_tasks:
            return self.active_tasks[task_id]
        
        # Поиск в завершенных задачах
        if task_id in self.completed_tasks:
            return self.completed_tasks[task_id]
        
        # Поиск в очереди
        for task in self.task_queue:
            if task.id == task_id:
                return task
        
        return None
    
    def _load_knowledge_base(self):
        """Загружает базу знаний"""
        try:
            # Здесь можно загрузить сохраненную базу знаний
            # Пока используем пустую базу
            pass
            
        except Exception as e:
            self.logger.error(f"Ошибка загрузки базы знаний: {e}")
    
    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """Возвращает статус задачи"""
        task = self._get_task(task_id)
        if not task:
            return None
        
        return {
            'id': task.id,
            'description': task.description,
            'status': task.status.value,
            'progress': self._calculate_task_progress(task),
            'steps_total': len(task.steps) if task.steps else 0,
            'steps_completed': len([s for s in task.steps if s.status == StepStatus.COMPLETED]) if task.steps else 0,
            'created_at': task.created_at,
            'started_at': task.started_at,
            'completed_at': task.completed_at,
            'error': task.error
        }
    
    def _calculate_task_progress(self, task: Task) -> float:
        """Вычисляет прогресс выполнения задачи"""
        if not task.steps:
            return 0.0
        
        completed_steps = len([s for s in task.steps if s.status == StepStatus.COMPLETED])
        return completed_steps / len(task.steps)
    
    def get_statistics(self) -> Dict:
        """Возвращает статистику планировщика"""
        return {
            **self.stats,
            'active_tasks': len(self.active_tasks),
            'queued_tasks': len(self.task_queue),
            'completed_tasks': len(self.completed_tasks),
            'knowledge_base_size': {
                'successful_patterns': len(self.knowledge_base['successful_patterns']),
                'failed_patterns': len(self.knowledge_base['failed_patterns']),
                'optimization_rules': len(self.knowledge_base['optimization_rules'])
            },
            'ai_manager_available': self.ai_manager is not None,
            'multimodal_manager_available': self.multimodal_manager is not None
        }
    
    async def process_task_queue(self):
        """Обрабатывает очередь задач"""
        try:
            while self.task_queue and len(self.active_tasks) < self.max_concurrent_tasks:
                task = self.task_queue.pop(0)
                
                # Планирование задачи
                if await self.plan_task(task.id):
                    # Выполнение задачи
                    asyncio.create_task(self.execute_task(task.id))
                else:
                    # Перемещение неудачной задачи в завершенные
                    self.completed_tasks[task.id] = task
            
        except Exception as e:
            self.logger.error(f"Ошибка обработки очереди задач: {e}")
    
    def cleanup(self):
        """Очистка ресурсов"""
        try:
            # Сохранение базы знаний
            # Здесь можно сохранить базу знаний в файл
            
            # Очистка кэшей
            self.task_queue.clear()
            self.active_tasks.clear()
            
            self.logger.info("Ресурсы планировщика очищены")
            
        except Exception as e:
            self.logger.error(f"Ошибка очистки ресурсов: {e}")
