"""
RagaRasa Music Therapy Backend
Main FastAPI application entry point
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create app
app = FastAPI(
    title="RagaRasa Music Therapy Backend",
    description="AI-powered emotion-based music therapy using Indian classical music",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Basic health check endpoint
@app.get("/health")
async def health():
    return {"status": "ok", "service": "RagaRasa Backend"}

@app.get("/")
async def root():
    return {"message": "RagaRasa Backend is running"}

@app.get("/test")
async def test():
    return {"status": "ok", "test": "passed"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
