# RagaRasa Deployment Troubleshooting Guide

## Common Issues & Solutions

---

## 🔴 CRITICAL ISSUES

### 1. CORS Errors in Browser Console

**Error Message:**
```
Access to XMLHttpRequest at 'https://...' from origin 'https://...' has been blocked by CORS policy
```

**Root Causes:**
- Backend's `ALLOWED_ORIGINS_STR` doesn't include frontend URL
- Backend's `ALLOWED_ORIGINS_REGEX` doesn't match frontend URL pattern
- Frontend is using a Vercel preview URL that wasn't anticipated

**Solutions:**

**Option A: Fix via Environment Variable (Recommended)**
```bash
# In Koyeb backend settings, set:
ALLOWED_ORIGINS_STR=https://raga-rasa-music-52.vercel.app,http://localhost:5173,http://localhost:8080

# The regex pattern automatically handles *.vercel.app
ALLOWED_ORIGINS_REGEX=https://.*\.vercel\.app
```

**Option B: Verify Backend CORS Configuration**

Check `Backend/app/config.py`:
```python
ALLOWED_ORIGINS_STR = os.getenv("ALLOWED_ORIGINS_STR", "...")
ALLOWED_ORIGINS_REGEX = os.getenv("ALLOWED_ORIGINS_REGEX", r"https://.*\.vercel\.app")
```

**Option C: Test CORS from Browser Console**
```javascript
// Check what origins are actually being used
const testUrl = 'https://your-koyeb-url.koyeb.app/health';
fetch(testUrl)
  .then(r => console.log('CORS OK:', r.status))
  .catch(e => console.error('CORS Error:', e.message));
```

**Option D: Check Backend Logs**
```bash
# In Koyeb dashboard:
1. Go to your service
2. Click "Logs" tab
3. Look for CORS-related messages
4. Check what origin was rejected
```

---

### 2. Backend Returns 502/503 Errors

**Error Message:**
```
502 Bad Gateway
503 Service Unavailable
```

**Root Causes:**
- Backend service crashed or didn't start
- Database connection failed
- Memory limit exceeded
- Timeout during cold start

**Solutions:**

**Step 1: Check Service Status**
```bash
# In Koyeb dashboard:
1. Go to Services → your-backend-service
2. Check status indicator (should be green "Active")
3. If red, service has crashed
```

**Step 2: Check Backend Logs**
```bash
# In Koyeb dashboard:
1. Click "Logs" tab
2. Filter by "Runtime" (not Build)
3. Look for errors in recent logs
# Common errors:
# - "Connection refused" → Database issue
# - "timeout" → Slow startup
# - "ModuleNotFoundError" → Missing dependency
```

**Step 3: Restart Service**
```bash
# In Koyeb dashboard:
1. Click "Actions" dropdown (top right)
2. Select "Restart"
3. Wait 30 seconds
4. Test again: curl https://your-url.koyeb.app/health
```

**Step 4: Check Environment Variables**
```bash
# In Koyeb dashboard → Settings → Environment Variables:
- MONGODB_URL must be valid and complete
- JWT_SECRET_KEY must be set
- EMOTION_SERVICE_URL must be set
- All required variables must have values
```

**Step 5: Increase Resources (if out of memory)**
```bash
# In Koyeb dashboard → Settings → Resources:
1. Increase RAM from 512 MB to 1 GB
2. Or increase Max instances to 2
3. Click Save
4. Service will restart automatically
```

---

### 3. Database Connection Fails

**Error Message:**
```
Failed to connect to MongoDB: timed out
Connection refused
Authentication failed
```

**Root Causes:**
- Invalid MongoDB URL in `MONGODB_URL`
- MongoDB Atlas whitelist doesn't allow deployment IP
- Database credentials are wrong
- Network connectivity issue

**Solutions:**

**Step 1: Verify MongoDB URL Format**
```
Correct format:
mongodb+srv://username:password@cluster.mongodb.net/?appName=AppName

Common mistakes:
❌ mongodb://localhost:27017  (local, won't work in cloud)
❌ mongodb+srv://user:pass@cluster  (missing parameters)
✅ mongodb+srv://Rishi123:Rishi_123@majorproject.lpwzhzc.mongodb.net/?appName=MajorProject
```

**Step 2: Check MongoDB Atlas Whitelist**
```bash
# Go to MongoDB Atlas → Network Access:
1. Click "+ Add IP Address"
2. Add: 0.0.0.0/0 (allows all IPs)
# OR add specific Koyeb deployment IP (found in logs)
3. Click Confirm
```

**Step 3: Test Connection Locally**
```bash
# Install MongoDB client:
# Windows: choco install mongodb-cli
# macOS: brew install mongosh
# Linux: sudo apt-get install mongosh

# Test connection:
mongosh "mongodb+srv://Rishi123:Rishi_123@majorproject.lpwzhzc.mongodb.net/raga_rasa"
# You should connect and see a prompt
```

**Step 4: Check Backend Logs for Exact Error**
```bash
# In Koyeb logs, look for:
# - "Connection timeout" → IP whitelist issue
# - "Authentication failed" → Wrong credentials
# - "Invalid hostname" → Wrong URL format
```

---

### 4. Emotion Detection Returns Error

**Error Message:**
```
500 Internal Server Error
503 Service Unavailable
Emotion detector not initialized
```

**Root Causes:**
- HF Spaces emotion service is sleeping or down
- `EMOTION_SERVICE_URL` is wrong or unreachable
- Emotion service didn't start properly

**Solutions:**

**Step 1: Test HF Spaces Directly**
```bash
# Get your HF Spaces URL and test it:
curl https://[username]-raga-rasa-emotion.hf.space/health

# Should return:
# {"status": "ok", "service": "emotion-recognition", ...}

# If fails:
# - Service is sleeping (first request takes 30-60 seconds)
# - Service has errors (check HF Spaces logs)
# - URL is wrong
```

**Step 2: Verify Emotion Service URL in Backend**
```bash
# In Koyeb backend logs, look for:
[Emotion] Attempting external emotion detection...

# Should show successful emotion detection
# If shows errors, check EMOTION_SERVICE_URL env var
```

**Step 3: Check Backend Env Variable**
```bash
# In Koyeb dashboard → Settings → Environment Variables:
EMOTION_SERVICE_URL must be:
- Correct URL (https://[username]-raga-rasa-emotion.hf.space)
- Not localhost (won't work in cloud)
- Not typo'd or malformed
```

**Step 4: HF Spaces Sleep Issue**
```bash
# HF Spaces free tier sleeps after 24 hours of inactivity
# First request after sleep takes 30-60 seconds
# Solution: Keep it warm OR upgrade to paid tier

# To keep warm temporarily:
# 1. Visit HF Spaces URL regularly
# 2. Or add uptime monitoring service
# 3. Or upgrade to CPU Upgrade tier ($3.50/month)
```

---

## 🟡 HIGH PRIORITY ISSUES

### 5. Frontend Loads Blank Page

**Symptoms:**
- Page loads but shows nothing
- No errors in console initially
- Then network errors appear

**Root Causes:**
- Frontend .env variable not set
- Wrong API base URL
- Frontend build didn't include env variables

**Solutions:**

**Step 1: Check Frontend .env**
```bash
# File: raga-rasa-soul-main/.env

# Must have:
VITE_API_BASE_URL=https://your-koyeb-url.koyeb.app/api

# Must NOT have:
✅ Full URL with https://
✅ /api suffix included
❌ localhost (in production)
❌ Without /api suffix
```

**Step 2: Clear Browser Cache**
```bash
# Chrome/Edge: Ctrl+Shift+Delete or Cmd+Shift+Delete
# Firefox: Ctrl+Shift+Delete
# Safari: Develop menu → Empty Caches
# Then hard refresh: Ctrl+F5 or Cmd+Shift+R
```

**Step 3: Check if Vercel Redeployed**
```bash
# In Vercel dashboard:
1. Click your project
2. Go to "Deployments" tab
3. Check if latest deployment is "Ready" (not "Building")
4. If still building, wait for it to complete
5. If failed, check build logs for errors
```

**Step 4: Verify .env Was Pushed to GitHub**
```bash
# Check git history:
git log --oneline -5 | grep -i "env\|backend\|url"

# Should show recent commit with .env changes
# If not, need to:
git add raga-rasa-soul-main/.env
git commit -m "Update backend URL"
git push origin main
```

---

### 6. API Calls Timeout

**Error Message:**
```
Timeout waiting for response
504 Gateway Timeout
Request timeout
```

**Root Causes:**
- Backend is slow or cold-starting
- Large response data (e.g., loading all songs)
- Database query is expensive
- Network latency

**Solutions:**

**Step 1: Check Cold Start Time**
```bash
# First request to Koyeb takes 10-30 seconds
# Subsequent requests are fast (< 1 second)
# This is normal - just wait longer for first request
```

**Step 2: Increase Timeout in Frontend**

If using axios:
```typescript
// In src/services/api.ts or axios config:
import axios from 'axios';

// Increase default timeout to 60 seconds
axios.defaults.timeout = 60000;

// Or per request:
fetch(url, { timeout: 60000 })
```

**Step 3: Optimize Slow Queries**

If specifically catalog/songs endpoint is slow:
```bash
# In Koyeb logs, look for query times
# Consider:
- Adding database indexes
- Paginating results (return 20 instead of all)
- Caching results
```

**Step 4: Monitor Koyeb Resources**
```bash
# In Koyeb dashboard → Metrics:
- CPU usage should be < 80%
- Memory should be < 90%
- If consistently maxed out, increase resources
```

---

## 🟢 MEDIUM PRIORITY ISSUES

### 7. Songs Don't Load

**Symptoms:**
- API responds but returns empty list
- Songs show as "undefined"
- No audio URLs

**Root Causes:**
- Database is empty
- Songs collection doesn't exist
- Cloudinary URLs are broken

**Solutions:**

**Step 1: Check If Database Has Songs**
```bash
# In Koyeb dashboard → test endpoint:
curl https://your-url.koyeb.app/api/catalog/songs

# Should return array with songs
# If empty, database might not be seeded
```

**Step 2: Seed Database**
```bash
# If database is empty, you need to add songs
# See: raga_rasa_music/seed_data.py or seed_all_data.py

# Run locally:
python seed_all_data.py

# Or check MongoDB Atlas directly:
# Go to Collections → songs
# Should see documents with title, rasa, audio_url
```

**Step 3: Check Audio URLs**
```bash
# In MongoDB Atlas:
1. Go to Collections → songs
2. Look at documents
3. audio_url should be:
   ✅ Valid Cloudinary URL: https://res.cloudinary.com/...
   ✅ Or valid web URL
   ❌ NOT empty
   ❌ NOT file:// paths

# If broken, need to update URLs:
# Using: Backend/fix_cloudinary_urls.py or similar
```

---

### 8. User Authentication Fails

**Symptoms:**
- Can't log in
- Token not being saved
- Redirects back to login

**Root Causes:**
- Backend auth endpoint not working
- LocalStorage not persisting
- JWT token invalid

**Solutions:**

**Step 1: Check Auth Endpoint**
```bash
# Test login endpoint:
curl -X POST https://your-url.koyeb.app/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'

# Should return:
# {
#   "access_token": "...",
#   "user": { "user_id": "...", "email": "..." }
# }

# If 401 or 500, check backend logs
```

**Step 2: Check LocalStorage**
```javascript
// In browser console:
console.log(localStorage.getItem('auth_token'));
console.log(localStorage.getItem('user'));

// Should show JWT token and user object
// If null, localStorage might be disabled or cleared
```

**Step 3: Check JWT_SECRET_KEY**
```bash
# In Koyeb env vars:
JWT_SECRET_KEY must be set to a strong value

# If changed after users logged in:
# Existing tokens become invalid (users must re-login)
```

---

## 📝 DEBUGGING COMMANDS

### View Frontend Network Traffic
```javascript
// In browser console:
// See all API calls
console.log(document.querySelectorAll('img[src*="api"]'));

// Monitor fetch calls
const originalFetch = window.fetch;
window.fetch = function(...args) {
  console.log('Fetch:', args);
  return originalFetch.apply(this, args);
};
```

### View Backend Logs
```bash
# Get last 100 lines of logs:
koyeb service logs your-service-name -t runtime --tail 100

# Stream logs in real-time:
koyeb service logs your-service-name -t runtime --follow

# Filter by error:
koyeb service logs your-service-name -t runtime | grep -i error
```

### Test All Endpoints
```bash
# Health check
curl https://your-url.koyeb.app/health

# Database test
curl https://your-url.koyeb.app/db-test

# Emotion service health
curl https://your-url.koyeb.app/api/emotion-service/health

# Catalog
curl https://your-url.koyeb.app/api/catalog/songs

# Ragas
curl https://your-url.koyeb.app/api/catalog/ragas
```

---

## 🆘 EMERGENCY PROCEDURES

### Service Won't Start
1. Check Koyeb logs for error message
2. Restart service (Koyeb dashboard → Actions → Restart)
3. Increase resources (RAM to 1 GB)
4. Check all environment variables are set
5. Verify Procfile is correct

### Database Locked
1. Wait 30 seconds
2. Restart backend service
3. Check MongoDB Atlas → Metrics for issues
4. Restart MongoDB cluster if needed

### Complete Loss of Service
1. Revert latest code changes: `git revert HEAD`
2. Push to GitHub
3. Koyeb auto-redeploys
4. If still down, check git history for what broke

---

## 📞 GETTING HELP

### Before Contacting Support, Gather:
1. **Error message** (exact text from console/logs)
2. **Timestamp** (when error occurred)
3. **Your actions** (what were you doing when it broke)
4. **Backend logs** (last 20 lines from Koyeb)
5. **Browser console** (screenshot of errors)
6. **Environment** (dev/staging/production)

### Debugging Checklist
- [ ] Cleared browser cache
- [ ] Restarted backend service
- [ ] Checked all environment variables
- [ ] Verified database connectivity
- [ ] Tested endpoints directly with curl
- [ ] Checked backend logs
- [ ] Verified frontend .env is set
- [ ] Checked CORS configuration

---

## 📚 Quick Reference

| Issue | Quick Fix |
|-------|-----------|
| CORS error | Update `ALLOWED_ORIGINS_STR` in Koyeb |
| 502 error | Restart Koyeb service |
| Empty database | Run seed script or add songs manually |
| Blank page | Clear cache + verify .env + check Vercel deployment |
| Slow API | Wait for cold start (first request slow) |
| Emotion fails | Check HF Spaces URL and service status |
| Token invalid | Re-login, check JWT_SECRET_KEY |
| Songs empty | Check MongoDB collections and Cloudinary URLs |

---

**Still stuck? Check the deployment guides for your specific platform:**
- Backend: `KOYEB_BACKEND_DEPLOYMENT.md`
- Frontend: `VERCEL_FRONTEND_CONFIG.md`
- Emotion: `HF_SPACES_DEPLOYMENT_GUIDE.md`
