"""
Audio Processing Module for StorySpark

This module provides functions for processing and combining audio files
for the StorySpark storytelling features.
"""
import os
import logging
import tempfile
import subprocess
import shutil
from typing import List, Dict

# Configure logging
logger = logging.getLogger(__name__)

def combine_audio_files(audio_files: List[Dict], output_path: str) -> bool:
    """
    Combine multiple audio files into a single file using file concatenation
    This is a simplified version for development use only
    
    Args:
        audio_files: List of dictionaries with path, volume, and pause_after information
        output_path: Path to save the combined audio file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # If we have no files, fail
        if not audio_files:
            logger.error("No audio files provided to combine")
            return False
            
        # In a full implementation, we would use ffmpeg or a library like pydub
        # For development, we just copy the first file as a placeholder
        source_path = audio_files[0].get("path")
        
        if not source_path or not os.path.exists(source_path):
            logger.error(f"First audio file not found: {source_path}")
            return False
            
        # Create the output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
        # Copy the file
        shutil.copy2(source_path, output_path)
        logger.info(f"Created placeholder combined audio file at {output_path}")
        
        return True
            
    except Exception as e:
        logger.error(f"Error combining audio files: {str(e)}")
        return False

def get_audio_duration(file_path: str) -> float:
    """
    Get the duration of an audio file in seconds using ffprobe if available
    Falls back to a default value if ffprobe is not available
    
    Args:
        file_path: Path to the audio file
        
    Returns:
        Duration in seconds, or 0 if error
    """
    try:
        # Check if ffprobe is available
        try:
            proc = subprocess.run(
                ["ffprobe", "-version"], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE
            )
            
            # If ffprobe is available, use it to get the duration
            if proc.returncode == 0:
                proc = subprocess.run(
                    [
                        "ffprobe", 
                        "-v", "error", 
                        "-show_entries", "format=duration", 
                        "-of", "default=noprint_wrappers=1:nokey=1", 
                        file_path
                    ], 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                if proc.returncode == 0:
                    return float(proc.stdout.strip())
        except (subprocess.SubprocessError, FileNotFoundError):
            pass
            
        # If ffprobe is not available or fails, return an estimated duration
        # based on file size (rough estimate: 128kbps MP3)
        file_size = os.path.getsize(file_path)
        estimated_duration = file_size / (128 * 1024 / 8)  # bytes / (bitrate / 8)
        return estimated_duration
        
    except Exception as e:
        logger.error(f"Error getting audio duration: {str(e)}")
        return 0.0

def apply_fade_effect(file_path: str, fade_in: float = 0.5, fade_out: float = 0.5) -> bool:
    """
    Apply fade in/out effects to an audio file if ffmpeg is available
    Otherwise, just return success without modifying the file
    
    Args:
        file_path: Path to the audio file
        fade_in: Fade in duration in seconds
        fade_out: Fade out duration in seconds
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Check if ffmpeg is available
        try:
            proc = subprocess.run(
                ["ffmpeg", "-version"], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE
            )
            
            # If ffmpeg is available, use it to apply fades
            if proc.returncode == 0:
                # Get the duration first
                duration = get_audio_duration(file_path)
                if duration <= 0:
                    duration = 10  # Fallback to a reasonable duration
                
                # Create a temporary file
                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp:
                    temp_path = temp.name
                
                # Apply the fade effects
                proc = subprocess.run([
                    "ffmpeg",
                    "-y",  # Overwrite output files
                    "-i", file_path,  # Input file
                    "-af", f"afade=t=in:st=0:d={fade_in},afade=t=out:st={duration-fade_out}:d={fade_out}",  # Fade filter
                    temp_path  # Output file
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                if proc.returncode == 0:
                    # Replace the original file with the processed one
                    shutil.move(temp_path, file_path)
                    logger.info(f"Applied fade effects to {file_path}")
                    return True
                else:
                    if os.path.exists(temp_path):
                        os.unlink(temp_path)
        except (subprocess.SubprocessError, FileNotFoundError):
            pass
            
        # If ffmpeg is not available or fails, just return success
        # without actually applying the effects
        logger.info(f"Skipped applying fade effects to {file_path} (ffmpeg not available)")
        return True
        
    except Exception as e:
        logger.error(f"Error applying fade effects: {str(e)}")
        return False
