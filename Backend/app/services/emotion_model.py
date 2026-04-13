"""
Emotion detection model - Handles HSEmotion model loading and inference
Part of integrated emotion detection service
"""

import numpy as np
import ssl
import warnings
from typing import Tuple, Optional, Dict
import logging

# Suppress warnings
ssl._create_default_https_context = ssl._create_unverified_context
warnings.filterwarnings("ignore")

logger = logging.getLogger(__name__)


def _patch_torch_load_for_hsemotion() -> None:
    """Ensure HSEmotion checkpoints load on newer PyTorch defaults."""
    try:
        import torch

        if getattr(torch.load, "_raga_rasa_patched", False):
            return
        original_load = torch.load

        def patched_load(*args, **kwargs):
            if "weights_only" not in kwargs:
                kwargs["weights_only"] = False
            return original_load(*args, **kwargs)

        patched_load._raga_rasa_patched = True
        torch.load = patched_load
    except Exception as e:
        logger.warning(f"[EmotionModel] torch.load patch skipped: {e}")


def _load_cv2_or_none():
    try:
        import cv2

        return cv2
    except Exception as e:
        logger.error(f"[EmotionModel] OpenCV import failed: {e}")
        return None

try:
    from hsemotion.facial_emotions import HSEmotionRecognizer
except ImportError:
    logger.warning("hsemotion library not installed. Emotion detection will use fallback.")
    HSEmotionRecognizer = None


class EmotionModel:
    """
    Encapsulates the HSEmotion model for emotion detection.
    Model is loaded once during initialization.
    """

    # HSEmotion class order (8 emotions)
    HS_CLASSES = [
        "Anger",
        "Contempt",
        "Disgust",
        "Fear",
        "Happiness",
        "Neutral",
        "Sadness",
        "Surprise",
    ]

    def __init__(self):
        """Initialize emotion model and face cascade classifiers"""
        logger.info("[EmotionModel] Initializing emotion recognition model...")

        self.cv2 = _load_cv2_or_none()
        if self.cv2 is None:
            logger.error("[EmotionModel] OpenCV unavailable; model disabled")
            self.recognizer = None
            self.face_cascade = None
            self.face_cascade_alt = None
            return

        try:
            _patch_torch_load_for_hsemotion()
            # Load HSEmotion model (pretrained on AffectNet)
            self.recognizer = HSEmotionRecognizer(
                model_name="enet_b0_8_best_afew", device="cpu"
            )
            logger.info("[EmotionModel] ✓ HSEmotion model loaded successfully")
        except Exception as e:
            logger.error(f"[EmotionModel] Failed to load HSEmotion: {e}")
            self.recognizer = None

        # Load face cascade classifiers
        self.face_cascade = self.cv2.CascadeClassifier(
            self.cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        self.face_cascade_alt = self.cv2.CascadeClassifier(
            self.cv2.data.haarcascades + "haarcascade_frontalface_alt2.xml"
        )

        logger.info("[EmotionModel] ✓ Face detection cascades loaded")

    def detect_face(self, frame: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """
        Detect face in the frame using cascade classifiers.

        Args:
            frame: Input image as numpy array (BGR format)

        Returns:
            Tuple of (x, y, w, h) for the largest face, or None if no face detected
        """
        if self.cv2 is None:
            return None
        try:
            gray = self.cv2.cvtColor(frame, self.cv2.COLOR_BGR2GRAY)
            gray = self.cv2.equalizeHist(gray)

            # Try both cascade classifiers
            for cascade in [self.face_cascade, self.face_cascade_alt]:
                if cascade is None or cascade.empty():
                    continue
                faces = cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.05,
                    minNeighbors=4,
                    minSize=(50, 50),
                    flags=self.cv2.CASCADE_SCALE_IMAGE,
                )

                if len(faces) > 0:
                    # Return the largest face (by area)
                    return tuple(max(faces, key=lambda f: f[2] * f[3]))

            return None
        except Exception as e:
            logger.error(f"[EmotionModel] Face detection error: {e}")
            return None

    def predict_emotion(
        self, face_crop: np.ndarray
    ) -> Tuple[str, Dict[str, float]]:
        """
        Predict emotion from face crop using HSEmotion model.

        Args:
            face_crop: Cropped face image (BGR format)

        Returns:
            Tuple of (emotion_label, raw_scores_dict)
        """
        if self.recognizer is None:
            raise RuntimeError("HSEmotion model not loaded")

        try:
            emotion_label, scores = self.recognizer.predict_emotions(
                face_crop, logits=False
            )
            # Create dictionary of raw emotion scores
            raw_scores = {
                self.HS_CLASSES[i].lower(): float(scores[i])
                for i in range(len(self.HS_CLASSES))
            }
            return emotion_label, raw_scores
        except Exception as e:
            logger.error(f"[EmotionModel] Error predicting emotions: {str(e)}")
            raise RuntimeError(f"Error predicting emotions: {str(e)}")
