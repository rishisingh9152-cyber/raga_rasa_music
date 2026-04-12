"""
RagaRasa Music Therapy Backend
Main FastAPI application entry point
Restart: 2
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
    logger.info("=" * 60)
    logger.info("BACKEND STARTUP SEQUENCE")
    logger.info("=" * 60)
    
    try:
        logger.info("Step 1: Initializing song directories...")
        initialize_directories()
        logger.info("✓ Song directories initialized")
    except Exception as e:
        logger.warning(f"⚠ Song directory initialization failed: {e}")
    
    try:
        logger.info("Step 2: Initializing database...")
        await init_db()
        logger.info("✓ Database initialized")
    except Exception as e:
        logger.error(f"✗ Database initialization failed: {e}")
        logger.warning("⚠ Continuing without database - some features may not work")
    
    try:
        logger.info("Step 3: Initializing Redis cache...")
        await init_redis()
        logger.info("✓ Redis cache initialized")
    except Exception as e:
        logger.warning(f"⚠ Redis initialization failed (optional): {e}")
    
    logger.info("=" * 60)
    logger.info("✓ BACKEND STARTUP COMPLETE")
    logger.info("=" * 60)
    
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
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
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


@app.get("/db-test")
async def db_test():
    """Test database connection"""
    from app.database import get_db
    try:
        db = get_db()
        if db is None:
            logger.error("[DBTest] Database is None - not initialized")
            return {"status": "error", "message": "Database not initialized", "initialized": False}
        
        logger.info("[DBTest] Testing database count_documents...")
        count = await db.songs.count_documents({})
        logger.info(f"[DBTest] Success - found {count} songs")
        return {"status": "success", "total_songs": count, "initialized": True}
    except Exception as e:
        logger.error(f"[DBTest] Database test failed: {e}", exc_info=True)
        return {"status": "error", "message": str(e), "initialized": False}


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
        "openapi": "/openapi.json",
        "health": "/health",
        "version": "1.0.0"
    }


@app.options("/{full_path:path}")
async def preflight_handler(full_path: str):
    """Handle CORS preflight requests"""
    return {"message": "CORS preflight OK"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False
    )
