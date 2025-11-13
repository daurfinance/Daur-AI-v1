#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Autonomous Agent - Fully autonomous AI agent with vision, adaptation, and self-correction
Sees the screen, understands context, plans adaptively, and corrects errors
"""

import asyncio
import logging
import os
from typing import Dict, List, Any, Optional
from pathlib import Path
import time

from src.ai.openai_client import OpenAIClient
from src.ai.adaptive_planner import AdaptivePlanner, Plan, Action
from src.system.system_profiler import SystemProfiler
from src.vision.vision_analyzer import VisionAnalyzer
from src.vision.screen_capture import ScreenCapture
from src.input.controller import InputController

LOG = logging.getLogger("daur_ai.autonomous_agent")


class AutonomousAgent:
    """
    Fully autonomous AI agent that:
    - Profiles the system on initialization
    - Analyzes screen state before and after actions
    - Creates adaptive plans based on current context
    - Verifies action results through vision
    - Self-corrects when things go wrong
    - Learns from the environment
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the autonomous agent.
        
        Args:
            api_key: OpenAI API key (optional, will use env var if not provided)
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY env var.")
        
        # Initialize components
        self.ai = OpenAIClient(api_key=self.api_key)
        self.profiler = SystemProfiler()
        self.planner = AdaptivePlanner(api_key=self.api_key)
        self.vision = VisionAnalyzer(api_key=self.api_key)
        self.capture = ScreenCapture()
        self.controller = InputController(config={"safe_mode": False})
        
        # State
        self.system_profile: Optional[Dict[str, Any]] = None
        self.conversation_history: List[Dict[str, str]] = []
        self.screenshots_dir = Path.home() / ".daur_ai" / "screenshots"
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        
        LOG.info("AutonomousAgent initialized")
    
    async def initialize(self):
        """Initialize the agent by profiling the system."""
        print("\n🔍 Профилирую систему...")
        LOG.info("Profiling system...")
        
        self.system_profile = self.profiler.get_profile()
        
        print(f"✅ Система: {self.system_profile['os']['system']} {self.system_profile['os']['release']}")
        print(f"✅ Приложений установлено: {len(self.system_profile['applications'])}")
        print(f"✅ Раскладка переключается: {self.system_profile['keyboard']['switch_shortcut']}")
        print(f"✅ Spotlight: {self.system_profile['shortcuts']['spotlight']}")
        
        LOG.info("System profiling complete")
    
    async def process_command(self, command: str) -> Dict[str, Any]:
        """
        Process a command with full autonomy: vision, planning, execution, verification.
        
        Args:
            command: Natural language command from user
            
        Returns:
            Result dictionary with execution details
        """
        LOG.info(f"Processing command: {command}")
        print(f"\n🎯 Команда: {command}")
        
        try:
            # Step 1: Analyze current screen state
            print("\n📸 Анализирую текущее состояние экрана...")
            before_screenshot = await self._take_screenshot("before")
            screen_state = await self.vision.analyze_screen(
                before_screenshot,
                context=f"User wants to: {command}"
            )
            
            print(f"   Активное приложение: {screen_state.get('active_app', 'unknown')}")
            print(f"   Spotlight открыт: {screen_state.get('spotlight_open', False)}")
            print(f"   Раскладка: {screen_state.get('keyboard_layout', 'unknown')}")
            
            # Step 2: Create adaptive plan
            print("\n🧠 Создаю адаптивный план...")
            plan = await self.planner.create_plan(
                command,
                self.system_profile,
                screen_state
            )
            
            print(f"   Цель: {plan.goal}")
            print(f"   Действий: {len(plan.actions)}")
            print(f"   Время: ~{plan.estimated_time}с")
            
            # Step 3: Execute plan with vision verification
            print("\n⚙️ Выполняю план...")
            result = await self._execute_plan_with_vision(plan, screen_state)
            
            return {
                "success": result['success'],
                "command": command,
                "plan": {
                    "goal": plan.goal,
                    "actions_count": len(plan.actions),
                    "reasoning": plan.reasoning
                },
                "result": result
            }
        
        except Exception as e:
            LOG.error(f"Command processing failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "command": command
            }
    
    async def _execute_plan_with_vision(
        self,
        plan: Plan,
        initial_screen_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute plan with vision verification after each action.
        Self-corrects if actions don't produce expected results.
        """
        results = []
        current_screen_state = initial_screen_state
        
        for i, action in enumerate(plan.actions, 1):
            print(f"\n   [{i}/{len(plan.actions)}] {action.description}")
            print(f"       Ожидаемый результат: {action.expected_outcome}")
            
            try:
                # Execute action
                before_screenshot = await self._take_screenshot(f"action_{i}_before")
                
                await self._execute_action(action)
                
                # Wait for UI to respond
                await asyncio.sleep(1)
                
                # Verify result
                after_screenshot = await self._take_screenshot(f"action_{i}_after")
                verification = await self.vision.verify_action_result(
                    before_screenshot,
                    after_screenshot,
                    action.expected_outcome
                )
                
                if verification['success']:
                    print(f"       ✅ Успешно!")
                    results.append({
                        "step": i,
                        "action": action.description,
                        "success": True,
                        "verification": verification
                    })
                else:
                    print(f"       ⚠️ Не получилось: {', '.join(verification['issues'])}")
                    
                    # Try to adapt and continue
                    if verification.get('next_action'):
                        print(f"       🔄 Адаптирую план...")
                        adapted_plan = await self.planner.adapt_plan(
                            plan,
                            i,
                            current_screen_state,
                            ', '.join(verification['issues'])
                        )
                        
                        # Execute adapted plan
                        adapted_result = await self._execute_plan_with_vision(
                            adapted_plan,
                            current_screen_state
                        )
                        
                        results.append({
                            "step": i,
                            "action": action.description,
                            "success": False,
                            "adapted": True,
                            "adapted_result": adapted_result
                        })
                    else:
                        results.append({
                            "step": i,
                            "action": action.description,
                            "success": False,
                            "verification": verification
                        })
                
                # Update current screen state
                current_screen_state = await self.vision.analyze_screen(
                    after_screenshot,
                    context="After action"
                )
            
            except Exception as e:
                LOG.error(f"Action {i} failed: {e}")
                print(f"       ❌ Ошибка: {e}")
                results.append({
                    "step": i,
                    "action": action.description,
                    "success": False,
                    "error": str(e)
                })
        
        # Calculate overall success
        successful = sum(1 for r in results if r.get('success', False))
        
        return {
            "success": successful > 0,
            "total_steps": len(plan.actions),
            "successful_steps": successful,
            "failed_steps": len(plan.actions) - successful,
            "details": results
        }
    
    async def _execute_action(self, action: Action):
        """Execute a single action."""
        action_type = action.type
        params = action.parameters
        
        LOG.info(f"Executing: {action_type} with {params}")
        
        if action_type == "open_app":
            app_name = params.get('app', '')
            
            # Use Spotlight
            spotlight_shortcut = self.profiler.get_spotlight_shortcut()
            keys = spotlight_shortcut.split('+')
            await self.controller.hotkey(*keys)
            await asyncio.sleep(1)
            
            # Type app name
            await self.controller.type(app_name)
            await asyncio.sleep(0.5)
            
            # Press Enter
            await self.controller.key("enter")
            await asyncio.sleep(2)
        
        elif action_type == "hotkey":
            # Handle both formats
            keys = params.get('keys', [])
            if not keys:
                keys = []
                i = 1
                while f'key{i}' in params:
                    keys.append(params[f'key{i}'])
                    i += 1
            
            if isinstance(keys, str):
                keys = keys.split('+')
            
            await self.controller.hotkey(*keys)
        
        elif action_type == "type_text":
            text = params.get('text', '')
            await self.controller.type(text)
        
        elif action_type == "press_key":
            key = params.get('key', 'enter')
            await self.controller.key(key)
        
        elif action_type == "click":
            x = params.get('x', 0)
            y = params.get('y', 0)
            await self.controller.click(x, y)
        
        elif action_type == "wait":
            seconds = params.get('seconds', 1)
            await asyncio.sleep(seconds)
        
        elif action_type == "switch_layout":
            layout_shortcut = self.profiler.get_layout_switch_shortcut()
            keys = layout_shortcut.split('+')
            await self.controller.hotkey(*keys)
            await asyncio.sleep(0.3)
        
        elif action_type == "verify_screen":
            # Take screenshot and analyze
            screenshot = await self._take_screenshot("verification")
            expected = params.get('expected', '')
            analysis = await self.vision.analyze_screen(screenshot, context=expected)
            LOG.info(f"Screen verification: {analysis}")
        
        else:
            LOG.warning(f"Unknown action type: {action_type}")
    
    async def _take_screenshot(self, label: str = "screenshot") -> str:
        """
        Take a screenshot and return the file path.
        
        Args:
            label: Label for the screenshot file
            
        Returns:
            Path to screenshot file
        """
        timestamp = int(time.time() * 1000)
        filename = f"{label}_{timestamp}.png"
        filepath = self.screenshots_dir / filename
        
        try:
            result = self.capture.capture_sync(str(filepath))
            if result:
                LOG.info(f"Screenshot saved: {filepath}")
                return str(filepath)
            else:
                LOG.error("Screenshot failed: capture_sync returned None")
                return str(filepath)
        except Exception as e:
            LOG.error(f"Screenshot failed: {e}")
            # Return a dummy path
            return str(filepath)
    
    async def chat(self, message: str) -> str:
        """
        Chat with the agent. Determines if message is a command or question.
        
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
                response = f"✅ Выполнено!\n\n"
                response += f"Цель: {result['plan']['goal']}\n"
                response += f"Действий выполнено: {result['result']['successful_steps']}/{result['result']['total_steps']}\n"
                
                if result['result']['failed_steps'] > 0:
                    response += f"\n⚠ Неудачных действий: {result['result']['failed_steps']}"
            else:
                response = f"❌ Ошибка: {result.get('error', 'Unknown error')}"
        else:
            # This is a question - just chat
            prompt = f"""You are Daur AI, an autonomous AI agent for macOS.
You can see the screen, control the computer, open apps, automate tasks, and help users.

You have access to:
- System profiling (OS, apps, shortcuts)
- Computer vision (can see and analyze the screen)
- Adaptive planning (create context-aware plans)
- Self-correction (fix errors automatically)

Conversation history:
{self.conversation_history[-5:]}

Respond naturally and helpfully to the user's message.
If they ask what you can do, explain your autonomous capabilities.
"""
            response = await self.ai.chat_async(prompt)
        
        # Add to history
        self.conversation_history.append({
            "role": "assistant",
            "content": response
        })
        
        return response


if __name__ == "__main__":
    # Test the autonomous agent
    logging.basicConfig(level=logging.INFO)
    
    async def test():
        agent = AutonomousAgent()
        await agent.initialize()
        
        print("\n" + "="*60)
        print("AUTONOMOUS AGENT TEST")
        print("="*60)
        print("\nAgent initialized with full autonomy:")
        print("✅ System profiling")
        print("✅ Computer vision")
        print("✅ Adaptive planning")
        print("✅ Self-correction")
        print("="*60)
    
    asyncio.run(test())

