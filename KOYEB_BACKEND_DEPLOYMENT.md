# Koyeb Backend Deployment Guide - RagaRasa FastAPI

## Overview

This guide walks you through deploying the RagaRasa backend (FastAPI) to Koyeb.

**Time Required:** 15-20 minutes
**Cost:** FREE tier available (with paid options for production)
**Requirements:**
- Koyeb account (free signup at https://app.koyeb.com/)
- GitHub account with access to raga_rasa_music repository
- MongoDB Atlas connection string (already have this)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Vercel Frontend                          │
│                  (raga-rasa-music-52.vercel.app)               │
└────────────────────────────┬────────────────────────────────────┘
                             │ API Calls
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Koyeb Backend                              │
│                    (FastAPI, Port 8000)                         │
│  - Database: MongoDB Atlas                                      │
│  - Emotion Service: HF Spaces (outbound requests)              │
└─────────────────────────────────────────────────────────────────┘
                             │ Calls
                             ▼
        ┌─────────────────────────────────────┐
        │  HF Spaces Emotion Service          │
        │  (rishisingh9152-raga-emotion.hf.space) │
        └─────────────────────────────────────┘
                             │
                             ▼
        ┌─────────────────────────────────────┐
        │       MongoDB Atlas Database        │
        │     (MongoDB+srv connection)        │
        └─────────────────────────────────────┘
```

---

## Prerequisites

### 1. Get Your Emotion Service URL

From HF Spaces deployment, you should have a URL like:
```
https://[username]-raga-rasa-emotion.hf.space
```

If you haven't deployed to HF Spaces yet, follow `HF_SPACES_DEPLOYMENT_GUIDE.md` first.

### 2. MongoDB Atlas Connection String

You should already have this:
```
mongodb+srv://Rishi123:Rishi_123@majorproject.lpwzhzc.mongodb.net/?appName=MajorProject
```

### 3. Generate a Secure JWT Secret

Run this command to generate a new secure key:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

This will output something like: `N_qP7xK9mB_2L-9zJ_4wX_5yQ_6rS_7tU`

Save this - you'll need it for Koyeb configuration.

---

## Step 1: Create a Koyeb Account

1. Go to https://app.koyeb.com/
2. Click **Sign Up** (or **Sign In** if you have an account)
3. Choose sign up method (Email, GitHub, Google)
4. Complete account setup

---

## Step 2: Access Your GitHub Repository

Ensure your `raga_rasa_music` repository on GitHub has the latest changes committed and pushed.

```bash
cd C:\Users\rishi\raga_rasa_music
git status
git add .
git commit -m "Prepare for Koyeb deployment"
git push origin main
```

---

## Step 3: Create a Koyeb Service

1. Go to https://app.koyeb.com/services
2. Click **Create Service** button
3. Choose **GitHub** as deployment source

---

## Step 4: Configure Git Repository

1. Click **Connect with GitHub** (if not already connected)
   - This will redirect to GitHub OAuth
   - Authorize Koyeb to access your repositories
2. Select your repository:
   - **Repository:** `rishisingh9152-cyber/raga_rasa_music`
   - **Branch:** `main`
3. Click **Next**

---

## Step 5: Configure Build Settings

1. **Build Settings:**
   - **Builder:** Select **Buildpack** (Koyeb will auto-detect Python)
   - **Entrypoint/Run command:** Leave empty (will use Procfile)

2. **Root directory:** Leave empty (Koyeb will auto-detect)

3. Click **Next**

---

## Step 6: Configure Environment Variables

In the **Environment Variables** section, add the following:

| Key | Value |
|-----|-------|
| `MONGODB_URL` | `mongodb+srv://Rishi123:Rishi_123@majorproject.lpwzhzc.mongodb.net/?appName=MajorProject` |
| `JWT_SECRET_KEY` | `N_qP7xK9mB_2L-9zJ_4wX_5yQ_6rS_7tU` (use the one you generated) |
| `EMOTION_SERVICE_URL` | `https://[username]-raga-rasa-emotion.hf.space` |
| `DATABASE_NAME` | `raga_rasa` |
| `DEBUG` | `False` |
| `ALLOWED_ORIGINS_STR` | `https://raga-rasa-music-52.vercel.app,https://*.vercel.app,http://localhost:5173,http://localhost:8080` |

**Optional (for cloud storage):**
| `CLOUDINARY_CLOUD_NAME` | `dlx3ufj3t` |
| `CLOUDINARY_API_KEY` | `255318353319693` |
| `CLOUDINARY_API_SECRET` | `MKFvdiyfmNpzxbaGKBMFM6SlT2c` |

Click **Add environment variable** for each one.

---

## Step 7: Configure Scaling & Resources

1. **Scaling:**
   - **Min instances:** 1
   - **Max instances:** 3 (or 1 for testing)
   - **CPU:** 0.5 (micro)
   - **RAM:** 512 MB (should be sufficient)

2. **Scale-to-zero:** Optional (saves costs, service sleeps after inactivity)
   - Toggle to **ON** if desired (recommended for development)

---

## Step 8: Review & Deploy

1. **Service name:** `raga-rasa-backend` (or your preferred name)
2. **Instance type:** Kosmos (free tier)
3. Review all settings
4. Click **Create Service**

**Deployment starts automatically!**
- This takes 3-5 minutes
- Koyeb will:
  1. Clone your repository
  2. Install Python dependencies (from requirements.txt)
  3. Build the application
  4. Start the service

---

## Step 9: Monitor Deployment

1. Go to your service dashboard: https://app.koyeb.com/services
2. Click on `raga-rasa-backend` service
3. In **Logs** tab, watch the build process:
   - Should see "Building image..."
   - Then "Deploying..."
   - Finally "Service running"

4. Once complete, you'll see a public URL like:
   ```
   https://raga-rasa-backend-[randomid].koyeb.app
   ```

**Save this URL - you'll need it for the frontend!**

---

## Step 10: Test the Backend

Once deployed, test your backend endpoints:

### Health Check
```bash
curl https://raga-rasa-backend-[randomid].koyeb.app/health
```

Expected response:
```json
{"status": "ok", "message": "Backend is running"}
```

### Database Check
```bash
curl https://raga-rasa-backend-[randomid].koyeb.app/db-test
```

Expected response:
```json
{"database": "connected", "collection_count": 5}
```

### List Ragas
```bash
curl https://raga-rasa-backend-[randomid].koyeb.app/api/catalog/ragas
```

Expected response:
```json
{
  "ragas": ["Shringar", "Veer", "Shaant", "Shok"]
}
```

---

## Step 11: Update Frontend Configuration

Now that your backend is deployed on Koyeb, update the frontend `.env`:

### File: `raga-rasa-soul-main/.env`

```env
VITE_API_BASE_URL=https://raga-rasa-backend-[randomid].koyeb.app/api
```

Push to GitHub:
```bash
cd raga-rasa-soul-main
git add .env
git commit -m "Update backend URL to Koyeb"
git push origin main
```

This will automatically trigger a Vercel redeploy.

---

## Step 12: Verify Everything Works

Test the complete flow:

1. **Frontend loads:**
   ```
   https://raga-rasa-music-52.vercel.app
   ```

2. **Open browser console (F12) and check:**
   - No CORS errors
   - No network errors
   - Songs load from API

3. **Test login:**
   - Use any credentials
   - Should connect to MongoDB via Koyeb backend

4. **Test emotion detection:**
   - Upload photo
   - Should call Koyeb backend
   - Backend calls HF Spaces emotion service
   - Returns emotion result

---

## Common Issues & Troubleshooting

### Issue: Build fails with "Requirements not found"

**Solution:**
- Ensure `Backend/requirements.txt` exists and is in root of Backend directory
- Check that file names are exact (case-sensitive on Linux)
- Verify requirements.txt is committed to Git

### Issue: Service running but returns 503

**Solution:**
- Check logs for database connection errors
- Verify `MONGODB_URL` is correct in environment variables
- Wait 30 seconds for initial startup to complete
- Check MongoDB Atlas whitelist (should allow all IPs: `0.0.0.0/0`)

### Issue: CORS errors from frontend

**Solution:**
- Verify `ALLOWED_ORIGINS_STR` includes Vercel URL
- Use pattern: `https://*.vercel.app` to allow all preview URLs
- Restart service after updating env vars (Koyeb does this automatically)
- Backend already has custom CORS middleware from previous fix

### Issue: Emotion service returns 502/503

**Solution:**
- Verify `EMOTION_SERVICE_URL` in Koyeb env vars is correct
- Test emotion service URL manually: `curl [EMOTION_SERVICE_URL]/health`
- HF Spaces might be sleeping - first request takes 30-60 seconds
- Check Koyeb logs for actual error message

### Issue: Service keeps crashing

**Solution:**
- Check Koyeb logs for Python errors
- Common causes:
  - Missing environment variables
  - Database connection timeout
  - Port binding issue
- Increase RAM to 1GB if crashes persist

---

## Monitoring & Maintenance

### View Logs
1. Go to service dashboard
2. Click **Logs** tab
3. Filter by:
   - **Build** - see build output
   - **Runtime** - see application logs

### Restart Service
If needed:
1. Go to service dashboard
2. Click **Actions** dropdown
3. Select **Restart**

### Update Code
Any push to `main` branch automatically redeploys:
```bash
git push origin main
# Koyeb detects change and rebuilds automatically
```

### Update Environment Variables
1. Go to service dashboard
2. Click **Settings**
3. Click **Environment variables**
4. Edit values
5. Click **Save** - service auto-restarts

---

## Performance Optimization (Optional)

For production use:

1. **Enable Scale-to-Zero:**
   - Saves costs when service is idle
   - First request after sleep takes 30-60 seconds
   - Toggle in Settings → Scaling

2. **Increase RAM if needed:**
   - Start with 512 MB
   - If crashes, increase to 1 GB or 2 GB
   - Monitor in Metrics tab

3. **Use Redis for caching:**
   - Add Redis URL in environment (optional)
   - Will speed up recommendations and caching

4. **Enable CDN:**
   - Koyeb provides built-in CDN
   - Speeds up frontend asset delivery

---

## Next Steps

1. ✅ HF Spaces emotion service deployed
2. ✅ Koyeb backend deployed
3. ⬜ Frontend already on Vercel (update .env with new Koyeb URL)
4. ⬜ Test complete end-to-end flow
5. ⬜ Configure custom domain (optional)

---

## Support & References

- Koyeb Documentation: https://koyeb.com/docs
- FastAPI: https://fastapi.tiangolo.com/
- Koyeb Python Guide: https://koyeb.com/docs/deploy/python
- Koyeb GitHub Integration: https://koyeb.com/docs/build-and-deploy/deploy-with-git

---

**Your backend is now live on Koyeb!**

Next: Update frontend and test the complete system.
