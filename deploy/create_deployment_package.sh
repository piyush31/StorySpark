#!/bin/bash

# StorySpark Production Deployment Package Creator
# This script packages everything needed for cloud deployment

set -e

echo "📦 Creating StorySpark deployment package..."

# Configuration
PACKAGE_NAME="storyspark-deployment-$(date +%Y%m%d-%H%M%S)"
PACKAGE_DIR="/tmp/$PACKAGE_NAME"
CURRENT_DIR=$(pwd)

# Create package directory
mkdir -p "$PACKAGE_DIR"

echo "📁 Setting up package structure..."

# Copy essential files for deployment
cp -r ../backend "$PACKAGE_DIR/"
cp -r ../frontend "$PACKAGE_DIR/"
cp -r . "$PACKAGE_DIR/deploy/"

# Clean up unnecessary files
echo "🧹 Cleaning package..."
find "$PACKAGE_DIR" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find "$PACKAGE_DIR" -name "*.pyc" -delete 2>/dev/null || true
find "$PACKAGE_DIR" -name ".DS_Store" -delete 2>/dev/null || true
find "$PACKAGE_DIR" -name "node_modules" -type d -exec rm -rf {} + 2>/dev/null || true
rm -rf "$PACKAGE_DIR/backend/instance/" 2>/dev/null || true
rm -rf "$PACKAGE_DIR/frontend/dist/" 2>/dev/null || true

# Create deployment instructions
cat > "$PACKAGE_DIR/DEPLOY_INSTRUCTIONS.txt" << 'EOF'
🚀 StorySpark Cloud Deployment Instructions

QUICK START:
1. Upload this entire folder to your VM: /opt/storyspark/
2. cd /opt/storyspark/deploy/
3. chmod +x setup_vm.sh && sudo ./setup_vm.sh
4. Add your Google service account JSON to: deploy/secrets/service-account.json
5. Copy deploy/.env.example to deploy/.env and fill in your values
6. chmod +x deploy_cloud.sh && ./deploy_cloud.sh
7. Your app will be running at http://YOUR_VM_IP:5001

DETAILED GUIDE:
See deploy/CLOUD_DEPLOYMENT_GUIDE.md for complete instructions.

REQUIREMENTS:
- Google Cloud VM (Ubuntu 20.04+)
- Docker and Docker Compose (installed by setup_vm.sh)
- Google service account with TTS API access
- Gemini API key

SUPPORT:
Check logs with: docker-compose logs -f
Health check: curl http://localhost:5001/health
EOF

# Create a quick setup script
cat > "$PACKAGE_DIR/QUICK_DEPLOY.sh" << 'EOF'
#!/bin/bash
echo "🚀 StorySpark Quick Deploy"
echo "This script will set up StorySpark on a fresh Ubuntu VM"
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "⚠️  Don't run this script as root. Run as a regular user with sudo access."
    exit 1
fi

# Check if we're on the right system
if ! command -v apt-get &> /dev/null; then
    echo "❌ This script is designed for Ubuntu/Debian systems"
    exit 1
fi

echo "📍 Current directory: $(pwd)"
echo "📂 Contents:"
ls -la

# Run VM setup if Docker isn't installed
if ! command -v docker &> /dev/null; then
    echo "🐳 Installing Docker and dependencies..."
    cd deploy/
    chmod +x setup_vm.sh
    sudo ./setup_vm.sh
    echo "✅ VM setup completed"
    echo ""
    echo "⚠️  IMPORTANT: You need to log out and log back in for Docker permissions to take effect"
    echo "   After logging back in, run this script again to continue deployment"
    exit 0
fi

# Check for required files
if [ ! -f "deploy/secrets/service-account.json" ]; then
    echo "❌ Missing: deploy/secrets/service-account.json"
    echo "📝 Please upload your Google service account JSON file to:"
    echo "   $(pwd)/deploy/secrets/service-account.json"
    exit 1
fi

if [ ! -f "deploy/.env" ]; then
    echo "📝 Creating environment file..."
    cp deploy/.env.example deploy/.env
    echo "⚠️  Please edit deploy/.env with your actual values:"
    echo "   - GEMINI_API_KEY"
    echo "   - GOOGLE_CLOUD_PROJECT"
    echo "   - SECRET_KEY (generate a random string)"
    echo ""
    echo "   Then run this script again."
    exit 1
fi

# Deploy
echo "🚀 Deploying StorySpark..."
cd deploy/
chmod +x deploy_cloud.sh
./deploy_cloud.sh

echo "🎉 Deployment completed!"
echo "🌐 Access your app at: http://$(curl -s ifconfig.me):5001"
EOF

chmod +x "$PACKAGE_DIR/QUICK_DEPLOY.sh"

# Create archive
echo "📦 Creating deployment archive..."
cd /tmp
tar -czf "$PACKAGE_NAME.tar.gz" "$PACKAGE_NAME"

# Move to original directory
mv "$PACKAGE_NAME.tar.gz" "$CURRENT_DIR/"

# Cleanup
rm -rf "$PACKAGE_DIR"

echo "✅ Deployment package created: $PACKAGE_NAME.tar.gz"
echo ""
echo "📋 Next steps:"
echo "1. Upload $PACKAGE_NAME.tar.gz to your Google Cloud VM"
echo "2. Extract: tar -xzf $PACKAGE_NAME.tar.gz"
echo "3. cd $PACKAGE_NAME && ./QUICK_DEPLOY.sh"
echo ""
echo "📖 Or follow the detailed guide in CLOUD_DEPLOYMENT_GUIDE.md"
echo ""
echo "🎯 Your StorySpark PWA will be ready in minutes!"
