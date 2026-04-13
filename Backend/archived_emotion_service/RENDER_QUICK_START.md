# Render Deployment - Step-by-Step Visual Guide

## Overview
```
Your Code (GitHub)
       ↓
Render Dashboard
       ↓
Build & Deploy
       ↓
Live Service URL
       ↓
Use in Backend
```

---

## The 5 Minute Deployment Process

### STEP 1: Commit & Push to GitHub (2 minutes)

```bash
cd C:\Users\rishi\raga_rasa_music

# See what's new
git status

# Stage emotion_recognition folder
git add emotion_recognition/

# Create commit message
git commit -m "Add emotion_recognition service for Render deployment"

# Push to GitHub
git push origin main
```

**Expected Output:**
```
[main xxxxxxx] Add emotion_recognition service for Render deployment
 6 files changed, 150 insertions(+)
 create mode 100644 emotion_recognition/__init__.py
 create mode 100644_/emotion_recognition/api.py
 ...
```

---

### STEP 2: Log into Render Dashboard (30 seconds)

1. Open: https://dashboard.render.com
2. Sign in with your account
3. You should see your existing services (if any)

---

### STEP 3: Create New Web Service (1 minute)

```
Render Dashboard
    ↓
Click "New +" (top right)
    ↓
Select "Web Service"
    ↓
Click "Connect Repository"
    ↓
Select "raga_rasa_music"
    ↓
Click "Connect"
```

---

### STEP 4: Fill Configuration Form (1.5 minutes)

```
┌─────────────────────────────────────────────┐
│  CREATE NEW WEB SERVICE                     │
├─────────────────────────────────────────────┤
│                                             │
│  Name:                                      │
│  ┌─────────────────────────────────────┐  │
│  │ emotion-recognition                 │  │
│  └─────────────────────────────────────┘  │
│                                             │
│  Region: Singapore (Singapore)              │
│                                             │
│  Branch:                                    │
│  ┌─────────────────────────────────────┐  │
│  │ main                                │  │
│  └─────────────────────────────────────┘  │
│                                             │
│  Root Directory:                            │
│  ┌─────────────────────────────────────┐  │
│  │ emotion_recognition                 │  │
│  └─────────────────────────────────────┘  │
│                                             │
│  Environment: Python 3                      │
│                                             │
│  Build Command:                             │
│  ┌─────────────────────────────────────┐  │
│  │ pip install -r requirements.txt     │  │
│  └─────────────────────────────────────┘  │
│                                             │
│  Start Command:                             │
│  ┌─────────────────────────────────────┐  │
│  │ gunicorn --workers 4 \               │  │
│  │ --bind 0.0.0.0:$PORT api:app        │  │
│  └─────────────────────────────────────┘  │
│                                             │
│  [ Create Web Service ]                    │
│                                             │
└─────────────────────────────────────────────┘
```

---

### STEP 5: Watch Deployment (2-5 minutes)

```
Status Page will show:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Building...
 ▓▓▓░░░░░░  Building image
 
Deploying...
 ▓▓▓▓▓▓░░░░  Installing dependencies
 
 ▓▓▓▓▓▓▓░░░  Running build
 
 ▓▓▓▓▓▓▓▓▓░  Starting service

✅ LIVE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Service URL: https://emotion-recognition-xxxx.onrender.com
```

---

## What Gets Deployed?

```
emotion_recognition/
├── api.py                    ← Main Flask app
├── emotion_detector.py       ← ML model code
├── __init__.py              ← Package marker
├── requirements.txt         ← Dependencies
├── Procfile                 ← Render config
├── runtime.txt              ← Python version
└── RENDER_DEPLOYMENT_GUIDE.md ← This guide
```

---

## After Deployment: Testing

### Via Terminal (curl)

```bash
# 1. Check if service is alive
curl https://emotion-recognition-xxxx.onrender.com/health

# Expected response:
# {"status":"ok","service":"emotion-recognition"}

# 2. List available endpoints
curl https://emotion-recognition-xxxx.onrender.com/

# Expected response:
# {
#   "service": "Emotion Recognition API",
#   "status": "running",
#   "version": "1.0.0",
#   "endpoints": {
#     "GET /": "Service info",
#     "GET /health": "Health check",
#     "POST /detect": "Detect emotion from image"
#   }
# }
```

### Via Browser

Simply visit:
```
https://emotion-recognition-xxxx.onrender.com/
```

You'll see the service info as JSON.

---

## Configuration Reference

| Part | Value | Why? |
|------|-------|------|
| **Name** | `emotion-recognition` | Identifies your service |
| **Root Directory** | `emotion_recognition` | Where code lives in repo |
| **Build Command** | `pip install -r requirements.txt` | Install dependencies |
| **Start Command** | `gunicorn --workers 4 --bind 0.0.0.0:$PORT api:app` | Run Flask app with gunicorn |
| **Branch** | `main` | Which branch to deploy from |
| **Environment** | `Python 3` | Runtime environment |

---

## Connection from Backend

Once deployed, update your Backend to use the service:

### In `Backend/.env` or `Backend/.env.production`:

```env
EMOTION_SERVICE_URL=https://emotion-recognition-xxxx.onrender.com
EMOTION_SERVICE_ENDPOINT=/detect
```

### In `Backend/app/services/external_emotion.py`:

```python
class ExternalEmotionServiceClient:
    def __init__(self):
        self.base_url = settings.EMOTION_SERVICE_URL
        # This now points to your Render-deployed service!
```

---

## Common Issues & Fixes

### ❌ "Build failed"
**Check:** Root Directory is `emotion_recognition`, not `.` or `Backend`

### ❌ "Service keeps crashing"
**Check:** Logs (click service → Logs) for import errors
**Fix:** Make sure all imports in `api.py` and `emotion_detector.py` are in `requirements.txt`

### ❌ "Service is very slow"
**Expected:** First request takes 10-15 seconds (loading HSEmotion model)
**Fix:** Keep-alive pings to prevent cold stops

### ❌ "Port error: Address already in use"
**Wrong Start Command**. Should be:
```
gunicorn --workers 4 --bind 0.0.0.0:$PORT api:app
```
NOT:
```
python api.py  # ❌ This will fail on Render
```

---

## Monitoring Your Service

### In Render Dashboard:

1. Click your service name
2. See **Logs** tab → Live output
3. See **Events** tab → Deployment history
4. See **Metrics** tab → CPU, Memory usage

---

## Auto-Deployment on Code Changes

Render automatically redeploys when you push to GitHub:

```bash
# Make a code change
# Commit and push
git push origin main

# Render will automatically:
# 1. Detect new commit
# 2. Pull latest code
# 3. Rebuild and deploy
# (no manual action needed!)
```

---

## Final Checklist

- [ ] Pushed `emotion_recognition` folder to GitHub
- [ ] Created Web Service on Render
- [ ] Set Root Directory to `emotion_recognition`
- [ ] Service is green and running
- [ ] Health check responds with 200 OK
- [ ] Got service URL from Render
- [ ] Updated Backend with service URL

---

## Your Service URL Pattern

```
https://emotion-recognition-xxxx.onrender.com

Replace xxxx with random string Render assigns
```

---

## Need Help?

1. **Deployment Issues**: Check Render Logs tab
2. **Code Issues**: See `RENDER_DEPLOYMENT_GUIDE.md`
3. **Stuck?**: Check that:
   - GitHub has the emotion_recognition folder
   - Root Directory is set correctly
   - All dependencies are in requirements.txt

Good luck! 🚀
