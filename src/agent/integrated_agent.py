"""
Integrated AI Agent
Full-featured autonomous agent that coordinates all system components.
"""

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Union, Any
from pathlib import Path

# Import core components
from src.ai.model_manager import ModelManager
from src.input.controller import InputController
from src.parser.command_parser import CommandParser
from src.automation.browser import BrowserAutomation
from src.automation.system import SystemAutomation
from src.web.api import WebAPI

class AgentState(Enum):
    """Agent states"""
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    STOPPING = "stopping"
    STOPPED = "stopped"

@dataclass
class Task:
    """Task representation"""
    id: str
    type: str
    params: Dict[str, Any]
    priority: int = 1
    status: str = "pending"
    result: Optional[Dict] = None
    error: Optional[str] = None
    created_at: float = time.time()
    started_at: Optional[float] = None
    completed_at: Optional[float] = None

class IntegratedAgent:
    """
    Full-featured AI agent that coordinates all system components.
    Provides complete automation capabilities including:
    - AI model integration
    - Input/Output control
    - Browser automation
    - System automation
    - Web API interface
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the agent with configuration.
        
        Args:
            config: Configuration dictionary containing all settings
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.state = AgentState.INITIALIZING
        self.agent_id = str(uuid.uuid4())
        
        # Initialize core components
        self.model_manager = None
        self.input_controller = None
        self.command_parser = None
        self.browser_automation = None
        self.system_automation = None
        self.web_api = None
        
        # Task management
        self.task_queue = asyncio.Queue()
        self.active_tasks: Dict[str, Task] = {}
        self.completed_tasks: Dict[str, Task] = {}
        
        # Statistics
        self.stats = {
            "tasks_completed": 0,
            "tasks_failed": 0,
            "uptime": 0,
            "last_error": None,
            "start_time": None
        }
        
        # Initialize components
        self._initialize_components()
        
    def _initialize_components(self):
        """Initialize all system components."""
        try:
            # Initialize AI model manager
            model_config = self.config.get("ai", {})
            self.model_manager = ModelManager(model_config)
            
            # Initialize input controller
            input_config = self.config.get("input", {})
            self.input_controller = InputController(input_config)
            
            # Initialize command parser
            parser_config = self.config.get("parser", {})
            self.command_parser = CommandParser(parser_config)
            
            # Initialize automation components
            automation_config = self.config.get("automation", {})
            self.browser_automation = BrowserAutomation(automation_config)
            self.system_automation = SystemAutomation(automation_config)
            
            # Initialize web API if enabled
            if self.config.get("web", {}).get("enabled", True):
                web_config = self.config.get("web", {})
                self.web_api = WebAPI(web_config, agent=self)
                
            self.logger.info("All components initialized successfully")
            self.state = AgentState.STOPPED
            
        except Exception as e:
            self.logger.error(f"Failed to initialize components: {e}")
            self.state = AgentState.ERROR
            raise
            
    async def start(self):
        """Start the agent and all its components."""
        try:
            if self.state != AgentState.STOPPED:
                raise RuntimeError(f"Cannot start agent in state {self.state}")
                
            self.logger.info("Starting agent...")
            self.state = AgentState.INITIALIZING
            
            # Start all components
            await self.model_manager.start()
            await self.input_controller.start()
            await self.browser_automation.start()
            await self.system_automation.start()
            
            # Start web API if enabled
            if self.web_api:
                await self.web_api.start()
            
            # Start task processor
            self.task_processor = asyncio.create_task(self._process_tasks())
            
            self.stats["start_time"] = time.time()
            self.state = AgentState.RUNNING
            self.logger.info("Agent started successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to start agent: {e}")
            self.state = AgentState.ERROR
            raise
            
    async def stop(self):
        """Stop the agent and all its components."""
        try:
            if self.state not in [AgentState.RUNNING, AgentState.ERROR]:
                return
                
            self.logger.info("Stopping agent...")
            self.state = AgentState.STOPPING
            
            # Stop all components
            await self.model_manager.stop()
            await self.input_controller.stop()
            await self.browser_automation.stop()
            await self.system_automation.stop()
            
            if self.web_api:
                await self.web_api.stop()
            
            # Stop task processor
            if hasattr(self, 'task_processor'):
                self.task_processor.cancel()
                
            self.state = AgentState.STOPPED
            self.logger.info("Agent stopped successfully")
            
        except Exception as e:
            self.logger.error(f"Error stopping agent: {e}")
            self.state = AgentState.ERROR
            raise
            
    async def pause(self):
        """Pause agent operation."""
        if self.state == AgentState.RUNNING:
            self.state = AgentState.PAUSED
            self.logger.info("Agent paused")
            
    async def resume(self):
        """Resume agent operation."""
        if self.state == AgentState.PAUSED:
            self.state = AgentState.RUNNING
            self.logger.info("Agent resumed")
            
    async def execute_command(self, command: str) -> Dict[str, Any]:
        """
        Execute a command string.
        
        Args:
            command: Command string to execute
            
        Returns:
            Dict containing execution results
        """
        try:
            # Parse command
            action = self.command_parser.parse(command)
            if not action:
                return {"success": False, "error": "Failed to parse command"}
            
            # Create task
            task = Task(
                id=str(uuid.uuid4()),
                type=action["type"],
                params=action["params"]
            )
            
            # Add to queue
            await self.task_queue.put(task)
            
            # Wait for completion
            while task.id in self.active_tasks:
                await asyncio.sleep(0.1)
                
            # Get result
            if task.id in self.completed_tasks:
                task = self.completed_tasks[task.id]
                return {
                    "success": True,
                    "task_id": task.id,
                    "result": task.result,
                    "completed_at": task.completed_at
                }
            else:
                return {"success": False, "error": "Task processing failed"}
                
        except Exception as e:
            self.logger.error(f"Error executing command: {e}")
            return {"success": False, "error": str(e)}
            
    async def _process_tasks(self):
        """Process tasks from the queue."""
        while True:
            try:
                # Get task from queue
                task = await self.task_queue.get()
                
                # Skip if paused
                if self.state == AgentState.PAUSED:
                    await asyncio.sleep(1)
                    continue
                    
                # Process task
                self.active_tasks[task.id] = task
                task.started_at = time.time()
                
                try:
                    if task.type == "input":
                        task.result = await self.input_controller.execute(task.params)
                    elif task.type == "browser":
                        task.result = await self.browser_automation.execute(task.params)
                    elif task.type == "system":
                        task.result = await self.system_automation.execute(task.params)
                    else:
                        task.error = f"Unknown task type: {task.type}"
                        
                except Exception as e:
                    task.error = str(e)
                    self.logger.error(f"Task {task.id} failed: {e}")
                    
                # Update task status
                task.completed_at = time.time()
                task.status = "completed" if not task.error else "failed"
                
                # Update statistics
                if task.error:
                    self.stats["tasks_failed"] += 1
                else:
                    self.stats["tasks_completed"] += 1
                    
                # Move to completed
                del self.active_tasks[task.id]
                self.completed_tasks[task.id] = task
                
                # Update uptime
                if self.stats["start_time"]:
                    self.stats["uptime"] = time.time() - self.stats["start_time"]
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in task processor: {e}")
                self.stats["last_error"] = str(e)
                await asyncio.sleep(1)
                
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status."""
        return {
            "agent_id": self.agent_id,
            "state": self.state.value,
            "stats": self.stats,
            "active_tasks": len(self.active_tasks),
            "queued_tasks": self.task_queue.qsize()
        }