import { useState, useEffect, useRef } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { ScrollArea } from '@/components/ui/scroll-area.jsx'
import { Textarea } from '@/components/ui/textarea.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Label } from '@/components/ui/label.jsx'
import { Switch } from '@/components/ui/switch.jsx'
import { 
  Activity, 
  Brain, 
  Camera, 
  Cpu, 
  Eye, 
  HardDrive, 
  Keyboard, 
  MemoryStick, 
  Monitor, 
  Mouse, 
  Play, 
  Pause, 
  Square, 
  Settings, 
  Zap,
  Globe,
  FileText,
  Image,
  Video,
  Mic,
  Speaker,
  Terminal,
  ChevronRight,
  CheckCircle,
  XCircle,
  Clock,
  AlertTriangle,
  TrendingUp,
  BarChart3,
  PieChart,
  LineChart
} from 'lucide-react'
import { LineChart as RechartsLineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area, BarChart, Bar, PieChart as RechartsPieChart, Cell } from 'recharts'
import './App.css'

function App() {
  // Состояние агента
  const [agentStatus, setAgentStatus] = useState('stopped')
  const [isConnected, setIsConnected] = useState(true)
  const [currentTask, setCurrentTask] = useState(null)
  
  // Системная статистика
  const [systemStats, setSystemStats] = useState({
    cpu: 45,
    memory: 62,
    disk: 78,
    processes: 156,
    uptime: '2h 34m'
  })
  
  // Статистика устройств
  const [deviceStats, setDeviceStats] = useState({
    screen: { status: 'active', lastUsed: '2 min ago', operations: 45 },
    keyboard: { status: 'idle', lastUsed: '5 min ago', operations: 23 },
    mouse: { status: 'active', lastUsed: '1 min ago', operations: 67 },
    camera: { status: 'offline', lastUsed: '1h ago', operations: 0 },
    browser: { status: 'active', lastUsed: '30s ago', operations: 12 },
    system: { status: 'active', lastUsed: '10s ago', operations: 89 }
  })
  
  // AI модели
  const [aiModels, setAiModels] = useState({
    textModel: { name: 'Ollama Llama 3.2', status: 'ready', confidence: 0.95 },
    visionModel: { name: 'Computer Vision', status: 'ready', confidence: 0.87 },
    multimodal: { name: 'Multimodal AI', status: 'ready', confidence: 0.92 }
  })
  
  // Задачи и команды
  const [tasks, setTasks] = useState([
    { id: 1, description: 'Создать файл test.txt', status: 'completed', progress: 100, startTime: '14:23', duration: '2.3s' },
    { id: 2, description: 'Открыть браузер и найти информацию', status: 'running', progress: 65, startTime: '14:25', duration: '45s' },
    { id: 3, description: 'Сделать скриншот экрана', status: 'pending', progress: 0, startTime: null, duration: null }
  ])
  
  // Логи активности
  const [activityLogs, setActivityLogs] = useState([
    { time: '14:26:15', type: 'system', message: 'Выполнена команда: создать файл test.txt', status: 'success' },
    { time: '14:26:10', type: 'browser', message: 'Переход на страницу: https://google.com', status: 'success' },
    { time: '14:26:05', type: 'input', message: 'Клик по координатам (450, 300)', status: 'success' },
    { time: '14:25:58', type: 'vision', message: 'OCR анализ завершен: найдено 15 текстовых элементов', status: 'success' },
    { time: '14:25:45', type: 'ai', message: 'Обработка запроса: "найди информацию о погоде"', status: 'processing' },
    { time: '14:25:30', type: 'system', message: 'Агент запущен успешно', status: 'success' }
  ])
  
  // Данные для графиков
  const [performanceData, setPerformanceData] = useState([
    { time: '14:20', cpu: 35, memory: 45, tasks: 2 },
    { time: '14:21', cpu: 42, memory: 48, tasks: 3 },
    { time: '14:22', cpu: 38, memory: 52, tasks: 2 },
    { time: '14:23', cpu: 45, memory: 58, tasks: 4 },
    { time: '14:24', cpu: 52, memory: 62, tasks: 3 },
    { time: '14:25', cpu: 48, memory: 65, tasks: 5 },
    { time: '14:26', cpu: 45, memory: 62, tasks: 3 }
  ])
  
  // Визуализация действий
  const [currentAction, setCurrentAction] = useState({
    type: 'browser',
    description: 'Поиск элемента на странице',
    coordinates: { x: 450, y: 300 },
    confidence: 0.89,
    timestamp: Date.now()
  })
  
  // Форма команд
  const [commandInput, setCommandInput] = useState('')
  const [isExecuting, setIsExecuting] = useState(false)
  
  // Настройки
  const [settings, setSettings] = useState({
    autoMode: true,
    visualFeedback: true,
    soundNotifications: false,
    debugMode: false,
    learningMode: true
  })
  
  // Обновление данных в реальном времени
  useEffect(() => {
    const interval = setInterval(() => {
      // Обновление системной статистики
      setSystemStats(prev => ({
        ...prev,
        cpu: Math.max(20, Math.min(90, prev.cpu + (Math.random() - 0.5) * 10)),
        memory: Math.max(30, Math.min(95, prev.memory + (Math.random() - 0.5) * 5))
      }))
      
      // Обновление данных производительности
      setPerformanceData(prev => {
        const newData = [...prev.slice(1)]
        const lastTime = new Date()
        newData.push({
          time: lastTime.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' }),
          cpu: Math.max(20, Math.min(90, prev[prev.length - 1].cpu + (Math.random() - 0.5) * 10)),
          memory: Math.max(30, Math.min(95, prev[prev.length - 1].memory + (Math.random() - 0.5) * 5)),
          tasks: Math.max(0, Math.min(10, prev[prev.length - 1].tasks + Math.floor((Math.random() - 0.5) * 3)))
        })
        return newData
      })
      
      // Обновление текущего действия
      if (agentStatus === 'running') {
        const actions = [
          { type: 'screen', description: 'Анализ экрана', coordinates: { x: Math.random() * 800, y: Math.random() * 600 } },
          { type: 'mouse', description: 'Перемещение курсора', coordinates: { x: Math.random() * 800, y: Math.random() * 600 } },
          { type: 'keyboard', description: 'Ввод текста', coordinates: null },
          { type: 'browser', description: 'Поиск элемента', coordinates: { x: Math.random() * 800, y: Math.random() * 600 } },
          { type: 'vision', description: 'OCR распознавание', coordinates: null }
        ]
        
        const randomAction = actions[Math.floor(Math.random() * actions.length)]
        setCurrentAction({
          ...randomAction,
          confidence: 0.7 + Math.random() * 0.3,
          timestamp: Date.now()
        })
      }
    }, 2000)
    
    return () => clearInterval(interval)
  }, [agentStatus])
  
  // Функции управления агентом
  const startAgent = () => {
    setAgentStatus('running')
    addActivityLog('system', 'Агент запущен', 'success')
  }
  
  const stopAgent = () => {
    setAgentStatus('stopped')
    addActivityLog('system', 'Агент остановлен', 'success')
  }
  
  const pauseAgent = () => {
    setAgentStatus('paused')
    addActivityLog('system', 'Агент приостановлен', 'warning')
  }
  
  // Выполнение команды
  const executeCommand = async () => {
    if (!commandInput.trim()) return
    
    setIsExecuting(true)
    addActivityLog('user', `Команда: ${commandInput}`, 'processing')
    
    // Симуляция выполнения команды
    setTimeout(() => {
      const newTask = {
        id: tasks.length + 1,
        description: commandInput,
        status: 'running',
        progress: 0,
        startTime: new Date().toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' }),
        duration: null
      }
      
      setTasks(prev => [...prev, newTask])
      setCommandInput('')
      setIsExecuting(false)
      
      addActivityLog('system', `Задача создана: ${commandInput}`, 'success')
    }, 1000)
  }
  
  // Добавление лога активности
  const addActivityLog = (type, message, status) => {
    const newLog = {
      time: new Date().toLocaleTimeString('ru-RU'),
      type,
      message,
      status
    }
    
    setActivityLogs(prev => [newLog, ...prev.slice(0, 49)]) // Ограничиваем до 50 записей
  }
  
  // Получение иконки статуса
  const getStatusIcon = (status) => {
    switch (status) {
      case 'success': return <CheckCircle className="w-4 h-4 text-green-500" />
      case 'error': return <XCircle className="w-4 h-4 text-red-500" />
      case 'warning': return <AlertTriangle className="w-4 h-4 text-yellow-500" />
      case 'processing': return <Clock className="w-4 h-4 text-blue-500 animate-spin" />
      default: return <Activity className="w-4 h-4 text-gray-500" />
    }
  }
  
  // Получение цвета статуса устройства
  const getDeviceStatusColor = (status) => {
    switch (status) {
      case 'active': return 'bg-green-500'
      case 'idle': return 'bg-yellow-500'
      case 'offline': return 'bg-red-500'
      default: return 'bg-gray-500'
    }
  }
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white">
      {/* Заголовок */}
      <header className="border-b border-white/10 bg-black/20 backdrop-blur-sm">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <Brain className="w-8 h-8 text-purple-400" />
                <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                  Daur-AI Advanced Control Panel
                </h1>
              </div>
              <Badge variant={isConnected ? "default" : "destructive"} className="ml-4">
                {isConnected ? "Подключено" : "Отключено"}
              </Badge>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className={`w-3 h-3 rounded-full ${agentStatus === 'running' ? 'bg-green-500 animate-pulse' : agentStatus === 'paused' ? 'bg-yellow-500' : 'bg-red-500'}`}></div>
                <span className="text-sm font-medium">
                  {agentStatus === 'running' ? 'Активен' : agentStatus === 'paused' ? 'Приостановлен' : 'Остановлен'}
                </span>
              </div>
              
              <div className="flex space-x-2">
                <Button 
                  onClick={startAgent} 
                  disabled={agentStatus === 'running'}
                  size="sm"
                  className="bg-green-600 hover:bg-green-700"
                >
                  <Play className="w-4 h-4 mr-1" />
                  Запустить
                </Button>
                <Button 
                  onClick={pauseAgent} 
                  disabled={agentStatus !== 'running'}
                  size="sm"
                  variant="outline"
                >
                  <Pause className="w-4 h-4 mr-1" />
                  Пауза
                </Button>
                <Button 
                  onClick={stopAgent} 
                  disabled={agentStatus === 'stopped'}
                  size="sm"
                  variant="destructive"
                >
                  <Square className="w-4 h-4 mr-1" />
                  Стоп
                </Button>
              </div>
            </div>
          </div>
        </div>
      </header>
      
      {/* Основной контент */}
      <main className="container mx-auto px-6 py-6">
        <Tabs defaultValue="dashboard" className="space-y-6">
          <TabsList className="grid w-full grid-cols-6 bg-black/20 backdrop-blur-sm">
            <TabsTrigger value="dashboard" className="data-[state=active]:bg-purple-600">
              <BarChart3 className="w-4 h-4 mr-2" />
              Панель
            </TabsTrigger>
            <TabsTrigger value="devices" className="data-[state=active]:bg-purple-600">
              <Monitor className="w-4 h-4 mr-2" />
              Устройства
            </TabsTrigger>
            <TabsTrigger value="tasks" className="data-[state=active]:bg-purple-600">
              <Activity className="w-4 h-4 mr-2" />
              Задачи
            </TabsTrigger>
            <TabsTrigger value="vision" className="data-[state=active]:bg-purple-600">
              <Eye className="w-4 h-4 mr-2" />
              Зрение
            </TabsTrigger>
            <TabsTrigger value="ai" className="data-[state=active]:bg-purple-600">
              <Brain className="w-4 h-4 mr-2" />
              ИИ Модели
            </TabsTrigger>
            <TabsTrigger value="settings" className="data-[state=active]:bg-purple-600">
              <Settings className="w-4 h-4 mr-2" />
              Настройки
            </TabsTrigger>
          </TabsList>
          
          {/* Панель управления */}
          <TabsContent value="dashboard" className="space-y-6">
            {/* Системная статистика */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <Card className="bg-black/20 backdrop-blur-sm border-white/10">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium text-white/80">CPU</CardTitle>
                  <Cpu className="h-4 w-4 text-blue-400" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-white">{systemStats.cpu}%</div>
                  <Progress value={systemStats.cpu} className="mt-2" />
                </CardContent>
              </Card>
              
              <Card className="bg-black/20 backdrop-blur-sm border-white/10">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium text-white/80">Память</CardTitle>
                  <MemoryStick className="h-4 w-4 text-green-400" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-white">{systemStats.memory}%</div>
                  <Progress value={systemStats.memory} className="mt-2" />
                </CardContent>
              </Card>
              
              <Card className="bg-black/20 backdrop-blur-sm border-white/10">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium text-white/80">Диск</CardTitle>
                  <HardDrive className="h-4 w-4 text-orange-400" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-white">{systemStats.disk}%</div>
                  <Progress value={systemStats.disk} className="mt-2" />
                </CardContent>
              </Card>
              
              <Card className="bg-black/20 backdrop-blur-sm border-white/10">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium text-white/80">Процессы</CardTitle>
                  <Activity className="h-4 w-4 text-purple-400" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-white">{systemStats.processes}</div>
                  <p className="text-xs text-white/60 mt-1">Активных процессов</p>
                </CardContent>
              </Card>
            </div>
            
            {/* Графики производительности */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card className="bg-black/20 backdrop-blur-sm border-white/10">
                <CardHeader>
                  <CardTitle className="text-white">Производительность системы</CardTitle>
                  <CardDescription className="text-white/60">CPU и память в реальном времени</CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <AreaChart data={performanceData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                      <XAxis dataKey="time" stroke="rgba(255,255,255,0.6)" />
                      <YAxis stroke="rgba(255,255,255,0.6)" />
                      <Tooltip 
                        contentStyle={{ 
                          backgroundColor: 'rgba(0,0,0,0.8)', 
                          border: '1px solid rgba(255,255,255,0.2)',
                          borderRadius: '8px',
                          color: 'white'
                        }} 
                      />
                      <Area type="monotone" dataKey="cpu" stackId="1" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.6} />
                      <Area type="monotone" dataKey="memory" stackId="1" stroke="#10b981" fill="#10b981" fillOpacity={0.6} />
                    </AreaChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
              
              <Card className="bg-black/20 backdrop-blur-sm border-white/10">
                <CardHeader>
                  <CardTitle className="text-white">Активность задач</CardTitle>
                  <CardDescription className="text-white/60">Количество выполняемых задач</CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={performanceData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                      <XAxis dataKey="time" stroke="rgba(255,255,255,0.6)" />
                      <YAxis stroke="rgba(255,255,255,0.6)" />
                      <Tooltip 
                        contentStyle={{ 
                          backgroundColor: 'rgba(0,0,0,0.8)', 
                          border: '1px solid rgba(255,255,255,0.2)',
                          borderRadius: '8px',
                          color: 'white'
                        }} 
                      />
                      <Bar dataKey="tasks" fill="#8b5cf6" />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </div>
            
            {/* Текущее действие и логи */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Текущее действие */}
              <Card className="bg-black/20 backdrop-blur-sm border-white/10">
                <CardHeader>
                  <CardTitle className="text-white flex items-center">
                    <Zap className="w-5 h-5 mr-2 text-yellow-400" />
                    Текущее действие
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {agentStatus === 'running' ? (
                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <span className="text-white/80">{currentAction.description}</span>
                        <Badge variant="outline" className="text-purple-400 border-purple-400">
                          {currentAction.type}
                        </Badge>
                      </div>
                      
                      {currentAction.coordinates && (
                        <div className="text-sm text-white/60">
                          Координаты: ({Math.round(currentAction.coordinates.x)}, {Math.round(currentAction.coordinates.y)})
                        </div>
                      )}
                      
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-white/60">Уверенность:</span>
                        <span className="text-sm font-medium text-white">
                          {Math.round(currentAction.confidence * 100)}%
                        </span>
                      </div>
                      
                      <Progress value={currentAction.confidence * 100} className="mt-2" />
                    </div>
                  ) : (
                    <div className="text-center text-white/60 py-8">
                      <Activity className="w-12 h-12 mx-auto mb-4 opacity-50" />
                      <p>Агент не активен</p>
                    </div>
                  )}
                </CardContent>
              </Card>
              
              {/* Логи активности */}
              <Card className="bg-black/20 backdrop-blur-sm border-white/10">
                <CardHeader>
                  <CardTitle className="text-white">Логи активности</CardTitle>
                  <CardDescription className="text-white/60">Последние действия агента</CardDescription>
                </CardHeader>
                <CardContent>
                  <ScrollArea className="h-64">
                    <div className="space-y-2">
                      {activityLogs.map((log, index) => (
                        <div key={index} className="flex items-start space-x-3 p-2 rounded-lg bg-white/5">
                          {getStatusIcon(log.status)}
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center justify-between">
                              <span className="text-xs text-white/60">{log.time}</span>
                              <Badge variant="outline" className="text-xs">
                                {log.type}
                              </Badge>
                            </div>
                            <p className="text-sm text-white/80 mt-1">{log.message}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </ScrollArea>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
          
          {/* Устройства */}
          <TabsContent value="devices" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {Object.entries(deviceStats).map(([device, stats]) => {
                const icons = {
                  screen: Monitor,
                  keyboard: Keyboard,
                  mouse: Mouse,
                  camera: Camera,
                  browser: Globe,
                  system: Terminal
                }
                
                const Icon = icons[device] || Activity
                
                return (
                  <Card key={device} className="bg-black/20 backdrop-blur-sm border-white/10">
                    <CardHeader>
                      <CardTitle className="text-white flex items-center justify-between">
                        <div className="flex items-center">
                          <Icon className="w-5 h-5 mr-2 text-purple-400" />
                          {device.charAt(0).toUpperCase() + device.slice(1)}
                        </div>
                        <div className={`w-3 h-3 rounded-full ${getDeviceStatusColor(stats.status)}`}></div>
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        <div className="flex justify-between">
                          <span className="text-white/60">Статус:</span>
                          <span className="text-white capitalize">{stats.status}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-white/60">Последнее использование:</span>
                          <span className="text-white">{stats.lastUsed}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-white/60">Операций:</span>
                          <span className="text-white font-medium">{stats.operations}</span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                )
              })}
            </div>
          </TabsContent>
          
          {/* Задачи */}
          <TabsContent value="tasks" className="space-y-6">
            {/* Форма создания задачи */}
            <Card className="bg-black/20 backdrop-blur-sm border-white/10">
              <CardHeader>
                <CardTitle className="text-white">Создать новую задачу</CardTitle>
                <CardDescription className="text-white/60">
                  Введите команду для выполнения агентом
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex space-x-4">
                  <Textarea
                    placeholder="Например: создай файл test.txt с содержимым 'Hello World'"
                    value={commandInput}
                    onChange={(e) => setCommandInput(e.target.value)}
                    className="flex-1 bg-white/10 border-white/20 text-white placeholder:text-white/40"
                    rows={3}
                  />
                  <Button 
                    onClick={executeCommand}
                    disabled={isExecuting || !commandInput.trim()}
                    className="bg-purple-600 hover:bg-purple-700"
                  >
                    {isExecuting ? (
                      <Clock className="w-4 h-4 mr-2 animate-spin" />
                    ) : (
                      <Play className="w-4 h-4 mr-2" />
                    )}
                    Выполнить
                  </Button>
                </div>
              </CardContent>
            </Card>
            
            {/* Список задач */}
            <Card className="bg-black/20 backdrop-blur-sm border-white/10">
              <CardHeader>
                <CardTitle className="text-white">Активные задачи</CardTitle>
                <CardDescription className="text-white/60">
                  Текущие и завершенные задачи агента
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {tasks.map((task) => (
                    <div key={task.id} className="p-4 rounded-lg bg-white/5 border border-white/10">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-white font-medium">{task.description}</span>
                        <Badge 
                          variant={task.status === 'completed' ? 'default' : task.status === 'running' ? 'secondary' : 'outline'}
                          className={
                            task.status === 'completed' ? 'bg-green-600' :
                            task.status === 'running' ? 'bg-blue-600' : 'bg-gray-600'
                          }
                        >
                          {task.status === 'completed' ? 'Завершено' :
                           task.status === 'running' ? 'Выполняется' : 'Ожидает'}
                        </Badge>
                      </div>
                      
                      <div className="flex items-center justify-between text-sm text-white/60 mb-2">
                        <span>Прогресс: {task.progress}%</span>
                        <span>
                          {task.startTime && `Начато: ${task.startTime}`}
                          {task.duration && ` | Длительность: ${task.duration}`}
                        </span>
                      </div>
                      
                      <Progress value={task.progress} className="mt-2" />
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
          
          {/* Компьютерное зрение */}
          <TabsContent value="vision" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Анализ экрана */}
              <Card className="bg-black/20 backdrop-blur-sm border-white/10">
                <CardHeader>
                  <CardTitle className="text-white flex items-center">
                    <Eye className="w-5 h-5 mr-2 text-blue-400" />
                    Анализ экрана
                  </CardTitle>
                  <CardDescription className="text-white/60">
                    Визуальное распознавание и OCR
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="aspect-video bg-gradient-to-br from-blue-900/20 to-purple-900/20 rounded-lg border border-white/10 flex items-center justify-center">
                      <div className="text-center text-white/60">
                        <Monitor className="w-12 h-12 mx-auto mb-2 opacity-50" />
                        <p>Предварительный просмотр экрана</p>
                        <p className="text-xs mt-1">Захват экрана в реальном времени</p>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-4">
                      <Button variant="outline" className="border-white/20 text-white hover:bg-white/10">
                        <Camera className="w-4 h-4 mr-2" />
                        Скриншот
                      </Button>
                      <Button variant="outline" className="border-white/20 text-white hover:bg-white/10">
                        <FileText className="w-4 h-4 mr-2" />
                        OCR Анализ
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
              
              {/* Результаты OCR */}
              <Card className="bg-black/20 backdrop-blur-sm border-white/10">
                <CardHeader>
                  <CardTitle className="text-white">Результаты OCR</CardTitle>
                  <CardDescription className="text-white/60">
                    Распознанный текст с экрана
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <ScrollArea className="h-64">
                    <div className="space-y-2 text-sm">
                      <div className="p-2 bg-white/5 rounded">
                        <span className="text-white/60">Найдено:</span>
                        <span className="text-white ml-2">"Daur-AI Advanced Control Panel"</span>
                      </div>
                      <div className="p-2 bg-white/5 rounded">
                        <span className="text-white/60">Найдено:</span>
                        <span className="text-white ml-2">"Панель управления"</span>
                      </div>
                      <div className="p-2 bg-white/5 rounded">
                        <span className="text-white/60">Найдено:</span>
                        <span className="text-white ml-2">"Запустить агента"</span>
                      </div>
                    </div>
                  </ScrollArea>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
          
          {/* AI Модели */}
          <TabsContent value="ai" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {Object.entries(aiModels).map(([modelKey, model]) => (
                <Card key={modelKey} className="bg-black/20 backdrop-blur-sm border-white/10">
                  <CardHeader>
                    <CardTitle className="text-white flex items-center justify-between">
                      <div className="flex items-center">
                        <Brain className="w-5 h-5 mr-2 text-purple-400" />
                        {model.name}
                      </div>
                      <div className={`w-3 h-3 rounded-full ${model.status === 'ready' ? 'bg-green-500' : 'bg-red-500'}`}></div>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div className="flex justify-between">
                        <span className="text-white/60">Статус:</span>
                        <span className="text-white capitalize">{model.status}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-white/60">Уверенность:</span>
                        <span className="text-white">{Math.round(model.confidence * 100)}%</span>
                      </div>
                      <Progress value={model.confidence * 100} className="mt-2" />
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
            
            {/* Тестирование модели */}
            <Card className="bg-black/20 backdrop-blur-sm border-white/10">
              <CardHeader>
                <CardTitle className="text-white">Тестирование AI модели</CardTitle>
                <CardDescription className="text-white/60">
                  Отправьте запрос для тестирования возможностей AI
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <Textarea
                    placeholder="Введите ваш запрос для AI модели..."
                    className="bg-white/10 border-white/20 text-white placeholder:text-white/40"
                    rows={3}
                  />
                  <Button className="bg-purple-600 hover:bg-purple-700">
                    <Brain className="w-4 h-4 mr-2" />
                    Тестировать модель
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
          
          {/* Настройки */}
          <TabsContent value="settings" className="space-y-6">
            <Card className="bg-black/20 backdrop-blur-sm border-white/10">
              <CardHeader>
                <CardTitle className="text-white">Настройки агента</CardTitle>
                <CardDescription className="text-white/60">
                  Конфигурация поведения и возможностей AI агента
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  {Object.entries(settings).map(([key, value]) => (
                    <div key={key} className="flex items-center justify-between">
                      <div>
                        <Label className="text-white font-medium">
                          {key === 'autoMode' ? 'Автоматический режим' :
                           key === 'visualFeedback' ? 'Визуальная обратная связь' :
                           key === 'soundNotifications' ? 'Звуковые уведомления' :
                           key === 'debugMode' ? 'Режим отладки' :
                           key === 'learningMode' ? 'Режим обучения' : key}
                        </Label>
                        <p className="text-sm text-white/60">
                          {key === 'autoMode' ? 'Автоматическое выполнение задач' :
                           key === 'visualFeedback' ? 'Показывать действия на экране' :
                           key === 'soundNotifications' ? 'Воспроизводить звуки при событиях' :
                           key === 'debugMode' ? 'Подробные логи и отладочная информация' :
                           key === 'learningMode' ? 'Обучение на основе обратной связи' : 'Настройка'}
                        </p>
                      </div>
                      <Switch
                        checked={value}
                        onCheckedChange={(checked) => 
                          setSettings(prev => ({ ...prev, [key]: checked }))
                        }
                      />
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  )
}

export default App
