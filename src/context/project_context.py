"""
Project Context System

Based on ANUS project's ANUS.md concept:
- Read project-specific context from .daur/context.md
- Allow users to customize agent behavior per project
- Include context in agent prompts
"""

import os
import logging
from pathlib import Path
from typing import Optional, Dict, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ProjectContext:
    """Project-specific context"""
    project_name: Optional[str] = None
    project_description: Optional[str] = None
    goals: List[str] = None
    instructions: List[str] = None
    custom_commands: Dict[str, str] = None
    preferences: Dict[str, str] = None
    raw_content: str = ""
    
    def __post_init__(self):
        if self.goals is None:
            self.goals = []
        if self.instructions is None:
            self.instructions = []
        if self.custom_commands is None:
            self.custom_commands = {}
        if self.preferences is None:
            self.preferences = {}


class ProjectContextLoader:
    """Loads project context from .daur/context.md"""
    
    CONTEXT_FILENAME = "context.md"
    CONTEXT_DIR = ".daur"
    
    @staticmethod
    def find_context_file(start_dir: Optional[str] = None) -> Optional[Path]:
        """
        Find .daur/context.md file by walking up directory tree
        
        Args:
            start_dir: Directory to start search from (default: current dir)
            
        Returns:
            Path to context file or None
        """
        if start_dir is None:
            start_dir = os.getcwd()
        
        current = Path(start_dir).resolve()
        
        # Walk up directory tree
        while True:
            context_file = current / ProjectContextLoader.CONTEXT_DIR / ProjectContextLoader.CONTEXT_FILENAME
            
            if context_file.exists():
                logger.info(f"Found project context: {context_file}")
                return context_file
            
            # Check if we've reached root
            parent = current.parent
            if parent == current:
                break
            current = parent
        
        logger.debug("No project context file found")
        return None
    
    @staticmethod
    def load_context(context_file: Path) -> ProjectContext:
        """
        Load and parse project context file
        
        Args:
            context_file: Path to context.md file
            
        Returns:
            ProjectContext object
        """
        try:
            with open(context_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return ProjectContextLoader.parse_context(content)
        
        except Exception as e:
            logger.error(f"Failed to load context file: {e}")
            return ProjectContext(raw_content="")
    
    @staticmethod
    def parse_context(content: str) -> ProjectContext:
        """
        Parse markdown context content
        
        Args:
            content: Markdown content
            
        Returns:
            ProjectContext object
        """
        context = ProjectContext(raw_content=content)
        
        lines = content.split('\n')
        current_section = None
        current_list = []
        
        for line in lines:
            line_stripped = line.strip()
            
            # Skip empty lines
            if not line_stripped:
                continue
            
            # Check for headers
            if line_stripped.startswith('#'):
                # Save previous section
                if current_section and current_list:
                    ProjectContextLoader._save_section(
                        context, current_section, current_list
                    )
                    current_list = []
                
                # Parse header
                header = line_stripped.lstrip('#').strip().lower()
                
                if 'project' in header and ':' in line_stripped:
                    # Project: Name format
                    context.project_name = line_stripped.split(':', 1)[1].strip()
                elif 'goal' in header:
                    current_section = 'goals'
                elif 'instruction' in header:
                    current_section = 'instructions'
                elif 'command' in header:
                    current_section = 'commands'
                elif 'preference' in header:
                    current_section = 'preferences'
                elif 'description' in header:
                    current_section = 'description'
                else:
                    current_section = None
            
            # Check for list items
            elif line_stripped.startswith('-') or line_stripped.startswith('*'):
                item = line_stripped.lstrip('-*').strip()
                current_list.append(item)
            
            # Check for key-value pairs (for commands/preferences)
            elif current_section in ['commands', 'preferences'] and ':' in line_stripped:
                key, value = line_stripped.split(':', 1)
                key = key.strip().strip('"\'')
                value = value.strip().strip('"\'')
                
                if current_section == 'commands':
                    context.custom_commands[key] = value
                elif current_section == 'preferences':
                    context.preferences[key] = value
            
            # Regular text for description
            elif current_section == 'description':
                if context.project_description:
                    context.project_description += ' ' + line_stripped
                else:
                    context.project_description = line_stripped
        
        # Save last section
        if current_section and current_list:
            ProjectContextLoader._save_section(context, current_section, current_list)
        
        return context
    
    @staticmethod
    def _save_section(context: ProjectContext, section: str, items: List[str]):
        """Save parsed section to context"""
        if section == 'goals':
            context.goals = items
        elif section == 'instructions':
            context.instructions = items
    
    @staticmethod
    def load_project_context(start_dir: Optional[str] = None) -> Optional[ProjectContext]:
        """
        Find and load project context
        
        Args:
            start_dir: Directory to start search from
            
        Returns:
            ProjectContext or None
        """
        context_file = ProjectContextLoader.find_context_file(start_dir)
        
        if context_file is None:
            return None
        
        return ProjectContextLoader.load_context(context_file)
    
    @staticmethod
    def format_context_for_prompt(context: ProjectContext) -> str:
        """
        Format project context for inclusion in AI prompt
        
        Args:
            context: ProjectContext object
            
        Returns:
            Formatted string for prompt
        """
        if not context or not context.raw_content:
            return ""
        
        parts = []
        
        parts.append("## Project Context")
        parts.append("")
        
        if context.project_name:
            parts.append(f"**Project:** {context.project_name}")
            parts.append("")
        
        if context.project_description:
            parts.append(f"**Description:** {context.project_description}")
            parts.append("")
        
        if context.goals:
            parts.append("**Goals:**")
            for goal in context.goals:
                parts.append(f"- {goal}")
            parts.append("")
        
        if context.instructions:
            parts.append("**Instructions:**")
            for instruction in context.instructions:
                parts.append(f"- {instruction}")
            parts.append("")
        
        if context.custom_commands:
            parts.append("**Custom Commands:**")
            for cmd, action in context.custom_commands.items():
                parts.append(f"- `{cmd}` → {action}")
            parts.append("")
        
        if context.preferences:
            parts.append("**Preferences:**")
            for key, value in context.preferences.items():
                parts.append(f"- {key}: {value}")
            parts.append("")
        
        return '\n'.join(parts)


# Convenience function

def load_and_format_context(start_dir: Optional[str] = None) -> str:
    """
    Load project context and format for prompt
    
    Args:
        start_dir: Directory to start search from
        
    Returns:
        Formatted context string (empty if no context found)
    """
    context = ProjectContextLoader.load_project_context(start_dir)
    
    if context is None:
        return ""
    
    return ProjectContextLoader.format_context_for_prompt(context)

