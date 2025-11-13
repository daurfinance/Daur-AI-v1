#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Adaptive Planner - Creates and adapts execution plans based on vision and system state
Plans actions dynamically based on current screen state and system capabilities
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import json

from src.ai.openai_client import OpenAIClient

LOG = logging.getLogger("daur_ai.adaptive_planner")


@dataclass
class Action:
    """Represents a planned action"""
    type: str  # 'open_app', 'type_text', 'click', 'hotkey', etc.
    description: str
    parameters: Dict[str, Any]
    reasoning: str = ""  # Optional
    expected_outcome: str = ""  # Optional


@dataclass
class Plan:
    """Represents an execution plan"""
    goal: str
    actions: List[Action]
    reasoning: str = ""
    estimated_time: int = 0  # seconds
    contingency: Optional[str] = None  # Optional


class AdaptivePlanner:
    """
    Creates execution plans that adapt to current system state and screen content.
    Uses vision analysis and system profile to generate context-aware plans.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the adaptive planner.
        
        Args:
            api_key: OpenAI API key (optional, will use env var if not provided)
        """
        self.ai = OpenAIClient(api_key=api_key)
        LOG.info("AdaptivePlanner initialized")
    
    async def create_plan(
        self,
        command: str,
        system_profile: Dict[str, Any],
        screen_analysis: Optional[Dict[str, Any]] = None
    ) -> Plan:
        """
        Create an adaptive execution plan based on command, system state, and screen content.
        
        Args:
            command: User's natural language command
            system_profile: System profile from SystemProfiler
            screen_analysis: Current screen analysis from VisionAnalyzer (optional)
            
        Returns:
            Plan object with adaptive actions
        """
        LOG.info(f"Creating adaptive plan for: {command}")
        
        # Build context-aware prompt
        prompt = self._build_planning_prompt(command, system_profile, screen_analysis)
        
        try:
            response = await self.ai.chat_async(prompt, json_mode=True)
            
            # JSON mode guarantees valid JSON
            plan_data = json.loads(response)
            
            # Convert to Plan object
            actions = [
                Action(
                    type=a['type'],
                    description=a['description'],
                    parameters=a.get('parameters', {}),
                    reasoning=a.get('reasoning', ''),
                    expected_outcome=a.get('expected_outcome', '')
                )
                for a in plan_data.get('actions', [])
            ]
            
            plan = Plan(
                goal=plan_data.get('goal', command),
                actions=actions,
                reasoning=plan_data.get('reasoning', ''),
                estimated_time=plan_data.get('estimated_time', len(actions) * 3),
                contingency=plan_data.get('contingency')
            )
            
            LOG.info(f"Plan created with {len(actions)} actions")
            return plan
        
        except Exception as e:
            LOG.error(f"Plan creation failed: {e}")
            return self._create_fallback_plan(command)
    
    def _build_planning_prompt(
        self,
        command: str,
        system_profile: Dict[str, Any],
        screen_analysis: Optional[Dict[str, Any]]
    ) -> str:
        """Build a context-aware planning prompt."""
        
        # Extract key system info
        os_info = system_profile.get('os', {})
        shortcuts = system_profile.get('shortcuts', {})
        keyboard = system_profile.get('keyboard', {})
        apps = system_profile.get('applications', [])
        
        # Extract screen info if available
        screen_context = ""
        if screen_analysis:
            screen_context = f"""

CURRENT SCREEN STATE:
- Active app: {screen_analysis.get('active_app', 'unknown')}
- Visible apps: {', '.join(screen_analysis.get('visible_apps', []))}
- Spotlight open: {screen_analysis.get('spotlight_open', False)}
- Keyboard layout: {screen_analysis.get('keyboard_layout', 'unknown')}
- Issues: {', '.join(screen_analysis.get('issues', []))}
"""
        
        prompt = f"""You are an adaptive AI agent creating an execution plan for macOS.

USER COMMAND: "{command}"

SYSTEM INFORMATION:
- OS: {os_info.get('system', 'macOS')} {os_info.get('release', '')}
- Spotlight shortcut: {shortcuts.get('spotlight', 'command+space')}
- Layout switch: {keyboard.get('switch_shortcut', 'ctrl+space')}
- Installed apps: {', '.join(apps[:20])}... ({len(apps)} total)
{screen_context}

AVAILABLE ACTION TYPES:
1. open_app: Open an application
   Parameters: {{"app": "AppName"}}
   
2. hotkey: Press keyboard shortcut
   Parameters: {{"key1": "command", "key2": "space", ...}}
   
3. type_text: Type text
   Parameters: {{"text": "text to type"}}
   
4. press_key: Press single key
   Parameters: {{"key": "enter"}}
   
5. click: Click at coordinates
   Parameters: {{"x": 100, "y": 200}}
   
6. wait: Wait for duration
   Parameters: {{"seconds": 2}}
   
7. switch_layout: Switch keyboard layout
   Parameters: {{"target_layout": "en"}}

PLANNING RULES:
1. Use ACTUAL system information (installed apps, shortcuts)
2. Consider CURRENT screen state if provided
3. Include keyboard layout switching if needed (use {shortcuts.get('keyboard_layout_switch', 'ctrl+space')})
4. Add small wait times (1-2s) after actions that change UI
5. Keep it simple - model will see results in screenshots

Create a simple, executable plan in JSON format:

{{
  "goal": "Clear description of goal",
  "reasoning": "Brief reasoning for approach",
  "estimated_time": 10,
  "actions": [
    {{
      "type": "action_type",
      "description": "What this action does",
      "parameters": {{"param": "value"}}
    }},
    ...
  ]
}}

Keep it simple. No verification steps - model will see results automatically.
"""
        
        return prompt
    
    def _create_fallback_plan(self, command: str) -> Plan:
        """Create a simple fallback plan when planning fails."""
        LOG.warning("Creating fallback plan")
        
        return Plan(
            goal=command,
            actions=[
                Action(
                    type="open_app",
                    description=f"Attempt to execute: {command}",
                    parameters={"app": "Finder"},
                    reasoning="Fallback action",
                    expected_outcome="Finder opens"
                )
            ],
            reasoning="Fallback plan due to planning failure",
            estimated_time=5,
            contingency="Manual intervention required"
        )
    
    async def adapt_plan(
        self,
        original_plan: Plan,
        current_action_index: int,
        screen_analysis: Dict[str, Any],
        issue_description: str
    ) -> Plan:
        """
        Adapt an existing plan based on unexpected screen state or issues.
        
        Args:
            original_plan: The original plan being executed
            current_action_index: Index of action that failed or caused issue
            screen_analysis: Current screen analysis
            issue_description: Description of what went wrong
            
        Returns:
            Adapted plan with corrective actions
        """
        LOG.info(f"Adapting plan due to: {issue_description}")
        
        prompt = f"""An execution plan encountered an issue and needs adaptation.

ORIGINAL GOAL: {original_plan.goal}
CURRENT ACTION INDEX: {current_action_index}
ISSUE: {issue_description}

CURRENT SCREEN STATE:
{json.dumps(screen_analysis, indent=2)}

REMAINING ACTIONS:
{json.dumps([
    {{
        "type": a.type,
        "description": a.description,
        "expected_outcome": a.expected_outcome
    }}
    for a in original_plan.actions[current_action_index:]
], indent=2)}

Create an ADAPTED plan that:
1. Addresses the current issue
2. Gets back on track to achieve the original goal
3. Includes verification steps
4. Has a contingency if this also fails

Respond in the same JSON format as before.
"""
        
        try:
            response = await self.ai.chat_async(prompt, temperature=0.7, max_tokens=2000)
            
            # Extract JSON
            start = response.find('{')
            end = response.rfind('}') + 1
            
            if start >= 0 and end > start:
                json_str = response[start:end]
                plan_data = json.loads(json_str)
                
                # Convert to Plan object
                actions = [
                    Action(
                        type=a['type'],
                        description=a['description'],
                        parameters=a.get('parameters', {}),
                        reasoning=a.get('reasoning', ''),
                        expected_outcome=a.get('expected_outcome', '')
                    )
                    for a in plan_data.get('actions', [])
                ]
                
                adapted_plan = Plan(
                    goal=plan_data.get('goal', original_plan.goal),
                    actions=actions,
                    reasoning=plan_data.get('reasoning', 'Adapted plan'),
                    estimated_time=plan_data.get('estimated_time', len(actions) * 3),
                    contingency=plan_data.get('contingency')
                )
                
                LOG.info(f"Plan adapted with {len(actions)} new actions")
                return adapted_plan
        
        except Exception as e:
            LOG.error(f"Plan adaptation failed: {e}")
        
        # Return simplified continuation plan
        return Plan(
            goal=original_plan.goal,
            actions=original_plan.actions[current_action_index:],
            reasoning="Continue with remaining actions",
            estimated_time=5,
            contingency="Manual intervention"
        )


if __name__ == "__main__":
    # Test the adaptive planner
    import asyncio
    
    logging.basicConfig(level=logging.INFO)
    
    async def test():
        planner = AdaptivePlanner()
        
        # Mock system profile
        system_profile = {
            "os": {"system": "Darwin", "release": "23.0.0"},
            "shortcuts": {"spotlight": "command+space"},
            "keyboard": {"switch_shortcut": "ctrl+space"},
            "applications": ["Safari", "Finder", "Terminal", "Notes"]
        }
        
        # Test plan creation
        plan = await planner.create_plan(
            "Open Safari and search for AI",
            system_profile
        )
        
        print("\n" + "="*60)
        print("ADAPTIVE PLANNER TEST")
        print("="*60)
        print(f"\nGoal: {plan.goal}")
        print(f"Reasoning: {plan.reasoning}")
        print(f"Estimated time: {plan.estimated_time}s")
        print(f"\nActions ({len(plan.actions)}):")
        for i, action in enumerate(plan.actions, 1):
            print(f"\n{i}. {action.type}: {action.description}")
            print(f"   Parameters: {action.parameters}")
            print(f"   Expected: {action.expected_outcome}")
        print("="*60)
    
    asyncio.run(test())

