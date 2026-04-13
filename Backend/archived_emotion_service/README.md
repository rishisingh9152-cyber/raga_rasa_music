# Emotion Recognition Service - Render Deployment Summary

## What's Ready to Deploy

Your `emotion_recognition` service is fully configured and ready for Render deployment.

```
emotion_recognition/
├── api.py                          Flask REST API
├── emotion_detector.py             ML model code (HSEmotion)
├── requirements.txt                Dependencies (includes gunicorn)
├── runtime.txt                     Python 3.10.15
├── Procfile                        Deployment config
├── __init__.py                     Python package marker
├── RENDER_DEPLOYMENT_GUIDE.md      📖 Detailed guide
├── RENDER_QUICK_START.md           📖 Visual quick start
└── DEPLOYMENT_CHECKLIST.md         ✅ Step-by-step checklist
```

---

## Quick Deployment (5 Minutes)

### Step 1: Push to GitHub
```bash
cd C:\Users\rishi\raga_rasa_music
git add emotion_recognition/
git commit -m "Add emotion_recognition service for Render"
git push origin main
```

### Step 2: Deploy on Render
1. Go to https://dashboard.render.com
2. Click **New +** → **Web Service**
3. Select your GitHub repo (`raga_rasa_music`)
4. Fill in:
   - **Name**: `emotion-recognition`
   - **Root Directory**: `emotion_recognition`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --workers 4 --bind 0.0.0.0:$PORT api:app`
5. Click **Create Web Service**
6. Wait 2-5 minutes for deployment to complete

### Step 3: Get Your Service URL
- Copy URL from Render dashboard (format: `https://emotion-recognition-xxxx.onrender.com`)

### Step 4: Test It
```bash
curl https://emotion-recognition-xxxx.onrender.com/health
# Should respond: {"status":"ok","service":"emotion-recognition"}
```

### Step 5: Update Backend
In `Backend/.env.production` or Render env vars:
```
EMOTION_SERVICE_URL=https://emotion-recognition-xxxx.onrender.com
```

---

## API Endpoints

Once deployed, your service has 3 endpoints:

### 1. Health Check
```bash
GET https://emotion-recognition-xxxx.onrender.com/health
# Response: {"status":"ok","service":"emotion-recognition"}
```

### 2. Service Info
```bash
GET https://emotion-recognition-xxxx.onrender.com/
# Response: Service description and available endpoints
```

### 3. Emotion Detection
```bash
POST https://emotion-recognition-xxxx.onrender.com/detect
Content-Type: application/json

{
  "image": "base64_encoded_image_data_here"
}

# Response:
{
  "emotion": "happy",
  "confidence": 0.95,
  "dominant": "happy",
  "raw_dominant": "happy"
}
```

---

## Configuration Files Explained

### `requirements.txt`
```
Flask==3.0.0              # Web framework
Flask-CORS==4.0.0         # Cross-origin requests
hsemotion>=0.1.0          # Emotion detection model
opencv-python>=4.10.0     # Image processing
numpy>=1.26.0             # Numerical operations
gunicorn>=21.0.0          # Production WSGI server (REQUIRED for Render)
```

### `Procfile`
```
web: python api.py
```
This tells Render how to start the service (Render overrides with gunicorn command).

### `runtime.txt`
```
python-3.10.15
```
Specifies Python version to use.

### `api.py`
Flask REST API with 3 endpoints serving the emotion detection.

### `emotion_detector.py`
Core ML model using HSEmotion for facial emotion recognition.

---

## Important Notes

### 🔴 Critical: Root Directory Must Be `emotion_recognition`
When setting up Render, set:
- **Root Directory**: `emotion_recognition` (NOT `.` or `Backend`)

This tells Render where your service code is in the repository.

### 🟡 Cold Start Performance
- **First request**: 10-15 seconds (loading HSEmotion model)
- **Subsequent requests**: 1-2 seconds
- This is normal and expected
- Keep the service warm with periodic health checks to avoid cold stops

### 🟢 Production Ready
- Uses **gunicorn** (production WSGI server)
- Configured with **4 workers** for concurrency
- Includes **CORS** headers for cross-origin requests
- Ready for production use

---

## Integration with Backend

Your Backend (`raga_rasa_music/Backend`) can now call this service:

```python
# In Backend/app/services/external_emotion.py

import httpx
import os

EMOTION_SERVICE_URL = os.getenv(
    "EMOTION_SERVICE_URL",
    "https://emotion-recognition-xxxx.onrender.com"
)

async def detect_emotion(base64_image: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{EMOTION_SERVICE_URL}/detect",
            json={"image": base64_image},
            timeout=60.0
        )
        return response.json()
```

---

## Troubleshooting

### "Build failed"
- Check that **Root Directory** is exactly `emotion_recognition`
- Check Render Logs for specific error message
- Verify all files are in GitHub: emotion_recognition/api.py, requirements.txt, etc.

### "Service keeps crashing"
- Click service → **Logs** tab
- Look for Python import errors
- Verify all imports are in requirements.txt
- Test locally: `cd emotion_recognition && pip install -r requirements.txt && python api.py`

### "Service takes forever to respond"
- Expected: First request 10-15 seconds (model loading)
- Subsequent requests should be 1-2 seconds
- Check Logs for errors if consistently slow

### "API returns error"
- Check that your request has correct format:
  ```json
  {"image": "base64_image_data"}
  ```
- Test health endpoint first: `/health` should always work

---

## Monitoring Your Service

After deployment:

1. **View Logs**: Click service → **Logs** tab
2. **Check Metrics**: Click service → **Metrics** tab
3. **Restart Service**: Click service → **Restart Service** button
4. **Redeploy Code**: Click service → **Manual Deploy** → **Redeploy Latest Commit**

---

## Auto-Updates

When you push new code to GitHub:
```bash
git push origin main
```

Render automatically:
1. Detects the new commit
2. Rebuilds the service
3. Deploys the changes

No manual action needed! ✨

---

## Files for Reference

- **RENDER_DEPLOYMENT_GUIDE.md** - Detailed step-by-step guide
- **RENDER_QUICK_START.md** - Visual quick-start guide with ASCII diagrams
- **DEPLOYMENT_CHECKLIST.md** - Checkbox checklist for deployment

---

## Next Steps

1. ✅ Push emotion_recognition to GitHub
2. ✅ Deploy to Render
3. ✅ Get your service URL
4. ✅ Update Backend with service URL
5. ✅ Test end-to-end

---

## Your Service is Ready! 🚀

Everything is configured and ready to go. Just:

1. Push to GitHub
2. Deploy on Render
3. Get your URL
4. Use it in your Backend

The emotion_recognition service will be live in ~5 minutes.

Questions? Check the deployment guides above.

Good luck! 🎉
