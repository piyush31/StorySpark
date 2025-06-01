#!/bin/bash

# Quick deployment script for development testing
# This builds and runs StorySpark locally using Docker

set -e

echo "🚀 Quick deployment for testing..."

# Check if we're in the right directory
if [ ! -f "Dockerfile" ]; then
    echo "❌ Error: Please run this script from the deploy/ directory"
    exit 1
fi

# Detect Docker Compose command
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
elif docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
else
    echo "❌ Error: Docker Compose not found. Please install Docker Compose."
    echo "   Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "📦 Using: $DOCKER_COMPOSE"

# Stop existing containers
echo "🛑 Stopping existing containers..."
$DOCKER_COMPOSE down 2>/dev/null || true

# Build and start
echo "🏗️  Building and starting StorySpark..."
$DOCKER_COMPOSE up --build -d

# Wait for startup
echo "⏳ Waiting for application to start..."
sleep 15

# Check if it's running
if curl -f http://localhost:5001/health > /dev/null 2>&1; then
    echo "✅ StorySpark is running!"
    echo "🌐 Open: http://localhost:5001"
else
    echo "❌ Something went wrong. Checking logs..."
    $DOCKER_COMPOSE logs --tail=20
fi

echo "📋 Use '$DOCKER_COMPOSE logs -f' to view logs"
echo "📋 Use '$DOCKER_COMPOSE down' to stop"