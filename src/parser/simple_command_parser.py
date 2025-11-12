#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: Simple Command Parser
Processes and parses user commands for agent execution

Version: 1.0
"""

import re
import json
import logging
from typing import Dict, List, Union, Any, Optional

class SimpleCommandParser:
    """
    Simple command parser for processing user input and converting it to structured commands
    """
    
    def __init__(self):
        """Initialize command parser"""
        self.logger = logging.getLogger('daur_ai.parser')
        
        # Basic command patterns
        self._command_patterns = {
            # Basic actions
            'click': r'(?:click|press|tap)\s+(?:on\s+)?["\']?([^"\']+)["\']?',
            'type': r'(?:type|input|write)\s+["\']([^"\']+)["\'](?:\s+in\s+([^"\']+))?',
            'key': r'(?:press|hit)\s+(?:key\s+)?["\']?([^"\']+)["\']?',
            
            # Window management
            'open': r'(?:open|launch|start)\s+(?:app|program)?\s*["\']?([^"\']+)["\']?',
            'close': r'(?:close|quit|exit)\s+(?:app|program)?\s*["\']?([^"\']+)["\']?',
            'switch': r'(?:switch|go)\s+(?:to)?\s+(?:app|program|window)?\s*["\']?([^"\']+)["\']?',
            
            # File operations
            'file_create': r'(?:create|new)\s+file\s+["\']?([^"\']+)["\']?(?:\s+with\s+content\s+["\']([^"\']+)["\'])?',
            'file_read': r'(?:read|open|show|display)\s+(?:content|file)?\s+["\']?([^"\']+)["\']?',
            'file_write': r'(?:write|save)\s+["\']([^"\']+)["\'](?:\s+to\s+(?:file)?\s+["\']?([^"\']+)["\']?)',
            'file_delete': r'(?:delete|remove)\s+file\s+["\']?([^"\']+)["\']?',
            
            # System commands
            'system_exec': r'(?:execute|run)\s+command\s+["\']([^"\']+)["\']',
            'system_info': r'(?:info|status)(?:\s+(?:about|on)?\s+system)?',
            
            # Wait command
            'wait': r'(?:wait|pause|delay)\s+(?:for\s+)?(\d+)\s+(?:second|sec)s?'
        }
        
        # Compile regex patterns for optimization
        self._compiled_patterns = {
            cmd: re.compile(pattern, re.IGNORECASE) 
            for cmd, pattern in self._command_patterns.items()
        }
        
        # Chain pattern for sequences
        self.sequence_pattern = re.compile(
            r'(?:\s*,\s*|\s+and\s+|\s+then\s+)',
            re.IGNORECASE
        )
        
        self.logger.info("Command parser initialized")
    
    def parse(self, command: str) -> List[Dict[str, Any]]:
        """
        Main command parsing method
        
        Args:
            command (str): User command
            
        Returns:
            List[Dict]: List of actions to execute
        """
        try:
            parsed = self.parse_command(command)
            if parsed.get('success', False):
                return [parsed]
            return []
        except Exception as e:
            self.logger.error(f"Command parsing error: {e}")
            return []

    def parse_command(self, text: str) -> Dict[str, Any]:
        """
        Parse text command into structured format
        
        Args:
            text (str): User text command
            
        Returns:
            dict: Structured command for execution
                {
                    "type": command type,
                    "params": command parameters,
                    "raw": original command text,
                    "success": parsing success flag,
                    "error": error message (if any)
                }
        """
        self.logger.debug(f"Parsing command: {text}")
        
        # Check for empty command
        if not text or not text.strip():
            return {
                "type": "invalid",
                "params": {},
                "raw": text,
                "success": False,
                "error": "Empty command"
            }
        
        text = text.strip()
        
        # Check for command sequence
        if self.sequence_pattern.search(text):
            return self._parse_sequence(text)
        
        # Parse single command
        return self._parse_simple_command(text)
    
    def _parse_sequence(self, text: str) -> Dict[str, Any]:
        """
        Parse command sequence
        
        Args:
            text (str): Text command with sequence
            
        Returns:
            dict: Structured sequence of commands
        """
        commands_text = self.sequence_pattern.split(text)
        
        parsed_commands = []
        for cmd_text in commands_text:
            cmd_text = cmd_text.strip()
            if cmd_text:
                parsed_cmd = self._parse_simple_command(cmd_text)
                parsed_commands.append(parsed_cmd)
        
        if not parsed_commands:
            return {
                "type": "invalid",
                "params": {},
                "raw": text,
                "success": False,
                "error": "Failed to recognize commands in sequence"
            }
        
        result = {
            "type": "sequence",
            "params": {
                "commands": parsed_commands
            },
            "raw": text,
            "success": True
        }
        
        self.logger.debug(f"Recognized command sequence: {len(parsed_commands)} commands")
        return result
    
    def _parse_simple_command(self, text: str) -> Dict[str, Any]:
        """
        Parse simple command
        
        Args:
            text (str): Text command
            
        Returns:
            dict: Structured command
        """
        for cmd_type, pattern in self._compiled_patterns.items():
            match = pattern.match(text)
            if match:
                params = match.groups()
                params_dict = {}
                
                # Process parameters based on command type
                if cmd_type == 'click':
                    params_dict['target'] = params[0]
                
                elif cmd_type == 'type':
                    params_dict['text'] = params[0]
                    if len(params) > 1 and params[1]:
                        params_dict['target'] = params[1]
                
                elif cmd_type in ['open', 'close', 'switch']:
                    params_dict['app'] = params[0]
                
                elif cmd_type == 'file_create':
                    params_dict['path'] = params[0]
                    if len(params) > 1 and params[1]:
                        params_dict['content'] = params[1]
                
                elif cmd_type == 'file_read':
                    params_dict['path'] = params[0]
                
                elif cmd_type == 'file_write':
                    params_dict['content'] = params[0]
                    if len(params) > 1 and params[1]:
                        params_dict['path'] = params[1]
                
                elif cmd_type == 'file_delete':
                    params_dict['path'] = params[0]
                
                elif cmd_type == 'system_exec':
                    params_dict['command'] = params[0]
                
                elif cmd_type == 'key':
                    params_dict['key'] = params[0]
                
                elif cmd_type == 'wait':
                    params_dict['seconds'] = int(params[0]) if params[0] else 1
                
                result = {
                    "type": cmd_type,
                    "params": params_dict,
                    "raw": text,
                    "success": True
                }
                
                self.logger.debug(f"Recognized command: {cmd_type} with parameters {params_dict}")
                return result
        
        # If command not recognized
        return {
            "type": "unknown",
            "params": {"text": text},
            "raw": text,
            "success": False,
            "error": "Unknown command"
        }
    
    def format_error_message(self, cmd: Dict[str, Any]) -> str:
        """
        Format error message
        
        Args:
            cmd (dict): Command parsing result
            
        Returns:
            str: Error message
        """
        if cmd["success"]:
            return "Command recognized successfully"
        
        if "error" in cmd:
            return f"Error: {cmd['error']}"
        
        if cmd["type"] == "unknown":
            return f"Command not recognized: '{cmd['raw']}'"
        
        if cmd["type"] == "invalid":
            return f"Invalid command: '{cmd['raw']}'"
        
        return "Unknown error during command parsing"