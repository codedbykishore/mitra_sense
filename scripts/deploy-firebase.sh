#!/bin/bash

# MITRA Sense Firebase Hosting + Cloud Run Backend Deployment
# Frontend: Firebase Hosting (Clean URL: https://ordinal-rig-470915-d0.web.app)
# Backend: Cloud Run (Stable URL: https://mitra-api-751581682843.us-central1.run.app)

set -e

# Configuration
export PROJECT_ID="ordinal-rig-470915-d0"
export FIREBASE_PROJECT_ID="mitrasense"  # Custom Firebase project name - CLEAN!
export REGION="us-central1"
export AR_REGION="us-central1"
export REPOSITORY_NAME="mitra-repo"
export BACKEND_SERVICE_NAME="mitra-api"

# Environment variables (Update these if needed)
export GOOGLE_CLIENT_ID="751581682843-bnfs1qgkma2kl6cbu645jf4ct57il748.apps.googleusercontent.com"
export GOOGLE_CLIENT_SECRET="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"
export SECRET_KEY="Vh3Djw7wXvM4t8rPxkU0oX2dQeR9sB5yFuP6vX1tKjW2hZ9lRm8pA4nDqT7bF6yC"
export CORPUS_NAME="projects/ordinal-rig-470915-d0/locations/us-east4/ragCorpora/6917529027641081856"

echo "🚀 Starting MITRA Sense deployment with Firebase Hosting..."
echo "Google Cloud Project: $PROJECT_ID"
echo "Firebase Project: $FIREBASE_PROJECT_ID"
echo "Backend Service: $BACKEND_SERVICE_NAME"

# Step 1: Set up Google Cloud
echo "📋 Setting up Google Cloud configuration..."
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable firebase.googleapis.com

# Firebase project 'mitrasense' already exists and configured
echo "🔥 Using Firebase project: $FIREBASE_PROJECT_ID (https://mitrasense.web.app)"

# Configure Docker for Artifact Registry
echo "🔧 Configuring Docker for Artifact Registry..."
gcloud auth configure-docker ${AR_REGION}-docker.pkg.dev

# Create/update secrets
echo "🔐 Creating/updating GCP service account credentials..."
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

# Step 2: Build and Deploy Backend to Cloud Run
echo "🏗️  Building backend Docker image..."
docker build -t ${AR_REGION}-docker.pkg.dev/$PROJECT_ID/$REPOSITORY_NAME/$BACKEND_SERVICE_NAME:latest .

echo "📤 Pushing backend image to Artifact Registry..."
docker push ${AR_REGION}-docker.pkg.dev/$PROJECT_ID/$REPOSITORY_NAME/$BACKEND_SERVICE_NAME:latest

# Deploy backend with stable URL
echo "🚀 Deploying backend to Cloud Run with stable URL..."
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
  --set-env-vars GOOGLE_APPLICATION_CREDENTIALS=/secrets/secrets.json,GOOGLE_PROJECT_ID="$PROJECT_ID",GOOGLE_CLIENT_ID="$GOOGLE_CLIENT_ID",GOOGLE_CLIENT_SECRET="$GOOGLE_CLIENT_SECRET",SECRET_KEY="$SECRET_KEY",CORPUS_NAME="$CORPUS_NAME",REDIRECT_URI="PLACEHOLDER_BACKEND_URL/auth/google/callback",FRONTEND_BASE_URL="https://$FIREBASE_PROJECT_ID.web.app" \
  --set-secrets /secrets/secrets.json=mitra-secrets:latest

export BACKEND_URL=$(gcloud run services describe $BACKEND_SERVICE_NAME --region $REGION --format 'value(status.url)')
echo "✅ Backend API deployed at: $BACKEND_URL"

# Step 3: Build and Deploy Frontend to Firebase Hosting  
echo "🏗️  Building frontend for Firebase Hosting..."
cd frontend

# Set backend URL for build
export NEXT_PUBLIC_BACKEND_URL=$BACKEND_URL
echo "Building with backend URL: $NEXT_PUBLIC_BACKEND_URL"

# Build the Next.js app for static export
npm run build

# Go back to root for Firebase deployment
cd ..

# Deploy to Firebase Hosting from root directory
echo "🚀 Deploying frontend to Firebase Hosting..."
firebase deploy --only hosting --project $FIREBASE_PROJECT_ID

# Get Firebase URL with custom project name
export FIREBASE_URL="https://$FIREBASE_PROJECT_ID.web.app"
echo "✅ Frontend deployed at: $FIREBASE_URL"

# Step 4: Update backend with correct OAuth redirect URI
echo "🔄 Updating backend with Firebase redirect URI..."
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
  --set-env-vars GOOGLE_APPLICATION_CREDENTIALS=/secrets/secrets.json,GOOGLE_PROJECT_ID="$PROJECT_ID",GOOGLE_CLIENT_ID="$GOOGLE_CLIENT_ID",GOOGLE_CLIENT_SECRET="$GOOGLE_CLIENT_SECRET",SECRET_KEY="$SECRET_KEY",CORPUS_NAME="$CORPUS_NAME",REDIRECT_URI="$BACKEND_URL/auth/google/callback",FRONTEND_BASE_URL="$FIREBASE_URL" \
  --set-secrets /secrets/secrets.json=mitra-secrets:latest

cd ..

cd ..

echo ""
echo "🎉 Deployment Complete with Clean URLs!"
echo "================================"
echo "Frontend: $FIREBASE_URL (Firebase Hosting)"
echo "Backend:  $BACKEND_URL (Cloud Run)"
echo "================================"
echo ""
echo "✨ Your app now has a beautiful, branded URL!"
echo "🎯 Frontend: https://mitrasense.web.app"
echo ""
echo "🧪 Testing endpoints..."

# Test backend health
echo "Testing backend health..."
if curl -f "$BACKEND_URL/health" >/dev/null 2>&1; then
    echo "✅ Backend health check passed"
else
    echo "❌ Backend health check failed"
fi

# Test Firebase hosting
echo "Testing Firebase hosting..."
if curl -s -I "$FIREBASE_URL" | head -n1 | grep -q "200"; then
    echo "✅ Firebase hosting check passed"
else
    echo "❌ Firebase hosting check failed"
fi

echo ""
echo "📋 IMPORTANT: OAuth Configuration Required"
echo "⚠️  Update Google Cloud Console OAuth settings:"
echo "1. Go to: https://console.cloud.google.com/apis/credentials"
echo "2. Find OAuth 2.0 Client ID: $GOOGLE_CLIENT_ID"
echo "3. Add this redirect URI: $BACKEND_URL/auth/google/callback"
echo "4. Save the changes"
echo ""
echo "🔍 URLs for testing:"
echo "• Frontend App: $FIREBASE_URL"
echo "• Backend API: $BACKEND_URL/api/v1"
echo "• Backend Docs: $BACKEND_URL/docs"
echo ""
echo "✅ Your app now has professional, stable URLs!"
echo "✅ Frontend URL will NEVER change: $FIREBASE_URL"
echo "✅ Backend URL will NEVER change: $BACKEND_URL"
