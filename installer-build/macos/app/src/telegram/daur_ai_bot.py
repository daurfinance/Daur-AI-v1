#!/usr/bin/env python3
"""
Daur-AI Telegram Bot
Удаленное управление AI-агентом через Telegram с поддержкой аудио, файлов и текста
"""

import os
import sys
import logging
import asyncio
import json
import tempfile
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

# Добавляем путь к модулям проекта
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import telegram
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, filters, ConversationHandler
)

# Импорты проекта
try:
    from agent.integrated_ai_agent import IntegratedAIAgent, Task, TaskPriority
    from config.settings import Settings
except ImportError as e:
    logging.warning(f"Не удалось импортировать модули проекта: {e}")

class DaurAITelegramBot:
    """Telegram бот для управления Daur-AI агентом"""
    
    def __init__(self, token: str, allowed_users: List[int] = None):
        self.token = token
        self.allowed_users = allowed_users or []
        self.ai_agent = None
        self.active_sessions = {}
        self.task_history = []
        
        # Настройка логирования
        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO
        )
        self.logger = logging.getLogger(__name__)
        
        # Создаем директории для файлов
        self.temp_dir = Path(tempfile.gettempdir()) / "daur_ai_bot"
        self.temp_dir.mkdir(exist_ok=True)
        
        # Состояния для ConversationHandler
        self.WAITING_FOR_TASK = 1
        self.WAITING_FOR_CONFIG = 2
        
    async def initialize_agent(self):
        """Инициализация AI агента"""
        try:
            self.ai_agent = IntegratedAIAgent()
            await self.ai_agent.initialize()
            self.logger.info("AI агент инициализирован")
        except Exception as e:
            self.logger.error(f"Ошибка инициализации AI агента: {e}")
            self.ai_agent = None
    
    def check_user_access(self, user_id: int) -> bool:
        """Проверка доступа пользователя"""
        if not self.allowed_users:
            return True  # Если список пуст, доступ для всех
        return user_id in self.allowed_users
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /start"""
        user = update.effective_user
        
        if not self.check_user_access(user.id):
            await update.message.reply_text(
                "❌ У вас нет доступа к этому боту."
            )
            return
        
        welcome_text = f"""
🤖 **Добро пожаловать в Daur-AI Bot!**

Привет, {user.first_name}! Я ваш персональный AI-агент.

**Что я умею:**
🧠 Выполнять сложные задачи на компьютере
👁️ Анализировать изображения и экран
🎵 Обрабатывать аудио сообщения
📁 Работать с файлами и документами
⚡ Автоматизировать любые процессы

**Основные команды:**
/help - Справка по командам
/status - Статус системы
/tasks - История задач
/settings - Настройки бота

**Как использовать:**
• Отправьте текстовое сообщение с задачей
• Запишите голосовое сообщение
• Отправьте файл для обработки
• Используйте кнопки для быстрых действий

Начните с команды /help для подробной информации!
        """
        
        # Создаем клавиатуру с быстрыми действиями
        keyboard = [
            [
                InlineKeyboardButton("📊 Статус", callback_data="status"),
                InlineKeyboardButton("📋 Задачи", callback_data="tasks")
            ],
            [
                InlineKeyboardButton("⚙️ Настройки", callback_data="settings"),
                InlineKeyboardButton("❓ Справка", callback_data="help")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            welcome_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /help"""
        help_text = """
📖 **Справка по Daur-AI Bot**

**Основные команды:**
/start - Запуск бота и приветствие
/help - Эта справка
/status - Статус AI агента и системы
/tasks - История выполненных задач
/settings - Настройки бота
/agent_start - Запустить AI агента
/agent_stop - Остановить AI агента

**Типы сообщений:**

🗣️ **Голосовые сообщения**
Записывайте голосовые команды - я их распознаю и выполню

📝 **Текстовые сообщения**
Пишите задачи на естественном языке:
• "Создай документ с планом на завтра"
• "Найди информацию о Python"
• "Сделай скриншот экрана"

📁 **Файлы**
Отправляйте файлы для обработки:
• Изображения - для анализа
• Документы - для чтения и обработки
• Аудио - для транскрипции

**Примеры задач:**
• Автоматизация рутинных действий
• Поиск и анализ информации
• Создание документов и отчетов
• Управление файлами и папками
• Мониторинг системы

**Быстрые действия:**
Используйте кнопки под сообщениями для частых операций.

**Безопасность:**
Бот имеет ограничения на выполнение потенциально опасных операций.
        """
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /status"""
        try:
            # Получаем статус системы
            system_status = await self.get_system_status()
            agent_status = "🟢 Активен" if self.ai_agent else "🔴 Неактивен"
            
            status_text = f"""
📊 **Статус системы Daur-AI**

🤖 **AI Агент:** {agent_status}
💻 **CPU:** {system_status.get('cpu', 'N/A')}%
🧠 **Память:** {system_status.get('memory', 'N/A')}%
💾 **Диск:** {system_status.get('disk', 'N/A')}%
📊 **Процессы:** {system_status.get('processes', 'N/A')}

📋 **Активные задачи:** {len(self.active_sessions)}
📈 **Всего задач:** {len(self.task_history)}

🕐 **Время:** {datetime.now().strftime('%H:%M:%S')}
            """
            
            keyboard = [
                [
                    InlineKeyboardButton("🔄 Обновить", callback_data="status"),
                    InlineKeyboardButton("🚀 Запустить агента", callback_data="start_agent")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                status_text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка получения статуса: {e}")
    
    async def tasks_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /tasks - история задач"""
        if not self.task_history:
            await update.message.reply_text("📋 История задач пуста")
            return
        
        # Показываем последние 10 задач
        recent_tasks = self.task_history[-10:]
        
        tasks_text = "📋 **Последние задачи:**\n\n"
        for i, task in enumerate(recent_tasks, 1):
            status_emoji = "✅" if task.get('status') == 'completed' else "⏳"
            tasks_text += f"{status_emoji} **{i}.** {task.get('description', 'Без описания')}\n"
            tasks_text += f"   ⏰ {task.get('timestamp', 'N/A')}\n\n"
        
        keyboard = [
            [
                InlineKeyboardButton("🗑️ Очистить историю", callback_data="clear_tasks"),
                InlineKeyboardButton("📊 Подробнее", callback_data="task_details")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            tasks_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка текстовых сообщений"""
        user = update.effective_user
        
        if not self.check_user_access(user.id):
            await update.message.reply_text("❌ У вас нет доступа к этому боту.")
            return
        
        message_text = update.message.text
        
        # Показываем что бот обрабатывает сообщение
        await update.message.reply_text("🤔 Обрабатываю вашу задачу...")
        
        try:
            # Выполняем задачу через AI агента
            result = await self.execute_task(message_text, user.id)
            
            # Сохраняем в историю
            self.task_history.append({
                'description': message_text,
                'user_id': user.id,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'status': 'completed' if result.get('success') else 'failed',
                'result': result
            })
            
            # Отправляем результат
            if result.get('success'):
                response_text = f"✅ **Задача выполнена!**\n\n{result.get('message', 'Готово')}"
            else:
                response_text = f"❌ **Ошибка выполнения:**\n\n{result.get('error', 'Неизвестная ошибка')}"
            
            # Добавляем кнопки для дополнительных действий
            keyboard = [
                [
                    InlineKeyboardButton("📊 Детали", callback_data=f"task_result_{len(self.task_history)-1}"),
                    InlineKeyboardButton("🔄 Повторить", callback_data=f"repeat_task_{len(self.task_history)-1}")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                response_text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
        except Exception as e:
            self.logger.error(f"Ошибка выполнения задачи: {e}")
            await update.message.reply_text(f"❌ Произошла ошибка: {e}")
    
    async def handle_voice_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка голосовых сообщений"""
        user = update.effective_user
        
        if not self.check_user_access(user.id):
            await update.message.reply_text("❌ У вас нет доступа к этому боту.")
            return
        
        await update.message.reply_text("🎵 Обрабатываю голосовое сообщение...")
        
        try:
            # Скачиваем голосовое сообщение
            voice_file = await update.message.voice.get_file()
            voice_path = self.temp_dir / f"voice_{user.id}_{datetime.now().timestamp()}.ogg"
            
            await voice_file.download_to_drive(voice_path)
            
            # Конвертируем и распознаем речь
            text = await self.speech_to_text(voice_path)
            
            if text:
                await update.message.reply_text(f"🗣️ **Распознано:** {text}")
                
                # Выполняем задачу как текстовую
                context.user_data['voice_text'] = text
                await self.handle_text_message_from_voice(update, context, text)
            else:
                await update.message.reply_text("❌ Не удалось распознать речь. Попробуйте еще раз.")
            
            # Удаляем временный файл
            voice_path.unlink(missing_ok=True)
            
        except Exception as e:
            self.logger.error(f"Ошибка обработки голосового сообщения: {e}")
            await update.message.reply_text(f"❌ Ошибка обработки аудио: {e}")
    
    async def handle_document(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка документов и файлов"""
        user = update.effective_user
        
        if not self.check_user_access(user.id):
            await update.message.reply_text("❌ У вас нет доступа к этому боту.")
            return
        
        document = update.message.document
        await update.message.reply_text(f"📁 Обрабатываю файл: {document.file_name}")
        
        try:
            # Скачиваем файл
            file = await document.get_file()
            file_path = self.temp_dir / f"doc_{user.id}_{document.file_name}"
            
            await file.download_to_drive(file_path)
            
            # Анализируем файл
            analysis = await self.analyze_file(file_path)
            
            response_text = f"""
📄 **Анализ файла:** {document.file_name}
📊 **Размер:** {document.file_size} байт
🔍 **Тип:** {document.mime_type}

**Результат анализа:**
{analysis}
            """
            
            keyboard = [
                [
                    InlineKeyboardButton("🔄 Обработать", callback_data=f"process_file_{file_path.name}"),
                    InlineKeyboardButton("📋 Извлечь текст", callback_data=f"extract_text_{file_path.name}")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                response_text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
        except Exception as e:
            self.logger.error(f"Ошибка обработки файла: {e}")
            await update.message.reply_text(f"❌ Ошибка обработки файла: {e}")
    
    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка изображений"""
        user = update.effective_user
        
        if not self.check_user_access(user.id):
            await update.message.reply_text("❌ У вас нет доступа к этому боту.")
            return
        
        await update.message.reply_text("🖼️ Анализирую изображение...")
        
        try:
            # Получаем изображение в лучшем качестве
            photo = update.message.photo[-1]
            file = await photo.get_file()
            
            photo_path = self.temp_dir / f"photo_{user.id}_{datetime.now().timestamp()}.jpg"
            await file.download_to_drive(photo_path)
            
            # Анализируем изображение
            analysis = await self.analyze_image(photo_path)
            
            response_text = f"""
🖼️ **Анализ изображения:**

{analysis}
            """
            
            keyboard = [
                [
                    InlineKeyboardButton("🔍 OCR", callback_data=f"ocr_image_{photo_path.name}"),
                    InlineKeyboardButton("🎨 Описание", callback_data=f"describe_image_{photo_path.name}")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                response_text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
            # Удаляем временный файл
            photo_path.unlink(missing_ok=True)
            
        except Exception as e:
            self.logger.error(f"Ошибка анализа изображения: {e}")
            await update.message.reply_text(f"❌ Ошибка анализа изображения: {e}")
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка нажатий на кнопки"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data == "status":
            await self.status_callback(query, context)
        elif data == "tasks":
            await self.tasks_callback(query, context)
        elif data == "help":
            await self.help_callback(query, context)
        elif data == "start_agent":
            await self.start_agent_callback(query, context)
        elif data == "stop_agent":
            await self.stop_agent_callback(query, context)
        elif data.startswith("task_result_"):
            await self.task_result_callback(query, context, data)
        elif data.startswith("repeat_task_"):
            await self.repeat_task_callback(query, context, data)
        else:
            await query.edit_message_text("❓ Неизвестная команда")
    
    async def execute_task(self, task_description: str, user_id: int) -> Dict[str, Any]:
        """Выполнение задачи через AI агента"""
        try:
            if not self.ai_agent:
                return {
                    'success': False,
                    'error': 'AI агент не инициализирован. Используйте /agent_start'
                }
            
            # Создаем задачу
            task = Task(
                description=task_description,
                priority=TaskPriority.MEDIUM,
                user_id=str(user_id)
            )
            
            # Выполняем через агента
            result = await self.ai_agent.execute_task(task)
            
            return {
                'success': True,
                'message': result.get('message', 'Задача выполнена'),
                'details': result
            }
            
        except Exception as e:
            self.logger.error(f"Ошибка выполнения задачи: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def speech_to_text(self, audio_path: Path) -> Optional[str]:
        """Распознавание речи из аудио файла"""
        try:
            # Используем manus-speech-to-text утилиту
            result = subprocess.run([
                'manus-speech-to-text', str(audio_path)
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                self.logger.error(f"Ошибка распознавания речи: {result.stderr}")
                return None
                
        except Exception as e:
            self.logger.error(f"Ошибка speech-to-text: {e}")
            return None
    
    async def analyze_file(self, file_path: Path) -> str:
        """Анализ файла"""
        try:
            file_size = file_path.stat().st_size
            file_ext = file_path.suffix.lower()
            
            analysis = f"Размер: {file_size} байт\nРасширение: {file_ext}\n"
            
            # Базовый анализ по типу файла
            if file_ext in ['.txt', '.md', '.py', '.js', '.html', '.css']:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    lines = len(content.splitlines())
                    chars = len(content)
                    analysis += f"Строк: {lines}\nСимволов: {chars}"
            
            elif file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
                analysis += "Тип: Изображение\nМожно выполнить OCR или анализ содержимого"
            
            elif file_ext in ['.pdf']:
                analysis += "Тип: PDF документ\nМожно извлечь текст и изображения"
            
            else:
                analysis += "Тип: Неизвестный\nТребуется дополнительный анализ"
            
            return analysis
            
        except Exception as e:
            return f"Ошибка анализа: {e}"
    
    async def analyze_image(self, image_path: Path) -> str:
        """Анализ изображения"""
        try:
            # Базовая информация об изображении
            from PIL import Image
            
            with Image.open(image_path) as img:
                width, height = img.size
                mode = img.mode
                format_name = img.format
                
                analysis = f"""
📐 **Размеры:** {width}x{height} пикселей
🎨 **Режим:** {mode}
📄 **Формат:** {format_name}

🔍 **Доступные операции:**
• OCR - извлечение текста
• Анализ содержимого
• Поиск объектов
• Обработка изображения
                """
                
                return analysis.strip()
                
        except Exception as e:
            return f"Ошибка анализа изображения: {e}"
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Получение статуса системы"""
        try:
            import psutil
            
            return {
                'cpu': round(psutil.cpu_percent(interval=1), 1),
                'memory': round(psutil.virtual_memory().percent, 1),
                'disk': round(psutil.disk_usage('/').percent, 1),
                'processes': len(psutil.pids())
            }
        except Exception as e:
            self.logger.error(f"Ошибка получения статуса системы: {e}")
            return {}
    
    async def handle_text_message_from_voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
        """Обработка текста из голосового сообщения"""
        # Создаем фейковое обновление для обработки как текстового сообщения
        class FakeMessage:
            def __init__(self, text):
                self.text = text
        
        class FakeUpdate:
            def __init__(self, message, user):
                self.message = message
                self.effective_user = user
        
        fake_update = FakeUpdate(FakeMessage(text), update.effective_user)
        await self.handle_text_message(fake_update, context)
    
    # Callback методы для кнопок
    async def status_callback(self, query, context):
        """Callback для кнопки статуса"""
        try:
            system_status = await self.get_system_status()
            agent_status = "🟢 Активен" if self.ai_agent else "🔴 Неактивен"
            
            status_text = f"""
📊 **Статус системы Daur-AI**

🤖 **AI Агент:** {agent_status}
💻 **CPU:** {system_status.get('cpu', 'N/A')}%
🧠 **Память:** {system_status.get('memory', 'N/A')}%
💾 **Диск:** {system_status.get('disk', 'N/A')}%

🕐 **Обновлено:** {datetime.now().strftime('%H:%M:%S')}
            """
            
            await query.edit_message_text(status_text, parse_mode='Markdown')
        except Exception as e:
            await query.edit_message_text(f"❌ Ошибка: {e}")
    
    async def start_agent_callback(self, query, context):
        """Callback для запуска агента"""
        try:
            if not self.ai_agent:
                await self.initialize_agent()
            
            if self.ai_agent:
                await query.edit_message_text("✅ AI агент успешно запущен!")
            else:
                await query.edit_message_text("❌ Не удалось запустить AI агента")
        except Exception as e:
            await query.edit_message_text(f"❌ Ошибка запуска: {e}")
    
    def run(self):
        """Запуск бота"""
        # Создаем приложение
        application = Application.builder().token(self.token).build()
        
        # Добавляем обработчики команд
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("status", self.status_command))
        application.add_handler(CommandHandler("tasks", self.tasks_command))
        
        # Добавляем обработчики сообщений
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text_message))
        application.add_handler(MessageHandler(filters.VOICE, self.handle_voice_message))
        application.add_handler(MessageHandler(filters.Document.ALL, self.handle_document))
        application.add_handler(MessageHandler(filters.PHOTO, self.handle_photo))
        
        # Добавляем обработчик кнопок
        application.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Устанавливаем команды бота
        asyncio.create_task(self.set_bot_commands(application.bot))
        
        self.logger.info("Daur-AI Telegram Bot запущен!")
        
        # Запускаем бота
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    
    async def set_bot_commands(self, bot):
        """Установка команд бота в меню"""
        commands = [
            BotCommand("start", "Запуск бота"),
            BotCommand("help", "Справка по командам"),
            BotCommand("status", "Статус системы"),
            BotCommand("tasks", "История задач"),
            BotCommand("settings", "Настройки бота")
        ]
        
        await bot.set_my_commands(commands)


def main():
    """Главная функция для запуска бота"""
    # Получаем токен из переменных окружения или конфига
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        print("❌ Не указан TELEGRAM_BOT_TOKEN")
        print("Установите переменную окружения или укажите токен в коде")
        return
    
    # Список разрешенных пользователей (опционально)
    allowed_users_str = os.getenv('TELEGRAM_ALLOWED_USERS', '')
    allowed_users = []
    
    if allowed_users_str:
        try:
            allowed_users = [int(uid.strip()) for uid in allowed_users_str.split(',')]
        except ValueError:
            print("⚠️ Неверный формат TELEGRAM_ALLOWED_USERS")
    
    # Создаем и запускаем бота
    bot = DaurAITelegramBot(token, allowed_users)
    
    try:
        bot.run()
    except KeyboardInterrupt:
        print("\n👋 Бот остановлен")
    except Exception as e:
        print(f"❌ Ошибка запуска бота: {e}")


if __name__ == "__main__":
    main()
