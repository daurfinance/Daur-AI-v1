import React, { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Textarea } from '@/components/ui/textarea.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { ScrollArea } from '@/components/ui/scroll-area.jsx'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert.jsx'
import { 
  Play, 
  Square, 
  Settings, 
  Monitor, 
  Brain, 
  Terminal, 
  FileText, 
  Activity,
  Cpu,
  HardDrive,
  Wifi,
  AlertCircle,
  CheckCircle,
  Clock,
  Send,
  Trash2,
  Download,
  Upload,
  RefreshCw
} from 'lucide-react'
import './App.css'

// API базовый URL
const API_BASE = 'http://localhost:8000'

function App() {
  // Состояние приложения
  const [isConnected, setIsConnected] = useState(false)
  const [agentStatus, setAgentStatus] = useState(null)
  const [currentCommand, setCurrentCommand] = useState('')
  const [commandHistory, setCommandHistory] = useState([])
  const [isExecuting, setIsExecuting] = useState(false)
  const [systemStats, setSystemStats] = useState({
    cpu: { percent: 0 },
    memory: { percent: 0 },
    disk: { percent: 0 },
    processes: { count: 0 }
  })
  const [aiStatus, setAiStatus] = useState({
    manager_type: 'Unknown',
    available: false,
    models: {}
  })
  const [logs, setLogs] = useState([])
  const [testPrompt, setTestPrompt] = useState('Привет! Как дела?')
  const [testResult, setTestResult] = useState(null)
  const [isTesting, setIsTesting] = useState(false)

  // Функция для выполнения API запросов
  const apiCall = async (endpoint, options = {}) => {
    try {
      const response = await fetch(`${API_BASE}${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      })
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }
      
      return await response.json()
    } catch (error) {
      console.error(`API Error (${endpoint}):`, error)
      throw error
    }
  }

  // Проверка подключения к API
  const checkConnection = async () => {
    try {
      await apiCall('/health')
      setIsConnected(true)
    } catch (error) {
      setIsConnected(false)
    }
  }

  // Загрузка системной статистики
  const loadSystemStats = async () => {
    try {
      const data = await apiCall('/system/status')
      setSystemStats(data)
    } catch (error) {
      console.error('Ошибка загрузки системной статистики:', error)
    }
  }

  // Загрузка статуса агента
  const loadAgentStatus = async () => {
    try {
      const data = await apiCall('/agent/status')
      setAgentStatus(data)
    } catch (error) {
      console.error('Ошибка загрузки статуса агента:', error)
    }
  }

  // Загрузка статуса AI
  const loadAiStatus = async () => {
    try {
      const data = await apiCall('/ai/status')
      setAiStatus(data)
    } catch (error) {
      console.error('Ошибка загрузки статуса AI:', error)
    }
  }

  // Загрузка истории команд
  const loadCommandHistory = async () => {
    try {
      const data = await apiCall('/commands/history?limit=20')
      setCommandHistory(data.commands || [])
    } catch (error) {
      console.error('Ошибка загрузки истории команд:', error)
    }
  }

  // Запуск агента
  const startAgent = async () => {
    try {
      await apiCall('/agent/start', { method: 'POST' })
      await loadAgentStatus()
    } catch (error) {
      console.error('Ошибка запуска агента:', error)
    }
  }

  // Остановка агента
  const stopAgent = async () => {
    try {
      await apiCall('/agent/stop', { method: 'POST' })
      await loadAgentStatus()
    } catch (error) {
      console.error('Ошибка остановки агента:', error)
    }
  }

  // Выполнение команды
  const executeCommand = async (command = currentCommand) => {
    if (!command.trim() || isExecuting) return

    setIsExecuting(true)
    try {
      const result = await apiCall('/commands/execute', {
        method: 'POST',
        body: JSON.stringify({ command: command.trim() }),
      })
      
      // Очищаем поле ввода только если команда была из текущего поля
      if (command === currentCommand) {
        setCurrentCommand('')
      }
      
      // Обновляем данные
      await Promise.all([
        loadCommandHistory(),
        loadAgentStatus()
      ])
      
      return result
    } catch (error) {
      console.error('Ошибка выполнения команды:', error)
    } finally {
      setIsExecuting(false)
    }
  }

  // Тестирование AI модели
  const testAiModel = async () => {
    if (!testPrompt.trim() || isTesting) return

    setIsTesting(true)
    try {
      const result = await apiCall('/ai/test', {
        method: 'POST',
        body: JSON.stringify({ prompt: testPrompt.trim() }),
      })
      setTestResult(result)
    } catch (error) {
      setTestResult({ success: false, error: error.message })
    } finally {
      setIsTesting(false)
    }
  }

  // Очистка истории команд
  const clearCommandHistory = async () => {
    try {
      await apiCall('/commands/clear-history', { method: 'POST' })
      await loadCommandHistory()
    } catch (error) {
      console.error('Ошибка очистки истории:', error)
    }
  }

  // Обновление всех данных
  const refreshData = async () => {
    await Promise.all([
      checkConnection(),
      loadSystemStats(),
      loadAgentStatus(),
      loadAiStatus(),
      loadCommandHistory()
    ])
  }

  // Эффект для периодического обновления данных
  useEffect(() => {
    refreshData()
    
    // Обновляем данные каждые 5 секунд
    const interval = setInterval(refreshData, 5000)
    
    return () => clearInterval(interval)
  }, [])

  // Получение цвета индикатора для процентных значений
  const getIndicatorColor = (percent) => {
    if (percent > 80) return 'bg-red-500'
    if (percent > 50) return 'bg-yellow-500'
    return 'bg-green-500'
  }

  // Форматирование времени
  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString('ru-RU')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Заголовок */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-4">
              <h1 className="text-2xl font-bold text-gray-900">Daur-AI</h1>
              <Badge variant="outline">v1.2</Badge>
            </div>
            
            <div className="flex items-center space-x-4">
              <Button
                variant="outline"
                size="sm"
                onClick={refreshData}
                className="flex items-center space-x-2"
              >
                <RefreshCw className="h-4 w-4" />
                <span>Обновить</span>
              </Button>
              
              <div className="flex items-center space-x-2">
                {isConnected ? (
                  <CheckCircle className="h-5 w-5 text-green-500" />
                ) : (
                  <AlertCircle className="h-5 w-5 text-red-500" />
                )}
                <span className="text-sm text-gray-600">
                  {isConnected ? 'Подключено' : 'Нет подключения'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Основной контент */}
      <main className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        <Tabs defaultValue="dashboard" className="space-y-6">
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="dashboard" className="flex items-center space-x-2">
              <Monitor className="h-4 w-4" />
              <span>Панель</span>
            </TabsTrigger>
            <TabsTrigger value="commands" className="flex items-center space-x-2">
              <Terminal className="h-4 w-4" />
              <span>Команды</span>
            </TabsTrigger>
            <TabsTrigger value="ai" className="flex items-center space-x-2">
              <Brain className="h-4 w-4" />
              <span>ИИ Модели</span>
            </TabsTrigger>
            <TabsTrigger value="logs" className="flex items-center space-x-2">
              <FileText className="h-4 w-4" />
              <span>Логи</span>
            </TabsTrigger>
            <TabsTrigger value="settings" className="flex items-center space-x-2">
              <Settings className="h-4 w-4" />
              <span>Настройки</span>
            </TabsTrigger>
          </TabsList>

          {/* Панель управления */}
          <TabsContent value="dashboard" className="space-y-6">
            {/* Системная статистика */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">CPU</CardTitle>
                  <Cpu className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <div className="text-2xl font-bold">{systemStats.cpu?.percent || 0}%</div>
                    <div className={`w-3 h-3 rounded-full ${getIndicatorColor(systemStats.cpu?.percent || 0)}`}></div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Память</CardTitle>
                  <Activity className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <div className="text-2xl font-bold">{systemStats.memory?.percent || 0}%</div>
                    <div className={`w-3 h-3 rounded-full ${getIndicatorColor(systemStats.memory?.percent || 0)}`}></div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Диск</CardTitle>
                  <HardDrive className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <div className="text-2xl font-bold">{systemStats.disk?.percent || 0}%</div>
                    <div className={`w-3 h-3 rounded-full ${getIndicatorColor(systemStats.disk?.percent || 0)}`}></div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Процессы</CardTitle>
                  <Settings className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{systemStats.processes?.count || 0}</div>
                </CardContent>
              </Card>
            </div>

            {/* Управление агентом */}
            <Card>
              <CardHeader>
                <CardTitle>Управление агентом</CardTitle>
                <CardDescription>
                  Статус и управление Daur-AI агентом
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className="flex items-center space-x-2">
                      {agentStatus?.running ? (
                        <CheckCircle className="h-5 w-5 text-green-500" />
                      ) : (
                        <AlertCircle className="h-5 w-5 text-red-500" />
                      )}
                      <span className="font-medium">
                        {agentStatus?.running ? 'Запущен' : 'Остановлен'}
                      </span>
                    </div>
                    
                    {agentStatus?.commands_executed !== undefined && (
                      <Badge variant="secondary">
                        Команд: {agentStatus.commands_executed}
                      </Badge>
                    )}
                  </div>
                  
                  <div className="flex space-x-2">
                    <Button
                      onClick={startAgent}
                      disabled={agentStatus?.running}
                      className="flex items-center space-x-2"
                    >
                      <Play className="h-4 w-4" />
                      <span>Запустить</span>
                    </Button>
                    
                    <Button
                      variant="destructive"
                      onClick={stopAgent}
                      disabled={!agentStatus?.running}
                      className="flex items-center space-x-2"
                    >
                      <Square className="h-4 w-4" />
                      <span>Остановить</span>
                    </Button>
                  </div>
                </div>
                
                {agentStatus?.last_command && (
                  <div className="mt-4 p-3 bg-gray-50 rounded-md">
                    <p className="text-sm text-gray-600">Последняя команда:</p>
                    <p className="text-sm font-mono">{agentStatus.last_command}</p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Быстрые действия */}
            <Card>
              <CardHeader>
                <CardTitle>Быстрые действия</CardTitle>
                <CardDescription>
                  Часто используемые команды
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <Button
                    variant="outline"
                    onClick={() => executeCommand('создай файл test.txt')}
                    className="h-20 flex flex-col items-center justify-center space-y-2"
                    disabled={isExecuting}
                  >
                    <FileText className="h-6 w-6" />
                    <span className="text-xs">Создать файл</span>
                  </Button>
                  
                  <Button
                    variant="outline"
                    onClick={() => executeCommand('покажи процессы')}
                    className="h-20 flex flex-col items-center justify-center space-y-2"
                    disabled={isExecuting}
                  >
                    <Activity className="h-6 w-6" />
                    <span className="text-xs">Процессы</span>
                  </Button>
                  
                  <Button
                    variant="outline"
                    onClick={() => executeCommand('сделай скриншот')}
                    className="h-20 flex flex-col items-center justify-center space-y-2"
                    disabled={isExecuting}
                  >
                    <Download className="h-6 w-6" />
                    <span className="text-xs">Скриншот</span>
                  </Button>
                  
                  <Button
                    variant="outline"
                    onClick={() => executeCommand('помощь')}
                    className="h-20 flex flex-col items-center justify-center space-y-2"
                    disabled={isExecuting}
                  >
                    <AlertCircle className="h-6 w-6" />
                    <span className="text-xs">Справка</span>
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Команды */}
          <TabsContent value="commands" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Выполнение команд */}
              <Card>
                <CardHeader>
                  <CardTitle>Выполнение команд</CardTitle>
                  <CardDescription>
                    Введите команду для выполнения агентом
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <Textarea
                    placeholder="создай файл test.txt с содержимым 'Hello World'"
                    value={currentCommand}
                    onChange={(e) => setCurrentCommand(e.target.value)}
                    className="min-h-[100px]"
                    disabled={isExecuting}
                  />
                  
                  <div className="flex space-x-2">
                    <Button
                      onClick={() => executeCommand()}
                      disabled={!currentCommand.trim() || isExecuting}
                      className="flex-1 flex items-center space-x-2"
                    >
                      {isExecuting ? (
                        <RefreshCw className="h-4 w-4 animate-spin" />
                      ) : (
                        <Send className="h-4 w-4" />
                      )}
                      <span>{isExecuting ? 'Выполняется...' : 'Выполнить'}</span>
                    </Button>
                    
                    <Button
                      variant="outline"
                      onClick={() => setCurrentCommand('')}
                    >
                      Очистить
                    </Button>
                  </div>
                </CardContent>
              </Card>

              {/* История команд */}
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle>История команд</CardTitle>
                      <CardDescription>
                        Последние выполненные команды
                      </CardDescription>
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={clearCommandHistory}
                      className="flex items-center space-x-2"
                    >
                      <Trash2 className="h-4 w-4" />
                      <span>Очистить</span>
                    </Button>
                  </div>
                </CardHeader>
                <CardContent>
                  <ScrollArea className="h-[300px]">
                    {commandHistory.length === 0 ? (
                      <p className="text-gray-500 text-sm">История команд пуста</p>
                    ) : (
                      <div className="space-y-3">
                        {commandHistory.slice(-10).reverse().map((cmd, index) => (
                          <div key={index} className="border-l-4 border-gray-200 pl-3 py-2">
                            <div className="flex items-center justify-between">
                              <span className="text-sm font-mono text-gray-800">{cmd.command}</span>
                              <Badge variant={
                                cmd.status === 'completed' ? 'default' :
                                cmd.status === 'failed' ? 'destructive' : 'secondary'
                              }>
                                {cmd.status}
                              </Badge>
                            </div>
                            {cmd.result?.message && (
                              <p className="text-xs text-gray-600 mt-1">{cmd.result.message}</p>
                            )}
                            <p className="text-xs text-gray-400 mt-1">
                              {formatTime(cmd.timestamp)}
                            </p>
                          </div>
                        ))}
                      </div>
                    )}
                  </ScrollArea>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* AI Модели */}
          <TabsContent value="ai" className="space-y-6">
            {/* Статус AI */}
            <Card>
              <CardHeader>
                <CardTitle>Статус AI моделей</CardTitle>
                <CardDescription>
                  Информация о доступных AI моделях
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-3 bg-gray-50 rounded-md">
                    <div>
                      <span className="font-medium">Менеджер: {aiStatus.manager_type}</span>
                      <span className="text-sm text-gray-600 ml-2">
                        ({aiStatus.available ? 'Доступен' : 'Недоступен'})
                      </span>
                    </div>
                    <div className={`w-3 h-3 rounded-full ${aiStatus.available ? 'bg-green-500' : 'bg-red-500'}`}></div>
                  </div>
                  
                  {aiStatus.models?.ollama && (
                    <div className="flex items-center justify-between p-3 bg-gray-50 rounded-md">
                      <div>
                        <span className="font-medium">Ollama</span>
                        <span className="text-sm text-gray-600 ml-2">
                          ({aiStatus.models.ollama.models?.length || 0} моделей)
                        </span>
                      </div>
                      <div className={`w-3 h-3 rounded-full ${aiStatus.models.ollama.available ? 'bg-green-500' : 'bg-red-500'}`}></div>
                    </div>
                  )}
                  
                  {aiStatus.models?.openai && (
                    <div className="flex items-center justify-between p-3 bg-gray-50 rounded-md">
                      <div>
                        <span className="font-medium">OpenAI</span>
                      </div>
                      <div className={`w-3 h-3 rounded-full ${aiStatus.models.openai.available ? 'bg-green-500' : 'bg-red-500'}`}></div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Тестирование модели */}
            <Card>
              <CardHeader>
                <CardTitle>Тестирование модели</CardTitle>
                <CardDescription>
                  Проверьте работу AI модели
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Тестовый промпт:
                  </label>
                  <Input
                    value={testPrompt}
                    onChange={(e) => setTestPrompt(e.target.value)}
                    placeholder="Введите тестовый промпт"
                  />
                </div>
                
                <Button
                  onClick={testAiModel}
                  disabled={isTesting || !testPrompt.trim()}
                  className="w-full flex items-center space-x-2"
                >
                  {isTesting ? (
                    <RefreshCw className="h-4 w-4 animate-spin" />
                  ) : (
                    <Brain className="h-4 w-4" />
                  )}
                  <span>{isTesting ? 'Тестирование...' : 'Тестировать модель'}</span>
                </Button>
                
                {testResult && (
                  <Alert className={testResult.success ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'}>
                    <AlertTitle>
                      {testResult.success ? 'Успешно' : 'Ошибка'}
                    </AlertTitle>
                    <AlertDescription>
                      {testResult.success ? (
                        <div>
                          <p className="mb-2">Ответ получен за {testResult.response_time}с:</p>
                          <p className="font-mono text-sm">{testResult.response}</p>
                        </div>
                      ) : (
                        <p>{testResult.error}</p>
                      )}
                    </AlertDescription>
                  </Alert>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Логи */}
          <TabsContent value="logs">
            <Card>
              <CardHeader>
                <CardTitle>Системные логи</CardTitle>
                <CardDescription>
                  Последние события системы
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-[400px]">
                  <div className="bg-gray-900 text-green-400 p-4 rounded-md font-mono text-sm space-y-1">
                    <div>2025-10-01 03:08:00 [INFO] API сервер запущен</div>
                    <div>2025-10-01 03:08:01 [INFO] Ollama модель загружена</div>
                    <div>2025-10-01 03:08:02 [INFO] Система готова к работе</div>
                    <div>2025-10-01 03:08:03 [INFO] Веб-панель подключена</div>
                  </div>
                </ScrollArea>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Настройки */}
          <TabsContent value="settings">
            <Card>
              <CardHeader>
                <CardTitle>Настройки</CardTitle>
                <CardDescription>
                  Конфигурация системы
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Alert>
                  <Settings className="h-4 w-4" />
                  <AlertTitle>В разработке</AlertTitle>
                  <AlertDescription>
                    Настройки будут добавлены в следующих версиях.
                  </AlertDescription>
                </Alert>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  )
}

export default App
