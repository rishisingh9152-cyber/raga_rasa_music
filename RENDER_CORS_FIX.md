# URGENT: Update Render Backend Environment Variables

## Problem
CORS error: The backend is rejecting requests from the frontend because the `ALLOWED_ORIGINS` environment variable is incorrect.

**Current:** `https://raga-rasa-music-52-iaimxdrak-rishisingh9152-cybers-projects.vercel.app`
**Should be:** `https://raga-rasa-music-52.vercel.app`

---

## Solution: Update Render Environment Variables

### Step 1: Go to Render Dashboard
1. Visit https://render.com/dashboard
2. Click on your **raga-rasa-backend-gopl** web service

### Step 2: Edit Environment Variables
1. Click the **Settings** tab
2. Scroll to **Environment** section
3. Find the line with `ALLOWED_ORIGINS`
4. Click the **pencil icon** to edit it

### Step 3: Update the Value
**Replace:**
```
https://raga-rasa-music-52-iaimxdrak-rishisingh9152-cybers-projects.vercel.app,http://localhost:5173,http://localhost:3000
```

**With:**
```
https://raga-rasa-music-52.vercel.app,http://localhost:5173,http://localhost:3000
```

### Step 4: Save and Redeploy
1. Click **Save** 
2. Render will automatically redeploy the service (takes ~2-3 minutes)
3. Wait for the deployment to complete

### Step 5: Test
1. Clear browser cache (Ctrl+Shift+Delete)
2. Hard refresh (Ctrl+F5)
3. Try accessing the frontend again

---

## Environment Variable to Update

```
ALLOWED_ORIGINS=https://raga-rasa-music-52.vercel.app,http://localhost:5173,http://localhost:3000
```

---

## What We've Done Locally

✅ Updated `.env.production` with the correct frontend URL
✅ Ready to push changes to GitHub

Once you update the Render environment variable, the CORS error should be resolved!
