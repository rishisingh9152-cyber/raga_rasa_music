# Render.com Deployment Guide - Complete Walkthrough

## **PREREQUISITES**

Before starting, have ready:
- [ ] MongoDB Atlas connection string (from previous step)
- [ ] GitHub account with repo access
- [ ] This project pushed to GitHub (will check)

---

## **STEP 1: Create Render Account**

### Sign Up
1. Go to https://render.com
2. Click "Get Started" or "Sign Up"
3. Select "Sign up with GitHub"
4. Authorize Render to access your repos
5. Create account and confirm email

### Verify GitHub Connection
1. In Render dashboard, go to "Settings" → "GitHub"
2. You should see your GitHub account connected
3. Grant access to repository if prompted

---

## **STEP 2: Prepare Repository for Deployment**

### Check Your GitHub Repo
1. Go to your GitHub project
2. Ensure `Backend/` folder exists with:
   - [ ] `main.py`
   - [ ] `requirements.txt`
   - [ ] `app/` folder with routes, services, models
3. Ensure `emotion_service/` folder exists with:
   - [ ] `app.py` (or main entry point)
   - [ ] `requirements.txt`

### Add Environment Files to Gitignore (CRITICAL!)
Open `.gitignore` and ensure these are ignored:
```
*.env
.env
.env.local
.env.production
.env.*.local
```

**Never commit secrets to GitHub!**

---

## **STEP 3: Create Emotion Service on Render**

### Create New Service
1. In Render dashboard, click "+ New"
2. Select "Web Service"
3. Connect to your GitHub repo
4. Fill in:
   - **Name**: `emotion-service`
   - **Branch**: `main`
   - **Runtime**: `Python 3.11`
   - **Build Command**: 
     ```
     cd emotion_service && pip install -r requirements.txt
     ```
   - **Start Command**:
     ```
     cd emotion_service && python app.py
     ```
   - **Plan**: Free (starts instantly)
   - **Region**: Same as closest to you

### Add Environment Variables
1. Scroll to "Environment" section
2. Add variables (click "+ Add Environment Variable"):

```
FLASK_ENV=production
PORT=5000
DEBUG=False
```

3. Click "Create Web Service"

### Wait for Deployment
- Initial build: 3-5 minutes
- You'll see logs as it builds
- When complete, you'll get a public URL like:
  ```
  https://emotion-service-xxxxx.onrender.com
  ```
  
**✅ Copy this URL** - you'll need it for backend!

### Test Emotion Service
```bash
curl https://emotion-service-xxxxx.onrender.com/health
```

Expected response:
```json
{"status": "healthy"}
```

---

## **STEP 4: Create Backend Service on Render**

### Create New Service
1. In Render dashboard, click "+ New"
2. Select "Web Service"
3. Connect to your GitHub repo
4. Fill in:
   - **Name**: `raga-rasa-backend`
   - **Branch**: `main`
   - **Runtime**: `Python 3.11`
   - **Build Command**:
     ```
     pip install -r Backend/requirements.txt
     ```
   - **Start Command**:
     ```
     cd Backend && python -m uvicorn main:app --host 0.0.0.0 --port 8000
     ```
   - **Plan**: Free
   - **Region**: Same as emotion service

### Add Environment Variables

Click "Add Environment Variable" for each:

```
# Database
MONGODB_URL=mongodb+srv://ragarasa:MySecurePassword123@raga-rasa.xxxxx.mongodb.net/?retryWrites=true&w=majority
DATABASE_NAME=raga_rasa

# Emotion Service (use the URL from previous step)
USE_EXTERNAL_EMOTION_SERVICE=True
EMOTION_SERVICE_URL=https://emotion-service-xxxxx.onrender.com
EMOTION_SERVICE_ENDPOINT=/detect
EMOTION_CONFIDENCE_THRESHOLD=0.3

# API
API_HOST=0.0.0.0
API_PORT=8000

# Storage (Dropbox - we'll add token later)
STORAGE_PROVIDER=local
STORAGE_BASE_PATH=./Songs/
DROPBOX_ACCESS_TOKEN=

# JWT & Auth
JWT_SECRET_KEY=dt_aRvdBIakTz2GI_qC4U1EqVVgmq4nrRDSc5XX73iY
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# CORS (for your Vercel domain - update later)
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# GitHub OAuth (we'll add these later)
GITHUB_CLIENT_ID=
GITHUB_CLIENT_SECRET=

# Logging
DEBUG=False
```

### Create Service
1. Click "Create Web Service"
2. Wait for deployment (5-10 minutes)
3. You'll get URL like:
   ```
   https://raga-rasa-backend-xxxxx.onrender.com
   ```

**✅ Copy this URL** - you'll need it for frontend!

### Test Backend
```bash
curl https://raga-rasa-backend-xxxxx.onrender.com/health
```

Expected response:
```json
{"status": "healthy", "service": "RagaRasa Music Therapy Backend"}
```

---

## **STEP 5: Update Backend with Emotion Service URL**

After emotion service is running:

1. In Render backend dashboard, go to "Environment"
2. Find `EMOTION_SERVICE_URL`
3. Update it to your emotion service public URL:
   ```
   EMOTION_SERVICE_URL=https://emotion-service-xxxxx.onrender.com
   ```
4. Click "Save" button
5. Service will redeploy (1-2 minutes)

---

## **STEP 6: Test Backend-Emotion Integration**

```bash
curl -X POST https://raga-rasa-backend-xxxxx.onrender.com/api/emotion/detect \
  -H "Content-Type: application/json" \
  -d '{"image_base64": "data:image/jpeg;base64,..."}'
```

Or test via Python:
```python
import requests

backend_url = "https://raga-rasa-backend-xxxxx.onrender.com"
response = requests.get(f"{backend_url}/health")
print(response.json())
```

---

## **STEP 7: Configure MongoDB Network Access**

Since your backend is now on Render (IP changes), update MongoDB:

1. Go to MongoDB Atlas Dashboard
2. Click "Security" → "Network Access"
3. Click the edit (pencil) icon next to "Allow Access from Anywhere"
4. It already allows `0.0.0.0/0` which includes Render IPs ✅

---

## **ENVIRONMENT VARIABLES TO SAVE**

Create a file `DEPLOYMENT_VARIABLES.txt` (don't commit!):

```
# Save these URLs
EMOTION_SERVICE_URL=https://emotion-service-xxxxx.onrender.com
BACKEND_URL=https://raga-rasa-backend-xxxxx.onrender.com

# MongoDB Connection
MONGODB_URL=mongodb+srv://ragarasa:Password@raga-rasa.xxxxx.mongodb.net/?retryWrites=true&w=majority

# JWT Secret (keep safe!)
JWT_SECRET_KEY=dt_aRvdBIakTz2GI_qC4U1EqVVgmq4nrRDSc5XX73iY
```

---

## **MONITORING & LOGS**

### View Logs
1. In Render dashboard, click service
2. Click "Logs" tab
3. See real-time build and runtime logs

### Restart Service
1. Click service
2. Click "Settings"
3. Click "Restart service"

### View Metrics
1. Click service
2. Click "Metrics" tab
3. See CPU, memory, requests

---

## **NEXT STEPS**

Once both services are running and verified:
1. Create GitHub OAuth app (Day 2c)
2. Implement Dropbox provider (Day 2d)
3. Deploy frontend to Vercel (Day 3)
4. Add Vercel domain to CORS origins

---

## **TROUBLESHOOTING**

### Backend won't start
- Check logs for errors
- Verify all environment variables set
- Check `requirements.txt` is in `Backend/` folder

### Can't connect to MongoDB
- Verify `MONGODB_URL` is correct
- Check MongoDB IP whitelist includes `0.0.0.0/0`
- Test connection string locally first

### Emotion service not responding
- Check logs for errors
- Verify Python 3.11 is compatible with your code
- Test locally first with `python emotion_service/app.py`

### Free tier limitations
- Services sleep after 15 minutes of inactivity
- Each free service gets 750 free hours/month
- Good for development, may need upgrade for production

---

**Status**: Ready for Day 2c (GitHub OAuth) once both Render services confirmed working!
