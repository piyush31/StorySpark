#!/bin/bash

# StorySpark VM Setup Script for Google Cloud Linux
# Run this script as root or with sudo privileges

set -e

echo "🚀 Setting up StorySpark on Google Cloud VM..."

# Update system
echo "📦 Updating system packages..."
apt-get update && apt-get upgrade -y

# Install Docker and Docker Compose
echo "🐳 Installing Docker..."
apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker repository
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io

# Install Docker Compose
echo "🔧 Installing Docker Compose..."
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Start and enable Docker
systemctl start docker
systemctl enable docker

# Install additional utilities
echo "🛠️ Installing additional utilities..."
apt-get install -y git curl wget unzip htop ufw

# Configure firewall
echo "🔒 Configuring firewall..."
ufw --force enable
ufw allow 22/tcp   # SSH
ufw allow 80/tcp   # HTTP
ufw allow 443/tcp  # HTTPS
ufw allow 5001/tcp # StorySpark direct access

# Create app user
echo "👤 Creating application user..."
useradd -m -s /bin/bash storyspark
usermod -aG docker storyspark

# Create application directories
echo "📁 Setting up application directories..."
mkdir -p /opt/storyspark
mkdir -p /opt/storyspark/secrets
mkdir -p /opt/storyspark/logs
mkdir -p /opt/storyspark/ssl
chown -R storyspark:storyspark /opt/storyspark

# Install Node.js (for potential frontend builds)
echo "📦 Installing Node.js..."
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt-get install -y nodejs

echo "✅ VM setup completed!"
echo "📋 Next steps:"
echo "1. Upload your StorySpark code to /opt/storyspark/"
echo "2. Upload your Google service account JSON to /opt/storyspark/secrets/"
echo "3. Run the deployment script: /opt/storyspark/deploy_cloud.sh"
echo "4. Your app will be available at http://YOUR_VM_IP"