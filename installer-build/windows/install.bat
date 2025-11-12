@echo off
echo ===================================================
echo Daur-AI v2.0 Installer for Windows
echo ===================================================
echo.

echo Checking system requirements...
echo.

:: Проверка версии Windows
ver | findstr /i "10\." > nul
if %ERRORLEVEL% EQU 0 (
    echo Windows 10 detected - Compatible
) else (
    ver | findstr /i "11\." > nul
    if %ERRORLEVEL% EQU 0 (
        echo Windows 11 detected - Compatible
    ) else (
        echo WARNING: Unsupported Windows version detected.
        echo Daur-AI is optimized for Windows 10/11.
        echo Installation will continue, but some features may not work correctly.
        echo.
        pause
    )
)

:: Проверка наличия Python
where python > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python not found. Installing Python...
    echo Please download and install Python 3.11 or newer from https://www.python.org/downloads/
    echo After installing Python, run this installer again.
    echo.
    echo Press any key to open the Python download page...
    pause > nul
    start https://www.python.org/downloads/
    exit /b 1
) else (
    echo Python detected - Compatible
)

echo.
echo Creating installation directory...

:: Создание директории установки
set INSTALL_DIR=%LOCALAPPDATA%\Daur-AI
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

echo Copying files...
xcopy /E /I /Y app "%INSTALL_DIR%\app"
xcopy /E /I /Y docs "%INSTALL_DIR%\docs"
xcopy /E /I /Y resources "%INSTALL_DIR%\resources"

echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r "%INSTALL_DIR%\app\requirements.txt"

echo Creating shortcuts...
:: Создание ярлыка на рабочем столе
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%TEMP%\CreateShortcut.vbs"
echo sLinkFile = "%USERPROFILE%\Desktop\Daur-AI.lnk" >> "%TEMP%\CreateShortcut.vbs"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%TEMP%\CreateShortcut.vbs"
echo oLink.TargetPath = "pythonw" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.Arguments = "%INSTALL_DIR%\app\main.py" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.WorkingDirectory = "%INSTALL_DIR%\app" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.IconLocation = "%INSTALL_DIR%\resources\icon.ico" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.Description = "Daur-AI v2.0" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.Save >> "%TEMP%\CreateShortcut.vbs"
cscript /nologo "%TEMP%\CreateShortcut.vbs"
del "%TEMP%\CreateShortcut.vbs"

:: Создание ярлыка в меню Пуск
set START_MENU=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Daur-AI
if not exist "%START_MENU%" mkdir "%START_MENU%"

echo Set oWS = WScript.CreateObject("WScript.Shell") > "%TEMP%\CreateStartShortcut.vbs"
echo sLinkFile = "%START_MENU%\Daur-AI.lnk" >> "%TEMP%\CreateStartShortcut.vbs"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%TEMP%\CreateStartShortcut.vbs"
echo oLink.TargetPath = "pythonw" >> "%TEMP%\CreateStartShortcut.vbs"
echo oLink.Arguments = "%INSTALL_DIR%\app\main.py" >> "%TEMP%\CreateStartShortcut.vbs"
echo oLink.WorkingDirectory = "%INSTALL_DIR%\app" >> "%TEMP%\CreateStartShortcut.vbs"
echo oLink.IconLocation = "%INSTALL_DIR%\resources\icon.ico" >> "%TEMP%\CreateStartShortcut.vbs"
echo oLink.Description = "Daur-AI v2.0" >> "%TEMP%\CreateStartShortcut.vbs"
echo oLink.Save >> "%TEMP%\CreateStartShortcut.vbs"
cscript /nologo "%TEMP%\CreateStartShortcut.vbs"
del "%TEMP%\CreateStartShortcut.vbs"

echo.
echo ===================================================
echo Installation completed successfully!
echo.
echo Daur-AI v2.0 has been installed to:
echo %INSTALL_DIR%
echo.
echo Shortcuts have been created on your desktop and in the Start Menu.
echo.
echo To launch Daur-AI, double-click the shortcut or run:
echo pythonw "%INSTALL_DIR%\app\main.py"
echo.
echo For more information, see the documentation in:
echo %INSTALL_DIR%\docs
echo ===================================================
echo.

pause
