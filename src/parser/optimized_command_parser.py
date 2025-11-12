#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: Оптимизированный парсер команд
Включает кэширование, параллельную обработку, улучшенное распознавание и обработку ошибок

Версия: 2.0
Дата: 25.10.2025
Автор: Manus AI
"""

import re
import json
import logging
import hashlib
import threading
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from collections import OrderedDict, defaultdict
import time
from datetime import datetime


class CommandType(Enum):
    """Типы команд"""
    FILE_OPERATION = "file_operation"
    SYSTEM_CONTROL = "system_control"
    APPLICATION = "application"
    TEXT_INPUT = "text_input"
    MOUSE_ACTION = "mouse_action"
    SCREENSHOT = "screenshot"
    SEARCH = "search"
    HELP = "help"
    UNKNOWN = "unknown"


class ActionType(Enum):
    """Типы действий"""
    CREATE = "create"
    DELETE = "delete"
    OPEN = "open"
    CLOSE = "close"
    MOVE = "move"
    COPY = "copy"
    CLICK = "click"
    TYPE = "type"
    SCROLL = "scroll"
    TAKE = "take"
    SEARCH = "search"
    HELP = "help"
    MODIFY = "modify"
    READ = "read"
    EXECUTE = "execute"


class ParsedCommand:
    """Структура для хранения распознанной команды"""
    
    def __init__(self, command_type: CommandType, action: ActionType, 
                 parameters: Dict[str, Any], confidence: float = 1.0):
        """
        Args:
            command_type: Тип команды
            action: Тип действия
            parameters: Параметры команды
            confidence: Уровень уверенности (0-1)
        """
        self.command_type = command_type
        self.action = action
        self.parameters = parameters
        self.confidence = confidence
        self.timestamp = datetime.now()
        self.raw_text = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return {
            'command_type': self.command_type.value,
            'action': self.action.value,
            'parameters': self.parameters,
            'confidence': self.confidence,
            'timestamp': self.timestamp.isoformat()
        }


class OptimizedCommandParser:
    """
    Оптимизированный парсер команд с расширенными возможностями
    """
    
    def __init__(self, ai_manager=None, cache_size: int = 500):
        """
        Инициализация парсера
        
        Args:
            ai_manager: Менеджер AI моделей (опционально)
            cache_size: Размер кэша распознанных команд
        """
        self.logger = logging.getLogger('daur_ai.optimized_parser')
        self.ai_manager = ai_manager
        self.cache_size = cache_size
        
        # Кэш распознанных команд
        self.command_cache = OrderedDict()
        self.cache_lock = threading.RLock()
        
        # Статистика парсинга
        self.parse_stats = {
            'total_parses': 0,
            'successful_parses': 0,
            'failed_parses': 0,
            'cache_hits': 0,
            'total_parse_time': 0
        }
        
        # История команд для обучения
        self.command_history = []
        self.max_history = 1000
        
        # Шаблоны для быстрого распознавания (оптимизированные регулярные выражения)
        self.quick_patterns = self._compile_patterns()
        
        # Словарь синонимов для улучшенного распознавания
        self.synonyms = self._build_synonyms()
        
        self.logger.info("Оптимизированный парсер команд инициализирован")
    
    def _compile_patterns(self) -> Dict[CommandType, List[Tuple[re.Pattern, ActionType]]]:
        """
        Компиляция регулярных выражений для быстрого распознавания
        
        Returns:
            Dict: Скомпилированные шаблоны
        """
        patterns = {}
        
        # Файловые операции
        patterns[CommandType.FILE_OPERATION] = [
            (re.compile(r'создай файл (.+)', re.IGNORECASE), ActionType.CREATE),
            (re.compile(r'удали файл (.+)', re.IGNORECASE), ActionType.DELETE),
            (re.compile(r'открой файл (.+)', re.IGNORECASE), ActionType.OPEN),
            (re.compile(r'скопируй файл (.+)', re.IGNORECASE), ActionType.COPY),
            (re.compile(r'переименуй файл (.+)', re.IGNORECASE), ActionType.MODIFY),
            (re.compile(r'прочитай файл (.+)', re.IGNORECASE), ActionType.READ),
            (re.compile(r'сохрани (.+) в файл (.+)', re.IGNORECASE), ActionType.CREATE),
            (re.compile(r'создать (.+\.(?:txt|py|js|html|css|json|md))', re.IGNORECASE), ActionType.CREATE),
        ]
        
        # Приложения
        patterns[CommandType.APPLICATION] = [
            (re.compile(r'открой (.+)', re.IGNORECASE), ActionType.OPEN),
            (re.compile(r'запусти (.+)', re.IGNORECASE), ActionType.EXECUTE),
            (re.compile(r'закрой (.+)', re.IGNORECASE), ActionType.CLOSE),
            (re.compile(r'открыть (.+)', re.IGNORECASE), ActionType.OPEN),
            (re.compile(r'запустить (.+)', re.IGNORECASE), ActionType.EXECUTE),
            (re.compile(r'браузер', re.IGNORECASE), ActionType.OPEN),
            (re.compile(r'терминал', re.IGNORECASE), ActionType.OPEN),
            (re.compile(r'блокнот', re.IGNORECASE), ActionType.OPEN),
        ]
        
        # Ввод текста
        patterns[CommandType.TEXT_INPUT] = [
            (re.compile(r'напиши (.+)', re.IGNORECASE), ActionType.TYPE),
            (re.compile(r'введи (.+)', re.IGNORECASE), ActionType.TYPE),
            (re.compile(r'напишите (.+)', re.IGNORECASE), ActionType.TYPE),
            (re.compile(r'вводи (.+)', re.IGNORECASE), ActionType.TYPE),
        ]
        
        # Действия с мышью
        patterns[CommandType.MOUSE_ACTION] = [
            (re.compile(r'клик по (.+)', re.IGNORECASE), ActionType.CLICK),
            (re.compile(r'нажми (.+)', re.IGNORECASE), ActionType.CLICK),
            (re.compile(r'прокрути (.+)', re.IGNORECASE), ActionType.SCROLL),
            (re.compile(r'скролл (.+)', re.IGNORECASE), ActionType.SCROLL),
        ]
        
        # Скриншоты
        patterns[CommandType.SCREENSHOT] = [
            (re.compile(r'снимок экрана', re.IGNORECASE), ActionType.TAKE),
            (re.compile(r'скриншот', re.IGNORECASE), ActionType.TAKE),
            (re.compile(r'сделай скриншот', re.IGNORECASE), ActionType.TAKE),
            (re.compile(r'сфотографируй экран', re.IGNORECASE), ActionType.TAKE),
        ]
        
        # Поиск
        patterns[CommandType.SEARCH] = [
            (re.compile(r'найди (.+)', re.IGNORECASE), ActionType.SEARCH),
            (re.compile(r'поиск (.+)', re.IGNORECASE), ActionType.SEARCH),
            (re.compile(r'ищи (.+)', re.IGNORECASE), ActionType.SEARCH),
            (re.compile(r'найти (.+)', re.IGNORECASE), ActionType.SEARCH),
        ]
        
        # Справка
        patterns[CommandType.HELP] = [
            (re.compile(r'помощь', re.IGNORECASE), ActionType.HELP),
            (re.compile(r'справка', re.IGNORECASE), ActionType.HELP),
            (re.compile(r'что ты можешь делать', re.IGNORECASE), ActionType.HELP),
            (re.compile(r'помоги', re.IGNORECASE), ActionType.HELP),
        ]
        
        return patterns
    
    def _build_synonyms(self) -> Dict[str, List[str]]:
        """
        Построение словаря синонимов для улучшенного распознавания
        
        Returns:
            Dict: Словарь синонимов
        """
        return {
            'создай': ['создать', 'сделай', 'создаю', 'создавай'],
            'удали': ['удалить', 'удаляй', 'стирай', 'сотри'],
            'открой': ['открыть', 'откройте', 'открывай', 'запусти'],
            'скопируй': ['копировать', 'скопируй', 'дублируй'],
            'напиши': ['напишите', 'напишу', 'вводи', 'введи'],
            'клик': ['нажми', 'кликни', 'нажимай'],
            'найди': ['поиск', 'ищи', 'найти', 'поищи'],
            'помощь': ['справка', 'помоги', 'подскажи', 'инструкция'],
        }
    
    def _generate_cache_key(self, text: str) -> str:
        """
        Генерация ключа кэша
        
        Args:
            text: Текст команды
            
        Returns:
            str: Хэш-ключ
        """
        return hashlib.md5(text.lower().encode()).hexdigest()
    
    def _get_from_cache(self, cache_key: str) -> Optional[ParsedCommand]:
        """
        Получить команду из кэша
        
        Args:
            cache_key: Ключ кэша
            
        Returns:
            Optional[ParsedCommand]: Команда из кэша или None
        """
        with self.cache_lock:
            if cache_key in self.command_cache:
                self.parse_stats['cache_hits'] += 1
                # Переместить в конец (LRU)
                self.command_cache.move_to_end(cache_key)
                return self.command_cache[cache_key]
        
        return None
    
    def _set_cache(self, cache_key: str, command: ParsedCommand):
        """
        Сохранить команду в кэш
        
        Args:
            cache_key: Ключ кэша
            command: Распознанная команда
        """
        with self.cache_lock:
            # Если кэш переполнен, удаляем самый старый элемент
            if len(self.command_cache) >= self.cache_size:
                self.command_cache.popitem(last=False)
            
            self.command_cache[cache_key] = command
    
    def _normalize_text(self, text: str) -> str:
        """
        Нормализация текста для парсинга
        
        Args:
            text: Исходный текст
            
        Returns:
            str: Нормализованный текст
        """
        # Преобразование в нижний регистр
        text = text.lower().strip()
        
        # Удаление лишних пробелов
        text = re.sub(r'\s+', ' ', text)
        
        # Замена синонимов
        for key, synonyms in self.synonyms.items():
            for synonym in synonyms:
                text = re.sub(r'\b' + synonym + r'\b', key, text)
        
        return text
    
    def _quick_parse(self, text: str) -> Optional[ParsedCommand]:
        """
        Быстрый парсинг с использованием регулярных выражений
        
        Args:
            text: Текст команды
            
        Returns:
            Optional[ParsedCommand]: Распознанная команда или None
        """
        normalized_text = self._normalize_text(text)
        
        # Проверяем все шаблоны
        for command_type, patterns in self.quick_patterns.items():
            for pattern, action_type in patterns:
                match = pattern.search(normalized_text)
                if match:
                    # Извлекаем параметры из групп
                    parameters = {}
                    if match.groups():
                        if len(match.groups()) == 1:
                            parameters['target'] = match.group(1)
                        else:
                            for i, group in enumerate(match.groups()):
                                parameters[f'param_{i}'] = group
                    
                    command = ParsedCommand(
                        command_type=command_type,
                        action=action_type,
                        parameters=parameters,
                        confidence=0.95  # Высокая уверенность для шаблонных команд
                    )
                    command.raw_text = text
                    return command
        
        return None
    
    def parse(self, text: str, use_cache: bool = True, use_ai: bool = True) -> ParsedCommand:
        """
        Парсинг текстовой команды
        
        Args:
            text: Текст команды
            use_cache: Использовать кэш
            use_ai: Использовать AI для сложных команд
            
        Returns:
            ParsedCommand: Распознанная команда
        """
        start_time = time.time()
        self.parse_stats['total_parses'] += 1
        
        # Проверка кэша
        if use_cache:
            cache_key = self._generate_cache_key(text)
            cached_command = self._get_from_cache(cache_key)
            
            if cached_command is not None:
                return cached_command
        
        # Быстрый парсинг
        command = self._quick_parse(text)
        
        # Если быстрый парсинг не сработал и есть AI, используем AI
        if command is None and use_ai and self.ai_manager:
            try:
                command = self._ai_parse(text)
            except Exception as e:
                self.logger.warning(f"Ошибка AI парсинга: {e}")
        
        # Если ничего не сработало, возвращаем неизвестную команду
        if command is None:
            command = ParsedCommand(
                command_type=CommandType.UNKNOWN,
                action=ActionType.HELP,
                parameters={'original_text': text},
                confidence=0.0
            )
            self.parse_stats['failed_parses'] += 1
        else:
            self.parse_stats['successful_parses'] += 1
        
        command.raw_text = text
        
        # Сохраняем в кэш
        if use_cache:
            cache_key = self._generate_cache_key(text)
            self._set_cache(cache_key, command)
        
        # Сохраняем в историю
        self._add_to_history(command)
        
        # Обновляем статистику
        parse_time = time.time() - start_time
        self.parse_stats['total_parse_time'] += parse_time
        
        return command
    
    def _ai_parse(self, text: str) -> Optional[ParsedCommand]:
        """
        AI-парсинг для сложных команд
        
        Args:
            text: Текст команды
            
        Returns:
            Optional[ParsedCommand]: Распознанная команда или None
        """
        if not self.ai_manager:
            return None
        
        # Создаем prompt для AI
        prompt = f"""Проанализируй команду и определи:
1. Тип команды (file_operation, application, text_input, mouse_action, screenshot, search, help, unknown)
2. Тип действия (create, delete, open, close, move, copy, click, type, scroll, take, search, help, modify, read, execute)
3. Параметры команды
4. Уровень уверенности (0-1)

Команда: "{text}"

Ответь в формате JSON:
{{"command_type": "...", "action": "...", "parameters": {{}}, "confidence": 0.0}}"""
        
        try:
            response = self.ai_manager.generate_response(prompt)
            
            if response.get('success'):
                # Парсим JSON ответ
                json_str = response.get('response', '{}')
                parsed = json.loads(json_str)
                
                command = ParsedCommand(
                    command_type=CommandType[parsed.get('command_type', 'UNKNOWN').upper()],
                    action=ActionType[parsed.get('action', 'HELP').upper()],
                    parameters=parsed.get('parameters', {}),
                    confidence=float(parsed.get('confidence', 0.5))
                )
                
                return command
        
        except Exception as e:
            self.logger.error(f"Ошибка при AI парсинге: {e}")
        
        return None
    
    def _add_to_history(self, command: ParsedCommand):
        """
        Добавить команду в историю
        
        Args:
            command: Распознанная команда
        """
        self.command_history.append(command)
        
        # Ограничиваем размер истории
        if len(self.command_history) > self.max_history:
            self.command_history.pop(0)
    
    def get_parse_stats(self) -> Dict[str, Any]:
        """
        Получить статистику парсинга
        
        Returns:
            Dict: Статистика парсинга
        """
        avg_parse_time = 0
        if self.parse_stats['total_parses'] > 0:
            avg_parse_time = self.parse_stats['total_parse_time'] / self.parse_stats['total_parses']
        
        success_rate = 0
        if self.parse_stats['total_parses'] > 0:
            success_rate = (self.parse_stats['successful_parses'] / self.parse_stats['total_parses']) * 100
        
        return {
            'total_parses': self.parse_stats['total_parses'],
            'successful_parses': self.parse_stats['successful_parses'],
            'failed_parses': self.parse_stats['failed_parses'],
            'cache_hits': self.parse_stats['cache_hits'],
            'average_parse_time': round(avg_parse_time, 4),
            'success_rate': round(success_rate, 2),
            'cache_size': len(self.command_cache),
            'history_size': len(self.command_history)
        }
    
    def clear_cache(self):
        """Очистить кэш команд"""
        with self.cache_lock:
            self.command_cache.clear()
            self.logger.info("Кэш парсера очищен")
    
    def get_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Получить историю команд
        
        Args:
            limit: Максимальное количество команд
            
        Returns:
            List[Dict]: История команд
        """
        return [cmd.to_dict() for cmd in self.command_history[-limit:]]


def create_optimized_parser(ai_manager=None) -> OptimizedCommandParser:
    """
    Фабрика для создания оптимизированного парсера
    
    Args:
        ai_manager: Менеджер AI моделей
        
    Returns:
        OptimizedCommandParser: Инициализированный парсер
    """
    return OptimizedCommandParser(ai_manager)

