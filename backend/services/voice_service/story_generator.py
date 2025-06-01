"""
Story Generation Service for StorySpark

This module handles the generation and narration of stories,
utilizing the voice service for audio output.
"""
import logging
import os
import time
import json
import google.generativeai as genai
from typing import Dict, List, Optional, Any, Union
from .voice_service import voice_service, SoundItem

# Configure logging
logger = logging.getLogger(__name__)

# Set up Gemini API
GEMINI_API_KEY = os.environ.get("GEMINI_KEY")  # Use GEMINI_KEY instead of GEMINI_API_KEY
if not GEMINI_API_KEY:
    logger.error("GEMINI_KEY not found in environment variables")
    logger.info("Environment variables available: " + ", ".join([k for k in os.environ.keys() if not k.startswith("_")]))
else:
    logger.info(f"GEMINI_KEY found with length: {len(GEMINI_API_KEY)}")
    
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    logger.info("Gemini API configured successfully")
else:
    logger.warning("Skipping Gemini API configuration due to missing API key")

class StoryGenerator:
    """
    Service for generating and narrating stories
    """
    
    def __init__(self):
        """Initialize the story generator"""
        self.voice_service = voice_service
        self.gemini_model = None
        self.setup_gemini_model()
    
    def setup_gemini_model(self):
        """Set up the Gemini model for story generation"""
        try:
            # Check if API key is available
            if not GEMINI_API_KEY:
                logger.error("GEMINI_API_KEY not found in environment variables")
                self.gemini_model = None
                return
                
            # Initialize Gemini model - using the flash model for faster responses
            self.gemini_model = genai.GenerativeModel('gemini-2.0-flash')
            
            # Test the model with a simple prompt to verify it works
            test_response = self.gemini_model.generate_content("Hello")
            if test_response and hasattr(test_response, 'text'):
                logger.info("Gemini model initialized and tested successfully")
            else:
                logger.error("Gemini model initialization failed: Test response invalid")
                self.gemini_model = None
        except Exception as e:
            logger.error(f"Failed to initialize Gemini model: {str(e)}")
            self.gemini_model = None
    
    def generate_story(
        self, 
        theme: Optional[str] = None,
        characters: Optional[List[str]] = None,
        setting: Optional[str] = None,
        duration: str = "medium",
        age_group: str = "5-8",
        language: str = "en",
        child_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a new story based on given parameters
        
        Args:
            theme: Theme or moral of the story (e.g., "kindness", "courage")
            characters: List of character types or names to include
            setting: Setting for the story (e.g., "forest", "space")
            duration: Length of the story ("short", "medium", "long")
            age_group: Target age group (e.g., "3-5", "5-8", "8-12")
            language: Primary language code
            child_name: Name of the child for personalization
            
        Returns:
            Dictionary containing story data including title, text, and audio
        """
        logger.info(f"Generating {duration} story with theme '{theme}' for age {age_group}")
        
        # Convert duration to minutes for the prompt
        duration_minutes = {"short": "3-5", "medium": "5-10", "long": "10-15"}.get(duration, "5-10")
        
        # Build the prompt for the Gemini model
        prompt = self._build_story_prompt(
            theme=theme, 
            characters=characters,
            setting=setting,
            duration_minutes=duration_minutes,
            age_group=age_group,
            language=language,
            child_name=child_name
        )
        
        try:
            # Generate story using Gemini
            if self.gemini_model:
                logger.info(f"Sending prompt to Gemini: {prompt[:100]}...")
                story_response = self.gemini_model.generate_content(prompt)
                story_content = story_response.text
                logger.info(f"Received response from Gemini: {len(story_content)} characters")
                
                # Extract title and text from the generated content
                story_title, story_text = self._parse_story_content(story_content, theme, setting)
                logger.info(f"Parsed story title: {story_title}")
            else:
                # Fallback if model isn't available
                logger.warning("Gemini model not available, using fallback story generation")
                story_title = f"The Adventure in the {setting or 'Magical Land'}"
                story_text = self._generate_fallback_story(theme, setting, child_name, age_group)
                
                # Log the fallback story
                logger.info(f"Generated fallback story with title: {story_title} and text: {story_text[:100]}...")
        except Exception as e:
            logger.error(f"Error generating story with Gemini: {str(e)}")
            # Fallback story if generation fails
            story_title = f"The Adventure in the {setting or 'Magical Land'}"
            story_text = self._generate_fallback_story(theme, setting, child_name, age_group)
        
        # Convert story text to structured sound sequence
        sound_sequence = self._create_sound_sequence(story_text, story_title)
        
        # Process the sound sequence to create audio
        audio_path = self.voice_service.process_sound_sequence(sound_sequence)
        
        # Create unique ID for the story
        story_id = int(time.time() * 1000)
        
        # Create the story data structure
        story_data = {
            "id": story_id,
            "title": story_title,
            "text": story_text,
            "audio_path": audio_path,
            "duration": self._estimate_duration(sound_sequence),
            "theme": theme,
            "age_group": age_group,
            "language": language,
            "created_by": child_name,
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "is_downloadable": True
        }
        
        return story_data
    
    def _create_sound_sequence(
        self, 
        story_text: str, 
        story_title: str
    ) -> List[SoundItem]:
        """
        Convert story text into a sequence of sound items
        
        Args:
            story_text: The full text of the story
            story_title: The title of the story
            
        Returns:
            List of SoundItem objects defining the audio sequence
        """
        # Start with an opening sound effect
        sound_sequence = [
            SoundItem(
                sound_type="effect",
                content="magic",
                pause_after=0.5,
                volume=0.7
            )
        ]
        
        # Add the title narration
        sound_sequence.append(
            SoundItem(
                sound_type="human",
                content=f"The story of {story_title}",
                emotion="excited",
                pause_after=1.0
            )
        )
        
        # Split story into paragraphs for better pacing and appropriate emotions
        paragraphs = story_text.split('\n\n')
        
        # Process each paragraph
        for i, paragraph in enumerate(paragraphs):
            if not paragraph.strip():
                continue
                
            # Determine appropriate emotion based on content keywords
            emotion = self._detect_emotion(paragraph)
            
            # Add paragraph narration
            sound_sequence.append(
                SoundItem(
                    sound_type="human",
                    content=paragraph.strip(),
                    emotion=emotion,
                    pause_after=0.8 if i < len(paragraphs) - 1 else 0.5
                )
            )
            
            # Add relevant sound effect after some paragraphs
            if i < len(paragraphs) - 1 and i % 3 == 0 and len(paragraphs) > 3:
                effect = self._determine_sound_effect(paragraph)
                if effect:
                    sound_sequence.append(
                        SoundItem(
                            sound_type="effect",
                            content=effect,
                            pause_after=0.5,
                            volume=0.5
                        )
                    )
        
        # Add a closing sound effect
        sound_sequence.append(
            SoundItem(
                sound_type="effect",
                content="magic",
                pause_after=0.0,
                volume=0.5
            )
        )
        
        return sound_sequence
    
    def _detect_emotion(self, text: str) -> str:
        """
        Detect appropriate emotion for narrating a paragraph
        
        Args:
            text: Paragraph text
            
        Returns:
            Emotion name
        """
        text = text.lower()
        
        # Simple keyword-based detection
        if any(word in text for word in ['happy', 'joy', 'laugh', 'smile', 'dance', 'celebrate']):
            return 'happy'
        elif any(word in text for word in ['scared', 'fear', 'afraid', 'terrified', 'horror']):
            return 'scared'
        elif any(word in text for word in ['sad', 'cry', 'tear', 'sorrow', 'unhappy']):
            return 'sad'
        elif any(word in text for word in ['wow', 'amazing', 'wonder', 'incredible', 'magic']):
            return 'excited'
        elif any(word in text for word in ['calm', 'peace', 'quiet', 'gentle', 'soft']):
            return 'calm'
        elif any(word in text for word in ['secret', 'mystery', 'hidden', 'unknown']):
            return 'mysterious'
        else:
            return 'neutral'
    
    def _determine_sound_effect(self, text: str) -> Optional[str]:
        """
        Determine an appropriate sound effect for a paragraph
        
        Args:
            text: Paragraph text
            
        Returns:
            Sound effect name or None
        """
        text = text.lower()
        
        # Map keywords to sound effects
        if any(word in text for word in ['forest', 'tree', 'wood', 'jungle']):
            return 'forest'
        elif any(word in text for word in ['rain', 'storm', 'thunder', 'water']):
            return 'rain'
        elif any(word in text for word in ['magic', 'spell', 'wizard', 'fairy']):
            return 'magic'
        elif any(word in text for word in ['door', 'knock', 'enter', 'house']):
            return 'door'
        elif any(word in text for word in ['animal', 'dog', 'cat', 'bird']):
            return 'animal'
        
        return None
    
    def _estimate_duration(self, sound_sequence: List[SoundItem]) -> str:
        """
        Estimate the duration of a sound sequence
        
        Args:
            sound_sequence: List of SoundItem objects
            
        Returns:
            String describing the approximate duration (e.g., "5 minutes")
        """
        # Calculate the actual duration based on text length, pauses, and effects
        total_chars = sum(len(item.content) for item in sound_sequence if item.sound_type == "human")
        total_pauses = sum(item.pause_after for item in sound_sequence)
        total_effects = sum(1 for item in sound_sequence if item.sound_type == "effect")
        
        # Rough estimate: 15 characters per second for speech
        speech_seconds = total_chars / 15
        effects_seconds = total_effects * 3  # Assume average 3 seconds per effect
        total_seconds = speech_seconds + total_pauses + effects_seconds
        
        minutes = int(total_seconds / 60)
        
        if minutes < 5:
            return "3 minutes"
        elif minutes < 10:
            return "5 minutes"
        elif minutes < 15:
            return "10 minutes"
        else:
            return "15+ minutes"
        
    def narrate_existing_story(self, story_id: Union[int, str]) -> Dict[str, Any]:
        """
        Generate narration for an existing story
        
        Args:
            story_id: ID of the story to narrate
            
        Returns:
            Dictionary with narration data including audio path
            
        Raises:
            ValueError: If story_id is not found
        """
        logger.info(f"Generating narration for story ID {story_id}")
        
        # In a real implementation, this would:
        # 1. Fetch the story from a database
        # 2. Process the text into a sound sequence
        # 3. Generate the audio file
        
        # Return mock narration data
        return {
            "story_id": story_id,
            "audio_path": f"generated/narration_{story_id}.mp3",
            "duration": "5 minutes",
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
    
    def _build_story_prompt(
        self,
        theme: Optional[str] = None,
        characters: Optional[List[str]] = None,
        setting: Optional[str] = None,
        duration_minutes: str = "5-10",
        age_group: str = "5-8",
        language: str = "en",
        child_name: Optional[str] = None
    ) -> str:
        """
        Build a prompt for the Gemini model to generate a story
        
        Args:
            theme: Theme or moral of the story
            characters: List of character types or names to include
            setting: Setting for the story
            duration_minutes: Target duration in minutes
            age_group: Target age group
            language: Primary language code
            child_name: Name of the child for personalization
            
        Returns:
            Formatted prompt string
        """
        # Base prompt
        prompt = f"""Write a children's story for age group {age_group} years that would take about {duration_minutes} minutes to read aloud.
        """
        
        # Add theme if provided
        if theme:
            prompt += f"The story should be about {theme} and teach the value of {theme}. "
        
        # Add setting if provided
        if setting:
            prompt += f"The story should take place in a {setting}. "
        
        # Add characters if provided
        if characters and len(characters) > 0:
            chars_str = ', '.join(characters)
            prompt += f"Include these characters: {chars_str}. "
        
        # Add child name for personalization if provided
        if child_name:
            prompt += f"Make {child_name} the main character or mention {child_name} in the story. "
        
        # Add formatting instructions
        prompt += """
        Make the story engaging, age-appropriate, and with a clear beginning, middle, and end.
        Use simple language that children can understand.
        Divide the story into paragraphs for better readability.
        Start with a title on the first line prefixed with "Title: ".
        
        The story should convey positive values and end with a meaningful lesson.
        """
        
        return prompt
    
    def _parse_story_content(self, content: str, theme: Optional[str] = None, setting: Optional[str] = None) -> tuple:
        """
        Parse the generated content into title and story text
        
        Args:
            content: Raw content from Gemini
            theme: Theme of the story (for fallback title)
            setting: Setting of the story (for fallback title)
            
        Returns:
            Tuple of (title, story_text)
        """
        # Default fallback values
        default_title = f"The Adventure of {theme or 'Kindness'}"
        if setting:
            default_title += f" in the {setting}"
            
        try:
            # Check if content starts with "Title: " format
            if "Title:" in content and content.index("Title:") < 20:
                parts = content.split("\n", 1)
                title = parts[0].replace("Title:", "").strip()
                story_text = parts[1].strip() if len(parts) > 1 else ""
            else:
                # Try to find a logical title from the first line
                lines = content.split("\n")
                if len(lines[0]) < 100 and not lines[0].startswith("Once upon"):
                    title = lines[0].strip()
                    story_text = "\n".join(lines[1:]).strip()
                else:
                    # Couldn't find a clear title
                    title = default_title
                    story_text = content
                    
            # If either is empty, use defaults
            if not title:
                title = default_title
            if not story_text:
                story_text = f"Once upon a time, in a {setting or 'magical land'}, there lived..."
                
            return title, story_text
            
        except Exception as e:
            logger.error(f"Error parsing story content: {str(e)}")
            return default_title, content
    
    def _generate_fallback_story(self, theme=None, setting=None, child_name=None, age_group="5-8"):
        """
        Generate a fallback story when the AI generation fails
        
        Args:
            theme: Theme of the story
            setting: Setting of the story
            child_name: Name of the child for personalization
            age_group: Target age group
            
        Returns:
            A placeholder story text
        """
        theme = theme or "kindness"
        setting = setting or "magical forest"
        
        # Create different stories based on age group
        if age_group == "3-5":
            # Simpler story for younger children
            if child_name:
                return f"""Once upon a time, there was a child named {child_name} who lived near a {setting}.
                
{child_name} was kind and helpful to everyone.

One day, {child_name} found a little bird with a broken wing.

{child_name} gently picked up the bird and took care of it until it was better.

The bird was so happy that it sang a beautiful song just for {child_name}.

And that's how {child_name} learned that {theme} makes everyone happy.

The end."""
            else:
                return f"""Once upon a time, in a beautiful {setting}, there lived a little rabbit.
                
The rabbit was very good at showing {theme}.

Every day, the rabbit helped all the animals in the {setting}.

Everyone loved the rabbit because it was so kind.

And they all lived happily ever after."""
                
        elif age_group == "8-12":
            # More complex story for older children
            if child_name:
                return f"""In the heart of the {setting}, there lived a brave child named {child_name}.
                
{child_name} was known throughout the land for their incredible sense of {theme}.

One stormy night, the wise elder of the {setting} came to {child_name} with an important mission.

"Only someone with true {theme} in their heart can save our home," the elder explained.

{child_name} embarked on a journey across the {setting}, facing challenges that tested their courage and determination.

Along the way, {child_name} helped many creatures, showing that {theme} was more powerful than any magic.

When {child_name} finally reached the ancient tree at the center of the {setting}, they discovered that the journey itself was the solution.

The {setting} began to heal because {child_name} had spread {theme} to every corner during their travels.

"Remember," said the elder, "true {theme} can change the world in ways we never imagine."

And from that day forward, the {setting} flourished as never before, all because of {child_name}'s {theme}."""
            else:
                return f"""In the ancient {setting}, a legend spoke of a power greater than any magic - the power of {theme}.
                
For centuries, the inhabitants had forgotten this power, chasing instead after temporary solutions to their problems.

Then one day, a mysterious visitor arrived, demonstrating {theme} in everything they did.

Small acts of {theme} began to change the {setting}, first slowly, then with gathering momentum.

The streams ran clearer, the trees grew taller, and the animals lived in harmony.

The elders of the {setting} realized that {theme} was the missing element that could heal their world.

They established a festival of {theme} that continues to this day, reminding everyone that the greatest power lies not in magic or strength, but in how we treat one another."""
        else:
            # Default story for middle age group (5-8)
            if child_name:
                return f"""Once upon a time, there was a child named {child_name} who lived near a {setting}.
                
{child_name} was known for their {theme}. Every day, {child_name} would help the animals in the forest.

One day, {child_name} met a wise old owl who said, "Your {theme} is a gift. Use it wisely."

{child_name} learned that being {theme} made everyone happy, including themselves.

And they all lived happily ever after."""
            else:
                return f"""Once upon a time, in a beautiful {setting}, there lived many creatures who learned about {theme}.

They discovered that {theme} made their lives better in many ways.

The wise old owl taught everyone that {theme} was the most important value of all.

And from that day forward, {theme} filled the {setting} with joy and happiness.

The end."""

# Create an instance of the StoryGenerator class
story_generator = StoryGenerator()
