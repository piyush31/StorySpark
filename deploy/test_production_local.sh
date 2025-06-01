#!/bin/bash

# Local Production Testing Script
# Tests the production deployment on your local machine

set -e

echo "🧪 Testing StorySpark production deployment locally..."

# Check if we're in the right directory
if [ ! -f "Dockerfile" ]; then
    echo "❌ Error: Please run this script from the deploy/ directory"
    exit 1
fi

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker not found. Please install Docker Desktop."
    exit 1
fi

# Detect Docker Compose command
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
elif docker compose version &> /dev/null 2>&1; then
    DOCKER_COMPOSE="docker compose"
else
    echo "❌ Error: Docker Compose not found."
    exit 1
fi

echo "📦 Using: $DOCKER_COMPOSE"

# Create secrets directory if it doesn't exist
mkdir -p secrets

# Check for Google service account (optional for local testing)
if [ ! -f "secrets/service-account.json" ]; then
    echo "⚠️  Warning: No Google service account found at secrets/service-account.json"
    echo "🔧 Creating dummy service account for local testing..."
    echo '{"type": "service_account", "project_id": "dummy-project"}' > secrets/service-account.json
fi

# Create local environment file if it doesn't exist
if [ ! -f ".env.local" ]; then
    echo "📝 Creating local environment file..."
    cat > .env.local << 'EOF'
# Local testing environment variables
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=local-test-secret-key-change-in-production
DATABASE_URL=sqlite:///data/storyspark.db
GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/service-account.json
GOOGLE_CLOUD_PROJECT=dummy-project
GEMINI_API_KEY=dummy-key-for-local-testing
PORT=5001
HOST=0.0.0.0
LOG_LEVEL=INFO
EOF
    echo "✅ Created .env.local - you can edit this file with real API keys for full testing"
fi

# Stop any existing containers
echo "🛑 Stopping existing containers..."
$DOCKER_COMPOSE -f docker-compose.local.yml down 2>/dev/null || true

# Clean up old images
echo "🧹 Cleaning up old images..."
docker system prune -f >/dev/null 2>&1 || true

# Build and start the application
echo "🏗️  Building and starting StorySpark in production mode..."
$DOCKER_COMPOSE -f docker-compose.local.yml up --build -d

# Wait for the application to start
echo "⏳ Waiting for application to start..."
sleep 20

# Check health
echo "🏥 Checking application health..."
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
        
        # Show container status
        echo "📋 Container status:"
        $DOCKER_COMPOSE -f docker-compose.local.yml ps
        
        echo ""
        echo "📋 Useful commands:"
        echo "  View logs: $DOCKER_COMPOSE -f docker-compose.local.yml logs -f"
        echo "  Stop app: $DOCKER_COMPOSE -f docker-compose.local.yml down"
        echo "  Restart: $DOCKER_COMPOSE -f docker-compose.local.yml restart"
        echo ""
        echo "🎉 Production test deployment successful!"
        exit 0
    else
        echo "⏳ Attempt $attempt/$max_attempts - waiting for app to start..."
        sleep 5
        ((attempt++))
    fi
done

echo "❌ Health check failed after $max_attempts attempts. Checking logs..."
$DOCKER_COMPOSE -f docker-compose.local.yml logs --tail=30
echo ""
echo "🔧 Troubleshooting:"
echo "  1. Check logs above for errors"
echo "  2. Verify Docker is running"
echo "  3. Check if port 5001 is available"
echo "  4. Try: $DOCKER_COMPOSE -f docker-compose.local.yml down && $DOCKER_COMPOSE -f docker-compose.local.yml up --build"

exit 1
