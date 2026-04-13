"""
Emotion detection endpoints integrated in backend (no external service).

MAIN FLOW (Used by Frontend):
- Frontend calls: POST /api/detect (with session_id + base64 image)
- This endpoint detects emotion and updates session database
- Returns: { emotion: "Happy", confidence: 0.92, ... }

ALTERNATIVE CLEAN SERVICE (NEW):
- POST /api/emotion/detect-clean - Clean HSEmotion service (8 emotions + bravery)
- POST /api/emotion/detect-file-clean - File upload version
- GET /api/emotion/health-clean - Health check
- GET /api/emotion/info-clean - Service information

The frontend is connected to the main /api/detect endpoint which works with the
existing emotion detection pipeline (emotion_recognition_local, emotion module, etc).

The new clean emotion service (/api/emotion/detect-clean) is available as an
alternative with detailed emotion breakdown but frontend is not using it yet.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
import logging
import traceback
import asyncio

from app.database import get_db
from app.services.rasa_model import get_rasa_model
from app.models import EmotionDetectSchema
from app.services.cache import cache_get, cache_set
from app.config import settings
from app.services.emotion_recognition_local import get_local_emotion_detector
from app.services.clean_emotion_service import get_clean_emotion_service

logger = logging.getLogger(__name__)

router = APIRouter()

# Lazy-load detector only when first request arrives.
_emotion_detector = None


class EmotionDetectRequest(BaseModel):
    """Emotion detection request from frontend session camera capture."""

    image_base64: str
    session_id: str


def _fallback_response() -> EmotionDetectSchema:
    return EmotionDetectSchema(emotion="Neutral", confidence=0.5, raw_dominant="neutral")


def get_emotion_detector_lazy():
    """Initialize integrated detector from backend service module."""

    if not getattr(settings, "USE_INTERNAL_EMOTION_MODEL", False):
        logger.info("[Emotion] Internal model disabled in config, using fallback mode")
        return None

    global _emotion_detector
    if _emotion_detector is None:
        try:
            from app.services.emotion import get_emotion_detector

            _emotion_detector = get_emotion_detector()
        except Exception as e:
            logger.error(f"[Emotion] Internal detector init failed: {e}")
            return None
    return _emotion_detector


async def detect_with_local_emotion_module(image_base64: str):
    """Use in-process local emotion_recognition module (no separate server)."""
    detector = get_local_emotion_detector()
    emotion_raw, confidence, _ = await asyncio.wait_for(
        asyncio.to_thread(detector.detect_from_base64, image_base64),
        timeout=8.0,
    )
    emotion_map = {
        "happy": "Happy",
        "neutral": "Neutral",
        "sad": "Sad",
        "angry": "Angry",
        "fear": "Fearful",
        "fearful": "Fearful",
        "surprise": "Surprised",
        "surprised": "Surprised",
        "disgust": "Disgusted",
        "disgusted": "Disgusted",
    }
    emotion = emotion_map.get(str(emotion_raw).lower(), "Neutral")
    return emotion, float(confidence)


@router.get("/emotion-service/health")
async def emotion_service_health():
    """Health check for integrated backend detector."""

    try:
        detector = get_emotion_detector_lazy()
        if detector is None:
            return {
                "status": "degraded",
                "service": "internal_emotion_recognition",
                "mode": "fallback_neutral",
                "external_service_used": False,
            }

        is_healthy = bool(getattr(detector, "recognizer", None) or getattr(detector, "detector", None))
        return {
            "status": "healthy" if is_healthy else "unavailable",
            "service": "internal_emotion_recognition",
            "model_type": getattr(detector, "model_type", "unknown"),
            "fallback_available": True,
            "external_service_used": False,
        }
    except Exception as e:
        logger.error(f"[Emotion] Health check failed: {e}")
        return {
            "status": "error",
            "service": "internal_emotion_recognition",
            "external_service_used": False,
            "error": str(e),
        }


@router.post("/detect-emotion", response_model=EmotionDetectSchema)
@router.post("/detect", response_model=EmotionDetectSchema)
async def detect_emotion(request: EmotionDetectRequest):
    """
    Detect emotion from frontend base64 image via integrated backend model.
    
    This endpoint is called by the frontend (LiveSession.tsx) to detect emotion
    from camera capture. It uses the existing emotion detection pipeline which includes:
    - Local emotion_recognition module (primary)
    - Internal detector module (fallback)
    - Fallback to Neutral if all methods fail
    
    The emotion is then used to:
    1. Get rasa (Indian classical music concept) from rasa_model
    2. Cache the emotion for 5 minutes
    3. Update the session in database with emotion, rasa, and confidence scores
    """

    try:
        image_base64 = request.image_base64
        if image_base64.startswith("data:image/"):
            image_base64 = image_base64.split(",", 1)[-1]

        cache_key = f"emotion:{request.session_id}"
        cached_emotion = await cache_get(cache_key)
        if cached_emotion:
            return EmotionDetectSchema(
                emotion=cached_emotion,
                confidence=0.9,
                raw_dominant=str(cached_emotion).lower(),
            )

        detector = get_emotion_detector_lazy()
        try:
            # Primary path: integrated local emotion_recognition module (no separate server)
            emotion, confidence = await asyncio.wait_for(
                detect_with_local_emotion_module(image_base64),
                timeout=10.0,
            )
        except Exception as local_err:
            logger.warning(f"[Emotion] Integrated local module failed: {local_err}")
            if detector is None:
                emotion, confidence = "Neutral", 0.5
            else:
                try:
                    # Secondary path: internal detector module
                    emotion, confidence = await asyncio.wait_for(
                        detector.detect_from_base64(image_base64),
                        timeout=8.0,
                    )
                except Exception as detection_err:
                    logger.warning(f"[Emotion] Internal detector fallback failed: {detection_err}")
                    emotion, confidence = "Neutral", 0.5

        threshold = getattr(settings, "EMOTION_CONFIDENCE_THRESHOLD", 0.3)
        if confidence < threshold:
            emotion = "Neutral"

        emotion = (emotion or "Neutral").title()

        rasa_model = get_rasa_model()
        rasa_result = rasa_model.predict_rasa(emotion)
        rasa = rasa_result.get("rasa", "Shaant")

        await cache_set(cache_key, emotion, expiry=300)

        db = get_db()
        await db.sessions.update_one(
            {"_id": request.session_id},
            {
                "$set": {
                    "emotion": emotion,
                    "rasa": rasa,
                    "emotion_confidence": confidence,
                    "rasa_confidence": rasa_result.get("confidence", 0.8),
                }
            },
        )

        return EmotionDetectSchema(emotion=emotion, confidence=confidence, raw_dominant=emotion.lower())

     except HTTPException:
         raise
     except Exception as e:
         logger.error(f"[Emotion] Unexpected error: {e}")
         logger.error(f"[Emotion] Traceback: {traceback.format_exc()}")
         try:
             db = get_db()
             await db.sessions.update_one(
                 {"_id": request.session_id},
                 {"$set": {"emotion": "Neutral", "rasa": "Shaant"}},
             )
         except Exception as db_err:
             logger.error(f"[Emotion] Failed to persist fallback emotion: {db_err}")
         return _fallback_response()


# ============================================================================
# NEW CLEAN EMOTION DETECTION SERVICE - INTEGRATED ENDPOINTS
# ============================================================================


class CleanEmotionResponse(BaseModel):
    """Response model for clean emotion detection"""
    success: bool
    emotion: str
    confidence: float
    emotions: dict
    is_brave: bool
    face_detected: bool
    error: str = None


@router.post("/emotion/detect-clean")
async def detect_emotion_clean(image_base64: str = Form(...)) -> CleanEmotionResponse:
    """
    Clean emotion detection from base64 image.
    Uses refactored HSEmotion service with 8 emotions.
    
    Args:
        image_base64: Base64-encoded image string
        
    Returns:
        CleanEmotionResponse with detailed emotion breakdown
    """
    try:
        if not image_base64:
            raise ValueError("Image data is required")
        
        # Get clean emotion service
        service = get_clean_emotion_service()
        result = service.detect_from_base64(image_base64)
        
        return CleanEmotionResponse(**result)
    
    except ValueError as e:
        logger.warning(f"[CleanEmotion] Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"[CleanEmotion] Error detecting emotion: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/emotion/detect-file-clean")
async def detect_emotion_file_clean(file: UploadFile = File(...)) -> CleanEmotionResponse:
    """
    Clean emotion detection from uploaded image file.
    
    Args:
        file: Uploaded image file (JPEG, PNG, BMP)
        
    Returns:
        CleanEmotionResponse with detailed emotion breakdown
    """
    try:
        if not file:
            raise ValueError("Image file is required")
        
        # Validate file type
        allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/bmp"]
        if file.content_type not in allowed_types:
            raise ValueError(f"Invalid file type. Allowed: {', '.join(allowed_types)}")
        
        # Read file
        file_bytes = await file.read()
        
        # Get clean emotion service
        service = get_clean_emotion_service()
        result = service.detect_from_file(file_bytes)
        
        return CleanEmotionResponse(**result)
    
    except ValueError as e:
        logger.warning(f"[CleanEmotion] Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"[CleanEmotion] Error detecting emotion: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/emotion/health-clean")
async def emotion_health_clean():
    """Health check for clean emotion detection service"""
    try:
        service = get_clean_emotion_service()
        is_healthy = service.model is not None
        
        return {
            "status": "healthy" if is_healthy else "degraded",
            "service": "clean_emotion_detection",
            "model": "HSEmotion (enet_b0_8_best_afew)",
            "device": "CPU",
            "emotions": ["happy", "neutral", "sad", "angry", "bravery"],
        }
    except Exception as e:
        logger.error(f"[CleanEmotion] Health check failed: {e}")
        return {
            "status": "error",
            "service": "clean_emotion_detection",
            "error": str(e),
        }


@router.get("/emotion/info-clean")
async def emotion_info_clean():
    """Information about clean emotion detection service"""
    return {
        "name": "Clean Emotion Detection Service",
        "version": "1.0.0",
        "model": "HSEmotion (enet_b0_8_best_afew)",
        "raw_emotions": ["Anger", "Contempt", "Disgust", "Fear", "Happiness", "Neutral", "Sadness", "Surprise"],
        "simplified_emotions": ["happy", "neutral", "sad", "angry", "bravery"],
        "endpoints": {
            "POST /api/emotion/detect-clean": "Detect emotion from base64 image",
            "POST /api/emotion/detect-file-clean": "Detect emotion from file upload",
            "GET /api/emotion/health-clean": "Health check",
            "GET /api/emotion/info-clean": "Service information",
        },
        "bravery_formula": "0.6 × happiness + 0.4 × neutral - 0.7 × fear",
    }
