# RagaRasa Music Therapy Backend

Production-ready FastAPI backend for AI-based music therapy platform using Indian classical music (Ragas).

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Running the Backend](#running-the-backend)
- [API Endpoints](#api-endpoints)
- [Database Schema](#database-schema)
- [Configuration](#configuration)
- [Development](#development)
- [Deployment](#deployment)

---

## ✨ Features

- **Emotion Detection**: Real-time facial emotion detection from webcam frames
- **Hybrid Recommendation Engine**: Content-based + Collaborative filtering
- **Session Management**: Track user sessions with cognitive metrics
- **Music Catalog**: Browse and manage Indian classical music ragas
- **User Ratings**: Collect feedback and ratings for personalization
- **Caching Layer**: Redis integration for performance optimization
- **Async Processing**: Celery for background tasks
- **Type Safety**: Full TypeScript-style validation with Pydantic
- **CORS Enabled**: Ready for frontend integration

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│           FastAPI Backend (Port 8000)              │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌─ Emotion Detection Service                      │
│  │  ├─ FER / DeepFace ML Models                    │
│  │  └─ Base64 Image Processing                    │
│  │                                                 │
│  ├─ Recommendation Engine                         │
│  │  ├─ Content-Based Filtering                    │
│  │  ├─ Collaborative Filtering                    │
│  │  └─ Hybrid Scoring System                      │
│  │                                                 │
│  ├─ API Routes                                    │
│  │  ├─ Session Management                        │
│  │  ├─ Emotion Detection                         │
│  │  ├─ Recommendations                           │
│  │  ├─ User Ratings                              │
│  │  ├─ Session History                           │
│  │  └─ Raga Catalog                              │
│  │                                                 │
│  └─ Cache & Database Layer                        │
│     ├─ MongoDB (Primary Storage)                 │
│     └─ Redis (Caching)                           │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 📦 Prerequisites

- **Python**: 3.11+
- **MongoDB**: 7.0+
- **Redis**: 7.0+
- **Docker**: (optional, for containerized setup)

### System Requirements

- 2+ CPU cores
- 4GB+ RAM
- 1GB free disk space

---

## 🚀 Installation

### Option 1: Local Setup (Windows/Mac/Linux)

#### 1. Clone and Navigate

```bash
cd "C:\Major Project\backend"
```

#### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 4. Start MongoDB and Redis

**Option A: Using Docker**
```bash
docker run -d -p 27017:27017 --name raga-mongo mongo:7.0
docker run -d -p 6379:6379 --name raga-redis redis:7-alpine
```

**Option B: Local Installation**

MongoDB:
- **Windows**: Download from https://www.mongodb.com/try/download/community
- **Mac**: `brew install mongodb-community`
- **Linux**: `sudo apt-get install mongodb`

Start MongoDB:
```bash
# Windows (from installed directory)
mongod

# Mac/Linux
mongod
```

Redis:
- **Windows**: Download from https://github.com/microsoftarchive/redis/releases
- **Mac**: `brew install redis`
- **Linux**: `sudo apt-get install redis-server`

Start Redis:
```bash
# Windows
redis-server

# Mac/Linux
redis-server
```

#### 5. Initialize Database

```bash
# Create required indexes and collections
python seed_data.py
```

#### 6. Start Backend

```bash
python main.py
```

Backend will be available at: **http://localhost:8000**

API Docs available at: **http://localhost:8000/docs**

---

### Option 2: Docker Compose (Recommended)

#### 1. Build and Start

```bash
cd "C:\Major Project\backend"
docker-compose up --build
```

This will start:
- FastAPI Backend (port 8000)
- MongoDB (port 27017)
- Redis (port 6379)

#### 2. Verify Services

```bash
# Check backend
curl http://localhost:8000/health

# Check MongoDB
mongosh --eval "db.adminCommand('ping')"

# Check Redis
redis-cli ping
```

#### 3. Stop Services

```bash
docker-compose down
```

---

## 🔌 API Endpoints

### 1. Session Management

**POST /session/start**
- Initialize new therapy session
- Request: `{}`
- Response: `{"session_id": "uuid"}`

Example:
```bash
curl -X POST http://localhost:8000/session/start
```

### 2. Emotion Detection

**POST /detect-emotion**
- Detect emotion from webcam image
- Request:
```json
{
  "image_base64": "data:image/jpeg;base64,...",
  "session_id": "uuid"
}
```
- Response: `{"emotion": "Happy"}`

### 3. Live Recommendations

**POST /recommend/live**
- Get song recommendations for active session
- Request:
```json
{
  "emotion": "Happy",
  "session_id": "uuid",
  "cognitive_data": {
    "memory_score": 4,
    "reaction_time": 285,
    "accuracy_score": 66.67
  }
}
```
- Response:
```json
[
  {
    "song_id": "raga_001",
    "title": "Raga Yaman",
    "audio_url": "http://localhost:8000/audio/raga-yaman.mp3",
    "rasa": "Shringar",
    "confidence": 0.92,
    "duration": "8:45"
  }
]
```

### 4. Final Recommendations

**POST /recommend/final**
- Get recommendations after post-test
- Same as /recommend/live but includes feedback

### 5. Rate Song

**POST /rate**
- Store user rating for a song
- Request:
```json
{
  "user_id": "uuid",
  "song_id": "raga_001",
  "rating": 5,
  "session_id": "uuid",
  "feedback": {
    "mood_after": "Felt relaxed",
    "session_rating": 4,
    "comment": "Great experience"
  }
}
```
- Response: HTTP 200

### 6. Session History

**GET /sessions/history?user_id=uuid**
- Get user's session history
- Response:
```json
[
  {
    "session_id": "uuid",
    "date": "Mar 15, 2025",
    "emotion": "Happy",
    "top_raga": "Raga Yaman",
    "rating": 5,
    "mood_before": 4,
    "mood_after": 8
  }
]
```

### 7. Raga Catalog

**GET /ragas/list?rasa=Shringar**
- Get available ragas (optional filter by rasa)
- Response:
```json
[
  {
    "song_id": "raga_001",
    "title": "Raga Yaman",
    "rasa": "Shringar",
    "audio_url": "http://localhost:8000/audio/raga-yaman.mp3",
    "duration": "8:45"
  }
]
```

**GET /ragas/{raga_id}**
- Get specific raga details

---

## 🗄️ Database Schema

### MongoDB Collections

#### 1. users
```json
{
  "_id": "uuid",
  "created_at": "2025-03-15T10:00:00Z"
}
```

#### 2. sessions
```json
{
  "_id": "session_id",
  "user_id": "user_uuid",
  "emotion": "Happy",
  "cognitive_data": {
    "memory_score": 4,
    "reaction_time": 285,
    "accuracy_score": 66.67
  },
  "feedback": {
    "mood_after": "Felt great",
    "session_rating": 5,
    "comment": "..."
  },
  "recommended_songs": [...],
  "created_at": "2025-03-15T10:00:00Z"
}
```

#### 3. songs
```json
{
  "_id": "raga_001",
  "title": "Raga Yaman",
  "rasa": "Shringar",
  "audio_url": "http://...",
  "duration": "8:45",
  "audio_features": {
    "energy": 0.6,
    "valence": 0.7,
    "tempo": 120
  },
  "embedding": [0.1, 0.2, ...],
  "created_at": "2025-03-15T10:00:00Z"
}
```

#### 4. ratings
```json
{
  "user_id": "user_uuid",
  "song_id": "raga_001",
  "rating": 5,
  "session_id": "session_id",
  "feedback": {...},
  "created_at": "2025-03-15T10:00:00Z"
}
```

---

## ⚙️ Configuration

Edit `.env` file to customize:

```env
# API Settings
API_HOST=0.0.0.0
API_PORT=8000

# Database
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=raga_rasa

# Redis Cache
REDIS_URL=redis://localhost:6379
REDIS_CACHE_EXPIRY=3600  # 1 hour

# ML Models
EMOTION_MODEL=fer  # or 'deepface'
EMOTION_CONFIDENCE_THRESHOLD=0.3

# Recommendations
MAX_RECOMMENDATIONS=5
EMBEDDING_DIMENSION=128

# Environment
DEBUG=False
```

---

## 🔍 Testing Endpoints

### Using curl

```bash
# 1. Start session
SESSION_ID=$(curl -s -X POST http://localhost:8000/session/start | jq -r '.session_id')

# 2. Detect emotion (need actual image)
# Convert image to base64 first
curl -X POST http://localhost:8000/detect-emotion \
  -H "Content-Type: application/json" \
  -d "{\"image_base64\": \"...\", \"session_id\": \"$SESSION_ID\"}"

# 3. Get recommendations
curl -X POST http://localhost:8000/recommend/live \
  -H "Content-Type: application/json" \
  -d "{
    \"emotion\": \"Happy\",
    \"session_id\": \"$SESSION_ID\",
    \"cognitive_data\": {
      \"memory_score\": 4,
      \"reaction_time\": 285,
      \"accuracy_score\": 66.67
    }
  }"

# 4. Get ragas
curl http://localhost:8000/ragas/list
```

### Using Swagger UI

Navigate to: **http://localhost:8000/docs**

All endpoints are interactive with request/response examples.

---

## 📊 Monitoring

### Health Check

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "service": "RagaRasa Music Therapy Backend",
  "version": "1.0.0"
}
```

### Logs

Logs are printed to console. For production, configure file logging in `main.py`.

---

## 🔧 Development

### Add New Endpoint

1. Create route file in `app/routes/`
2. Define FastAPI router
3. Include in `main.py`

Example:
```python
from fastapi import APIRouter

router = APIRouter()

@router.get("/custom")
async def custom_endpoint():
    return {"message": "Hello"}
```

### Add New Service

1. Create service file in `app/services/`
2. Implement logic
3. Import in routes

### Running Tests

```bash
pytest tests/ -v
```

---

## 🚢 Deployment

### Production Checklist

- [ ] Set `DEBUG=False` in `.env`
- [ ] Use production MongoDB (MongoDB Atlas)
- [ ] Use production Redis (Redis Cloud)
- [ ] Configure CORS properly (set specific origins)
- [ ] Set up SSL/TLS certificates
- [ ] Enable authentication
- [ ] Configure logging to file/service
- [ ] Set up monitoring and alerts
- [ ] Use production-grade ASGI server (Gunicorn)

### Production Start Command

```bash
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --env-file .env.prod
```

### Docker Production Build

```bash
docker build -t raga-rasa-backend:1.0 .
docker run -p 8000:8000 \
  -e MONGODB_URL="..." \
  -e REDIS_URL="..." \
  raga-rasa-backend:1.0
```

---

## 🔗 Frontend Integration

The backend is fully compatible with the RagaRasa React frontend.

**Frontend expects backend at**: `http://localhost:8000`

Configure frontend's `.env`:
```
VITE_API_BASE_URL=http://localhost:8000
```

---

## 📝 Logs & Debugging

### Enable Debug Logging

Set in `.env`:
```
DEBUG=True
```

### View Logs

```bash
# Follow logs in real-time
docker-compose logs -f backend

# View specific service
docker logs raga-rasa-backend
```

---

## 🐛 Troubleshooting

### MongoDB Connection Failed
- Ensure MongoDB is running: `mongosh`
- Check MONGODB_URL in `.env`
- Verify port 27017 is available

### Redis Connection Failed
- Ensure Redis is running: `redis-cli ping`
- Check REDIS_URL in `.env`
- Verify port 6379 is available

### Emotion Detection Not Working
- Ensure camera access is granted on frontend
- Check FER/DeepFace models are installed
- Verify image is valid base64 format

### Slow Recommendations
- Check Redis cache is working
- Verify database has indexes
- Monitor CPU usage (ML inference is CPU-intensive)

---

## 📚 Additional Resources

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [MongoDB Docs](https://docs.mongodb.com/)
- [Redis Docs](https://redis.io/docs/)
- [FER Library](https://github.com/justinshenk/fer)
- [DeepFace](https://github.com/serengp/deepface)

---

## 📄 License

MIT License

---

## 🤝 Support

For issues or questions:
1. Check troubleshooting section
2. Review API logs
3. Check MongoDB/Redis connectivity
4. Verify frontend integration

---

**Last Updated**: March 2025
**Version**: 1.0.0
