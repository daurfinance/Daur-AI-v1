# API Reference

## agent.core

### class DaurAgent

Основной класс агента, координирующий работу всех компонентов и обрабатывающий команды пользователя.

#### Методы

| Метод | Описание |
| ----- | -------- |
| `__init__(config, ui_mode="console", sandbox=False)` | Конструктор. |
| `run()` | Запускает агента и начинает обработку команд. |
| `handle_command(command)` | Обрабатывает полученную команду от пользователя. |
| `cleanup()` | Освобождает ресурсы при завершении работы. |

## ai.model_manager

### class AIModelManager

Менеджер для загрузки и использования локальных моделей ИИ.

#### Методы

| Метод | Описание |
| ----- | -------- |
| `__init__(model_path, timeout=30, context_length=4096, n_threads=None, use_gpu=True, device=None)` | Конструктор. |
| `load_model()` | Загружает модель в память. |
| `unload_model()` | Выгружает модель из памяти. |
| `generate_text(prompt, max_tokens=256, temperature=0.7, top_p=0.95)` | Генерирует текст с использованием модели. |
| `parse_command(command_text)` | Парсит команду пользователя в структурированный формат. |
| `cleanup()` | Освобождает ресурсы. |

## ai.trainer

### class AITrainer

Модуль для обучения AI-моделей на основе логов действий пользователя.

#### Методы

| Метод | Описание |
| ----- | -------- |
| `__init__(model_path, output_dir=None)` | Конструктор. |
| `process_logs(log_path)` | Обрабатывает логи для создания обучающего датасета. |
| `train(log_entries, epochs=3, batch_size=4, learning_rate=5e-5, use_gpu=True)` | Обучает модель на логах. |
| `finetune_model(log_path, epochs=3, batch_size=4, learning_rate=5e-5, use_gpu=True)` | Дообучает модель на основе логов. |

## parser.command_parser

### class CommandParser

Парсер команд для обработки пользовательского ввода.

#### Методы

| Метод | Описание |
| ----- | -------- |
| `__init__()` | Конструктор. |
| `parse(command_text)` | Парсит команду пользователя в список действий. |

## input.controller

### class InputController

Контроллер ввода для эмуляции мыши и клавиатуры.

#### Методы

| Метод | Описание |
| ----- | -------- |
| `__init__(os_platform)` | Конструктор. |
| `execute_action(action)` | Выполняет действие ввода. |
| `mouse_click(x, y, button="left", count=1)` | Выполняет клик мышью. |
| `mouse_move(x, y, duration=0.5)` | Перемещает курсор мыши. |
| `key_press(key, hold=0.0)` | Нажимает клавишу на клавиатуре. |
| `type_text(text, interval=0.05)` | Набирает текст. |

## apps.manager

### class AppManager

Управление приложениями.

#### Методы

| Метод | Описание |
| ----- | -------- |
| `__init__(os_platform, input_controller)` | Конструктор. |
| `execute_action(action)` | Выполняет действие для управления приложением. |
| `open_app(app_name, args=[])` | Запускает приложение. |
| `close_app(app_name)` | Закрывает приложение. |
| `switch_to_app(app_name)` | Переключается на запущенное приложение. |
| `get_running_apps()` | Возвращает список запущенных приложений. |

## files.manager

### class FileManager

Управление файловой системой.

#### Методы

| Метод | Описание |
| ----- | -------- |
| `__init__(allowed_extensions=None, restricted_paths=None)` | Конструктор. |
| `execute_action(action)` | Выполняет действие с файлами. |
| `create_file(path, content="")` | Создает файл. |
| `read_file(path)` | Читает содержимое файла. |
| `write_file(path, content)` | Записывает в файл. |
| `delete_file(path)` | Удаляет файл. |
| `list_directory(path)` | Возвращает содержимое директории. |

## logger.logger

### class ActionLogger

Логирование действий агента.

#### Методы

| Метод | Описание |
| ----- | -------- |
| `__init__(log_path, encrypt=False)` | Конструктор. |
| `log_action(command, action, result, error=None)` | Логирует действие. |
| `get_logs(start_date=None, end_date=None)` | Возвращает логи за указанный период. |

### Функции

| Функция | Описание |
| ------- | -------- |
| `setup_logger(level=logging.INFO)` | Настраивает логирование для всего приложения. |

## ui.console

### class ConsoleUI

Консольный интерфейс для работы с агентом.

#### Методы

| Метод | Описание |
| ----- | -------- |
| `__init__(prompt="Daur-AI> ", history_size=100, command_callback=None)` | Конструктор. |
| `run()` | Запускает интерфейс. |
| `show_message(message)` | Отображает сообщение. |
| `show_progress(message, duration=None)` | Отображает индикатор прогресса. |

## ui.gui

### class GraphicalUI

Графический интерфейс для работы с агентом.

#### Методы

| Метод | Описание |
| ----- | -------- |
| `__init__(theme=None, window_size=(800, 600), command_callback=None)` | Конструктор. |
| `run()` | Запускает интерфейс. |
| `show_message(message, message_type="info")` | Отображает сообщение. |
| `show_progress(message, duration=None)` | Отображает индикатор прогресса. |
