"""Unit tests for the AI integration in the story generator.

This module tests the integration with Google's Gemini model for story generation.
"""

import unittest
import json
import os
import sys
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.voice_service.story_generator import StoryGenerator
from models.story import Story, StoryMetadata


class TestStoryGenerator(unittest.TestCase):
    """Test the StoryGenerator class and its integration with AI."""

    def setUp(self):
        """Set up the test environment."""
        self.story_generator = StoryGenerator()
        
        # Sample story request parameters
        self.story_params = {
            "theme": "Kindness",
            "age_group": "5-8",
            "duration": "medium",
            "child_name": "Aarav",
            "language": "en"
        }
        
        # Sample successful response from the AI model
        self.sample_ai_response = {
            "title": "Aarav's Act of Kindness",
            "content": "Once upon a time, there was a little boy named Aarav who lived in a small village...",
            "mood_markers": [
                {"emotion": "happy", "position": 10},
                {"emotion": "surprised", "position": 50},
                {"emotion": "thoughtful", "position": 80}
            ],
            "sound_effects": [
                {"effect": "birds", "position": 15},
                {"effect": "laughter", "position": 60}
            ]
        }

    @patch('services.voice_service.story_generator.GoogleGenerativeAI')
    def test_generate_story_content_success(self, mock_genai):
        """Test story generation content creation with successful AI response."""
        # Mock the AI service response
        mock_model = MagicMock()
        mock_genai.configure.return_value = None
        mock_genai.GenerativeModel.return_value = mock_model
        
        # Setup the mock response
        mock_response = MagicMock()
        mock_response.text = json.dumps(self.sample_ai_response)
        mock_model.generate_content.return_value = mock_response
        
        # Call the method under test
        result = self.story_generator.generate_story_content(self.story_params)
        
        # Verify results
        self.assertEqual(result["title"], self.sample_ai_response["title"])
        self.assertEqual(result["content"], self.sample_ai_response["content"])
        self.assertEqual(len(result["mood_markers"]), len(self.sample_ai_response["mood_markers"]))
        self.assertEqual(len(result["sound_effects"]), len(self.sample_ai_response["sound_effects"]))
        
        # Verify that the AI model was called with the correct prompt
        prompt_call = mock_model.generate_content.call_args[0][0]
        self.assertIn("Kindness", prompt_call)
        self.assertIn("Aarav", prompt_call)
        self.assertIn("5-8", prompt_call)
    
    @patch('services.voice_service.story_generator.GoogleGenerativeAI')
    def test_generate_story_content_error_handling(self, mock_genai):
        """Test error handling when AI service fails."""
        # Mock the AI service to raise an exception
        mock_model = MagicMock()
        mock_genai.configure.return_value = None
        mock_genai.GenerativeModel.return_value = mock_model
        mock_model.generate_content.side_effect = Exception("AI service error")
        
        # Call the method under test and verify it handles the error
        with self.assertRaises(Exception) as context:
            self.story_generator.generate_story_content(self.story_params)
        
        self.assertIn("Failed to generate story", str(context.exception))
    
    @patch('services.voice_service.story_generator.StoryGenerator.generate_story_content')
    @patch('services.voice_service.story_generator.VoiceService')
    def test_create_story_with_narration(self, mock_voice_service, mock_generate_content):
        """Test the creation of a complete story with narration."""
        # Mock the content generation
        mock_generate_content.return_value = self.sample_ai_response
        
        # Mock the voice synthesis
        mock_voice = MagicMock()
        mock_voice_service.return_value = mock_voice
        mock_voice.synthesize_speech.return_value = "/path/to/audio.mp3"
        
        # Call the method under test
        story = self.story_generator.create_story(self.story_params, user_id=1)
        
        # Verify the story was created correctly
        self.assertIsInstance(story, Story)
        self.assertEqual(story.title, self.sample_ai_response["title"])
        self.assertEqual(story.text, self.sample_ai_response["content"])
        self.assertEqual(story.audio_path, "/path/to/audio.mp3")
        self.assertEqual(story.user_id, 1)
        
        # Verify the story metadata was created
        self.assertIsInstance(story.metadata, StoryMetadata)
        self.assertEqual(story.metadata.theme, self.story_params["theme"])
        self.assertEqual(story.metadata.age_group, self.story_params["age_group"])
        self.assertEqual(story.metadata.duration, self.story_params["duration"])
    
    def test_validate_story_params(self):
        """Test the validation of story parameters."""
        # Test valid parameters
        result = self.story_generator.validate_story_params(self.story_params)
        self.assertTrue(result)
        
        # Test missing required parameter
        invalid_params = self.story_params.copy()
        del invalid_params["theme"]
        with self.assertRaises(ValueError) as context:
            self.story_generator.validate_story_params(invalid_params)
        self.assertIn("theme", str(context.exception))
        
        # Test invalid age group
        invalid_params = self.story_params.copy()
        invalid_params["age_group"] = "invalid-age"
        with self.assertRaises(ValueError) as context:
            self.story_generator.validate_story_params(invalid_params)
        self.assertIn("age_group", str(context.exception))


if __name__ == "__main__":
    unittest.main()
