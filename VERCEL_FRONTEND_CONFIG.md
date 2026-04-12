# Vercel Frontend Deployment Guide - RagaRasa Music Therapy

## Overview

The RagaRasa frontend is already deployed on Vercel. This guide explains how to update the backend URL configuration and redeploy if needed.

**Current Status:** ✅ Already deployed at https://raga-rasa-music-52.vercel.app
**Time to update config:** 2-3 minutes

---

## Architecture

```
                    ┌────────────────────────┐
                    │  Vercel (Frontend)     │
                    │ React + TypeScript     │
                    │ Vite Build Tool        │
                    └────────────┬───────────┘
                                 │ API calls
                                 ▼
                    ┌────────────────────────┐
                    │  Koyeb (Backend)       │
                    │  FastAPI               │
                    │  MongoDB Atlas         │
                    └────────────┬───────────┘
                                 │ calls
                                 ▼
                    ┌────────────────────────┐
                    │  HF Spaces (Emotions)  │
                    │  Emotion Recognition   │
                    └────────────────────────┘
```

---

## Current Deployment Status

### Frontend (Vercel)
- **Status:** ✅ Live
- **URL:** https://raga-rasa-music-52.vercel.app
- **Branch:** `main` (from `raga-rasa-soul-main/` subdirectory)
- **Auto-deploy:** Yes (on push to main)

### Backend (Koyeb)
- **Status:** 🔧 To be deployed
- **URL:** https://raga-rasa-backend-[randomid].koyeb.app (after deployment)
- **Port:** 8000

### Emotion Service (HF Spaces)
- **Status:** 🔧 To be deployed
- **URL:** https://[username]-raga-rasa-emotion.hf.space (after deployment)

---

## Step 1: Get Koyeb Backend URL

After deploying to Koyeb (see `KOYEB_BACKEND_DEPLOYMENT.md`), you'll have a URL like:

```
https://raga-rasa-backend-[randomid].koyeb.app
```

**Write this down - you'll need it in the next step.**

---

## Step 2: Update Frontend Configuration

### File Location
```
raga-rasa-soul-main/.env
```

### Current Content
```env
VITE_API_BASE_URL=https://raga-rasa-backend.onrender.com/api
```

### New Content
Replace with your Koyeb URL:

```env
VITE_API_BASE_URL=https://raga-rasa-backend-[randomid].koyeb.app/api
```

**Example:**
```env
VITE_API_BASE_URL=https://raga-rasa-backend-abc123xyz.koyeb.app/api
```

---

## Step 3: Update Code to Use Environment Variable

### File: `raga-rasa-soul-main/src/context/AuthContext.tsx`

The file should have:

```typescript
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://raga-rasa-backend.onrender.com/api';
```

This is already correct and will use the `.env` variable.

### File: `raga-rasa-soul-main/src/pages/Login.tsx`

Verify it uses the same pattern:

```typescript
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://raga-rasa-backend.onrender.com/api';
```

This is already correct.

---

## Step 4: Commit and Push Changes

```bash
cd raga-rasa-soul-main

# Stage changes
git add .env

# Commit
git commit -m "Update backend URL to Koyeb deployment"

# Push to GitHub
git push origin main
```

**Automatic Deployment:**
- Vercel watches the `main` branch
- Within 30-60 seconds, Vercel detects the change
- Automatically rebuilds and redeploys the frontend
- New deployment goes live immediately

---

## Step 5: Verify Deployment

### Check Vercel Dashboard

1. Go to https://vercel.com/dashboard
2. Click on your project
3. In **Deployments** tab:
   - Should see new deployment in progress
   - Status will show: Building → Ready
   - Takes about 1-2 minutes

### Check New Deployment

Once deployment completes:

1. Visit https://raga-rasa-music-52.vercel.app
2. Open browser console (F12 → Console)
3. Check for any errors
4. Should NOT see:
   - CORS errors
   - `401 Unauthorized` errors
   - Network connection errors

### Test API Connection

```bash
# In browser console, run:
fetch('https://raga-rasa-backend-[randomid].koyeb.app/api/health')
  .then(r => r.json())
  .then(console.log)
```

Expected response:
```json
{"status": "ok", "message": "Backend is running"}
```

---

## Step 6: Manual Redeploy (If Needed)

If automatic deployment doesn't work, manually redeploy from Vercel:

1. Go to https://vercel.com/dashboard
2. Click your project
3. In **Deployments** tab, click the **...** menu
4. Select **Redeploy**
5. Click **Redeploy** again to confirm

---

## Vercel Environment Variables (Alternative)

Instead of `.env` file, you can set variables in Vercel dashboard:

1. Go to project settings: https://vercel.com/dashboard
2. Click your project
3. Go to **Settings** → **Environment Variables**
4. Add:
   - **Key:** `VITE_API_BASE_URL`
   - **Value:** `https://raga-rasa-backend-[randomid].koyeb.app/api`
5. Click **Add**
6. Redeploy the project

**Note:** Variables in Vercel dashboard override `.env` files.

---

## Troubleshooting

### Issue: Frontend still connecting to old backend

**Solution:**
- Clear browser cache (Ctrl+Shift+Delete or Cmd+Shift+Delete)
- Clear Vercel cache:
  1. Go to Vercel dashboard
  2. Project → Settings → Git
  3. Click "Clear Build Cache"
  4. Redeploy
- Verify `.env` file was pushed: `git log --oneline` should show your commit

### Issue: CORS errors in console

**Solution:**
- Verify backend URL in `.env` is correct
- Backend Koyeb service must be running
- Verify `ALLOWED_ORIGINS_STR` in Koyeb includes:
  - `https://raga-rasa-music-52.vercel.app`
  - `https://*.vercel.app` (wildcard for preview URLs)

### Issue: 502/503 errors from backend

**Solution:**
- Backend service might be sleeping or down
- Check Koyeb dashboard: https://app.koyeb.com/services
- Service should show "Active" status
- Click service → **Logs** to check for errors
- Restart service if needed: **Actions** → **Restart**

### Issue: Emotion service not working

**Solution:**
- Verify HF Spaces emotion service is deployed
- Check backend logs for emotion service errors
- Verify `EMOTION_SERVICE_URL` in Koyeb env vars is correct
- HF Spaces might be sleeping - first request takes time

---

## Preview URLs

Vercel generates preview URLs for pull requests:

```
https://raga-rasa-[branch-name]-[randomid].vercel.app
```

These use the same backend as production, so they should also work once backend is configured.

**Note:** Backend CORS must allow these URLs using the pattern: `https://.*.vercel.app`

---

## Custom Domain (Optional)

To use a custom domain instead of `vercel.app`:

1. Purchase domain from registrar (Namecheap, GoDaddy, etc.)
2. In Vercel project settings:
   - Go to **Settings** → **Domains**
   - Click **Add Domain**
   - Enter your domain name
   - Vercel will guide you through DNS setup
3. Update backend CORS to allow your domain:
   ```env
   ALLOWED_ORIGINS_STR=https://yourdomain.com,https://*.vercel.app,...
   ```

---

## Production Best Practices

### 1. Environment Secrets
- Never commit API keys or passwords
- Use Vercel Environment Variables for sensitive data
- Mark as "Sensitive" in Vercel dashboard

### 2. Monitoring
- Enable Vercel Analytics: https://vercel.com/analytics
- Monitor API response times
- Check error rates

### 3. Caching
- Vercel caches static assets (HTML, CSS, JS)
- Set proper cache headers for API responses
- Use Vercel's Edge Caching for global distribution

### 4. Rate Limiting
- Backend implements rate limiting via SlowAPI
- Configure in Koyeb if needed
- Protects against abuse

---

## Deployment Checklist

- [ ] Created Koyeb account
- [ ] Deployed backend on Koyeb
- [ ] Have Koyeb backend URL
- [ ] Deployed emotion service on HF Spaces
- [ ] Have HF Spaces emotion service URL
- [ ] Updated Koyeb env vars with emotion service URL
- [ ] Updated frontend `.env` with Koyeb URL
- [ ] Pushed changes to GitHub
- [ ] Vercel automatically redeployed
- [ ] Tested frontend → backend connection
- [ ] Tested complete emotion detection flow
- [ ] No CORS errors in console
- [ ] All API endpoints responding correctly

---

## Next Steps

1. ✅ Frontend already deployed on Vercel
2. ⬜ Deploy emotion service on HF Spaces
3. ⬜ Deploy backend on Koyeb
4. ✅ Update frontend configuration (this step)
5. ⬜ Run end-to-end tests

---

## Support & References

- Vercel Docs: https://vercel.com/docs
- Vercel Environment Variables: https://vercel.com/docs/concepts/projects/environment-variables
- Vite Environment Variables: https://vitejs.dev/guide/env-and-modes

---

**Your frontend is ready! Just update the backend URL and you're set.**
