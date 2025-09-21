# MITRA Sense Deployment Guide

## 🚀 Initial Setup (One Time Only)

### 1. Install Firebase CLI
```bash
npm install -g firebase-tools
firebase login
```

### 2. First Deployment
```bash
./deploy-firebase.sh
```

This will:
- ✅ Deploy backend to Cloud Run with stable URL
- ✅ Deploy frontend to Firebase Hosting with clean URL
- ✅ Configure OAuth redirect URIs automatically
- ✅ Set up all required Google Cloud services

**Your stable URLs will be:**
- Frontend: `https://mitrasense.web.app` ✨
- Backend: `https://mitra-api-751581682843.us-central1.run.app`

## 🔄 Future Deployments (When You Change Code)

**For ANY code changes (backend, frontend, or both):**

```bash
./deploy-firebase.sh
```

That's it! The script handles everything:
- ✅ Rebuilds containers with your latest code
- ✅ Deploys to the SAME stable URLs
- ✅ Updates both backend and frontend automatically
- ✅ Maintains OAuth configuration

## 📝 What Each Deployment Does

### Backend Changes (Python/FastAPI):
- Rebuilds Docker image with your new code
- Pushes to Artifact Registry
- Deploys to Cloud Run (same URL)
- Updates environment variables if needed

### Frontend Changes (React/Next.js):
- Rebuilds with latest code
- Builds static files for Firebase
- Deploys to Firebase Hosting (same URL)
- Updates API connections automatically

## ⚡ Quick Development Workflow

1. **Make your code changes** (any files in `app/` or `frontend/`)
2. **Test locally** (optional):
   ```bash
   # Backend
   uvicorn app.main:app --reload
   
   # Frontend  
   cd frontend && npm run dev
   ```
3. **Deploy everything**:
   ```bash
   ./deploy-firebase.sh
   ```
4. **Test your live app** at `https://mitrasense.web.app`

## 🎯 Key Benefits

- ✅ **Stable URLs**: Never change, perfect for OAuth
- ✅ **One Command**: Deploy everything with one script
- ✅ **Clean URLs**: Professional Firebase Hosting domain
- ✅ **Fast**: Static frontend, serverless backend
- ✅ **Reliable**: Google Cloud infrastructure

## 🔧 Troubleshooting

If deployment fails:
1. Check you're logged into Firebase: `firebase login`
2. Check Docker is running: `docker --version`
3. Check gcloud auth: `gcloud auth list`
4. Run deployment script again: `./deploy-firebase.sh`

## 🌐 OAuth Configuration

After first deployment, update Google Cloud Console:
1. Go to: https://console.cloud.google.com/apis/credentials
2. Find your OAuth Client ID
3. Add redirect URI: `https://mitrasense.web.app/auth/google/callback`
4. Save changes

**URLs will NEVER change after this setup!** 🎉
