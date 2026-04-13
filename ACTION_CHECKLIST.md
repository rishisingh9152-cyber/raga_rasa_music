# IMMEDIATE ACTION CHECKLIST - CORS Fix

## Status: Code Ready ✅ | Awaiting Render Env Update ⏳

---

## YOUR ACTION REQUIRED (5 minutes)

### Step 1: Update Render Environment Variable

```
1. Visit: https://render.com/dashboard
2. Click: "raga-rasa-backend-gopl" web service
3. Click: "Settings" tab
4. Find: "ALLOWED_ORIGINS" environment variable
5. Replace old URL with new URL (see below)
6. Click: "Save" button
```

### What to Change

**Old Value:**
```
https://raga-rasa-music-52-iaimxdrak-rishisingh9152-cybers-projects.vercel.app,http://localhost:5173,http://localhost:3000
```

**New Value:**
```
https://raga-rasa-music-52.vercel.app,http://localhost:5173,http://localhost:3000
```

### What Changed
- Removed: `iaimxdrak-rishisingh9152-cybers-projects` (preview URL suffix)
- Kept: Base URL `https://raga-rasa-music-52.vercel.app`
- Kept: Local dev URLs

---

## Step 2: Wait for Auto-Redeploy

- ⏱ **Time:** 2-3 minutes
- 📊 **Watch:** Render dashboard "Deployments" tab
- ✅ **Look for:** Green checkmark next to latest deployment

---

## Step 3: Test the Fix

### Browser Testing
1. Clear cache: **Ctrl+Shift+Delete**
2. Hard refresh: **Ctrl+F5**
3. Go to: https://raga-rasa-music-52.vercel.app
4. Check console for errors (press F12)

### Should See
- ✅ Songs loading in dropdown
- ✅ No CORS errors in console
- ✅ No "Failed to fetch" errors
- ✅ Session ID available
- ✅ API responses working

### Should NOT See
- ❌ "Blocked by CORS policy"
- ❌ "No 'Access-Control-Allow-Origin' header"
- ❌ "Failed to fetch"
- ❌ "net::ERR_FAILED"

---

## If It Still Doesn't Work

### Verify Backend is Running
```
Open in browser:
https://raga-rasa-backend-gopl.onrender.com/health

Should see:
{"status": "healthy", "service": "RagaRasa Music Therapy Backend", "version": "1.0.0"}
```

### Check Render Logs
```
1. Go to: https://render.com/dashboard
2. Click: "raga-rasa-backend-gopl"
3. Click: "Logs" tab
4. Look for: Any "ImportError" or "Exception" messages
```

### Common Issues

**Issue:** Backend returns 500 error
- **Fix:** Check MongoDB connection in logs

**Issue:** Backend keeps crashing
- **Fix:** Verify libgl1-mesa-glx is in Dockerfile (line 17)

**Issue:** CORS still failing
- **Fix:** Verify ALLOWED_ORIGINS was saved (check value again)

---

## Files Already Updated (No Action Needed)

✅ `Backend/main.py` - CORS middleware configured
✅ `Backend/app/middleware/cors.py` - Proper CORS handling
✅ `Backend/app/config.py` - Origin patterns set
✅ `Backend/Dockerfile` - libgl1-mesa-glx added
✅ `Backend/.env.production` - Frontend URL configured
✅ `raga-rasa-soul-main/.env` - Backend URL configured
✅ All frontend instances updated

---

## Support Links

- **Render Dashboard:** https://render.com/dashboard
- **Vercel Frontend:** https://raga-rasa-music-52.vercel.app
- **Backend Health Check:** https://raga-rasa-backend-gopl.onrender.com/health
- **Backend API Docs:** https://raga-rasa-backend-gopl.onrender.com/docs

---

## Expected Timeline

| Task | Time | Status |
|------|------|--------|
| Update Render env var | 1 min | ⏳ YOU DO THIS |
| Backend redeploy | 2-3 min | ⏳ AUTOMATIC |
| Cache clear + refresh | 1 min | ⏳ YOU DO THIS |
| Full fix complete | **4-5 min** | 📈 TOTAL TIME |

---

## TL;DR

1. ⏳ Go to Render dashboard
2. 🔧 Change ALLOWED_ORIGINS to: `https://raga-rasa-music-52.vercel.app,http://localhost:5173,http://localhost:3000`
3. 💾 Click Save
4. ⏱ Wait 2-3 minutes
5. 🔄 Ctrl+Shift+Delete, then Ctrl+F5 on frontend
6. ✅ Test and enjoy!

**That's it!** CORS errors should be gone.
