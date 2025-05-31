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
CORS(app)
jwt = JWTManager(app)
init_db(app)

# Register blueprints
app.register_blueprint(api, url_prefix='/api')
app.register_blueprint(voice_api, url_prefix='/api/voice')
app.register_blueprint(auth_api, url_prefix='/api/auth')

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
    # Get port from environment variable or default to 5000
    port = int(os.environ.get('PORT', 5000))
    # Get debug mode from environment variable or default to True
    debug = os.environ.get('DEBUG', 'True').lower() in ('true', '1', 't')
    # Run the Flask app
    app.run(debug=debug, host='0.0.0.0', port=port)
