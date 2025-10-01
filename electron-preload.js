const { contextBridge, ipcRenderer } = require('electron');

// Безопасный API для рендер процесса
contextBridge.exposeInMainWorld('electronAPI', {
    // Системные операции
    getSystemStatus: () => ipcRenderer.invoke('get-system-status'),
    
    // Управление агентом
    startAgent: () => ipcRenderer.invoke('start-agent'),
    stopAgent: () => ipcRenderer.invoke('stop-agent'),
    executeCommand: (command) => ipcRenderer.invoke('execute-command', command),
    
    // Telegram бот
    setupTelegramBot: (config) => ipcRenderer.invoke('setup-telegram-bot', config),
    
    // Файловые операции
    selectFile: () => ipcRenderer.invoke('select-file'),
    
    // Уведомления
    showNotification: (title, body) => ipcRenderer.invoke('show-notification', title, body),
    
    // События от главного процесса
    onCreateNewTask: (callback) => ipcRenderer.on('create-new-task', callback),
    onShowAgentStatus: (callback) => ipcRenderer.on('show-agent-status', callback),
    onOpenSettings: (callback) => ipcRenderer.on('open-settings', callback),
    
    // Удаление слушателей
    removeAllListeners: (channel) => ipcRenderer.removeAllListeners(channel),
    
    // Информация о платформе
    platform: process.platform,
    
    // Версия приложения
    version: '2.0.0'
});
