#!/bin/bash

# Build script for StorySpark production deployment

# Change directory to the project root
cd "$(dirname "$0")"

echo "Building StorySpark for production..."

# Build the frontend
echo "Building React frontend..."
cd frontend
npm run build
BUILD_STATUS=$?

if [ $BUILD_STATUS -ne 0 ]; then
    echo "Frontend build failed with status $BUILD_STATUS"
    exit $BUILD_STATUS
fi

echo "Frontend build complete."

# Create a dist directory in the backend folder for the built frontend
echo "Copying frontend build to backend/dist..."
mkdir -p ../backend/dist
cp -r dist/* ../backend/dist/

# Go back to project root
cd ..

# Create production ready Python environment
echo "Setting up backend for production..."
cd backend

# Install production dependencies if needed
# pip install -r requirements.txt

echo "---------------------------------------"
echo "Build completed successfully!"
echo "To run the production server:"
echo "cd backend && python app.py"
echo "---------------------------------------"
