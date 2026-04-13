# RENDER BACKEND DEPLOYMENT - ENVIRONMENT VARIABLES & TERMINAL STEPS

## Quick Copy-Paste Environment Variables

### 1. Generate JWT Secret (Run this in terminal)

```bash
# On Mac/Linux:
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# On Windows (PowerShell):
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Example output:
# kV_3xK-2mPqRs4tUvWxYz5aB6cDeF7gHi8jKlMnOpQ
# ^ Copy this value
```

### 2. MongoDB Connection String

**If you have MongoDB Atlas:**

```
mongodb+srv://raga_rasa_admin:YOUR_PASSWORD@cluster-name.xxxxx.mongodb.net/raga_rasa?retryWrites=true&w=majority
```

**Replace:**
- `YOUR_PASSWORD` - Password from MongoDB Atlas
- `cluster-name` - Your cluster name
- `xxxxx` - Random MongoDB ID

**If you DON'T have MongoDB yet**, follow Step 1 first.

---

## Step-by-Step Terminal Commands

### STEP 1: Set Up MongoDB Atlas (if you don't have it yet)

#### 1.1 Create MongoDB Atlas Account
```bash
# Go to https://www.mongodb.com/cloud/atlas
# Sign up for free (M0 tier)
# Email verification takes 2 minutes
```

#### 1.2 Create Cluster
```bash
# In MongoDB Atlas dashboard:
# 1. Click "Create" → "Build a Database"
# 2. Select "M0 Free" (appears at bottom)
# 3. Cloud Provider: AWS
# 4. Region: us-central1 (same as Render)
# 5. Cluster Name: raga-rasa-prod
# 6. Click "Create Cluster"
# Wait 3-5 minutes for cluster to be ready
```

#### 1.3 Create Database User
```bash
# In MongoDB Atlas:
# 1. Go to "Database Access"
# 2. Click "Add New Database User"
# 3. Username: raga_rasa_admin
# 4. Password: [Create strong password - save this!]
# 5. Built-in Roles: Atlas Admin
# 6. Click "Add User"
```

#### 1.4 Allow Network Access
```bash
# In MongoDB Atlas:
# 1. Go to "Network Access"
# 2. Click "Add IP Address"
# 3. Select "Allow access from anywhere" (0.0.0.0/0)
# 4. Click "Confirm"
```

#### 1.5 Get Connection String
```bash
# In MongoDB Atlas:
# 1. Click "Databases" → Your cluster
# 2. Click "Connect" button
# 3. Select "Connect your application"
# 4. Copy the connection string
# Example: mongodb+srv://raga_rasa_admin:PASSWORD@raga-rasa-prod.xxxxx.mongodb.net/?retryWrites=true&w=majority
```

---

### STEP 2: Prepare Backend Code

#### 2.1 Navigate to Backend Directory
```bash
cd Backend

# Verify you're in correct directory:
ls -la
# Should show: main.py, requirements.txt, app/, config.py, Dockerfile
```

#### 2.2 Verify requirements.txt
```bash
# Check that requirements.txt exists and contains:
cat requirements.txt | grep -E "fastapi|uvicorn|gunicorn|pymongo|motor"

# Should output:
# fastapi==0.109.0
# uvicorn[standard]==0.27.0
# gunicorn==21.0.0
# pymongo==4.6.0
# motor==3.3.2
```

#### 2.3 Create Procfile (if it doesn't exist)
```bash
# Create Procfile in Backend directory
cat > Procfile << 'EOF'
web: gunicorn --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout 120 main:app
EOF

# Verify it was created:
cat Procfile
```

#### 2.4 Create .renderignore (if it doesn't exist)
```bash
# Create .renderignore in Backend directory
cat > .renderignore << 'EOF'
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
EOF

# Verify:
cat .renderignore
```

#### 2.5 Commit Changes to GitHub
```bash
# Go back to root directory
cd ..

# Stage all files
git add Backend/

# Check what's staged
git status

# Commit with message
git commit -m "Backend: Prepare for Render deployment"

# Push to GitHub
git push origin main

# Verify it's on GitHub (should see recent commit in a few seconds)
```

---

### STEP 3: Generate Required Secrets

#### 3.1 Generate JWT Secret
```bash
# Run this command in terminal:
python3 -c "import secrets; print('JWT_SECRET=' + secrets.token_urlsafe(32))"

# Output will look like:
# JWT_SECRET=kV_3xK-2mPqRs4tUvWxYz5aB6cDeF7gHi8jKlMnOpQ

# Copy the part after = (just the random string)
# You'll paste this into Render dashboard
```

#### 3.2 Prepare MongoDB Connection String
```bash
# Get from MongoDB Atlas (see STEP 1.5)
# Should look like:
# mongodb+srv://raga_rasa_admin:PASSWORD@raga-rasa-prod.xxxxx.mongodb.net/?retryWrites=true&w=majority

# IMPORTANT: Replace PASSWORD with actual password
# Example:
# mongodb+srv://raga_rasa_admin:MySecurePass123@raga-rasa-prod.xxxxx.mongodb.net/?retryWrites=true&w=majority
```

---

### STEP 4: Create Render Service

#### 4.1 Open Render Dashboard
```bash
# Go to https://render.com/dashboard
# Log in or sign up (if you haven't already)
```

#### 4.2 Create New Web Service
```bash
# In Render Dashboard:
# 1. Click "+ New"
# 2. Select "Web Service"
# 3. Click "Connect repository" (or "GitHub" button)
# 4. Authorize Render to access GitHub
# 5. Select your repository: raga_rasa_music
# 6. Click "Connect"
```

#### 4.3 Configure Service (Fill these fields in Render)

```
Name:                      raga-rasa-backend
Runtime:                   Python 3
Root Directory:            Backend
Branch:                    main

Build Command:
pip install --upgrade pip setuptools && pip install -r requirements.txt

Start Command:
gunicorn --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout 120 main:app

Instance Type:             Starter ($7/month)
Region:                    Ohio (us-east-1) [or choose closest to you]
```

#### 4.4 Add Environment Variables

In Render Dashboard, under "Environment":

```
PORT=8000
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=info
DATABASE_NAME=raga_rasa
```

Click "Add Environment Variable" for each:

```
MONGODB_URL
[Paste your MongoDB connection string here]

JWT_SECRET
[Paste the JWT secret you generated]

JWT_ALGORITHM
HS256

JWT_EXPIRATION_HOURS
24

CORS_ORIGINS
https://raga-rasa-soul.vercel.app

ALLOWED_HOSTS
render.com,yourdomain.com

USE_EXTERNAL_EMOTION_SERVICE
true

EMOTION_SERVICE_URL
https://rishi22652-emotion-recognition.hf.space

EMOTION_SERVICE_ENDPOINT
/detect

ENABLE_STREAMING
true

ENABLE_RECOMMENDATIONS
true

ENABLE_ANALYTICS
true

MAX_UPLOAD_SIZE_MB
50

LOG_FORMAT
json
```

---

## ENVIRONMENT VARIABLES CHECKLIST

### Copy-Paste Ready (Fill in YOUR values)

```bash
# ============================================
# RAGA RASA SOUL - BACKEND ENVIRONMENT VARIABLES
# ============================================

# === SERVER ===
PORT=8000
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=info

# === DATABASE ===
DATABASE_NAME=raga_rasa
MONGODB_URL=mongodb+srv://raga_rasa_admin:YOUR_PASSWORD@cluster-name.xxxxx.mongodb.net/raga_rasa?retryWrites=true&w=majority

# === AUTHENTICATION ===
JWT_SECRET=YOUR_GENERATED_SECRET_HERE
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# === CORS & SECURITY ===
CORS_ORIGINS=https://raga-rasa-soul.vercel.app,https://yourdomain.com
ALLOWED_HOSTS=render.com,yourdomain.com

# === EXTERNAL SERVICES ===
USE_EXTERNAL_EMOTION_SERVICE=true
EMOTION_SERVICE_URL=https://rishi22652-emotion-recognition.hf.space
EMOTION_SERVICE_ENDPOINT=/detect

# === FEATURES ===
ENABLE_STREAMING=true
ENABLE_RECOMMENDATIONS=true
ENABLE_ANALYTICS=true

# === FILE UPLOAD ===
MAX_UPLOAD_SIZE_MB=50

# === LOGGING ===
LOG_FORMAT=json
```

---

## Step-by-Step Render Dashboard Setup

### Create Web Service in Render

**Terminal command** (optional, if you prefer CLI):
```bash
# Install render CLI (optional)
npm install -g @render-com/cli

# Or use dashboard (easier)
# Go to https://render.com/dashboard
```

### In Render Dashboard:

#### Step 4.5: Click "Create Web Service"
```
1. Click the "+ New" button (top right)
2. Select "Web Service"
3. Click "GitHub" (or "Connect repository")
4. Select your repository
5. Fill in the form:
   - Name: raga-rasa-backend
   - Root Directory: Backend
   - Build Command: [see above]
   - Start Command: [see above]
   - Plan: Starter ($7/month)
6. Click "Advanced" to set environment variables
7. Add all environment variables from checklist above
8. Click "Create Web Service"
```

### Step 4.6: Verify Deployment

```bash
# Watch the build logs in Render dashboard
# It will show:
# 1. Building... (30-60 seconds)
# 2. Deploying... (30-60 seconds)
# 3. Live! (service is running)

# After "Live", you'll see your service URL:
# https://raga-rasa-backend.onrender.com
```

---

## Testing After Deployment

### Step 5: Test Backend Health

#### 5.1 Health Check
```bash
# In terminal, replace URL with your actual URL:
curl https://raga-rasa-backend.onrender.com/health

# Expected response:
# {
#   "status": "healthy",
#   "service": "raga-rasa-backend",
#   "environment": "production",
#   "port": "8000"
# }
```

#### 5.2 Test API Endpoints
```bash
# Get all songs (no auth needed)
curl https://raga-rasa-backend.onrender.com/api/catalog/songs

# Register new user
curl -X POST https://raga-rasa-backend.onrender.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!"
  }'

# Get emotions (no auth needed)
curl https://raga-rasa-backend.onrender.com/api/catalog/emotions

# Get recommendations
curl -X POST https://raga-rasa-backend.onrender.com/api/recommendations/emotion \
  -H "Content-Type: application/json" \
  -d '{
    "emotion": "anxious",
    "limit": 5
  }'
```

#### 5.3 Python Test Script
```bash
# Create a test file:
cat > test_render_deploy.py << 'EOF'
import requests

BACKEND_URL = "https://raga-rasa-backend.onrender.com"

print("Testing Render Deployment...")
print("=" * 60)

# Test 1: Health Check
print("\n[1] Health Check")
try:
    response = requests.get(f"{BACKEND_URL}/health", timeout=10)
    if response.status_code == 200:
        print("✅ PASS - Backend is healthy")
        print(f"Response: {response.json()}")
    else:
        print(f"❌ FAIL - Got status {response.status_code}")
except Exception as e:
    print(f"❌ FAIL - Error: {e}")

# Test 2: Get Songs
print("\n[2] Get All Songs")
try:
    response = requests.get(f"{BACKEND_URL}/api/catalog/songs", timeout=10)
    if response.status_code == 200:
        songs = response.json()
        print(f"✅ PASS - Retrieved {len(songs)} songs")
    else:
        print(f"❌ FAIL - Got status {response.status_code}")
except Exception as e:
    print(f"❌ FAIL - Error: {e}")

# Test 3: Register User
print("\n[3] Register User")
try:
    response = requests.post(
        f"{BACKEND_URL}/api/auth/register",
        json={
            "email": f"test_{int(__import__('time').time())}@example.com",
            "password": "TestPassword123!"
        },
        timeout=10
    )
    if response.status_code == 200:
        user = response.json()
        print(f"✅ PASS - User registered")
        print(f"Email: {user['user']['email']}")
    else:
        print(f"❌ FAIL - Got status {response.status_code}")
        print(f"Response: {response.text}")
except Exception as e:
    print(f"❌ FAIL - Error: {e}")

# Test 4: Get Emotions
print("\n[4] Get Available Emotions")
try:
    response = requests.get(f"{BACKEND_URL}/api/catalog/emotions", timeout=10)
    if response.status_code == 200:
        emotions = response.json()
        print(f"✅ PASS - Retrieved emotions")
        print(f"Count: {len(emotions)}")
    else:
        print(f"❌ FAIL - Got status {response.status_code}")
except Exception as e:
    print(f"❌ FAIL - Error: {e}")

# Test 5: Get Recommendations
print("\n[5] Get Emotion-Based Recommendations")
try:
    response = requests.post(
        f"{BACKEND_URL}/api/recommendations/emotion",
        json={"emotion": "anxious", "limit": 5},
        timeout=10
    )
    if response.status_code == 200:
        recs = response.json()
        print(f"✅ PASS - Got recommendations")
        print(f"Songs: {len(recs) if isinstance(recs, list) else 'See response'}")
    else:
        print(f"❌ FAIL - Got status {response.status_code}")
except Exception as e:
    print(f"❌ FAIL - Error: {e}")

print("\n" + "=" * 60)
print("Testing Complete!")
EOF

# Run the test:
python3 test_render_deploy.py
```

---

## Troubleshooting

### Issue 1: Build Fails
```bash
# Check build logs in Render dashboard
# Common causes:
# 1. Missing requirements.txt
# 2. Typo in Procfile
# 3. Wrong root directory (should be "Backend")
# 4. Python version incompatibility

# Fix: Go back to Render dashboard and check logs
```

### Issue 2: Service Crashes on Startup
```bash
# Check logs in Render dashboard → Logs tab
# Look for error messages like:
# - "ModuleNotFoundError" - Missing dependency
# - "ImportError" - Import issue
# - "Connection refused" - Database error

# Fix:
# 1. Check MONGODB_URL environment variable
# 2. Ensure MongoDB is running
# 3. Verify password in connection string
```

### Issue 3: CORS Errors from Frontend
```bash
# Error: Access to XMLHttpRequest blocked by CORS

# Fix: In Render dashboard
# 1. Go to Settings → Environment
# 2. Update CORS_ORIGINS to match your frontend URL
# 3. Trigger redeploy (auto-deploys on next git push)
```

### Issue 4: 503 Service Unavailable
```bash
# Backend is overloaded or crashed

# Fix:
# 1. Check logs in Render dashboard
# 2. Verify database connection
# 3. Restart service (in Render dashboard)
# 4. Upgrade to Standard tier if needed
```

---

## Verify Environment Variables Are Set

```bash
# In Render dashboard, under Settings → Environment
# Click each variable to verify it shows correctly
# (Passwords will be hidden, that's normal)

# Or check via API:
curl -H "Authorization: Bearer YOUR_API_TOKEN" \
  https://api.render.com/v1/services/srv-xxxxx/env-vars

# (Requires Render API token from account settings)
```

---

## Summary: What You Just Did

```
✅ Created MongoDB Atlas cluster (M0 free)
✅ Created database user for backend
✅ Generated JWT secret
✅ Prepared backend code (Procfile, .renderignore)
✅ Pushed to GitHub
✅ Created Render service
✅ Set all environment variables
✅ Deployed backend (2-5 minutes)
✅ Tested all endpoints
✅ Backend is LIVE! 🎉
```

---

## Next: Update Frontend to Use Your Backend URL

```bash
# Get your backend URL from Render dashboard:
# https://raga-rasa-backend.onrender.com

# Update frontend environment variable:
VITE_API_URL=https://raga-rasa-backend.onrender.com/api

# Deploy frontend to Vercel with this URL
# (See VERCEL_FRONTEND_DEPLOYMENT.md)
```

---

## Quick Reference: All URLs

```
Backend API:       https://raga-rasa-backend.onrender.com
Emotion Service:   https://rishi22652-emotion-recognition.hf.space
MongoDB Database:  mongodb+srv://... (secure, don't expose)
Frontend (Vercel): https://raga-rasa-soul.vercel.app (once deployed)
```

---

## Support

### Check Logs
```bash
# In Render Dashboard:
# 1. Select your service
# 2. Click "Logs" tab
# 3. View real-time logs
# 4. Search for errors
```

### Common Log Messages
```
"Service started" - ✅ Running OK
"Error: Connection refused" - ❌ Database issue
"ModuleNotFoundError" - ❌ Missing dependency
"Health check passed" - ✅ All good
```

---

**Status**: ✅ Ready to Deploy

You now have everything needed to deploy to Render!

Last Step: Go to https://render.com/dashboard and create your service 🚀
