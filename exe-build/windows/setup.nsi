; Daur-AI v2.0 Installer Script
; NSIS Modern User Interface

;--------------------------------
; Includes
!include "MUI2.nsh"

;--------------------------------
; General
Name "Daur-AI v2.0"
OutFile "Daur-AI-v2.0-Setup.exe"
Unicode True

; Default installation folder
InstallDir "$LOCALAPPDATA\Daur-AI"

; Request application privileges
RequestExecutionLevel user

;--------------------------------
; Interface Settings
!define MUI_ABORTWARNING
!define MUI_ICON "${NSISDIR}\Contrib\Graphics\Icons\modern-install.ico"
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"

;--------------------------------
; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

;--------------------------------
; Languages
!insertmacro MUI_LANGUAGE "English"
!insertmacro MUI_LANGUAGE "Russian"

;--------------------------------
; Installer Sections
Section "Daur-AI Core" SecCore
  SectionIn RO
  
  ; Set output path to the installation directory
  SetOutPath "$INSTDIR"
  
  ; Create directories
  CreateDirectory "$INSTDIR\app"
  CreateDirectory "$INSTDIR\docs"
  CreateDirectory "$INSTDIR\resources"
  
  ; Add files
  FileOpen $0 "$INSTDIR\app\main.py" w
  FileWrite $0 "#!/usr/bin/env python$\r$\n"
  FileWrite $0 "# -*- coding: utf-8 -*-$\r$\n"
  FileWrite $0 "$\r$\n"
  FileWrite $0 "print('Daur-AI v2.0 Starting...')$\r$\n"
  FileWrite $0 "print('Initializing AI components...')$\r$\n"
  FileWrite $0 "$\r$\n"
  FileWrite $0 "import time$\r$\n"
  FileWrite $0 "import sys$\r$\n"
  FileWrite $0 "$\r$\n"
  FileWrite $0 "try:$\r$\n"
  FileWrite $0 "    import tkinter as tk$\r$\n"
  FileWrite $0 "    from tkinter import messagebox$\r$\n"
  FileWrite $0 "$\r$\n"
  FileWrite $0 "    # Create main window$\r$\n"
  FileWrite $0 "    root = tk.Tk()$\r$\n"
  FileWrite $0 "    root.title('Daur-AI v2.0')$\r$\n"
  FileWrite $0 "    root.geometry('600x400')$\r$\n"
  FileWrite $0 "    root.configure(bg='#1e1e2e')$\r$\n"
  FileWrite $0 "$\r$\n"
  FileWrite $0 "    # Add header$\r$\n"
  FileWrite $0 "    header = tk.Label(root, text='Daur-AI v2.0', font=('Arial', 24, 'bold'), bg='#1e1e2e', fg='#00ffff')$\r$\n"
  FileWrite $0 "    header.pack(pady=20)$\r$\n"
  FileWrite $0 "$\r$\n"
  FileWrite $0 "    # Add status message$\r$\n"
  FileWrite $0 "    status = tk.Label(root, text='Initializing AI components...', font=('Arial', 12), bg='#1e1e2e', fg='#ffffff')$\r$\n"
  FileWrite $0 "    status.pack(pady=10)$\r$\n"
  FileWrite $0 "$\r$\n"
  FileWrite $0 "    # Add progress bar$\r$\n"
  FileWrite $0 "    progress_frame = tk.Frame(root, bg='#1e1e2e')$\r$\n"
  FileWrite $0 "    progress_frame.pack(pady=20, fill=tk.X, padx=50)$\r$\n"
  FileWrite $0 "    progress_bg = tk.Label(progress_frame, bg='#333344', width=50, height=2)$\r$\n"
  FileWrite $0 "    progress_bg.pack(fill=tk.X)$\r$\n"
  FileWrite $0 "    progress = tk.Label(progress_frame, bg='#00ffff', width=1, height=2)$\r$\n"
  FileWrite $0 "    progress.place(x=0, y=0)$\r$\n"
  FileWrite $0 "$\r$\n"
  FileWrite $0 "    # Add info text$\r$\n"
  FileWrite $0 "    info = tk.Text(root, height=8, width=50, bg='#2d2d3d', fg='#ffffff', font=('Consolas', 10))$\r$\n"
  FileWrite $0 "    info.pack(pady=20, padx=50, fill=tk.BOTH, expand=True)$\r$\n"
  FileWrite $0 "    info.insert(tk.END, 'Daur-AI v2.0 Demo Interface\\n')$\r$\n"
  FileWrite $0 "    info.insert(tk.END, '------------------------\\n')$\r$\n"
  FileWrite $0 "$\r$\n"
  FileWrite $0 "    # Update function$\r$\n"
  FileWrite $0 "    def update_progress(value, message):$\r$\n"
  FileWrite $0 "        progress.config(width=int(value/2))$\r$\n"
  FileWrite $0 "        status.config(text=message)$\r$\n"
  FileWrite $0 "        info.insert(tk.END, message + '\\n')$\r$\n"
  FileWrite $0 "        info.see(tk.END)$\r$\n"
  FileWrite $0 "        root.update()$\r$\n"
  FileWrite $0 "$\r$\n"
  FileWrite $0 "    # Simulate startup$\r$\n"
  FileWrite $0 "    steps = [$\r$\n"
  FileWrite $0 "        'Loading core modules...',$\r$\n"
  FileWrite $0 "        'Initializing AI engine...',$\r$\n"
  FileWrite $0 "        'Loading language model...',$\r$\n"
  FileWrite $0 "        'Connecting to services...',$\r$\n"
  FileWrite $0 "        'Checking for updates...',$\r$\n"
  FileWrite $0 "        'Ready!'$\r$\n"
  FileWrite $0 "    ]$\r$\n"
  FileWrite $0 "$\r$\n"
  FileWrite $0 "    for i, step in enumerate(steps):$\r$\n"
  FileWrite $0 "        update_progress((i+1) * 100 / len(steps), step)$\r$\n"
  FileWrite $0 "        time.sleep(1)$\r$\n"
  FileWrite $0 "$\r$\n"
  FileWrite $0 "    # Show completion message$\r$\n"
  FileWrite $0 "    messagebox.showinfo('Daur-AI v2.0', 'Демонстрационная версия Daur-AI v2.0 успешно запущена!\\n\\nЭто демонстрационный интерфейс. Для получения полной версии свяжитесь с разработчиком:\\n\\nEmail: daur@daur-ai.tech\\nTelegram: @daur_abd')$\r$\n"
  FileWrite $0 "$\r$\n"
  FileWrite $0 "    root.mainloop()$\r$\n"
  FileWrite $0 "$\r$\n"
  FileWrite $0 "except Exception as e:$\r$\n"
  FileWrite $0 "    print(f'Error: {e}')$\r$\n"
  FileWrite $0 "    import sys$\r$\n"
  FileWrite $0 "    if sys.platform.startswith('win'):$\r$\n"
  FileWrite $0 "        import ctypes$\r$\n"
  FileWrite $0 "        ctypes.windll.user32.MessageBoxW(0, f'Ошибка запуска Daur-AI v2.0:\\n{e}\\n\\nУбедитесь, что Python установлен в системе.', 'Daur-AI v2.0', 0x10)$\r$\n"
  FileWrite $0 "    sys.exit(1)$\r$\n"
  FileClose $0
  
  ; Create README file
  FileOpen $0 "$INSTDIR\README.txt" w
  FileWrite $0 "Daur-AI v2.0$\r$\n"
  FileWrite $0 "=============$\r$\n"
  FileWrite $0 "$\r$\n"
  FileWrite $0 "Спасибо за установку Daur-AI v2.0!$\r$\n"
  FileWrite $0 "$\r$\n"
  FileWrite $0 "Для запуска программы используйте ярлык на рабочем столе$\r$\n"
  FileWrite $0 "или в меню 'Пуск'.$\r$\n"
  FileWrite $0 "$\r$\n"
  FileWrite $0 "Контакты для поддержки:$\r$\n"
  FileWrite $0 "- Email: daur@daur-ai.tech$\r$\n"
  FileWrite $0 "- Telegram: @daur_abd$\r$\n"
  FileWrite $0 "- WhatsApp: +44 7715 433247$\r$\n"
  FileWrite $0 "- Веб-сайт: daur-ai.tech$\r$\n"
  FileClose $0
  
  ; Create uninstaller
  WriteUninstaller "$INSTDIR\Uninstall.exe"
  
  ; Create shortcuts
  CreateDirectory "$SMPROGRAMS\Daur-AI"
  CreateShortcut "$SMPROGRAMS\Daur-AI\Daur-AI v2.0.lnk" "pythonw.exe" '"$INSTDIR\app\main.py"' "$INSTDIR\app\main.py" 0
  CreateShortcut "$SMPROGRAMS\Daur-AI\Uninstall.lnk" "$INSTDIR\Uninstall.exe"
  CreateShortcut "$DESKTOP\Daur-AI v2.0.lnk" "pythonw.exe" '"$INSTDIR\app\main.py"' "$INSTDIR\app\main.py" 0
SectionEnd

;--------------------------------
; Uninstaller Section
Section "Uninstall"
  ; Remove files and directories
  RMDir /r "$INSTDIR\app"
  RMDir /r "$INSTDIR\docs"
  RMDir /r "$INSTDIR\resources"
  Delete "$INSTDIR\README.txt"
  Delete "$INSTDIR\Uninstall.exe"
  RMDir "$INSTDIR"
  
  ; Remove shortcuts
  Delete "$SMPROGRAMS\Daur-AI\Daur-AI v2.0.lnk"
  Delete "$SMPROGRAMS\Daur-AI\Uninstall.lnk"
  RMDir "$SMPROGRAMS\Daur-AI"
  Delete "$DESKTOP\Daur-AI v2.0.lnk"
SectionEnd
