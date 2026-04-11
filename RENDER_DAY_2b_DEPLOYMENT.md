# Day 2b: Render.com Deployment - Step-by-Step Guide

**Status**: Ready to deploy both services  
**Services to Deploy**: 2 (emotion_recognition + Backend)

---

## Prerequisites Checklist

Before proceeding, ensure:
- [ ] You have a Render.com account (https://render.com)
- [ ] You signed up with GitHub
- [ ] You authorized Render to access your GitHub repos
- [ ] You confirmed your email

---

## Deployment Steps

### Phase 1: Deploy Emotion Recognition Service

**1. In Render Dashboard:**
- Click **"+ New"** → **"Web Service"**
- Connect to your GitHub repository
- Select the repo containing the emotion_recognition folder

**2. Configure Emotion Service:**
- **Name**: `emotion-recognition`
- **Root Directory**: `emotion_recognition`
- **Build Command**: 
  ```
  pip install -r requirements.txt
  ```
- **Start Command**: 
  ```
  python api.py
  ```
- **Plan**: Free

**3. Environment Variables:**
Add these in Render dashboard:
```
FLASK_ENV=production
DEBUG=False
```

**4. Deploy:**
- Click **"Create Web Service"**
- Wait 5-10 minutes for deployment
- Once deployed, you'll get a public URL like: `https://emotion-recognition-xxxxx.onrender.com`
- **Save this URL - you'll need it for the backend!**

**5. Test Emotion Service:**
```bash
curl https://emotion-recognition-xxxxx.onrender.com/health
```

Expected response:
```json
{"status": "ok", "model": "HSEmotion enet_b0_8_best_afew"}
```

---

### Phase 2: Deploy Backend Service

**1. In Render Dashboard:**
- Click **"+ New"** → **"Web Service"**
- Connect to your GitHub repository (same repo)

**2. Configure Backend:**
- **Name**: `raga-rasa-backend`
- **Root Directory**: `.` (root of repo)
- **Build Command**: 
  ```
  pip install -r Backend/requirements.txt
  ```
- **Start Command**: 
  ```
  cd Backend && python -m uvicorn main:app --host 0.0.0.0 --port 8000
  ```
- **Plan**: Free

**3. Environment Variables:**

Add these in Render environment variables:

```
# MongoDB
MONGODB_URL=mongodb+srv://Rishi123:Rishi_123@majorproject.lpwzhzc.mongodb.net/?appName=MajorProject
DATABASE_NAME=raga_rasa

# External Emotion Service (UPDATE WITH YOUR URL)
USE_EXTERNAL_EMOTION_SERVICE=True
EMOTION_SERVICE_URL=https://emotion-recognition-xxxxx.onrender.com
EMOTION_SERVICE_ENDPOINT=/detect
EMOTION_CONFIDENCE_THRESHOLD=0.3

# API
API_HOST=0.0.0.0
API_PORT=8000

# JWT
JWT_SECRET_KEY=dt_aRvdBIakTz2GI_qC4U1EqVVgmq4nrRDSc5XX73iY
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Storage
STORAGE_PROVIDER=local
STORAGE_BASE_PATH=./Songs/

# Debug
DEBUG=False

# CORS
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000,https://raga-rasa.vercel.app
```

**Important**: Replace `https://emotion-recognition-xxxxx.onrender.com` with your actual emotion service URL from Step 1!

**4. Deploy:**
- Click **"Create Web Service"**
- Wait 5-10 minutes for deployment
- You'll get a public URL like: `https://raga-rasa-backend-xxxxx.onrender.com`
- **Save this URL!**

**5. Test Backend:**
```bash
curl https://raga-rasa-backend-xxxxx.onrender.com/health
```

---

## Troubleshooting

### Emotion Service Not Starting
- Check Render logs: Dashboard → Service → Logs
- Common issues:
  - Missing Python dependencies (check requirements.txt)
  - Wrong port (should use PORT from env, not hardcoded 5000)

### Backend Connection Fails
- Check if MongoDB connection string is correct
- Verify EMOTION_SERVICE_URL is correct in environment
- Check Render logs for full error messages

### Deployment Takes Too Long
- Render free tier builds can take 10-15 minutes
- Be patient, don't cancel
- Check deployment logs for progress

---

## URLs to Save

After deployment, save these URLs:

```
Emotion Service URL: https://emotion-recognition-xxxxx.onrender.com
Backend Service URL: https://raga-rasa-backend-xxxxx.onrender.com

Test endpoints:
- Emotion Health: https://emotion-recognition-xxxxx.onrender.com/health
- Backend Health: https://raga-rasa-backend-xxxxx.onrender.com/health
```

---

## Next Steps (Day 2c)

Once both services are deployed and tested:

1. Create GitHub OAuth app (https://github.com/settings/developers)
2. Get Client ID and Secret
3. Add to Render backend environment variables
4. Backend will auto-redeploy

---

## Manual Redeploy (if needed)

If you need to redeploy a service later:
1. Go to Render dashboard
2. Select the service
3. Click "Manual Deploy" button
4. Choose branch (main)
5. Wait for redeployment

---

## Render Dashboard Tips

- **View Logs**: Select service → "Logs" tab
- **Environment Vars**: Select service → "Environment" tab  
- **Restart Service**: Select service → "Settings" tab → "Restart"
- **Delete Service**: Select service → "Settings" tab → "Delete Service"

---

**Status**: Ready for your action!  
Once you've completed the deployment steps, let me know the URLs and we'll test and move to Day 2c (GitHub OAuth).
