# Hugging Face Spaces Deployment Guide - Emotion Recognition Service

## Overview

This guide walks you through deploying the RagaRasa emotion recognition service to Hugging Face Spaces using Docker.

**Time Required:** 10-15 minutes
**Cost:** FREE (on CPU Basic tier)

---

## Step 1: Create a Hugging Face Account

1. Go to https://huggingface.co/
2. Click **Sign Up** (if you don't have an account)
3. Create your account with email/GitHub/Google

---

## Step 2: Create a New Space

1. Go to https://huggingface.co/spaces
2. Click **Create new Space** button (top right)
3. Fill in the form:
   - **Space name:** `raga-rasa-emotion` (or any name you prefer)
   - **License:** MIT (or Apache 2.0)
   - **Space SDK:** Select **Docker**
   - **Visibility:** Public (recommended for easier testing)
4. Click **Create Space**

You'll now be on your new Space's page. The URL will look like:
```
https://huggingface.co/spaces/[YOUR_USERNAME]/raga-rasa-emotion
```

---

## Step 3: Clone the Space Repository

Open your terminal and run:

```bash
git clone https://huggingface.co/spaces/[YOUR_USERNAME]/raga-rasa-emotion
cd raga-rasa-emotion
```

Replace `[YOUR_USERNAME]` with your actual HF username.

---

## Step 4: Copy the Emotion Recognition Code

Copy these files from the original repository to your cloned Space:

```bash
# From the raga_rasa_music/emotion_recognition directory:
cp emotion_recognition/api.py ./
cp emotion_recognition/emotion_detector.py ./
cp emotion_recognition/requirements.txt ./
cp emotion_recognition/Dockerfile ./
cp emotion_recognition/runtime.txt ./  # Optional
```

Or manually create these files in your Space repository.

---

## Step 5: Create/Update Files

### `Dockerfile`
Should contain the Docker configuration (already in emotion_recognition folder or created above)

### `requirements.txt`
```
Flask==3.0.0
Flask-CORS==4.0.0
hsemotion>=0.1.0
opencv-python>=4.10.0
numpy>=1.26.0
gunicorn>=21.0.0
requests>=2.31.0
```

### `api.py`
Copy from `emotion_recognition/api.py` (contains Flask app with emotion detection endpoints)

### `emotion_detector.py`
Copy from `emotion_recognition/emotion_detector.py` (contains EmotionDetector class)

---

## Step 6: Push to Hugging Face

```bash
cd raga-rasa-emotion

# Stage changes
git add .

# Commit
git commit -m "Initial emotion recognition service deployment"

# Push to HF Spaces (auto-deploys)
git push
```

HF Spaces will automatically:
1. Detect the Dockerfile
2. Build the Docker image
3. Deploy the service
4. Assign a public URL

**This takes about 3-5 minutes.**

---

## Step 7: Get Your Public URL

Once deployment completes:

1. Go to your Space page: https://huggingface.co/spaces/[YOUR_USERNAME]/raga-rasa-emotion
2. Look for **Embed** button or view the Space details
3. Your public URL will be: `https://[username]-raga-rasa-emotion.hf.space`

**Important:** Write down this URL - you'll need it for the backend configuration!

---

## Step 8: Test the Service

Open a terminal and test your deployed service:

```bash
# Health check
curl https://[username]-raga-rasa-emotion.hf.space/health

# Should return:
# {"status": "ok", "service": "emotion-recognition", "detector_initialized": true}
```

---

## Step 9: Configure Backend

Now that your emotion service is deployed, update the **backend** `.env` file:

```env
EMOTION_SERVICE_URL=https://[username]-raga-rasa-emotion.hf.space
```

Replace `[username]` with your HF username.

---

## Common Issues & Troubleshooting

### Issue: Space is sleeping/not responding

**Solution:**
- HF Spaces on free tier may sleep after inactivity
- The first request after sleep will be slow (30-60 seconds)
- To prevent sleeping, upgrade to paid tier (cheapest: ~$3.50/month CPU Upgrade)
- Or, you can test with paid tier for a bit then downgrade

### Issue: "Service is building"

**Solution:**
- Wait for deployment to complete (usually 3-5 minutes)
- Check the **Build** tab in Space settings for logs
- If build fails, check the Docker build logs for errors

### Issue: Model download fails

**Solution:**
- First startup might take 2-3 minutes as it downloads emotion model
- Ensure `requirements.txt` has `hsemotion>=0.1.0`
- Check Space logs for errors

### Issue: CORS errors from frontend

**Solution:**
- The API already has `CORS(app)` enabled in `api.py`
- If still getting CORS errors, the backend (Koyeb) needs to allow HF Spaces URL
- Backend CORS config should include: `https://.*\.hf\.space`

---

## Endpoints Available

Once deployed, your service provides:

```
GET  /                           - Service info
GET  /health                     - Health check
POST /detect                     - Detect emotion from base64 image
POST /emotion/detect             - Alias for /detect
```

### Example: Detect Emotion

```bash
curl -X POST https://[username]-raga-rasa-emotion.hf.space/detect \
  -H "Content-Type: application/json" \
  -d '{
    "image": "data:image/jpeg;base64,/9j/4AAQSkZJRg..."
  }'

# Response:
# {
#   "emotion": "happy",
#   "confidence": 0.95,
#   "dominant": "Happy",
#   "raw_dominant": "happy",
#   "emotions": {...},
#   "is_brave": false
# }
```

---

## Next Steps

1. ✅ Emotion service deployed on HF Spaces
2. ⬜ Update backend configuration with HF Spaces URL
3. ⬜ Deploy backend on Koyeb
4. ⬜ Deploy frontend on Vercel (already done)
5. ⬜ Test end-to-end integration

See `KOYEB_BACKEND_DEPLOYMENT.md` for backend setup instructions.

---

## Support & References

- HF Spaces Documentation: https://huggingface.co/docs/hub/spaces-overview
- HF Spaces Docker Guide: https://huggingface.co/docs/hub/spaces-sdks-docker
- Emotion Recognition Model: https://github.com/HSEmotion/HSEmotion

---

**Your emotion service is now live and ready for integration!**
