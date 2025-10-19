# MITRA Sense - Step by Step Deployment Commands
# Project: ordinal-rig-470915-d0

## Prerequisites Setup
```bash
# Set project configuration
export PROJECT_ID="ordinal-rig-470915-d0"
gcloud config set project $PROJECT_ID

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com  
gcloud services enable cloudbuild.googleapis.com
gcloud services enable secretmanager.googleapis.com
```

## Step 1: Create GCP Secret
```bash
# Create secret from your secrets.json file
gcloud secrets create mitra-secrets --data-file=secrets/secrets.json

# Grant Cloud Run access to the secret
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')
gcloud secrets add-iam-policy-binding mitra-secrets \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

## Step 2: Build and Deploy Backend
```bash
# Build backend image
docker build -t gcr.io/ordinal-rig-470915-d0/mitra-backend:latest .

# Push to Google Container Registry
docker push gcr.io/ordinal-rig-470915-d0/mitra-backend:latest

# Deploy backend to Cloud Run
gcloud run deploy mitra-backend \
  --image gcr.io/ordinal-rig-470915-d0/mitra-backend:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8000 \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300s \
  --concurrency 80 \
  --max-instances 10 \
  --set-env-vars GOOGLE_APPLICATION_CREDENTIALS=/secrets/secrets.json \
  --set-env-vars GOOGLE_CLIENT_ID="751581682843-bnfs1qgkma2kl6cbu645jf4ct57il748.apps.googleusercontent.com" \
  --set-env-vars GOOGLE_CLIENT_SECRET="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" \
  --set-env-vars SECRET_KEY="Vh3Djw7wXvM4t8rPxkU0oX2dQeR9sB5yFuP6vX1tKjW2hZ9lRm8pA4nDqT7bF6yC" \
  --set-env-vars CORPUS_NAME="projects/ordinal-rig-470915-d0/locations/us-east4/ragCorpora/6917529027641081856" \
  --set-env-vars REDIRECT_URI="PLACEHOLDER_WILL_UPDATE_LATER"

# Mount secrets file as volume
gcloud run services update mitra-backend \
  --region us-central1 \
  --update-secrets /secrets/secrets.json=mitra-secrets:latest
```

## Step 3: Get Backend URL and Build Frontend
```bash
# Get backend URL
export BACKEND_URL=$(gcloud run services describe mitra-backend --region us-central1 --format 'value(status.url)')
echo "Backend URL: $BACKEND_URL"

# Build frontend image with backend URL
cd frontend
docker build -t gcr.io/ordinal-rig-470915-d0/mitra-frontend:latest \
  --build-arg NEXT_PUBLIC_BACKEND_URL=$BACKEND_URL .

# Push frontend image
docker push gcr.io/ordinal-rig-470915-d0/mitra-frontend:latest
```

## Step 4: Deploy Frontend
```bash
# Deploy frontend
gcloud run deploy mitra-frontend \
  --image gcr.io/ordinal-rig-470915-d0/mitra-frontend:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 3000 \
  --memory 1Gi \
  --cpu 1 \
  --timeout 60s \
  --concurrency 100 \
  --max-instances 5 \
  --set-env-vars NEXT_PUBLIC_BACKEND_URL=$BACKEND_URL

# Get frontend URL
export FRONTEND_URL=$(gcloud run services describe mitra-frontend --region us-central1 --format 'value(status.url)')
echo "Frontend URL: $FRONTEND_URL"
```

## Step 5: Update Backend with Correct OAuth Redirect
```bash
# Update backend with correct frontend URL for OAuth
gcloud run services update mitra-backend \
  --region us-central1 \
  --set-env-vars REDIRECT_URI="$FRONTEND_URL/auth/google/callback"
```

## Testing Commands
```bash
# Test backend health
curl -f "$BACKEND_URL/health"

# Test chat endpoint
curl -X POST "$BACKEND_URL/api/v1/input/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, how are you?", "language": "en-US"}'

# Test crisis detection
curl -X POST "$BACKEND_URL/api/v1/crisis/detect" \
  -H "Content-Type: application/json" \
  -d '{"message": "I feel very sad and hopeless", "language": "en-US"}'

# Test frontend connectivity
curl -I "$FRONTEND_URL"
```

## Production Settings (Optional)
```bash
# Backend production settings
gcloud run services update mitra-backend \
  --region us-central1 \
  --memory 4Gi \
  --cpu 2 \
  --timeout 900s \
  --concurrency 80 \
  --max-instances 20 \
  --min-instances 1

# Frontend production settings  
gcloud run services update mitra-frontend \
  --region us-central1 \
  --memory 2Gi \
  --cpu 1 \
  --timeout 120s \
  --concurrency 1000 \
  --max-instances 10 \
  --min-instances 1
```

## Environment Variables Used
- **Project ID**: ordinal-rig-470915-d0
- **Google Client ID**: 751581682843-bnfs1qgkma2kl6cbu645jf4ct57il748.apps.googleusercontent.com
- **Google Client Secret**: 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
- **Secret Key**: Vh3Djw7wXvM4t8rPxkU0oX2dQeR9sB5yFuP6vX1tKjW2hZ9lRm8pA4nDqT7bF6yC
- **RAG Corpus**: projects/ordinal-rig-470915-d0/locations/us-east4/ragCorpora/6917529027641081856
- **GCP Service Account**: Available in secrets/secrets.json
