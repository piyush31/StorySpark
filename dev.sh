#!/bin/bash

# Check if there are any existing servers and kill them
echo "Stopping any existing servers..."
pkill -f "python app.py" || true
pkill -f "python proxy_server.py" || true
pkill -f "vite" || true

# Change directory to the project root
cd "$(dirname "$0")"

# Set up sound effects for development
echo "Setting up sound effects for development..."
python3 setup_sound_effects.py

# Start the backend server
echo "Starting Flask backend server..."
cd backend
source venv/bin/activate
# Set environment variables from .env file
export $(grep -v '^#' ../.env | xargs)
python app.py &
BACKEND_PID=$!
cd ..

# Give the backend a moment to start up
sleep 2

# Start the proxy server
echo "Starting API proxy server..."
cd backend
python ../proxy_server.py &
PROXY_PID=$!
cd ..

# Give the proxy a moment to start up
sleep 1

# Start the frontend server
echo "Starting React frontend server..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo "---------------------------------------"
echo "StorySpark servers are running!"
echo "Backend: http://localhost:5000"
echo "Proxy: http://localhost:3001"
echo "Frontend: http://localhost:5173"
echo "---------------------------------------"
echo "Press Ctrl+C to stop all servers"

# Function to clean up servers on exit
cleanup() {
    echo "Stopping servers..."
    kill $BACKEND_PID $PROXY_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

# Set up trap to catch exit signal
trap cleanup INT TERM

# Wait for user to press Ctrl+C
wait
