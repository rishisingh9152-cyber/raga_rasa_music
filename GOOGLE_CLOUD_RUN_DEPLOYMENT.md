# GOOGLE CLOUD RUN DEPLOYMENT GUIDE - RAGA RASA SOUL

## Overview

This guide walks through deploying the RagaRasa Soul backend (FastAPI + MongoDB) to Google Cloud Run with all production configurations.

**Estimated Deployment Time**: 45 minutes
**Cost Estimate**: Free tier supports ~28.6M requests/month

---

## Prerequisites

Before starting, ensure you have:

1. **Google Cloud Account**
   - Active billing enabled
   - Free credits ($300 for 90 days)
   - Or existing payment method

2. **Tools Installed**
   - `gcloud` CLI (Google Cloud SDK)
   - `docker` (Docker Desktop or equivalent)
   - GitHub account with project access

3. **Project Setup**
   - Forked/cloned RagaRasa repo
   - All Backend files in `/Backend` directory
   - Docker credentials configured

---

## Step 1: Set Up Google Cloud Project

### 1.1 Create Project
```bash
# Set your project ID (use lowercase, hyphens only)
export GCP_PROJECT_ID="raga-rasa-soul-prod"
export GCP_REGION="us-central1"

# Create project
gcloud projects create $GCP_PROJECT_ID --name="RagaRasa Soul Production"

# Set default project
gcloud config set project $GCP_PROJECT_ID
```

### 1.2 Enable Required APIs
```bash
gcloud services enable \
  run.googleapis.com \
  cloudresourcemanager.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  container.googleapis.com \
  compute.googleapis.com
```

### 1.3 Create Service Account
```bash
# Create service account
gcloud iam service-accounts create raga-rasa-backend \
  --display-name="RagaRasa Soul Backend"

# Grant Cloud Run Admin role
gcloud projects add-iam-policy-binding $GCP_PROJECT_ID \
  --member=serviceAccount:raga-rasa-backend@$GCP_PROJECT_ID.iam.gserviceaccount.com \
  --role=roles/run.admin

# Grant Cloud SQL Client role (for database)
gcloud projects add-iam-policy-binding $GCP_PROJECT_ID \
  --member=serviceAccount:raga-rasa-backend@$GCP_PROJECT_ID.iam.gserviceaccount.com \
  --role=roles/cloudsql.client

# Create key for local authentication
gcloud iam service-accounts keys create ~/cloud-run-key.json \
  --iam-account=raga-rasa-backend@$GCP_PROJECT_ID.iam.gserviceaccount.com
```

---

## Step 2: Set Up MongoDB Atlas

### 2.1 Create MongoDB Atlas Cluster
```bash
# Go to https://cloud.mongodb.com/
# 1. Click "Create Cluster"
# 2. Choose "Dedicated" (M0 free tier)
# 3. Region: us-central1 (matches GCP)
# 4. Cluster name: "raga-rasa-prod"
# 5. Create cluster (wait 3-5 minutes)
```

### 2.2 Configure Database Access
```bash
# In MongoDB Atlas dashboard:
# 1. Go to "Database Access"
# 2. Create new database user:
#    Username: raga_rasa_admin
#    Password: [Generate strong password]
#    Built-in Role: Atlas Admin
# 3. Save user
```

### 2.3 Configure Network Access
```bash
# In MongoDB Atlas dashboard:
# 1. Go to "Network Access"
# 2. Add IP Address
# 3. Select "Allow access from anywhere" (0.0.0.0/0)
#    OR add your GCP Cloud Run region
# 4. Confirm
```

### 2.4 Get Connection String
```bash
# In MongoDB Atlas dashboard:
# 1. Click "Connect" button
# 2. Choose "Connect your application"
# 3. Copy connection string
# Example: mongodb+srv://raga_rasa_admin:PASSWORD@raga-rasa-prod.xxxxx.mongodb.net/raga_rasa

# Store as environment variable
export MONGODB_URL="mongodb+srv://raga_rasa_admin:PASSWORD@raga-rasa-prod.xxxxx.mongodb.net/raga_rasa"
```

---

## Step 3: Configure Backend for Production

### 3.1 Update .env.production
```bash
# In Backend directory, update .env.production
cat > Backend/.env.production << 'EOF'
# Server
PORT=8080
DEBUG=false
ENVIRONMENT=production

# Database
MONGODB_URL=mongodb+srv://raga_rasa_admin:PASSWORD@raga-rasa-prod.xxxxx.mongodb.net/raga_rasa
DATABASE_NAME=raga_rasa

# Cache (optional - use in-memory if no Redis)
REDIS_URL=
USE_REDIS=false

# External Services
EMOTION_SERVICE_URL=https://raga-rasa-emotion.hf.space
USE_EXTERNAL_EMOTION_SERVICE=true
EMOTION_SERVICE_ENDPOINT=/detect

# Security
JWT_SECRET=[Generate 32-char random string]
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
CORS_ORIGINS=["https://raga-rasa-frontend.vercel.app","https://yourdomain.com"]
ALLOWED_HOSTS=["run.app","yourdomain.com"]

# Features
MAX_UPLOAD_SIZE_MB=50
ENABLE_STREAMING=true
ENABLE_RECOMMENDATIONS=true
ENABLE_ANALYTICS=true

# Logging
LOG_LEVEL=info
LOG_FORMAT=json
EOF
```

### 3.2 Update main.py for Cloud Run
```python
# In Backend/app/main.py, ensure health check is present:
@app.get("/health")
async def health_check():
    """Cloud Run health check endpoint"""
    return {
        "status": "healthy",
        "service": "raga-rasa-backend",
        "environment": os.getenv("ENVIRONMENT", "development")
    }
```

### 3.3 Create .dockerignore
```bash
cat > Backend/.dockerignore << 'EOF'
.git
.gitignore
.env
.env.local
__pycache__
*.pyc
*.pyo
*.egg-info
dist
build
.pytest_cache
.venv
venv
node_modules
.DS_Store
*.log
uploads/
test_*.py
EOF
```

---

## Step 4: Create Artifact Registry

### 4.1 Set Up Container Registry
```bash
# Create Artifact Registry repository
gcloud artifacts repositories create raga-rasa-repo \
  --repository-format=docker \
  --location=$GCP_REGION \
  --description="RagaRasa Soul containers"

# Configure Docker authentication
gcloud auth configure-docker $GCP_REGION-docker.pkg.dev
```

### 4.2 Build and Push Image
```bash
# Set image variables
export REGISTRY="$GCP_REGION-docker.pkg.dev"
export IMAGE_NAME="raga-rasa-backend"
export IMAGE_TAG="latest"
export IMAGE_URL="$REGISTRY/$GCP_PROJECT_ID/raga-rasa-repo/$IMAGE_NAME:$IMAGE_TAG"

# Build image locally (or skip to Cloud Build)
docker build -t $IMAGE_URL -f Backend/Dockerfile Backend/

# Push to Artifact Registry
docker push $IMAGE_URL
```

**Alternative: Use Cloud Build (recommended)**
```bash
# Cloud Build handles authentication automatically
gcloud builds submit Backend/ \
  --tag=$IMAGE_URL \
  --timeout=1800s
```

---

## Step 5: Deploy to Cloud Run

### 5.1 Deploy Service
```bash
# Deploy backend service
gcloud run deploy raga-rasa-backend \
  --image=$IMAGE_URL \
  --platform=managed \
  --region=$GCP_REGION \
  --allow-unauthenticated \
  --service-account=raga-rasa-backend@$GCP_PROJECT_ID.iam.gserviceaccount.com \
  --set-env-vars=\
"MONGODB_URL=$MONGODB_URL,\
DATABASE_NAME=raga_rasa,\
JWT_SECRET=$(openssl rand -base64 32),\
ENVIRONMENT=production,\
LOG_LEVEL=info,\
CORS_ORIGINS=https://raga-rasa-frontend.vercel.app" \
  --memory=2Gi \
  --cpu=2 \
  --timeout=3600 \
  --max-instances=100 \
  --min-instances=1
```

### 5.2 Get Service URL
```bash
# After deployment completes
export BACKEND_URL=$(gcloud run services describe raga-rasa-backend \
  --platform=managed \
  --region=$GCP_REGION \
  --format='value(status.url)')

echo "Backend URL: $BACKEND_URL"
# Example: https://raga-rasa-backend-xxxxx.run.app
```

---

## Step 6: Verify Deployment

### 6.1 Health Check
```bash
# Test backend health
curl $BACKEND_URL/health

# Expected response:
# {
#   "status": "healthy",
#   "service": "raga-rasa-backend",
#   "environment": "production"
# }
```

### 6.2 Test API Endpoints
```bash
# Test registration
curl -X POST $BACKEND_URL/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!"
  }'

# Test catalog
curl $BACKEND_URL/api/catalog/songs

# Test recommendations
curl -X POST $BACKEND_URL/api/recommendations/emotion \
  -H "Content-Type: application/json" \
  -d '{
    "emotion": "anxious",
    "limit": 5
  }'
```

### 6.3 Check Logs
```bash
# View recent logs
gcloud run logs read raga-rasa-backend \
  --limit=50 \
  --region=$GCP_REGION

# Stream live logs
gcloud run logs read raga-rasa-backend \
  --region=$GCP_REGION \
  --follow
```

---

## Step 7: Update Frontend Configuration

### 7.1 Update API URL
```bash
# In frontend .env.production
VITE_API_URL=$BACKEND_URL
# Example: https://raga-rasa-backend-xxxxx.run.app/api
```

### 7.2 Add CORS Origins
```bash
# Update in Backend environment variables
gcloud run services update raga-rasa-backend \
  --region=$GCP_REGION \
  --update-env-vars=\
"CORS_ORIGINS=https://raga-rasa-frontend.vercel.app,https://yourdomain.com"
```

---

## Step 8: Set Up Continuous Deployment

### 8.1 Create Cloud Build Trigger
```bash
# Connect GitHub repo
gcloud builds connect --repo-name=raga-rasa-soul \
  --repo-owner=YOUR_GITHUB_USERNAME

# Create trigger for Backend
gcloud builds triggers create github \
  --name=raga-rasa-backend-deploy \
  --repo-name=raga-rasa-soul \
  --repo-owner=YOUR_GITHUB_USERNAME \
  --branch-pattern=^main$ \
  --build-config=Backend/cloudbuild.yaml
```

### 8.2 Create cloudbuild.yaml
```yaml
# Backend/cloudbuild.yaml
steps:
  # Build image
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'build'
      - '-t'
      - '${LOCATION}-docker.pkg.dev/${PROJECT_ID}/raga-rasa-repo/raga-rasa-backend:${SHORT_SHA}'
      - '-t'
      - '${LOCATION}-docker.pkg.dev/${PROJECT_ID}/raga-rasa-repo/raga-rasa-backend:latest'
      - '-f'
      - 'Backend/Dockerfile'
      - 'Backend/'

  # Push to Artifact Registry
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'push'
      - '${LOCATION}-docker.pkg.dev/${PROJECT_ID}/raga-rasa-repo/raga-rasa-backend:${SHORT_SHA}'

  # Deploy to Cloud Run
  - name: 'gcr.io/cloud-builders/run'
    args:
      - 'deploy'
      - 'raga-rasa-backend'
      - '--image'
      - '${LOCATION}-docker.pkg.dev/${PROJECT_ID}/raga-rasa-repo/raga-rasa-backend:${SHORT_SHA}'
      - '--region'
      - '${LOCATION}'
      - '--platform'
      - 'managed'
      - '--allow-unauthenticated'

images:
  - '${LOCATION}-docker.pkg.dev/${PROJECT_ID}/raga-rasa-repo/raga-rasa-backend:${SHORT_SHA}'

options:
  machineType: 'N1_HIGHCPU_8'
```

---

## Step 9: Set Up Monitoring

### 9.1 Enable Cloud Monitoring
```bash
# View metrics in Cloud Console
# Navigate to Monitoring → Dashboards
# Create new dashboard with:
# - Request count
# - Error rate
# - Latency
# - Memory usage
# - CPU usage
```

### 9.2 Create Alerts
```bash
# Alert on high error rate
gcloud alpha monitoring policies create \
  --notification-channels=[CHANNEL_ID] \
  --display-name="High Error Rate" \
  --condition-display-name="Error rate > 5%" \
  --condition-threshold-value=5
```

---

## Step 10: Production Checklist

Before going live:

- [ ] MongoDB Atlas cluster running
- [ ] Backend deployed to Cloud Run
- [ ] Health check endpoint responding
- [ ] All 35+ API endpoints tested
- [ ] CORS configured correctly
- [ ] JWT tokens working
- [ ] Email notifications setup (optional)
- [ ] Logging and monitoring active
- [ ] Backup strategy configured
- [ ] Load testing completed

---

## Common Issues and Solutions

### Issue: Image not found in Artifact Registry
```bash
# Solution: Verify image was pushed
gcloud artifacts docker images list $GCP_REGION-docker.pkg.dev/$GCP_PROJECT_ID/raga-rasa-repo

# Re-push if needed
docker push $IMAGE_URL
```

### Issue: Container exits immediately
```bash
# Check logs
gcloud run logs read raga-rasa-backend --limit=100

# Common causes:
# - Missing environment variables
# - Database connection failed
# - Port not bound to 8080
```

### Issue: Database connection timeout
```bash
# Verify connection string
gcloud run services describe raga-rasa-backend --format=json | grep MONGODB

# Test connection locally
python3 -c "
from pymongo import MongoClient
uri = 'YOUR_MONGODB_URL'
client = MongoClient(uri, serverSelectionTimeoutMS=5000)
client.server_info()
print('Connected!')
"
```

### Issue: CORS errors from frontend
```bash
# Update CORS origins
gcloud run services update raga-rasa-backend \
  --region=$GCP_REGION \
  --set-env-vars=CORS_ORIGINS="https://yourdomain.com"
```

---

## Cost Optimization

1. **Auto-scaling**: Set `--min-instances=0` for zero-cost idle time
2. **Memory**: Use `--memory=1Gi` if sufficient (default 2Gi)
3. **CPU**: Use `--cpu=1` for less demanding workloads
4. **Caching**: Enable Redis for better performance (additional cost)
5. **Database**: Use MongoDB shared cluster for free tier

**Estimated Monthly Cost**:
- Cloud Run: $0 - $20 (free tier + occasional usage)
- MongoDB Atlas: $0 (free M0 tier)
- **Total: ~$20/month**

---

## Next Steps

1. Deploy frontend to Vercel (see VERCEL_FRONTEND_DEPLOYMENT.md)
2. Deploy emotion service to HF Spaces (see HF_SPACES_EMOTION_DEPLOYMENT.md)
3. Set up custom domain with Cloud Armor
4. Configure CDN for static assets
5. Implement analytics and monitoring dashboards

---

## Support and Documentation

- Google Cloud Run Docs: https://cloud.google.com/run/docs
- MongoDB Atlas Docs: https://docs.atlas.mongodb.com
- FastAPI Deployment: https://fastapi.tiangolo.com/deployment
- Docker Docs: https://docs.docker.com

**Last Updated**: April 2026
**Version**: 1.0
