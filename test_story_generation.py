#!/usr/bin/env python3
"""
Test script to verify that story generation is working properly.
"""
import os
import sys
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the backend directory to the path so we can import from it
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Import the story generator
from services.voice_service import story_generator

def main():
    """Test story generation"""
    logger.info("Testing story generation...")
    
    # Check if the Gemini model is initialized
    logger.info(f"Gemini model initialized: {story_generator.gemini_model is not None}")
    
    # Generate a story
    story_data = story_generator.generate_story(
        theme="adventure",
        setting="magical forest",
        duration="short",
        age_group="5-8",
        child_name="Alex"
    )
    
    # Print the story
    logger.info(f"Generated story with title: {story_data.get('title', 'No title')}")
    logger.info(f"Story length: {len(story_data.get('text', ''))}")
    logger.info(f"Story text sample: {story_data.get('text', '')[:200]}...")
    
    if story_data.get('audio_path'):
        logger.info(f"Generated audio at: {story_data.get('audio_path')}")
    else:
        logger.error("No audio was generated!")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
