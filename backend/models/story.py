"""
Story models for StorySpark application

This module defines the Story and StoryMetadata models for managing 
generated stories and related data.
"""
from datetime import datetime
from .user import db

class Story(db.Model):
    """Model for storing generated stories"""
    __tablename__ = 'stories'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    audio_path = db.Column(db.String(255), nullable=True)
    theme = db.Column(db.String(100), nullable=True)
    duration = db.Column(db.String(50), nullable=True)  # "short", "medium", "long"
    age_group = db.Column(db.String(50), nullable=True)  # "3-5", "6-8", etc.
    language = db.Column(db.String(10), default='en')  # ISO language code
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Relationships
    story_metadata = db.relationship('StoryMetadata', backref='story', lazy=True, uselist=False)
    
    def to_dict(self):
        """Convert story object to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'audio_path': self.audio_path,
            'theme': self.theme,
            'duration': self.duration,
            'age_group': self.age_group,
            'language': self.language,
            'created_at': self.created_at.isoformat(),
            'user_id': self.user_id,
            'metadata': self.story_metadata.to_dict() if self.story_metadata else None
        }


class StoryMetadata(db.Model):
    """Metadata for generated stories, including emotional markers and sound effects"""
    __tablename__ = 'story_metadata'
    
    id = db.Column(db.Integer, primary_key=True)
    story_id = db.Column(db.Integer, db.ForeignKey('stories.id'), nullable=False)
    
    # Generation parameters 
    prompt_used = db.Column(db.Text, nullable=True)
    generation_time = db.Column(db.Float, nullable=True)  # Time in seconds
    
    # Emotional markers - stored as JSON string
    emotional_markers = db.Column(db.Text, nullable=True)  # JSON string with paragraph-level emotions
    
    # Sound effects - stored as JSON string
    sound_effects = db.Column(db.Text, nullable=True)  # JSON string with sound effect mappings
    
    # Cultural elements - stored as JSON string
    cultural_elements = db.Column(db.Text, nullable=True)  # JSON string with cultural element markers
    
    def to_dict(self):
        """Convert metadata object to dictionary"""
        return {
            'id': self.id,
            'story_id': self.story_id,
            'prompt_used': self.prompt_used,
            'generation_time': self.generation_time,
            'emotional_markers': self.emotional_markers,
            'sound_effects': self.sound_effects,
            'cultural_elements': self.cultural_elements
        }
