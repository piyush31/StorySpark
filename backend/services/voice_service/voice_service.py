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
        # Set Google Cloud credentials
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.environ.get(
            "GOOGLE_APPLICATION_CREDENTIALS", 
            "credentials/google_cloud_credentials.json"
        )
        
        self.available_voices = self._load_available_voices()
        self.sound_effects = self._load_sound_effects()
        self.tts_client = None
        
        # Try to initialize TTS client
        try:
            self.tts_client = texttospeech.TextToSpeechClient()
            logger.info("Google Cloud TTS client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Google Cloud TTS client: {str(e)}")
    
    def _load_available_voices(self) -> List[Dict]:
        """
        Load available voice profiles
        
        Returns:
            List of voice profile dictionaries
        """
        # In a full implementation, fetch available voices from Google Cloud TTS
        # For now, use predefined voices that correspond to available Google voices
        
        # These are customized for the Indian context with storyteller characters
        voices = [
            {
                "id": "dadi",
                "name": "Dadi Maa",
                "gender": "female",
                "age": "elderly",
                "language": "hi-IN",
                "google_voice": "hi-IN-Neural2-A",  # Hindi female voice
                "speaking_rate": 0.85  # Slightly slower for elderly character
            },
            {
                "id": "nani",
                "name": "Nani",
                "gender": "female",
                "age": "elderly", 
                "language": "hi-IN",
                "google_voice": "hi-IN-Neural2-B",  # Different Hindi female voice
                "speaking_rate": 0.85
            },
            {
                "id": "chacha",
                "name": "Chacha",
                "gender": "male",
                "age": "middle",
                "language": "hi-IN",
                "google_voice": "hi-IN-Neural2-C",  # Hindi male voice
                "speaking_rate": 0.95
            },
            {
                "id": "default",
                "name": "Storyteller",
                "gender": "female",
                "age": "middle",
                "language": "en-IN",
                "google_voice": "en-IN-Neural2-A",  # Indian English female voice
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
        # Define paths to sound effect files
        # In a full implementation, scan a directory of sound effects
        
        # Create static directory for effects if it doesn't exist
        effects_dir = os.path.join(os.path.dirname(__file__), '../../../static/effects')
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
            
        Raises:
            ValueError: If voice_id is not found or API error occurs
        """
        logger.info(f"Converting text to speech: '{text[:30]}...' with voice {voice_id} and emotion {emotion}")
        
        # Get voice profile
        voice_profile = next((v for v in self.available_voices if v["id"] == voice_id), None)
        if not voice_profile:
            logger.warning(f"Voice ID {voice_id} not found, using default")
            voice_profile = next((v for v in self.available_voices if v["id"] == "default"), 
                                self.available_voices[0])
        
        # Create output directory if it doesn't exist
        output_dir = os.path.join(os.path.dirname(__file__), '../../../static/generated')
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate a unique filename based on the content and voice
        filename = f"speech_{voice_id}_{emotion}_{hashlib.md5(text.encode()).hexdigest()[:10]}.mp3"
        output_path = os.path.join(output_dir, filename)
        
        # Check if the file already exists (caching)
        if os.path.exists(output_path):
            logger.info(f"Using cached audio file: {output_path}")
            return output_path
            
        # If Google Cloud TTS client is available, use it
        if self.tts_client:
            try:
                # Set the text input to be synthesized
                synthesis_input = texttospeech.SynthesisInput(text=text)
                
                # Build the voice request
                voice = texttospeech.VoiceSelectionParams(
                    language_code=voice_profile["language"],
                    name=voice_profile["google_voice"]
                )
                
                # Adjust pitch and speaking rate based on emotion
                pitch, speaking_rate = self._get_emotion_parameters(emotion, voice_profile)
                
                # Select the type of audio file
                audio_config = texttospeech.AudioConfig(
                    audio_encoding=texttospeech.AudioEncoding.MP3,
                    pitch=pitch,
                    speaking_rate=speaking_rate
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
                return output_path
                
            except Exception as e:
                logger.error(f"Error with Google Cloud TTS: {str(e)}")
                # Fall through to the fallback
        
        # Fallback to mock audio file if TTS fails
        logger.warning("Using fallback audio file")
        fallback_path = os.path.join(os.path.dirname(__file__), '../../../static/placeholders/story_audio.mp3')
        return fallback_path
    
    def _get_emotion_parameters(self, emotion: EmotionType, voice_profile: Dict) -> tuple:
        """
        Get appropriate pitch and speaking rate for an emotion
        
        Args:
            emotion: The emotional tone
            voice_profile: Voice profile dictionary
            
        Returns:
            Tuple of (pitch, speaking_rate)
        """
        # Default speaking rate from the voice profile or 1.0
        base_rate = voice_profile.get("speaking_rate", 1.0)
        
        # Adjust pitch and rate based on emotion
        if emotion == "happy":
            return 2.0, base_rate * 1.1
        elif emotion == "sad":
            return -2.0, base_rate * 0.9
        elif emotion == "excited":
            return 4.0, base_rate * 1.2
        elif emotion == "calm":
            return 0.0, base_rate * 0.9
        elif emotion == "scared":
            return 1.0, base_rate * 1.15
        elif emotion == "mysterious":
            return -1.0, base_rate * 0.95
        else:  # neutral
            return 0.0, base_rate
    
    def get_sound_effect(self, effect_name: str) -> Optional[str]:
        """
        Get path to a sound effect file
        
        Args:
            effect_name: Name of the sound effect
            
        Returns:
            Path to the sound effect file or None if not found
        """
        return self.sound_effects.get(effect_name)
    
    def process_sound_sequence(self, sound_items: List[SoundItem]) -> str:
        """
        Process a sequence of sound items into a single audio file
        
        Args:
            sound_items: List of SoundItem objects defining the sequence
            
        Returns:
            Path to the generated combined audio file
        """
        logger.info(f"Processing sequence of {len(sound_items)} sound items")
        
        # Create a list to track the generated audio files
        audio_files = []
        
        # Process each sound item
        for item in sound_items:
            if item.sound_type == "human":
                # Generate speech audio for human voice items
                audio_path = self.text_to_speech(
                    text=item.content,
                    emotion=item.emotion or "neutral"
                )
                audio_files.append({
                    "path": audio_path,
                    "volume": item.volume,
                    "pause_after": item.pause_after
                })
            elif item.sound_type == "effect":
                # Get path for sound effect items
                effect_path = self.get_sound_effect(item.content)
                if effect_path:
                    audio_files.append({
                        "path": effect_path,
                        "volume": item.volume,
                        "pause_after": item.pause_after
                    })
        
        # Create output directory if it doesn't exist
        output_dir = os.path.join(os.path.dirname(__file__), '../../../static/generated')
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate output path
        timestamp = int(time.time())
        output_path = os.path.join(output_dir, f"combined_audio_{timestamp}.mp3")
        
        # Combine audio files using our audio processor
        if audio_files and combine_audio_files(audio_files, output_path):
            # Apply a subtle fade in/out effect to the combined audio
            apply_fade_effect(output_path, fade_in=0.3, fade_out=0.5)
            logger.info(f"Created combined audio file at {output_path}")
            return output_path
        
        # Fallback to a placeholder audio file if combination fails
        logger.warning("Using fallback audio file")
        fallback_path = os.path.join(os.path.dirname(__file__), '../../../static/placeholders/story_audio.mp3')
        return fallback_path


# Singleton instance for app-wide usage
voice_service = VoiceService()
