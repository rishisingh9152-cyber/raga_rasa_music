# RENDER BACKEND DEPLOYMENT GUIDE - RAGA RASA SOUL

## Overview

This guide walks through deploying the RagaRasa Soul backend (FastAPI + MongoDB) to Render with automatic CI/CD from GitHub.

**Estimated Deployment Time**: 30 minutes
**Cost Estimate**: Free tier or $7+/month for production

---

## Prerequisites

Before starting, ensure you have:

1. **Render Account**
   - Sign up at https://render.com
   - Free tier available (with limitations)
   - Payment method for production tier

2. **GitHub Account**
   - Repository with Backend code
   - GitHub personal access token (for deploys)

3. **MongoDB**
   - MongoDB Atlas cluster ready
   - Connection string obtained
   - Database user created

---

## Step 1: Prepare Backend Code

### 1.1 Verify Backend Structure
```bash
# In Backend directory, ensure you have:
ls -la
# Should contain:
# - main.py
# - requirements.txt
# - app/
# - config.py
# - Dockerfile
```

### 1.2 Create render.yaml
```yaml
# render.yaml - in root of Backend directory
services:
  - type: web
    name: raga-rasa-backend
    runtime: python
    pythonVersion: 3.10
    buildCommand: pip install --upgrade pip setuptools && pip install -r requirements.txt
    startCommand: gunicorn --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout 120 main:app
    envVars:
      - key: PORT
        value: 8000
      - key: ENVIRONMENT
        value: production
      - key: LOG_LEVEL
        value: info
      - key: DEBUG
        value: false
      - key: MONGODB_URL
        sync: false
      - key: JWT_SECRET
        sync: false
      - key: CORS_ORIGINS
        value: https://raga-rasa-soul.vercel.app
      - key: EMOTION_SERVICE_URL
        value: https://rishi22652-emotion-recognition.hf.space
```

### 1.3 Create Procfile (Alternative Method)
```bash
# Procfile - in Backend directory
web: gunicorn --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout 120 main:app
```

### 1.4 Update requirements.txt
Ensure all dependencies are specified:
```bash
# Make sure requirements.txt includes:
# - fastapi==0.109.0
# - uvicorn[standard]==0.27.0
# - gunicorn==21.0.0
# - All other dependencies
```

### 1.5 Create .renderignore
```bash
# .renderignore - in Backend directory
.git
.gitignore
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
test_*.py
.env
```

### 1.6 Update main.py for Render

Ensure the health check and error handling are in place:

```python
# In Backend/app/main.py
import os
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

app = FastAPI(title="RagaRasa Soul API")

@app.get("/health")
async def health_check():
    """Render health check endpoint"""
    return {
        "status": "healthy",
        "service": "raga-rasa-backend",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "port": os.getenv("PORT", "8000")
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "RagaRasa Soul API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }

# IMPORTANT: Listen on port from environment
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
```

### 1.7 Configure Database Connection

```python
# In Backend/app/database.py or config.py
import os
from motor.motor_asyncio import AsyncClient

# Get MongoDB URL from environment
MONGODB_URL = os.getenv("MONGODB_URL")

# Ensure retry logic
client = AsyncClient(MONGODB_URL, serverSelectionTimeoutMS=5000, connectTimeoutMS=10000)

# Test connection on startup
@app.on_event("startup")
async def startup_db_client():
    try:
        await client.admin.command('ping')
        print("MongoDB connection successful")
    except Exception as e:
        print(f"MongoDB connection failed: {e}")
        raise
```

---

## Step 2: Push Code to GitHub

### 2.1 Commit Backend Code
```bash
cd Backend

# Ensure all files are staged
git add .

# Commit with message
git commit -m "Backend: Production-ready for Render deployment"

# Push to main branch
git push origin main
```

### 2.2 Create GitHub Personal Access Token
```bash
# Go to GitHub → Settings → Developer settings → Personal access tokens → Fine-grained tokens
# Create new token with:
# - Repository access: Your repo
# - Permissions:
#   - Contents: Read and write
#   - Webhooks: Read and write
#   - Deployments: Read and write

# Save token as: GITHUB_TOKEN=ghp_xxxxx
```

---

## Step 3: Create Render Service

### 3.1 Log in to Render
```bash
# Go to https://render.com/dashboard
# Click "New +"
# Select "Web Service"
```

### 3.2 Connect GitHub Repository
```
1. Click "Connect account" (GitHub)
2. Authorize Render to access your GitHub account
3. Select your repository: raga_rasa_music
4. Click "Connect"
```

### 3.3 Configure Web Service

**Fill in the following:**

```
Name:                      raga-rasa-backend
Environment:               Python 3
Build Command:             pip install --upgrade pip setuptools && pip install -r requirements.txt
Start Command:             gunicorn --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout 120 main:app
Repository:                raga_rasa_music
Branch:                    main
Root Directory:            Backend
Plan:                      Starter ($7/month) or Free (with limitations)
```

### 3.4 Set Environment Variables

In Render Dashboard → Settings → Environment:

```
PORT=8000
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=info
DATABASE_NAME=raga_rasa
MONGODB_URL=[Your MongoDB Atlas connection string]
JWT_SECRET=[Generate 32-character random string]
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
CORS_ORIGINS=https://raga-rasa-soul.vercel.app,https://yourdomain.com
ALLOWED_HOSTS=render.com,yourdomain.com
USE_EXTERNAL_EMOTION_SERVICE=true
EMOTION_SERVICE_URL=https://rishi22652-emotion-recognition.hf.space
EMOTION_SERVICE_ENDPOINT=/detect
ENABLE_STREAMING=true
ENABLE_RECOMMENDATIONS=true
ENABLE_ANALYTICS=true
MAX_UPLOAD_SIZE_MB=50
LOG_FORMAT=json
```

### 3.5 Generate JWT Secret

```bash
# Generate a secure random string (32 chars)
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Or use OpenSSL
openssl rand -base64 32

# Copy this value to JWT_SECRET in Render
```

---

## Step 4: Deploy Service

### 4.1 Initiate Deployment
```
1. In Render Dashboard
2. Click "Create Web Service"
3. Wait for build to complete (2-5 minutes)
4. Monitor build logs in real-time
```

### 4.2 Monitor Build Process

Build stages:
1. **Clone Repository** - Fetch code from GitHub
2. **Install Dependencies** - Run `pip install -r requirements.txt`
3. **Build** - Create deployment package
4. **Deploy** - Start service instance
5. **Health Check** - Verify service is running

### 4.3 Get Service URL

After successful deployment:
```
Service URL: https://raga-rasa-backend.onrender.com
Status: Live
```

Save this URL - you'll need it for frontend configuration.

---

## Step 5: Verify Deployment

### 5.1 Health Check
```bash
curl https://raga-rasa-backend.onrender.com/health

# Expected response:
# {
#   "status": "healthy",
#   "service": "raga-rasa-backend",
#   "environment": "production",
#   "port": "8000"
# }
```

### 5.2 Check Logs
```bash
# In Render Dashboard → Logs
# View real-time logs and any errors
```

### 5.3 Test API Endpoints
```bash
# Get songs
curl https://raga-rasa-backend.onrender.com/api/catalog/songs

# Register user
curl -X POST https://raga-rasa-backend.onrender.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!"
  }'

# Get recommendations
curl -X POST https://raga-rasa-backend.onrender.com/api/recommendations/emotion \
  -H "Content-Type: application/json" \
  -d '{
    "emotion": "anxious",
    "limit": 5
  }'
```

---

## Step 6: Set Up Auto-Deploy from GitHub

### 6.1 Configure GitHub Integration
```
1. In Render Dashboard → Settings
2. Under "GitHub", connect your repository
3. Enable "Auto-deploy" on push to main
4. Save settings
```

### 6.2 Test Auto-Deploy

Make a small change to Backend code:
```bash
# Edit a file
echo "# Updated" >> Backend/main.py

# Commit and push
git add Backend/main.py
git commit -m "Test auto-deploy"
git push origin main

# Watch for automatic deployment in Render dashboard
# Should start deploying within 30 seconds
```

### 6.3 Webhook Configuration

Render automatically creates GitHub webhooks:
```
Webhook URL: https://api.render.com/deploy/service-xxxxx?key=xxxxx
Events: Push to branch
```

---

## Step 7: Update Frontend Configuration

### 7.1 Update Vercel Environment Variables

In Vercel Dashboard:
```
VITE_API_URL=https://raga-rasa-backend.onrender.com/api
VITE_EMOTION_SERVICE_URL=https://rishi22652-emotion-recognition.hf.space
VITE_DEBUG=false
```

### 7.2 Redeploy Frontend

```bash
# Frontend will automatically redeploy when env vars change
# Or manually trigger in Vercel dashboard
```

---

## Step 8: Configure Custom Domain (Optional)

### 8.1 Add Custom Domain
```
1. In Render Dashboard → Settings
2. Under "Custom Domains"
3. Add your domain: api.yourdomain.com
4. Get CNAME record: raga-rasa-backend.onrender.com
```

### 8.2 Update DNS

In your domain registrar:
```
CNAME: api.yourdomain.com → raga-rasa-backend.onrender.com
TTL: 3600 (or default)
```

### 8.3 SSL Certificate
```
Render automatically provisions:
- Free SSL certificate
- Auto-renewal
- HSTS headers
```

---

## Step 9: Set Up Monitoring and Logs

### 9.1 View Logs in Render
```
1. Render Dashboard → Your Service
2. Click "Logs" tab
3. View real-time logs
4. Search by keyword
5. Filter by log level
```

### 9.2 Configure Alerts (Paid Plan)

For Render Pro:
```
1. Settings → Monitoring
2. Alert when:
   - Error rate > 5%
   - Response time > 2 seconds
   - Service down
   - Memory usage > 80%
```

### 9.3 Export Logs

```bash
# Via Render API
curl https://api.render.com/v1/services/srv-xxxxx/logs \
  -H "Authorization: Bearer YOUR_API_KEY"
```

---

## Step 10: Production Checklist

Before going live:

- [ ] Service deployed successfully
- [ ] Health check responding
- [ ] All API endpoints tested
- [ ] MongoDB connection verified
- [ ] CORS configured correctly
- [ ] JWT tokens working
- [ ] Error handling tested
- [ ] Logging functional
- [ ] Auto-deploy from GitHub working
- [ ] Custom domain configured (if applicable)
- [ ] Monitoring active
- [ ] Backups configured
- [ ] Performance acceptable
- [ ] Load testing completed

---

## Common Issues and Solutions

### Issue: Build Fails with Module Not Found
```
Error: No module named 'fastapi'
```

**Solution**:
1. Check requirements.txt is in Backend directory
2. Verify all dependencies listed
3. Test locally: `pip install -r requirements.txt`

```bash
# Common missing packages:
# - gunicorn
# - uvicorn[standard]
# - motor
# - pymongo
```

### Issue: Service Crashes on Startup
```
Status: Runtime error
```

**Solution**:
1. Check logs in Render dashboard
2. Verify environment variables set
3. Test start command locally:
```bash
gunicorn --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --timeout 120 main:app
```

### Issue: MongoDB Connection Timeout
```
Error: ServerSelectionTimeoutError
```

**Solution**:
1. Verify MongoDB URL is correct
2. Check MongoDB Atlas IP whitelist includes Render
   - Add 0.0.0.0/0 (allow all) or
   - Add Render IP (https://render.com/docs/web-services#ip-addresses)
3. Test connection:
```bash
python3 << 'EOF'
from pymongo import MongoClient
uri = "YOUR_MONGODB_URL"
client = MongoClient(uri, serverSelectionTimeoutMS=5000)
client.server_info()
print("Connected!")
EOF
```

### Issue: CORS Errors from Frontend
```
Error: Access to XMLHttpRequest blocked by CORS
```

**Solution**:
1. Update CORS_ORIGINS in Render environment:
```
CORS_ORIGINS=https://your-vercel-url.vercel.app
```
2. Restart service (or auto-deploys on next push)
3. Clear browser cache

### Issue: 503 Service Unavailable
```
Error: All instances are busy
```

**Solution**:
1. Check if using free tier (has limitations)
2. Upgrade to paid tier if needed
3. Optimize database queries
4. Implement caching

### Issue: Cold Start Taking Too Long
```
First request slow, subsequent requests fast
```

**Solution**:
1. Upgrade to Starter tier ($7/month) for persistent service
2. Implement keep-alive in frontend
3. Pre-warm critical routes

---

## Performance Optimization

### 1. Database Optimization
```python
# In database.py
# Enable connection pooling
client = AsyncClient(
    MONGODB_URL,
    maxPoolSize=50,
    minPoolSize=10,
    serverSelectionTimeoutMS=5000
)

# Create indexes for frequently queried fields
await db.songs.create_index([("rasa", 1)])
await db.sessions.create_index([("user_id", 1), ("created_at", -1)])
```

### 2. Enable Caching
```python
# Use Redis for caching (optional)
from redis.asyncio import Redis

redis = Redis(host=REDIS_URL)

# Cache recommendation results
@app.get("/api/recommendations/emotion")
async def get_recommendations(emotion: str):
    # Check cache first
    cached = await redis.get(f"recs:{emotion}")
    if cached:
        return json.loads(cached)
    
    # Generate and cache
    result = generate_recommendations(emotion)
    await redis.setex(f"recs:{emotion}", 3600, json.dumps(result))
    return result
```

### 3. Optimize Endpoints
```python
# Use select() to limit fields returned
songs = await db.songs.find({}, {"_id": 1, "title": 1, "rasa": 1}).limit(20).to_list(None)

# Implement pagination
@app.get("/api/catalog/songs")
async def get_songs(skip: int = 0, limit: int = 20):
    songs = await db.songs.find().skip(skip).limit(limit).to_list(None)
    return songs
```

### 4. Worker Configuration
```bash
# In Procfile or start command
# Adjust workers based on available memory
# Free tier: 512MB → 1-2 workers
# Starter: 512MB → 2-4 workers
# Standard: 2GB → 4-8 workers

gunicorn --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
```

---

## Cost Analysis

### Render Pricing
| Plan | Price | Resources | Use Case |
|------|-------|-----------|----------|
| Free | $0 | 512MB, 0.5 CPU | Development |
| Starter | $7/month | 512MB, 0.5 CPU | Small production |
| Standard | $25/month | 2GB, 2 CPU | Production |
| Pro | $50+/month | 4GB+, 4+ CPU | High traffic |

### Cost Optimization
1. **Free tier** for development/testing
2. **Starter tier** for production with low traffic
3. Monitor usage and upgrade as needed
4. Use MongoDB free tier (M0)
5. Implement caching to reduce database load

**Recommended**: Starter tier ($7/month) for production

---

## Deployment Workflow Summary

```
1. Code → GitHub (main branch)
   ↓
2. Push triggers Render webhook
   ↓
3. Render clones repository
   ↓
4. Install dependencies (pip install)
   ↓
5. Build container
   ↓
6. Start service (gunicorn)
   ↓
7. Health check passes
   ↓
8. Service live at https://raga-rasa-backend.onrender.com
   ↓
9. Monitor logs and metrics
```

---

## Next Steps

1. ✅ **Backend Deployed** - on Render
2. **Frontend**: Deploy to Vercel (see VERCEL_FRONTEND_DEPLOYMENT.md)
3. **Testing**: Run integration test suite
4. **Monitoring**: Set up alerts and logs
5. **Optimization**: Monitor performance and optimize

---

## Useful Commands

```bash
# Check if service is running
curl https://raga-rasa-backend.onrender.com/health

# Test with sample data
python test_integration_suite.py

# View logs locally
# (In Render dashboard → Logs tab)

# Monitor service
# (In Render dashboard → Metrics tab)

# Update environment variables
# (In Render dashboard → Environment)

# Force redeploy
# (In Render dashboard → Manual Deploy)
```

---

## Render-Specific Features

### 1. Persistent Disk (Paid Plan)
```yaml
# For storing large files
disks:
  - name: data
    path: /data
    sizeGB: 10
```

### 2. Private Services
```bash
# Internal service (not public)
# Can be used for background jobs
```

### 3. Cron Jobs
```yaml
# Schedule background tasks
crons:
  - name: cleanup
    command: python cleanup.py
    schedule: "0 2 * * *"  # Daily at 2 AM
```

### 4. Webhooks
```bash
# Integrate with external services
# Slack notifications, analytics, etc.
```

---

## Support and Documentation

- Render Docs: https://render.com/docs
- FastAPI Docs: https://fastapi.tiangolo.com
- MongoDB Docs: https://docs.mongodb.com
- GitHub Actions: https://docs.github.com/en/actions

---

## Migration from Other Platforms

### From Google Cloud Run
```bash
# If you previously deployed to GCP:
# 1. Same Docker configuration works
# 2. Update environment variables
# 3. Render handles container orchestration
```

### From Vercel Functions
```bash
# If using Vercel serverless functions:
# 1. This is a full backend service (better for FastAPI)
# 2. More control and customization
# 3. Better for long-running tasks
```

### From Heroku
```bash
# Render is a Heroku alternative
# 1. Similar deployment model (push → deploy)
# 2. Better pricing and performance
# 3. More native support for Python apps
```

---

## Troubleshooting Checklist

- [ ] GitHub account connected
- [ ] Repository is public or access granted
- [ ] requirements.txt in Backend directory
- [ ] main.py has correct import/structure
- [ ] Port defaults to 8000 or uses $PORT env var
- [ ] All environment variables set in Render
- [ ] MongoDB URL is valid and whitelisted
- [ ] Health check endpoint exists
- [ ] Start command is correct
- [ ] Build logs show no errors
- [ ] Service shows "Live" status
- [ ] Health check returns 200

---

**Last Updated**: April 13, 2026
**Version**: 1.0
**Status**: ✅ PRODUCTION READY

🚀 Deploy now and go live!
