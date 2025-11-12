"""
Интеграционные модули Daur-AI
Обеспечивают связь между различными компонентами системы
"""

from .bot_agent_bridge import BotAgentBridge, get_bridge, initialize_bridge

__all__ = ['BotAgentBridge', 'get_bridge', 'initialize_bridge']
