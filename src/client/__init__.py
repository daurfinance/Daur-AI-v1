#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: Система взаимодействия с клиентом
"""

from .client_interaction import (
    CommunicationChannel,
    MessageType,
    TaskStatus,
    ClientMessage,
    ClientTask,
    ClientProfile,
    TelegramConnector,
    EmailConnector,
    WebhookConnector,
    ClientInteractionManager,
    get_client_interaction_manager
)

__all__ = [
    'CommunicationChannel',
    'MessageType',
    'TaskStatus',
    'ClientMessage',
    'ClientTask',
    'ClientProfile',
    'TelegramConnector',
    'EmailConnector',
    'WebhookConnector',
    'ClientInteractionManager',
    'get_client_interaction_manager'
]

