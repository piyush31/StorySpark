"""
Voice service package for StorySpark

This package contains modules for text-to-speech conversion, 
sound effect management, and story narration.
"""

from .voice_service import voice_service, SoundItem, SoundType, EmotionType
from .story_generator import story_generator

__all__ = [
    'voice_service',
    'story_generator',
    'SoundItem',
    'SoundType',
    'EmotionType'
]
