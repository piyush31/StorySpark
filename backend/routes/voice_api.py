"""
Voice and Story API routes for StorySpark

This module defines the API endpoints for voice-related features,
including story generation and narration.
"""
from flask import Blueprint, jsonify, request, current_app
import os
import json
import logging
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..services.voice_service import voice_service, story_generator
from ..models.story import Story, StoryMetadata, db
from ..models.user import User, UserPreference
from ..utils.auth import get_current_user

# Configure logging
logger = logging.getLogger(__name__)

# Create a Blueprint for voice API routes
voice_api = Blueprint('voice_api', __name__)

@voice_api.route('/generate-story', methods=['POST'])
def generate_story():
    """
    Generate a new story based on given parameters
    
    Request JSON parameters:
    - theme: Theme or moral of the story (optional)
    - characters: List of character types or names (optional)
    - setting: Setting for the story (optional)
    - duration: Length of the story (default: "medium")
    - age_group: Target age group (default: "5-8")
    - language: Primary language code (default: "en")
    - child_name: Name of the child for personalization (optional)
    - save: Whether to save the story to the database (default: false)
    
    Returns:
        JSON with story data including title, text, and audio path
    """
    try:
        # Get request data
        data = request.json or {}
        
        # Get current user (if authenticated)
        current_user = get_current_user()
        
        # Use user preferences if available and not overridden
        if current_user:
            user_prefs = UserPreference.query.filter_by(user_id=current_user.id).first()
            if user_prefs:
                if 'language' not in data and user_prefs.preferred_language:
                    data['language'] = user_prefs.preferred_language
                if 'child_name' not in data and user_prefs.child_name:
                    data['child_name'] = user_prefs.child_name
        
        # Track generation start time
        generation_start = datetime.utcnow()
        
        # Check if Gemini model is initialized
        logger.info(f"Gemini model initialized: {story_generator.gemini_model is not None}")
        
        # Generate the story
        story_data = story_generator.generate_story(
            theme=data.get('theme'),
            characters=data.get('characters'),
            setting=data.get('setting'),
            duration=data.get('duration', 'medium'),
            age_group=data.get('age_group', '5-8'),
            language=data.get('language', 'en'),
            child_name=data.get('child_name')
        )
        
        # Track generation end time
        generation_time = (datetime.utcnow() - generation_start).total_seconds()
        
        # Save to database if requested
        if data.get('save', False) and current_user:
            try:
                # Create new story record
                story = Story(
                    title=story_data.get('title', 'Untitled Story'),
                    content=story_data.get('text', ''),
                    audio_path=story_data.get('audio_path'),
                    theme=data.get('theme'),
                    duration=data.get('duration', 'medium'),
                    age_group=data.get('age_group', '5-8'),
                    language=data.get('language', 'en'),
                    user_id=current_user.id
                )
                
                # Create metadata
                metadata = StoryMetadata(
                    prompt_used=json.dumps(data),
                    generation_time=generation_time,
                    emotional_markers=json.dumps(story_data.get('emotions', {})),
                    sound_effects=json.dumps(story_data.get('sound_effects', {})),
                    cultural_elements=json.dumps(story_data.get('cultural_elements', {}))
                )
                
                story.story_metadata = metadata
                
                # Save to database
                db.session.add(story)
                db.session.commit()
                
                # Update story_data with database ID
                story_data['id'] = story.id
                story_data['saved'] = True
            
            except Exception as e:
                logger.error(f"Error saving story to database: {str(e)}")
                db.session.rollback()
                # Continue without saving
                story_data['saved'] = False
        
        return jsonify({
            'status': 'success',
            'story': story_data
        })
    
    except Exception as e:
        logger.error(f"Error generating story: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@voice_api.route('/narrate-story/<story_id>', methods=['GET'])
def narrate_story(story_id):
    """
    Generate narration for an existing story
    
    Path parameters:
    - story_id: ID of the story to narrate
    
    Returns:
        JSON with narration data including audio path
    """
    try:
        # Generate narration for the story
        narration_data = story_generator.narrate_existing_story(story_id)
        
        return jsonify({
            'status': 'success',
            'narration': narration_data
        })
    
    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 404
    
    except Exception as e:
        logger.error(f"Error narrating story: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@voice_api.route('/available-voices', methods=['GET'])
def get_available_voices():
    """
    Get list of available voice profiles
    
    Returns:
        JSON with list of available voices
    """
    try:
        voices = voice_service._load_available_voices()
        
        return jsonify({
            'status': 'success',
            'voices': voices
        })
    
    except Exception as e:
        logger.error(f"Error fetching voices: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@voice_api.route('/available-sound-effects', methods=['GET'])
def get_available_sound_effects():
    """
    Get list of available sound effects
    
    Returns:
        JSON with list of available sound effects
    """
    try:
        effects = voice_service._load_sound_effects()
        
        return jsonify({
            'status': 'success',
            'effects': [{'name': name, 'path': path} for name, path in effects.items()]
        })
    
    except Exception as e:
        logger.error(f"Error fetching sound effects: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
