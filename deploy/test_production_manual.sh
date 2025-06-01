#!/bin/bash

# Test StorySpark in Production Mode (without Docker)
# This simulates production deployment using gunicorn locally

set -e

echo "🧪 Testing StorySpark in production mode (without Docker)..."

# Check if we're in the right directory structure
if [ ! -f "../backend/app.py" ]; then
    echo "❌ Error: Please run this script from the deploy/ directory"
    echo "📁 Current directory: $(pwd)"
    exit 1
fi

# Navigate to the project root
cd ..

# Check if Python virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install production dependencies
echo "📦 Installing production dependencies..."
pip install -r backend/requirements.txt

# Install gunicorn for production testing
pip install gunicorn

# Set production environment variables
export FLASK_ENV=production
export FLASK_DEBUG=False
export PORT=5001
export SECRET_KEY=local-test-secret-key-change-in-production
export GEMINI_API_KEY=${GEMINI_API_KEY:-dummy-key-for-testing}
export GOOGLE_CLOUD_PROJECT=${GOOGLE_CLOUD_PROJECT:-dummy-project}

# Create dummy credentials if they don't exist
mkdir -p backend/credentials
if [ ! -f "backend/credentials/google_cloud_credentials.json" ]; then
    echo "🔧 Creating dummy Google credentials for testing..."
    echo '{"type": "service_account", "project_id": "dummy-project"}' > backend/credentials/google_cloud_credentials.json
fi

# Build frontend for production
echo "🏗️  Building frontend for production..."
cd frontend
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
fi

echo "🔨 Building production frontend..."
npm run build

# Go back to project root
cd ..

# Create static directory structure
mkdir -p backend/static
mkdir -p backend/data
mkdir -p backend/logs

# Copy built frontend to backend static directory
if [ -d "frontend/dist" ]; then
    echo "📁 Copying built frontend to backend..."
    cp -r frontend/dist/* backend/static/ 2>/dev/null || true
    # Create index.html if it doesn't exist
    if [ ! -f "backend/static/index.html" ]; then
        echo "🔧 Creating minimal index.html..."
        cat > backend/static/index.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>StorySpark PWA</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body>
    <div id="root">
        <h1>StorySpark PWA</h1>
        <p>Production build is running!</p>
        <p><a href="/health">Health Check</a></p>
        <p><a href="/api/stories">API Test</a></p>
    </div>
</body>
</html>
EOF
    fi
fi

# Kill any existing processes on port 5001
echo "🛑 Stopping any existing processes on port 5001..."
lsof -ti:5001 | xargs kill -9 2>/dev/null || true

# Start the application with gunicorn (production WSGI server)
echo "🚀 Starting StorySpark with gunicorn (production mode)..."
echo "📡 Server will run on http://localhost:5001"

# Run gunicorn from project root with proper module path
# This allows proper import of backend.app and all its dependencies
gunicorn --bind 0.0.0.0:5001 --workers 2 --timeout 120 --chdir . backend.app:app &
GUNICORN_PID=$!

# Wait for the server to start
echo "⏳ Waiting for server to start..."
sleep 5

# Test the health endpoint
max_attempts=10
attempt=1

while [ $attempt -le $max_attempts ]; do
    if curl -f http://localhost:5001/health > /dev/null 2>&1; then
        echo "✅ StorySpark is running in production mode!"
        echo ""
        echo "🌐 Application URLs:"
        echo "   Main app: http://localhost:5001"
        echo "   Health check: http://localhost:5001/health"
        echo "   API test: http://localhost:5001/api/stories"
        echo ""
        
        # Test the health endpoint
        echo "📊 Health check response:"
        curl -s http://localhost:5001/health | python3 -m json.tool 2>/dev/null || curl -s http://localhost:5001/health
        echo ""
        
        echo "📋 Process info:"
        ps aux | grep gunicorn | grep -v grep
        echo ""
        
        echo "🎉 Production test successful!"
        echo ""
        echo "🧪 Test the app by visiting: http://localhost:5001"
        echo ""
        echo "📋 To stop the server:"
        echo "   kill $GUNICORN_PID"
        echo "   or use: pkill -f gunicorn"
        echo ""
        
        # Keep the server running for testing
        echo "⚡ Server is running with PID $GUNICORN_PID"
        echo "📱 Open http://localhost:5001 in your browser to test"
        echo ""
        echo "Press Ctrl+C to stop the server and return to shell"
        
        # Wait for user input or keep running
        wait $GUNICORN_PID
        exit 0
    else
        echo "⏳ Attempt $attempt/$max_attempts - waiting for server to start..."
        sleep 3
        ((attempt++))
    fi
done

echo "❌ Server failed to start after $max_attempts attempts"
echo "🔍 Checking for gunicorn process..."
ps aux | grep gunicorn | grep -v grep || echo "No gunicorn process found"

# Kill the background process if it exists
kill $GUNICORN_PID 2>/dev/null || true

echo ""
echo "🔧 Troubleshooting:"
echo "  1. Check if port 5001 is available: lsof -i :5001"
echo "  2. Try running manually: gunicorn --bind 0.0.0.0:5001 --chdir . backend.app:app"
echo "  3. Check backend logs for errors"

exit 1
