# 🐳 Docker Deployment - RagaRasa Backend

## Quick Start - Local Testing

### Prerequisites
- Docker installed
- Docker Compose installed

### Run Locally

```bash
# From project root
docker-compose up

# In another terminal, test
curl http://localhost:8000/health
```

This starts:
- ✅ Backend (FastAPI) on port 8000
- ✅ MongoDB on port 27017
- ✅ Redis on port 6379

---

## For Render Deployment

See **RENDER_DOCKER_DEPLOY.md** for complete step-by-step instructions.

### Key Points
- ✅ Root Directory in Render must be: `Backend`
- ✅ Environment must be: `Docker`
- ✅ Python version: 3.10.13 (automatic via Dockerfile)
- ✅ All dependencies: Included in requirements.txt

---

## Docker Files

- **Backend/Dockerfile** - Main application container
- **Backend/.dockerignore** - Excludes unnecessary files
- **docker-compose.yml** - Local development setup

---

## Environment Variables

Required for production:
```
MONGODB_URL=your_mongodb_connection_string
EMOTION_SERVICE_URL=https://raga-rasa-music.onrender.com
JWT_SECRET=your_jwt_secret
```

Optional:
```
REDIS_URL=your_redis_url
DATABASE_NAME=raga_rasa
USE_EXTERNAL_EMOTION_SERVICE=true
EMOTION_SERVICE_ENDPOINT=/detect
```

---

## Troubleshooting

### Docker build fails locally
```bash
# Clear cache and rebuild
docker-compose down -v
docker-compose build --no-cache
docker-compose up
```

### Port already in use
Change ports in docker-compose.yml:
```yaml
ports:
  - "8001:8000"  # Use 8001 instead
```

### Memory issues
Docker might need more memory. Check Docker Desktop settings.

---

**For Render deployment guide: See RENDER_DOCKER_DEPLOY.md**
