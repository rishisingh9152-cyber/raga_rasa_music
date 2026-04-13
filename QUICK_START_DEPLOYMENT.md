# QUICK START - PRODUCTION DEPLOYMENT

## TL;DR - Deploy in 90 Minutes

### Step 1: Backend Deployment

Choose ONE of these three options:

#### Option A: Render (Easiest - 30 min) ⭐ RECOMMENDED
```bash
# 1. Push to GitHub
git push origin main

# 2. Go to https://render.com/dashboard
# 3. Click "New +" → "Web Service"
# 4. Connect GitHub repo: raga_rasa_music
# 5. Fill in:
#    - Name: raga-rasa-backend
#    - Root Directory: Backend
#    - Build Command: pip install --upgrade pip && pip install -r requirements.txt
#    - Start Command: gunicorn --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT main:app

# 6. Add Environment Variables:
#    - MONGODB_URL: [your_mongodb_url]
#    - JWT_SECRET: [generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"]
#    - CORS_ORIGINS: https://raga-rasa-soul.vercel.app

# 7. Click "Create Web Service"
# 8. Wait for deployment (2-5 min)
```

**Result**: `https://raga-rasa-backend.onrender.com`
**Cost**: $7/month (Starter tier) or Free (with limitations)

#### Option B: Google Cloud Run (30 min)
```bash
# 1. Create GCP project
gcloud projects create raga-rasa-soul-prod

# 2. Enable APIs
gcloud services enable run.googleapis.com cloudbuild.googleapis.com

# 3. Build & push image
gcloud builds submit Backend/ --tag us-central1-docker.pkg.dev/raga-rasa-soul-prod/raga-rasa-repo/backend:latest

# 4. Deploy to Cloud Run
gcloud run deploy raga-rasa-backend \
  --image=us-central1-docker.pkg.dev/raga-rasa-soul-prod/raga-rasa-repo/backend:latest \
  --region=us-central1 \
  --allow-unauthenticated \
  --set-env-vars MONGODB_URL=YOUR_MONGODB_URL

# 5. Get URL
gcloud run services describe raga-rasa-backend --region=us-central1 --format='value(status.url)'
```

**Result**: `https://raga-rasa-backend-xxxxx.run.app`
**Cost**: Pay-as-you-go ($0-50/month)

#### Option C: Heroku (if you have credits)
```bash
# 1. heroku create raga-rasa-backend
# 2. heroku buildpacks:set heroku/python
# 3. heroku config:set MONGODB_URL=your_url JWT_SECRET=your_secret
# 4. git push heroku main
```

**Result**: `https://raga-rasa-backend.herokuapp.com`
**Cost**: $7/month minimum

### Step 2: Frontend Deployment (15 min) → Vercel

```bash
# 1. Push to GitHub
git push origin main

# 2. Go to https://vercel.com/new
# 3. Import repository: raga_rasa_music
# 4. Root directory: raga-rasa-soul-main
# 5. Add environment variables:
#    VITE_API_URL=https://raga-rasa-backend-xxxxx.run.app/api
# 6. Deploy

# 7. Get URL from Vercel dashboard
```

**Result**: `https://raga-rasa-soul.vercel.app`

### Step 3: Emotion Service (10 min) → HF Spaces

Already deployed at: `https://rishi22652-emotion-recognition.hf.space`

Just update backend environment:

```bash
gcloud run services update raga-rasa-backend \
  --region=us-central1 \
  --update-env-vars EMOTION_SERVICE_URL=https://rishi22652-emotion-recognition.hf.space
```

### Step 4: Test Everything (20 min)

```bash
# Run integration tests
python Backend/test_integration_suite.py

# Run E2E tests
python test_e2e_production.py
```

---

## Detailed Deployment Guides

For complete step-by-step instructions:

1. **Render (Recommended)**: See `RENDER_BACKEND_DEPLOYMENT.md` (30 min)
2. **Google Cloud Run**: See `GOOGLE_CLOUD_RUN_DEPLOYMENT.md` (45 min)
3. **Frontend**: See `VERCEL_FRONTEND_DEPLOYMENT.md` (15 min)
4. **Emotion Service**: See `HF_SPACES_EMOTION_DEPLOYMENT.md` (10 min)

---

## Environment Variables Needed

### Backend (Google Cloud Run)
```
MONGODB_URL=mongodb+srv://user:pass@cluster.mongodb.net/raga_rasa
DATABASE_NAME=raga_rasa
JWT_SECRET=[32-char random string]
EMOTION_SERVICE_URL=https://rishi22652-emotion-recognition.hf.space
CORS_ORIGINS=https://raga-rasa-soul.vercel.app
```

### Frontend (Vercel)
```
VITE_API_URL=https://raga-rasa-backend-xxxxx.run.app/api
VITE_EMOTION_SERVICE_URL=https://rishi22652-emotion-recognition.hf.space
VITE_DEBUG=false
```

---

## Verify Deployment

```bash
# Check backend health
curl https://raga-rasa-backend-xxxxx.run.app/health

# Check frontend loads
curl https://raga-rasa-soul.vercel.app

# Check emotion service
curl https://rishi22652-emotion-recognition.hf.space/health

# Run tests
python Backend/test_integration_suite.py
```

---

## Cost Summary

### Option 1: Render (Recommended)
| Service | Free Tier | Monthly Cost |
|---------|-----------|--------------|
| Render Backend | No* | $7+ |
| MongoDB Atlas | Yes (M0) | $0 |
| Vercel Frontend | Yes | $0 |
| HF Spaces Emotion | Yes (CPU) | $0-4.50 |
| **Total** | | **$7-12/month** |

*Free tier available with limitations (auto-suspends after 15 min of inactivity)

### Option 2: Google Cloud Run
| Service | Free Tier | Monthly Cost |
|---------|-----------|--------------|
| Google Cloud Run | Yes* | $0-50 |
| MongoDB Atlas | Yes (M0) | $0 |
| Vercel Frontend | Yes | $0 |
| HF Spaces Emotion | Yes (CPU) | $0-4.50 |
| **Total** | | **$0-55/month** |

*Free tier: 2M requests/month, 360K vCPU-seconds/month

### Recommendation
- **Cheapest**: Google Cloud Run (~$0-20/month)
- **Easiest**: Render (~$7/month)
- **Best Balance**: Render Starter tier

---

## Feature Checklist

- [x] 35+ API endpoints
- [x] User authentication (JWT)
- [x] Session management
- [x] Music recommendations (hybrid algorithm)
- [x] Emotion detection (FER2013 model)
- [x] 68+ curated Raga pieces
- [x] 4 Rasa types (Shringar, Shaant, Veer, Shok)
- [x] Psychometric testing
- [x] User analytics and history
- [x] Rating and feedback system
- [x] Responsive mobile design
- [x] Audio streaming
- [x] Admin dashboard
- [x] Error handling and logging
- [x] Rate limiting
- [x] CORS and security headers

---

## Estimated Timeline

| Phase | Duration | Status |
|-------|----------|--------|
| Backend deployment | 45 min | ⏳ Ready |
| Frontend deployment | 15 min | ⏳ Ready |
| Emotion service | 10 min | ✅ Done |
| Testing | 20 min | ⏳ Ready |
| Total | 90 min | ✅ All Ready |

---

## Key Endpoints to Test

```bash
# Get health
GET /health

# Register
POST /api/auth/register
  {"email": "test@example.com", "password": "Test123!"}

# Get songs
GET /api/catalog/songs

# Get recommendations
POST /api/recommendations/emotion
  {"emotion": "anxious", "limit": 5}

# Create session
POST /api/session/create
  {"emotion": "calm", "cognitive_baseline": 50}
```

---

## Support

- Full docs: `PRODUCTION_READY_RELEASE.md`
- Backend guide: `GOOGLE_CLOUD_RUN_DEPLOYMENT.md`
- Frontend guide: `VERCEL_FRONTEND_DEPLOYMENT.md`
- Emotion guide: `HF_SPACES_EMOTION_DEPLOYMENT.md`
- Architecture: `COMPLETE_PROJECT_GUIDE.md`

---

**Last Updated**: April 13, 2026
**Status**: ✅ PRODUCTION READY

🚀 Start deploying now!
