#!/bin/bash
# Quick Cloud Deployment Options for StorySpark PWA

set -e

echo "🚀 StorySpark Cloud Deployment Options"
echo "======================================"
echo ""

echo "Choose your deployment method:"
echo "1) Google Cloud VM (Full control, Docker)"
echo "2) Google Cloud Run (Serverless, auto-scaling)"
echo "3) Google App Engine (Managed, traditional)"
echo ""

read -p "Enter your choice (1-3): " choice

case $choice in
  1)
    echo ""
    echo "🖥️  Google Cloud VM Deployment"
    echo "==============================="
    echo ""
    echo "Prerequisites:"
    echo "- Google Cloud project with billing enabled"
    echo "- gcloud CLI configured"
    echo "- Service account JSON file"
    echo ""
    
    read -p "Enter your project ID: " PROJECT_ID
    read -p "Enter your preferred zone (default: us-central1-a): " ZONE
    ZONE=${ZONE:-us-central1-a}
    
    echo ""
    echo "Creating VM..."
    gcloud compute instances create storyspark-vm \
      --project=$PROJECT_ID \
      --zone=$ZONE \
      --machine-type=e2-medium \
      --image-family=ubuntu-2004-lts \
      --image-project=ubuntu-os-cloud \
      --boot-disk-size=30GB \
      --tags=http-server,https-server \
      --metadata=startup-script='#!/bin/bash
        apt-get update
        apt-get install -y docker.io docker-compose
        usermod -aG docker $USER'
    
    echo ""
    echo "Uploading deployment package..."
    gcloud compute scp storyspark-deployment-*.tar.gz storyspark-vm:/tmp/ --zone=$ZONE --project=$PROJECT_ID
    
    echo ""
    echo "Next steps:"
    echo "1. SSH to your VM: gcloud compute ssh storyspark-vm --zone=$ZONE --project=$PROJECT_ID"
    echo "2. Extract and deploy: cd /tmp && tar -xzf storyspark-deployment-*.tar.gz && cd storyspark-deployment-* && ./QUICK_DEPLOY.sh"
    echo "3. Configure your .env file with API keys"
    echo "4. Access your app at: http://$(gcloud compute instances describe storyspark-vm --zone=$ZONE --project=$PROJECT_ID --format='value(networkInterfaces[0].accessConfigs[0].natIP)'):5001"
    ;;
    
  2)
    echo ""
    echo "☁️  Google Cloud Run Deployment"
    echo "==============================="
    echo ""
    echo "Prerequisites:"
    echo "- Google Cloud project with Cloud Run API enabled"
    echo "- Cloud Build API enabled"
    echo "- gcloud CLI configured"
    echo ""
    
    read -p "Enter your project ID: " PROJECT_ID
    
    echo ""
    echo "Building frontend..."
    cd ../frontend
    npm ci
    npm run build
    cp -r dist/* ../backend/static/
    cd ../deploy
    
    echo ""
    echo "Submitting build to Cloud Build..."
    gcloud builds submit --config=cloudbuild.yaml --project=$PROJECT_ID ..
    
    echo ""
    echo "Your app will be available at:"
    echo "https://storyspark-$(echo $PROJECT_ID | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9-]//g')-uc.a.run.app"
    ;;
    
  3)
    echo ""
    echo "🎯 Google App Engine Deployment"
    echo "==============================="
    echo ""
    echo "Prerequisites:"
    echo "- Google Cloud project with App Engine API enabled"
    echo "- gcloud CLI configured"
    echo ""
    
    read -p "Enter your project ID: " PROJECT_ID
    
    echo ""
    echo "Building frontend..."
    cd ../frontend
    npm ci
    npm run build
    cp -r dist/* ../backend/static/
    cd ../deploy
    
    echo ""
    echo "Deploying to App Engine..."
    gcloud app deploy app.yaml --project=$PROJECT_ID --quiet
    
    echo ""
    echo "Your app will be available at:"
    echo "https://$PROJECT_ID.appspot.com"
    ;;
    
  *)
    echo "Invalid choice. Exiting."
    exit 1
    ;;
esac

echo ""
echo "✅ Deployment initiated successfully!"
echo ""
echo "Important: Don't forget to:"
echo "1. Set up your environment variables (API keys)"
echo "2. Configure your service account credentials"
echo "3. Test all functionality after deployment"
