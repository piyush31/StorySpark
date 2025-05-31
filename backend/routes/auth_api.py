"""
Authentication API routes for StorySpark

This module defines API endpoints for user registration, login, logout,
and account management.
"""
from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity,
    get_jwt, current_user
)
import datetime
import logging
from email_validator import validate_email, EmailNotValidError
from models.user import User, UserPreference, db

# Configure logging
logger = logging.getLogger(__name__)

# Create a Blueprint for auth API routes
auth_api = Blueprint('auth_api', __name__)

@auth_api.route('/register', methods=['POST'])
def register():
    """
    Register a new user
    
    Request JSON parameters:
    - username: Username (required)
    - email: Email address (required)
    - password: Password (required)
    - first_name: First name (optional)
    - last_name: Last name (optional)
    """
    data = request.get_json()
    
    # Validate required fields
    if not all(k in data for k in ('username', 'email', 'password')):
        return jsonify({
            'status': 'error',
            'message': 'Missing required fields (username, email, password)'
        }), 400
    
    # Validate email format
    try:
        email_info = validate_email(data['email'], check_deliverability=False)
        email = email_info.normalized
    except EmailNotValidError as e:
        return jsonify({
            'status': 'error',
            'message': f'Invalid email: {str(e)}'
        }), 400
    
    # Check if username or email already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({
            'status': 'error',
            'message': 'Username already exists'
        }), 409
    
    if User.query.filter_by(email=email).first():
        return jsonify({
            'status': 'error',
            'message': 'Email already exists'
        }), 409
    
    # Create new user
    try:
        new_user = User(
            username=data['username'],
            email=email,
            first_name=data.get('first_name'),
            last_name=data.get('last_name')
        )
        new_user.set_password(data['password'])
        
        # Create default preferences
        default_preferences = UserPreference(
            preferred_language=data.get('language', 'en'),
            preferred_storyteller=data.get('storyteller', 'Dadi Maa')
        )
        
        new_user.preferences.append(default_preferences)
        
        # Save to database
        db.session.add(new_user)
        db.session.commit()
        
        # Generate tokens
        access_token = create_access_token(identity=new_user.id)
        refresh_token = create_refresh_token(identity=new_user.id)
        
        return jsonify({
            'status': 'success',
            'message': 'User registered successfully',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': new_user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error registering user: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Registration failed. Please try again.'
        }), 500


@auth_api.route('/login', methods=['POST'])
def login():
    """
    Login a user
    
    Request JSON parameters:
    - username_or_email: Username or email (required)
    - password: Password (required)
    """
    data = request.get_json()
    
    # Validate required fields
    if not all(k in data for k in ('username_or_email', 'password')):
        return jsonify({
            'status': 'error',
            'message': 'Missing required fields (username_or_email, password)'
        }), 400
    
    # Find user by username or email
    username_or_email = data['username_or_email']
    user = User.query.filter(
        (User.username == username_or_email) | 
        (User.email == username_or_email)
    ).first()
    
    # Check if user exists and password is correct
    if not user or not user.check_password(data['password']):
        return jsonify({
            'status': 'error',
            'message': 'Invalid username/email or password'
        }), 401
    
    # Check if user is active
    if not user.is_active:
        return jsonify({
            'status': 'error',
            'message': 'Account is inactive. Please contact support.'
        }), 403
    
    # Generate tokens
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    
    return jsonify({
        'status': 'success',
        'message': 'Login successful',
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user.to_dict()
    }), 200


@auth_api.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    """Refresh access token using a valid refresh token"""
    user_id = get_jwt_identity()
    access_token = create_access_token(identity=user_id)
    
    return jsonify({
        'status': 'success',
        'access_token': access_token
    }), 200


@auth_api.route('/me', methods=['GET'])
@jwt_required()
def get_user_profile():
    """Get current user's profile"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({
            'status': 'error',
            'message': 'User not found'
        }), 404
    
    # Get user preferences
    preferences = UserPreference.query.filter_by(user_id=user_id).first()
    
    return jsonify({
        'status': 'success',
        'user': user.to_dict(),
        'preferences': preferences.to_dict() if preferences else None
    }), 200


@auth_api.route('/me/preferences', methods=['PUT'])
@jwt_required()
def update_preferences():
    """
    Update user preferences
    
    Request JSON parameters:
    - preferred_language: ISO language code (optional)
    - preferred_storyteller: Storyteller name (optional)
    - preferred_theme: Theme preference (optional)
    - child_name: Child's name (optional)
    - child_age: Child's age (optional)
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Get or create user preferences
    preferences = UserPreference.query.filter_by(user_id=user_id).first()
    
    if not preferences:
        preferences = UserPreference(user_id=user_id)
        db.session.add(preferences)
    
    # Update fields
    if 'preferred_language' in data:
        preferences.preferred_language = data['preferred_language']
    
    if 'preferred_storyteller' in data:
        preferences.preferred_storyteller = data['preferred_storyteller']
    
    if 'preferred_theme' in data:
        preferences.preferred_theme = data['preferred_theme']
    
    if 'child_name' in data:
        preferences.child_name = data['child_name']
    
    if 'child_age' in data:
        preferences.child_age = data['child_age']
    
    try:
        db.session.commit()
        return jsonify({
            'status': 'success',
            'message': 'Preferences updated successfully',
            'preferences': preferences.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating preferences: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to update preferences'
        }), 500


@auth_api.route('/me/password', methods=['PUT'])
@jwt_required()
def change_password():
    """
    Change user password
    
    Request JSON parameters:
    - current_password: Current password (required)
    - new_password: New password (required)
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate required fields
    if not all(k in data for k in ('current_password', 'new_password')):
        return jsonify({
            'status': 'error',
            'message': 'Missing required fields (current_password, new_password)'
        }), 400
    
    # Get user
    user = User.query.get(user_id)
    
    # Verify current password
    if not user.check_password(data['current_password']):
        return jsonify({
            'status': 'error',
            'message': 'Current password is incorrect'
        }), 401
    
    # Update password
    try:
        user.set_password(data['new_password'])
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Password updated successfully'
        }), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error changing password: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to update password'
        }), 500
