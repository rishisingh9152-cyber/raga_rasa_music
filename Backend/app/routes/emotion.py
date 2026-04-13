"""Emotion detection endpoints integrated in backend (no external service)."""

from fastapi import APIRouter, HTTPException
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


async def detect_with_integrated_archived_module(image_base64: str):
    """Use in-process local emotion_recognition module (no separate server)."""
    detector = get_local_emotion_detector()
    emotion_raw, confidence, _ = await asyncio.to_thread(detector.detect_from_base64, image_base64)
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
    """Detect emotion from frontend base64 image via integrated backend model."""

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
            # Primary path: integrated archived emotion_recognition module (no separate server)
            emotion, confidence = await asyncio.wait_for(
                detect_with_integrated_archived_module(image_base64),
                timeout=10.0,
            )
        except Exception as archived_err:
            logger.warning(f"[Emotion] Integrated archived module failed: {archived_err}")
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
