"""
Data models for the multi-character roleplay system.
This module re-exports models and managers from other modules for backward compatibility.
"""

# Re-export all models from data_models
from data_models import (
    Message,
    Scene,
    TimelineHistory,
    TimelineEvent,
    CharacterPersona,
    CharacterMemory,
    CharacterState,
    Character
)

# Re-export managers
from managers.timelineManager import TimelineManager
from managers.characterManager import CharacterManager

__all__ = [
    # Data models
    'Message',
    'Scene',
    'TimelineHistory',
    'TimelineEvent',
    'CharacterPersona',
    'CharacterMemory',
    'CharacterState',
    'Character',
    # Managers
    'TimelineManager',
    'CharacterManager'
]

