"""
User models for StorySpark application

This module defines the User and UserPreference models for authentication
and personalization features.
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

class User(db.Model):
    """User model for authentication and user management"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    
    # Relationships
    preferences = db.relationship('UserPreference', backref='user', lazy=True)
    stories = db.relationship('Story', backref='creator', lazy=True)
    
    def set_password(self, password):
        """Hash and set the user password"""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        """Check if the provided password matches the stored hash"""
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert user object to dictionary (excludes password)"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'created_at': self.created_at.isoformat(),
            'is_admin': self.is_admin
        }


class UserPreference(db.Model):
    """User preferences for story generation and app settings"""
    __tablename__ = 'user_preferences'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    preferred_language = db.Column(db.String(10), default='en')  # ISO language code
    preferred_storyteller = db.Column(db.String(50), default='Dadi Maa')
    preferred_theme = db.Column(db.String(50), nullable=True)
    child_name = db.Column(db.String(50), nullable=True)
    child_age = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert preference object to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'preferred_language': self.preferred_language,
            'preferred_storyteller': self.preferred_storyteller,
            'preferred_theme': self.preferred_theme,
            'child_name': self.child_name,
            'child_age': self.child_age
        }
