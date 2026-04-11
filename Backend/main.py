"""
RagaRasa Music Therapy Backend
Main FastAPI application entry point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="RagaRasa Music Therapy Backend",
    description="AI-powered emotion-based music therapy using Indian classical music",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.get("/test")
async def test():
    """Test endpoint"""
    return {"status": "ok", "message": "Backend is running"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
