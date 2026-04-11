# Vercel Deployment - Updated Instructions

## ✅ Project Name Fixed

The vercel.json now specifies a valid project name: **`raga-rasa-frontend`**
- ✅ Lowercase
- ✅ Uses hyphens (not underscores)
- ✅ No invalid characters

## 🚀 Deploy to Vercel - Simplified Steps

### Step 1: Go to Vercel
Open: https://vercel.com/new

### Step 2: Sign In with GitHub
Click **"Continue with GitHub"**
- Login if needed
- Authorize Vercel

### Step 3: Import Project
Look for **`raga_rasa_music`** in your repos list
Click **Import**

### Step 4: Vercel Auto-Detects Settings
Vercel should automatically detect:
- ✅ Framework: Vite
- ✅ Build Command: `npm run build`
- ✅ Output: `dist`
- ✅ Root Directory: `raga-rasa-soul-main`
- ✅ Project Name: `raga-rasa-frontend` (from vercel.json)

**If Root Directory is empty**, manually set it to: `raga-rasa-soul-main`

### Step 5: Add Environment Variable
In the **"Environment Variables"** section:
- Name: `VITE_API_BASE_URL`
- Value: `https://raga-rasa-backend.onrender.com/api`
- Click **Add**

### Step 6: Deploy
Click **"Deploy"** button

Wait for build to complete (2-3 minutes)

### Step 7: Get Your Live URL
Once successful, you'll get a URL like:
```
https://raga-rasa-frontend.vercel.app
```

---

## ✅ What's Configured in vercel.json

```json
{
  "name": "raga-rasa-frontend",           // Valid project name
  "buildCommand": "npm run build",        // Builds React app
  "outputDirectory": "dist",              // Where built files go
  "framework": "vite",                    // Tells Vercel it's Vite
  "rewrites": [                           // SPA routing fix
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

---

## 🔗 Your Complete System (After Deploy)

| Service | URL | Status |
|---------|-----|--------|
| Frontend | `https://raga-rasa-frontend.vercel.app` | 🚀 Ready to Deploy |
| Backend | `https://raga-rasa-backend.onrender.com` | ✅ Live |
| Emotion Service | `https://raga-rasa-music.onrender.com` | ✅ Live |

---

## 📝 Git Info

- **Latest Commit**: `c75b05c0`
- **Changes**: Updated vercel.json with valid project name
- **Status**: ✅ Ready to deploy

---

**Next**: Go to https://vercel.com/new and start the deployment! 🚀
