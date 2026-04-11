# Day 2b: Render.com Deployment - Action Steps

**Status**: Ready to deploy both services  
**Date**: April 11, 2026  
**Prerequisites**: Render.com account created with GitHub authorization

---

## Quick Summary

You will deploy **2 services** to Render.com:
1. **Emotion Recognition Service** (Flask) - Emotion detection API
2. **Backend Service** (FastAPI) - Main application server

Expected deployment time: 20-30 minutes total

---

## Phase 1: Deploy Emotion Recognition Service

### Step 1: Log into Render Dashboard
- Go to https://dashboard.render.com
- Sign in with your GitHub account

### Step 2: Create New Web Service
1. Click **"+ New"** button (top right)
2. Select **"Web Service"**

### Step 3: Connect Repository
1. You'll see a page asking you to connect a GitHub repo
2. Look for: `rishi17205-ops/raga_rasa_music_therapy`
3. Click to connect it
4. Select the repo
5. Click **"Connect"**

### Step 4: Configure Emotion Service

Fill in the following settings:

**Name**: 
```
emotion-recognition
```

**Root Directory**: 
```
emotion_recognition
```

**Build Command**: 
```
pip install -r requirements.txt
```

**Start Command**: 
```
python api.py
```

**Instance Type**: 
```
Free
```

**Scroll down** and click **"Create Web Service"**

### Step 5: Wait for Deployment
- Render will start building your service
- You'll see: "Building service..."
- This takes 5-10 minutes (it's downloading PyTorch, so be patient)
- When complete, you'll see a green "Active" status

### Step 6: Get Your Service URL

Once active:
- Look at the top of the service page
- You'll see a URL like: `https://emotion-recognition-xxxxx.onrender.com`
- **Copy this URL - you need it for the backend!**

### Step 7: Test Emotion Service

Open your terminal and test:

```bash
curl https://emotion-recognition-xxxxx.onrender.com/health
```

Expected response:
```json
{"status":"ok","model":"HSEmotion enet_b0_8_best_afew"}
```

If you see this, the emotion service is working!

---

## Phase 2: Deploy Backend Service

### Step 1: Create Another Web Service
1. Go back to dashboard
2. Click **"+ New"** → **"Web Service"**
3. Select the same repository again

### Step 2: Configure Backend Service

Fill in these settings:

**Name**:
```
raga-rasa-backend
```

**Root Directory** (leave empty or use `.` for root)
```
.
```

**Build Command**:
```
pip install -r Backend/requirements.txt
```

**Start Command**:
```
cd Backend && python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

**Instance Type**:
```
Free
```

### Step 3: Add Environment Variables

This is important! Click the **"Environment"** tab and add these variables:

```
# MongoDB Connection
MONGODB_URL=mongodb+srv://Rishi123:Rishi_123@majorproject.lpwzhzc.mongodb.net/?appName=MajorProject
DATABASE_NAME=raga_rasa

# Emotion Service (USE THE URL FROM STEP 1!)
USE_EXTERNAL_EMOTION_SERVICE=True
EMOTION_SERVICE_URL=https://emotion-recognition-xxxxx.onrender.com
EMOTION_SERVICE_ENDPOINT=/detect
EMOTION_CONFIDENCE_THRESHOLD=0.3

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# JWT Secret (already generated)
JWT_SECRET_KEY=dt_aRvdBIakTz2GI_qC4U1EqVVgmq4nrRDSc5XX73iY

# Storage & CORS
STORAGE_PROVIDER=local
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Environment
DEBUG=False
```

**Important**: Replace `https://emotion-recognition-xxxxx.onrender.com` with the actual URL from Step 1!

### Step 4: Deploy Backend
- Click **"Create Web Service"**
- Wait for build (5-10 minutes)
- You'll get another URL like: `https://raga-rasa-backend-xxxxx.onrender.com`

---

## Phase 3: Verification

### Test Emotion Service
```bash
curl https://emotion-recognition-xxxxx.onrender.com/health
```
Response: `{"status":"ok","model":"HSEmotion enet_b0_8_best_afew"}`

### Test Backend Service
```bash
curl https://raga-rasa-backend-xxxxx.onrender.com/health
```
Response: Should return health status

### Check Backend Logs
In Render dashboard:
1. Click on `raga-rasa-backend` service
2. Go to **"Logs"** tab
3. Look for any errors (red text)
4. Should see: "Application startup complete"

---

## Troubleshooting

**Emotion Service won't deploy:**
- Check build logs for PyTorch download issues
- Free tier has limited resources; deployment may take 15+ minutes
- Check that `emotion_recognition/requirements.txt` exists

**Backend service fails:**
- Check MongoDB connection string (should match exactly)
- Verify `EMOTION_SERVICE_URL` is correct (don't forget `https://`)
- Check `Backend/requirements.txt` exists

**Getting "Error: Unsupported Python Version":**
- Check Backend/main.py and ensure it's Python 3.8+

---

## Files & Credentials to Verify

**MongoDB Atlas**:
- Connection String: `mongodb+srv://Rishi123:Rishi_123@majorproject.lpwzhzc.mongodb.net/`
- Database: `raga_rasa`
- Username: `Rishi123`
- Password: `Rishi_123`

**GitHub Repo**:
- Repo: https://github.com/rishi17205-ops/raga_rasa_music_therapy
- Branch: main
- Status: Code pushed (commit: b28ab40)

**JWT Secret**:
- Already configured in backend
- Don't need to change

---

## Next Steps (After Deployment)

### Day 2c: GitHub OAuth (30 minutes)
- Create OAuth app at https://github.com/settings/developers
- Get Client ID and Secret
- Add to Render backend environment

### Day 2d: Dropbox Setup (2-3 hours)
- Create app at https://www.dropbox.com/developers/apps
- Setup cloud storage

### Day 3: Vercel Frontend
- Deploy frontend to Vercel
- Update API endpoints to use Render URLs

---

## Important Notes

1. **MongoDB IP Whitelist**: Currently allows all IPs (0.0.0.0/0)
   - For production: restrict to Render IP ranges
   - How: MongoDB Atlas → Security → Network Access

2. **Free Tier Limits**:
   - Services spin down after 15 minutes of inactivity
   - First request may be slow (cold start)
   - This is normal and acceptable

3. **Build Times**:
   - First build: 10-15 minutes (downloading dependencies)
   - Redeploys: 5-10 minutes
   - Be patient!

4. **Logs**:
   - Always check logs if something fails
   - Click service → Logs tab
   - Search for "error" (case-insensitive)

---

## Deployment Checklist

- [ ] Emotion service deployed and active
- [ ] Emotion service `/health` returns OK
- [ ] Backend service deployed and active
- [ ] Backend service `/health` returns OK
- [ ] Environment variables correctly set
- [ ] MongoDB connection working
- [ ] No errors in backend logs
- [ ] Got Emotion Service URL and saved it
- [ ] Got Backend Service URL and saved it

---

## After Successful Deployment

Save these URLs:
- **Emotion Service**: https://emotion-recognition-xxxxx.onrender.com
- **Backend Service**: https://raga-rasa-backend-xxxxx.onrender.com

You'll need these for Day 2c and Day 3!

---

**Created**: April 11, 2026  
**Status**: Ready to deploy
