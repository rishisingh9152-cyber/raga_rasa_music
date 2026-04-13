"""
Clean emotion detection service - Core business logic
Integrated into main backend
"""

import numpy as np
from typing import Dict, Optional, Any
import logging

from app.services.emotion_model import EmotionModel
from app.services.image_processor import ImageProcessor

logger = logging.getLogger(__name__)

# Sensitivity multipliers for emotion normalization
SENSITIVITY = {
    "happy": 1.8,
    "sad": 1.0,
    "angry": 1.0,
    "fear": 1.0,
}

BRAVERY_THRESHOLD = 50


class CleanEmotionService:
    """
    Clean emotion detection service.
    Handles emotion detection pipeline from image to emotion classification.
    """

    # Emotion label mappings
    EMOTION_LABELS = {
        "happy": "Happy 😊",
        "neutral": "Neutral 😐",
        "sad": "Sad 😢",
        "angry": "Angry 😠",
        "bravery": "Bravery 💪",
    }

    def __init__(self):
        """Initialize emotion service with pre-loaded model"""
        try:
            self.model = EmotionModel()
            logger.info("[CleanEmotionService] ✓ Initialized successfully")
        except Exception as e:
            logger.error(f"[CleanEmotionService] Failed to initialize: {e}")
            self.model = None

    def detect_from_base64(self, base64_image: str) -> Dict[str, Any]:
        """
        Detect emotion from base64-encoded image.

        Args:
            base64_image: Base64-encoded image string

        Returns:
            Dictionary with emotion results
        """
        try:
            # Convert base64 to OpenCV format
            frame = ImageProcessor.base64_to_cv2(base64_image)

            # Normalize frame (ensure correct channels)
            frame = ImageProcessor.normalize_frame(frame)

            return self._detect_emotion_from_frame(frame)
        except Exception as e:
            logger.error(f"[CleanEmotionService] Error in detect_from_base64: {e}")
            return self._error_response(str(e))

    def detect_from_file(self, file_bytes: bytes) -> Dict[str, Any]:
        """
        Detect emotion from file bytes.

        Args:
            file_bytes: Raw image file bytes

        Returns:
            Dictionary with emotion results
        """
        try:
            # Convert file to OpenCV format
            frame = ImageProcessor.file_to_cv2(file_bytes)

            # Normalize frame
            frame = ImageProcessor.normalize_frame(frame)

            return self._detect_emotion_from_frame(frame)
        except Exception as e:
            logger.error(f"[CleanEmotionService] Error in detect_from_file: {e}")
            return self._error_response(str(e))

    def _detect_emotion_from_frame(self, frame: np.ndarray) -> Dict[str, Any]:
        """
        Internal method to detect emotion from OpenCV frame.

        Args:
            frame: OpenCV image (BGR numpy array)

        Returns:
            Dictionary with emotion detection results
        """
        try:
            if self.model is None:
                return self._empty_response()

            # Detect face
            face_box = self.model.detect_face(frame)

            if face_box is None:
                logger.warning("[CleanEmotionService] No face detected in image")
                return self._empty_response()

            # Crop face region
            face_crop = ImageProcessor.crop_face(frame, face_box)

            # Predict emotion
            emotion_label, raw_scores = self.model.predict_emotion(face_crop)

            # Process and normalize emotions
            emotions = self._process_emotions(raw_scores)

            # Determine dominant emotion
            dominant_raw = self._get_dominant_emotion(emotions)

            # Calculate bravery
            bravery = emotions["bravery"]

            return {
                "success": True,
                "emotion": dominant_raw,
                "confidence": round(emotions[dominant_raw] / 100, 2),
                "emotions": {
                    "happy": round(emotions["happy"], 1),
                    "neutral": round(emotions["neutral"], 1),
                    "sad": round(emotions["sad"], 1),
                    "angry": round(emotions["angry"], 1),
                    "bravery": round(emotions["bravery"], 1),
                },
                "is_brave": bravery >= BRAVERY_THRESHOLD,
                "face_detected": True,
            }

        except Exception as e:
            logger.error(f"[CleanEmotionService] Error detecting emotion: {str(e)}")
            return self._error_response(str(e))

    def _process_emotions(self, raw_scores: Dict[str, float]) -> Dict[str, float]:
        """
        Process and normalize raw emotion scores.

        Args:
            raw_scores: Raw emotion scores from model

        Returns:
            Normalized emotion scores (0-100 scale)
        """
        # Extract individual emotion scores
        happy = raw_scores.get("happiness", 0.0) * 100
        sad = raw_scores.get("sadness", 0.0) * 100
        angry = raw_scores.get("anger", 0.0) * 100
        neutral = raw_scores.get("neutral", 0.0) * 100
        fear = raw_scores.get("fear", 0.0) * 100

        # Apply sensitivity multipliers
        happy *= SENSITIVITY["happy"]
        sad *= SENSITIVITY["sad"]
        angry *= SENSITIVITY["angry"]

        # Normalize with neutral
        base = happy + sad + angry + neutral or 1.0

        happy = round(happy / base * 100, 1)
        sad = round(sad / base * 100, 1)
        angry = round(angry / base * 100, 1)
        neutral = round(neutral / base * 100, 1)

        # Calculate bravery (derived emotion)
        # Formula: 0.6 × happiness + 0.4 × neutral - 0.7 × fear
        bravery = 0.6 * happy + 0.4 * neutral - 0.7 * fear
        bravery = round(max(0.0, min(100.0, bravery)), 1)

        return {
            "happy": happy,
            "neutral": neutral,
            "sad": sad,
            "angry": angry,
            "bravery": bravery,
        }

    def _get_dominant_emotion(self, emotions: Dict[str, float]) -> str:
        """
        Determine dominant emotion from processed scores.

        Args:
            emotions: Processed emotion scores

        Returns:
            Name of dominant emotion
        """
        # Check neutral threshold first
        if emotions["neutral"] > 50:
            return "neutral"

        # Find emotion with highest score (excluding bravery)
        dominant = max(
            ["happy", "neutral", "sad", "angry"],
            key=lambda k: emotions[k],
        )

        return dominant

    def _empty_response(self) -> Dict[str, Any]:
        """Return empty response when no face is detected or model not available"""
        return {
            "success": True,
            "emotion": "neutral",
            "confidence": 0.0,
            "emotions": {
                "happy": 0.0,
                "neutral": 0.0,
                "sad": 0.0,
                "angry": 0.0,
                "bravery": 0.0,
            },
            "is_brave": False,
            "face_detected": False,
        }

    def _error_response(self, error_msg: str) -> Dict[str, Any]:
        """Return error response"""
        return {
            "success": False,
            "error": error_msg,
            "emotion": "neutral",
            "confidence": 0.0,
            "face_detected": False,
        }


# Singleton instance
_clean_emotion_service = None


def get_clean_emotion_service() -> CleanEmotionService:
    """Get singleton instance of clean emotion service"""
    global _clean_emotion_service
    if _clean_emotion_service is None:
        _clean_emotion_service = CleanEmotionService()
    return _clean_emotion_service
