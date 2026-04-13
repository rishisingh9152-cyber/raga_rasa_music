# Render Deployment Guide - Emotion Recognition Service

## Quick Summary
Deploy the emotion_recognition Flask service as a **Web Service** on Render.com in ~5 minutes.

---

## Prerequisites
- ✅ Render.com account
- ✅ GitHub repository with emotion_recognition code pushed
- ✅ Internet connection

---

## Step 1: Push Code to GitHub

Make sure your emotion_recognition folder is committed and pushed to GitHub:

```bash
cd C:\Users\rishi\raga_rasa_music

# Check git status
git status

# Add emotion_recognition folder
git add emotion_recognition/

# Commit
git commit -m "Add emotion_recognition standalone service"

# Push to GitHub
git push origin main
```

**Verify on GitHub:** Visit your repo and check if the `emotion_recognition/` folder is visible.

---

## Step 2: Connect Render to GitHub

1. Go to [render.com](https://render.com)
2. Sign in with your account
3. Click **New +** button (top right)
4. Select **Web Service**
5. Click **Connect Repository**
   - If not connected yet: Authorize Render to access your GitHub
   - Select your `raga_rasa_music` repository
   - Click **Connect**

---

## Step 3: Configure Render Web Service

Fill in the configuration:

| Field | Value |
|-------|-------|
| **Name** | `emotion-recognition` |
| **Root Directory** | `emotion_recognition` |
| **Environment** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn --workers 4 --bind 0.0.0.0:$PORT api:app` |
| **Branch** | `main` |

### Build Command Explanation:
```bash
pip install -r requirements.txt
```
Installs: Flask, Flask-CORS, hsemotion, opencv-python, numpy

### Start Command Explanation:
```bash
gunicorn --workers 4 --bind 0.0.0.0:$PORT api:app
```
- **gunicorn**: Production WSGI server (Render provides this by default)
- **--workers 4**: Use 4 worker processes
- **--bind 0.0.0.0:$PORT**: Listen on dynamic port
- **api:app**: Import `app` from `api.py`

---

## Step 4: Set Environment Variables (Optional)

If you need custom settings, add them:

1. Scroll down to **Environment** section
2. Click **Add Environment Variable**
3. Add variables (if needed):

| Key | Value | Note |
|-----|-------|------|
| `DEBUG` | `False` | Production mode |
| `FLASK_ENV` | `production` | Flask environment |

**Optional:** Leave these blank - defaults will work fine.

---

## Step 5: Configure Plan & Deploy

1. **Instance Type**: Select `Starter` (free tier) or `Standard` (paid)
   - Free tier: Good for testing
   - Standard: Better for production

2. Click **Create Web Service**

3. Render will now:
   - Clone your repository
   - Install dependencies
   - Build the service
   - Deploy and start the service

**Deployment Time**: ~2-5 minutes

---

## Step 6: Verify Deployment

Once deployment completes:

1. You'll see a green checkmark ✓
2. Render provides a URL like: `https://emotion-recognition-xxxx.onrender.com`

### Test the service:

```bash
# Health check
curl https://emotion-recognition-xxxx.onrender.com/health

# Response should be:
# {"status":"ok","service":"emotion-recognition"}

# Test emotion detection (with base64 image)
curl -X POST https://emotion-recognition-xxxx.onrender.com/detect \
  -H "Content-Type: application/json" \
  -d '{"image":"base64_encoded_image_here"}'
```

---

## Important Notes

### 1. **Gunicorn Required**
Update `emotion_recognition/requirements.txt` to include gunicorn:

```txt
Flask==3.0.0
Flask-CORS==4.0.0
hsemotion>=0.1.0
opencv-python>=4.10.0
numpy>=1.26.0
gunicorn>=21.0.0
```

### 2. **Cold Starts**
- First request may take 10-15 seconds (model loading)
- Subsequent requests are fast
- Consider keeping it warm with periodic health checks

### 3. **Memory Usage**
- HSEmotion model is ~150MB
- Render Starter includes 512MB (sufficient)
- For production, consider Standard instance

### 4. **API Endpoint from Backend**
Update your Backend's `external_emotion.py` to use the Render URL:

```python
# In Backend/app/services/external_emotion.py
EMOTION_SERVICE_URL = "https://emotion-recognition-xxxx.onrender.com"
```

Or use environment variable:
```python
EMOTION_SERVICE_URL = os.getenv("EMOTION_SERVICE_URL", "http://localhost:5000")
```

Then set in Backend's Render deployment:
```
EMOTION_SERVICE_URL=https://emotion-recognition-xxxx.onrender.com
```

---

## Troubleshooting

### Deployment Failed?

1. **Check Build Logs**: Click the deployment → **Logs** tab
2. Common issues:
   - Missing `requirements.txt`
   - Incorrect `Root Directory` (should be `emotion_recognition`)
   - Missing `gunicorn` in requirements

### Service Crashes After Deploy?

Check logs:
1. Click your service
2. **Logs** tab → scroll to see errors
3. Common issues:
   - Import errors (missing dependencies)
   - Port binding issues (usually fixed with correct start command)

### Slow Response Time?

- First request loads the model (~10-15s) - this is normal
- HSEmotion is heavy; consider:
  - Keep service warm with periodic pings
  - Use Standard instance for better CPU/memory
  - Pre-warm model on startup (advanced)

---

## What's Your Service URL?

Once deployed, your emotion_recognition service will be at:

```
https://emotion-recognition-xxxx.onrender.com
```

Use this URL in your Backend's `EMOTION_SERVICE_URL` configuration.

---

## Monitoring & Maintenance

1. **View Logs**: Click service → **Logs** tab
2. **Restart Service**: Click **Restart Service** button
3. **Update Code**: Push to GitHub → Render auto-redeploys
4. **Check Status**: Green = Running, Red = Failed

---

## Next Steps

1. ✅ Push emotion_recognition to GitHub
2. ✅ Deploy to Render
3. ✅ Get the service URL
4. ✅ Update Backend with service URL
5. ✅ Test emotion detection end-to-end

---

## Quick Command Reference

```bash
# Push to GitHub
git add emotion_recognition/
git commit -m "Deploy emotion_recognition"
git push origin main

# Test locally before pushing (optional)
cd emotion_recognition
pip install -r requirements.txt
python api.py
# Visit http://localhost:5000

# Test deployed service
curl https://emotion-recognition-xxxx.onrender.com/health
```

Good luck! 🚀
