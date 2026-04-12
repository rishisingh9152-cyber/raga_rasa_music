"""Configuration settings for RagaRasa backend"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # Database - Production MongoDB Atlas (use environment variable in production)
    MONGODB_URL: str = os.getenv(
        "MONGODB_URL",
        "mongodb://localhost:27017"  # Local dev default
    )
    DATABASE_NAME: str = "raga_rasa"
    
    # Redis - Production Redis (optional, can be empty)
    REDIS_URL: str = ""
    REDIS_CACHE_EXPIRY: int = 3600  # 1 hour
    
    # External Emotion Recognition Service - Configure via environment variable
    USE_EXTERNAL_EMOTION_SERVICE: bool = True
    EMOTION_SERVICE_URL: str = os.getenv(
        "EMOTION_SERVICE_URL",
        "http://localhost:5000"  # Local dev default
    )
    EMOTION_SERVICE_ENDPOINT: str = "/detect"
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
    
    # Celery - Optional for production
    CELERY_BROKER: str = ""
    CELERY_BACKEND: str = ""
    
    # Audio
    AUDIO_UPLOAD_DIR: str = "./audio"
    MAX_AUDIO_SIZE_MB: int = 50
    
    # Security & JWT (use environment variables in production!)
    DEBUG: bool = False
    JWT_SECRET_KEY: str = os.getenv(
        "JWT_SECRET_KEY",
        "change-me-in-production-use-env-variable"  # MUST be set in production
    )
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    # CORS Configuration - Production frontend URLs + Vercel preview deployments
    ALLOWED_ORIGINS_STR: str = "https://raga-rasa-music-52.vercel.app,http://localhost:5173,http://localhost:8080,http://127.0.0.1:5173,http://127.0.0.1:8080"
    ALLOWED_ORIGINS_REGEX: str = r"https://.*\.vercel\.app"
    ALLOWED_METHODS: list = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
    ALLOWED_HEADERS: list = ["*"]
    
    @property
    def ALLOWED_ORIGINS(self) -> list:
        """Parse ALLOWED_ORIGINS from comma-separated string"""
        origins = []
        if self.ALLOWED_ORIGINS_STR:
            origins = [origin.strip() for origin in self.ALLOWED_ORIGINS_STR.split(",")]
        else:
            origins = ["http://localhost:5173"]
        
        return list(set(origins))  # Remove duplicates
    
    # Storage Configuration - Use Cloudinary for production
    STORAGE_PROVIDER: str = "cloudinary"
    STORAGE_BASE_PATH: str = "./Songs/"
    
    # Cloudinary Configuration - Use environment variables (optional storage)
    CLOUDINARY_CLOUD_NAME: Optional[str] = os.getenv("CLOUDINARY_CLOUD_NAME")
    CLOUDINARY_API_KEY: Optional[str] = os.getenv("CLOUDINARY_API_KEY")
    CLOUDINARY_API_SECRET: Optional[str] = os.getenv("CLOUDINARY_API_SECRET")
    
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
