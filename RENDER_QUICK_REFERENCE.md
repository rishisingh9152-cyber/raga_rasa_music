# RENDER DEPLOYMENT - QUICK REFERENCE CARD

## 5-Minute TL;DR

### 1. Generate JWT Secret
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
# Copy output ↓
```

### 2. Get MongoDB URL
From MongoDB Atlas → Connect → Your connection string:
```
mongodb+srv://raga_rasa_admin:PASSWORD@cluster.xxxxx.mongodb.net/raga_rasa
```

### 3. Push Code to GitHub
```bash
cd Backend
git add .
git commit -m "Backend ready for Render"
git push origin main
```

### 4. Create Render Service
- Go to https://render.com/dashboard
- Click "+ New" → "Web Service"
- Connect GitHub (raga_rasa_music)
- Fill in:
  - **Name**: raga-rasa-backend
  - **Root Directory**: Backend
  - **Start Command**: `gunicorn --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout 120 main:app`

### 5. Add These Environment Variables

| Variable | Value |
|----------|-------|
| `PORT` | `8000` |
| `ENVIRONMENT` | `production` |
| `DEBUG` | `false` |
| `DATABASE_NAME` | `raga_rasa` |
| `MONGODB_URL` | Your MongoDB connection string |
| `JWT_SECRET` | Your generated secret |
| `CORS_ORIGINS` | `https://raga-rasa-soul.vercel.app` |
| `EMOTION_SERVICE_URL` | `https://rishi22652-emotion-recognition.hf.space` |
| `USE_EXTERNAL_EMOTION_SERVICE` | `true` |
| `MAX_UPLOAD_SIZE_MB` | `50` |

### 6. Click "Create Web Service"

### 7. Wait 2-5 Minutes

### 8. Test It
```bash
curl https://raga-rasa-backend.onrender.com/health
# Should return: {"status": "healthy", ...}
```

**Done! Your backend is live! 🎉**

---

## Environment Variables (Copy-Paste)

```
PORT=8000
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=info
DATABASE_NAME=raga_rasa
MONGODB_URL=mongodb+srv://raga_rasa_admin:YOUR_PASSWORD@YOUR_CLUSTER.xxxxx.mongodb.net/raga_rasa
JWT_SECRET=YOUR_GENERATED_SECRET_HERE
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
CORS_ORIGINS=https://raga-rasa-soul.vercel.app
ALLOWED_HOSTS=render.com
USE_EXTERNAL_EMOTION_SERVICE=true
EMOTION_SERVICE_URL=https://rishi22652-emotion-recognition.hf.space
EMOTION_SERVICE_ENDPOINT=/detect
ENABLE_STREAMING=true
ENABLE_RECOMMENDATIONS=true
ENABLE_ANALYTICS=true
MAX_UPLOAD_SIZE_MB=50
LOG_FORMAT=json
```

---

## Terminal Commands (Copy-Paste)

### Generate JWT Secret
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Test Backend (after deployment)
```bash
# Health check
curl https://raga-rasa-backend.onrender.com/health

# Get songs
curl https://raga-rasa-backend.onrender.com/api/catalog/songs

# Register user
curl -X POST https://raga-rasa-backend.onrender.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!"}'

# Get recommendations
curl -X POST https://raga-rasa-backend.onrender.com/api/recommendations/emotion \
  -H "Content-Type: application/json" \
  -d '{"emotion":"anxious","limit":5}'
```

---

## Files to Have Ready

- ✅ GitHub repository with Backend folder
- ✅ MongoDB Atlas account with cluster
- ✅ JWT secret (generated)
- ✅ Render account (free signup)
- ✅ MongoDB connection string
- ✅ Frontend URL (for CORS_ORIGINS)

---

## Render Dashboard Walkthrough

```
1. Visit https://render.com/dashboard
   ↓
2. Click "+ New" (top right)
   ↓
3. Select "Web Service"
   ↓
4. Click "GitHub" button
   ↓
5. Select your repository
   ↓
6. Fill in Form:
   Name:              raga-rasa-backend
   Root Directory:    Backend
   Build Command:     pip install -r requirements.txt
   Start Command:     gunicorn --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT main:app
   ↓
7. Click "Advanced" (bottom of form)
   ↓
8. Add Environment Variables (see list above)
   ↓
9. Click "Create Web Service"
   ↓
10. Watch build logs (2-5 minutes)
    ↓
11. See "Live" status ✅
    ↓
12. Copy service URL: https://raga-rasa-backend.onrender.com
```

---

## Your Backend URL

After deployment, you'll have:
```
https://raga-rasa-backend.onrender.com
```

Use this URL for:
- Frontend API calls: `https://raga-rasa-backend.onrender.com/api`
- Testing: `https://raga-rasa-backend.onrender.com/health`
- Documentation: `https://raga-rasa-backend.onrender.com/docs`

---

## Typical Deployment Timeline

| Step | Time |
|------|------|
| Generate secrets | 1 min |
| Setup MongoDB (if new) | 10 min |
| Push to GitHub | 1 min |
| Create Render service | 2 min |
| Build & deploy | 2-5 min |
| Test | 2 min |
| **Total** | **18-21 min** |

---

## What Each Environment Variable Does

| Variable | Purpose |
|----------|---------|
| `PORT` | Render assigns dynamic port, should be 8000 |
| `ENVIRONMENT` | Tells app it's in production (production/development) |
| `DEBUG` | Disable debugging in production (false) |
| `MONGODB_URL` | Connection to database |
| `JWT_SECRET` | Encrypts authentication tokens (keep secret!) |
| `CORS_ORIGINS` | Which domains can call the API |
| `EMOTION_SERVICE_URL` | Where emotion detection API is |
| `MAX_UPLOAD_SIZE_MB` | Max file upload size |

---

## If Something Goes Wrong

### Build Fails
- Check Backend/ folder exists in GitHub
- Check requirements.txt is in Backend/
- Check Procfile is correct (copy from guide)

### Backend Won't Start
- Check logs in Render dashboard → Logs tab
- Verify MONGODB_URL is correct
- Verify all required env vars are set

### Health Check Fails
- Wait 30 more seconds
- Refresh page
- Check Backend/main.py has `/health` endpoint

### CORS Errors
- Update `CORS_ORIGINS` to match frontend URL
- Trigger redeploy (git push or manual)

---

## Useful Links

| What | Link |
|------|------|
| Render Dashboard | https://render.com/dashboard |
| MongoDB Atlas | https://cloud.mongodb.com |
| GitHub | https://github.com |
| API Docs | https://raga-rasa-backend.onrender.com/docs |
| Full Guide | `RENDER_BACKEND_DEPLOYMENT.md` |
| Environment Variables | `RENDER_ENVIRONMENT_VARIABLES.md` |

---

## Next Steps After Backend is Live

1. ✅ Backend deployed
2. ⏳ Deploy frontend to Vercel
3. ⏳ Update frontend's VITE_API_URL
4. ⏳ Test complete flow
5. ⏳ Monitor logs and metrics

---

## Support

| Problem | Check |
|---------|-------|
| Not deployed | Render dashboard → Logs tab |
| API not responding | Health check: `curl /health` |
| Database not connecting | MONGODB_URL env var |
| CORS errors | CORS_ORIGINS env var |
| 503 errors | Check logs, restart service |

---

**Status**: Ready to Deploy

**Time to Deploy**: 20 minutes

**Cost**: $7/month

**Next**: Follow terminal steps above! 🚀
