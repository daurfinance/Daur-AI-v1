#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: OpenAI Client Wrapper
Simplified client for intelligent agent usage

Version: 1.0
Date: 2025-01-13
"""

import json
import logging
import os
import requests
from typing import Dict, List, Any, Optional


class OpenAIClient:
    """
    Simplified OpenAI API client for intelligent agent
    """
    
    def __init__(self, api_key: str = None, model: str = "gpt-4"):
        """
        Initialize OpenAI client
        
        Args:
            api_key (str): OpenAI API key (defaults to OPENAI_API_KEY env var)
            model (str): Model to use (default: gpt-4)
        """
        self.logger = logging.getLogger('daur_ai.openai_client')
        
        self.api_key = api_key or os.getenv('OPENAI_API_KEY', '')
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
        
        self.model = model
        self.base_url = "https://api.openai.com/v1"
        self.timeout = 60  # Longer timeout for complex requests
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        self.logger.info(f"OpenAI client initialized with model: {self.model}")
    
    async def chat_async(self, prompt: str, 
                        temperature: float = 0.7,
                        max_tokens: int = 2000,
                        json_mode: bool = False) -> str:
        """Async chat with simple prompt string.
        
        Args:
            prompt: User prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            json_mode: Enable JSON mode for structured output
            
        Returns:
            str: Generated response
        """
        messages = [{"role": "user", "content": prompt}]
        return self.chat(messages, temperature, max_tokens, json_mode=json_mode)
    
    def chat(self, messages: List[Dict[str, str]], 
             temperature: float = 0.7,
             max_tokens: int = 2000,
             json_mode: bool = False,
             **kwargs) -> str:
        """
        Send chat completion request
        
        Args:
            messages (List[Dict]): List of message dicts with 'role' and 'content'
            temperature (float): Sampling temperature (0-2)
            max_tokens (int): Maximum tokens to generate
            json_mode (bool): Enable JSON mode for structured output
            **kwargs: Additional parameters
            
        Returns:
            str: Generated response text
            
        Raises:
            Exception: If API request fails
        """
        try:
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                **kwargs
            }
            
            # Enable JSON mode if requested
            if json_mode:
                payload["response_format"] = {"type": "json_object"}
            
            self.logger.debug(f"Sending chat request: {len(messages)} messages, model={self.model}")
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data['choices'][0]['message']['content']
                
                # Log token usage if available
                if 'usage' in data:
                    usage = data['usage']
                    self.logger.debug(
                        f"Tokens used: {usage.get('total_tokens', 0)} "
                        f"(prompt: {usage.get('prompt_tokens', 0)}, "
                        f"completion: {usage.get('completion_tokens', 0)})"
                    )
                
                return content
            else:
                error_msg = f"OpenAI API error: HTTP {response.status_code}"
                try:
                    error_data = response.json()
                    if 'error' in error_data:
                        error_msg += f" - {error_data['error'].get('message', '')}"
                except:
                    pass
                
                self.logger.error(error_msg)
                raise Exception(error_msg)
                
        except requests.exceptions.Timeout:
            error_msg = "OpenAI API request timed out"
            self.logger.error(error_msg)
            raise Exception(error_msg)
            
        except requests.exceptions.RequestException as e:
            error_msg = f"OpenAI API request failed: {str(e)}"
            self.logger.error(error_msg)
            raise Exception(error_msg)
            
        except Exception as e:
            error_msg = f"Unexpected error in OpenAI chat: {str(e)}"
            self.logger.error(error_msg)
            raise Exception(error_msg)
    
    def simple_chat(self, user_message: str, 
                    system_message: str = None,
                    temperature: float = 0.7,
                    max_tokens: int = 2000) -> str:
        """
        Simple chat interface with single user message
        
        Args:
            user_message (str): User's message
            system_message (str): Optional system message
            temperature (float): Sampling temperature
            max_tokens (int): Maximum tokens to generate
            
        Returns:
            str: Generated response
        """
        messages = []
        
        if system_message:
            messages.append({
                "role": "system",
                "content": system_message
            })
        
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        return self.chat(messages, temperature=temperature, max_tokens=max_tokens)
    
    def parse_json_response(self, response: str) -> Any:
        """
        Parse JSON from response, handling markdown code blocks
        
        Args:
            response (str): Response text that may contain JSON
            
        Returns:
            Any: Parsed JSON object
            
        Raises:
            json.JSONDecodeError: If JSON parsing fails
        """
        # Clean response
        response = response.strip()
        
        # Remove markdown code blocks
        if response.startswith('```json'):
            response = response[7:]
        elif response.startswith('```'):
            response = response[3:]
        
        if response.endswith('```'):
            response = response[:-3]
        
        response = response.strip()
        
        # Parse JSON
        return json.loads(response)
    
    def chat_with_json(self, messages: List[Dict[str, str]], 
                       temperature: float = 0.7,
                       max_tokens: int = 2000) -> Any:
        """
        Chat and parse response as JSON
        
        Args:
            messages (List[Dict]): Chat messages
            temperature (float): Sampling temperature
            max_tokens (int): Maximum tokens
            
        Returns:
            Any: Parsed JSON object
        """
        response = self.chat(messages, temperature=temperature, max_tokens=max_tokens)
        return self.parse_json_response(response)
    
    def is_available(self) -> bool:
        """
        Check if OpenAI API is available
        
        Returns:
            bool: True if API is accessible
        """
        try:
            response = requests.get(
                f"{self.base_url}/models",
                headers=self.headers,
                timeout=5
            )
            return response.status_code == 200
        except:
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get current model information
        
        Returns:
            Dict: Model configuration
        """
        return {
            "provider": "OpenAI",
            "model": self.model,
            "base_url": self.base_url,
            "timeout": self.timeout,
            "available": self.is_available()
        }


# Convenience function for quick usage
def create_client(model: str = "gpt-4") -> OpenAIClient:
    """
    Create OpenAI client with default settings
    
    Args:
        model (str): Model to use
        
    Returns:
        OpenAIClient: Initialized client
    """
    return OpenAIClient(model=model)

