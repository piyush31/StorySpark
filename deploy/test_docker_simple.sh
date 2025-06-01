#!/bin/bash

# Simple Docker Production Test (without Docker Compose)
# Tests the production Docker build on your local machine

set -e

echo "🧪 Testing StorySpark production build with Docker..."

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

# Create secrets directory if it doesn't exist
mkdir -p secrets

# Check for Google service account (optional for local testing)
if [ ! -f "secrets/service-account.json" ]; then
    echo "⚠️  Warning: No Google service account found at secrets/service-account.json"
    echo "🔧 Creating dummy service account for local testing..."
    echo '{"type": "service_account", "project_id": "dummy-project"}' > secrets/service-account.json
fi

# Stop any existing container
echo "🛑 Stopping existing StorySpark container..."
docker stop storyspark-test 2>/dev/null || true
docker rm storyspark-test 2>/dev/null || true

# Build the Docker image
echo "🏗️  Building StorySpark Docker image..."
docker build -t storyspark:test -f Dockerfile ..

# Create and start the container
echo "🚀 Starting StorySpark container..."
docker run -d \
  --name storyspark-test \
  -p 5001:5001 \
  -e FLASK_ENV=production \
  -e PORT=5001 \
  -e SECRET_KEY=local-test-secret-key \
  -e GEMINI_API_KEY=${GEMINI_API_KEY:-dummy-key} \
  -e GOOGLE_CLOUD_PROJECT=${GOOGLE_CLOUD_PROJECT:-dummy-project} \
  -v "$(pwd)/secrets:/app/credentials:ro" \
  storyspark:test

# Wait for the application to start
echo "⏳ Waiting for application to start..."
sleep 15

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
        docker ps --filter name=storyspark-test --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        
        echo ""
        echo "📋 Useful commands:"
        echo "  View logs: docker logs -f storyspark-test"
        echo "  Stop app: docker stop storyspark-test"
        echo "  Remove: docker rm storyspark-test"
        echo "  Shell access: docker exec -it storyspark-test /bin/bash"
        echo ""
        echo "🎉 Production test deployment successful!"
        echo ""
        echo "🧪 Test the app by visiting http://localhost:5001"
        exit 0
    else
        echo "⏳ Attempt $attempt/$max_attempts - waiting for app to start..."
        sleep 5
        ((attempt++))
    fi
done

echo "❌ Health check failed after $max_attempts attempts. Checking logs..."
echo ""
echo "🔍 Container logs:"
docker logs storyspark-test --tail=30
echo ""
echo "📋 Container status:"
docker ps -a --filter name=storyspark-test
echo ""
echo "🔧 Troubleshooting:"
echo "  1. Check logs above for errors"
echo "  2. Verify Docker is running"
echo "  3. Check if port 5001 is available: lsof -i :5001"
echo "  4. Try manual inspection: docker exec -it storyspark-test /bin/bash"

exit 1
