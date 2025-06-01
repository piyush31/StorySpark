"""
Voice Service Module for StorySpark

This module provides the interface for text-to-speech and sound effect generation
used in StorySpark storytelling features.
"""
import os
import logging
import time
import tempfile
import json
import hashlib
from typing import Dict, List, Union, Optional, Literal
from google.cloud import texttospeech

# Import local audio processor
from .audio_processor import combine_audio_files, apply_fade_effect

# Configure logging
logger = logging.getLogger(__name__)

# Define sound item types
SoundType = Literal["human", "effect"]
EmotionType = Literal["neutral", "happy", "sad", "excited", "calm", "scared", "mysterious"]

class SoundItem:
    """Represents a single sound item in a story sequence"""
    
    def __init__(
        self,
        sound_type: SoundType,
        content: str,
        emotion: Optional[EmotionType] = "neutral",
        pause_after: float = 0.0,
        volume: float = 1.0
    ):
        """
        Initialize a sound item
        
        Args:
            sound_type: Either "human" (for spoken text) or "effect" (for sound effects)
            content: Text to speak or name of sound effect to play
            emotion: The emotional tone for voice synthesis (only for human type)
            pause_after: Seconds to pause after this sound item plays
            volume: Volume level from 0.0 to 1.0
        """
        self.sound_type = sound_type
        self.content = content
        self.emotion = emotion if sound_type == "human" else None
        self.pause_after = pause_after
        self.volume = max(0.0, min(1.0, volume))  # Clamp volume between 0 and 1
    
    def to_dict(self) -> Dict:
        """Convert to dictionary representation"""
        return {
            "sound_type": self.sound_type,
            "content": self.content,
            "emotion": self.emotion,
            "pause_after": self.pause_after,
            "volume": self.volume
        }


class VoiceService:
    """
    Service for text-to-speech conversion and sound effect management
    """
    
    def __init__(self):
        """
        Initialize the voice service
        """
        # Use the same API key as Gemini for TTS
        self.tts_api_key = os.environ.get("GEMINI_KEY")
        
        self.available_voices = self._load_available_voices()
        self.sound_effects = self._load_sound_effects()
        self.tts_client = None
        
        # Try to initialize TTS client with API key
        try:
            if self.tts_api_key:
                self.tts_client = texttospeech.TextToSpeechClient(
                    client_options={"api_key": self.tts_api_key}
                )
                logger.info("Google Cloud TTS client initialized successfully with Gemini API key")
            else:
                logger.warning("GEMINI_KEY environment variable not found, TTS functionality will be limited")
        except Exception as e:
            logger.error(f"Failed to initialize Google Cloud TTS client: {str(e)}")
    
    def _load_available_voices(self) -> List[Dict]:
        """
        Load available voice profiles
        
        Returns:
            List of voice profile dictionaries
        """
        voices = [
            {
                "id": "dadi",
                "name": "Dadi Maa",
                "gender": "female",
                "age": "elderly",
                "language": "en-US",
                "google_voice": "en-US-Chirp3-HD-Charon",
                "speaking_rate": 0.85
            },
            {
                "id": "default",
                "name": "Storyteller",
                "gender": "female",
                "age": "middle",
                "language": "en-US",
                "google_voice": "en-US-Chirp3-HD-Charon",
                "speaking_rate": 1.0
            }
        ]
        
        logger.info(f"Loaded {len(voices)} voice profiles")
        return voices
    
    def _load_sound_effects(self) -> Dict[str, str]:
        """
        Load available sound effects
        
        Returns:
            Dictionary mapping effect names to file paths
        """
        effects_dir = os.path.join(os.path.dirname(__file__), '../../static/effects')
        os.makedirs(effects_dir, exist_ok=True)
        
        effects = {
            "forest": os.path.join(effects_dir, "forest.mp3"),
            "rain": os.path.join(effects_dir, "rain.mp3"),
            "magic": os.path.join(effects_dir, "magic.mp3"),
            "door": os.path.join(effects_dir, "door.mp3"),
            "animal": os.path.join(effects_dir, "animal.mp3"),
            "river": os.path.join(effects_dir, "river.mp3"),
            "wind": os.path.join(effects_dir, "wind.mp3")
        }
        
        logger.info(f"Loaded {len(effects)} sound effects")
        return effects
    
    def text_to_speech(
        self, 
        text: str, 
        voice_id: str = "default",
        emotion: EmotionType = "neutral"
    ) -> str:
        """
        Convert text to speech audio file using Google Cloud TTS
        
        Args:
            text: The text to convert to speech
            voice_id: ID of the voice profile to use
            emotion: Emotional tone for the speech
            
        Returns:
            Path to the generated audio file
        """
        logger.info(f"Converting text to speech: '{text[:30]}...' with voice {voice_id} and emotion {emotion}")
        
        # Get voice profile
        voice_profile = next((v for v in self.available_voices if v["id"] == voice_id), None)
        if not voice_profile:
            logger.warning(f"Voice ID {voice_id} not found, using default")
            voice_profile = next((v for v in self.available_voices if v["id"] == "default"), 
                                self.available_voices[0])
        
        # Create output directory if it doesn't exist
        output_dir = os.path.join(os.path.dirname(__file__), '../../static/generated')
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate a unique filename based on the content and voice
        filename = f"speech_{voice_id}_{emotion}_{hashlib.md5(text.encode()).hexdigest()[:10]}.mp3"
        output_path = os.path.join(output_dir, filename)
        relative_path = f"/static/generated/{filename}"
        
        # Check if the file already exists (caching)
        if os.path.exists(output_path):
            logger.info(f"Using cached audio file: {output_path}")
            return relative_path
            
        # If Google Cloud TTS client is available, use it
        if self.tts_client:
            try:
                # Set the text input to be synthesized
                synthesis_input = texttospeech.SynthesisInput(text=text)
                
                # Build the voice request
                voice = texttospeech.VoiceSelectionParams(
                    language_code=voice_profile["language"],
                    name=voice_profile["google_voice"],
                    ssml_gender=texttospeech.SsmlVoiceGender.FEMALE if voice_profile["gender"] == "female" 
                               else texttospeech.SsmlVoiceGender.MALE
                )
                
                # Select the type of audio file
                audio_config = texttospeech.AudioConfig(
                    audio_encoding=texttospeech.AudioEncoding.MP3,
                    speaking_rate=voice_profile.get("speaking_rate", 1.0)
                )
                
                # Perform the text-to-speech request
                response = self.tts_client.synthesize_speech(
                    input=synthesis_input,
                    voice=voice,
                    audio_config=audio_config
                )
                
                # Write the response to the output file
                with open(output_path, "wb") as out:
                    out.write(response.audio_content)
                
                logger.info(f"Audio content written to: {output_path}")
                return relative_path
                
            except Exception as e:
                logger.error(f"Error with Google Cloud TTS: {str(e)}")
        
        # Fallback to mock audio file if TTS fails
        logger.warning("Using fallback audio file")
        return "/static/placeholders/story_audio.mp3"
    
    def process_sound_sequence(self, sound_sequence: List[SoundItem]) -> str:
        """
        Process a sequence of sound items into a single audio file
        
        Args:
            sound_sequence: List of SoundItem objects
            
        Returns:
            Path to the generated audio file
        """
        if not sound_sequence:
            logger.warning("Empty sound sequence provided")
            return "/static/placeholders/story_audio.mp3"
        
        # Collect all human speech items and combine them into complete story text
        speech_parts = []
        for item in sound_sequence:
            if item.sound_type == "human":
                speech_parts.append(item.content)
        
        if not speech_parts:
            logger.warning("No human speech found in sequence, using fallback")
            return "/static/placeholders/story_audio.mp3"
        
        # Combine all speech parts into a single narrative
        # Add natural pauses between sentences/paragraphs
        combined_text = ""
        for i, part in enumerate(speech_parts):
            combined_text += part
            # Add pause between segments (except the last one)
            if i < len(speech_parts) - 1:
                combined_text += "... "  # Natural pause in speech
        
        logger.info(f"Processing complete story audio with {len(speech_parts)} speech segments, total length: {len(combined_text)} characters")
        
        # Convert the complete story text to speech
        return self.text_to_speech(
            text=combined_text,
            voice_id="default",
            emotion="neutral"  # Use neutral for the overall story, could be enhanced to detect dominant emotion
        )


# Create a singleton instance
voice_service = VoiceService()
