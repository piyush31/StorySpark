#!/bin/bash

# Script to start both frontend and backend services

echo "Starting StorySpark services..."

# Start the backend
cd backend
source venv/bin/activate
python app.py &
BACKEND_PID=$!
echo "Backend started with PID: $BACKEND_PID"

# Start the frontend
cd ../frontend
npm start &
FRONTEND_PID=$!
echo "Frontend started with PID: $FRONTEND_PID"

echo "Services are running!"
echo "- Backend: http://localhost:5000"
echo "- Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all services"

# Handle termination
trap "kill $BACKEND_PID $FRONTEND_PID; exit" SIGINT SIGTERM

# Keep script running
wait
