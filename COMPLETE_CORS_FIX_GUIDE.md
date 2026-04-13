# Complete CORS & API Connectivity Fix Guide

## Root Cause Analysis

Your CORS errors are happening because:

1. ❌ Frontend URL mismatch: `https://raga-rasa-music-52.vercel.app`
2. ❌ Backend CORS config: Still has old URL `https://raga-rasa-music-52-iaimxdrak-rishisingh9152-cybers-projects.vercel.app`
3. ❌ Render env variable: Not updated after the fix
4. ❌ Missing libgl1-mesa-glx: Causing container to crash

---

## Complete Step-by-Step Fix

### Part A: Backend Code (Already Fixed)

#### 1. CORS Middleware (`app/middleware/cors.py`) ✅
- Supports regex patterns for Vercel wildcard domains
- Handles preflight OPTIONS requests correctly
- Adds proper CORS headers to responses

**Current Status:** ✅ WORKING (no changes needed)

#### 2. Main App (`main.py`) ✅
- Custom CORS middleware registered
- OPTIONS handler for preflight requests
- Routes properly prefixed with `/api`

**Current Status:** ✅ WORKING (no changes needed)

#### 3. Config (`app/config.py`) ✅
- `ALLOWED_ORIGINS_STR`: Production + localhost URLs
- `ALLOWED_ORIGINS_REGEX`: `r"https://.*\.vercel\.app"` (matches all Vercel URLs)
- `ALLOWED_METHODS`: GET, POST, PUT, DELETE, OPTIONS, PATCH

**Current Status:** ⚠️ NEEDS ENVIRONMENT VARIABLE UPDATE

---

### Part B: Environment Variable on Render (⚠️ CRITICAL - YOU MUST DO THIS)

**The Problem:**
Your Render service has the old Vercel URL in the environment variable.

**What to Update:**

Navigate to Render Dashboard:
```
https://render.com/dashboard
→ Click "raga-rasa-backend-gopl"
→ Click "Settings" tab
→ Find "ALLOWED_ORIGINS" environment variable
```

**Current Value (Wrong):**
```
https://raga-rasa-music-52-iaimxdrak-rishisingh9152-cybers-projects.vercel.app,http://localhost:5173,http://localhost:3000
```

**New Value (Correct):**
```
https://raga-rasa-music-52.vercel.app,http://localhost:5173,http://localhost:3000
```

**Steps:**
1. Click the pencil icon next to ALLOWED_ORIGINS
2. Replace the old URL with the new one
3. Click "Save"
4. Render will auto-redeploy (2-3 minutes)

---

### Part C: Also Update the Dockerfile Fix

Make sure the Dockerfile has the missing libgl1-mesa-glx library.

**Check if this line exists in Dockerfile (line 17):**
```dockerfile
libgl1-mesa-glx \
```

If not, add it to the RUN apt-get install command.

**Status:** Should be in latest commit `94e4c4e3`

---

### Part D: Frontend Configuration (React/Vercel)

#### 1. Check .env file (`raga-rasa-soul-main/.env`)
```
VITE_API_BASE_URL=https://raga-rasa-backend-gopl.onrender.com/api
```

**Status:** ✅ Should be correct from earlier updates

#### 2. API Service (`src/services/api.ts`)
```typescript
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";
```

**Status:** ✅ Should be correct

#### 3. Fetch Requests (in React components)
```typescript
const response = await fetch(`${API_BASE_URL}/songs/by-rasa`, {
  method: "GET",
  headers: { "Content-Type": "application/json" }
  // DO NOT include credentials unless backend expects them
});
```

**Status:** ✅ Should be correct

---

### Part E: Verify CORS is Working

#### Test 1: Check CORS Headers with curl
```bash
curl -i -X OPTIONS \
  -H "Origin: https://raga-rasa-music-52.vercel.app" \
  -H "Access-Control-Request-Method: GET" \
  https://raga-rasa-backend-gopl.onrender.com/api/songs/by-rasa
```

**Expected Response:**
```
HTTP/1.1 200 OK
access-control-allow-origin: https://raga-rasa-music-52.vercel.app
access-control-allow-methods: GET, POST, PUT, DELETE, OPTIONS, PATCH
access-control-allow-headers: *
access-control-allow-credentials: true
```

#### Test 2: Test API Endpoint with curl
```bash
curl -i -X GET \
  -H "Origin: https://raga-rasa-music-52.vercel.app" \
  https://raga-rasa-backend-gopl.onrender.com/api/songs/by-rasa
```

**Should return 200 with songs data + CORS headers**

#### Test 3: Check Backend Logs
Go to Render dashboard → "Logs" tab:
```
[OK] Database initialized
[OK] All workers started
```

No `ImportError: libGL.so.1` errors

#### Test 4: Test in Browser Console
```javascript
// Open browser console and run:
fetch('https://raga-rasa-backend-gopl.onrender.com/api/health', {
  method: 'GET',
  headers: { 'Content-Type': 'application/json' }
})
.then(r => r.json())
.then(data => console.log('SUCCESS:', data))
.catch(e => console.error('ERROR:', e))
```

**Expected:** Should log success object with status "healthy"

---

## Summary of Issues & Fixes

| Issue | Status | Fix |
|-------|--------|-----|
| CORS header missing | ✅ Code ready | Update Render env var |
| Wrong Vercel URL | ✅ Code ready | Update Render env var |
| Missing OpenGL lib | ✅ Dockerfile fixed | Redeploy on Render |
| Frontend config | ✅ Already updated | Nothing to do |
| Backend config | ✅ Already updated | Nothing to do |

---

## What YOU Need to Do

### Immediate (REQUIRED):

1. **Go to Render Dashboard** (https://render.com/dashboard)
2. **Update ALLOWED_ORIGINS** environment variable
   - Old: `https://raga-rasa-music-52-iaimxdrak-...vercel.app,...`
   - New: `https://raga-rasa-music-52.vercel.app,http://localhost:5173,http://localhost:3000`
3. **Wait for auto-redeploy** (2-3 minutes)

### Testing (After Redeploy):

1. **Clear browser cache** (Ctrl+Shift+Delete)
2. **Hard refresh** (Ctrl+F5)
3. **Check browser console** for errors
4. **Try accessing frontend** (https://raga-rasa-music-52.vercel.app)
5. **Test song fetch** (should load songs without CORS error)

---

## Why This Works

✅ **Custom CORS Middleware**: Properly validates origins and adds headers
✅ **OPTIONS Handler**: Responds to preflight requests immediately
✅ **Regex Pattern**: Matches any Vercel deployment (*.vercel.app)
✅ **Environment Variable**: Allows specific origins in addition to regex
✅ **Credentials Support**: Enabled for session/cookie-based auth
✅ **Proper Headers**: All required CORS headers included

---

## If Issues Persist

### Still Getting CORS Error?

1. Check Render logs for the exact error
2. Verify ALLOWED_ORIGINS env var was saved
3. Verify backend redeployed (check deployment timestamp)
4. Test with curl first (not browser)
5. Check if Vercel URL is exactly correct (case-sensitive)

### Still Getting "Failed to Fetch"?

1. Check backend health: `https://raga-rasa-backend-gopl.onrender.com/health`
2. Check MongoDB connection in Render logs
3. Verify all environment variables are set
4. Check for 500 errors in Render logs

### Getting 405 Method Not Allowed?

1. Verify endpoint exists in backend code
2. Ensure correct HTTP method (GET vs POST)
3. Check route prefix in main.py (`/api`)
4. Verify OPTIONS requests are handled

---

## Next Steps

1. ✅ Update Render environment variable (YOUR ACTION)
2. ⏳ Wait for backend redeploy
3. ⏳ Test frontend
4. ⏳ If errors, check logs and report errors

The fix is ready - just need to update that ONE environment variable on Render!
