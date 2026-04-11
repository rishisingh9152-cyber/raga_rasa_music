"""Emotion detection endpoints"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import logging
import traceback

from app.database import get_db
from app.services.external_emotion import get_emotion_service_client, check_emotion_service
from app.services.rasa_model import get_rasa_model
from app.models import EmotionDetectSchema
from app.services.cache import cache_get, cache_set
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

# Flag to track which service to use
USE_EXTERNAL_SERVICE = getattr(settings, 'USE_EXTERNAL_EMOTION_SERVICE', True)


class EmotionDetectRequest(BaseModel):
    """Emotion detection request"""
    image_base64: str
    session_id: str


@router.get("/emotion-service/health")
async def emotion_service_health():
    """Check if emotion recognition service is available"""
    try:
        is_healthy = await check_emotion_service()
        return {
            "status": "healthy" if is_healthy else "unavailable",
            "service": "external_emotion_recognition",
            "fallback_available": True
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "error",
            "service": "external_emotion_recognition",
            "error": str(e)
        }


@router.post("/detect-emotion", response_model=EmotionDetectSchema)
async def detect_emotion(request: EmotionDetectRequest):
    """
    Detect emotion from webcam image using external service with fallback
    
    Args:
        image_base64: Base64 encoded JPEG image from frontend
        session_id: Session identifier for tracking
    
    Returns:
        Detected emotion label
    """
    try:
        # Handle case where frontend sends data URI prefix
        image_base64 = request.image_base64
        if image_base64.startswith("data:image/"):
            # Strip data URI prefix (e.g., "data:image/jpeg;base64,")
            logger.warning("[Emotion] Detected data URI prefix, stripping it")
            image_base64 = image_base64.split(",", 1)[-1]
            logger.info("[Emotion] Data URI prefix removed, proceeding with pure base64")
        
        # Check cache first
        cache_key = f"emotion:{request.session_id}"
        cached_emotion = await cache_get(cache_key)
        if cached_emotion:
            logger.info(f"[Emotion] Emotion retrieved from cache: {cached_emotion}")
            return EmotionDetectSchema(
                emotion=cached_emotion,
                confidence=0.9,  # Cached result
                raw_dominant=cached_emotion.lower()
            )
        
        logger.info(f"[Emotion] Attempting external emotion detection for session: {request.session_id}")
        
        # Try to use external emotion recognition service
        emotion = None
        confidence = 0.5
        
        try:
            client = get_emotion_service_client()
            emotion, confidence = await client.predict_emotion(image_base64)
            logger.info(f"[Emotion] External service returned: {emotion} (confidence: {confidence:.2f})")
            
            # Validate confidence threshold
            threshold = getattr(settings, 'EMOTION_CONFIDENCE_THRESHOLD', 0.3)
            if confidence < threshold:
                emotion = 'Neutral'
                logger.warning(f"[Emotion] Low confidence ({confidence:.2f}), defaulting to Neutral")
        
        except Exception as service_err:
            logger.warning(f"[Emotion] External service unavailable: {str(service_err)}")
            logger.info(f"[Emotion] Using fallback: assigning Neutral emotion")
            emotion = 'Neutral'
            confidence = 0.5
        
        # Ensure emotion is set
        if not emotion:
            emotion = 'Neutral'
            logger.warning(f"[Emotion] Emotion detection returned None, using Neutral")
        
        # Normalize emotion to title case
        emotion = emotion.title() if emotion else 'Neutral'
        logger.info(f"[Emotion] Final emotion: {emotion}")
        
        # Get rasa classification using trained model
        rasa_model = get_rasa_model()
        rasa_result = rasa_model.predict_rasa(emotion)
        rasa = rasa_result.get('rasa', 'Shaant')
        
        # Cache the result
        await cache_set(cache_key, emotion, expiry=300)  # Cache for 5 minutes
        
        # Update session with detected emotion and classified rasa
        db = get_db()
        await db.sessions.update_one(
            {"_id": request.session_id},
            {
                "$set": {
                    "emotion": emotion,
                    "rasa": rasa,
                    "emotion_confidence": confidence,
                    "rasa_confidence": rasa_result.get('confidence', 0.8)
                }
            }
        )
        
        logger.info(
            f"[Emotion] Session {request.session_id}: "
            f"emotion={emotion} (conf: {confidence:.2f}), "
            f"rasa={rasa} (conf: {rasa_result.get('confidence', 0.8):.2f})"
        )
        return EmotionDetectSchema(
            emotion=emotion,
            confidence=confidence,
            raw_dominant=emotion.lower()
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"[Emotion] Unexpected error in emotion detection: {str(e)}")
        logger.error(f"[Emotion] Traceback: {traceback.format_exc()}")
        # Return a fallback emotion instead of erroring out
        logger.info(f"[Emotion] Using fallback emotion: Neutral")
        try:
            db = get_db()
            await db.sessions.update_one(
                {"_id": request.session_id},
                {"$set": {"emotion": "Neutral", "rasa": "Shaant"}}
            )
            return EmotionDetectSchema(
                emotion="Neutral",
                confidence=0.5,
                raw_dominant="neutral"
            )
        except Exception as db_err:
            logger.error(f"[Emotion] Failed to update fallback emotion: {db_err}")
            raise HTTPException(status_code=500, detail="Emotion detection failed")
