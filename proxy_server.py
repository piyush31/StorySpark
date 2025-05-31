# Simple proxy for voice API requests
# Will be used by Vite for frontend development

from flask import Flask, request, jsonify, send_from_directory
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up API keys
os.environ["GEMINI_API_KEY"] = os.environ.get("GEMINI_API_KEY", "")
os.environ["OPENAI_API_KEY"] = os.environ.get("OPENAI_API_KEY", "")

app = Flask(__name__)

# Backend API URL
BACKEND_URL = 'http://localhost:5000/api'

@app.route('/api/voice/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy_voice_api(path):
    """Proxy requests to the voice API"""
    url = f"{BACKEND_URL}/voice/{path}"
    
    if request.method == 'GET':
        resp = requests.get(url, params=request.args)
    elif request.method == 'POST':
        resp = requests.post(url, json=request.json)
    elif request.method == 'PUT':
        resp = requests.put(url, json=request.json)
    elif request.method == 'DELETE':
        resp = requests.delete(url)
    
    return jsonify(resp.json()), resp.status_code

@app.route('/api/stories', methods=['GET'])
def get_stories():
    """Get list of stories"""
    url = f"{BACKEND_URL}/stories"
    resp = requests.get(url)
    return jsonify(resp.json()), resp.status_code

@app.route('/generated/<path:filename>')
def serve_generated_audio(filename):
    """Serve generated audio files"""
    # In development, we'll just serve placeholder audio
    return send_from_directory('static/placeholders', 'story_audio.mp3')

if __name__ == '__main__':
    app.run(port=3001)
