# -*- coding: utf-8 -*-

"""
Dynamic Agent - Simple screenshot → decide → execute loop
Based on OpenAI Computer Use API architecture
No pre-planning, model decides next action dynamically
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

from src.ai.openai_client import OpenAIClient
from src.input.controller import InputController
from src.vision.screen_capture import ScreenCapture
from src.system.system_profiler import SystemProfiler

LOG = logging.getLogger("daur_ai.dynamic_agent")


class DynamicAgent:
    """
    Dynamic agent that decides actions on-the-fly based on screenshots.
    
    Architecture:
    1. Take screenshot
    2. Ask model: "What's the next action?"
    3. Execute action
    4. Repeat until done
    
    No pre-planning, no verification - model sees results in next screenshot.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize dynamic agent."""
        LOG.info("Initializing Dynamic Agent...")
        
        # Initialize components
        self.ai = OpenAIClient(api_key=api_key, model="gpt-4o")
        self.controller = InputController(config={"safe_mode": False})
        self.capture = ScreenCapture()
        self.profiler = SystemProfiler()
        
        # Profile system once
        self.system_profile = self.profiler.get_profile()
        LOG.info(f"System profiled: {self.system_profile['os']['system']} {self.system_profile['os']['version']}")
        
        # Screenshot directory
        self.screenshot_dir = Path.home() / ".daur_ai" / "screenshots"
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
        
        # Action counter
        self.action_count = 0
        self.max_actions = 20  # Safety limit
    
    async def execute_command(self, command: str) -> Dict[str, Any]:
        """
        Execute command using dynamic action selection.
        
        Args:
            command: User command
            
        Returns:
            Execution result
        """
        LOG.info(f"Executing command: {command}")
        print(f"\n🎯 Команда: {command}\n")
        
        self.action_count = 0
        actions_taken = []
        
        try:
            # Initial screenshot
            print("📸 Анализирую начальное состояние...")
            screenshot_path = await self._take_screenshot("initial")
            
            # Main loop: screenshot → decide → execute → repeat
            while self.action_count < self.max_actions:
                self.action_count += 1
                
                # Ask model: what's next?
                print(f"\n🤔 Решаю следующее действие ({self.action_count}/{self.max_actions})...")
                
                next_action = await self._decide_next_action(
                    command=command,
                    screenshot_path=screenshot_path,
                    actions_taken=actions_taken
                )
                
                # Check if done
                if next_action['action'] == 'done':
                    print(f"\n✅ Задача выполнена!")
                    print(f"   Причина: {next_action.get('reasoning', 'Goal achieved')}")
                    break
                
                # Execute action
                print(f"\n⚙️ Выполняю: {next_action['description']}")
                
                success = await self._execute_action(next_action)
                
                if success:
                    print(f"   ✅ Выполнено")
                    actions_taken.append({
                        "action": next_action['action'],
                        "description": next_action['description'],
                        "success": True
                    })
                else:
                    print(f"   ⚠️ Ошибка")
                    actions_taken.append({
                        "action": next_action['action'],
                        "description": next_action['description'],
                        "success": False
                    })
                
                # Wait for UI to respond
                await asyncio.sleep(1)
                
                # Take new screenshot for next iteration
                screenshot_path = await self._take_screenshot(f"action_{self.action_count}")
            
            # Check if we hit max actions
            if self.action_count >= self.max_actions:
                print(f"\n⚠️ Достигнут лимит действий ({self.max_actions})")
            
            # Summary
            successful = sum(1 for a in actions_taken if a['success'])
            print(f"\n📊 Итого: {successful}/{len(actions_taken)} действий выполнено успешно")
            
            return {
                "success": successful == len(actions_taken),
                "actions_taken": len(actions_taken),
                "actions_successful": successful,
                "command": command
            }
        
        except Exception as e:
            LOG.error(f"Command execution failed: {e}", exc_info=True)
            print(f"\n❌ Ошибка: {e}")
            return {
                "success": False,
                "error": str(e),
                "command": command,
                "actions_taken": 0,
                "actions_successful": 0
            }
    
    async def _decide_next_action(
        self,
        command: str,
        screenshot_path: str,
        actions_taken: list
    ) -> Dict[str, Any]:
        """
        Ask model to decide next action based on current screenshot.
        
        Args:
            command: Original user command
            screenshot_path: Path to current screenshot
            actions_taken: List of actions taken so far
            
        Returns:
            Next action to take
        """
        # Build context
        system_info = self._build_system_context()
        actions_history = self._build_actions_history(actions_taken)
        
        prompt = f"""You are an AI agent controlling a macOS computer. You see the current screen and decide the next action.

ORIGINAL GOAL: {command}

SYSTEM INFO:
{system_info}

ACTIONS TAKEN SO FAR:
{actions_history}

CURRENT SCREEN:
[See screenshot]

Decide the NEXT action to take. Respond in JSON format:

{{
  "action": "open_app|hotkey|type_text|press_key|click|wait|done",
  "description": "What this action does",
  "parameters": {{"param": "value"}},
  "reasoning": "Why this action is needed now"
}}

AVAILABLE ACTIONS:
- open_app: Open application (params: {{"app": "AppName"}})
- hotkey: Press keyboard shortcut (params: {{"key1": "command", "key2": "space"}})
- type_text: Type text (params: {{"text": "text to type"}})
- press_key: Press single key (params: {{"key": "enter"}})
- click: Click at position (params: {{"x": 100, "y": 200}})
- wait: Wait seconds (params: {{"seconds": 2}})
- done: Task completed (params: {{}})

RULES:
1. Look at the screenshot - what do you see?
2. What's the next logical step toward the goal?
3. If goal is achieved, return action="done"
4. Keep actions simple and atomic
5. Remember: keyboard layout is {self.system_profile['keyboard']['current_layout']}
6. To switch layout, use hotkey: {self.system_profile['shortcuts']['keyboard_layout_switch']}

Decide now - what's the next action?
"""
        
        try:
            # Note: In production, would send actual screenshot to GPT-4 Vision
            # For now, using text-based decision (would need image upload)
            response = await self.ai.chat_async(prompt, json_mode=True)
            action = json.loads(response)
            
            LOG.info(f"Next action decided: {action['action']} - {action['description']}")
            return action
        
        except Exception as e:
            LOG.error(f"Failed to decide next action: {e}")
            # Fallback: mark as done
            return {
                "action": "done",
                "description": "Failed to decide next action",
                "parameters": {},
                "reasoning": f"Error: {e}"
            }
    
    async def _execute_action(self, action: Dict[str, Any]) -> bool:
        """
        Execute a single action.
        
        Args:
            action: Action to execute
            
        Returns:
            True if successful
        """
        action_type = action['action']
        params = action.get('parameters', {})
        
        try:
            if action_type == 'open_app':
                app_name = params.get('app', '')
                await self._open_app(app_name)
            
            elif action_type == 'hotkey':
                # Extract keys
                keys = []
                i = 1
                while f'key{i}' in params:
                    keys.append(params[f'key{i}'])
                    i += 1
                
                if keys:
                    await self.controller.hotkey(*keys)
            
            elif action_type == 'type_text':
                text = params.get('text', '')
                
                # Auto-switch layout if needed
                if self._needs_english_layout(text):
                    print("   📝 Переключаю раскладку на английскую...")
                    layout_switch = self.system_profile['keyboard'].get('switch_shortcut', 'ctrl+space')
                    if '+' in layout_switch:
                        keys = layout_switch.split('+')
                        await self.controller.hotkey(*keys)
                        await asyncio.sleep(0.5)
                
                await self.controller.type(text)
            
            elif action_type == 'press_key':
                key = params.get('key', '')
                await self.controller.key(key)
            
            elif action_type == 'click':
                x = params.get('x', 0)
                y = params.get('y', 0)
                await self.controller.click(x, y)
            
            elif action_type == 'wait':
                seconds = params.get('seconds', 1)
                await asyncio.sleep(seconds)
            
            elif action_type == 'done':
                # No action needed
                pass
            
            else:
                LOG.warning(f"Unknown action type: {action_type}")
                return False
            
            return True
        
        except Exception as e:
            LOG.error(f"Action execution failed: {e}")
            return False
    
    async def _open_app(self, app_name: str):
        """Open application using Spotlight."""
        # Open Spotlight
        spotlight_shortcut = self.system_profile['shortcuts']['spotlight']
        keys = spotlight_shortcut.split('+')
        await self.controller.hotkey(*keys)
        await asyncio.sleep(0.5)
        
        # Switch to English layout if needed
        if self._needs_english_layout(app_name):
            layout_switch = self.system_profile['keyboard'].get('switch_shortcut', 'ctrl+space')
            if '+' in layout_switch:
                keys = layout_switch.split('+')
                await self.controller.hotkey(*keys)
                await asyncio.sleep(0.3)
        
        # Type app name
        await self.controller.type(app_name)
        await asyncio.sleep(0.5)
        
        # Press Enter
        await self.controller.key('enter')
    
    def _needs_english_layout(self, text: str) -> bool:
        """Check if text contains English characters."""
        return any(ord('a') <= ord(c.lower()) <= ord('z') for c in text)
    
    async def _take_screenshot(self, name: str) -> str:
        """Take screenshot and return path."""
        try:
            screenshot_path = self.screenshot_dir / f"{name}.png"
            self.capture.capture_sync(str(screenshot_path))
            return str(screenshot_path)
        except Exception as e:
            LOG.error(f"Screenshot failed: {e}")
            return ""
    
    def _build_system_context(self) -> str:
        """Build system context string."""
        os_info = self.system_profile['os']
        keyboard = self.system_profile['keyboard']
        shortcuts = self.system_profile['shortcuts']
        screen = self.system_profile['screen']
        
        return f"""- OS: {os_info['system']} {os_info['version']}
- Screen: {screen.get('resolution', 'Unknown')}
- Keyboard Layout: {keyboard['current_layout']}
- Layout Switch: {keyboard.get('switch_shortcut', 'ctrl+space')}
- Spotlight: {shortcuts.get('spotlight', 'command+space')}
- Installed Apps: {len(self.system_profile['applications'])} apps"""
    
    def _build_actions_history(self, actions_taken: list) -> str:
        """Build actions history string."""
        if not actions_taken:
            return "None yet - this is the first action"
        
        history = []
        for i, action in enumerate(actions_taken, 1):
            status = "✅" if action['success'] else "❌"
            history.append(f"{i}. {status} {action['description']}")
        
        return "\n".join(history)

