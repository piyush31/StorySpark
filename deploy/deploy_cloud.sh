#!/bin/bash

# StorySpark Cloud Deployment Script
# Run this on your Google Cloud VM after uploading the code

set -e

echo "🚀 Deploying StorySpark to production..."

# Configuration
APP_DIR="/opt/storyspark"
SERVICE_NAME="storyspark"

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Error: docker-compose.yml not found. Make sure you're in the deploy directory."
    echo "📁 Current directory: $(pwd)"
    echo "📁 Expected files: docker-compose.yml, Dockerfile"
    exit 1
fi

# Detect Docker Compose command
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
elif docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
else
    echo "❌ Error: Docker Compose not found. Please run setup_vm.sh first."
    exit 1
fi

echo "📦 Using: $DOCKER_COMPOSE"

# Check for required files
echo "🔍 Checking required files..."
if [ ! -f "../backend/app.py" ]; then
    echo "❌ Error: Backend app.py not found at ../backend/app.py"
    exit 1
fi

if [ ! -f "../frontend/package.json" ]; then
    echo "❌ Error: Frontend package.json not found at ../frontend/package.json"
    exit 1
fi

# Check for Google service account credentials
if [ ! -f "secrets/service-account.json" ]; then
    echo "⚠️  Warning: Google service account JSON not found at secrets/service-account.json"
    echo "📝 Please upload your service account credentials before starting the app"
    echo "   Example: upload your-service-account.json to $(pwd)/secrets/service-account.json"
fi

# Stop existing containers
echo "🛑 Stopping existing containers..."
$DOCKER_COMPOSE down --remove-orphans || true

# Remove old images
echo "🧹 Cleaning up old images..."
docker system prune -f

# Build and start the application
echo "🏗️  Building and starting StorySpark..."
$DOCKER_COMPOSE up -d --build

# Wait for the application to start
echo "⏳ Waiting for application to start..."
sleep 30

# Check health
echo "🏥 Checking application health..."
if curl -f http://localhost:5001/health > /dev/null 2>&1; then
    echo "✅ StorySpark is running successfully!"
    echo "🌐 Application URL: http://$(curl -s ifconfig.me):5001"
    echo "🔗 Local URL: http://localhost:5001"
else
    echo "❌ Health check failed. Checking logs..."
    $DOCKER_COMPOSE logs --tail=50
    exit 1
fi

# Show status
echo "📊 Container status:"
$DOCKER_COMPOSE ps

echo "📋 Useful commands:"
echo "  View logs: $DOCKER_COMPOSE logs -f"
echo "  Stop app: $DOCKER_COMPOSE down"
echo "  Restart: $DOCKER_COMPOSE restart"
echo "  Update: git pull && $DOCKER_COMPOSE up -d --build"

echo "🎉 Deployment completed successfully!"