#!/usr/bin/env python3
"""
This script checks if the Gemini API key is valid by making a simple API call.
It will help debug issues with the Gemini API key.
"""

import os
import sys
import logging
from dotenv import load_dotenv
import google.generativeai as genai

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def print_env_info():
    """Print information about relevant environment variables"""
    logger.info("Environment variables:")
    for key in sorted(os.environ.keys()):
        if "API" in key or "KEY" in key or "TOKEN" in key:
            # Mask the value except first 4 and last 4 characters
            value = os.environ.get(key, "")
            if len(value) > 12:
                masked_value = value[:4] + "*" * (len(value) - 8) + value[-4:]
            else:
                masked_value = "****"
            logger.info(f"  {key}: {masked_value} (length: {len(value)})")

def test_api_key(api_key):
    """Test if the API key is valid"""
    try:
        # Configure Gemini with the API key
        genai.configure(api_key=api_key)
        
        # Try to use a model
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content("Hello")
        
        logger.info(f"✅ API key is valid! Got response: {response.text}")
        return True
    except Exception as e:
        logger.error(f"❌ API key is not valid: {str(e)}")
        return False

def test_api_key_with_2_0(api_key):
    """Test if the API key works with gemini-2.0 models"""
    try:
        # Configure Gemini with the API key
        genai.configure(api_key=api_key)
        
        # Try to use a 2.0 model
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content("Hello")
        
        logger.info(f"✅ API key works with gemini-2.0-flash! Got response: {response.text}")
        return True
    except Exception as e:
        logger.error(f"❌ API key doesn't work with gemini-2.0-flash: {str(e)}")
        return False

def get_available_models(api_key):
    """Get a list of available models for this API key"""
    try:
        genai.configure(api_key=api_key)
        models = genai.list_models()
        logger.info("Available models:")
        for model in models:
            logger.info(f"  - {model.name}")
        return models
    except Exception as e:
        logger.error(f"❌ Error listing models: {str(e)}")
        return []

def main():
    """Main function"""
    logger.info("Gemini API Key Checker")
    logger.info("=====================")
    
    # Print environment information
    print_env_info()
    
    # Get API key from environment
    api_key = os.environ.get("GEMINI_KEY")  # Try GEMINI_KEY instead
    if not api_key:
        logger.error("GEMINI_KEY environment variable is not set")
        return 1
    
    # Test with the environment API key
    valid = test_api_key(api_key)
    
    # If valid, try testing with gemini-2.0-flash
    if valid:
        valid_2_0 = test_api_key_with_2_0(api_key)
        
        # If not valid with 2.0, list available models
        if not valid_2_0:
            logger.info("Checking available models for this API key...")
            get_available_models(api_key)
    
    return 0 if valid else 1

if __name__ == "__main__":
    sys.exit(main())
