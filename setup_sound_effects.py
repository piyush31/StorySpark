#!/usr/bin/env python3
"""
Script to set up placeholder sound effects for StorySpark development
This script creates dummy sound effect files for development
"""
import os
import time
import sys
import argparse
import shutil

# Define the effects directory
EFFECTS_DIR = os.path.join(os.path.dirname(__file__), "backend/static/effects")
PLACEHOLDERS_DIR = os.path.join(os.path.dirname(__file__), "backend/static/placeholders")

# Ensure the directories exist
os.makedirs(EFFECTS_DIR, exist_ok=True)
os.makedirs(PLACEHOLDERS_DIR, exist_ok=True)

# Define sound effects
SOUND_EFFECTS = [
    # Basic effects
    "forest", "rain", "magic", "door", "animal", "river", "wind",
    # Additional effects
    "footsteps", "laughter", "thunder", "cricket", "birds", 
    "heartbeat", "chimes", "ocean", "crowd", "fire"
]

def create_dummy_audio_file(path):
    """Create a dummy MP3 file for development purposes."""
    # This creates an empty file with minimal MP3 header, sufficient for development
    with open(path, 'wb') as f:
        # Write minimal MP3 header (not a valid MP3, but works for testing)
        f.write(b'\xFF\xFB\x90\x44\x00\x00\x00\x00')
    
    print(f"Created dummy file: {path}")

def create_story_audio_placeholder(path):
    """Create a placeholder for story audio"""
    # Create a larger dummy file
    with open(path, 'wb') as f:
        # Write minimal MP3 header followed by some null bytes
        f.write(b'\xFF\xFB\x90\x44\x00\x00\x00\x00')
        # Add some data to make it larger (1KB)
        f.write(b'\x00' * 1024)
    
    print(f"Created story audio placeholder: {path}")

def main():
    """Main function to create sound effects"""
    parser = argparse.ArgumentParser(description='Setup sound effects for StorySpark')
    parser.add_argument('--force', action='store_true', help='Force recreate all sound effects')
    args = parser.parse_args()
    
    print(f"Setting up sound effects in {EFFECTS_DIR}")
    
    # Create placeholder story audio
    placeholder_path = os.path.join(PLACEHOLDERS_DIR, "story_audio.mp3")
    if args.force or not os.path.exists(placeholder_path):
        create_story_audio_placeholder(placeholder_path)
    else:
        print(f"Skipping story audio placeholder, file already exists")
    
    # Create sound effects
    success_count = 0
    for effect_name in SOUND_EFFECTS:
        output_path = os.path.join(EFFECTS_DIR, f"{effect_name}.mp3")
        
        # If file already exists and not force mode, skip
        if os.path.exists(output_path) and not args.force:
            print(f"Skipping {effect_name}, file already exists")
            success_count += 1
            continue
        
        try:
            print(f"Creating {effect_name} sound effect...")
            create_dummy_audio_file(output_path)
            success_count += 1
            
            # Sleep briefly to avoid resource contention
            time.sleep(0.1)
            
        except Exception as e:
            print(f"Error processing {effect_name}: {str(e)}")
    
    print(f"\nCompleted: {success_count}/{len(SOUND_EFFECTS)} effects processed")
    return 0 if success_count == len(SOUND_EFFECTS) else 1

if __name__ == "__main__":
    sys.exit(main())
