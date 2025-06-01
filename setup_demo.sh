#!/bin/bash

# Demo Setup for StorySpark
# This creates a single demoable link by exposing the frontend via ngrok
# The frontend will proxy API calls to the local backend

echo "🎭 Setting up StorySpark for demo..."
echo ""

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    echo "❌ ngrok is not installed. Please install it from https://ngrok.com/download"
    exit 1
fi

echo "📋 Demo Setup Instructions:"
echo ""
echo "1. Start the backend server (Terminal 1):"
echo "   cd backend && python app.py"
echo ""
echo "2. Start the frontend dev server (Terminal 2):"
echo "   cd frontend && npm run dev"
echo ""
echo "3. Expose frontend via ngrok (Terminal 3):"
echo "   ngrok http 5173"
echo ""
echo "💡 The ngrok URL will be your demoable link!"
echo "   Users can access the full StorySpark app via that URL"
echo ""
echo "🔧 Backend runs on: http://localhost:5001"
echo "🎨 Frontend runs on: http://localhost:5173"
echo "🌐 Demo URL will be: https://xxxxx.ngrok.io"
echo ""
echo "⚠️  Make sure both servers are running before starting ngrok!"
