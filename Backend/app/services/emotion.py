"""Emotion detection service using ML models"""

import cv2
import numpy as np
import base64
from io import BytesIO
import logging
from typing import Tuple
import asyncio
from concurrent.futures import ThreadPoolExecutor

from app.config import settings

logger = logging.getLogger(__name__)

# Thread pool for CPU-intensive ML operations
executor = ThreadPoolExecutor(max_workers=4)

# Emotion labels mapping
EMOTION_MAPPING = {
    # FER/DeepFace labels -> Frontend compatible labels
    'angry': 'Angry',
    'disgust': 'Disgusted',
    'fear': 'Fearful',
    'happy': 'Happy',
    'neutral': 'Neutral',
    'sad': 'Sad',
    'surprise': 'Surprised',
}

# Rasa mapping (Indian classical music emotional classification)
EMOTION_TO_RASA = {
    'Happy': 'Shringar',      # Romantic/Aesthetic
    'Surprised': 'Shringar',  # Surprise can be pleasant
    'Sad': 'Shok',            # Sorrowful
    'Angry': 'Veer',          # Heroic/Energetic
    'Fearful': 'Veer',        # Fearful → Stimulating
    'Disgusted': 'Veer',      # Disgust → Stimulating
    'Neutral': 'Shaant',      # Peaceful/Calm
}


class EmotionDetector:
    """Emotion detection from facial expressions"""
    
    def __init__(self):
        """Initialize emotion detection model"""
        self.model_type = settings.EMOTION_MODEL
        self._init_model()
    
    def _init_model(self):
        """Initialize the emotion detection model"""
        try:
            if self.model_type == 'fer':
                from fer import FER
                self.detector = FER(emotion_model_path=None)
                logger.info("FER model initialized successfully")
            elif self.model_type == 'deepface':
                import deepface
                self.detector = deepface
                logger.info("DeepFace model initialized successfully")
            else:
                logger.warning(f"Unknown emotion model: {self.model_type}, using FER")
                from fer import FER
                self.detector = FER(emotion_model_path=None)
        except ImportError as e:
            logger.warning(f"Failed to initialize emotion model: {e}, using fallback")
            self.detector = None
    
    async def detect_from_base64(self, image_base64: str) -> Tuple[str, float]:
        """
        Detect emotion from base64 encoded image
        
        Args:
            image_base64: Base64 encoded image string (with or without data URI prefix)
        
        Returns:
            Tuple of (emotion_label, confidence_score)
        """
        try:
            # Decode base64 image
            image_array = self._decode_base64(image_base64)
            
            # Run emotion detection in thread pool (blocking operation)
            emotion, confidence = await asyncio.get_event_loop().run_in_executor(
                executor,
                self._detect_emotion_sync,
                image_array
            )
            
            logger.info(f"Detected emotion: {emotion} (confidence: {confidence:.2f})")
            return emotion, confidence
            
        except Exception as e:
            logger.error(f"Emotion detection failed: {e}")
            # Fallback to neutral
            return 'Neutral', 0.5
    
    def _decode_base64(self, image_base64: str) -> np.ndarray:
        """Decode base64 image to numpy array"""
        try:
            # Handle data URI format
            if ',' in image_base64:
                image_base64 = image_base64.split(',')[1]
            
            # Decode base64
            image_data = base64.b64decode(image_base64)
            image_array = np.frombuffer(image_data, dtype=np.uint8)
            image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            
            if image is None:
                raise ValueError("Failed to decode image")
            
            return image
            
        except Exception as e:
            logger.error(f"Base64 decode failed: {e}")
            raise
    
    def _detect_emotion_sync(self, image: np.ndarray) -> Tuple[str, float]:
        """
        Synchronous emotion detection (runs in thread pool)
        
        Args:
            image: OpenCV image (BGR format)
        
        Returns:
            Tuple of (emotion_label, confidence)
        """
        try:
            if self.model_type == 'fer' and self.detector:
                # FER library
                result = self.detector.top_emotion(image)
                if result:
                    emotion_label, confidence = result
                    emotion_label = emotion_label.lower()
                    if emotion_label in EMOTION_MAPPING:
                        return EMOTION_MAPPING[emotion_label], confidence
            
            elif self.model_type == 'deepface' and self.detector:
                # DeepFace
                try:
                    analysis = self.detector.analyze(image, actions=['emotion'], enforce_detection=False)
                    if analysis and len(analysis) > 0:
                        emotion_dict = analysis[0]['emotion']
                        top_emotion = max(emotion_dict, key=emotion_dict.get)
                        confidence = emotion_dict[top_emotion] / 100.0
                        if top_emotion in EMOTION_MAPPING:
                            return EMOTION_MAPPING[top_emotion], confidence
                except Exception as e:
                    logger.warning(f"DeepFace analysis failed: {e}")
            
            # Fallback
            return 'Neutral', 0.5
            
        except Exception as e:
            logger.error(f"Emotion detection sync failed: {e}")
            return 'Neutral', 0.5
    
    @staticmethod
    def emotion_to_rasa(emotion: str) -> str:
        """
        Map detected emotion to Indian classical music rasa
        
        Args:
            emotion: Detected emotion label
        
        Returns:
            Rasa classification (Shringar, Shaant, Veer, Shok)
        """
        return EMOTION_TO_RASA.get(emotion, 'Shaant')  # Default to peaceful


# Global emotion detector instance
_detector: EmotionDetector = None


def get_emotion_detector() -> EmotionDetector:
    """Get or create emotion detector instance"""
    global _detector
    if _detector is None:
        _detector = EmotionDetector()
    return _detector
