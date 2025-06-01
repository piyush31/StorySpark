from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import os
from datetime import timedelta
from dotenv import load_dotenv
from routes.api import api
from routes.voice_api import voice_api
from routes.auth_api import auth_api
from models import init_db

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__, static_folder='dist')

# Configure app
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI', 'sqlite:///storyspark.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)

# Initialize extensions
CORS(app, resources={
    r"/*": {
        "origins": "*",  # Allow all origins for ngrok compatibility
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "Accept", "Origin", "X-Requested-With"],
        "expose_headers": ["Content-Range", "X-Content-Range"],
        "supports_credentials": True
    }
})
jwt = JWTManager(app)
init_db(app)

# Register blueprints
app.register_blueprint(api, url_prefix='/api')
app.register_blueprint(voice_api, url_prefix='/api/voice')
app.register_blueprint(auth_api, url_prefix='/api/auth')

# Route for serving audio files from the static directory
@app.route('/static/<path:filename>')
def serve_static_audio(filename):
    """Serve static audio files"""
    try:
        static_dir = os.path.join(os.path.dirname(__file__), '../static')
        if not os.path.exists(os.path.join(static_dir, filename)):
            app.logger.warning(f"Static file not found: {filename}")
            # Return a 404 if the file doesn't exist
            return jsonify({
                'status': 'error',
                'message': f'File not found: {filename}'
            }), 404
        
        return send_from_directory(static_dir, filename)
    except Exception as e:
        app.logger.error(f"Error serving static file {filename}: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Error serving file: {str(e)}'
        }), 500

@app.route('/')
def hello_world():
    """Simple route to verify the API is working"""
    # In development, return a simple JSON response
    if os.environ.get('FLASK_ENV') == 'development':
        return jsonify({
            'message': 'Hello from StorySpark API!',
            'status': 'success'
        })
    # In production, serve the React app
    else:
        return send_from_directory(app.static_folder, 'index.html')

# Serve static files in production
@app.route('/<path:path>')
def serve_static(path):
    """Serve static files from the frontend build directory"""
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    # Get port from environment variable or default to 5001 (to match frontend proxy)
    port = int(os.environ.get('PORT', 5001))
    # Get debug mode from environment variable or default to True
    debug = os.environ.get('DEBUG', 'True').lower() in ('true', '1', 't')
    # Run the Flask app with host='0.0.0.0' to allow external connections (ngrok)
    print(f"Starting StorySpark backend on host=0.0.0.0, port={port}")
    print("This allows external connections via ngrok or other tunneling services")
    app.run(debug=debug, host='0.0.0.0', port=port)
