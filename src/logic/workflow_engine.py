#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: Модуль улучшения логики работы системы
Управление рабочими процессами, логикой и автоматизацией

Версия: 2.0
Дата: 25.10.2025
Автор: Manus AI
"""

import logging
import json
import time
from typing import Dict, List, Any, Optional, Callable, Tuple
from pathlib import Path
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from abc import ABC, abstractmethod


class WorkflowState(Enum):
    """Состояния рабочего процесса"""
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StepStatus(Enum):
    """Статусы шагов"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class WorkflowStep:
    """Шаг рабочего процесса"""
    step_id: str
    name: str
    description: str = ""
    action: Optional[Callable] = None
    status: StepStatus = StepStatus.PENDING
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    timeout: int = 300
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class Workflow:
    """Рабочий процесс"""
    workflow_id: str
    name: str
    description: str = ""
    steps: List[WorkflowStep] = field(default_factory=list)
    state: WorkflowState = WorkflowState.CREATED
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LogicRule:
    """Правило логики"""
    rule_id: str
    name: str
    condition: Callable[[Dict[str, Any]], bool]
    action: Callable[[Dict[str, Any]], Dict[str, Any]]
    priority: int = 5
    enabled: bool = True


class WorkflowEngine:
    """Движок рабочих процессов"""
    
    def __init__(self):
        """Инициализация"""
        self.logger = logging.getLogger('daur_ai.workflow_engine')
        self.workflows: Dict[str, Workflow] = {}
        self.running_workflows: Dict[str, Workflow] = {}
    
    def create_workflow(self, workflow_id: str, name: str,
                       description: str = "") -> Workflow:
        """
        Создать рабочий процесс
        
        Args:
            workflow_id: ID рабочего процесса
            name: Имя
            description: Описание
            
        Returns:
            Workflow: Объект рабочего процесса
        """
        workflow = Workflow(workflow_id, name, description)
        self.workflows[workflow_id] = workflow
        self.logger.info(f"Рабочий процесс создан: {workflow_id}")
        return workflow
    
    def add_step(self, workflow_id: str, step: WorkflowStep) -> bool:
        """
        Добавить шаг в рабочий процесс
        
        Args:
            workflow_id: ID рабочего процесса
            step: Шаг
            
        Returns:
            bool: Успешность операции
        """
        if workflow_id not in self.workflows:
            self.logger.error(f"Рабочий процесс не найден: {workflow_id}")
            return False
        
        self.workflows[workflow_id].steps.append(step)
        self.logger.info(f"Шаг добавлен: {step.step_id}")
        return True
    
    def execute_workflow(self, workflow_id: str) -> bool:
        """
        Выполнить рабочий процесс
        
        Args:
            workflow_id: ID рабочего процесса
            
        Returns:
            bool: Успешность выполнения
        """
        if workflow_id not in self.workflows:
            self.logger.error(f"Рабочий процесс не найден: {workflow_id}")
            return False
        
        workflow = self.workflows[workflow_id]
        workflow.state = WorkflowState.RUNNING
        workflow.started_at = datetime.now()
        self.running_workflows[workflow_id] = workflow
        
        try:
            for step in workflow.steps:
                if not self._execute_step(workflow, step):
                    workflow.state = WorkflowState.FAILED
                    self.logger.error(f"Рабочий процесс завершился с ошибкой: {workflow_id}")
                    return False
            
            workflow.state = WorkflowState.COMPLETED
            workflow.completed_at = datetime.now()
            self.logger.info(f"Рабочий процесс завершен: {workflow_id}")
            return True
        
        except Exception as e:
            workflow.state = WorkflowState.FAILED
            self.logger.error(f"Ошибка выполнения рабочего процесса: {e}")
            return False
        
        finally:
            if workflow_id in self.running_workflows:
                del self.running_workflows[workflow_id]
    
    def _execute_step(self, workflow: Workflow, step: WorkflowStep) -> bool:
        """
        Выполнить шаг
        
        Args:
            workflow: Рабочий процесс
            step: Шаг
            
        Returns:
            bool: Успешность выполнения
        """
        step.status = StepStatus.RUNNING
        step.started_at = datetime.now()
        
        try:
            if step.action:
                result = step.action(step.input_data)
                step.output_data = result or {}
            
            step.status = StepStatus.COMPLETED
            step.completed_at = datetime.now()
            self.logger.info(f"Шаг выполнен: {step.step_id}")
            return True
        
        except Exception as e:
            step.error = str(e)
            
            if step.retry_count < step.max_retries:
                step.retry_count += 1
                self.logger.warning(f"Повтор шага {step.step_id} ({step.retry_count}/{step.max_retries})")
                return self._execute_step(workflow, step)
            
            step.status = StepStatus.FAILED
            self.logger.error(f"Ошибка выполнения шага: {step.step_id} - {e}")
            return False
    
    def pause_workflow(self, workflow_id: str) -> bool:
        """
        Приостановить рабочий процесс
        
        Args:
            workflow_id: ID рабочего процесса
            
        Returns:
            bool: Успешность операции
        """
        if workflow_id in self.running_workflows:
            self.running_workflows[workflow_id].state = WorkflowState.PAUSED
            self.logger.info(f"Рабочий процесс приостановлен: {workflow_id}")
            return True
        
        return False
    
    def cancel_workflow(self, workflow_id: str) -> bool:
        """
        Отменить рабочий процесс
        
        Args:
            workflow_id: ID рабочего процесса
            
        Returns:
            bool: Успешность операции
        """
        if workflow_id in self.running_workflows:
            self.running_workflows[workflow_id].state = WorkflowState.CANCELLED
            del self.running_workflows[workflow_id]
            self.logger.info(f"Рабочий процесс отменен: {workflow_id}")
            return True
        
        return False
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """
        Получить статус рабочего процесса
        
        Args:
            workflow_id: ID рабочего процесса
            
        Returns:
            Optional[Dict]: Статус рабочего процесса
        """
        if workflow_id not in self.workflows:
            return None
        
        workflow = self.workflows[workflow_id]
        
        return {
            'workflow_id': workflow.workflow_id,
            'name': workflow.name,
            'state': workflow.state.value,
            'steps': len(workflow.steps),
            'completed_steps': sum(1 for s in workflow.steps if s.status == StepStatus.COMPLETED),
            'failed_steps': sum(1 for s in workflow.steps if s.status == StepStatus.FAILED)
        }


class LogicEngine:
    """Движок логики"""
    
    def __init__(self):
        """Инициализация"""
        self.logger = logging.getLogger('daur_ai.logic_engine')
        self.rules: Dict[str, LogicRule] = {}
    
    def add_rule(self, rule: LogicRule) -> bool:
        """
        Добавить правило
        
        Args:
            rule: Правило
            
        Returns:
            bool: Успешность операции
        """
        self.rules[rule.rule_id] = rule
        self.logger.info(f"Правило добавлено: {rule.rule_id}")
        return True
    
    def remove_rule(self, rule_id: str) -> bool:
        """
        Удалить правило
        
        Args:
            rule_id: ID правила
            
        Returns:
            bool: Успешность операции
        """
        if rule_id in self.rules:
            del self.rules[rule_id]
            self.logger.info(f"Правило удалено: {rule_id}")
            return True
        
        return False
    
    def evaluate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Оценить контекст с применением правил
        
        Args:
            context: Контекст
            
        Returns:
            Dict: Результат оценки
        """
        result = context.copy()
        
        # Сортируем правила по приоритету
        sorted_rules = sorted(
            [r for r in self.rules.values() if r.enabled],
            key=lambda r: r.priority,
            reverse=True
        )
        
        for rule in sorted_rules:
            try:
                if rule.condition(result):
                    result = rule.action(result)
                    self.logger.info(f"Правило применено: {rule.rule_id}")
            
            except Exception as e:
                self.logger.error(f"Ошибка применения правила {rule.rule_id}: {e}")
        
        return result
    
    def get_status(self) -> Dict[str, Any]:
        """Получить статус движка"""
        return {
            'rules': len(self.rules),
            'enabled_rules': sum(1 for r in self.rules.values() if r.enabled)
        }


class AutomationEngine:
    """Движок автоматизации"""
    
    def __init__(self):
        """Инициализация"""
        self.logger = logging.getLogger('daur_ai.automation_engine')
        self.workflow_engine = WorkflowEngine()
        self.logic_engine = LogicEngine()
        self.automations: Dict[str, Dict[str, Any]] = {}
    
    def create_automation(self, automation_id: str, name: str,
                        trigger: Callable, action: Callable) -> bool:
        """
        Создать автоматизацию
        
        Args:
            automation_id: ID автоматизации
            name: Имя
            trigger: Функция триггера
            action: Функция действия
            
        Returns:
            bool: Успешность операции
        """
        self.automations[automation_id] = {
            'name': name,
            'trigger': trigger,
            'action': action,
            'enabled': True,
            'created_at': datetime.now()
        }
        
        self.logger.info(f"Автоматизация создана: {automation_id}")
        return True
    
    def check_automations(self, context: Dict[str, Any]) -> List[Tuple[str, Any]]:
        """
        Проверить автоматизации
        
        Args:
            context: Контекст
            
        Returns:
            List: Список активированных автоматизаций и результатов
        """
        results = []
        
        for automation_id, automation in self.automations.items():
            if not automation['enabled']:
                continue
            
            try:
                if automation['trigger'](context):
                    result = automation['action'](context)
                    results.append((automation_id, result))
                    self.logger.info(f"Автоматизация активирована: {automation_id}")
            
            except Exception as e:
                self.logger.error(f"Ошибка автоматизации {automation_id}: {e}")
        
        return results
    
    def get_status(self) -> Dict[str, Any]:
        """Получить статус движка"""
        return {
            'automations': len(self.automations),
            'enabled_automations': sum(1 for a in self.automations.values() if a['enabled']),
            'workflow_engine': {
                'workflows': len(self.workflow_engine.workflows),
                'running': len(self.workflow_engine.running_workflows)
            },
            'logic_engine': self.logic_engine.get_status()
        }


# Глобальные экземпляры
_workflow_engine = None
_logic_engine = None
_automation_engine = None


def get_workflow_engine() -> WorkflowEngine:
    """Получить движок рабочих процессов"""
    global _workflow_engine
    if _workflow_engine is None:
        _workflow_engine = WorkflowEngine()
    return _workflow_engine


def get_logic_engine() -> LogicEngine:
    """Получить движок логики"""
    global _logic_engine
    if _logic_engine is None:
        _logic_engine = LogicEngine()
    return _logic_engine


def get_automation_engine() -> AutomationEngine:
    """Получить движок автоматизации"""
    global _automation_engine
    if _automation_engine is None:
        _automation_engine = AutomationEngine()
    return _automation_engine

