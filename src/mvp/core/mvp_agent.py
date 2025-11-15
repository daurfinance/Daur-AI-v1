"""
MVP Agent - Autonomous AI Agent with Local LLM
Main agent that coordinates all modules using Ollama for reasoning
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any
from pathlib import Path
import json
import time

from .ollama_client import get_ollama_client
from .input_controller import get_input_controller
from ..vision.screen_analyzer import get_screen_analyzer

logger = logging.getLogger(__name__)


class MVPAgent:
    """
    Autonomous AI Agent using 100% local LLM
    
    Capabilities:
    - Browser control (Chrome, Safari)
    - Creative apps (Photoshop, Blender, Canva, Word)
    - Local coding (create, save, run projects)
    - BlueStacks emulator control
    - Free screen analysis (OCR + Accessibility + Local Vision)
    """
    
    def __init__(self):
        """Initialize MVP agent"""
        self.llm = get_ollama_client()
        self.input = get_input_controller()
        self.vision = get_screen_analyzer()
        
        # Conversation history
        self.conversation_history: List[Dict[str, str]] = []
        
        # Current state
        self.current_task: Optional[str] = None
        self.current_plan: List[str] = []
        self.current_step: int = 0
        
        # Screenshots directory
        self.screenshots_dir = Path.home() / ".daur_ai" / "screenshots"
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("MVP Agent initialized with local LLM")
        
        # Check if all components are available
        self._check_components()
    
    def _check_components(self):
        """Check if all required components are available"""
        components = {
            'Ollama LLM': self.llm.check_connection(),
            'Input Control': self.input.is_available(),
            'OCR': self.vision.ocr.is_available(),
            'Accessibility API': self.vision.accessibility.is_available()
        }
        
        logger.info("Component Status:")
        for name, available in components.items():
            status = "✓" if available else "✗"
            logger.info(f"  {status} {name}")
        
        # Check available models
        models = self.llm.list_models()
        if models:
            logger.info(f"Available models: {', '.join(models)}")
        else:
            logger.warning("No Ollama models found. Please install models:")
            logger.warning("  ollama pull llama3.2:3b")
            logger.warning("  ollama pull llava")
    
    def take_screenshot(self) -> str:
        """
        Take screenshot and return path
        
        Returns:
            Path to screenshot file
        """
        timestamp = int(time.time())
        screenshot_path = str(self.screenshots_dir / f"screen_{timestamp}.png")
        
        if self.input.take_screenshot(screenshot_path):
            logger.debug(f"Screenshot saved: {screenshot_path}")
            return screenshot_path
        else:
            logger.error("Failed to take screenshot")
            return ""
    
    def analyze_current_screen(self, task: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze current screen state
        
        Args:
            task: Optional task context
            
        Returns:
            Screen analysis result
        """
        screenshot_path = self.take_screenshot()
        if not screenshot_path:
            return {}
        
        return self.vision.analyze_screen(screenshot_path, task)
    
    def create_plan(self, task: str) -> List[str]:
        """
        Create action plan for task using local LLM
        
        Args:
            task: Task description
            
        Returns:
            List of action steps
        """
        logger.info(f"Creating plan for task: {task}")
        
        # Get current screen context
        screen_info = self.vision.get_current_app_info()
        context = f"Current app: {screen_info['app_name']}\nWindow: {screen_info['window_title']}"
        
        # Ask LLM to create plan
        plan_text = self.llm.plan_actions(task, context)
        
        # Parse plan into steps
        steps = []
        for line in plan_text.split('\n'):
            line = line.strip()
            # Look for numbered steps
            if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                # Remove numbering
                step = line.lstrip('0123456789.-•) ').strip()
                if step:
                    steps.append(step)
        
        logger.info(f"Created plan with {len(steps)} steps")
        for i, step in enumerate(steps, 1):
            logger.info(f"  {i}. {step}")
        
        return steps
    
    def execute_step(self, step: str) -> bool:
        """
        Execute a single action step
        
        Args:
            step: Step description
            
        Returns:
            True if successful
        """
        logger.info(f"Executing step: {step}")
        
        # Analyze current screen
        screenshot_path = self.take_screenshot()
        if not screenshot_path:
            return False
        
        screen_analysis = self.vision.analyze_screen(screenshot_path, step)
        
        # Ask LLM what action to take
        prompt = f"""You are controlling a computer. Execute this step: {step}

Current screen state:
- App: {screen_analysis.get('app_name', 'Unknown')}
- Window: {screen_analysis.get('window_title', 'Unknown')}
- Text on screen: {screen_analysis.get('text_content', '')[:500]}
- Buttons: {screen_analysis.get('buttons', [])}

What action should you take? Choose ONE action:
1. CLICK <button_text> - Click a button
2. TYPE <text> - Type text
3. HOTKEY <key1>+<key2> - Press key combination
4. OPEN_APP <app_name> - Open application
5. WAIT <seconds> - Wait

Output format: ACTION <parameters>
Example: CLICK Submit
Example: TYPE hello world
Example: HOTKEY cmd+space
"""
        
        action_response = self.llm.generate(prompt, temperature=0.3)
        
        logger.debug(f"LLM action: {action_response}")
        
        # Parse and execute action
        return self._execute_action(action_response, screenshot_path)
    
    def _execute_action(self, action_text: str, screenshot_path: str) -> bool:
        """
        Parse and execute action
        
        Args:
            action_text: Action description from LLM
            screenshot_path: Current screenshot path
            
        Returns:
            True if successful
        """
        action_text = action_text.strip().upper()
        
        # Parse action
        if action_text.startswith('CLICK '):
            button_text = action_text[6:].strip()
            return self._click_button(button_text, screenshot_path)
        
        elif action_text.startswith('TYPE '):
            text = action_text[5:].strip()
            return self.input.type_text(text)
        
        elif action_text.startswith('HOTKEY '):
            keys = action_text[7:].strip().split('+')
            return self.input.hotkey(*keys)
        
        elif action_text.startswith('OPEN_APP '):
            app_name = action_text[9:].strip()
            return self._open_app(app_name)
        
        elif action_text.startswith('WAIT '):
            try:
                seconds = float(action_text[5:].strip())
                self.input.wait(seconds)
                return True
            except ValueError:
                return False
        
        else:
            logger.warning(f"Unknown action: {action_text}")
            return False
    
    def _click_button(self, button_text: str, screenshot_path: str) -> bool:
        """Click button by text"""
        # Try to find button coordinates
        coords = self.vision.find_element(screenshot_path, button_text, 'button')
        
        if coords:
            return self.input.click(coords[0], coords[1])
        else:
            logger.warning(f"Button '{button_text}' not found")
            return False
    
    def _open_app(self, app_name: str) -> bool:
        """Open application using Spotlight"""
        # Open Spotlight
        if not self.input.open_spotlight():
            return False
        
        # Wait for Spotlight to open
        self.input.wait(0.5)
        
        # Type app name
        if not self.input.type_text(app_name):
            return False
        
        # Wait for search
        self.input.wait(0.5)
        
        # Press Enter
        return self.input.press_key('return')
    
    async def execute_task(self, task: str) -> bool:
        """
        Execute complete task
        
        Args:
            task: Task description
            
        Returns:
            True if successful
        """
        logger.info(f"Starting task: {task}")
        
        self.current_task = task
        
        # Create plan
        self.current_plan = self.create_plan(task)
        
        if not self.current_plan:
            logger.error("Failed to create plan")
            return False
        
        # Execute each step
        for i, step in enumerate(self.current_plan, 1):
            self.current_step = i
            
            logger.info(f"Step {i}/{len(self.current_plan)}: {step}")
            
            success = self.execute_step(step)
            
            if not success:
                logger.error(f"Step {i} failed: {step}")
                return False
            
            # Wait between steps
            self.input.wait(1.0)
        
        logger.info("Task completed successfully!")
        return True
    
    def chat(self, message: str) -> str:
        """
        Chat with agent
        
        Args:
            message: User message
            
        Returns:
            Agent response
        """
        # Add to conversation history
        self.conversation_history.append({
            'role': 'user',
            'content': message
        })
        
        # Get response from LLM
        response = self.llm.chat(self.conversation_history)
        
        # Add to history
        self.conversation_history.append({
            'role': 'assistant',
            'content': response
        })
        
        return response
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            'current_task': self.current_task,
            'current_step': self.current_step,
            'total_steps': len(self.current_plan),
            'plan': self.current_plan,
            'statistics': self.vision.get_statistics()
        }


# Singleton instance
_mvp_agent: Optional[MVPAgent] = None


def get_mvp_agent() -> MVPAgent:
    """Get singleton MVP agent instance"""
    global _mvp_agent
    if _mvp_agent is None:
        _mvp_agent = MVPAgent()
    return _mvp_agent

