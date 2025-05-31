#!/usr/bin/env python3
"""
Test script for audio processing in StorySpark

This script tests the audio processing features of StorySpark,
particularly the combination of multiple audio clips.
"""
import os
import sys
import logging
import tempfile
import shutil
from pathlib import Path

# Add parent directory to path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from backend.services.voice_service.audio_processor import combine_audio_files, get_audio_duration, apply_fade_effect

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_test_files():
    """Create test audio files for the test"""
    # Create a temp directory for test files
    temp_dir = tempfile.mkdtemp()
    logger.info(f"Created temp directory: {temp_dir}")
    
    # We'll use the actual effects from our app for testing
    effects_dir = os.path.join(os.path.dirname(__file__), "backend/static/effects")
    
    # Make sure we have some effects
    if not os.path.exists(effects_dir) or len(os.listdir(effects_dir)) == 0:
        logger.error(f"No effects found in {effects_dir}. Please run setup_sound_effects.py first.")
        return None
    
    # Get the first few effect files
    effect_files = []
    for file in os.listdir(effects_dir):
        if file.endswith(".mp3"):
            effect_files.append(os.path.join(effects_dir, file))
            if len(effect_files) >= 3:
                break
    
    # If we don't have enough effects, abort
    if len(effect_files) < 3:
        logger.error(f"Not enough effect files found in {effects_dir}. Need at least 3.")
        return None
    
    return {
        "temp_dir": temp_dir,
        "effect_files": effect_files
    }

def run_audio_processing_test():
    """Test the audio processing functionality"""
    logger.info("Starting audio processing test")
    
    # Setup test files
    test_data = setup_test_files()
    if not test_data:
        return False
    
    temp_dir = test_data["temp_dir"]
    effect_files = test_data["effect_files"]
    
    # Test file paths
    output_path = os.path.join(temp_dir, "combined_output.mp3")
    
    # Create audio files list in the format expected by combine_audio_files
    audio_files = [
        {"path": effect_files[0], "volume": 1.0, "pause_after": 0.5},
        {"path": effect_files[1], "volume": 0.7, "pause_after": 0.3},
        {"path": effect_files[2], "volume": 0.9, "pause_after": 0.0}
    ]
    
    # Test combine_audio_files
    logger.info("Testing combine_audio_files")
    result = combine_audio_files(audio_files, output_path)
    
    if result and os.path.exists(output_path):
        logger.info(f"Successfully combined audio files to: {output_path}")
        
        # Test get_audio_duration
        logger.info("Testing get_audio_duration")
        duration = get_audio_duration(output_path)
        logger.info(f"Combined audio duration: {duration:.2f} seconds")
        
        # Test apply_fade_effect
        logger.info("Testing apply_fade_effect")
        fade_path = os.path.join(temp_dir, "fade_output.mp3")
        
        # Copy the file first
        shutil.copy(output_path, fade_path)
        
        fade_result = apply_fade_effect(fade_path, fade_in=0.3, fade_out=0.5)
        if fade_result and os.path.exists(fade_path):
            logger.info(f"Successfully applied fade effect to: {fade_path}")
            return True
        else:
            logger.error("Failed to apply fade effect")
    else:
        logger.error("Failed to combine audio files")
    
    return False

def main():
    """Main test runner"""
    success = run_audio_processing_test()
    
    if success:
        logger.info("All audio processing tests passed!")
        return 0
    else:
        logger.error("Some audio processing tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
