from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.story import Story, StoryMetadata, db
from models.user import User
from utils.auth import get_current_user

# Create a Blueprint for API routes
api = Blueprint('api', __name__)

@api.route('/stories')
def get_stories():
    """
    Get list of stories
    
    Query parameters:
    - public_only: If 'true', return only public stories
    """
    # Get current user (if authenticated)
    current_user = get_current_user()
    
    # Check if we should return only public stories
    public_only = request.args.get('public_only', 'false').lower() == 'true'
    
    # Query stories
    if current_user and not public_only:
        # Return both public stories and user's private stories
        stories = Story.query.filter(
            (Story.user_id == current_user.id) | (Story.user_id.is_(None))
        ).order_by(Story.created_at.desc()).all()
    else:
        # Return only public stories
        stories = Story.query.filter(Story.user_id.is_(None)).order_by(Story.created_at.desc()).all()
    
    # Convert to dictionaries
    stories_data = [story.to_dict() for story in stories]
    
    return jsonify(stories_data)

@api.route('/stories/<int:story_id>')
def get_story(story_id):
    """Get a specific story by ID"""
    # Get current user (if authenticated)
    current_user = get_current_user()
    
    # Find the story
    story = Story.query.get(story_id)
    
    # Check if story exists
    if not story:
        return jsonify({
            'status': 'error',
            'message': 'Story not found'
        }), 404
    
    # Check permission - users can only access their own stories or public stories
    if story.user_id and (not current_user or story.user_id != current_user.id):
        return jsonify({
            'status': 'error',
            'message': 'You do not have permission to access this story'
        }), 403
    
    return jsonify(story.to_dict())

@api.route('/stories/<int:story_id>', methods=['DELETE'])
@jwt_required()
def delete_story(story_id):
    """Delete a story (must be owner)"""
    user_id = get_jwt_identity()
    
    # Find the story
    story = Story.query.get(story_id)
    
    # Check if story exists
    if not story:
        return jsonify({
            'status': 'error',
            'message': 'Story not found'
        }), 404
    
    # Check permission - users can only delete their own stories
    if not story.user_id or story.user_id != user_id:
        return jsonify({
            'status': 'error',
            'message': 'You do not have permission to delete this story'
        }), 403
    
    try:
        # Delete associated metadata first
        if story.metadata:
            db.session.delete(story.metadata)
        
        # Delete the story
        db.session.delete(story)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Story deleted successfully'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Failed to delete story: {str(e)}'
        }), 500

@api.route('/my-stories')
@jwt_required()
def get_my_stories():
    """Get stories created by the authenticated user"""
    user_id = get_jwt_identity()
    
    # Get user's stories
    stories = Story.query.filter_by(user_id=user_id).order_by(Story.created_at.desc()).all()
    
    # Convert to dictionaries
    stories_data = [story.to_dict() for story in stories]
    
    return jsonify(stories_data)
