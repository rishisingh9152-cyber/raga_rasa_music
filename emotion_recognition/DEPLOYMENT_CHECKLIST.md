# Render Deployment Checklist

## Pre-Deployment (Do This First)

- [ ] **GitHub Setup**
  - [ ] Commit emotion_recognition folder to git
  - [ ] Push to GitHub: `git push origin main`
  - [ ] Verify on GitHub.com that emotion_recognition folder is visible

- [ ] **Code Verification**
  - [ ] `emotion_recognition/api.py` exists
  - [ ] `emotion_recognition/emotion_detector.py` exists
  - [ ] `emotion_recognition/requirements.txt` has gunicorn
  - [ ] `emotion_recognition/Procfile` exists with: `web: python api.py`
  - [ ] `emotion_recognition/runtime.txt` exists with: `python-3.10.15`

---

## Deployment Steps (5 minutes)

### 1. Go to Render Dashboard
- [ ] Open https://dashboard.render.com
- [ ] Sign in with your account

### 2. Create New Service
- [ ] Click **New +** button (top right)
- [ ] Click **Web Service**
- [ ] Click **Connect Repository**

### 3. Select Repository
- [ ] Authorize Render (if needed)
- [ ] Select **raga_rasa_music** repository
- [ ] Click **Connect**

### 4. Configure Service
- [ ] **Name**: `emotion-recognition`
- [ ] **Region**: Keep default (nearest to you)
- [ ] **Branch**: `main`
- [ ] **Root Directory**: `emotion_recognition` ⚠️ IMPORTANT
- [ ] **Environment**: `Python 3`

### 5. Set Commands
- [ ] **Build Command**: 
  ```
  pip install -r requirements.txt
  ```
- [ ] **Start Command**: 
  ```
  gunicorn --workers 4 --bind 0.0.0.0:$PORT api:app
  ```

### 6. Deploy
- [ ] Select plan: **Starter** (free) or **Standard** (paid)
- [ ] Click **Create Web Service**
- [ ] Watch the build progress (2-5 minutes)

---

## Post-Deployment Verification

### 1. Service Status
- [ ] Status shows green checkmark ✓
- [ ] "Live" button is available
- [ ] No error messages in Logs

### 2. Test the Service
Run these in terminal (replace xxxx with your actual Render URL):

```bash
# Test 1: Health Check
curl https://emotion-recognition-xxxx.onrender.com/health

# Expected: {"status":"ok","service":"emotion-recognition"}

# Test 2: Service Info
curl https://emotion-recognition-xxxx.onrender.com/

# Expected: JSON with endpoints list

# Test 3: Emotion Detection (without image)
curl -X POST https://emotion-recognition-xxxx.onrender.com/detect \
  -H "Content-Type: application/json" \
  -d '{"image":"test"}'

# Expected: Some response (may be error, that's ok for now)
```

- [ ] At least Test 1 and 2 respond
- [ ] No 500 errors

### 3. Check Logs
- [ ] Click service → **Logs** tab
- [ ] No error messages
- [ ] See startup messages like "* Running on..."

---

## Integration with Backend

### 1. Get Your Service URL
- [ ] Copy the service URL from Render dashboard
- [ ] Format: `https://emotion-recognition-xxxx.onrender.com`

### 2. Update Backend Configuration

In `Backend/.env.production`:
```
EMOTION_SERVICE_URL=https://emotion-recognition-xxxx.onrender.com
EMOTION_SERVICE_ENDPOINT=/detect
USE_EXTERNAL_EMOTION_SERVICE=true
```

OR in Render Backend deployment environment variables:
- [ ] Set `EMOTION_SERVICE_URL=https://emotion-recognition-xxxx.onrender.com`

### 3. Test Backend Connection
```bash
# Test that backend can reach the emotion service
python -c "
import requests
url = 'https://emotion-recognition-xxxx.onrender.com/health'
resp = requests.get(url)
print(resp.status_code, resp.json())
"
```
- [ ] Response is 200 with {"status":"ok","service":"emotion-recognition"}

---

## Monitoring (Optional)

- [ ] Set up periodic health checks (optional)
- [ ] Monitor Render Metrics tab
- [ ] Check logs regularly for errors

---

## Troubleshooting Checklist

If something goes wrong:

### Deployment Failed?
- [ ] Check **Logs** tab for error message
- [ ] Verify Root Directory is exactly `emotion_recognition`
- [ ] Verify all files exist in emotion_recognition folder
- [ ] Try redeploying: Click **Manual Deploy** → **Redeploy Latest Commit**

### Service Keeps Crashing?
- [ ] Check **Logs** tab for Python errors
- [ ] Verify Start Command is exactly:
  ```
  gunicorn --workers 4 --bind 0.0.0.0:$PORT api:app
  ```
- [ ] Verify `api.py` has no syntax errors (test locally)
- [ ] Verify all imports in `api.py` are in `requirements.txt`

### Service Doesn't Respond?
- [ ] Wait 30 seconds (cold start)
- [ ] Check service status is "Live" (green)
- [ ] Try health check: `curl https://..../health`
- [ ] Check **Metrics** tab - is CPU spiking?

### Slow Response?
- [ ] Expected: First request 10-15 seconds
- [ ] Normal: Subsequent requests 1-2 seconds
- [ ] If consistently slow: Check Logs for errors

---

## After Everything Works

### Auto-Deploy Future Changes
```bash
# Just push code to main
git push origin main
# Render automatically redeploys!
```

### Use in Your Application
```python
# In Backend code
EMOTION_SERVICE_URL = "https://emotion-recognition-xxxx.onrender.com"

# Call it
response = requests.post(
    f"{EMOTION_SERVICE_URL}/detect",
    json={"image": base64_image}
)
```

---

## Quick Reference

| What | Where | How |
|------|-------|-----|
| **Service URL** | Render Dashboard Home Page | Copy from top |
| **Logs** | Service Page → Logs Tab | See real-time output |
| **Restart** | Service Page → Restart Button | Restart service |
| **Settings** | Service Page → Settings | Change configuration |
| **Redeploy** | Service Page → Manual Deploy | Force redeploy |
| **Metrics** | Service Page → Metrics | CPU, Memory, Network |

---

## Done! ✅

Once you've checked everything off, your emotion_recognition service is live and ready to use.

Your Backend can now call it at:
```
https://emotion-recognition-xxxx.onrender.com/detect
```

---

## Support

**Render Help**: https://render.com/docs
**Common Issues**: See RENDER_DEPLOYMENT_GUIDE.md

Good luck! 🚀
