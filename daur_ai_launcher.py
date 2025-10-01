#!/usr/bin/env python3
"""
Daur-AI System Launcher
Главный запускатель всей системы: AI агент + Telegram бот + веб-интерфейс
"""

import os
import sys
import asyncio
import logging
import signal
import threading
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any
import json

# Добавляем путь к модулям проекта
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Импорты проекта
try:
    from integration.bot_agent_bridge import BotAgentBridge, initialize_bridge
    from telegram.daur_ai_bot import DaurAITelegramBot
    from agent.integrated_ai_agent import IntegratedAIAgent
except ImportError as e:
    print(f"❌ Ошибка импорта модулей: {e}")
    print("Убедитесь, что все зависимости установлены")
    sys.exit(1)

class DaurAILauncher:
    """Главный запускатель системы Daur-AI"""
    
    def __init__(self, config_path: str = "telegram_config.json"):
        self.config_path = config_path
        self.config = self.load_config()
        
        # Компоненты системы
        self.bridge: Optional[BotAgentBridge] = None
        self.telegram_bot: Optional[DaurAITelegramBot] = None
        self.web_server_process: Optional[subprocess.Popen] = None
        self.electron_process: Optional[subprocess.Popen] = None
        
        # Флаги состояния
        self.is_running = False
        self.shutdown_event = threading.Event()
        
        # Настройка логирования
        self.setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # Обработчики сигналов
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def load_config(self) -> Dict[str, Any]:
        """Загрузка конфигурации"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            self.create_default_config()
            return self.load_config()
        except Exception as e:
            print(f"❌ Ошибка загрузки конфигурации: {e}")
            return self.get_default_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """Получение конфигурации по умолчанию"""
        return {
            "telegram": {
                "bot_token": "",
                "allowed_users": [],
                "features": {
                    "voice_recognition": True,
                    "file_processing": True,
                    "image_analysis": True
                }
            },
            "ai_agent": {
                "auto_start": True,
                "default_model": "ollama",
                "fallback_model": "simple"
            },
            "web_interface": {
                "enabled": True,
                "port": 8000,
                "auto_open": False
            },
            "electron": {
                "enabled": True,
                "auto_start": False
            },
            "logging": {
                "level": "INFO",
                "file": "logs/daur_ai.log"
            }
        }
    
    def create_default_config(self):
        """Создание конфигурации по умолчанию"""
        config = self.get_default_config()
        
        # Создаем директорию для логов
        os.makedirs("logs", exist_ok=True)
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Создан файл конфигурации: {self.config_path}")
        print("📝 Отредактируйте его и укажите TELEGRAM_BOT_TOKEN")
    
    def setup_logging(self):
        """Настройка логирования"""
        log_config = self.config.get('logging', {})
        log_level = getattr(logging, log_config.get('level', 'INFO'))
        log_file = log_config.get('file', 'logs/daur_ai.log')
        
        # Создаем директорию для логов
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        # Настраиваем логирование
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    async def start_system(self):
        """Запуск всей системы"""
        try:
            self.logger.info("🚀 Запуск системы Daur-AI...")
            self.is_running = True
            
            # 1. Инициализируем мост
            await self.start_bridge()
            
            # 2. Запускаем веб-интерфейс
            if self.config.get('web_interface', {}).get('enabled', True):
                await self.start_web_interface()
            
            # 3. Запускаем Telegram бота
            if self.config.get('telegram', {}).get('bot_token'):
                await self.start_telegram_bot()
            else:
                self.logger.warning("⚠️ Telegram бот не запущен: не указан bot_token")
            
            # 4. Запускаем Electron (опционально)
            if self.config.get('electron', {}).get('enabled', False):
                await self.start_electron()
            
            self.logger.info("✅ Система Daur-AI успешно запущена!")
            self.print_status()
            
            # Ждем сигнала остановки
            await self.wait_for_shutdown()
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка запуска системы: {e}")
            raise
        finally:
            await self.shutdown_system()
    
    async def start_bridge(self):
        """Запуск моста между компонентами"""
        self.logger.info("🔗 Инициализация моста...")
        
        self.bridge = initialize_bridge(self.config_path)
        await self.bridge.initialize()
        
        self.logger.info("✅ Мост инициализирован")
    
    async def start_telegram_bot(self):
        """Запуск Telegram бота"""
        self.logger.info("🤖 Запуск Telegram бота...")
        
        telegram_config = self.config.get('telegram', {})
        bot_token = telegram_config.get('bot_token') or os.getenv('TELEGRAM_BOT_TOKEN')
        
        if not bot_token:
            raise ValueError("Не указан TELEGRAM_BOT_TOKEN")
        
        allowed_users = telegram_config.get('allowed_users', [])
        
        # Создаем бота
        self.telegram_bot = DaurAITelegramBot(bot_token, allowed_users)
        
        # Подключаем к мосту
        if self.bridge:
            self.bridge.set_telegram_bot(self.telegram_bot)
        
        # Запускаем в отдельном потоке
        bot_thread = threading.Thread(
            target=self.telegram_bot.run,
            daemon=True
        )
        bot_thread.start()
        
        self.logger.info("✅ Telegram бот запущен")
    
    async def start_web_interface(self):
        """Запуск веб-интерфейса"""
        self.logger.info("🌐 Запуск веб-интерфейса...")
        
        try:
            # Запускаем API сервер
            api_script = Path("src/web/enhanced_api_server.py")
            if api_script.exists():
                self.web_server_process = subprocess.Popen([
                    sys.executable, str(api_script)
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                self.logger.info("✅ Веб API сервер запущен на порту 8000")
            else:
                self.logger.warning("⚠️ API сервер не найден")
            
            # Запускаем React интерфейс (если доступен)
            react_dir = Path("daur-ai-advanced-panel")
            if react_dir.exists():
                self.logger.info("🎨 React интерфейс доступен на порту 5174")
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка запуска веб-интерфейса: {e}")
    
    async def start_electron(self):
        """Запуск Electron приложения"""
        self.logger.info("🖥️ Запуск Electron приложения...")
        
        try:
            # Проверяем наличие Electron
            if Path("node_modules/.bin/electron").exists():
                self.electron_process = subprocess.Popen([
                    "npm", "run", "electron"
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                self.logger.info("✅ Electron приложение запущено")
            else:
                self.logger.warning("⚠️ Electron не установлен")
                
        except Exception as e:
            self.logger.error(f"❌ Ошибка запуска Electron: {e}")
    
    def print_status(self):
        """Вывод статуса системы"""
        print("\n" + "="*60)
        print("🤖 DAUR-AI СИСТЕМА ЗАПУЩЕНА")
        print("="*60)
        
        if self.bridge:
            print("✅ AI Агент: Активен")
        else:
            print("❌ AI Агент: Неактивен")
        
        if self.telegram_bot:
            print("✅ Telegram Бот: Активен")
        else:
            print("❌ Telegram Бот: Неактивен")
        
        if self.web_server_process:
            print("✅ Веб API: http://localhost:8000")
        else:
            print("❌ Веб API: Неактивен")
        
        print("✅ Веб Панель: http://localhost:5174")
        
        if self.electron_process:
            print("✅ Desktop App: Запущено")
        
        print("\n📋 Доступные интерфейсы:")
        print("   🌐 Веб-панель: http://localhost:5174")
        print("   🔌 API: http://localhost:8000")
        print("   📱 Telegram: @your_bot_name")
        
        print("\n⚡ Команды управления:")
        print("   Ctrl+C - Остановка системы")
        print("   /status - Статус в Telegram")
        print("   /help - Справка в Telegram")
        
        print("\n🔄 Система готова к работе!")
        print("="*60 + "\n")
    
    async def wait_for_shutdown(self):
        """Ожидание сигнала остановки"""
        try:
            while self.is_running and not self.shutdown_event.is_set():
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("Получен сигнал остановки")
    
    async def shutdown_system(self):
        """Остановка системы"""
        self.logger.info("🛑 Остановка системы Daur-AI...")
        
        self.is_running = False
        
        # Останавливаем мост
        if self.bridge:
            self.bridge.shutdown()
        
        # Останавливаем веб-сервер
        if self.web_server_process:
            self.web_server_process.terminate()
            try:
                self.web_server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.web_server_process.kill()
        
        # Останавливаем Electron
        if self.electron_process:
            self.electron_process.terminate()
            try:
                self.electron_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.electron_process.kill()
        
        self.logger.info("✅ Система остановлена")
    
    def _signal_handler(self, signum, frame):
        """Обработчик сигналов"""
        self.logger.info(f"Получен сигнал {signum}")
        self.shutdown_event.set()


def main():
    """Главная функция"""
    print("🤖 Daur-AI System Launcher")
    print("=" * 40)
    
    # Проверяем Python версию
    if sys.version_info < (3, 8):
        print("❌ Требуется Python 3.8 или выше")
        sys.exit(1)
    
    # Создаем и запускаем лаунчер
    launcher = DaurAILauncher()
    
    try:
        # Запускаем систему
        asyncio.run(launcher.start_system())
    except KeyboardInterrupt:
        print("\n👋 Система остановлена пользователем")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
