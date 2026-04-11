"""
RagaRasa Music Therapy Backend
Main FastAPI application entry point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.database import init_db, close_db
from app.routes import session, emotion, recommendation, rating, history, catalog, upload, psychometric, images, auth, admin
from app.services.cache import init_redis
from app.services.song_upload import initialize_directories
from app.services.rate_limiting import limiter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown"""
    # Startup
    logger.info("Initializing song directories...")
    initialize_directories()
    
    logger.info("Initializing database...")
    try:
        await init_db()
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        logger.warning("Continuing without database - some features may not work")
    
    logger.info("Initializing Redis cache...")
    await init_redis()
    
    logger.info("Backend startup complete")
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    try:
        await close_db()
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


app = FastAPI(
    title="RagaRasa Music Therapy Backend",
    description="AI-powered emotion-based music therapy using Indian classical music",
    version="1.0.0",
    lifespan=lifespan
)

# Add rate limiter state to app
app.state.limiter = limiter

# CORS Configuration - Allow frontend requests
origins = settings.ALLOWED_ORIGINS
if settings.DEBUG:
    # In development, allow more origins
    origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=settings.ALLOWED_METHODS,
    allow_headers=settings.ALLOWED_HEADERS,
)


# Route Includes
app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(session.router, prefix="/api", tags=["session"])
app.include_router(emotion.router, prefix="/api", tags=["emotion"])
app.include_router(recommendation.router, prefix="/api", tags=["recommendation"])
app.include_router(rating.router, prefix="/api", tags=["rating"])
app.include_router(history.router, prefix="/api", tags=["history"])
app.include_router(catalog.router, prefix="/api", tags=["catalog"])
app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(psychometric.router, prefix="/api", tags=["psychometric"])
app.include_router(images.router, prefix="/api", tags=["images"])
app.include_router(admin.router, prefix="/api", tags=["admin"])


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "RagaRasa Music Therapy Backend",
        "version": "1.0.0"
    }


@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "Welcome to RagaRasa Music Therapy Backend",
        "docs": "/docs",
        "openapi": "/openapi.json"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
