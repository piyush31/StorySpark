#!/bin/bash

# All-in-one demo starter for StorySpark
# Starts backend, frontend, and provides ngrok instructions

echo "🚀 Starting StorySpark Demo Environment..."
echo ""

# Function to cleanup background processes
cleanup() {
    echo ""
    echo "🧹 Cleaning up processes..."
    pkill -f "python app.py" 2>/dev/null
    pkill -f "npm run dev" 2>/dev/null
    exit 0
}

# Set up cleanup on script exit
trap cleanup EXIT INT TERM

# Start backend in background
echo "📡 Starting backend server..."
cd backend
python app.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Check if backend is running
if ! curl -s http://localhost:5001/ > /dev/null; then
    echo "❌ Backend failed to start"
    exit 1
fi

echo "✅ Backend running on http://localhost:5001"

# Start frontend in background
echo "🎨 Starting frontend server..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

# Wait for frontend to start
sleep 5

# Check if frontend is running
if ! curl -s http://localhost:5173/ > /dev/null; then
    echo "❌ Frontend failed to start"
    exit 1
fi

echo "✅ Frontend running on http://localhost:5173"
echo ""
echo "🌐 Ready for ngrok! In a new terminal, run:"
echo "   ngrok http 5173"
echo ""
echo "📱 Your demo URL will be the ngrok HTTPS URL"
echo "🔧 Local access: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop all services"

# Keep script running and show logs
tail -f /dev/null
