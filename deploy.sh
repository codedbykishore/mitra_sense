#!/bin/bash

# MITRA Sense Complete Deployment Script for Google Cloud Run
# Project: ordinal-rig-470915-d0
# 
# This script deploys both backend and frontend services to Google Cloud Run
# with proper OAuth configuration and environment variables.

set -e  # Exit on any error

# Configuration
export PROJECT_ID="ordinal-rig-470915-d0"
export REGION="us-central1"
export AR_REGION="us-central1"
export REPOSITORY_NAME="mitra-repo"
export BACKEND_SERVICE_NAME="api"
export FRONTEND_SERVICE_NAME="app"

# Environment variables (Update these as needed)
export GOOGLE_CLIENT_ID="751581682843-bnfs1qgkma2kl6cbu645jf4ct57il748.apps.googleusercontent.com"
export GOOGLE_CLIENT_SECRET="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"
export SECRET_KEY="Vh3Djw7wXvM4t8rPxkU0oX2dQeR9sB5yFuP6vX1tKjW2hZ9lRm8pA4nDqT7bF6yC"
export CORPUS_NAME="projects/ordinal-rig-470915-d0/locations/us-east4/ragCorpora/6917529027641081856"

echo "🚀 Starting MITRA Sense deployment to Google Cloud Run..."
echo "Project: $PROJECT_ID"
echo "Region: $REGION"

# Step 1: Set up Google Cloud
echo "📋 Setting up Google Cloud configuration..."
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable secretmanager.googleapis.com

# Step 1.5: Create Artifact Registry repository
echo "📦 Creating Artifact Registry repository..."
if gcloud artifacts repositories describe $REPOSITORY_NAME --location=$AR_REGION >/dev/null 2>&1; then
    echo "Repository already exists, skipping creation..."
else
    echo "Creating new repository..."
    gcloud artifacts repositories create $REPOSITORY_NAME \
        --repository-format=docker \
        --location=$AR_REGION \
        --description="MITRA Sense Docker images"
fi

# Configure Docker for Artifact Registry
echo "🔧 Configuring Docker for Artifact Registry..."
gcloud auth configure-docker ${AR_REGION}-docker.pkg.dev

# Step 2: Create secret for GCP credentials
echo "🔐 Creating secret for GCP service account credentials..."
if gcloud secrets describe mitra-secrets >/dev/null 2>&1; then
    echo "Secret already exists, updating..."
    gcloud secrets versions add mitra-secrets --data-file=secrets/secrets.json
else
    echo "Creating new secret..."
    gcloud secrets create mitra-secrets --data-file=secrets/secrets.json
fi

# Grant Cloud Run access to the secret
echo "🔑 Granting Cloud Run access to secrets..."
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')
gcloud secrets add-iam-policy-binding mitra-secrets \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

# Step 3: Build and deploy backend
echo "🏗️  Building backend Docker image..."
docker build -t ${AR_REGION}-docker.pkg.dev/$PROJECT_ID/$REPOSITORY_NAME/$BACKEND_SERVICE_NAME:latest .

echo "📤 Pushing backend image to Artifact Registry..."
docker push ${AR_REGION}-docker.pkg.dev/$PROJECT_ID/$REPOSITORY_NAME/$BACKEND_SERVICE_NAME:latest

echo "🚀 Deploying backend to Cloud Run with consistent URL..."
gcloud run deploy $BACKEND_SERVICE_NAME \
  --image ${AR_REGION}-docker.pkg.dev/$PROJECT_ID/$REPOSITORY_NAME/$BACKEND_SERVICE_NAME:latest \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --port 8000 \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300s \
  --concurrency 80 \
  --max-instances 10 \
  --set-env-vars GOOGLE_APPLICATION_CREDENTIALS=/secrets/secrets.json,GOOGLE_PROJECT_ID="$PROJECT_ID",GOOGLE_CLIENT_ID="$GOOGLE_CLIENT_ID",GOOGLE_CLIENT_SECRET="$GOOGLE_CLIENT_SECRET",SECRET_KEY="$SECRET_KEY",CORPUS_NAME="$CORPUS_NAME",REDIRECT_URI="PLACEHOLDER_FRONTEND_URL/auth/google/callback" \
  --set-secrets /secrets/secrets.json=mitra-secrets:latest

# Get backend URL - this should now be consistent
export BACKEND_URL=$(gcloud run services describe $BACKEND_SERVICE_NAME --region $REGION --format 'value(status.url)')
echo "✅ Backend deployed at: $BACKEND_URL"

# Step 4: Build and deploy frontend
echo "🏗️  Building frontend Docker image..."
cd frontend

# Use the working Dockerfile.fast for reliable builds with npm
echo "Using Dockerfile.fast for stable npm-based builds..."
docker build -f Dockerfile.fast -t ${AR_REGION}-docker.pkg.dev/$PROJECT_ID/$REPOSITORY_NAME/$FRONTEND_SERVICE_NAME:latest \
  --build-arg NEXT_PUBLIC_BACKEND_URL=$BACKEND_URL .

echo "📤 Pushing frontend image to Artifact Registry..."
docker push ${AR_REGION}-docker.pkg.dev/$PROJECT_ID/$REPOSITORY_NAME/$FRONTEND_SERVICE_NAME:latest

echo "🚀 Deploying frontend to Cloud Run with consistent URL..."
gcloud run deploy $FRONTEND_SERVICE_NAME \
  --image ${AR_REGION}-docker.pkg.dev/$PROJECT_ID/$REPOSITORY_NAME/$FRONTEND_SERVICE_NAME:latest \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --port 3000 \
  --memory 1Gi \
  --cpu 1 \
  --timeout 60s \
  --concurrency 100 \
  --max-instances 5 \
  --set-env-vars NEXT_PUBLIC_BACKEND_URL=$BACKEND_URL

# Get frontend URL - this should now be consistent
export FRONTEND_URL=$(gcloud run services describe $FRONTEND_SERVICE_NAME --region $REGION --format 'value(status.url)')
echo "✅ Frontend deployed at: $FRONTEND_URL"

# Step 5: Update backend with correct redirect URI
echo "🔄 Updating backend with correct OAuth redirect URI..."
gcloud run deploy $BACKEND_SERVICE_NAME \
  --image ${AR_REGION}-docker.pkg.dev/$PROJECT_ID/$REPOSITORY_NAME/$BACKEND_SERVICE_NAME:latest \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --port 8000 \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300s \
  --concurrency 80 \
  --max-instances 10 \
  --set-env-vars GOOGLE_APPLICATION_CREDENTIALS=/secrets/secrets.json,GOOGLE_PROJECT_ID="$PROJECT_ID",GOOGLE_CLIENT_ID="$GOOGLE_CLIENT_ID",GOOGLE_CLIENT_SECRET="$GOOGLE_CLIENT_SECRET",SECRET_KEY="$SECRET_KEY",CORPUS_NAME="$CORPUS_NAME",REDIRECT_URI="$FRONTEND_URL/auth/google/callback" \
  --set-secrets /secrets/secrets.json=mitra-secrets:latest

cd ..

echo ""
echo "🎉 Deployment Complete!"
echo "================================"
echo "Backend URL:  $BACKEND_URL"
echo "Frontend URL: $FRONTEND_URL"
echo "================================"
echo ""
echo "🧪 Testing endpoints..."

# Test backend health
echo "Testing backend health..."
if curl -f "$BACKEND_URL/health" >/dev/null 2>&1; then
    echo "✅ Backend health check passed"
else
    echo "❌ Backend health check failed"
fi

# Test frontend connectivity
echo "Testing frontend connectivity..."
if curl -s -I "$FRONTEND_URL" | head -n1 | grep -q "200"; then
    echo "✅ Frontend connectivity check passed"
else
    echo "❌ Frontend connectivity check failed"
fi

# Test OAuth initiation endpoint
echo "Testing OAuth initiation endpoint..."
if curl -s -I "$BACKEND_URL/google/login" | head -n1 | grep -q "405\|307\|302"; then
    echo "✅ OAuth endpoint is accessible"
else
    echo "❌ OAuth endpoint test failed"
fi

# Verify redirect URI configuration
echo "Verifying redirect URI configuration..."
CONFIGURED_REDIRECT=$(gcloud run services describe $BACKEND_SERVICE_NAME --region $REGION --format="value(spec.template.spec.template.spec.containers[0].env[?(@.name=='REDIRECT_URI')].value)")
if [ "$CONFIGURED_REDIRECT" = "$FRONTEND_URL/auth/google/callback" ]; then
    echo "✅ Redirect URI correctly configured: $CONFIGURED_REDIRECT"
else
    echo "❌ Redirect URI configuration mismatch. Expected: $FRONTEND_URL/auth/google/callback, Got: $CONFIGURED_REDIRECT"
fi

echo ""
echo "🔍 Manual Testing URLs:"
echo "• Frontend App: $FRONTEND_URL"
echo "• Backend API: $BACKEND_URL/api/v1"
echo "• Backend Docs: $BACKEND_URL/docs"
echo ""
echo "� Manual Testing URLs:"
echo "• Frontend App: $FRONTEND_URL"
echo "• Backend API: $BACKEND_URL/api/v1"
echo "• Backend Docs: $BACKEND_URL/docs"
echo ""
echo "📋 OAuth Configuration Required:"
echo "⚠️  IMPORTANT: Update Google Cloud Console OAuth settings:"
echo "1. Go to: https://console.cloud.google.com/apis/credentials"
echo "2. Find OAuth 2.0 Client ID: $GOOGLE_CLIENT_ID"
echo "3. Add this redirect URI: $FRONTEND_URL/auth/google/callback"
echo "4. Save the changes"
echo ""
echo "Current OAuth redirect URI: $FRONTEND_URL/auth/google/callback"
echo ""
echo "�📋 Next Steps:"
echo "1. Visit $FRONTEND_URL in your browser"
echo "2. Test Google OAuth login functionality"
echo "3. Complete user onboarding flow"
echo "4. Test chat and voice features"
echo "5. Monitor logs with: gcloud logs tail --service=$BACKEND_SERVICE_NAME --region=$REGION"
echo ""
echo "🔧 Troubleshooting Commands:"
echo "• Backend logs: gcloud logs tail --service=$BACKEND_SERVICE_NAME --region=$REGION"
echo "• Frontend logs: gcloud logs tail --service=$FRONTEND_SERVICE_NAME --region=$REGION"
echo "• Backend env vars: gcloud run services describe $BACKEND_SERVICE_NAME --region $REGION --format='value(spec.template.spec.template.spec.containers[0].env[].name,spec.template.spec.template.spec.containers[0].env[].value)'"
echo ""
echo "✅ URLs should now remain consistent across deployments!"
echo ""
echo "🌐 Want a cleaner frontend URL? Deploy to Firebase Hosting instead:"
echo "• Frontend: https://ordinal-rig-470915-d0.web.app (or custom: https://mitra-sense.web.app)"
echo "• Backend: $BACKEND_URL (Cloud Run API)"
echo ""
echo "To switch to Firebase Hosting for frontend:"
echo "1. npm install -g firebase-tools"
echo "2. firebase login"
echo "3. firebase init hosting"
echo "4. npm run build"
echo "5. firebase deploy"
echo ""

# Optional: Custom Domain Mapping
echo "🌐 Custom Domain Setup (Optional)..."
echo "To use custom domains like mitra-sense.yourdomain.com:"
echo ""
echo "1. Purchase a domain from any domain registrar"
echo "2. Add these DNS records in your domain provider:"
echo "   - Frontend: CNAME mitra-sense -> ghs.googlehosted.com"
echo "   - Backend: CNAME api -> ghs.googlehosted.com"
echo "3. Run these commands to map domains:"
echo ""
echo "   # Map frontend"
echo "   gcloud run domain-mappings create \\"
echo "     --service $FRONTEND_SERVICE_NAME \\"
echo "     --domain mitra-sense.yourdomain.com \\"
echo "     --region $REGION"
echo ""
echo "   # Map backend API"
echo "   gcloud run domain-mappings create \\"
echo "     --service $BACKEND_SERVICE_NAME \\"
echo "     --domain api.yourdomain.com \\"
echo "     --region $REGION"
echo ""
echo "4. Update OAuth redirect URI to: https://mitra-sense.yourdomain.com/auth/google/callback"
echo ""
