"""Database models for RagaRasa"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr


# ==================== Authentication Schemas ====================

class RegisterSchema(BaseModel):
    """Schema for user registration"""
    email: EmailStr
    password: str = Field(..., min_length=8, description="Minimum 8 characters")


class LoginSchema(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class TokenSchema(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"
    user: Optional[Dict[str, Any]] = None


class TokenPayloadSchema(BaseModel):
    """JWT token payload"""
    user_id: str
    email: str
    role: str  # "user" or "admin"
    exp: float


# ==================== Song Schemas ====================

class SongAudioFeaturesSchema(BaseModel):
    """Audio features for a song"""
    energy: float = Field(default=0.5, ge=0, le=1)
    valence: float = Field(default=0.5, ge=0, le=1)
    tempo: int = Field(default=100, ge=0)
    bitrate: Optional[str] = None


class SongStorageMetadataSchema(BaseModel):
    """Cloud storage metadata for songs"""
    storage_type: str = Field(default="local", description="local, google_drive, aws_s3, or azure_blob")
    cloud_bucket: Optional[str] = None
    cloud_object_key: Optional[str] = None
    cloud_url: Optional[str] = None
    signed_url_expiry: Optional[datetime] = None
    file_hash: Optional[str] = None
    file_size: int = 0


class SongCreateSchema(BaseModel):
    """Schema for creating/updating a song"""
    title: str
    artist: Optional[str] = None
    rasa: str = Field(..., description="Shringar, Shaant, Veer, or Shok")
    audio_url: str
    file_path: str
    duration: str
    file_size: int
    file_size_mb: float
    audio_features: Optional[SongAudioFeaturesSchema] = None
    storage_metadata: Optional[SongStorageMetadataSchema] = None


class SongSchema(BaseModel):
    """Song object for recommendations"""
    song_id: str
    title: str
    audio_url: str
    rasa: str = Field(..., description="Emotional classification (Shringar, Shaant, Veer, Shok)")
    confidence: float = Field(default=1.0, ge=0, le=1, description="Confidence score 0-1")
    duration: Optional[str] = None
    rasa_confidence: Optional[float] = Field(default=1.0, ge=0, le=1, description="Rasa classification confidence")
    storage_metadata: Optional[SongStorageMetadataSchema] = None


class RagaSchema(BaseModel):
    """Raga catalog entry for music player"""
    song_id: str
    title: str
    rasa: str
    audio_url: str
    duration: str
    storage_metadata: Optional[SongStorageMetadataSchema] = None


# ==================== User Schemas ====================

class UserPreferencesSchema(BaseModel):
    """User preferences"""
    favorite_ragas: List[str] = Field(default_factory=list)
    preferred_time_of_day: Optional[str] = None
    listening_frequency: Optional[str] = None


class UserSchema(BaseModel):
    """User profile"""
    user_id: str
    email: str
    role: str = Field(default="user", description="user or admin")
    provider: str = Field(default="email", description="email, google, or github")
    created_at: datetime
    preferences: Optional[UserPreferencesSchema] = None
    total_sessions: int = Field(default=0)


# ==================== Psychometric Test Schemas ====================

class PsychometricTestDataSchema(BaseModel):
    """Psychometric test results"""
    memory_score: int = Field(..., ge=0, le=6, description="Memory test score 0-6")
    reaction_time: int = Field(..., ge=0, description="Average reaction time in ms")
    accuracy_score: float = Field(..., ge=0, le=100, description="Accuracy percentage 0-100")


class PsychometricTestSchema(BaseModel):
    """Complete psychometric test document"""
    test_id: str
    session_id: str
    user_id: Optional[str] = None
    test_type: str = Field(..., description="pre_test or post_test")
    timestamp: datetime
    data: PsychometricTestDataSchema


# ==================== Rating Schemas ====================

class RatingCreateSchema(BaseModel):
    """Schema for creating a rating"""
    song_id: str
    rating: int = Field(..., ge=1, le=5, description="Rating 1-5 stars")
    feedback_text: Optional[str] = None


class RatingSchema(BaseModel):
    """Song rating by user in a session"""
    rating_id: str
    session_id: str
    user_id: Optional[str] = None
    song_id: str
    rating: int = Field(..., ge=1, le=5)
    feedback_text: Optional[str] = None
    timestamp: datetime


# ==================== Emotion Detection Schemas ====================

class EmotionDetectSchema(BaseModel):
    """Emotion detection result"""
    emotion: str
    confidence: float = Field(..., ge=0, le=1)
    raw_dominant: str = Field(..., description="Raw emotion label from model")


# ==================== Feedback Schemas ====================

class FeedbackSchema(BaseModel):
    """User feedback on session or song"""
    feedback_text: Optional[str] = None
    rating: Optional[int] = Field(None, ge=1, le=5, description="Optional 1-5 rating")
    # Frontend session feedback shape
    mood_after: Optional[str] = None
    session_rating: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = None
    timestamp: Optional[datetime] = None


# ==================== Session History Schemas ====================

class SessionHistorySchema(BaseModel):
    """Historical session record"""
    session_id: str
    user_id: Optional[str] = None
    created_at: datetime
    emotion: Optional[str] = None
    rasa: Optional[str] = None
    status: str = Field(default="active")


# ==================== Cognitive Data Schemas ====================

class CognitiveDataSchema(BaseModel):
    """Cognitive assessment data (pre/post session)"""
    # Frontend live/final recommendation shape
    memory_score: Optional[float] = None
    reaction_time: Optional[float] = None
    accuracy_score: Optional[float] = None
    # Legacy/extended schema
    pre_test_id: Optional[str] = None
    post_test_id: Optional[str] = None
    pre_test: Optional[PsychometricTestDataSchema] = None
    post_test: Optional[PsychometricTestDataSchema] = None
    improvement: Optional[Dict[str, float]] = None


# ==================== Session Schemas ====================

class SessionCreateSchema(BaseModel):
    """Schema for session creation response"""
    session_id: str
    created_at: datetime
    message: str = "Session initialized"


class SessionSchema(BaseModel):
    """Complete session document"""
    session_id: str
    user_id: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    emotion: Optional[str] = None
    rasa: Optional[str] = None
    ratings: List[str] = Field(default_factory=list)
    images: List[str] = Field(default_factory=list)
    psychometric_tests: List[str] = Field(default_factory=list)
    cognitive_data: Optional[CognitiveDataSchema] = None
    feedback: Optional[str] = None
    status: str = Field(default="active", description="active, completed, cancelled")


# ==================== Image/Session Capture Schemas ====================

class SessionImageSchema(BaseModel):
    """Image captured during session"""
    image_id: str
    session_id: str
    timestamp: datetime
    image_path: str
    emotion_detected: Optional[str] = None
    confidence: float = Field(default=0.0, ge=0, le=1)


# ==================== Storage Configuration Schemas ====================

class StorageConfigSchema(BaseModel):
    """Storage provider configuration"""
    provider: str = Field(..., description="local, google_drive, aws_s3, or azure_blob")
    base_path: Optional[str] = None
    google_drive_folder_id: Optional[str] = None
    google_drive_api_key: Optional[str] = None
    aws_s3_bucket: Optional[str] = None
    aws_s3_region: Optional[str] = None
    azure_blob_container: Optional[str] = None
    azure_storage_account: Optional[str] = None


class StorageMigrationRequestSchema(BaseModel):
    """Request to migrate songs to a new storage provider"""
    target_provider: str = Field(..., description="Target storage provider")
    target_config: StorageConfigSchema


class StorageMigrationStatusSchema(BaseModel):
    """Status of storage migration operation"""
    migration_id: str
    status: str = Field(..., description="pending, in_progress, completed, failed")
    source_provider: str
    target_provider: str
    songs_total: int = 0
    songs_migrated: int = 0
    songs_failed: int = 0
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

