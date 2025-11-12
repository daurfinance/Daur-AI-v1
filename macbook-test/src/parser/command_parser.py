#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: Парсер команд
Обрабатывает и парсит команды пользователя для выполнения агентом

Версия: 1.0
Дата: 09.05.2025
"""

import re
import json
import logging
from typing import Dict, List, Union, Any, Optional, Tuple


class CommandParser:
    """
    Парсер команд для обработки пользовательского ввода и преобразования
    его в структурированные команды для выполнения агентом
    """
    
    def __init__(self, ai_manager=None):
        """Инициализация парсера команд"""
        self.logger = logging.getLogger('daur_ai.parser')
        self.ai_manager = ai_manager
        
        # Создание регулярных выражений для распознавания команд
        self._command_patterns = {
            # Паттерны для распознавания общих действий
            'click': r'(?:клик|нажми|нажать|кликнуть)(?:\s+(?:на|по))?(?:\s+кнопк(?:у|е|ой))?\s+["\']?([^"\']+)["\']?',
            'dblclick': r'(?:двойной\s+клик|двойное\s+нажатие|дабл\s+клик)(?:\s+(?:на|по))?\s+["\']?([^"\']+)["\']?',
            'move': r'(?:переместить|двигать|подвинуть)(?:\s+(?:курсор|мышь|указатель))?(?:\s+(?:на|к|в))?\s+["\']?([^"\']+)["\']?',
            'type': r'(?:напечатай|введи|написать|набрать|напиши)\s+["\']([^"\']+)["\'](?:\s+в\s+([^"\']+))?',
            
            # Паттерны для распознавания работы с окнами
            'open': r'(?:открой|открыть|запусти|запустить)\s+(?:приложение|программу|утилиту)?\s*["\']?([^"\']+)["\']?',
            'close': r'(?:закрой|закрыть|завершить|выйти из)\s+(?:приложение|программу|утилиту)?\s*["\']?([^"\']+)["\']?',
            'switch': r'(?:переключись|переключиться|перейти)(?:\s+(?:на|в|к))?\s+(?:приложение|программу|окно)?\s*["\']?([^"\']+)["\']?',
            
            # Паттерны для распознавания работы с файлами
            'file_create': r'(?:создай|создать|новый)\s+файл\s+["\']?([^"\']+)["\']?(?:\s+с\s+содержимым\s+["\']([^"\']+)["\'])?',
            'file_read': r'(?:прочитай|прочитать|открой|открыть|показать|покажи)\s+(?:содержимое|файл)?\s+["\']?([^"\']+)["\']?',
            'file_write': r'(?:запиши|записать|сохрани|сохранить)\s+["\']([^"\']+)["\'](?:\s+в\s+(?:файл)?\s+["\']?([^"\']+)["\']?)',
            'file_delete': r'(?:удали|удалить|стереть|убрать)\s+файл\s+["\']?([^"\']+)["\']?',
            
            # Паттерны для распознавания работы с директориями
            'dir_list': r'(?:покажи|показать|посмотреть|просмотреть)(?:\s+содержимое)?\s+(?:папк(?:у|и)|директори(?:ю|и)|каталог(?:а)?)\s+["\']?([^"\']+)["\']?',
            'dir_create': r'(?:создай|создать|новая)\s+(?:папк(?:у|а)|директори(?:ю|я)|каталог)\s+["\']?([^"\']+)["\']?',
            'dir_delete': r'(?:удали|удалить|стереть|убрать)\s+(?:папк(?:у|а)|директори(?:ю|я)|каталог)\s+["\']?([^"\']+)["\']?',
            
            # Паттерны для распознавания системных команд
            'system_exec': r'(?:выполни|выполнить|запусти|запустить)\s+команду\s+["\']([^"\']+)["\']',
            'system_info': r'(?:информация|инфо|статус)(?:\s+(?:о|про|об)\s+системе)?',
            
            # Паттерн для копирования и вставки
            'copy': r'(?:скопируй|скопировать|копировать)\s+(?:текст\s+)?["\']?([^"\']+)["\']?',
            'paste': r'(?:вставь|вставить|вставка)',
            
            # Паттерн для нажатия клавиш
            'key': r'(?:нажми|нажать|нажатие)\s+(?:клавиш(?:у|и|ей)?\s+)?["\']?([^"\']+)["\']?',
            'keydown': r'(?:зажми|зажать|удерживай|удерживать)\s+(?:клавиш(?:у|и|ей)?\s+)?["\']?([^"\']+)["\']?',
            'keyup': r'(?:отпусти|отпустить|освободи|освободить)\s+(?:клавиш(?:у|и|ей)?\s+)?["\']?([^"\']+)["\']?',
            
            # Паттерн для команды ожидания
            'wait': r'(?:подожди|ждать|ожидать|пауза|задержка)\s+(?:(\d+)\s+(?:секунд(?:ы|у)?|сек))',
            
            # Паттерн для скроллинга
            'scroll': r'(?:скролл|прокрути|прокрутить|скроллить)\s+(?:вниз|вверх|влево|вправо)(?:\s+на\s+(\d+))?',
            
            # Паттерн для скриншота
            'screenshot': r'(?:скриншот|снимок экрана|сделай скриншот|сохрани экран)'
        }
        
        # Компиляция регулярных выражений для оптимизации
        self._compiled_patterns = {
            cmd: re.compile(pattern, re.IGNORECASE) 
            for cmd, pattern in self._command_patterns.items()
        }
        
        # Инициализация шаблонов сложных команд
        self._init_complex_patterns()
        
        self.logger.info("Парсер команд инициализирован")
    
    def _init_complex_patterns(self):
        """
        Инициализация шаблонов для распознавания сложных команд,
        содержащих несколько действий
        """
        # Паттерн для распознавания цепочки действий, разделенных "и" или "затем"
        self.sequence_pattern = re.compile(
            r'(?:\s*,\s*|\s+и\s+|\s+затем\s+|\s+после этого\s+|\s+потом\s+)',
            re.IGNORECASE
        )
        
        # Паттерн для распознавания условий
        self.condition_pattern = re.compile(
            r'(?:если|когда|при условии)\s+([^,]+)(?:\s*,\s*|\s+то\s+)(.+)',
            re.IGNORECASE
        )
        
        # Паттерн для распознавания циклов
        self.loop_pattern = re.compile(
            r'(?:повторить|повторять)\s+(\d+)\s+раз(?:\s*:|\s+следующее\s*:)?\s*(.+)',
            re.IGNORECASE
        )
    
    def parse(self, command: str) -> List[Dict[str, Any]]:
        """
        Основной метод парсинга команд с использованием AI
        
        Args:
            command (str): Команда пользователя
            
        Returns:
            List[Dict]: Список действий для выполнения
        """
        try:
            if self.ai_manager and hasattr(self.ai_manager, 'parse_command'):
                # Используем AI для парсинга
                return self.ai_manager.parse_command(command)
            else:
                # Используем традиционный парсинг
                parsed = self.parse_command(command)
                if parsed.get('success', False):
                    return [parsed]
                else:
                    return []
        except Exception as e:
            self.logger.error(f"Ошибка парсинга команды: {e}")
            return []

    def parse_command(self, text: str) -> Dict[str, Any]:
        """
        Парсинг текстовой команды в структурированный формат
        
        Args:
            text (str): Текстовая команда пользователя
            
        Returns:
            dict: Структурированная команда для выполнения
                {
                    "type": тип команды,
                    "params": параметры команды,
                    "raw": исходный текст команды,
                    "success": успешность парсинга,
                    "error": сообщение об ошибке (если есть)
                }
        """
        self.logger.debug(f"Парсинг команды: {text}")
        
        # Проверка на пустую команду
        if not text or not text.strip():
            return {
                "type": "invalid",
                "params": {},
                "raw": text,
                "success": False,
                "error": "Пустая команда"
            }
        
        # Приведение команды к нижнему регистру для упрощения парсинга
        text = text.strip()
        
        # Проверка на последовательность команд
        if self.sequence_pattern.search(text):
            return self._parse_sequence(text)
        
        # Проверка на условную команду
        condition_match = self.condition_pattern.match(text)
        if condition_match:
            return self._parse_condition(condition_match)
        
        # Проверка на циклическую команду
        loop_match = self.loop_pattern.match(text)
        if loop_match:
            return self._parse_loop(loop_match)
        
        # Парсинг простой команды
        return self._parse_simple_command(text)
    
    def _parse_sequence(self, text: str) -> Dict[str, Any]:
        """
        Парсинг последовательности команд
        
        Args:
            text (str): Текстовая команда с последовательностью
            
        Returns:
            dict: Структурированная последовательность команд
        """
        # Разделение на отдельные команды
        commands_text = self.sequence_pattern.split(text)
        
        # Парсинг каждой команды
        parsed_commands = []
        for cmd_text in commands_text:
            cmd_text = cmd_text.strip()
            if cmd_text:
                parsed_cmd = self._parse_simple_command(cmd_text)
                parsed_commands.append(parsed_cmd)
        
        # Проверка наличия успешно распознанных команд
        if not parsed_commands:
            return {
                "type": "invalid",
                "params": {},
                "raw": text,
                "success": False,
                "error": "Не удалось распознать команды в последовательности"
            }
        
        # Формирование результата
        result = {
            "type": "sequence",
            "params": {
                "commands": parsed_commands
            },
            "raw": text,
            "success": True
        }
        
        self.logger.debug(f"Распознана последовательность команд: {len(parsed_commands)} команд")
        return result
    
    def _parse_condition(self, match) -> Dict[str, Any]:
        """
        Парсинг условной команды
        
        Args:
            match: Результат регулярного выражения
            
        Returns:
            dict: Структурированная условная команда
        """
        condition_text = match.group(1).strip()
        action_text = match.group(2).strip()
        
        # Парсинг условия и действия
        condition = self._parse_simple_command(condition_text)
        action = self.parse_command(action_text)  # Рекурсивный вызов для поддержки сложных команд
        
        # Формирование результата
        result = {
            "type": "condition",
            "params": {
                "condition": condition,
                "action": action
            },
            "raw": match.group(0),
            "success": True
        }
        
        self.logger.debug(f"Распознана условная команда: {condition_text} => {action_text}")
        return result
    
    def _parse_loop(self, match) -> Dict[str, Any]:
        """
        Парсинг циклической команды
        
        Args:
            match: Результат регулярного выражения
            
        Returns:
            dict: Структурированная циклическая команда
        """
        count = int(match.group(1))
        action_text = match.group(2).strip()
        
        # Парсинг действия
        action = self.parse_command(action_text)  # Рекурсивный вызов для поддержки сложных команд
        
        # Формирование результата
        result = {
            "type": "loop",
            "params": {
                "count": count,
                "action": action
            },
            "raw": match.group(0),
            "success": True
        }
        
        self.logger.debug(f"Распознана циклическая команда: {count} раз => {action_text}")
        return result
    
    def _parse_simple_command(self, text: str) -> Dict[str, Any]:
        """
        Парсинг простой команды
        
        Args:
            text (str): Текстовая команда
            
        Returns:
            dict: Структурированная команда
        """
        # Проверка каждого шаблона команды
        for cmd_type, pattern in self._compiled_patterns.items():
            match = pattern.match(text)
            if match:
                # Извлечение параметров команды
                params = match.groups()
                params_dict = {}
                
                # Обработка параметров в зависимости от типа команды
                if cmd_type == 'click' or cmd_type == 'dblclick':
                    params_dict['target'] = params[0]
                
                elif cmd_type == 'move':
                    params_dict['target'] = params[0]
                
                elif cmd_type == 'type':
                    params_dict['text'] = params[0]
                    if len(params) > 1 and params[1]:
                        params_dict['target'] = params[1]
                
                elif cmd_type == 'open' or cmd_type == 'close' or cmd_type == 'switch':
                    params_dict['app'] = params[0]
                
                elif cmd_type == 'file_create':
                    params_dict['path'] = params[0]
                    if len(params) > 1 and params[1]:
                        params_dict['content'] = params[1]
                
                elif cmd_type == 'file_read':
                    params_dict['path'] = params[0]
                
                elif cmd_type == 'file_write':
                    params_dict['content'] = params[0]
                    if len(params) > 1 and params[1]:
                        params_dict['path'] = params[1]
                
                elif cmd_type == 'file_delete' or cmd_type == 'dir_list' or cmd_type == 'dir_create' or cmd_type == 'dir_delete':
                    params_dict['path'] = params[0]
                
                elif cmd_type == 'system_exec':
                    params_dict['command'] = params[0]
                
                elif cmd_type == 'copy':
                    params_dict['text'] = params[0]
                
                elif cmd_type == 'key' or cmd_type == 'keydown' or cmd_type == 'keyup':
                    params_dict['key'] = params[0]
                
                elif cmd_type == 'wait':
                    params_dict['seconds'] = int(params[0]) if params[0] else 1
                
                elif cmd_type == 'scroll':
                    directions = {'вниз': 'down', 'вверх': 'up', 'влево': 'left', 'вправо': 'right'}
                    direction_match = re.search(r'(вниз|вверх|влево|вправо)', text, re.IGNORECASE)
                    if direction_match:
                        params_dict['direction'] = directions[direction_match.group(1).lower()]
                    
                    if params and params[0]:
                        params_dict['amount'] = int(params[0])
                
                # Формирование результата
                result = {
                    "type": cmd_type,
                    "params": params_dict,
                    "raw": text,
                    "success": True
                }
                
                self.logger.debug(f"Распознана команда: {cmd_type} с параметрами {params_dict}")
                return result
        
        # Если команда не распознана
        return {
            "type": "unknown",
            "params": {"text": text},
            "raw": text,
            "success": False,
            "error": "Неизвестная команда"
        }
    
    def parse_json_command(self, json_text: str) -> Dict[str, Any]:
        """
        Парсинг команды в формате JSON
        
        Args:
            json_text (str): Команда в формате JSON
            
        Returns:
            dict: Структурированная команда
        """
        try:
            # Попытка парсинга JSON
            cmd = json.loads(json_text)
            
            # Проверка наличия обязательных полей
            if "type" not in cmd:
                return {
                    "type": "invalid",
                    "params": {},
                    "raw": json_text,
                    "success": False,
                    "error": "Отсутствует обязательное поле 'type'"
                }
            
            # Добавление метаданных
            cmd["raw"] = json_text
            cmd["success"] = True
            
            # Если параметры не указаны, добавляем пустой словарь
            if "params" not in cmd:
                cmd["params"] = {}
            
            self.logger.debug(f"Распознана JSON-команда: {cmd['type']}")
            return cmd
            
        except json.JSONDecodeError as e:
            return {
                "type": "invalid",
                "params": {},
                "raw": json_text,
                "success": False,
                "error": f"Ошибка парсинга JSON: {e}"
            }
    
    def format_error_message(self, cmd: Dict[str, Any]) -> str:
        """
        Форматирование сообщения об ошибке
        
        Args:
            cmd (dict): Результат парсинга команды
            
        Returns:
            str: Сообщение об ошибке
        """
        if cmd["success"]:
            return "Команда распознана успешно"
        
        if "error" in cmd:
            return f"Ошибка: {cmd['error']}"
        
        if cmd["type"] == "unknown":
            return f"Команда не распознана: '{cmd['raw']}'"
        
        if cmd["type"] == "invalid":
            return f"Недопустимая команда: '{cmd['raw']}'"
        
        return "Неизвестная ошибка при парсинге команды"
