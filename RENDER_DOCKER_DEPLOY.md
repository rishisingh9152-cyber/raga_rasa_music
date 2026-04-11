# 🚀 Render Docker Deployment Guide

## Current Status
✅ Docker configuration complete and pushed to GitHub
✅ Python 3.10.13 explicitly specified in Dockerfile
✅ All ML dependencies included in requirements.txt

**Latest Commit:** `50fe1552` - Docker support ready

---

## 📋 Step-by-Step Deployment Instructions

### **IMPORTANT: Read This First**
The Dockerfile is located at: `Backend/Dockerfile`
When creating the service in Render, set **Root Directory** to `Backend` so Render finds the Dockerfile.

---

## **Step 1: Delete Old Service (Optional but Recommended)**

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Find `raga-rasa-backend` service
3. Click on it → Settings → Scroll down
4. Click **Delete Service**
5. Confirm deletion

---

## **Step 2: Create New Web Service**

1. Click **New +** button (top right)
2. Select **Web Service**
3. Choose **Deploy an existing repository** 
4. Search for: `raga_rasa_music`
5. Select the repo `rishisingh9152-cyber/raga_rasa_music`
6. Click **Connect**

---

## **Step 3: Configure Service**

Fill in these fields EXACTLY:

| Field | Value |
|-------|-------|
| Name | `raga-rasa-backend` |
| Environment | `Docker` |
| Region | `Ohio` (or closest) |
| Branch | `main` |
| **Root Directory** | `Backend` ⚠️ **IMPORTANT** |

**Leave these blank (Render will auto-detect):**
- Build Command (Render detects Dockerfile)
- Start Command (Dockerfile has CMD)

---

## **Step 4: Add Environment Variables**

Scroll down to **Advanced** section and click **Add Environment Variable** for each:

### Required Variables:

```
Name: MONGODB_URL
Value: mongodb+srv://Rishi123:Rishi_123@majorproject.lpwzhzc.mongodb.net/?appName=MajorProject
```

```
Name: EMOTION_SERVICE_URL
Value: https://raga-rasa-music.onrender.com
```

```
Name: JWT_SECRET
Value: dt_aRvdBIakTz2GI_qC4U1EqVVgmq4nrRDSc5XX73iY
```

### Optional Variables (can leave default):

```
Name: REDIS_URL
Value: (leave blank if no Redis on Render)
```

```
Name: DATABASE_NAME
Value: raga_rasa
```

```
Name: USE_EXTERNAL_EMOTION_SERVICE
Value: true
```

```
Name: EMOTION_SERVICE_ENDPOINT
Value: /detect
```

---

## **Step 5: Create & Deploy**

1. Scroll to bottom
2. Click **Create Web Service**
3. Wait for deployment (5-15 minutes)
4. Monitor the logs

---

## **Step 6: Verify Deployment**

Once deployed, you'll get a URL like: `https://raga-rasa-backend-xxxx.onrender.com`

Test these endpoints:

```bash
# Health check
curl https://raga-rasa-backend-xxxx.onrender.com/health

# Root
curl https://raga-rasa-backend-xxxx.onrender.com/

# Test endpoint
curl https://raga-rasa-backend-xxxx.onrender.com/test
```

Expected responses:
- `/health` → `{"status": "ok", ...}`
- `/` → Your API info
- `/test` → `{"status": "ok"}`

---

## 🐛 **Troubleshooting**

### If build fails with "Dockerfile not found":
- ❌ Make sure Root Directory is set to `Backend` (not empty, not `/`)
- Go back to settings and update it

### If container crashes:
- Check Logs tab in Render
- Make sure all environment variables are set correctly

### If "Cannot connect to MongoDB":
- Verify `MONGODB_URL` is correct
- Check MongoDB Atlas IP whitelist includes Render

### If "Cannot reach emotion service":
- The emotion service must be deployed at the URL provided
- Currently set to: `https://raga-rasa-music.onrender.com`

---

## ✨ **What This Docker Setup Does**

✅ Uses Python 3.10.13 (no more version conflicts!)
✅ Installs all ML dependencies (TensorFlow, OpenCV, etc.)
✅ Runs gunicorn with 4 workers
✅ Includes health checks
✅ All your app modules load correctly

---

## 📊 **Build Information**

- **Base Image:** `python:3.10.13-slim`
- **Start Command:** `gunicorn --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 main:app`
- **Port:** 8000
- **Health Check:** `/health` endpoint

---

## 🆘 **Need Help?**

If deployment fails:
1. Check Render logs tab
2. Look for specific error message
3. Common issues are environment variables or MongoDB connection
4. Feel free to ask for help debugging!

---

**Good luck! 🎯**
