#!/bin/bash

# Создание самозапускающегося установщика для macOS
# Daur-AI v2.0

# Создание директорий
mkdir -p Daur-AI.app/Contents/{MacOS,Resources}

# Создание Info.plist
cat > Daur-AI.app/Contents/Info.plist << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>installer</string>
    <key>CFBundleIconFile</key>
    <string>AppIcon</string>
    <key>CFBundleIdentifier</key>
    <string>com.daurfinance.daur-ai-installer</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>Daur-AI Installer</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>2.0.0</string>
    <key>CFBundleVersion</key>
    <string>2.0.0</string>
    <key>LSMinimumSystemVersion</key>
    <string>11.0.0</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>NSPrincipalClass</key>
    <string>NSApplication</string>
</dict>
</plist>
EOF

# Создание исполняемого файла установщика
cat > Daur-AI.app/Contents/MacOS/installer << EOF
#!/bin/bash

# Daur-AI v2.0 Installer for macOS
# Created by Daur Finance
# Date: October 3, 2025

# Определение директорий
SCRIPT_DIR="\$(cd "\$(dirname "\${BASH_SOURCE[0]}")" && pwd)"
RESOURCES_DIR="\${SCRIPT_DIR}/../Resources"
INSTALL_DIR="\${HOME}/Applications/Daur-AI"
APP_BUNDLE="\${HOME}/Applications/Daur-AI.app"

# Функция для отображения диалогов
show_dialog() {
    osascript -e "tell application \"System Events\" to display dialog \"\$1\" buttons {\"\$2\"} default button 1 with title \"Daur-AI v2.0\""
}

# Функция для отображения прогресса
show_progress() {
    osascript -e "tell application \"System Events\" to display dialog \"\$1\" buttons {\"Отмена\"} default button 1 with title \"Daur-AI v2.0 - Установка\" giving up after 1"
}

# Приветственное сообщение
show_dialog "Добро пожаловать в программу установки Daur-AI v2.0!\\n\\nЭта программа установит Daur-AI v2.0 на ваш компьютер.\\n\\nНажмите 'Продолжить' для начала установки." "Продолжить"

# Создание директорий
mkdir -p "\${INSTALL_DIR}"
mkdir -p "\${INSTALL_DIR}/app"
mkdir -p "\${INSTALL_DIR}/docs"
mkdir -p "\${INSTALL_DIR}/resources"

# Отображение прогресса
show_progress "Создание директорий..."

# Создание демонстрационного приложения
cat > "\${INSTALL_DIR}/app/main.py" << 'PYEOF'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

print('Daur-AI v2.0 Starting...')
print('Initializing AI components...')

import time
import sys

try:
    import tkinter as tk
    from tkinter import messagebox

    # Create main window
    root = tk.Tk()
    root.title('Daur-AI v2.0')
    root.geometry('600x400')
    root.configure(bg='#1e1e2e')

    # Add header
    header = tk.Label(root, text='Daur-AI v2.0', font=('Arial', 24, 'bold'), bg='#1e1e2e', fg='#00ffff')
    header.pack(pady=20)

    # Add status message
    status = tk.Label(root, text='Initializing AI components...', font=('Arial', 12), bg='#1e1e2e', fg='#ffffff')
    status.pack(pady=10)

    # Add progress bar
    progress_frame = tk.Frame(root, bg='#1e1e2e')
    progress_frame.pack(pady=20, fill=tk.X, padx=50)
    progress_bg = tk.Label(progress_frame, bg='#333344', width=50, height=2)
    progress_bg.pack(fill=tk.X)
    progress = tk.Label(progress_frame, bg='#00ffff', width=1, height=2)
    progress.place(x=0, y=0)

    # Add info text
    info = tk.Text(root, height=8, width=50, bg='#2d2d3d', fg='#ffffff', font=('Menlo', 10))
    info.pack(pady=20, padx=50, fill=tk.BOTH, expand=True)
    info.insert(tk.END, 'Daur-AI v2.0 Demo Interface\n')
    info.insert(tk.END, '------------------------\n')

    # Update function
    def update_progress(value, message):
        progress.config(width=int(value/2))
        status.config(text=message)
        info.insert(tk.END, message + '\n')
        info.see(tk.END)
        root.update()

    # Simulate startup
    steps = [
        'Loading core modules...',
        'Initializing AI engine...',
        'Loading language model...',
        'Connecting to services...',
        'Checking for updates...',
        'Ready!'
    ]

    for i, step in enumerate(steps):
        update_progress((i+1) * 100 / len(steps), step)
        time.sleep(1)

    # Show completion message
    messagebox.showinfo('Daur-AI v2.0', 'Демонстрационная версия Daur-AI v2.0 успешно запущена!\n\nЭто демонстрационный интерфейс. Для получения полной версии свяжитесь с разработчиком:\n\nEmail: daur@daur-ai.tech\nTelegram: @daur_abd')

    root.mainloop()

except Exception as e:
    print(f'Error: {e}')
    import sys
    if sys.platform == 'darwin':
        import os
        os.system(f'osascript -e "tell application \\"System Events\\" to display dialog \\"Ошибка запуска Daur-AI v2.0:\\n{e}\\n\\nУбедитесь, что Python установлен в системе.\\" buttons {\\"OK\\"} default button 1 with title \\"Daur-AI v2.0\\" with icon caution"')
    sys.exit(1)
PYEOF

# Отображение прогресса
show_progress "Создание файлов приложения..."

# Создание README файла
cat > "\${INSTALL_DIR}/README.txt" << EOF
Daur-AI v2.0
=============

Спасибо за установку Daur-AI v2.0!

Для запуска программы используйте приложение Daur-AI
в папке Applications или Launchpad.

Контакты для поддержки:
- Email: daur@daur-ai.tech
- Telegram: @daur_abd
- WhatsApp: +44 7715 433247
- Веб-сайт: daur-ai.tech
EOF

# Отображение прогресса
show_progress "Создание приложения..."

# Создание приложения
mkdir -p "\${APP_BUNDLE}/Contents/MacOS"
mkdir -p "\${APP_BUNDLE}/Contents/Resources"

# Создание Info.plist
cat > "\${APP_BUNDLE}/Contents/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>Daur-AI</string>
    <key>CFBundleIconFile</key>
    <string>AppIcon</string>
    <key>CFBundleIdentifier</key>
    <string>com.daurfinance.daur-ai</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>Daur-AI</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>2.0.0</string>
    <key>CFBundleVersion</key>
    <string>2.0.0</string>
    <key>LSMinimumSystemVersion</key>
    <string>11.0.0</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>NSPrincipalClass</key>
    <string>NSApplication</string>
</dict>
</plist>
EOF

# Создание исполняемого файла
cat > "\${APP_BUNDLE}/Contents/MacOS/Daur-AI" << EOF
#!/bin/bash
cd "\${HOME}/Applications/Daur-AI/app"
python3 main.py
EOF

# Установка прав на исполнение
chmod +x "\${APP_BUNDLE}/Contents/MacOS/Daur-AI"

# Создание ссылки в Applications
ln -sf "\${APP_BUNDLE}" "/Applications/Daur-AI.app"

# Отображение прогресса
show_progress "Завершение установки..."

# Завершение установки
show_dialog "Установка Daur-AI v2.0 успешно завершена!\\n\\nПриложение установлено в папку Applications.\\n\\nНажмите 'Запустить', чтобы запустить Daur-AI сейчас, или 'Закрыть', чтобы закрыть программу установки." "Запустить"

# Запуск приложения
open "\${APP_BUNDLE}"
EOF

# Установка прав на исполнение
chmod +x Daur-AI.app/Contents/MacOS/installer

# Создание DMG-образа
hdiutil create -volname "Daur-AI v2.0 Installer" -srcfolder Daur-AI.app -ov -format UDZO Daur-AI-v2.0-macOS-universal.dmg
