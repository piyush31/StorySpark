#!/usr/bin/env python3
"""
Simple test script to directly test the Gemini API
"""
import os
import google.generativeai as genai
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    # Check for API key
    gemini_api_key = os.environ.get("GEMINI_KEY")
    if not gemini_api_key:
        logger.error("GEMINI_KEY environment variable not found")
        return 1
    
    logger.info(f"Using GEMINI_KEY with length: {len(gemini_api_key)}")
    
    # Configure Gemini API
    genai.configure(api_key=gemini_api_key)
    
    # Create model instance
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    # Test prompt
    prompt = """Write a children's story for age group 5-8 years about friendship.
    Make the story take place in a space station.
    Make Luna the main character.
    Make the story engaging, age-appropriate, and with a clear beginning, middle, and end.
    Use simple language that children can understand.
    Divide the story into paragraphs for better readability.
    Start with a title on the first line prefixed with "Title: ".
    The story should convey positive values and end with a meaningful lesson.
    """
    
    # Generate content
    logger.info("Sending request to Gemini API...")
    response = model.generate_content(prompt)
    
    # Print response
    if hasattr(response, 'text'):
        logger.info(f"Generated story with {len(response.text)} characters")
        print("\n" + "="*50 + "\n")
        print(response.text)
        print("\n" + "="*50 + "\n")
        return 0
    else:
        logger.error("Failed to generate content: Response has no text attribute")
        logger.error(f"Response: {response}")
        return 1

if __name__ == "__main__":
    exit(main())
