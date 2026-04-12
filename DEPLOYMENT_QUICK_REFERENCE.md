# 🚀 RagaRasa Deployment - Quick Reference Card

## Copy-Paste Ready Commands

### 1️⃣ HF SPACES SETUP (15 min)

**Visit:** https://huggingface.co/spaces → Create new Space
- Name: `raga-rasa-emotion`
- SDK: Docker
- Visibility: Public

```bash
# Clone HF Space
git clone https://huggingface.co/spaces/[YOUR_HF_USERNAME]/raga-rasa-emotion
cd raga-rasa-emotion

# Copy files
cp ../raga_rasa_music/emotion_recognition/api.py ./
cp ../raga_rasa_music/emotion_recognition/emotion_detector.py ./
cp ../raga_rasa_music/emotion_recognition/requirements.txt ./
cp ../raga_rasa_music/emotion_recognition/Dockerfile ./

# Deploy
git add .
git commit -m "Initial emotion service deployment"
git push

# Wait 3-5 minutes for auto-deployment
# Get URL: https://[username]-raga-rasa-emotion.hf.space
# ✅ SAVE THIS URL
```

---

### 2️⃣ GENERATE JWT SECRET

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
# Output: N_qP7xK9mB_2L-9zJ_4wX_5yQ_6rS_7tU
# ✅ SAVE THIS KEY
```

---

### 3️⃣ KOYEB BACKEND SETUP (20 min)

**Visit:** https://app.koyeb.com/services → Create Service

**GitHub Connection:**
- Repository: `rishisingh9152-cyber/raga_rasa_music`
- Branch: `main`
- Builder: Buildpack

**Environment Variables** (copy each line, fill in brackets):
```
MONGODB_URL=mongodb+srv://Rishi123:Rishi_123@majorproject.lpwzhzc.mongodb.net/?appName=MajorProject
JWT_SECRET_KEY=[FROM_STEP_2]
EMOTION_SERVICE_URL=[FROM_STEP_1]
DATABASE_NAME=raga_rasa
DEBUG=False
ALLOWED_ORIGINS_STR=https://raga-rasa-music-52.vercel.app,https://*.vercel.app,http://localhost:5173
CLOUDINARY_CLOUD_NAME=dlx3ufj3t
CLOUDINARY_API_KEY=255318353319693
CLOUDINARY_API_SECRET=MKFvdiyfmNpzxbaGKBMFM6SlT2c
```

**Resources:**
- Instance type: Kosmos (free)
- Min instances: 1
- Max instances: 1
- RAM: 512 MB

**Deploy and wait 3-5 minutes**
- Get URL: `https://raga-rasa-backend-[randomid].koyeb.app`
- ✅ SAVE THIS URL

---

### 4️⃣ TEST KOYEB BACKEND

```bash
# Replace [KOYEB_ID] with your random ID from step 3
curl https://raga-rasa-backend-[KOYEB_ID].koyeb.app/health

# Should return: {"status": "ok", ...}
```

---

### 5️⃣ UPDATE FRONTEND CONFIG (5 min)

**File:** `raga-rasa-soul-main/.env`

**Replace:**
```env
VITE_API_BASE_URL=https://raga-rasa-backend.onrender.com/api
```

**With:**
```env
VITE_API_BASE_URL=https://raga-rasa-backend-[KOYEB_ID].koyeb.app/api
```

**Example:**
```env
VITE_API_BASE_URL=https://raga-rasa-backend-abc123xyz.koyeb.app/api
```

**Push to GitHub:**
```bash
cd raga-rasa-soul-main
git add .env
git commit -m "Update backend URL to Koyeb"
git push origin main

# Vercel auto-deploys in 1-2 minutes
```

---

### 6️⃣ TEST EVERYTHING

**1. Frontend loads:**
```
https://raga-rasa-music-52.vercel.app
```

**2. In browser console (F12):**
```javascript
fetch('https://raga-rasa-backend-[KOYEB_ID].koyeb.app/api/health')
  .then(r => r.json())
  .then(console.log)
// Should return success, NO CORS errors
```

**3. Manual test:**
- Load frontend
- Open DevTools (F12)
- Check Console tab - should be clean (no errors)
- Try logging in
- Should connect to backend via Koyeb
- Try emotion detection
- Should call HF Spaces emotion service

---

## URLs You'll Get

| Service | URL Pattern |
|---------|-----------|
| Frontend (Vercel) | https://raga-rasa-music-52.vercel.app |
| Backend (Koyeb) | https://raga-rasa-backend-**[randomid]**.koyeb.app |
| Emotion (HF Spaces) | https://[username]-raga-rasa-emotion.hf.space |

---

## Values to Save

| Variable | Value | Where |
|----------|-------|-------|
| HF Spaces URL | `https://[username]-raga-rasa-emotion.hf.space` | Use for Koyeb `EMOTION_SERVICE_URL` |
| JWT Secret | `N_qP7xK9mB_2L-9zJ_4wX_5yQ_6rS_7tU` | Use for Koyeb `JWT_SECRET_KEY` |
| Koyeb URL | `https://raga-rasa-backend-[randomid].koyeb.app` | Use for Frontend `VITE_API_BASE_URL` |

---

## Troubleshooting Quick Fix

| Problem | Fix |
|---------|-----|
| **CORS errors** | Check Koyeb env var `ALLOWED_ORIGINS_STR` includes `https://*.vercel.app` |
| **Backend 502** | Check Koyeb logs, restart service |
| **Emotion fails** | Test HF Spaces URL directly with `/health` endpoint |
| **Frontend blank** | Clear browser cache (Ctrl+Shift+Delete) |
| **DB connection error** | Verify MongoDB URL is correct in Koyeb |

---

## Timeline

```
Step 1: HF Spaces       ████ 15 min
Step 2: Generate JWT    █ 1 min
Step 3: Koyeb Backend   ██████ 20 min
Step 4: Test Koyeb      ██ 2 min
Step 5: Update Frontend ██ 5 min
Step 6: Full Testing    ██ 10 min
                         ───────────
TOTAL:                   ██████████ ~50 min
```

---

## Verification Checklist

After completing all steps:

- [ ] HF Spaces emotion service is live (`/health` responds)
- [ ] Koyeb backend is live (`/health` responds)
- [ ] Frontend loads without errors
- [ ] No CORS errors in browser console
- [ ] Backend and frontend can communicate
- [ ] Database connection works
- [ ] Can log in to frontend
- [ ] Can detect emotions
- [ ] Can see music recommendations
- [ ] Can play music

✅ **All checked?** You're live! 🎉

---

## Get Help

- **All guides:** `DEPLOYMENT_COMPLETE_GUIDE.md`
- **Emotion service:** `HF_SPACES_DEPLOYMENT_GUIDE.md`
- **Backend:** `KOYEB_BACKEND_DEPLOYMENT.md`
- **Frontend:** `VERCEL_FRONTEND_CONFIG.md`
- **Summary:** `DEPLOYMENT_READY_SUMMARY.md`

---

**Ready? Start with Step 1 above! 🚀**
