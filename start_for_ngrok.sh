#!/bin/bash

# Start StorySpark backend for ngrok usage
# This script starts the backend server configured to accept external connections

echo "🚀 Starting StorySpark backend for ngrok usage..."
echo ""
echo "Configuration:"
echo "- Host: 0.0.0.0 (allows external connections)"
echo "- Port: 5001"
echo "- CORS: Enabled for all origins"
echo ""

# Navigate to backend directory
cd backend

# Start the Flask app
echo "Starting Flask server..."
python app.py

echo ""
echo "💡 To expose this via ngrok, run in another terminal:"
echo "   ngrok http 5001"
echo ""
echo "📱 Frontend development server should run on port 5173:"
echo "   cd frontend && npm run dev"
