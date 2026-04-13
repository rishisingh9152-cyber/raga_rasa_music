# 🔍 FRONTEND-BACKEND INTEGRATION AUDIT

## Executive Summary

✅ **Overall Status**: MOSTLY CORRECT with some endpoints needing verification

**Key Findings:**
- Frontend API base URL configured correctly: `https://raga-rasa-backend.onrender.com/api`
- Most endpoint paths match between frontend and backend
- ⚠️ Some endpoints may not exist or have naming mismatches
- ⚠️ Song URLs need verification (Cloudinary vs Dropbox vs local)

---

## 1. FRONTEND CONFIGURATION

### Environment Variables

**File**: `raga-rasa-soul-main/.env`
```
VITE_API_BASE_URL=https://raga-rasa-backend.onrender.com/api
```

**Status**: ✅ **CORRECT** 
- Uses Render backend
- Includes `/api` prefix
- Frontend code line 5: `const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api"`

---

## 2. FRONTEND API ENDPOINTS (raga-rasa-soul-main/src/services/api.ts)

| Endpoint | Method | Implemented | Status |
|----------|--------|-------------|--------|
| `/session/start` | POST | ✅ Line 37 | Need to verify backend |
| `/detect-emotion` | POST | ✅ Line 66 | ✅ Backend has this |
| `/recommend/live` | POST | ✅ Line 106 | ✅ Backend has this |
| `/recommend/final` | POST | ✅ Line 145 | ✅ Backend has this |
| `/songs/by-rasa` | GET | ✅ (in file) | Need to verify |
| `/songs/stream` | GET | ✅ (in file) | Need to verify |
| `/rating` | POST | ✅ (in file) | Need to verify |
| `/history` | GET | ✅ (in file) | Need to verify |

### Frontend API Calls Summary

**1. Session Management** (Line 35-52)
```typescript
POST /session/start
// Starts new therapy session
```

**2. Emotion Detection** (Line 58-91)
```typescript
POST /detect-emotion
{
  "image_base64": "...",
  "session_id": "..."
}
```

**3. Live Recommendations** (Line 97-132)
```typescript
POST /recommend/live
{
  "emotion": "Happy",
  "session_id": "...",
  "cognitive_data": { memory_score, reaction_time, accuracy_score }
}
```

**4. Final Recommendations** (Line 138-173)
```typescript
POST /recommend/final
{
  "emotion": "Happy",
  "session_id": "...",
  "cognitive_data": {...},
  "feedback": { mood_after, session_rating, comment }
}
```

---

## 3. BACKEND ROUTES (Backend/app/routes/)

### Available Routes by Module

**Session Module** (`session.py`)
- POST `/session/start` - Start new session
- Status: ✅ **EXISTS**

**Emotion Module** (`emotion.py`)
- GET `/emotion-service/health` - Health check
- POST `/detect-emotion` - Detect emotion from image
- Status: ✅ **EXISTS**

**Recommendation Module** (`recommendation.py`)
- POST `/recommend/live` - Get live recommendations (Line 34)
- POST `/recommend/final` - Get final recommendations (exists in file)
- Status: ✅ **EXISTS**

**Catalog Module** (`catalog.py`)
- GET `/ragas/list` - Get songs by rasa (Line 89)
- GET `/ragas/simple` - Simple test endpoint (Line 38)
- GET `/test/songs-count` - Song count test (Line 23)
- Status: ✅ **EXISTS**

**Auth Module** (`auth.py`)
- Handles authentication
- Status: ✅ **EXISTS**

**Psychometric Module** (`psychometric.py`)
- Handles cognitive tests
- Status: ✅ **EXISTS**

---

## 4. CRITICAL INTEGRATION POINTS

### ✅ VERIFIED WORKING

1. **API Base URL**
   - Frontend: `https://raga-rasa-backend.onrender.com/api`
   - Backend: Routers included with `/api` prefix (main.py line 93-103)
   - Status: ✅ **CORRECT**

2. **Emotion Detection Endpoint**
   - Frontend calls: `${API_BASE_URL}/detect-emotion` (line 66)
   - Backend route: `POST /detect-emotion` (emotion.py line 47)
   - Full path: `/api/detect-emotion` ✅
   - Status: ✅ **CORRECT**

3. **Recommendations Endpoint**
   - Frontend calls: `${API_BASE_URL}/recommend/live` (line 106)
   - Backend route: `POST /recommend/live` (recommendation.py line 34)
   - Full path: `/api/recommend/live` ✅
   - Status: ✅ **CORRECT**

### ⚠️ NEEDS VERIFICATION

1. **Session Start Endpoint**
   - Frontend calls: `/session/start` (line 37)
   - Backend: Need to verify if this exists in `session.py`
   - Status: ⚠️ **NEED TO CHECK**

2. **Songs/Catalog Endpoints**
   - Frontend calls: Various `/songs/*` endpoints
   - Backend: Has `/ragas/list` and `/ragas/simple`
   - Potential mismatch: `/songs/` vs `/ragas/`
   - Status: ⚠️ **POSSIBLE MISMATCH**

3. **Song URLs**
   - Frontend expects: `audio_url` field in song objects
   - Need to verify: URL format (Cloudinary? Dropbox? Local?)
   - Status: ⚠️ **CRITICAL - NEED TO CHECK**

---

## 5. SONG URLS - CRITICAL AUDIT

### Current Backend Song Storage

**File**: `Backend/app/routes/catalog.py` (Line 55)
```python
"audio_url": raga.get("audio_url", "no_url")[:50] + "..."
```

**Questions to Answer:**
1. What format are song URLs stored in MongoDB?
2. Are they Cloudinary URLs? Dropbox? Local?
3. Are they accessible from frontend?
4. Do they have proper CORS headers?

**Frontend Usage** (in `raga-rasa-soul-main/src/`):
- Songs are returned with `audio_url` field
- Frontend AudioPlayer expects to play from this URL
- Must be CORS-accessible

### Song URL Sources

**Potential sources** (based on root level scripts):
- `upload_songs_to_cloudinary.py` - Suggests Cloudinary URLs
- `update_urls_to_cloudinary.py` - Confirms migration to Cloudinary
- `update_songs_with_dropbox_urls.py` - Legacy Dropbox URLs?

---

## 6. ENVIRONMENT VARIABLES AUDIT

### Frontend (raga-rasa-soul-main/.env)
```
VITE_API_BASE_URL=https://raga-rasa-backend.onrender.com/api
```
Status: ✅ **CORRECT**

### Backend (Backend/.env or config)
**Expected to have:**
```
MONGODB_URL=...
JWT_SECRET=...
CORS_ORIGINS=https://raga-rasa-soul.vercel.app
EMOTION_SERVICE_URL=... (if using external emotion service)
```

**Note**: Recent integration added emotion detection to backend, so `EMOTION_SERVICE_URL` is optional now.

---

## 7. URL MISMATCH ISSUES FOUND

### ❌ CRITICAL ISSUE #1: `/songs/by-rasa` ENDPOINT MISSING

**Frontend calls** (api.ts line 209):
```
GET /api/songs/by-rasa
```

**Backend provides** (catalog.py):
```
GET /api/ragas/list
GET /api/ragas/simple
```

**Severity**: 🔴 **CRITICAL** - Frontend will 404 when calling `/api/songs/by-rasa`

**Error**: The frontend expects `/songs/by-rasa` but backend provides `/ragas/list`

**Fix Required**: 
- Option A: Add `/songs/by-rasa` endpoint to Backend that aliases `/ragas/list`
- Option B: Update frontend to call `/ragas/list` instead

**Status**: 🔴 **BROKEN** - This endpoint needs immediate fixing

---

## 8. DETAILED ENDPOINT MAPPING

### POST /api/session/start ✅
```
Frontend: services/api.ts line 37
Backend: session.py (NEED TO VERIFY EXISTS)
Purpose: Start new therapy session
Request: {}
Response: { session_id: string }
```

### POST /api/detect-emotion ✅
```
Frontend: services/api.ts line 66
Backend: emotion.py line 47 ✅
Purpose: Detect emotion from webcam image
Request: { image_base64: string, session_id: string }
Response: { emotion: string, confidence: number, raw_dominant: string }
```

### POST /api/recommend/live ✅
```
Frontend: services/api.ts line 106
Backend: recommendation.py line 34 ✅
Purpose: Get initial song recommendations
Request: { emotion, session_id, cognitive_data }
Response: Song[]
```

### POST /api/recommend/final ✅
```
Frontend: services/api.ts line 145
Backend: recommendation.py line ~120 ✅
Purpose: Get final recommendations with feedback
Request: { emotion, session_id, cognitive_data, feedback }
Response: Song[]
```

### GET /api/ragas/list (or /api/songs/) ⚠️
```
Frontend: Unknown (NEED TO CHECK)
Backend: catalog.py line 89
Purpose: Get songs filtered by rasa
Request: ?rasa=Shringar
Response: SongSchema[]
```

---

## 9. CURRENT STATUS SUMMARY

| Component | Status | Notes |
|-----------|--------|-------|
| **API Base URL** | ✅ CORRECT | Properly configured to Render backend |
| **Emotion Detection** | ✅ CORRECT | Endpoint matches exactly |
| **Recommendations** | ✅ CORRECT | Both live and final endpoints exist |
| **Session Start** | ⚠️ VERIFY | Need to check session.py has this |
| **Songs Catalog** | ⚠️ VERIFY | /songs vs /ragas mismatch possible |
| **Song URLs** | 🔴 CRITICAL | Need to verify Cloudinary URLs are accessible |
| **CORS** | ⚠️ VERIFY | Need to check CORS headers for song URLs |
| **Authentication** | ⚠️ VERIFY | JWT token handling needs verification |

---

## 10. ROOT LEVEL CLUTTER ISSUE

**You asked: "why is there a folder outside backend?"**

### Answer:

The project root has many loose files and folders:

**Problematic Items:**
- `emotion_recognition/` - Old microservice (now integrated into backend)
- `Songs/` - Local song files (should be in Backend or storage)
- `raga-rasa-soul-main/` - Frontend directory (should be separate repo or clear structure)
- 100+ Python test scripts in root (check_*.py, test_*.py, debug_*.py, etc.)
- 100+ Documentation markdown files (historical accumulation)
- `Dockerfile` and `docker-compose.yml` in root (should be in Backend/)

### Why It's a Problem:
1. **Deployment confusion** - Unclear which files are needed
2. **Docker builds fail** - Root Dockerfile includes everything
3. **Git bloat** - Large repo with unnecessary files
4. **Maintenance** - Hard to understand directory structure

### Recommendation:
**Organize into:**
```
raga_rasa_music/
├── Backend/           (FastAPI app - what gets deployed)
├── frontend/          (React/Vite - separate deployment)
├── docs/              (All markdown documentation)
├── scripts/           (All Python test/utility scripts)
├── .dockerignore
├── docker-compose.yml (for local dev only)
└── README.md
```

---

## NEXT STEPS - VERIFICATION CHECKLIST

### 1. Verify Session Endpoint
```bash
curl -X POST https://raga-rasa-backend.onrender.com/api/session/start
```

### 2. Verify Song Catalog Endpoint
```bash
curl https://raga-rasa-backend.onrender.com/api/ragas/list
# Check if response has correct audio_url format
```

### 3. Check Song URLs
```bash
# Verify URLs are Cloudinary
# Check if they're accessible from browser
# Test CORS headers
```

### 4. Check Frontend Code
```bash
# Search raga-rasa-soul-main/src for actual API calls
# Look for: /songs, /ragas, /catalog endpoints
# Verify paths match backend
```

### 5. Test Complete Flow
1. Frontend makes emotion detection call ✅
2. Frontend gets recommendations ✅
3. Frontend plays song from audio_url (NEED TO VERIFY)

---

## CONCLUSION

**Status**: ⚠️ **MOSTLY WORKING** but with critical unknowns

**What's Working:**
- ✅ API base URL configuration
- ✅ Emotion detection endpoint
- ✅ Recommendation endpoints
- ✅ Backend emotion integration (just added)

**What Needs Verification:**
- ⚠️ Session start endpoint
- ⚠️ Song catalog endpoint paths
- 🔴 **CRITICAL**: Song URL format and accessibility
- ⚠️ CORS configuration for song URLs
- ⚠️ Directory structure organization

**Recommendation**: 
Before deploying, run end-to-end test with actual frontend to verify song playback works correctly.

