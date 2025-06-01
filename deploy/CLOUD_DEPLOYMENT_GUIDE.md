# 🚀 StorySpark Cloud Deployment Guide

Complete guide for deploying StorySpark PWA to Google Cloud Platform VM.

## 📋 Prerequisites

1. **Google Cloud VM** (Ubuntu 20.04+ recommended)
2. **Google Service Account** with the following APIs enabled:
   - Text-to-Speech API
   - Gemini API access
3. **Domain name** (optional, for SSL)
4. **API Keys**:
   - Gemini API key
   - Google Cloud TTS credentials

## 🎯 Quick Start (5 minutes)

### 1. Prepare Your VM

```bash
# SSH into your Google Cloud VM
gcloud compute ssh your-vm-name --zone=your-zone

# Download and run the setup script
curl -fsSL https://raw.githubusercontent.com/your-repo/StorySpark/main/deploy/setup_vm.sh | sudo bash
```

### 2. Upload Your Code

```bash
# From your local machine, upload the code
scp -r /Users/piyush/code/StorySpark your-vm-user@your-vm-ip:/opt/storyspark/

# Or clone from Git
git clone https://github.com/your-repo/StorySpark.git /opt/storyspark/
```

### 3. Configure Secrets

```bash
# Upload your Google service account JSON
scp your-service-account.json your-vm-user@your-vm-ip:/opt/storyspark/deploy/secrets/service-account.json

# Create environment file
cd /opt/storyspark/deploy
cp .env.example .env
nano .env  # Edit with your actual values
```

### 4. Deploy

```bash
cd /opt/storyspark/deploy
chmod +x deploy_cloud.sh
./deploy_cloud.sh
```

## 📁 Directory Structure on VM

```
/opt/storyspark/
├── backend/           # Backend Flask app
├── frontend/          # React PWA
├── deploy/            # Deployment files
│   ├── secrets/       # Service account & keys
│   ├── ssl/          # SSL certificates (optional)
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── deploy_cloud.sh
└── logs/             # Application logs
```

## 🔧 Detailed Setup Steps

### Step 1: VM Preparation

#### Option A: Automated Setup
```bash
curl -fsSL https://path-to-your-setup-script/setup_vm.sh | sudo bash
```

#### Option B: Manual Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Configure firewall
sudo ufw enable
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw allow 5001/tcp # App port
```

### Step 2: Code Deployment

#### From Local Machine:
```bash
# Archive and upload
tar -czf storyspark.tar.gz -C /Users/piyush/code StorySpark
scp storyspark.tar.gz user@vm-ip:/opt/
ssh user@vm-ip "cd /opt && tar -xzf storyspark.tar.gz && mv StorySpark storyspark"
```

#### From Git Repository:
```bash
ssh user@vm-ip
cd /opt
git clone https://github.com/your-username/StorySpark.git storyspark
```

### Step 3: Environment Configuration

```bash
cd /opt/storyspark/deploy

# Create secrets directory
mkdir -p secrets

# Upload your Google service account JSON
# (Upload via SCP or create manually)
nano secrets/service-account.json

# Configure environment
cp .env.example .env
nano .env
```

#### Required .env Variables:
```env
FLASK_ENV=production
SECRET_KEY=your-random-secret-key-here
GEMINI_API_KEY=your-gemini-api-key
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/service-account.json
```

### Step 4: Deploy Application

```bash
cd /opt/storyspark/deploy
chmod +x deploy_cloud.sh
./deploy_cloud.sh
```

## 🔒 Security Configuration

### Firewall Rules
```bash
# Basic security
sudo ufw --force enable
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

### SSL/HTTPS Setup (Optional)

#### Using Let's Encrypt:
```bash
# Install Certbot
sudo apt install snapd
sudo snap install --classic certbot

# Get certificate
sudo certbot certonly --standalone -d your-domain.com

# Copy certificates to deployment
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem /opt/storyspark/deploy/ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem /opt/storyspark/deploy/ssl/key.pem
sudo chown -R storyspark:storyspark /opt/storyspark/deploy/ssl/
```

#### Enable HTTPS in Docker Compose:
```bash
# Uncomment nginx service in docker-compose.yml
# Update nginx.conf with your domain
docker-compose --profile with-nginx up -d
```

## 📊 Monitoring & Maintenance

### View Application Status
```bash
cd /opt/storyspark/deploy
docker-compose ps
```

### View Logs
```bash
# All logs
docker-compose logs -f

# Specific service
docker-compose logs -f storyspark

# Last 50 lines
docker-compose logs --tail=50
```

### Health Check
```bash
curl http://localhost:5001/health
curl http://your-domain.com/health
```

### Update Application
```bash
cd /opt/storyspark
git pull origin main
cd deploy
docker-compose up -d --build
```

## 🚨 Troubleshooting

### Common Issues

#### Port Already in Use
```bash
sudo netstat -tulpn | grep :5001
sudo systemctl stop service-using-port
```

#### Docker Permission Issues
```bash
sudo usermod -aG docker $USER
newgrp docker
```

#### Service Account Issues
```bash
# Verify file exists and has correct permissions
ls -la /opt/storyspark/deploy/secrets/
cat /opt/storyspark/deploy/secrets/service-account.json | jq .
```

#### Memory Issues
```bash
# Check system resources
free -h
df -h
docker system prune -f
```

### Log Locations
- Application logs: `/opt/storyspark/logs/`
- Docker logs: `docker-compose logs`
- System logs: `/var/log/syslog`

## 🔄 Backup & Recovery

### Backup Script
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
tar -czf /opt/backups/storyspark_${DATE}.tar.gz \
  /opt/storyspark/backend/data \
  /opt/storyspark/deploy/secrets \
  /opt/storyspark/deploy/.env
```

### Recovery
```bash
# Restore from backup
tar -xzf /opt/backups/storyspark_20250601_120000.tar.gz -C /
cd /opt/storyspark/deploy
docker-compose up -d
```

## 📈 Performance Optimization

### For High Traffic
```bash
# Increase worker count in docker-compose.yml
# Add nginx caching
# Enable gzip compression
# Set up CDN for static assets
```

### Resource Monitoring
```bash
# Install monitoring tools
sudo apt install htop iotop
docker stats
```

## 🎉 Success Checklist

- [ ] VM setup completed
- [ ] Code uploaded and extracted
- [ ] Service account JSON configured
- [ ] Environment variables set
- [ ] Application deployed and running
- [ ] Health check passes
- [ ] External access working
- [ ] SSL configured (optional)
- [ ] Monitoring set up
- [ ] Backup strategy in place

## 📞 Support

If you encounter issues:
1. Check the logs: `docker-compose logs -f`
2. Verify environment variables
3. Test API endpoints manually
4. Check firewall rules
5. Verify Google Cloud credentials

Your StorySpark PWA should now be running at: **http://your-vm-ip:5001**

---

**🎯 Next Steps:**
- Set up monitoring and alerts
- Configure automated backups
- Implement CI/CD pipeline
- Scale with load balancer if needed
