# Daur-AI v2.0: Модули Управления Устройствами

**Дата:** 25 октября 2025  
**Версия:** 2.0  
**Автор:** Manus AI

## 📋 Содержание

1. [Обзор](#обзор)
2. [Модули](#модули)
3. [Быстрый Старт](#быстрый-старт)
4. [API Документация](#api-документация)
5. [Примеры Использования](#примеры-использования)

---

## 🎯 Обзор

Система управления устройствами Daur-AI v2.0 предоставляет полный контроль над компьютером и его устройствами. Система состоит из четырех основных модулей:

1. **Input Module** - Управление мышкой и клавиатурой
2. **Hardware Module** - Управление оборудованием и драйверами
3. **Vision Module** - Экранное распознавание и компьютерное зрение
4. **Device Manager** - Интегрированное управление всеми устройствами

---

## 📦 Модули

### 1. Input Module (Управление вводом)

#### Mouse Controller (Контроллер мыши)

Полный контроль над мышкой с поддержкой жестов и записи.

**Основные функции:**
- Перемещение мыши
- Нажатие кнопок (левая, правая, средняя)
- Прокрутка колесика
- Перетаскивание элементов
- Запись и воспроизведение жестов

**Класс:** `MouseController`

```python
from src.input import get_mouse_controller

mouse = get_mouse_controller()

# Переместить мышь
mouse.move_to(100, 200, duration=0.5)

# Нажать левую кнопку
mouse.click(MouseButton.LEFT)

# Перетащить
mouse.drag(100, 100, 200, 200, duration=0.5)

# Прокрутить
mouse.scroll(500, 500, clicks=3, direction='down')

# Записать жест
gesture = mouse.record_gesture("my_gesture", duration=5.0)

# Воспроизвести жест
mouse.playback_gesture("my_gesture")
```

#### Keyboard Controller (Контроллер клавиатуры)

Полный контроль над клавиатурой с поддержкой макросов и горячих клавиш.

**Основные функции:**
- Нажатие отдельных клавиш
- Печать текста
- Комбинации клавиш (Ctrl+C, Alt+Tab и т.д.)
- Регистрация горячих клавиш
- Создание и выполнение макросов

**Класс:** `KeyboardController`

```python
from src.input import get_keyboard_controller

keyboard = get_keyboard_controller()

# Нажать клавишу
keyboard.press_key('enter')

# Напечатать текст
keyboard.type_text("Hello, World!", interval=0.05)

# Комбинация клавиш
keyboard.hotkey('ctrl', 'c')

# Зарегистрировать горячую клавишу
keyboard.register_hotkey('copy', 'ctrl+c', lambda: print("Copied!"))

# Создать макрос
macro = keyboard.create_macro('my_macro', 'My Macro')
keyboard.add_key_to_macro('my_macro', 'a', delay=0.1)
keyboard.add_key_to_macro('my_macro', 'b', delay=0.1)

# Выполнить макрос
keyboard.execute_macro('my_macro', repeat=1)
```

---

### 2. Hardware Module (Управление оборудованием)

#### Hardware Monitor (Монитор оборудования)

Мониторинг состояния оборудования и ресурсов системы.

**Основные функции:**
- Информация о CPU
- Информация о памяти
- Информация о дисках
- Информация о сети
- Информация о процессах

**Класс:** `HardwareMonitor`

```python
from src.hardware import get_hardware_monitor

monitor = get_hardware_monitor()

# Информация о CPU
cpu_info = monitor.get_cpu_info()
print(f"CPU: {cpu_info['percent']}%")

# Информация о памяти
mem_info = monitor.get_memory_info()
print(f"RAM: {mem_info['percent']}%")

# Информация о диске
disk_info = monitor.get_disk_info()
print(f"Disk: {disk_info['percent']}%")

# Информация о сети
net_info = monitor.get_network_info()
print(f"Interfaces: {net_info['interfaces']}")

# Информация о процессах
processes = monitor.get_process_info()
for p in processes[:5]:
    print(f"{p['name']}: {p['cpu_percent']}% CPU")

# Полная информация об оборудовании
hw_info = monitor.get_hardware_info()
```

#### Driver Manager (Менеджер драйверов)

Управление устройствами и драйверами.

**Основные функции:**
- Обнаружение устройств
- Установка драйверов
- Обновление драйверов
- Проверка здоровья устройств

**Класс:** `DriverManager`

```python
from src.hardware import get_driver_manager

manager = get_driver_manager()

# Обнаружить устройства
devices = manager.detect_devices()
for device in devices:
    print(f"{device.name}: {device.device_type.value}")

# Установить драйвер
manager.install_driver('gpu_driver', 'NVIDIA Driver', DeviceType.GPU, '525.0')

# Обновить драйвер
manager.update_driver('gpu_driver', '530.0')

# Проверить здоровье
health = manager.check_device_health()
print(f"Overall status: {health['overall_status']}")
```

---

### 3. Vision Module (Компьютерное зрение)

#### Screen Analyzer (Анализатор экрана)

Анализ экрана, распознавание объектов и OCR.

**Основные функции:**
- Захват экрана
- Анализ экрана
- Распознавание текста (OCR)
- Обнаружение объектов
- Поиск элементов на экране

**Класс:** `ScreenAnalyzer`

```python
from src.vision import get_screen_analyzer

analyzer = get_screen_analyzer()

# Захватить экран
screenshot = analyzer.screen_capture.capture_screen()

# Анализировать экран
analysis = analyzer.analyze_screen()
print(f"Objects found: {len(analysis.objects)}")
print(f"Text: {analysis.text_content}")

# Найти объект по тексту
obj = analyzer.find_object_by_text("Click here")
if obj:
    print(f"Found at: {obj.center}")

# Найти кнопку
button = analyzer.find_button("Submit")
if button:
    print(f"Button at: {button.center}")

# Ждать появления объекта
obj = analyzer.wait_for_object("Loading...", timeout=10.0)
```

---

### 4. Device Manager (Интегрированный менеджер)

#### Integrated Device Manager

Центральное управление всеми устройствами и компонентами.

**Основные функции:**
- Управление мышкой
- Управление клавиатурой
- Управление оборудованием
- Управление экраном
- Комбинированные операции

**Класс:** `IntegratedDeviceManager`

```python
from src.devices import get_device_manager

manager = get_device_manager()

# ===== Управление мышкой =====
manager.mouse_move(100, 200, duration=0.5)
manager.mouse_click(100, 200, button="left", clicks=1)
manager.mouse_drag(100, 100, 200, 200)
manager.mouse_scroll(500, 500, direction="down", clicks=3)

# ===== Управление клавиатурой =====
manager.keyboard_press('enter')
manager.keyboard_type("Hello, World!")
manager.keyboard_hotkey('ctrl', 'c')
manager.keyboard_register_hotkey('my_hotkey', 'ctrl+shift+x', callback)

# ===== Управление оборудованием =====
devices = manager.hardware_detect_devices()
hw_info = manager.hardware_get_info()
health = manager.hardware_check_health()

# ===== Управление экраном =====
screenshot = manager.screen_capture()
analysis = manager.screen_analyze()
obj = manager.screen_find_object("Click here")
button = manager.screen_find_button("Submit")

# ===== Комбинированные операции =====
manager.click_on_text("Click here")
manager.click_button("Submit")
manager.type_and_press_enter("password")

# ===== Статус и диагностика =====
status = manager.get_status()
full_status = manager.get_full_status()
health_check = manager.health_check()
```

---

## 🚀 Быстрый Старт

### Установка зависимостей

```bash
pip install pyautogui pillow numpy psutil pytesseract
```

### Базовый пример

```python
from src.devices import get_device_manager

# Получить менеджер
manager = get_device_manager()

# Найти и нажать кнопку
manager.click_button("Start")

# Напечатать текст
manager.keyboard_type("My input text")

# Нажать Enter
manager.keyboard_press('enter')

# Проверить статус
status = manager.get_status()
print(f"System healthy: {status.hardware_healthy}")
```

---

## 📚 API Документация

### MouseController

| Метод | Описание |
|-------|---------|
| `move_to(x, y, duration)` | Переместить мышь в позицию |
| `move_relative(dx, dy, duration)` | Переместить мышь относительно текущей позиции |
| `click(button, clicks, interval)` | Нажать кнопку мыши |
| `drag(start_x, start_y, end_x, end_y, duration, button)` | Перетащить мышь |
| `scroll(x, y, clicks, direction)` | Прокрутить колесико |
| `record_gesture(gesture_id, duration)` | Записать жест |
| `playback_gesture(gesture_id, speed)` | Воспроизвести жест |
| `save_gesture(gesture_id, filepath)` | Сохранить жест в файл |
| `load_gesture(gesture_id, filepath)` | Загрузить жест из файла |
| `get_position()` | Получить текущую позицию |
| `get_status()` | Получить статус |

### KeyboardController

| Метод | Описание |
|-------|---------|
| `press_key(key, duration)` | Нажать клавишу |
| `type_text(text, interval)` | Напечатать текст |
| `write_text(text, interval)` | Написать текст (Unicode) |
| `key_down(key)` | Нажать и держать клавишу |
| `key_up(key)` | Отпустить клавишу |
| `hotkey(*keys)` | Комбинация клавиш |
| `register_hotkey(id, combo, callback, desc)` | Зарегистрировать горячую клавишу |
| `unregister_hotkey(id)` | Отменить горячую клавишу |
| `create_macro(id, name, desc)` | Создать макрос |
| `add_key_to_macro(id, key, delay)` | Добавить клавишу в макрос |
| `execute_macro(id, repeat)` | Выполнить макрос |
| `record_macro(id, duration)` | Записать макрос |
| `get_status()` | Получить статус |

### HardwareMonitor

| Метод | Описание |
|-------|---------|
| `get_cpu_info()` | Информация о CPU |
| `get_memory_info()` | Информация о памяти |
| `get_disk_info(path)` | Информация о диске |
| `get_network_info()` | Информация о сети |
| `get_process_info(pid)` | Информация о процессах |
| `get_hardware_info()` | Полная информация об оборудовании |

### ScreenAnalyzer

| Метод | Описание |
|-------|---------|
| `analyze_screen()` | Анализировать текущий экран |
| `find_object_by_text(text, threshold)` | Найти объект по тексту |
| `find_button(text)` | Найти кнопку |
| `wait_for_object(text, timeout)` | Ждать появления объекта |
| `highlight_object(obj, screenshot)` | Выделить объект |

### IntegratedDeviceManager

| Метод | Описание |
|-------|---------|
| `mouse_move(x, y, duration)` | Переместить мышь |
| `mouse_click(x, y, button, clicks)` | Нажать кнопку мыши |
| `mouse_drag(start_x, start_y, end_x, end_y, duration)` | Перетащить мышь |
| `mouse_scroll(x, y, direction, clicks)` | Прокрутить |
| `keyboard_press(key)` | Нажать клавишу |
| `keyboard_type(text, interval)` | Напечатать текст |
| `keyboard_hotkey(*keys)` | Комбинация клавиш |
| `hardware_detect_devices()` | Обнаружить устройства |
| `hardware_get_info()` | Информация об оборудовании |
| `hardware_check_health()` | Проверить здоровье |
| `screen_capture()` | Захватить экран |
| `screen_analyze()` | Анализировать экран |
| `screen_find_object(text)` | Найти объект |
| `screen_find_button(text)` | Найти кнопку |
| `click_on_text(text, button)` | Найти и нажать на текст |
| `click_button(text)` | Найти и нажать кнопку |
| `type_and_press_enter(text)` | Напечатать и нажать Enter |
| `get_status()` | Получить статус |
| `get_full_status()` | Получить полный статус |
| `health_check()` | Проверка здоровья |

---

## 💡 Примеры Использования

### Пример 1: Автоматизация веб-браузера

```python
from src.devices import get_device_manager

manager = get_device_manager()

# Найти поле поиска и ввести текст
manager.click_on_text("Search")
manager.keyboard_type("daur ai")
manager.keyboard_press('enter')

# Ждать результатов
import time
time.sleep(2)

# Найти и нажать первый результат
manager.click_on_text("Daur AI Official")
```

### Пример 2: Мониторинг системы

```python
from src.devices import get_device_manager

manager = get_device_manager()

# Получить информацию об оборудовании
hw_info = manager.hardware_get_info()

print(f"CPU: {hw_info['cpu_percent']}%")
print(f"RAM: {hw_info['ram_percent']}%")
print(f"Disk: {hw_info['disk_percent']}%")

# Проверить здоровье
health = manager.hardware_check_health()
if health['overall_status'] != 'healthy':
    print("Warning: System health degraded!")
```

### Пример 3: Запись и воспроизведение жестов

```python
from src.input import get_mouse_controller

mouse = get_mouse_controller()

# Записать жест (5 секунд)
print("Recording gesture... Move your mouse!")
gesture = mouse.record_gesture("signature", duration=5.0)

# Воспроизвести жест
print("Playing back gesture...")
mouse.playback_gesture("signature", speed=1.0)

# Сохранить жест
mouse.save_gesture("signature", "/tmp/signature.json")

# Загрузить и воспроизвести
mouse.load_gesture("signature", "/tmp/signature.json")
mouse.playback_gesture("signature")
```

### Пример 4: Создание макроса

```python
from src.input import get_keyboard_controller

keyboard = get_keyboard_controller()

# Создать макрос для ввода пароля
macro = keyboard.create_macro('password_macro', 'Password Entry')
keyboard.add_key_to_macro('password_macro', 'shift+p', delay=0.1)
keyboard.add_key_to_macro('password_macro', 'a', delay=0.1)
keyboard.add_key_to_macro('password_macro', 's', delay=0.1)
keyboard.add_key_to_macro('password_macro', 's', delay=0.1)
keyboard.add_key_to_macro('password_macro', 'w', delay=0.1)
keyboard.add_key_to_macro('password_macro', 'o', delay=0.1)
keyboard.add_key_to_macro('password_macro', 'r', delay=0.1)
keyboard.add_key_to_macro('password_macro', 'd', delay=0.1)
keyboard.add_key_to_macro('password_macro', 'enter', delay=0.1)

# Выполнить макрос
keyboard.execute_macro('password_macro')
```

---

## 🔧 Конфигурация

### Логирование

```python
import logging

# Настроить логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Получить логгер
logger = logging.getLogger('daur_ai.device_manager')
```

### Обработка ошибок

```python
from src.devices import get_device_manager

manager = get_device_manager()

try:
    manager.click_button("Submit")
except Exception as e:
    print(f"Error: {e}")
    # Fallback действие
    manager.keyboard_press('enter')
```

---

## 📊 Статистика

| Компонент | Функций | Классов | Строк кода |
|-----------|---------|---------|-----------|
| Input Module | 25+ | 4 | ~800 |
| Hardware Module | 15+ | 3 | ~600 |
| Vision Module | 20+ | 4 | ~700 |
| Device Manager | 30+ | 2 | ~500 |
| **Всего** | **90+** | **13** | **~2600** |

---

## 🎓 Следующие Шаги

1. **Интеграция в API** - Добавить REST endpoints для управления устройствами
2. **Расширение функциональности** - Добавить поддержку новых типов устройств
3. **Оптимизация производительности** - Улучшить скорость анализа экрана
4. **Документация** - Создать подробные гайды для каждого модуля

---

**Создано:** Manus AI  
**Дата:** 25 октября 2025  
**Версия:** 2.0

