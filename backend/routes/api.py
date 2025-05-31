from flask import Blueprint, jsonify

# Create a Blueprint for API routes
api = Blueprint('api', __name__)

@api.route('/stories')
def get_stories():
    """Example route for getting stories"""
    # Placeholder for actual story retrieval logic
    stories = [
        {
            'id': 1,
            'title': 'The Magical Forest',
            'duration': '5 minutes',
            'theme': 'Courage',
            'isDownloaded': True
        },
        {
            'id': 2,
            'title': 'Diwali Celebration',
            'duration': '10 minutes',
            'theme': 'Festive',
            'isDownloaded': False
        }
    ]
    return jsonify(stories)
