#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Intelligent AI Agent - Natural Language to Action
Accepts text commands, plans actions, generates code, and executes autonomously
"""

import asyncio
import logging
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import os

from src.ai.openai_client import OpenAIClient
from src.input.controller import InputController
from src.vision.screen_capture import ScreenCapture

LOG = logging.getLogger("daur_ai.intelligent_agent")


@dataclass
class Action:
    """Represents a planned action"""
    type: str  # 'mouse', 'keyboard', 'app', 'wait', 'screenshot'
    description: str
    parameters: Dict[str, Any]
    reasoning: str


@dataclass
class Plan:
    """Represents an execution plan"""
    goal: str
    actions: List[Action]
    reasoning: str
    estimated_time: int  # seconds


class IntelligentAgent:
    """
    AI Agent that understands natural language commands and autonomously
    executes them by planning, reasoning, and controlling the computer.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the intelligent agent.
        
        Args:
            api_key: OpenAI API key (optional, will use env var if not provided)
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY env var.")
        
        self.ai = OpenAIClient(api_key=self.api_key)
        self.controller = InputController()
        self.capture = ScreenCapture()
        
        self.conversation_history: List[Dict[str, str]] = []
        
        LOG.info("Intelligent Agent initialized")
    
    async def process_command(self, command: str) -> Dict[str, Any]:
        """
        Process a natural language command.
        
        Args:
            command: Natural language command from user
            
        Returns:
            Result dictionary with status and details
        """
        LOG.info(f"Processing command: {command}")
        
        try:
            # Step 1: Understand the command
            understanding = await self._understand_command(command)
            LOG.info(f"Understanding: {understanding['intent']}")
            
            # Step 2: Create a plan
            plan = await self._create_plan(command, understanding)
            LOG.info(f"Plan created with {len(plan.actions)} actions")
            
            # Step 3: Execute the plan
            result = await self._execute_plan(plan)
            
            return {
                "success": True,
                "command": command,
                "understanding": understanding,
                "plan": {
                    "goal": plan.goal,
                    "actions": [
                        {
                            "type": a.type,
                            "description": a.description,
                            "reasoning": a.reasoning
                        }
                        for a in plan.actions
                    ],
                    "reasoning": plan.reasoning
                },
                "result": result
            }
            
        except Exception as e:
            LOG.error(f"Error processing command: {e}")
            return {
                "success": False,
                "error": str(e),
                "command": command
            }
    
    async def _understand_command(self, command: str) -> Dict[str, Any]:
        """Understand the user's intent and extract key information."""
        
        prompt = f"""Analyze this user command and extract key information:

Command: "{command}"

Provide a JSON response with:
- intent: What the user wants to do (e.g., "open_app", "search_web", "create_file", "automate_task")
- target: The main target (app name, URL, file name, etc.)
- parameters: Any additional parameters
- complexity: "simple", "medium", or "complex"
- requires_planning: true/false

Example:
Command: "Open Safari and search for AI automation"
Response: {{
  "intent": "search_web",
  "target": "AI automation",
  "parameters": {{"browser": "Safari"}},
  "complexity": "simple",
  "requires_planning": true
}}

Now analyze: "{command}"
"""
        
        response = await self.ai.chat_async(prompt)
        
        # Extract JSON from response
        try:
            # Try to find JSON in the response
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = response[start:end]
                understanding = json.loads(json_str)
            else:
                # Fallback
                understanding = {
                    "intent": "general_task",
                    "target": command,
                    "parameters": {},
                    "complexity": "medium",
                    "requires_planning": True
                }
        except json.JSONDecodeError:
            understanding = {
                "intent": "general_task",
                "target": command,
                "parameters": {},
                "complexity": "medium",
                "requires_planning": True
            }
        
        return understanding
    
    async def _create_plan(self, command: str, understanding: Dict[str, Any]) -> Plan:
        """Create a detailed execution plan."""
        
        prompt = f"""Create a detailed execution plan for this task:

Command: "{command}"
Intent: {understanding['intent']}
Target: {understanding['target']}
Parameters: {understanding.get('parameters', {{}})}

Available actions:
1. open_app(app_name) - Open an application using Spotlight
2. type_text(text) - Type text
3. press_key(key) - Press a key (enter, escape, tab, etc.)
4. hotkey(key1, key2, ...) - Press key combination (command+space, command+t, etc.)
5. move_mouse(x, y) - Move mouse to coordinates
6. click(x, y) - Click at coordinates
7. wait(seconds) - Wait for specified time
8. screenshot(filename) - Take a screenshot

Create a step-by-step plan with:
- Clear reasoning for each step
- Specific parameters for each action
- Appropriate wait times between actions

Provide response as JSON:
{{
  "goal": "Clear description of what we're trying to achieve",
  "reasoning": "Overall strategy and approach",
  "estimated_time": 10,
  "actions": [
    {{
      "type": "open_app",
      "description": "Open Safari browser",
      "parameters": {{"app": "Safari"}},
      "reasoning": "Need browser to search web"
    }},
    ...
  ]
}}

Create plan for: "{command}"
"""
        
        response = await self.ai.chat_async(prompt)
        
        # Extract JSON
        try:
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = response[start:end]
                plan_data = json.loads(json_str)
            else:
                raise ValueError("No JSON found in response")
        except (json.JSONDecodeError, ValueError) as e:
            LOG.warning(f"Failed to parse plan JSON: {e}")
            # Create a simple fallback plan
            plan_data = {
                "goal": command,
                "reasoning": "Simple execution plan",
                "estimated_time": 5,
                "actions": [
                    {
                        "type": "open_app",
                        "description": f"Execute: {command}",
                        "parameters": {"app": understanding.get('target', 'Finder')},
                        "reasoning": "Direct execution"
                    }
                ]
            }
        
        # Convert to Plan object
        actions = [
            Action(
                type=a['type'],
                description=a['description'],
                parameters=a.get('parameters', {}),
                reasoning=a.get('reasoning', '')
            )
            for a in plan_data.get('actions', [])
        ]
        
        plan = Plan(
            goal=plan_data.get('goal', command),
            actions=actions,
            reasoning=plan_data.get('reasoning', ''),
            estimated_time=plan_data.get('estimated_time', 10)
        )
        
        return plan
    
    async def _execute_plan(self, plan: Plan) -> Dict[str, Any]:
        """Execute the planned actions."""
        
        LOG.info(f"Executing plan: {plan.goal}")
        LOG.info(f"Reasoning: {plan.reasoning}")
        LOG.info(f"Estimated time: {plan.estimated_time}s")
        
        results = []
        
        for i, action in enumerate(plan.actions, 1):
            LOG.info(f"Step {i}/{len(plan.actions)}: {action.description}")
            LOG.info(f"Reasoning: {action.reasoning}")
            
            try:
                result = await self._execute_action(action)
                results.append({
                    "step": i,
                    "action": action.description,
                    "success": True,
                    "result": result
                })
                LOG.info(f"✓ Step {i} completed")
                
            except Exception as e:
                LOG.error(f"✗ Step {i} failed: {e}")
                results.append({
                    "step": i,
                    "action": action.description,
                    "success": False,
                    "error": str(e)
                })
                # Continue with next action
        
        return {
            "total_steps": len(plan.actions),
            "successful_steps": sum(1 for r in results if r['success']),
            "failed_steps": sum(1 for r in results if not r['success']),
            "details": results
        }
    
    async def _execute_action(self, action: Action) -> Any:
        """Execute a single action."""
        
        action_type = action.type
        params = action.parameters
        
        if action_type == "open_app":
            app_name = params.get('app', '')
            await self.controller.hotkey("command", "space")
            await asyncio.sleep(1)
            await self.controller.type(app_name)
            await asyncio.sleep(0.5)
            await self.controller.key("enter")
            await asyncio.sleep(2)
            return f"Opened {app_name}"
        
        elif action_type == "type_text":
            text = params.get('text', '')
            await self.controller.type(text)
            return f"Typed: {text}"
        
        elif action_type == "press_key":
            key = params.get('key', 'enter')
            await self.controller.key(key)
            return f"Pressed: {key}"
        
        elif action_type == "hotkey":
            keys = params.get('keys', [])
            if isinstance(keys, str):
                keys = keys.split('+')
            await self.controller.hotkey(*keys)
            return f"Hotkey: {'+'.join(keys)}"
        
        elif action_type == "move_mouse":
            x = params.get('x', 0)
            y = params.get('y', 0)
            await self.controller.move(x, y)
            return f"Moved mouse to ({x}, {y})"
        
        elif action_type == "click":
            x = params.get('x', 0)
            y = params.get('y', 0)
            await self.controller.click(x, y)
            return f"Clicked at ({x}, {y})"
        
        elif action_type == "wait":
            seconds = params.get('seconds', 1)
            await asyncio.sleep(seconds)
            return f"Waited {seconds}s"
        
        elif action_type == "screenshot":
            filename = params.get('filename', 'screenshot.png')
            screenshot = self.capture.capture_screen()
            self.capture.save_screenshot(screenshot, filename)
            return f"Screenshot saved: {filename}"
        
        else:
            raise ValueError(f"Unknown action type: {action_type}")
    
    async def chat(self, message: str) -> str:
        """
        Interactive chat interface.
        
        Args:
            message: User message
            
        Returns:
            Agent response
        """
        # Add to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": message
        })
        
        # Check if this is a command or a question
        command_keywords = [
            # English
            'open', 'create', 'search', 'find', 'go to', 'make', 'do', 'launch', 'start', 'run',
            'click', 'type', 'write', 'screenshot', 'capture', 'move', 'close',
            # Russian
            'открой', 'создай', 'найди', 'ищи', 'перейди', 'сделай', 'запусти', 'запиши',
            'напиши', 'кликни', 'нажми', 'скриншот', 'закрой', 'введи'
        ]
        if any(keyword in message.lower() for keyword in command_keywords):
            # This is a command - execute it
            result = await self.process_command(message)
            
            if result['success']:
                response = f"✓ Выполнено!\n\n"
                response += f"Цель: {result['plan']['goal']}\n"
                response += f"Действий выполнено: {result['result']['successful_steps']}/{result['result']['total_steps']}\n"
                
                if result['result']['failed_steps'] > 0:
                    response += f"\n⚠ Неудачных действий: {result['result']['failed_steps']}"
            else:
                response = f"✗ Ошибка: {result['error']}"
        else:
            # This is a question - just chat
            prompt = f"""You are Daur AI, an intelligent automation agent for macOS.
You can control the computer, open apps, automate tasks, and help users.

Conversation history:
{json.dumps(self.conversation_history[-5:], indent=2)}

Respond naturally and helpfully to the user's message.
If they ask what you can do, explain your capabilities.
"""
            response = await self.ai.chat_async(prompt)
        
        # Add to history
        self.conversation_history.append({
            "role": "assistant",
            "content": response
        })
        
        return response

