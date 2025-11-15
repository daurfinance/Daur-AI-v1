"""
Ollama Client - Local LLM Integration
Provides interface to local Ollama models (Llama 3.2, LLaVA, CodeLlama)
"""

import requests
import json
import base64
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path

logger = logging.getLogger(__name__)


class OllamaClient:
    """Client for interacting with local Ollama LLM server"""
    
    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        default_model: str = "llama3.2:3b",
        vision_model: str = "llava",
        code_model: str = "codellama:7b"
    ):
        """
        Initialize Ollama client
        
        Args:
            base_url: Ollama server URL
            default_model: Default text model (llama3.2:3b or llama3.2:11b)
            vision_model: Vision model for image analysis (llava or llama3.2-vision:11b)
            code_model: Code generation model (codellama:7b)
        """
        self.base_url = base_url
        self.default_model = default_model
        self.vision_model = vision_model
        self.code_model = code_model
        
        self.generate_url = f"{base_url}/api/generate"
        self.chat_url = f"{base_url}/api/chat"
        self.models_url = f"{base_url}/api/tags"
        
        logger.info(f"Ollama client initialized with base URL: {base_url}")
        logger.info(f"Default model: {default_model}")
        logger.info(f"Vision model: {vision_model}")
        logger.info(f"Code model: {code_model}")
    
    def check_connection(self) -> bool:
        """Check if Ollama server is running"""
        try:
            response = requests.get(self.models_url, timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to connect to Ollama server: {e}")
            return False
    
    def list_models(self) -> List[str]:
        """List all available models"""
        try:
            response = requests.get(self.models_url)
            if response.status_code == 200:
                data = response.json()
                return [model['name'] for model in data.get('models', [])]
            return []
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            return []
    
    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        stream: bool = False
    ) -> str:
        """
        Generate text completion
        
        Args:
            prompt: Input prompt
            model: Model to use (defaults to default_model)
            system: System prompt
            temperature: Sampling temperature (0.0 - 1.0)
            max_tokens: Maximum tokens to generate
            stream: Whether to stream response
            
        Returns:
            Generated text
        """
        model = model or self.default_model
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": stream,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        if system:
            payload["system"] = system
        
        try:
            logger.debug(f"Generating with model {model}: {prompt[:100]}...")
            response = requests.post(self.generate_url, json=payload, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                generated_text = result.get('response', '')
                logger.debug(f"Generated {len(generated_text)} characters")
                return generated_text
            else:
                logger.error(f"Generation failed: {response.status_code} - {response.text}")
                return ""
                
        except Exception as e:
            logger.error(f"Error during generation: {e}")
            return ""
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """
        Chat completion with conversation history
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Assistant's response
        """
        model = model or self.default_model
        
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        try:
            logger.debug(f"Chat with {len(messages)} messages using {model}")
            response = requests.post(self.chat_url, json=payload, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                message = result.get('message', {})
                content = message.get('content', '')
                logger.debug(f"Chat response: {len(content)} characters")
                return content
            else:
                logger.error(f"Chat failed: {response.status_code} - {response.text}")
                return ""
                
        except Exception as e:
            logger.error(f"Error during chat: {e}")
            return ""
    
    def analyze_image(
        self,
        image_path: str,
        prompt: str,
        model: Optional[str] = None
    ) -> str:
        """
        Analyze image using vision model
        
        Args:
            image_path: Path to image file
            prompt: Question/instruction about the image
            model: Vision model to use (defaults to vision_model)
            
        Returns:
            Analysis result
        """
        model = model or self.vision_model
        
        # Read and encode image
        try:
            with open(image_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
        except Exception as e:
            logger.error(f"Failed to read image {image_path}: {e}")
            return ""
        
        payload = {
            "model": model,
            "prompt": prompt,
            "images": [image_data],
            "stream": False,
            "options": {
                "temperature": 0.3,  # Lower temperature for more focused analysis
                "num_predict": 1000
            }
        }
        
        try:
            logger.debug(f"Analyzing image with {model}: {prompt[:100]}...")
            response = requests.post(self.generate_url, json=payload, timeout=90)
            
            if response.status_code == 200:
                result = response.json()
                analysis = result.get('response', '')
                logger.debug(f"Image analysis: {len(analysis)} characters")
                return analysis
            else:
                logger.error(f"Image analysis failed: {response.status_code}")
                return ""
                
        except Exception as e:
            logger.error(f"Error during image analysis: {e}")
            return ""
    
    def generate_code(
        self,
        task_description: str,
        language: str = "python",
        model: Optional[str] = None
    ) -> str:
        """
        Generate code using specialized code model
        
        Args:
            task_description: What the code should do
            language: Programming language
            model: Code model to use (defaults to code_model)
            
        Returns:
            Generated code
        """
        model = model or self.code_model
        
        system_prompt = f"""You are an expert {language} programmer. 
Generate clean, working code based on the task description.
Only output the code, no explanations."""
        
        prompt = f"""Task: {task_description}

Language: {language}

Code:"""
        
        return self.generate(
            prompt=prompt,
            model=model,
            system=system_prompt,
            temperature=0.2,  # Lower temperature for more deterministic code
            max_tokens=3000
        )
    
    def plan_actions(self, task: str, context: Optional[str] = None) -> str:
        """
        Create action plan for a task
        
        Args:
            task: Task description
            context: Additional context (current screen state, etc.)
            
        Returns:
            Step-by-step action plan
        """
        system_prompt = """You are an AI agent that controls a computer.
Given a task, create a detailed step-by-step action plan.
Be specific about which applications to use and what actions to take.
Output the plan as a numbered list."""
        
        prompt = f"""Task: {task}"""
        
        if context:
            prompt += f"\n\nCurrent Context:\n{context}"
        
        prompt += "\n\nAction Plan:"
        
        return self.generate(
            prompt=prompt,
            system=system_prompt,
            temperature=0.5,
            max_tokens=1500
        )
    
    def extract_json(self, text: str, prompt: str) -> Dict[str, Any]:
        """
        Extract structured JSON from text
        
        Args:
            text: Input text
            prompt: Instruction for extraction
            
        Returns:
            Extracted JSON as dict
        """
        system_prompt = """You are a JSON extraction expert.
Extract the requested information and output ONLY valid JSON.
No explanations, no markdown, just pure JSON."""
        
        full_prompt = f"""{prompt}

Input:
{text}

JSON Output:"""
        
        response = self.generate(
            prompt=full_prompt,
            system=system_prompt,
            temperature=0.1,
            max_tokens=2000
        )
        
        # Try to parse JSON
        try:
            # Remove markdown code blocks if present
            response = response.strip()
            if response.startswith('```'):
                response = response.split('```')[1]
                if response.startswith('json'):
                    response = response[4:]
            
            return json.loads(response)
        except Exception as e:
            logger.error(f"Failed to parse JSON: {e}")
            return {}


# Singleton instance
_ollama_client: Optional[OllamaClient] = None


def get_ollama_client() -> OllamaClient:
    """Get singleton Ollama client instance"""
    global _ollama_client
    if _ollama_client is None:
        _ollama_client = OllamaClient()
    return _ollama_client

