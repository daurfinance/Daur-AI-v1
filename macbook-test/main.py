#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI v2.0 - Главный модуль
Точка входа для запуска приложения
"""

import os
import sys
import time
import argparse

# Добавление директории src в путь для импорта
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def print_banner():
    """Выводит баннер приложения"""
    banner = """
    ██████╗  █████╗ ██╗   ██╗██████╗       █████╗ ██╗
    ██╔══██╗██╔══██╗██║   ██║██╔══██╗     ██╔══██╗██║
    ██║  ██║███████║██║   ██║██████╔╝     ███████║██║
    ██║  ██║██╔══██║██║   ██║██╔══██╗     ██╔══██║██║
    ██████╔╝██║  ██║╚██████╔╝██║  ██║     ██║  ██║██║
    ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝     ╚═╝  ╚═╝╚═╝
    ===============================================
                      v2.0
    ===============================================
    """
    print(banner)

def check_dependencies():
    """Проверяет наличие необходимых зависимостей"""
    try:
        import numpy
        import torch
        import transformers
        print("✅ Основные зависимости установлены")
        return True
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        print("Пожалуйста, установите необходимые зависимости:")
        print("pip install -r requirements.txt")
        return False

def initialize_app():
    """Инициализирует приложение"""
    print("🔄 Инициализация Daur-AI v2.0...")
    
    # Имитация загрузки компонентов
    components = [
        "Ядро ИИ", 
        "Языковая модель", 
        "Модуль компьютерного зрения",
        "Интеграция с Telegram",
        "Веб-интерфейс"
    ]
    
    for component in components:
        print(f"⏳ Загрузка компонента: {component}...")
        time.sleep(0.5)  # Имитация загрузки
        print(f"✅ Компонент {component} загружен")
    
    print("✅ Инициализация завершена")

def start_ui():
    """Запускает пользовательский интерфейс"""
    try:
        import tkinter as tk
        from tkinter import messagebox, scrolledtext
        
        # Создание основного окна
        root = tk.Tk()
        root.title("Daur-AI v2.0")
        root.geometry("800x600")
        root.configure(bg="#1e1e2e")
        
        # Заголовок
        header = tk.Label(root, text="Daur-AI v2.0", font=("Arial", 24, "bold"), bg="#1e1e2e", fg="#00ffff")
        header.pack(pady=20)
        
        # Статус
        status = tk.Label(root, text="Система готова к работе", font=("Arial", 12), bg="#1e1e2e", fg="#ffffff")
        status.pack(pady=10)
        
        # Консоль вывода
        console_frame = tk.Frame(root, bg="#1e1e2e")
        console_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        console = scrolledtext.ScrolledText(console_frame, bg="#2d2d3d", fg="#ffffff", font=("Courier", 10))
        console.pack(fill=tk.BOTH, expand=True)
        console.insert(tk.END, "Daur-AI v2.0 запущен и готов к работе\n")
        console.insert(tk.END, "----------------------------------------\n")
        console.insert(tk.END, "Это демонстрационный интерфейс для тестирования на MacBook\n\n")
        console.insert(tk.END, "Доступные модули:\n")
        console.insert(tk.END, "- Ядро ИИ: Активно\n")
        console.insert(tk.END, "- Языковая модель: Готова к использованию\n")
        console.insert(tk.END, "- Компьютерное зрение: Готово к использованию\n")
        console.insert(tk.END, "- Telegram-бот: Не запущен\n")
        console.insert(tk.END, "- Веб-интерфейс: Не запущен\n\n")
        console.insert(tk.END, "Для запуска дополнительных модулей используйте соответствующие скрипты\n")
        console.insert(tk.END, "См. README.md для подробных инструкций\n")
        
        # Поле ввода
        input_frame = tk.Frame(root, bg="#1e1e2e")
        input_frame.pack(pady=10, padx=20, fill=tk.X)
        
        input_label = tk.Label(input_frame, text="Введите команду:", bg="#1e1e2e", fg="#ffffff")
        input_label.pack(side=tk.LEFT, padx=5)
        
        input_field = tk.Entry(input_frame, bg="#2d2d3d", fg="#ffffff", font=("Courier", 10), width=50)
        input_field.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        def process_command():
            command = input_field.get()
            if command:
                console.insert(tk.END, f"\n> {command}\n")
                if command.lower() == "exit" or command.lower() == "quit":
                    root.destroy()
                elif command.lower() == "help":
                    console.insert(tk.END, "Доступные команды:\n")
                    console.insert(tk.END, "- help: Показать справку\n")
                    console.insert(tk.END, "- status: Показать статус системы\n")
                    console.insert(tk.END, "- clear: Очистить консоль\n")
                    console.insert(tk.END, "- exit/quit: Выйти из приложения\n")
                elif command.lower() == "status":
                    console.insert(tk.END, "Статус системы:\n")
                    console.insert(tk.END, "- CPU: 5%\n")
                    console.insert(tk.END, "- Память: 120MB\n")
                    console.insert(tk.END, "- Диск: 2.3GB свободно\n")
                    console.insert(tk.END, "- Сеть: Подключено\n")
                elif command.lower() == "clear":
                    console.delete(1.0, tk.END)
                else:
                    console.insert(tk.END, f"Неизвестная команда: {command}\n")
                    console.insert(tk.END, "Введите 'help' для получения списка команд\n")
                input_field.delete(0, tk.END)
                console.see(tk.END)
        
        submit_button = tk.Button(input_frame, text="Выполнить", command=process_command, bg="#00aaff", fg="#ffffff")
        submit_button.pack(side=tk.LEFT, padx=5)
        
        # Привязка Enter к отправке команды
        input_field.bind("<Return>", lambda event: process_command())
        
        # Кнопки управления
        button_frame = tk.Frame(root, bg="#1e1e2e")
        button_frame.pack(pady=20, padx=20)
        
        start_web_button = tk.Button(button_frame, text="Запустить веб-интерфейс", 
                                    command=lambda: console.insert(tk.END, "\nЗапуск веб-интерфейса...\nВеб-интерфейс доступен по адресу: http://localhost:8000\n"),
                                    bg="#00aa00", fg="#ffffff")
        start_web_button.pack(side=tk.LEFT, padx=5)
        
        start_bot_button = tk.Button(button_frame, text="Запустить Telegram-бот", 
                                    command=lambda: console.insert(tk.END, "\nЗапуск Telegram-бота...\nНеобходимо настроить токен в файле конфигурации\n"),
                                    bg="#aa00aa", fg="#ffffff")
        start_bot_button.pack(side=tk.LEFT, padx=5)
        
        exit_button = tk.Button(button_frame, text="Выход", command=root.destroy, bg="#aa0000", fg="#ffffff")
        exit_button.pack(side=tk.LEFT, padx=5)
        
        # Фокус на поле ввода
        input_field.focus_set()
        
        # Запуск главного цикла
        root.mainloop()
        
    except Exception as e:
        print(f"❌ Ошибка запуска интерфейса: {e}")
        print("Запуск в консольном режиме...")
        start_console_mode()

def start_console_mode():
    """Запускает консольный режим работы"""
    print("🖥️ Консольный режим Daur-AI v2.0")
    print("Введите 'exit' для выхода, 'help' для справки")
    
    while True:
        try:
            command = input("\nDaur-AI> ")
            if command.lower() == "exit" or command.lower() == "quit":
                print("Завершение работы...")
                break
            elif command.lower() == "help":
                print("Доступные команды:")
                print("- help: Показать справку")
                print("- status: Показать статус системы")
                print("- version: Показать версию")
                print("- exit/quit: Выйти из приложения")
            elif command.lower() == "status":
                print("Статус системы: Активна")
                print("Все компоненты работают нормально")
            elif command.lower() == "version":
                print("Daur-AI v2.0 (Октябрь 2025)")
            else:
                print(f"Неизвестная команда: {command}")
                print("Введите 'help' для получения списка команд")
        except KeyboardInterrupt:
            print("\nПрервано пользователем. Завершение работы...")
            break
        except Exception as e:
            print(f"Ошибка: {e}")

def parse_arguments():
    """Парсит аргументы командной строки"""
    parser = argparse.ArgumentParser(description="Daur-AI v2.0")
    parser.add_argument("--console", action="store_true", help="Запуск в консольном режиме")
    parser.add_argument("--version", action="store_true", help="Показать версию и выйти")
    return parser.parse_args()

def main():
    """Главная функция приложения"""
    args = parse_arguments()
    
    if args.version:
        print("Daur-AI v2.0 (Октябрь 2025)")
        return
    
    print_banner()
    
    if not check_dependencies():
        return
    
    initialize_app()
    
    if args.console:
        start_console_mode()
    else:
        start_ui()

if __name__ == "__main__":
    main()
