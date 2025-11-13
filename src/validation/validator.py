"""
Validation System for AI Responses and Actions

Based on ANUS project best practices:
- Validate AI responses before use
- Validate actions before execution
- Retry logic for failed validations
- Fallback to defaults when needed
"""

import json
import logging
from typing import Any, Dict, Optional, Callable
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of a validation check"""
    is_valid: bool
    error_message: Optional[str] = None
    fixed_value: Optional[Any] = None


class ResponseValidator:
    """Validates AI responses"""
    
    @staticmethod
    def is_valid_response(response: Any) -> ValidationResult:
        """
        Validate AI response structure
        
        Args:
            response: Raw response from AI
            
        Returns:
            ValidationResult with validation status
        """
        if response is None:
            return ValidationResult(
                is_valid=False,
                error_message="Response is None"
            )
        
        if isinstance(response, str):
            if not response.strip():
                return ValidationResult(
                    is_valid=False,
                    error_message="Response is empty string"
                )
            return ValidationResult(is_valid=True)
        
        # For dict responses
        if isinstance(response, dict):
            if not response:
                return ValidationResult(
                    is_valid=False,
                    error_message="Response is empty dict"
                )
            return ValidationResult(is_valid=True)
        
        return ValidationResult(is_valid=True)
    
    @staticmethod
    def is_valid_json_response(response: str) -> ValidationResult:
        """
        Validate JSON response from AI
        
        Args:
            response: JSON string from AI
            
        Returns:
            ValidationResult with parsed JSON if valid
        """
        if not response or not response.strip():
            return ValidationResult(
                is_valid=False,
                error_message="Empty JSON response"
            )
        
        try:
            parsed = json.loads(response)
            return ValidationResult(
                is_valid=True,
                fixed_value=parsed
            )
        except json.JSONDecodeError as e:
            # Try to fix common JSON errors
            fixed_response = ResponseValidator._try_fix_json(response)
            if fixed_response:
                try:
                    parsed = json.loads(fixed_response)
                    logger.warning(f"Fixed malformed JSON: {str(e)}")
                    return ValidationResult(
                        is_valid=True,
                        fixed_value=parsed
                    )
                except:
                    pass
            
            return ValidationResult(
                is_valid=False,
                error_message=f"Invalid JSON: {str(e)}"
            )
    
    @staticmethod
    def _try_fix_json(json_str: str) -> Optional[str]:
        """
        Try to fix common JSON errors
        
        Args:
            json_str: Malformed JSON string
            
        Returns:
            Fixed JSON string or None
        """
        # Remove markdown code blocks
        if "```json" in json_str:
            json_str = json_str.split("```json")[1].split("```")[0].strip()
        elif "```" in json_str:
            json_str = json_str.split("```")[1].split("```")[0].strip()
        
        # Fix single quotes to double quotes
        # (careful with apostrophes in strings)
        # This is a simple fix, may not work for all cases
        
        # Fix Python bool to JSON bool
        json_str = json_str.replace("True", "true")
        json_str = json_str.replace("False", "false")
        json_str = json_str.replace("None", "null")
        
        # Remove trailing commas
        json_str = json_str.replace(",]", "]")
        json_str = json_str.replace(",}", "}")
        
        return json_str


class ActionValidator:
    """Validates actions before execution"""
    
    VALID_ACTION_TYPES = {
        'open_app', 'type_text', 'hotkey', 'press_key',
        'click', 'wait', 'screenshot', 'done'
    }
    
    @staticmethod
    def is_valid_action(action: Dict[str, Any]) -> ValidationResult:
        """
        Validate action structure
        
        Args:
            action: Action dict to validate
            
        Returns:
            ValidationResult with validation status
        """
        if not action:
            return ValidationResult(
                is_valid=False,
                error_message="Action is empty"
            )
        
        if not isinstance(action, dict):
            return ValidationResult(
                is_valid=False,
                error_message=f"Action must be dict, got {type(action)}"
            )
        
        # Check required fields
        if 'type' not in action:
            return ValidationResult(
                is_valid=False,
                error_message="Action missing 'type' field"
            )
        
        action_type = action['type']
        
        # Check valid action type
        if action_type not in ActionValidator.VALID_ACTION_TYPES:
            return ValidationResult(
                is_valid=False,
                error_message=f"Invalid action type: {action_type}"
            )
        
        # Validate action-specific requirements
        validation = ActionValidator._validate_action_params(action)
        if not validation.is_valid:
            return validation
        
        return ValidationResult(is_valid=True)
    
    @staticmethod
    def _validate_action_params(action: Dict[str, Any]) -> ValidationResult:
        """Validate action-specific parameters"""
        action_type = action['type']
        params = action.get('params', {})
        
        if action_type == 'open_app':
            if 'app_name' not in params:
                return ValidationResult(
                    is_valid=False,
                    error_message="open_app requires 'app_name' parameter"
                )
        
        elif action_type == 'type_text':
            if 'text' not in params:
                return ValidationResult(
                    is_valid=False,
                    error_message="type_text requires 'text' parameter"
                )
        
        elif action_type == 'hotkey':
            if not any(k.startswith('key') for k in params.keys()):
                return ValidationResult(
                    is_valid=False,
                    error_message="hotkey requires key parameters (key1, key2, etc.)"
                )
        
        elif action_type == 'press_key':
            if 'key' not in params:
                return ValidationResult(
                    is_valid=False,
                    error_message="press_key requires 'key' parameter"
                )
        
        elif action_type == 'wait':
            if 'seconds' not in params:
                return ValidationResult(
                    is_valid=False,
                    error_message="wait requires 'seconds' parameter"
                )
        
        return ValidationResult(is_valid=True)


class RetryValidator:
    """Handles retry logic with validation"""
    
    @staticmethod
    async def execute_with_retry(
        func: Callable,
        validator: Callable[[Any], ValidationResult],
        max_retries: int = 3,
        default_value: Any = None
    ) -> Any:
        """
        Execute function with retry logic
        
        Args:
            func: Async function to execute
            validator: Validation function
            max_retries: Maximum number of retries
            default_value: Default value if all retries fail
            
        Returns:
            Result from func or default_value
        """
        for attempt in range(max_retries):
            try:
                result = await func()
                
                # Validate result
                validation = validator(result)
                
                if validation.is_valid:
                    # Use fixed value if available
                    return validation.fixed_value if validation.fixed_value is not None else result
                
                logger.warning(
                    f"Validation failed (attempt {attempt + 1}/{max_retries}): "
                    f"{validation.error_message}"
                )
                
            except Exception as e:
                logger.warning(
                    f"Execution failed (attempt {attempt + 1}/{max_retries}): {str(e)}"
                )
        
        # All retries failed
        logger.error(f"All {max_retries} attempts failed, using default value")
        return default_value


# Convenience functions

async def validate_and_retry_json_response(
    func: Callable,
    max_retries: int = 3,
    default_value: Dict = None
) -> Dict:
    """
    Validate JSON response with retry
    
    Args:
        func: Async function that returns JSON string
        max_retries: Maximum retries
        default_value: Default dict if all fail
        
    Returns:
        Parsed JSON dict
    """
    if default_value is None:
        default_value = {}
    
    return await RetryValidator.execute_with_retry(
        func=func,
        validator=ResponseValidator.is_valid_json_response,
        max_retries=max_retries,
        default_value=default_value
    )


async def validate_and_retry_action(
    func: Callable,
    max_retries: int = 3,
    default_value: Dict = None
) -> Dict:
    """
    Validate action with retry
    
    Args:
        func: Async function that returns action dict
        max_retries: Maximum retries
        default_value: Default action if all fail
        
    Returns:
        Validated action dict
    """
    if default_value is None:
        default_value = {'type': 'done', 'params': {}}
    
    return await RetryValidator.execute_with_retry(
        func=func,
        validator=ActionValidator.is_valid_action,
        max_retries=max_retries,
        default_value=default_value
    )

