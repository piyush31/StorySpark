#!/usr/bin/env python3
"""
Test script to verify that the main story_generator.py is using Gemini API correctly.
"""
import os
import sys
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the backend directory to the path so we can import from it
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Use print to show what we're importing
print("Importing from:", os.path.join(os.path.dirname(__file__), 'backend', 'services', 'voice_service'))

# Import the story generator
from services.voice_service import story_generator

def main():
    """Test story generation"""
    print("\n=== Environment Variables ===")
    for key, value in os.environ.items():
        if "GEMINI" in key:
            print(f"{key}: {'*' * min(len(value), 5)}")
    
    print("\n=== Story Generator Status ===")
    print(f"StoryGenerator initialized: {story_generator is not None}")
    print(f"Gemini model initialized: {story_generator.gemini_model is not None}")
    
    if not story_generator.gemini_model:
        print("\nERROR: Gemini model not initialized. Check API key.")
        return 1
    
    # Try a simple generation
    print("\n=== Generating Test Story ===")
    try:
        # Build a simple prompt
        prompt = story_generator._build_story_prompt(
            theme="friendship",
            setting="space station",
            child_name="Luna",
            age_group="5-8",
            duration_minutes="3-5"
        )
        
        print(f"Prompt (first 200 chars): {prompt[:200]}...")
        
        # Generate content directly to test API connection
        response = story_generator.gemini_model.generate_content(prompt)
        
        if hasattr(response, 'text'):
            print(f"\nSuccess! Generated {len(response.text)} characters")
            print(f"First 200 chars: {response.text[:200]}...")
            return 0
        else:
            print(f"\nError: Response has no text attribute: {response}")
            return 1
    
    except Exception as e:
        print(f"\nError generating story: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
