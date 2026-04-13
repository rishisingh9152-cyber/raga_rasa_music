"""
Integrated adapter for archived emotion_recognition logic.

This module no longer runs a standalone Flask server.
It is imported by backend routes/services and exposes pure functions only.
"""

from typing import Dict, Any, Tuple
import base64
import logging
import numpy as np
import cv2

from .emotion_detector import EmotionDetector

logger = logging.getLogger(__name__)

_detector: EmotionDetector | None = None


def get_detector() -> EmotionDetector:
    """Lazy-load the archived detector as an in-process backend component."""
    global _detector
    if _detector is None:
        _detector = EmotionDetector()
    return _detector


def detect_emotion_from_base64(image_base64: str) -> Tuple[str, float, Dict[str, Any]]:
    """
    Run emotion detection directly (no external HTTP call).

    Returns:
      (emotion_raw, confidence_0_to_1, full_result_dict)
    """
    try:
        if image_base64.startswith("data:"):
            image_base64 = image_base64.split(",", 1)[1]

        image_bytes = base64.b64decode(image_base64)
        nparr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if frame is None:
            raise ValueError("Failed to decode image")

        detector = get_detector()
        result = detector.detect_from_frame(frame)

        dominant_raw = result.get("raw_dominant") or "neutral"
        emotions = result.get("emotions") or {}
        confidence = float(emotions.get(dominant_raw, 50.0))
        if confidence > 1.0:
            confidence = confidence / 100.0

        return str(dominant_raw), confidence, result
    except Exception as e:
        logger.error(f"Integrated archived emotion detection failed: {e}")
        return "neutral", 0.5, {"raw_dominant": "neutral", "emotions": {"neutral": 50.0}}
