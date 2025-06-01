#!/bin/bash
# Script to set up the API keys and test the story generation and TTS

# Make sure all test scripts are executable
chmod +x test_story_generation.py
chmod +x test_gemini_direct.py
chmod +x test_tts_api_key.py

# Define the API key - use one key for all services
export GEMINI_KEY="your-api-key-here"

echo "===== Testing Gemini API for story generation ====="
./test_gemini_direct.py

echo "===== Testing Google TTS API with Gemini API key ====="
./test_tts_api_key.py

echo "===== Testing Story Generator ====="
./test_story_generation.py

echo "All tests completed!"
