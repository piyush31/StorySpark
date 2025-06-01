"""
Authentication middleware and utilities for StorySpark

This module provides utility functions and middleware for authentication 
and authorization in the API.
"""
from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from ..models.user import User

def admin_required():
    """
    Decorator for endpoints that require admin access
    
    Usage:
    @app.route('/admin-only')
    @admin_required()
    def admin_endpoint():
        return jsonify(message="Admin only content")
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            # Verify JWT is present and valid
            verify_jwt_in_request()
            
            # Get user
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
            # Check if user is admin
            if not user or not user.is_admin:
                return jsonify({
                    'status': 'error',
                    'message': 'Admin access required'
                }), 403
                
            return fn(*args, **kwargs)
        return decorator
    return wrapper

def get_current_user():
    """
    Get the current authenticated user from the JWT token
    
    Returns:
        User object or None if not authenticated
    """
    try:
        verify_jwt_in_request(optional=True)
        user_id = get_jwt_identity()
        
        if user_id:
            return User.query.get(user_id)
        return None
    except:
        return None
