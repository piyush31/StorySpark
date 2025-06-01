#!/usr/bin/env python3
"""
Test script to verify that Google TTS API key authentication works properly.
"""
import os
import sys
import logging
from google.cloud import texttospeech

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Test Google Cloud TTS with API key authentication"""
    # Check for API key - use Gemini key for TTS as well
    tts_api_key = os.environ.get("GEMINI_KEY")
    if not tts_api_key:
        logger.error("GEMINI_KEY environment variable not found")
        logger.info("Please set the GEMINI_KEY environment variable with your Google Cloud API key")
        logger.info("Example: export GEMINI_KEY=your-api-key-here")
        return 1
    
    logger.info(f"Using GEMINI_KEY with length: {len(tts_api_key)}")
    
    try:
        # Initialize client with API key
        client = texttospeech.TextToSpeechClient(
            client_options={"api_key": tts_api_key}
        )
        
        # Set the text input to be synthesized
        synthesis_input = texttospeech.SynthesisInput(text="Hello, this is a test of the Chirp HD voice model.")
        
        # Build the voice request
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name="en-US-Chirp-3-HD-Charon",
            ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
        )
        
        # Select the type of audio file
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )
        
        # Perform the text-to-speech request
        logger.info("Sending request to Google Cloud TTS API...")
        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )
        
        # The response's audio_content is binary
        if hasattr(response, 'audio_content'):
            # Write the response to an output file
            output_file = "test_tts_output.mp3"
            with open(output_file, "wb") as out:
                out.write(response.audio_content)
            
            logger.info(f"Audio content written to: {output_file}")
            logger.info(f"Success! Generated audio file with size: {len(response.audio_content)} bytes")
            return 0
        else:
            logger.error(f"Error: Response has no audio_content attribute: {response}")
            return 1
        
    except Exception as e:
        logger.error(f"Error testing Google Cloud TTS: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
