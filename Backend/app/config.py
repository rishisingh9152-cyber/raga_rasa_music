"""Configuration settings for RagaRasa backend"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # Database
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "raga_rasa"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_CACHE_EXPIRY: int = 3600  # 1 hour
    
    # External Emotion Recognition Service
    USE_EXTERNAL_EMOTION_SERVICE: bool = True
    EMOTION_SERVICE_URL: str = "http://localhost:5000"  # Change to your service URL/port
    EMOTION_SERVICE_ENDPOINT: str = "/detect"  # Change to your service endpoint (Flask uses /detect)
    EMOTION_CONFIDENCE_THRESHOLD: float = 0.3
    
    # Rasa Classification Model
    RASA_MODEL_PATH: str = "./models/rasa_classification/"
    USE_RASA_MODEL: bool = True
    ALLOWED_RASAS: list = ["Shringar", "Veer", "Shaant", "Shok"]  # 4 core rasas for music therapy
    
    # Emotion Detection (Legacy - for fallback)
    EMOTION_MODEL: str = "fer"  # 'fer' or 'deepface'
    
    # Recommendation
    MAX_RECOMMENDATIONS: int = 5
    EMBEDDING_DIMENSION: int = 128
    
    # Celery
    CELERY_BROKER: str = "redis://localhost:6379"
    CELERY_BACKEND: str = "redis://localhost:6379"
    
    # Audio
    AUDIO_UPLOAD_DIR: str = "./audio"
    MAX_AUDIO_SIZE_MB: int = 50
    
    # Security & JWT
    DEBUG: bool = False
    JWT_SECRET_KEY: str = "your-secret-key-change-this-in-production"  # Override in .env
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    # CORS Configuration
    ALLOWED_ORIGINS: list = [
        "http://localhost:5173",
        "http://localhost:8080",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8080",
        "https://raga-rasa-music-52.vercel.app",
        "https://raga-rasa-music-52.vercel.app/"
    ]
    ALLOWED_METHODS: list = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    ALLOWED_HEADERS: list = ["Content-Type", "Authorization"]
    
    # Storage Configuration
    STORAGE_PROVIDER: str = "local"  # "local", "cloudinary", "google_drive", "aws_s3", "azure_blob"
    STORAGE_BASE_PATH: str = "./Songs/"
    
    # Cloudinary Configuration
    CLOUDINARY_CLOUD_NAME: Optional[str] = None
    CLOUDINARY_API_KEY: Optional[str] = None
    CLOUDINARY_API_SECRET: Optional[str] = None
    
    # Google Drive Configuration
    GOOGLE_DRIVE_FOLDER_ID: Optional[str] = None
    GOOGLE_DRIVE_API_KEY: Optional[str] = None
    GOOGLE_DRIVE_SERVICE_ACCOUNT_JSON: Optional[str] = None
    
    # AWS S3 Configuration
    AWS_S3_BUCKET: Optional[str] = None
    AWS_S3_REGION: Optional[str] = None
    
    # Azure Blob Configuration
    AZURE_BLOB_CONTAINER: Optional[str] = None
    AZURE_STORAGE_ACCOUNT: Optional[str] = None
    
    # GitHub OAuth
    GITHUB_CLIENT_ID: Optional[str] = None
    GITHUB_CLIENT_SECRET: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
