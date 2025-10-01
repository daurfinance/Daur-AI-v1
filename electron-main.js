const { app, BrowserWindow, Menu, ipcMain, dialog, shell, Tray, nativeImage } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');
const os = require('os');

// Глобальные переменные
let mainWindow;
let tray;
let apiServer;
let isQuitting = false;

// Конфигурация приложения
const APP_CONFIG = {
    name: 'Daur-AI',
    version: '2.0.0',
    description: 'Автономный AI-агент с компьютерным зрением',
    apiPort: 8000,
    webPort: 5174
};

class DaurAIElectronApp {
    constructor() {
        this.setupApp();
    }

    setupApp() {
        // Настройка приложения
        app.setName(APP_CONFIG.name);
        
        // События приложения
        app.whenReady().then(() => {
            this.createMainWindow();
            this.createTray();
            this.setupMenu();
            this.startBackendServices();
            this.setupIPC();
        });

        app.on('window-all-closed', () => {
            if (process.platform !== 'darwin') {
                this.cleanup();
                app.quit();
            }
        });

        app.on('activate', () => {
            if (BrowserWindow.getAllWindows().length === 0) {
                this.createMainWindow();
            }
        });

        app.on('before-quit', () => {
            isQuitting = true;
            this.cleanup();
        });
    }

    createMainWindow() {
        // Создание главного окна
        mainWindow = new BrowserWindow({
            width: 1400,
            height: 900,
            minWidth: 1200,
            minHeight: 700,
            icon: this.getAppIcon(),
            webPreferences: {
                nodeIntegration: false,
                contextIsolation: true,
                enableRemoteModule: false,
                preload: path.join(__dirname, 'electron-preload.js')
            },
            titleBarStyle: 'default',
            show: false, // Не показываем сразу
            backgroundColor: '#1a1a2e'
        });

        // Загружаем интерфейс
        this.loadInterface();

        // События окна
        mainWindow.once('ready-to-show', () => {
            mainWindow.show();
            
            // Показываем splash screen
            this.showSplashScreen();
        });

        mainWindow.on('close', (event) => {
            if (!isQuitting) {
                event.preventDefault();
                mainWindow.hide();
                
                // Показываем уведомление о сворачивании в трей
                this.showNotification('Daur-AI продолжает работать в фоне');
            }
        });

        mainWindow.webContents.setWindowOpenHandler(({ url }) => {
            shell.openExternal(url);
            return { action: 'deny' };
        });
    }

    createTray() {
        // Создание иконки в системном трее
        const trayIcon = this.getAppIcon();
        tray = new Tray(trayIcon);

        const contextMenu = Menu.buildFromTemplate([
            {
                label: 'Показать Daur-AI',
                click: () => {
                    mainWindow.show();
                    mainWindow.focus();
                }
            },
            {
                label: 'Статус агента',
                click: () => this.showAgentStatus()
            },
            { type: 'separator' },
            {
                label: 'Настройки',
                click: () => this.openSettings()
            },
            {
                label: 'Логи',
                click: () => this.openLogs()
            },
            { type: 'separator' },
            {
                label: 'Выход',
                click: () => {
                    isQuitting = true;
                    app.quit();
                }
            }
        ]);

        tray.setToolTip('Daur-AI - Автономный AI-агент');
        tray.setContextMenu(contextMenu);

        tray.on('double-click', () => {
            mainWindow.show();
            mainWindow.focus();
        });
    }

    setupMenu() {
        // Создание меню приложения
        const template = [
            {
                label: 'Файл',
                submenu: [
                    {
                        label: 'Новая задача',
                        accelerator: 'CmdOrCtrl+N',
                        click: () => this.createNewTask()
                    },
                    {
                        label: 'Импорт конфигурации',
                        click: () => this.importConfig()
                    },
                    {
                        label: 'Экспорт логов',
                        click: () => this.exportLogs()
                    },
                    { type: 'separator' },
                    {
                        label: 'Выход',
                        accelerator: process.platform === 'darwin' ? 'Cmd+Q' : 'Ctrl+Q',
                        click: () => {
                            isQuitting = true;
                            app.quit();
                        }
                    }
                ]
            },
            {
                label: 'Агент',
                submenu: [
                    {
                        label: 'Запустить агента',
                        accelerator: 'CmdOrCtrl+R',
                        click: () => this.startAgent()
                    },
                    {
                        label: 'Остановить агента',
                        accelerator: 'CmdOrCtrl+S',
                        click: () => this.stopAgent()
                    },
                    {
                        label: 'Перезапустить агента',
                        accelerator: 'CmdOrCtrl+Shift+R',
                        click: () => this.restartAgent()
                    },
                    { type: 'separator' },
                    {
                        label: 'Статус системы',
                        click: () => this.showSystemStatus()
                    }
                ]
            },
            {
                label: 'Инструменты',
                submenu: [
                    {
                        label: 'Telegram бот',
                        click: () => this.openTelegramBot()
                    },
                    {
                        label: 'Компьютерное зрение',
                        click: () => this.openVisionTools()
                    },
                    {
                        label: 'Настройки AI',
                        click: () => this.openAISettings()
                    },
                    { type: 'separator' },
                    {
                        label: 'Консоль разработчика',
                        accelerator: 'F12',
                        click: () => mainWindow.webContents.openDevTools()
                    }
                ]
            },
            {
                label: 'Справка',
                submenu: [
                    {
                        label: 'Документация',
                        click: () => shell.openExternal('https://github.com/daurfinance/Daur-AI-v1')
                    },
                    {
                        label: 'Горячие клавиши',
                        click: () => this.showHotkeys()
                    },
                    {
                        label: 'О программе',
                        click: () => this.showAbout()
                    }
                ]
            }
        ];

        const menu = Menu.buildFromTemplate(template);
        Menu.setApplicationMenu(menu);
    }

    setupIPC() {
        // Настройка межпроцессного взаимодействия
        
        // Получение статуса системы
        ipcMain.handle('get-system-status', async () => {
            return await this.getSystemStatus();
        });

        // Управление агентом
        ipcMain.handle('start-agent', async () => {
            return await this.startAgent();
        });

        ipcMain.handle('stop-agent', async () => {
            return await this.stopAgent();
        });

        // Выполнение команд
        ipcMain.handle('execute-command', async (event, command) => {
            return await this.executeCommand(command);
        });

        // Настройки Telegram бота
        ipcMain.handle('setup-telegram-bot', async (event, config) => {
            return await this.setupTelegramBot(config);
        });

        // Работа с файлами
        ipcMain.handle('select-file', async () => {
            const result = await dialog.showOpenDialog(mainWindow, {
                properties: ['openFile'],
                filters: [
                    { name: 'Все файлы', extensions: ['*'] },
                    { name: 'Изображения', extensions: ['jpg', 'png', 'gif', 'bmp'] },
                    { name: 'Документы', extensions: ['txt', 'pdf', 'doc', 'docx'] }
                ]
            });
            
            return result.filePaths[0] || null;
        });

        // Уведомления
        ipcMain.handle('show-notification', (event, title, body) => {
            this.showNotification(title, body);
        });
    }

    loadInterface() {
        // Загрузка веб-интерфейса
        const isDev = process.env.NODE_ENV === 'development';
        
        if (isDev) {
            // В режиме разработки загружаем с dev сервера
            mainWindow.loadURL(`http://localhost:${APP_CONFIG.webPort}`);
        } else {
            // В продакшене загружаем статические файлы
            const indexPath = path.join(__dirname, 'daur-ai-advanced-panel', 'dist', 'index.html');
            
            if (fs.existsSync(indexPath)) {
                mainWindow.loadFile(indexPath);
            } else {
                // Fallback на простую страницу
                mainWindow.loadFile(path.join(__dirname, 'electron-fallback.html'));
            }
        }
    }

    async startBackendServices() {
        // Запуск backend сервисов
        try {
            console.log('Запуск API сервера...');
            
            const apiServerPath = path.join(__dirname, 'src', 'web', 'enhanced_api_server.py');
            
            if (fs.existsSync(apiServerPath)) {
                apiServer = spawn('python3', [apiServerPath], {
                    cwd: __dirname,
                    stdio: ['pipe', 'pipe', 'pipe']
                });

                apiServer.stdout.on('data', (data) => {
                    console.log(`API Server: ${data}`);
                });

                apiServer.stderr.on('data', (data) => {
                    console.error(`API Server Error: ${data}`);
                });

                // Ждем запуска сервера
                await this.waitForServer(APP_CONFIG.apiPort);
                console.log('API сервер запущен');
            }
        } catch (error) {
            console.error('Ошибка запуска backend сервисов:', error);
        }
    }

    async waitForServer(port, timeout = 10000) {
        // Ожидание запуска сервера
        const startTime = Date.now();
        
        while (Date.now() - startTime < timeout) {
            try {
                const response = await fetch(`http://localhost:${port}/health`);
                if (response.ok) {
                    return true;
                }
            } catch (error) {
                // Сервер еще не готов
            }
            
            await new Promise(resolve => setTimeout(resolve, 500));
        }
        
        throw new Error(`Сервер не запустился в течение ${timeout}ms`);
    }

    getAppIcon() {
        // Получение иконки приложения
        const iconPath = path.join(__dirname, 'assets', 'icon.png');
        
        if (fs.existsSync(iconPath)) {
            return nativeImage.createFromPath(iconPath);
        } else {
            // Создаем простую иконку программно
            const canvas = require('canvas');
            const canvasInstance = canvas.createCanvas(64, 64);
            const ctx = canvasInstance.getContext('2d');
            
            // Рисуем простую иконку
            ctx.fillStyle = '#4f46e5';
            ctx.fillRect(0, 0, 64, 64);
            ctx.fillStyle = '#ffffff';
            ctx.font = '32px Arial';
            ctx.textAlign = 'center';
            ctx.fillText('AI', 32, 42);
            
            return nativeImage.createFromBuffer(canvasInstance.toBuffer());
        }
    }

    showSplashScreen() {
        // Показ заставки при запуске
        const splash = new BrowserWindow({
            width: 400,
            height: 300,
            frame: false,
            alwaysOnTop: true,
            transparent: true,
            webPreferences: {
                nodeIntegration: false
            }
        });

        splash.loadFile(path.join(__dirname, 'electron-splash.html'));
        
        setTimeout(() => {
            splash.close();
        }, 3000);
    }

    showNotification(title, body = '') {
        // Показ системного уведомления
        const { Notification } = require('electron');
        
        if (Notification.isSupported()) {
            new Notification({
                title: title,
                body: body,
                icon: this.getAppIcon()
            }).show();
        }
    }

    async getSystemStatus() {
        // Получение статуса системы
        try {
            const response = await fetch(`http://localhost:${APP_CONFIG.apiPort}/system/status`);
            return await response.json();
        } catch (error) {
            return { error: 'API недоступен' };
        }
    }

    async startAgent() {
        // Запуск агента
        try {
            const response = await fetch(`http://localhost:${APP_CONFIG.apiPort}/agent/start`, {
                method: 'POST'
            });
            return await response.json();
        } catch (error) {
            return { error: error.message };
        }
    }

    async stopAgent() {
        // Остановка агента
        try {
            const response = await fetch(`http://localhost:${APP_CONFIG.apiPort}/agent/stop`, {
                method: 'POST'
            });
            return await response.json();
        } catch (error) {
            return { error: error.message };
        }
    }

    async executeCommand(command) {
        // Выполнение команды через агента
        try {
            const response = await fetch(`http://localhost:${APP_CONFIG.apiPort}/agent/execute`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ command })
            });
            return await response.json();
        } catch (error) {
            return { error: error.message };
        }
    }

    cleanup() {
        // Очистка ресурсов при закрытии
        if (apiServer) {
            apiServer.kill();
        }
    }

    // Дополнительные методы для меню
    createNewTask() {
        mainWindow.webContents.send('create-new-task');
    }

    showAgentStatus() {
        mainWindow.webContents.send('show-agent-status');
    }

    openSettings() {
        mainWindow.webContents.send('open-settings');
    }

    showAbout() {
        dialog.showMessageBox(mainWindow, {
            type: 'info',
            title: 'О программе',
            message: `${APP_CONFIG.name} v${APP_CONFIG.version}`,
            detail: `${APP_CONFIG.description}\n\nАвтономный AI-агент с компьютерным зрением и системой самообучения.`
        });
    }
}

// Запуск приложения
new DaurAIElectronApp();
