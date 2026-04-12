# Complete Deployment Execution Guide - RagaRasa Music Therapy

## Quick Summary

You're deploying RagaRasa to three platforms:

| Component | Platform | URL Pattern | Time |
|-----------|----------|------------|------|
| **Frontend** | Vercel | `https://raga-rasa-music-52.vercel.app` | Already Done ✅ |
| **Emotion Service** | HF Spaces | `https://[username]-raga-rasa-emotion.hf.space` | 10-15 min |
| **Backend** | Koyeb | `https://raga-rasa-backend-[randomid].koyeb.app` | 15-20 min |

**Total Time:** ~45 minutes
**Cost:** FREE (all platforms have free tiers)

---

## Phase 1: Deploy Emotion Service (HF Spaces) - 15 minutes

### 1.1: Create HF Spaces Account

1. Go to https://huggingface.co/
2. Sign up (if needed) or sign in
3. Create account if first time

### 1.2: Create a New Space

1. Go to https://huggingface.co/spaces
2. Click **Create new Space**
3. Fill form:
   - **Name:** `raga-rasa-emotion`
   - **License:** MIT
   - **SDK:** Docker
   - **Visibility:** Public
4. Click **Create Space**

### 1.3: Clone Space Repository

```bash
git clone https://huggingface.co/spaces/[YOUR_HF_USERNAME]/raga-rasa-emotion
cd raga-rasa-emotion
```

### 1.4: Copy Emotion Service Files

Copy these files to the cloned Space directory:

```bash
# From your raga_rasa_music directory:
cp emotion_recognition/api.py ./raga-rasa-emotion/
cp emotion_recognition/emotion_detector.py ./raga-rasa-emotion/
cp emotion_recognition/requirements.txt ./raga-rasa-emotion/
cp emotion_recognition/Dockerfile ./raga-rasa-emotion/
```

### 1.5: Push to HF Spaces

```bash
cd raga-rasa-emotion
git add .
git commit -m "Initial deployment of emotion recognition service"
git push
```

**Wait for auto-deployment (3-5 minutes)**

### 1.6: Get Your HF Spaces URL

Once deployment completes, you'll have:
```
https://[YOUR_HF_USERNAME]-raga-rasa-emotion.hf.space
```

**✅ Save this URL** - You'll need it in Phase 2

---

## Phase 2: Deploy Backend (Koyeb) - 20 minutes

### 2.1: Create Koyeb Account

1. Go to https://app.koyeb.com/
2. Sign up (GitHub/Email/Google)
3. Complete account setup

### 2.2: Generate JWT Secret

Run in terminal:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Example output:** `N_qP7xK9mB_2L-9zJ_4wX_5yQ_6rS_7tU`

**✅ Save this JWT secret** - You'll need it in Step 2.5

### 2.3: Push Code to GitHub (if not already done)

```bash
cd C:\Users\rishi\raga_rasa_music
git status
git add .
git commit -m "Prepare for Koyeb deployment - add Docker and deployment guides"
git push origin main
```

### 2.4: Create Service in Koyeb

1. Go to https://app.koyeb.com/
2. Click **Create Service**
3. Select **GitHub** as deployment source
4. Click **Connect with GitHub** (authorize if needed)
5. Select repository:
   - **Repository:** `rishisingh9152-cyber/raga_rasa_music`
   - **Branch:** `main`
6. Click **Next**

### 2.5: Configure Build Settings

1. **Build Settings:**
   - **Builder:** Buildpack
   - **Buildpack runtime:** Python (auto-detected)
2. Click **Next**

### 2.6: Add Environment Variables

Add these in the "Environment Variables" section:

```
MONGODB_URL=mongodb+srv://Rishi123:Rishi_123@majorproject.lpwzhzc.mongodb.net/?appName=MajorProject

JWT_SECRET_KEY=[YOUR_JWT_SECRET_FROM_STEP_2.2]

EMOTION_SERVICE_URL=[YOUR_HF_SPACES_URL_FROM_PHASE_1]

DATABASE_NAME=raga_rasa

DEBUG=False

ALLOWED_ORIGINS_STR=https://raga-rasa-music-52.vercel.app,https://*.vercel.app,http://localhost:5173,http://localhost:8080

CLOUDINARY_CLOUD_NAME=dlx3ufj3t

CLOUDINARY_API_KEY=255318353319693

CLOUDINARY_API_SECRET=MKFvdiyfmNpzxbaGKBMFM6SlT2c
```

**Example filled form:**
```
MONGODB_URL=mongodb+srv://Rishi123:Rishi_123@majorproject.lpwzhzc.mongodb.net/?appName=MajorProject
JWT_SECRET_KEY=N_qP7xK9mB_2L-9zJ_4wX_5yQ_6rS_7tU
EMOTION_SERVICE_URL=https://rishisingh9152-raga-rasa-emotion.hf.space
[... rest of variables ...]
```

### 2.7: Configure Resources

1. **Instance type:** Select **Kosmos** (free tier)
2. **Scaling:**
   - Min instances: 1
   - Max instances: 1
3. Click **Next**

### 2.8: Review & Deploy

1. **Service name:** `raga-rasa-backend`
2. Review all settings
3. Click **Create Service**

**⏳ Wait for deployment (3-5 minutes)**

Check progress:
- Go to https://app.koyeb.com/services
- Click `raga-rasa-backend`
- Watch **Logs** tab

### 2.9: Get Koyeb Backend URL

Once deployment is done:
1. Go to service dashboard
2. Look for the public URL (like `https://raga-rasa-backend-abc123xyz.koyeb.app`)

**✅ Save this URL** - You'll need it in Phase 3

### 2.10: Test Backend

```bash
# Test health endpoint
curl https://raga-rasa-backend-[YOUR_ID].koyeb.app/health

# Should return:
# {"status": "ok", ...}
```

---

## Phase 3: Update Frontend Configuration - 5 minutes

### 3.1: Update Frontend .env

File: `raga-rasa-soul-main/.env`

Replace:
```env
VITE_API_BASE_URL=https://raga-rasa-backend.onrender.com/api
```

With:
```env
VITE_API_BASE_URL=https://raga-rasa-backend-[YOUR_KOYEB_ID].koyeb.app/api
```

**Example:**
```env
VITE_API_BASE_URL=https://raga-rasa-backend-abc123xyz.koyeb.app/api
```

### 3.2: Commit and Push

```bash
cd raga-rasa-soul-main
git add .env
git commit -m "Update backend URL to Koyeb"
git push origin main
```

**✅ Vercel automatically redeploys** (wait 1-2 minutes)

### 3.3: Verify Frontend Update

1. Go to https://vercel.com/dashboard
2. Click your project
3. Check **Deployments** tab
4. Should see new deployment in progress

---

## Phase 4: End-to-End Testing - 10 minutes

### 4.1: Test Frontend Loads

1. Visit https://raga-rasa-music-52.vercel.app
2. Page should load without errors
3. Open browser console (F12)
4. Check for CORS errors - there should be NONE

### 4.2: Test API Connection

In browser console:
```javascript
fetch('https://raga-rasa-backend-[YOUR_ID].koyeb.app/api/health')
  .then(r => r.json())
  .then(console.log)
```

Should see:
```json
{"status": "ok", ...}
```

### 4.3: Test Login

1. Go to https://raga-rasa-music-52.vercel.app
2. Try logging in with any username/password
3. Should NOT see:
   - CORS errors
   - 502/503 errors
   - Network timeouts
4. Should see user dashboard

### 4.4: Test Emotion Detection

1. Click on "Emotion Detection" or similar
2. Upload a photo or take webcam photo
3. Should process and show emotion result
4. In browser console, should see:
   - Call to HF Spaces emotion service
   - Response from backend with recommendation

### 4.5: Test Music Recommendations

1. After emotion detection, should see music recommendations
2. Click on a song
3. Should see song details and play button
4. Audio should play (if available)

### 4.6: Check All Endpoints

```bash
# Test different endpoints
curl https://raga-rasa-backend-[YOUR_ID].koyeb.app/api/catalog/ragas
curl https://raga-rasa-backend-[YOUR_ID].koyeb.app/api/catalog/songs
curl https://raga-rasa-backend-[YOUR_ID].koyeb.app/health
```

All should return valid JSON responses.

---

## Troubleshooting Quick Guide

### Issue: Frontend shows blank page

**Solution:**
- Clear browser cache (Ctrl+Shift+Delete)
- Check console for errors
- Verify `.env` was pushed to GitHub
- Wait 2 minutes for Vercel to redeploy

### Issue: CORS errors in console

**Solution:**
- Verify `ALLOWED_ORIGINS_STR` in Koyeb includes frontend URL
- Should include `https://*.vercel.app` pattern
- Restart Koyeb service after updating env vars

### Issue: Backend returns 502/503

**Solution:**
- Check Koyeb service status: https://app.koyeb.com/services
- Click service → **Logs** to see errors
- Common causes:
  - MongoDB connection issue
  - Missing environment variables
  - Memory limit exceeded
- Try restart: **Actions** → **Restart**

### Issue: Emotion detection fails

**Solution:**
- Test HF Spaces directly: `curl [HF_SPACES_URL]/health`
- Check Koyeb backend logs for emotion service errors
- HF Spaces might be sleeping - try again
- Verify `EMOTION_SERVICE_URL` in Koyeb env vars

### Issue: Database errors

**Solution:**
- Verify MongoDB URL is correct
- Check MongoDB Atlas whitelist (should be `0.0.0.0/0`)
- Ensure database exists in Atlas
- Test connection: `mongo "[YOUR_MONGODB_URL]"`

---

## Verification Checklist

After deployment, verify:

- [ ] HF Spaces emotion service is live and responding
- [ ] Koyeb backend is live and responding
- [ ] Frontend loads without CORS errors
- [ ] API health check responds
- [ ] Database connection works
- [ ] Login page is accessible
- [ ] Can log in successfully
- [ ] Can detect emotions
- [ ] Can see music recommendations
- [ ] Can play music
- [ ] No console errors

---

## Monitoring & Maintenance

### Daily Checks

- Monitor Koyeb dashboard for service health
- Check HF Spaces for service status
- Monitor error rates (if available)

### Weekly Maintenance

- Review logs for any errors
- Check performance metrics
- Update dependencies if needed

### When to Scale

If experiencing slowness:
1. Increase Koyeb RAM to 1GB (Settings → Resources)
2. Increase max instances to 2-3 (Settings → Scaling)
3. Consider upgrading HF Spaces to CPU Upgrade tier

---

## Cost Breakdown

| Service | Free Tier | Cost |
|---------|-----------|------|
| **Koyeb** | Yes | FREE (or $0.05-0.50/hr if paid) |
| **HF Spaces** | Yes | FREE (on CPU Basic) |
| **Vercel** | Yes | FREE (or $15+/month for pro) |
| **MongoDB Atlas** | Yes | FREE (512 MB storage) |
| **TOTAL** | ✅ | **$0/month** |

---

## Support & Resources

### Documentation
- HF Spaces: https://huggingface.co/docs/hub/spaces-overview
- Koyeb: https://koyeb.com/docs
- Vercel: https://vercel.com/docs
- FastAPI: https://fastapi.tiangolo.com/

### Guides in Repository
- `HF_SPACES_DEPLOYMENT_GUIDE.md` - Detailed HF Spaces setup
- `KOYEB_BACKEND_DEPLOYMENT.md` - Detailed Koyeb setup
- `VERCEL_FRONTEND_CONFIG.md` - Frontend configuration

### GitHub Issues
If you encounter issues:
1. Check service logs first
2. Check deployment guides
3. Review troubleshooting section above
4. Open GitHub issue with error details

---

## Timeline Estimate

| Phase | Task | Time |
|-------|------|------|
| **1** | HF Spaces setup | 15 min |
| **2** | Koyeb backend | 20 min |
| **3** | Frontend config | 5 min |
| **4** | Testing | 10 min |
| **TOTAL** | | **~50 minutes** |

---

## Success Indicators

You've successfully deployed when:

✅ Frontend loads: https://raga-rasa-music-52.vercel.app
✅ Backend responds: `curl [KOYEB_URL]/health` returns `{"status": "ok"}`
✅ No CORS errors in browser console
✅ Can log in to frontend
✅ Can detect emotions
✅ Can see music recommendations
✅ Can play music

---

## Next Steps After Deployment

1. **Monitor performance:**
   - Set up Vercel Analytics
   - Monitor Koyeb logs

2. **Optimize:**
   - Enable caching
   - Implement CDN
   - Configure auto-scaling

3. **Scale:**
   - Upgrade to paid tiers if needed
   - Add more features
   - Improve UI/UX

4. **Maintain:**
   - Regular security updates
   - Database optimization
   - Performance monitoring

---

**You're ready to deploy! Start with Phase 1 and follow each step sequentially.**

Good luck! 🚀
