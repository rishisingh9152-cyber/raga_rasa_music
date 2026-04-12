# RagaRasa - Production Deployment Guide

## Architecture Overview

The system consists of 3 main components:

1. **Frontend** (Vercel)
   - React/TypeScript application
   - Captures images from webcam
   - Sends to backend

2. **Backend API** (Render)
   - FastAPI application
   - Orchestrates emotion detection and recommendations
   - Connects to MongoDB

3. **Emotion Recognition Service** (Render - separate service)
   - Flask application
   - Uses HSEmotion model (real ML model, not fake)
   - Detects emotions from images
   - Returns emotion labels and confidence scores

4. **Database** (MongoDB Atlas)
   - Stores songs, sessions, ratings
   - Pre-populated with 19 ragas

---

## Step 1: Deploy Emotion Recognition Service on Render

### Create New Service:

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Select your GitHub repository: `raga_rasa_music`
4. **Service Details:**
   - **Name**: `raga-rasa-emotion-recognition`
   - **Runtime**: Python
   - **Build Command**: `pip install -r emotion_recognition/requirements.txt`
   - **Start Command**: `cd emotion_recognition && gunicorn --workers 1 --worker-class sync --bind 0.0.0.0:$PORT --timeout 300 api:app`
   - **Plan**: Free

5. **Environment Variables:**
   ```
   PYTHON_VERSION=3.10.15
   DEBUG=false
   ```

6. Click **Create Web Service**

### Wait for Deployment
- Service will auto-deploy from GitHub
- Check logs for "Application startup complete"
- Note the service URL: `https://raga-rasa-emotion-recognition.onrender.com`

---

## Step 2: Update Backend with Emotion Service URL

1. Go to your `raga-rasa-backend` Render service
2. Click **Settings** → **Environment**
3. **Add/Update these variables:**

```
MONGODB_URL=mongodb+srv://Rishi123:Rishi_123@majorproject.lpwzhzc.mongodb.net/?appName=MajorProject
DATABASE_NAME=raga_rasa
EMOTION_SERVICE_URL=https://raga-rasa-emotion-recognition.onrender.com
EMOTION_SERVICE_ENDPOINT=/detect
USE_EXTERNAL_EMOTION_SERVICE=true
PYTHON_VERSION=3.10.15
```

4. Click **Save** - backend will redeploy

---

## Step 3: Verify All Services

### Test Emotion Recognition Service:
```bash
curl -X POST https://raga-rasa-emotion-recognition.onrender.com/detect \
  -H "Content-Type: application/json" \
  -d '{"image": "<base64-image-here>"}'
```

### Test Backend Health:
```bash
curl https://raga-rasa-backend.onrender.com/health
```

### Test Recommendations:
```bash
curl -X POST https://raga-rasa-backend.onrender.com/api/recommend/live \
  -H "Content-Type: application/json" \
  -d '{
    "emotion": "happy",
    "session_id": "test-123",
    "cognitive_data": {
      "memory_score": 4,
      "reaction_time": 250,
      "accuracy_score": 85
    }
  }'
```

---

## Step 4: Frontend Configuration

The frontend `.env` file should already be configured:
```
VITE_API_BASE_URL=https://raga-rasa-backend.onrender.com/api
```

The frontend API service in `src/services/api.ts` already handles:
- Webcam image capture
- Base64 encoding
- Sending to backend `/api/detect-emotion` endpoint
- Receiving emotion detection results

---

## Full User Flow

1. **User takes selfie** 
   - Frontend captures image from webcam
   - Encodes as base64

2. **Frontend sends to Backend**
   - POST `/api/detect-emotion`
   - Backend receives base64 image

3. **Backend calls Emotion Service**
   - Forwards image to emotion recognition service
   - Gets back: emotion label + confidence

4. **Backend gets recommendations**
   - Uses detected emotion
   - Queries MongoDB for matching songs
   - Returns 5 songs with Cloudinary URLs

5. **Frontend plays music**
   - Displays recommended songs
   - Plays from Cloudinary streaming URLs

---

## Database Schema

### Songs Collection
```json
{
  "_id": "shaant_1",
  "song_id": "shaant_1",
  "song_name": "Raga Ahir Bhairav",
  "title": "Raga Ahir Bhairav",
  "rasa": "Shaant",
  "duration": 180,
  "streaming_url": "https://res.cloudinary.com/dlx3ufj3t/video/upload/raga-rasa/songs/Shaant/shaant_1.mp3",
  "cloudinary_url": "https://res.cloudinary.com/dlx3ufj3t/video/upload/raga-rasa/songs/Shaant/shaant_1.mp3",
  "avg_rating": 0.0,
  "num_users": 0
}
```

### Sessions Collection
```json
{
  "_id": "session-uuid",
  "user_id": "user-uuid",
  "emotion": "Happy",
  "rasa": "Shringar",
  "emotion_confidence": 0.95,
  "created_at": "2026-04-12T14:00:00",
  "songs_played": ["song-id-1", "song-id-2"],
  "ratings": {"song-id-1": 5}
}
```

---

## Emotion to Rasa Mapping

- **Happy/Surprised** → Shringar (romantic/joyful)
- **Sad** → Shaant + Shringar (calming + uplifting)
- **Angry** → Shaant (calming)
- **Fearful/Disgusted** → Veer (courageous)
- **Neutral** → Shaant (peaceful)

---

## Testing Checklist

- [ ] Emotion recognition service deployed on Render
- [ ] Backend has EMOTION_SERVICE_URL set correctly
- [ ] MongoDB has songs seeded (19 ragas)
- [ ] Backend returns recommendations (non-empty array)
- [ ] Frontend can send images and receive emotions
- [ ] Frontend can play songs from Cloudinary
- [ ] End-to-end flow: webcam → emotion → music

---

## Troubleshooting

**Emotion service returns 503 (Service Unavailable)**
- Check emotion service logs on Render
- Ensure HSEmotion library is installed (check requirements.txt)
- Model download might be slow on first run (check logs)

**Backend returns 0 recommendations**
- Check MONGODB_URL is set correctly
- Verify MongoDB Atlas has songs (check with seed_production_db.py)
- Check backend logs for database connection errors

**Frontend shows "Failed to detect emotion"**
- Check browser console for API errors
- Verify backend emotion endpoint is accessible
- Check CORS is enabled (should be configured in Flask)

**Audio doesn't play**
- Check Cloudinary URLs are valid (should work from browser)
- Check audio file format is supported
- Check browser audio permissions

---

## Production Checklist

✓ Backend deployed on Render
✓ Emotion service code updated to use real HSEmotion
✓ Database seeded with songs
✓ Frontend configured with Render URLs
✓ CORS enabled on emotion service
✓ Environment variables set on Render
✓ Procfiles configured for production (gunicorn, etc.)

All systems ready for production deployment!
