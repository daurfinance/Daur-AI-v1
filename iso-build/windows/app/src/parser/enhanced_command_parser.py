#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: Улучшенный парсер команд с AI
Использует настоящие языковые модели для понимания команд

Версия: 1.1
Дата: 01.10.2025
"""

import re
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum

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

class EnhancedCommandParser:
    """
    Улучшенный парсер команд с использованием AI
    """
    
    def __init__(self, ai_manager=None):
        """
        Инициализация парсера
        
        Args:
            ai_manager: Менеджер AI моделей
        """
        self.logger = logging.getLogger('daur_ai.enhanced_parser')
        self.ai_manager = ai_manager
        
        # Шаблоны для быстрого распознавания
        self.quick_patterns = {
            CommandType.FILE_OPERATION: [
                r'создай файл (.+)',
                r'удали файл (.+)',
                r'открой файл (.+)',
                r'скопируй файл (.+)',
                r'переименуй файл (.+)',
                r'создать (.+\.(?:txt|py|js|html|css|json))',
                r'сохрани (.+) в файл (.+)',
            ],
            CommandType.APPLICATION: [
                r'открой (.+)',
                r'запусти (.+)',
                r'закрой (.+)',
                r'открыть (.+)',
                r'запустить (.+)',
                r'браузер',
                r'терминал',
                r'блокнот',
                r'калькулятор',
            ],
            CommandType.TEXT_INPUT: [
                r'напечатай (.+)',
                r'введи (.+)',
                r'напиши (.+)',
                r'печатать (.+)',
                r'ввести (.+)',
            ],
            CommandType.MOUSE_ACTION: [
                r'кликни (.+)',
                r'нажми (.+)',
                r'щелкни (.+)',
                r'прокрути (.+)',
                r'перетащи (.+)',
            ],
            CommandType.SCREENSHOT: [
                r'сделай скриншот',
                r'скриншот',
                r'снимок экрана',
                r'сфотографируй экран',
            ],
            CommandType.SYSTEM_CONTROL: [
                r'выключи компьютер',
                r'перезагрузи',
                r'заблокируй экран',
                r'открой диспетчер задач',
                r'покажи процессы',
            ],
            CommandType.HELP: [
                r'помощь',
                r'справка',
                r'help',
                r'что ты умеешь',
                r'команды',
            ]
        }
        
        # Системный промпт для AI
        self.system_prompt = """Ты - парсер команд для автономного ИИ-агента Daur-AI. 
Твоя задача - анализировать команды пользователя на естественном языке и возвращать структурированный JSON.

Верни JSON в следующем формате:
{
    "command_type": "тип команды",
    "action": "действие", 
    "target": "цель действия",
    "parameters": {"дополнительные параметры"},
    "confidence": 0.95
}

Типы команд:
- file_operation: работа с файлами
- application: управление приложениями
- text_input: ввод текста
- mouse_action: действия мыши
- screenshot: создание скриншотов
- system_control: системные команды
- search: поиск
- help: справка

Примеры:
"создай файл test.txt" -> {"command_type": "file_operation", "action": "create", "target": "test.txt", "parameters": {"content": ""}, "confidence": 0.9}
"открой браузер" -> {"command_type": "application", "action": "open", "target": "browser", "parameters": {}, "confidence": 0.95}
"напечатай привет мир" -> {"command_type": "text_input", "action": "type", "target": "привет мир", "parameters": {}, "confidence": 0.9}

Отвечай ТОЛЬКО JSON, без дополнительного текста."""
        
        self.logger.info("Улучшенный парсер команд инициализирован")
    
    def parse(self, command_text: str) -> Dict[str, Any]:
        """
        Парсинг команды с использованием AI
        
        Args:
            command_text (str): Текст команды
            
        Returns:
            Dict: Структурированная команда
        """
        if not command_text or not command_text.strip():
            return self._create_error_result("Пустая команда")
        
        command_text = command_text.strip().lower()
        
        # Сначала пробуем быстрые шаблоны
        quick_result = self._try_quick_patterns(command_text)
        if quick_result and quick_result.get('confidence', 0) > 0.8:
            self.logger.debug(f"Команда распознана быстрым шаблоном: {quick_result}")
            return quick_result
        
        # Если быстрые шаблоны не сработали, используем AI
        if self.ai_manager:
            ai_result = self._parse_with_ai(command_text)
            if ai_result and ai_result.get('confidence', 0) > 0.5:
                self.logger.debug(f"Команда распознана через AI: {ai_result}")
                return ai_result
        
        # Fallback на простой парсинг
        fallback_result = self._fallback_parse(command_text)
        self.logger.debug(f"Использован fallback парсинг: {fallback_result}")
        return fallback_result
    
    def _try_quick_patterns(self, command_text: str) -> Optional[Dict[str, Any]]:
        """Попытка распознавания через быстрые шаблоны"""
        
        for command_type, patterns in self.quick_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, command_text, re.IGNORECASE)
                if match:
                    return self._create_result_from_pattern(command_type, pattern, match, command_text)
        
        return None
    
    def _create_result_from_pattern(self, command_type: CommandType, pattern: str, match, original_text: str) -> Dict[str, Any]:
        """Создание результата из шаблона"""
        
        result = {
            "command_type": command_type.value,
            "action": "unknown",
            "target": "",
            "parameters": {},
            "confidence": 0.85,
            "original_text": original_text
        }
        
        # Определяем действие и цель на основе шаблона
        if command_type == CommandType.FILE_OPERATION:
            if "создай" in pattern or "создать" in pattern:
                result["action"] = "create"
                result["target"] = match.group(1) if match.groups() else ""
                if not result["target"].endswith(('.txt', '.py', '.js', '.html', '.css', '.json')):
                    result["target"] += ".txt"
            elif "удали" in pattern:
                result["action"] = "delete"
                result["target"] = match.group(1) if match.groups() else ""
            elif "открой" in pattern:
                result["action"] = "open"
                result["target"] = match.group(1) if match.groups() else ""
            elif "скопируй" in pattern:
                result["action"] = "copy"
                result["target"] = match.group(1) if match.groups() else ""
        
        elif command_type == CommandType.APPLICATION:
            if "открой" in pattern or "запусти" in pattern:
                result["action"] = "open"
                target = match.group(1) if match.groups() else ""
                
                # Маппинг популярных приложений
                app_mapping = {
                    "браузер": "firefox",
                    "терминал": "gnome-terminal",
                    "блокнот": "gedit",
                    "калькулятор": "gnome-calculator",
                    "файлы": "nautilus",
                    "настройки": "gnome-control-center"
                }
                
                result["target"] = app_mapping.get(target.lower(), target)
            elif "закрой" in pattern:
                result["action"] = "close"
                result["target"] = match.group(1) if match.groups() else ""
        
        elif command_type == CommandType.TEXT_INPUT:
            result["action"] = "type"
            result["target"] = match.group(1) if match.groups() else ""
        
        elif command_type == CommandType.MOUSE_ACTION:
            if "кликни" in pattern or "нажми" in pattern:
                result["action"] = "click"
                result["target"] = match.group(1) if match.groups() else ""
            elif "прокрути" in pattern:
                result["action"] = "scroll"
                result["target"] = match.group(1) if match.groups() else ""
        
        elif command_type == CommandType.SCREENSHOT:
            result["action"] = "take"
            result["target"] = "screen"
        
        elif command_type == CommandType.HELP:
            result["action"] = "help"
            result["target"] = "commands"
        
        return result
    
    def _parse_with_ai(self, command_text: str) -> Optional[Dict[str, Any]]:
        """Парсинг команды через AI"""
        
        try:
            # Формируем промпт
            prompt = f"{self.system_prompt}\n\nКоманда пользователя: \"{command_text}\""
            
            # Получаем ответ от AI
            response = self.ai_manager.generate_response(prompt)
            
            if not response:
                return None
            
            # Пытаемся извлечь JSON из ответа
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                result = json.loads(json_str)
                
                # Валидация результата
                if self._validate_ai_result(result):
                    result["original_text"] = command_text
                    result["parsed_by"] = "ai"
                    return result
            
        except Exception as e:
            self.logger.warning(f"Ошибка AI парсинга: {e}")
        
        return None
    
    def _validate_ai_result(self, result: Dict[str, Any]) -> bool:
        """Валидация результата AI парсинга"""
        
        required_fields = ["command_type", "action", "target", "confidence"]
        
        # Проверяем наличие обязательных полей
        for field in required_fields:
            if field not in result:
                return False
        
        # Проверяем типы
        if not isinstance(result["confidence"], (int, float)):
            return False
        
        if not 0 <= result["confidence"] <= 1:
            return False
        
        # Проверяем валидность command_type
        valid_types = [ct.value for ct in CommandType]
        if result["command_type"] not in valid_types:
            return False
        
        return True
    
    def _fallback_parse(self, command_text: str) -> Dict[str, Any]:
        """Fallback парсинг для неизвестных команд"""
        
        # Простая эвристика
        if any(word in command_text for word in ["создай", "создать", "файл"]):
            return {
                "command_type": CommandType.FILE_OPERATION.value,
                "action": "create",
                "target": "новый_файл.txt",
                "parameters": {"content": ""},
                "confidence": 0.3,
                "original_text": command_text,
                "parsed_by": "fallback"
            }
        
        elif any(word in command_text for word in ["открой", "запусти"]):
            return {
                "command_type": CommandType.APPLICATION.value,
                "action": "open",
                "target": "unknown_app",
                "parameters": {},
                "confidence": 0.3,
                "original_text": command_text,
                "parsed_by": "fallback"
            }
        
        elif any(word in command_text for word in ["напечатай", "введи", "напиши"]):
            # Извлекаем текст после команды
            for word in ["напечатай", "введи", "напиши"]:
                if word in command_text:
                    text_to_type = command_text.split(word, 1)[-1].strip()
                    return {
                        "command_type": CommandType.TEXT_INPUT.value,
                        "action": "type",
                        "target": text_to_type or "текст",
                        "parameters": {},
                        "confidence": 0.4,
                        "original_text": command_text,
                        "parsed_by": "fallback"
                    }
        
        elif any(word in command_text for word in ["скриншот", "снимок"]):
            return {
                "command_type": CommandType.SCREENSHOT.value,
                "action": "take",
                "target": "screen",
                "parameters": {},
                "confidence": 0.6,
                "original_text": command_text,
                "parsed_by": "fallback"
            }
        
        elif any(word in command_text for word in ["помощь", "справка", "help"]):
            return {
                "command_type": CommandType.HELP.value,
                "action": "help",
                "target": "commands",
                "parameters": {},
                "confidence": 0.8,
                "original_text": command_text,
                "parsed_by": "fallback"
            }
        
        # Неизвестная команда
        return self._create_error_result(f"Не удалось распознать команду: {command_text}")
    
    def _create_error_result(self, error_message: str) -> Dict[str, Any]:
        """Создание результата с ошибкой"""
        
        return {
            "command_type": CommandType.UNKNOWN.value,
            "action": "error",
            "target": "",
            "parameters": {"error": error_message},
            "confidence": 0.0,
            "original_text": error_message,
            "parsed_by": "error"
        }
    
    def get_help(self) -> str:
        """Получение справки по командам"""
        
        help_text = """
🤖 Daur-AI - Справка по командам

📁 РАБОТА С ФАЙЛАМИ:
• создай файл <имя> - создать новый файл
• удали файл <имя> - удалить файл
• открой файл <имя> - открыть файл
• скопируй файл <имя> - скопировать файл

🚀 ПРИЛОЖЕНИЯ:
• открой браузер - запустить браузер
• открой терминал - запустить терминал
• открой блокнот - запустить текстовый редактор
• запусти калькулятор - запустить калькулятор

⌨️ ВВОД ТЕКСТА:
• напечатай <текст> - ввести текст
• введи <текст> - ввести текст
• напиши <текст> - ввести текст

🖱️ УПРАВЛЕНИЕ МЫШЬЮ:
• кликни <элемент> - кликнуть по элементу
• прокрути вверх/вниз - прокрутить страницу

📸 СКРИНШОТЫ:
• сделай скриншот - создать снимок экрана
• скриншот - создать снимок экрана

❓ СПРАВКА:
• помощь - показать эту справку
• справка - показать эту справку

Примеры:
• "создай файл test.txt"
• "открой браузер"
• "напечатай привет мир"
• "сделай скриншот"
        """
        
        return help_text.strip()


def create_enhanced_parser(ai_manager=None):
    """Фабричная функция для создания улучшенного парсера"""
    return EnhancedCommandParser(ai_manager)
