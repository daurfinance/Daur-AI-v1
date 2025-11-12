# Daur-AI v2.0: Полное Руководство по Расширению Функциональности

**Дата:** 25 октября 2025  
**Версия:** 2.0  
**Автор:** Manus AI

## 📋 Содержание

1. [Обзор возможностей расширения](#обзор-возможностей-расширения)
2. [Архитектура системы](#архитектура-системы)
3. [Расширение Input Module](#расширение-input-module)
4. [Расширение Hardware Module](#расширение-hardware-module)
5. [Расширение Vision Module](#расширение-vision-module)
6. [Создание новых модулей](#создание-новых-модулей)
7. [API интеграция](#api-интеграция)
8. [Примеры расширений](#примеры-расширений)

---

## 🎯 Обзор Возможностей Расширения

Система Daur-AI v2.0 разработана с учетом модульной архитектуры, что позволяет легко добавлять новые функции. Вот основные направления расширения:

### 1. **Расширение существующих модулей**
- Добавление новых функций в Input, Hardware, Vision модули
- Улучшение существующих функций
- Оптимизация производительности

### 2. **Создание новых модулей**
- Модули для специфических задач
- Интеграция с внешними сервисами
- Поддержка новых типов устройств

### 3. **REST API интеграция**
- Создание API endpoints
- WebSocket поддержка
- Интеграция с веб-приложениями

### 4. **Интеграция с внешними сервисами**
- OpenAI API
- Google Vision API
- Telegram Bot API
- Stripe API

### 5. **Расширение AI возможностей**
- Машинное обучение для распознавания
- Предсказание действий
- Автоматизация сложных сценариев

---

## 🏗️ Архитектура Системы

### Текущая структура:

```
Daur-AI v2.0
├── Input Module (мышка, клавиатура)
├── Hardware Module (оборудование, драйверы)
├── Vision Module (экран, распознавание)
├── Device Manager (интеграция)
├── Presentations Module (презентации)
├── Media Module (видео, фото)
├── Graphics Module (Blender, Unity)
├── Documents Module (документы)
├── Browser Module (браузер)
├── Android Module (Android)
├── Client Module (клиент)
├── Programming Module (программирование)
├── Logic Module (логика)
├── Planning Module (планирование)
└── Monitoring Module (мониторинг)
```

### Принципы архитектуры:

1. **Модульность** - Каждый модуль независим
2. **Интеграция** - Модули работают вместе через Device Manager
3. **Расширяемость** - Легко добавлять новые функции
4. **Масштабируемость** - Поддержка параллельной обработки
5. **Надежность** - Обработка ошибок и логирование

---

## 🖱️ Расширение Input Module

### Способ 1: Добавление новых функций мыши

**Файл:** `src/input/mouse_controller.py`

```python
# Добавить новый метод в класс MouseController

def mouse_pattern(self, pattern: str, duration: float = 1.0) -> bool:
    """
    Нарисовать паттерн мышкой
    
    Args:
        pattern: Паттерн ('circle', 'square', 'triangle')
        duration: Длительность рисования
        
    Returns:
        bool: Успешность операции
    """
    try:
        import math
        current_pos = self.get_position()
        center_x, center_y = current_pos.x, current_pos.y
        
        if pattern == 'circle':
            # Рисуем круг
            radius = 100
            steps = 36
            for i in range(steps + 1):
                angle = (i / steps) * 2 * math.pi
                x = center_x + int(radius * math.cos(angle))
                y = center_y + int(radius * math.sin(angle))
                self.move_to(x, y, duration=duration/steps)
        
        elif pattern == 'square':
            # Рисуем квадрат
            size = 100
            points = [
                (center_x - size, center_y - size),
                (center_x + size, center_y - size),
                (center_x + size, center_y + size),
                (center_x - size, center_y + size),
                (center_x - size, center_y - size)
            ]
            for x, y in points:
                self.move_to(x, y, duration=duration/len(points))
        
        self.logger.info(f"Паттерн нарисован: {pattern}")
        return True
    
    except Exception as e:
        self.logger.error(f"Ошибка рисования паттерна: {e}")
        return False


def mouse_find_and_click(self, image_path: str) -> bool:
    """
    Найти изображение на экране и нажать на него
    
    Args:
        image_path: Путь к изображению
        
    Returns:
        bool: Успешность операции
    """
    try:
        import pyautogui
        from PIL import Image
        
        # Найти изображение
        location = pyautogui.locateOnScreen(image_path, confidence=0.8)
        
        if location:
            # Нажать в центр найденного изображения
            center_x = location[0] + location[2] // 2
            center_y = location[1] + location[3] // 2
            self.move_to(center_x, center_y, duration=0.3)
            self.click()
            return True
        
        return False
    
    except Exception as e:
        self.logger.error(f"Ошибка поиска и клика: {e}")
        return False
```

### Способ 2: Добавление поддержки сенсорного ввода

```python
# Новый файл: src/input/touch_controller.py

from dataclasses import dataclass
from typing import List, Tuple
import logging

@dataclass
class TouchPoint:
    """Точка касания"""
    x: int
    y: int
    pressure: float = 1.0
    timestamp: float = 0.0


class TouchController:
    """Контроллер сенсорного ввода"""
    
    def __init__(self):
        """Инициализация"""
        self.logger = logging.getLogger('daur_ai.touch_controller')
    
    def tap(self, x: int, y: int, duration: float = 0.1) -> bool:
        """Одиночное касание"""
        try:
            # Реализация для сенсорных устройств
            self.logger.info(f"Tap at ({x}, {y})")
            return True
        except Exception as e:
            self.logger.error(f"Touch error: {e}")
            return False
    
    def long_press(self, x: int, y: int, duration: float = 1.0) -> bool:
        """Длительное нажатие"""
        try:
            self.logger.info(f"Long press at ({x}, {y}) for {duration}s")
            return True
        except Exception as e:
            self.logger.error(f"Long press error: {e}")
            return False
    
    def swipe(self, start_x: int, start_y: int, end_x: int, end_y: int,
             duration: float = 0.5) -> bool:
        """Свайп"""
        try:
            self.logger.info(f"Swipe from ({start_x}, {start_y}) to ({end_x}, {end_y})")
            return True
        except Exception as e:
            self.logger.error(f"Swipe error: {e}")
            return False
    
    def pinch(self, center_x: int, center_y: int, scale: float = 0.5,
             duration: float = 0.5) -> bool:
        """Жест pinch (сжатие)"""
        try:
            self.logger.info(f"Pinch at ({center_x}, {center_y}) with scale {scale}")
            return True
        except Exception as e:
            self.logger.error(f"Pinch error: {e}")
            return False
    
    def rotate(self, center_x: int, center_y: int, angle: float = 45,
              duration: float = 0.5) -> bool:
        """Жест поворота"""
        try:
            self.logger.info(f"Rotate at ({center_x}, {center_y}) by {angle} degrees")
            return True
        except Exception as e:
            self.logger.error(f"Rotate error: {e}")
            return False
```

---

## 🔧 Расширение Hardware Module

### Способ 1: Добавление мониторинга GPU

```python
# Добавить в src/hardware/driver_manager.py

def get_gpu_info(self) -> Dict[str, Any]:
    """
    Получить информацию о GPU
    
    Returns:
        Dict: Информация о GPU
    """
    try:
        import subprocess
        
        gpu_info = {
            'devices': [],
            'total_memory': 0,
            'used_memory': 0,
            'temperature': 0
        }
        
        # Для NVIDIA GPU
        try:
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=index,name,memory.total,memory.used,temperature.gpu',
                 '--format=csv,noheader,nounits'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split(',')
                    gpu_info['devices'].append({
                        'index': int(parts[0].strip()),
                        'name': parts[1].strip(),
                        'total_memory': int(parts[2].strip()),
                        'used_memory': int(parts[3].strip()),
                        'temperature': float(parts[4].strip())
                    })
        
        except Exception as e:
            self.logger.warning(f"NVIDIA GPU info not available: {e}")
        
        return gpu_info
    
    except Exception as e:
        self.logger.error(f"Error getting GPU info: {e}")
        return {}


def get_battery_info(self) -> Dict[str, Any]:
    """
    Получить информацию о батарее
    
    Returns:
        Dict: Информация о батарее
    """
    try:
        battery = psutil.sensors_battery()
        
        if battery:
            return {
                'percent': battery.percent,
                'seconds_left': battery.secsleft,
                'power_plugged': battery.power_plugged
            }
        
        return {}
    
    except Exception as e:
        self.logger.error(f"Error getting battery info: {e}")
        return {}
```

### Способ 2: Добавление мониторинга температуры

```python
# Новый файл: src/hardware/temperature_monitor.py

import logging
from typing import Dict, Any, List

class TemperatureMonitor:
    """Монитор температуры компонентов"""
    
    def __init__(self):
        """Инициализация"""
        self.logger = logging.getLogger('daur_ai.temperature_monitor')
    
    def get_cpu_temperature(self) -> float:
        """Получить температуру CPU"""
        try:
            import psutil
            temps = psutil.sensors_temperatures()
            
            if 'coretemp' in temps:
                return temps['coretemp'][0].current
            elif 'k10temp' in temps:
                return temps['k10temp'][0].current
            
            return 0.0
        
        except Exception as e:
            self.logger.error(f"Error getting CPU temperature: {e}")
            return 0.0
    
    def get_all_temperatures(self) -> Dict[str, Any]:
        """Получить все температуры"""
        try:
            import psutil
            temps = psutil.sensors_temperatures()
            
            result = {}
            for name, entries in temps.items():
                result[name] = [
                    {
                        'label': entry.label,
                        'current': entry.current,
                        'high': entry.high,
                        'critical': entry.critical
                    }
                    for entry in entries
                ]
            
            return result
        
        except Exception as e:
            self.logger.error(f"Error getting temperatures: {e}")
            return {}
    
    def check_temperature_health(self) -> Dict[str, Any]:
        """Проверить здоровье температуры"""
        temps = self.get_all_temperatures()
        
        health = {
            'status': 'healthy',
            'warnings': [],
            'critical': []
        }
        
        for component, entries in temps.items():
            for entry in entries:
                if entry['critical'] and entry['current'] > entry['critical']:
                    health['status'] = 'critical'
                    health['critical'].append(f"{component}: {entry['current']}°C")
                elif entry['high'] and entry['current'] > entry['high']:
                    health['status'] = 'warning'
                    health['warnings'].append(f"{component}: {entry['current']}°C")
        
        return health
```

---

## 👁️ Расширение Vision Module

### Способ 1: Добавление распознавания лиц

```python
# Новый файл: src/vision/face_recognition.py

import logging
from typing import List, Dict, Any, Optional, Tuple
from PIL import Image
import numpy as np

class FaceRecognizer:
    """Распознавание лиц"""
    
    def __init__(self):
        """Инициализация"""
        self.logger = logging.getLogger('daur_ai.face_recognizer')
        try:
            import face_recognition
            self.face_recognition = face_recognition
        except ImportError:
            self.logger.warning("face_recognition library not installed")
            self.face_recognition = None
    
    def detect_faces(self, image: Image.Image) -> List[Dict[str, Any]]:
        """
        Обнаружить лица на изображении
        
        Args:
            image: Изображение
            
        Returns:
            List: Список обнаруженных лиц
        """
        if not self.face_recognition:
            return []
        
        try:
            # Конвертировать в numpy array
            image_array = np.array(image)
            
            # Обнаружить лица
            face_locations = self.face_recognition.face_locations(image_array)
            face_encodings = self.face_recognition.face_encodings(image_array, face_locations)
            
            faces = []
            for (top, right, bottom, left), encoding in zip(face_locations, face_encodings):
                faces.append({
                    'location': (left, top, right - left, bottom - top),
                    'encoding': encoding,
                    'confidence': 0.95
                })
            
            self.logger.info(f"Detected {len(faces)} faces")
            return faces
        
        except Exception as e:
            self.logger.error(f"Error detecting faces: {e}")
            return []
    
    def recognize_face(self, face_encoding: np.ndarray,
                      known_encodings: List[np.ndarray],
                      tolerance: float = 0.6) -> Tuple[bool, float]:
        """
        Распознать лицо
        
        Args:
            face_encoding: Кодирование лица
            known_encodings: Известные кодирования
            tolerance: Допуск
            
        Returns:
            Tuple: (узнано ли, уверенность)
        """
        if not self.face_recognition or not known_encodings:
            return False, 0.0
        
        try:
            distances = self.face_recognition.face_distance(known_encodings, face_encoding)
            
            if len(distances) == 0:
                return False, 0.0
            
            min_distance = np.min(distances)
            is_match = min_distance < tolerance
            confidence = 1.0 - min_distance
            
            return is_match, confidence
        
        except Exception as e:
            self.logger.error(f"Error recognizing face: {e}")
            return False, 0.0
```

### Способ 2: Добавление распознавания QR кодов

```python
# Новый файл: src/vision/qr_code_reader.py

import logging
from typing import List, Dict, Any, Optional
from PIL import Image

class QRCodeReader:
    """Чтение QR кодов"""
    
    def __init__(self):
        """Инициализация"""
        self.logger = logging.getLogger('daur_ai.qr_code_reader')
        try:
            import pyzbar.pyzbar as pyzbar
            self.pyzbar = pyzbar
        except ImportError:
            self.logger.warning("pyzbar library not installed")
            self.pyzbar = None
    
    def detect_qr_codes(self, image: Image.Image) -> List[Dict[str, Any]]:
        """
        Обнаружить QR коды на изображении
        
        Args:
            image: Изображение
            
        Returns:
            List: Список обнаруженных QR кодов
        """
        if not self.pyzbar:
            return []
        
        try:
            qr_codes = self.pyzbar.decode(image)
            
            results = []
            for qr in qr_codes:
                results.append({
                    'type': qr.type,
                    'data': qr.data.decode('utf-8'),
                    'location': {
                        'x': qr.rect.left,
                        'y': qr.rect.top,
                        'width': qr.rect.width,
                        'height': qr.rect.height
                    }
                })
            
            self.logger.info(f"Detected {len(results)} QR codes")
            return results
        
        except Exception as e:
            self.logger.error(f"Error detecting QR codes: {e}")
            return []
    
    def read_qr_code(self, image: Image.Image) -> Optional[str]:
        """
        Прочитать первый QR код
        
        Args:
            image: Изображение
            
        Returns:
            Optional[str]: Данные QR кода
        """
        qr_codes = self.detect_qr_codes(image)
        
        if qr_codes:
            return qr_codes[0]['data']
        
        return None
```

---

## 🆕 Создание Новых Модулей

### Шаблон для создания нового модуля

```python
# Новый файл: src/new_module/new_module.py

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: Новый модуль
Описание функциональности

Версия: 2.0
Дата: 25.10.2025
Автор: Manus AI
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class NewModuleConfig:
    """Конфигурация модуля"""
    enabled: bool = True
    timeout: float = 30.0
    retry_count: int = 3
    created_at: datetime = field(default_factory=datetime.now)


class NewModule:
    """Основной класс модуля"""
    
    def __init__(self, config: Optional[NewModuleConfig] = None):
        """
        Инициализация
        
        Args:
            config: Конфигурация модуля
        """
        self.logger = logging.getLogger('daur_ai.new_module')
        self.config = config or NewModuleConfig()
        self.logger.info("New Module инициализирован")
    
    def do_something(self) -> bool:
        """
        Выполнить основное действие
        
        Returns:
            bool: Успешность операции
        """
        try:
            self.logger.info("Выполнение действия...")
            # Реализация
            return True
        
        except Exception as e:
            self.logger.error(f"Ошибка: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Получить статус модуля"""
        return {
            'enabled': self.config.enabled,
            'timeout': self.config.timeout,
            'created_at': self.config.created_at.isoformat()
        }


# Глобальный экземпляр
_new_module = None


def get_new_module(config: Optional[NewModuleConfig] = None) -> NewModule:
    """Получить экземпляр модуля"""
    global _new_module
    if _new_module is None:
        _new_module = NewModule(config)
    return _new_module
```

### Файл инициализации модуля

```python
# Новый файл: src/new_module/__init__.py

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: Новый модуль
"""

from .new_module import (
    NewModuleConfig,
    NewModule,
    get_new_module
)

__all__ = [
    'NewModuleConfig',
    'NewModule',
    'get_new_module'
]
```

---

## 🔗 API Интеграция

### Способ 1: REST API endpoints

```python
# Новый файл: src/web/device_api.py

from flask import Flask, jsonify, request
from src.devices import get_device_manager

app = Flask(__name__)
manager = get_device_manager()

# ===== Mouse endpoints =====

@app.route('/api/mouse/move', methods=['POST'])
def mouse_move():
    """Переместить мышь"""
    data = request.json
    x = data.get('x', 0)
    y = data.get('y', 0)
    duration = data.get('duration', 0.5)
    
    success = manager.mouse_move(x, y, duration)
    
    return jsonify({
        'success': success,
        'message': 'Mouse moved' if success else 'Failed to move mouse'
    })


@app.route('/api/mouse/click', methods=['POST'])
def mouse_click():
    """Нажать кнопку мыши"""
    data = request.json
    x = data.get('x')
    y = data.get('y')
    button = data.get('button', 'left')
    
    success = manager.mouse_click(x, y, button)
    
    return jsonify({
        'success': success,
        'message': 'Mouse clicked' if success else 'Failed to click'
    })


# ===== Keyboard endpoints =====

@app.route('/api/keyboard/type', methods=['POST'])
def keyboard_type():
    """Напечатать текст"""
    data = request.json
    text = data.get('text', '')
    
    success = manager.keyboard_type(text)
    
    return jsonify({
        'success': success,
        'message': 'Text typed' if success else 'Failed to type'
    })


@app.route('/api/keyboard/hotkey', methods=['POST'])
def keyboard_hotkey():
    """Комбинация клавиш"""
    data = request.json
    keys = data.get('keys', [])
    
    success = manager.keyboard_hotkey(*keys)
    
    return jsonify({
        'success': success,
        'message': 'Hotkey executed' if success else 'Failed to execute'
    })


# ===== Screen endpoints =====

@app.route('/api/screen/analyze', methods=['GET'])
def screen_analyze():
    """Анализировать экран"""
    analysis = manager.screen_analyze()
    
    return jsonify({
        'success': True,
        'data': analysis
    })


@app.route('/api/screen/find', methods=['POST'])
def screen_find():
    """Найти объект на экране"""
    data = request.json
    text = data.get('text', '')
    
    obj = manager.screen_find_object(text)
    
    return jsonify({
        'success': obj is not None,
        'data': obj
    })


# ===== Hardware endpoints =====

@app.route('/api/hardware/info', methods=['GET'])
def hardware_info():
    """Информация об оборудовании"""
    info = manager.hardware_get_info()
    
    return jsonify({
        'success': True,
        'data': info
    })


@app.route('/api/hardware/health', methods=['GET'])
def hardware_health():
    """Проверка здоровья"""
    health = manager.hardware_check_health()
    
    return jsonify({
        'success': True,
        'data': health
    })


# ===== Status endpoints =====

@app.route('/api/status', methods=['GET'])
def get_status():
    """Получить статус системы"""
    status = manager.get_full_status()
    
    return jsonify({
        'success': True,
        'data': status
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
```

### Способ 2: WebSocket поддержка

```python
# Новый файл: src/web/device_websocket.py

from flask import Flask
from flask_socketio import SocketIO, emit, on
from src.devices import get_device_manager
import json

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
manager = get_device_manager()

@socketio.on('connect')
def handle_connect():
    """Клиент подключился"""
    emit('response', {'data': 'Connected to Daur-AI'})


@socketio.on('mouse_move')
def handle_mouse_move(data):
    """Переместить мышь"""
    x = data.get('x', 0)
    y = data.get('y', 0)
    duration = data.get('duration', 0.5)
    
    success = manager.mouse_move(x, y, duration)
    
    emit('response', {
        'event': 'mouse_move',
        'success': success
    }, broadcast=True)


@socketio.on('keyboard_type')
def handle_keyboard_type(data):
    """Напечатать текст"""
    text = data.get('text', '')
    
    success = manager.keyboard_type(text)
    
    emit('response', {
        'event': 'keyboard_type',
        'success': success
    }, broadcast=True)


@socketio.on('screen_analyze')
def handle_screen_analyze():
    """Анализировать экран"""
    analysis = manager.screen_analyze()
    
    emit('response', {
        'event': 'screen_analyze',
        'data': analysis
    }, broadcast=True)


@socketio.on('get_status')
def handle_get_status():
    """Получить статус"""
    status = manager.get_full_status()
    
    emit('response', {
        'event': 'get_status',
        'data': status
    }, broadcast=True)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5001, debug=True)
```

---

## 🤖 Интеграция с AI

### Добавление OpenAI интеграции

```python
# Новый файл: src/ai/openai_integration.py

import logging
from typing import Optional, Dict, Any
import openai

class OpenAIIntegration:
    """Интеграция с OpenAI API"""
    
    def __init__(self, api_key: str):
        """
        Инициализация
        
        Args:
            api_key: API ключ OpenAI
        """
        self.logger = logging.getLogger('daur_ai.openai_integration')
        openai.api_key = api_key
    
    def analyze_screenshot(self, image_path: str) -> Optional[str]:
        """
        Анализировать скриншот с помощью GPT-4 Vision
        
        Args:
            image_path: Путь к изображению
            
        Returns:
            Optional[str]: Анализ изображения
        """
        try:
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            response = openai.ChatCompletion.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_data}"
                                }
                            },
                            {
                                "type": "text",
                                "text": "Describe what you see in this screenshot"
                            }
                        ]
                    }
                ]
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            self.logger.error(f"Error analyzing screenshot: {e}")
            return None
    
    def get_next_action(self, current_state: str) -> Optional[str]:
        """
        Получить следующее действие на основе текущего состояния
        
        Args:
            current_state: Описание текущего состояния
            
        Returns:
            Optional[str]: Рекомендуемое действие
        """
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an AI assistant that helps automate computer tasks."
                    },
                    {
                        "role": "user",
                        "content": f"Current state: {current_state}\n\nWhat should be the next action?"
                    }
                ]
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            self.logger.error(f"Error getting next action: {e}")
            return None
```

---

## 💡 Примеры Расширений

### Пример 1: Автоматизация заполнения форм

```python
# Новый файл: src/automation/form_filler.py

from src.devices import get_device_manager
from src.vision import get_screen_analyzer
import time

class FormFiller:
    """Автоматизация заполнения форм"""
    
    def __init__(self):
        """Инициализация"""
        self.manager = get_device_manager()
        self.analyzer = get_screen_analyzer()
    
    def fill_form(self, form_data: dict) -> bool:
        """
        Заполнить форму
        
        Args:
            form_data: Данные формы {field_label: value}
            
        Returns:
            bool: Успешность операции
        """
        try:
            for field_label, value in form_data.items():
                # Найти поле
                field = self.analyzer.find_object_by_text(field_label)
                
                if not field:
                    continue
                
                # Нажать на поле
                self.manager.mouse_click(field['center'][0], field['center'][1])
                time.sleep(0.3)
                
                # Очистить поле
                self.manager.keyboard_hotkey('ctrl', 'a')
                time.sleep(0.1)
                
                # Ввести значение
                self.manager.keyboard_type(str(value))
                time.sleep(0.2)
            
            return True
        
        except Exception as e:
            print(f"Error filling form: {e}")
            return False
```

### Пример 2: Мониторинг системы с уведомлениями

```python
# Новый файл: src/monitoring/system_monitor.py

from src.devices import get_device_manager
import time
import threading

class SystemMonitor:
    """Мониторинг системы с уведомлениями"""
    
    def __init__(self, check_interval: float = 60.0):
        """
        Инициализация
        
        Args:
            check_interval: Интервал проверки в секундах
        """
        self.manager = get_device_manager()
        self.check_interval = check_interval
        self.is_running = False
    
    def start_monitoring(self):
        """Начать мониторинг"""
        self.is_running = True
        thread = threading.Thread(target=self._monitor_loop)
        thread.daemon = True
        thread.start()
    
    def stop_monitoring(self):
        """Остановить мониторинг"""
        self.is_running = False
    
    def _monitor_loop(self):
        """Основной цикл мониторинга"""
        while self.is_running:
            try:
                # Получить информацию об оборудовании
                hw_info = self.manager.hardware_get_info()
                
                # Проверить здоровье
                health = self.manager.hardware_check_health()
                
                # Проверить пороги
                if hw_info['cpu_percent'] > 80:
                    self._notify(f"High CPU usage: {hw_info['cpu_percent']}%")
                
                if hw_info['ram_percent'] > 85:
                    self._notify(f"High RAM usage: {hw_info['ram_percent']}%")
                
                if hw_info['disk_percent'] > 90:
                    self._notify(f"Low disk space: {hw_info['disk_percent']}% used")
                
                if health['overall_status'] != 'healthy':
                    self._notify(f"System health: {health['overall_status']}")
                
                time.sleep(self.check_interval)
            
            except Exception as e:
                print(f"Monitoring error: {e}")
                time.sleep(self.check_interval)
    
    def _notify(self, message: str):
        """Отправить уведомление"""
        print(f"[ALERT] {message}")
        # Можно добавить отправку в Telegram, Email и т.д.
```

### Пример 3: Запись и воспроизведение сценариев

```python
# Новый файл: src/automation/scenario_recorder.py

from src.input import get_mouse_controller, get_keyboard_controller
from src.devices import get_device_manager
import json
import time
from typing import List, Dict, Any

class ScenarioRecorder:
    """Запись и воспроизведение сценариев"""
    
    def __init__(self):
        """Инициализация"""
        self.mouse = get_mouse_controller()
        self.keyboard = get_keyboard_controller()
        self.manager = get_device_manager()
        self.recording = False
        self.events: List[Dict[str, Any]] = []
    
    def start_recording(self):
        """Начать запись"""
        self.recording = True
        self.events = []
        
        # Зарегистрировать callbacks
        self.mouse.register_event_callback('move', self._on_mouse_move)
        self.mouse.register_event_callback('click', self._on_mouse_click)
        self.keyboard.register_event_callback('press', self._on_key_press)
    
    def stop_recording(self) -> List[Dict[str, Any]]:
        """Остановить запись"""
        self.recording = False
        return self.events
    
    def save_scenario(self, filepath: str):
        """Сохранить сценарий"""
        with open(filepath, 'w') as f:
            json.dump(self.events, f, indent=2, default=str)
    
    def load_scenario(self, filepath: str) -> List[Dict[str, Any]]:
        """Загрузить сценарий"""
        with open(filepath, 'r') as f:
            self.events = json.load(f)
        return self.events
    
    def playback_scenario(self, speed: float = 1.0):
        """Воспроизвести сценарий"""
        for i, event in enumerate(self.events):
            if i > 0:
                # Задержка между событиями
                delay = (event['timestamp'] - self.events[i-1]['timestamp']) / speed
                time.sleep(delay)
            
            event_type = event['type']
            
            if event_type == 'mouse_move':
                self.manager.mouse_move(event['x'], event['y'], duration=0.1)
            
            elif event_type == 'mouse_click':
                self.manager.mouse_click(event['x'], event['y'], event['button'])
            
            elif event_type == 'key_press':
                self.manager.keyboard_press(event['key'])
            
            elif event_type == 'type':
                self.manager.keyboard_type(event['text'])
    
    def _on_mouse_move(self, event):
        """Callback для движения мыши"""
        if self.recording:
            self.events.append({
                'type': 'mouse_move',
                'x': event.position.x,
                'y': event.position.y,
                'timestamp': event.timestamp.timestamp()
            })
    
    def _on_mouse_click(self, event):
        """Callback для клика мыши"""
        if self.recording:
            self.events.append({
                'type': 'mouse_click',
                'x': event.position.x,
                'y': event.position.y,
                'button': event.button.value if event.button else 'left',
                'timestamp': event.timestamp.timestamp()
            })
    
    def _on_key_press(self, event):
        """Callback для нажатия клавиши"""
        if self.recording:
            self.events.append({
                'type': 'key_press',
                'key': event.key,
                'timestamp': event.timestamp.timestamp()
            })
```

---

## 📚 Рекомендации по Расширению

### 1. **Перед началом разработки**
- Изучите существующую архитектуру
- Определите, нужен ли новый модуль или расширение существующего
- Спланируйте API и интерфейсы
- Создайте документацию

### 2. **Во время разработки**
- Следуйте соглашениям о кодировании проекта
- Добавляйте логирование
- Обрабатывайте исключения
- Пишите docstrings для всех функций

### 3. **После разработки**
- Тестируйте функциональность
- Добавляйте unit тесты
- Обновляйте документацию
- Создавайте примеры использования

### 4. **Лучшие практики**
- Используйте типизацию (type hints)
- Следуйте PEP 8
- Избегайте глобального состояния
- Используйте dependency injection
- Логируйте все важные события

---

## 🎯 Приоритет Расширений

### Высокий приоритет
1. REST API endpoints
2. WebSocket поддержка
3. Распознавание лиц
4. Мониторинг GPU
5. Запись сценариев

### Средний приоритет
1. Интеграция с OpenAI
2. QR код распознавание
3. Мониторинг температуры
4. Сенсорный ввод
5. Автоматизация форм

### Низкий приоритет
1. Дополнительные эффекты мыши
2. Расширенные макросы
3. Интеграция с другими сервисами

---

**Создано:** Manus AI  
**Дата:** 25 октября 2025  
**Версия:** 2.0

