"""
This module contains database models for the StorySpark application.
Models include:
- User: User authentication and profile
- UserPreference: User preferences for stories and UI
- Story: Generated story content and metadata
- StoryMetadata: Additional data about generated stories
"""

from models.user import db, bcrypt, User, UserPreference
from models.story import Story, StoryMetadata

# Initialize database and related modules
def init_db(app):
    """Initialize the database with the Flask app"""
    db.init_app(app)
    bcrypt.init_app(app)
    
    # Create tables if they don't exist
    with app.app_context():
        db.create_all()
