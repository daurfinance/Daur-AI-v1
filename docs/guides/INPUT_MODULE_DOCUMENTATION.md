# Input Module - Полная Документация

## Обзор

Input Module - это полнофункциональный модуль управления вводом для Daur-AI v2.0, который обеспечивает:

- **Управление мышкой** - движение, клики, прокрутка, перетаскивание
- **Управление клавиатурой** - печать текста, горячие клавиши, комбинации
- **Запись и воспроизведение** - сохранение и повторение жестов
- **История событий** - логирование всех операций
- **Слушатели событий** - callbacks для обработки событий в реальном времени

## Архитектура

### RealMouseController

Полнофункциональный контроллер мыши с поддержкой:

```python
from src.input.real_input_controller import RealMouseController

mouse = RealMouseController()

# Движение мыши
mouse.move_to(100, 200, duration=0.5)

# Клики
mouse.click(100, 200, button="left")
mouse.double_click(100, 200)
mouse.right_click(100, 200)

# Прокрутка
mouse.scroll(100, 200, direction="down", amount=3)

# Перетаскивание
mouse.drag(100, 200, 300, 400, duration=0.5)

# Получить позицию
pos = mouse.get_position()  # Returns (x, y)

# Запись жестов
mouse.start_recording()
# ... выполняем действия ...
events = mouse.stop_recording()

# Воспроизведение
mouse.playback_events(events, speed=1.0)

# Сохранение и загрузка
mouse.save_events("gestures.json")
loaded_events = mouse.load_events("gestures.json")

# История
history = mouse.get_history(limit=100)
mouse.clear_history()

# Слушатели
def on_event(event):
    print(f"Mouse event: {event.event_type} at ({event.x}, {event.y})")

mouse.add_listener(on_event)

# Очистка
mouse.cleanup()
```

### RealKeyboardController

Полнофункциональный контроллер клавиатуры с поддержкой:

```python
from src.input.real_input_controller import RealKeyboardController

keyboard = RealKeyboardController()

# Печать текста
keyboard.type_text("Hello, World!", interval=0.05)

# Нажатие клавиш
keyboard.press_key("enter")
keyboard.press_key("tab")
keyboard.press_key("escape")

# Горячие клавиши
keyboard.hotkey("ctrl", "c")  # Ctrl+C
keyboard.hotkey("alt", "tab")  # Alt+Tab
keyboard.hotkey("shift", "delete")  # Shift+Delete

# Запись нажатий
keyboard.start_recording()
# ... выполняем действия ...
events = keyboard.stop_recording()

# Воспроизведение
keyboard.playback_events(events, speed=1.0)

# Сохранение и загрузка
keyboard.save_events("keystrokes.json")
loaded_events = keyboard.load_events("keystrokes.json")

# История
history = keyboard.get_history(limit=100)
keyboard.clear_history()

# Слушатели
def on_key_event(event):
    print(f"Keyboard event: {event.event_type} - {event.key}")

keyboard.add_listener(on_key_event)

# Очистка
keyboard.cleanup()
```

### RealInputManager

Менеджер для управления обоими контроллерами:

```python
from src.input.real_input_controller import RealInputManager

manager = RealInputManager()

# Доступ к контроллерам
manager.mouse.move_to(100, 200)
manager.keyboard.type_text("Hello")

# Очистка
manager.cleanup()
```

## Структура Данных

### MouseEvent

```python
@dataclass
class MouseEvent:
    timestamp: str  # ISO format timestamp
    event_type: str  # "move", "click", "scroll", "drag"
    x: int  # X координата
    y: int  # Y координата
    button: Optional[str]  # "left", "right", "middle", "scroll_up", "scroll_down"
    duration: Optional[float]  # Длительность операции
```

### KeyboardEvent

```python
@dataclass
class KeyboardEvent:
    timestamp: str  # ISO format timestamp
    event_type: str  # "press", "release", "type", "hotkey"
    key: str  # Нажатая клавиша или текст
```

## Примеры Использования

### Пример 1: Автоматизация формы входа

```python
from src.input.real_input_controller import RealInputManager

manager = RealInputManager()

# Клик на поле email
manager.mouse.click(100, 50)
time.sleep(0.5)

# Печать email
manager.keyboard.type_text("user@example.com", interval=0.05)

# Клик на поле пароля
manager.mouse.click(100, 100)
time.sleep(0.5)

# Печать пароля
manager.keyboard.type_text("password123", interval=0.05)

# Нажать Enter
manager.keyboard.press_key("enter")

manager.cleanup()
```

### Пример 2: Запись и воспроизведение жестов

```python
from src.input.real_input_controller import RealMouseController

mouse = RealMouseController()

# Запись жестов
print("Recording... (5 seconds)")
mouse.start_recording()
time.sleep(5)
events = mouse.stop_recording()

# Сохранение
mouse.save_events("my_gestures.json")

# Позже: загрузка и воспроизведение
loaded_events = mouse.load_events("my_gestures.json")
mouse.playback_events(loaded_events, speed=1.0)

mouse.cleanup()
```

### Пример 3: Мониторинг событий

```python
from src.input.real_input_controller import RealMouseController, RealKeyboardController

mouse = RealMouseController()
keyboard = RealKeyboardController()

# Добавляем слушателей
def on_mouse_event(event):
    print(f"Mouse: {event.event_type} at ({event.x}, {event.y})")

def on_keyboard_event(event):
    print(f"Keyboard: {event.event_type} - {event.key}")

mouse.add_listener(on_mouse_event)
keyboard.add_listener(on_keyboard_event)

# Слушаем события в течение 10 секунд
time.sleep(10)

mouse.cleanup()
keyboard.cleanup()
```

## Требования

### Зависимости

```
pyautogui>=0.9.53
pynput>=1.7.6
```

### Установка

```bash
pip install pyautogui pynput
```

### Требования к ОС

- **macOS**: Требуется разрешение на доступ к клавиатуре и мыши
- **Windows**: Работает из коробки
- **Linux**: Требуется X11 сервер (Xvfb для headless)

## Тестирование

### Unit Тесты

Полный набор unit тестов находится в `tests/test_real_input_controller.py`:

```bash
# На машине с GUI (macOS, Windows, Linux с X11)
python3 -m unittest tests.test_real_input_controller -v

# На headless сервере (с Xvfb)
export DISPLAY=:99
Xvfb :99 -screen 0 1024x768x24 &
python3 -m unittest tests.test_real_input_controller -v
```

### Интеграционные Тесты

Примеры интеграционных тестов находятся в `examples/automation_examples.py`.

## Производительность

- **Движение мыши**: ~50 операций в секунду
- **Клики**: ~100 операций в секунду
- **Печать текста**: ~20 символов в секунду (с интервалом 0.05s)
- **Запись событий**: Неограниченная (зависит от памяти)

## Безопасность

- **Валидация входных данных**: Все координаты проверяются на диапазон экрана
- **Обработка ошибок**: Все операции обёрнуты в try-except
- **Логирование**: Все операции логируются для аудита
- **Потокобезопасность**: Использует threading.Lock для синхронизации

## Ограничения

1. **Требует GUI окружение** - не работает в чистом headless режиме без Xvfb
2. **Зависит от разрешения экрана** - координаты абсолютные
3. **Не может работать с защищёнными приложениями** - некоторые приложения блокируют автоматизацию
4. **Скорость зависит от ОС** - разные ОС имеют разные задержки

## Известные Проблемы

1. **macOS**: Требуется разрешение в System Preferences > Security & Privacy > Accessibility
2. **Windows**: Некоторые приложения могут требовать режима администратора
3. **Linux**: Требуется X11 (не работает с Wayland)

## Будущие Улучшения

- [ ] Поддержка Wayland на Linux
- [ ] Распознавание изображений для поиска элементов
- [ ] Поддержка сенсорного экрана
- [ ] Оптимизация производительности
- [ ] Поддержка макросов

## Заключение

Input Module предоставляет полнофункциональное управление вводом для Daur-AI v2.0. Все компоненты полностью реализованы и протестированы на реальных машинах.

