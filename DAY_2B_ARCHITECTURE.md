# Day 2b Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     RAGA RASA SOUL - Architecture               │
│                        After Day 2b                              │
└─────────────────────────────────────────────────────────────────┘

DEPLOYMENT TARGETS (Render.com - Free Tier)
═══════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────┐
│                      RENDER.COM (Cloud)                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Service 1: emotion-recognition (Flask)                 │   │
│  │  ─────────────────────────────────────────────────────  │   │
│  │  Port: 5000                                             │   │
│  │  Build: pip install -r requirements.txt                │   │
│  │  Start: python api.py                                  │   │
│  │                                                         │   │
│  │  Endpoints:                                             │   │
│  │  • GET  /health                                         │   │
│  │  • POST /detect (emotion detection)                    │   │
│  │                                                         │   │
│  │  URL: https://emotion-recognition-xxxxx.onrender.com   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Service 2: raga-rasa-backend (FastAPI)                │   │
│  │  ─────────────────────────────────────────────────────  │   │
│  │  Port: 8000                                             │   │
│  │  Build: pip install -r Backend/requirements.txt        │   │
│  │  Start: cd Backend && python -m uvicorn main:app ...   │   │
│  │                                                         │   │
│  │  Endpoints:                                             │   │
│  │  • Auth (login/register)                                │   │
│  │  • Music (songs)                                        │   │
│  │  • Sessions (therapy sessions)                          │   │
│  │  • Admin (dashboard)                                    │   │
│  │  • Recommendations                                      │   │
│  │                                                         │   │
│  │  URL: https://raga-rasa-backend-xxxxx.onrender.com     │   │
│  │                                                         │   │
│  │  Environment Variables:                                 │   │
│  │  • MONGODB_URL (Atlas connection)                       │   │
│  │  • EMOTION_SERVICE_URL (emotion-recognition service)   │   │
│  │  • JWT_SECRET_KEY                                       │   │
│  │  • Database credentials                                 │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
         ↑                                          ↑
         │                                          │
    API calls                              Internal service calls
         │                                          │
         ↓                                          ↓
┌──────────────────────────────┐    ┌──────────────────────────────┐
│   FRONTEND                   │    │    EXTERNAL SERVICES         │
│  (Localhost:5173)            │    │    (MongoDB Atlas)           │
│  Day 3: Vercel               │    │                              │
├──────────────────────────────┤    │  mongodb+srv://Rishi123:... │
│  • React + TypeScript        │    │  Database: raga_rasa        │
│  • Login/Register            │    │  Collections:                │
│  • Music Player              │    │  • users                     │
│  • Sessions                  │    │  • songs                     │
│  • Admin Dashboard           │    │  • sessions                  │
│  • Recommendations           │    │  • recommendations          │
│                              │    │                              │
└──────────────────────────────┘    └──────────────────────────────┘


DATA FLOW
═════════

1. USER LOGIN FLOW:
   ┌─────────────┐
   │  Frontend   │
   └──────┬──────┘
          │ POST /auth/login
          ↓
   ┌──────────────────┐      MongoDB check
   │  Backend Server  │ ────────→ ✓ Verify password
   │   (FastAPI)      │
   └──────┬───────────┘
          │ Return JWT token
          ↓
   ┌─────────────┐
   │  Frontend   │ (Store in localStorage)
   └─────────────┘

2. EMOTION DETECTION FLOW:
   ┌─────────────┐
   │  Frontend   │
   └──────┬──────┘
          │ Send image (base64)
          ↓
   ┌──────────────────┐
   │  Backend Server  │
   └──────┬───────────┘
          │ POST /detect (with image)
          ↓
   ┌─────────────────────────────┐
   │ Emotion Service (Flask)     │
   │ HSEmotion Model             │
   └──────┬──────────────────────┘
          │ Return emotion + confidence
          ↓
   ┌──────────────────┐
   │  Backend Server  │
   └──────┬───────────┘
          │ Match Raga + Store in DB
          ↓
   ┌─────────────────┐
   │  Frontend       │
   │  Play music     │
   └─────────────────┘

3. MUSIC RECOMMENDATION FLOW:
   Frontend → Backend → MongoDB (fetch songs) → 
   Recommendation Engine → Return Ragas → Play Music


TECHNOLOGY STACK
═════════════════

Backend Services (Render.com)
├── FastAPI (Web framework)
├── MongoDB Atlas (Database)
├── PyTorch (Emotion detection)
├── HSEmotion (Emotion model)
├── Flask (Emotion service)
├── JWT (Authentication)
└── Bcrypt (Password hashing)

Frontend (Later - Vercel)
├── React 18
├── TypeScript
├── Tailwind CSS
├── Context API (State management)
└── Vite (Build tool)

External Services
├── MongoDB Atlas (Cloud Database)
├── Render.com (Backend hosting)
├── Vercel (Frontend hosting - Day 3)
└── Dropbox (File storage - Day 2d)


DEPLOYMENT SEQUENCE
═══════════════════

Today (Day 2b):
  1. Deploy emotion-recognition service
     ✓ Flask server running
     ✓ HSEmotion model loaded
     ✓ /health endpoint working
  
  2. Deploy backend service
     ✓ FastAPI server running
     ✓ MongoDB connected
     ✓ Calls emotion service
     ✓ JWT auth working
  
  3. Verify both services

Tomorrow (Day 2c):
  1. GitHub OAuth setup
  2. Add OAuth credentials to backend

Next (Day 2d):
  1. Dropbox setup
  2. Implement cloud storage

Day 3:
  1. Deploy frontend to Vercel
  2. Update API endpoints to Render URLs
  3. End-to-end testing


SERVICE DEPENDENCIES
════════════════════

emotion-recognition Service
├── Python 3.8+
├── PyTorch 2.2.2
├── OpenCV 4.9
├── HSEmotion 0.3.0
├── Flask 3.0.2
└── Flask-CORS 4.0.0

Backend Service
├── Python 3.8+
├── FastAPI 0.95+
├── Uvicorn 0.21+
├── PyMongo 4.0+
├── Requests 2.28+
├── python-jose (JWT)
├── passlib (Bcrypt)
├── MongoDB Atlas connection
└── Emotion service (HTTP calls)


EXPECTED RESPONSE TIMES
═══════════════════════

After Cold Start (first request):
└─ 10-30 seconds (free tier spin-up)

Subsequent Requests:
├─ Health check: ~100ms
├─ Login: ~200-500ms
├─ Emotion detection: ~1-3 seconds
├─ Get songs: ~300-700ms
└─ Get recommendations: ~200-400ms

Note: Times depend on cold starts and MongoDB latency


MONITORING & LOGS
═════════════════

In Render Dashboard:
1. Select service
2. Go to "Logs" tab
3. Search for:
   ✓ "Application startup complete" (good)
   ✗ "error" (bad - scroll to see details)
   ✗ "Connection refused" (database issue)

Common Log Patterns:
- "Building dependencies..." → Normal, wait
- "ERROR - Cannot import module" → Missing dependency
- "WARNING - Could not connect to mongo..." → Database issue


COST ESTIMATE
══════════════

Render.com Free Tier:
- emotion-recognition: Free
- raga-rasa-backend: Free
- Total: $0/month for basic deployment

Limitations:
- Services spin down after 15 min inactivity
- First request takes 10-30 seconds
- Acceptable for development/testing

MongoDB Atlas Free Tier:
- 512MB storage
- 3 nodes
- Total: $0/month

Total Monthly Cost: $0 (for development)


NEXT STEPS CHECKLIST
════════════════════

Phase 1 - Emotion Service:
  □ Go to Render dashboard
  □ Create new Web Service
  □ Configure name: emotion-recognition
  □ Root directory: emotion_recognition
  □ Build command: pip install -r requirements.txt
  □ Start command: python api.py
  □ Click Create Web Service
  □ Wait for "Active" status
  □ Copy public URL

Phase 2 - Backend Service:
  □ Go to Render dashboard
  □ Create new Web Service
  □ Configure name: raga-rasa-backend
  □ Root directory: .
  □ Build command: pip install -r Backend/requirements.txt
  □ Start command: cd Backend && python -m uvicorn main:app --host 0.0.0.0 --port 8000
  □ Add environment variables (all of them!)
  □ Replace emotion service URL in env vars
  □ Click Create Web Service
  □ Wait for "Active" status

Phase 3 - Verification:
  □ Test emotion service /health endpoint
  □ Test backend service /health endpoint
  □ Check both services in "Active" state
  □ Review logs for any errors
  □ Save public URLs

Ready? → Day 2c: GitHub OAuth Setup


═══════════════════════════════════════════════════════════════════

Architecture Document
Created: April 11, 2026
Status: Ready for Day 2b Deployment
