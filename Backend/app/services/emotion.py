"""Emotion detection service using ML models"""

# CRITICAL: Configure environment BEFORE importing cv2
import os
import sys

# Set OpenCV to headless mode (no display server needed)
os.environ['DISPLAY'] = ''
os.environ['LIBGL_ALWAYS_INDIRECT'] = '1'
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
os.environ['OPENCV_VIDEOIO_DEBUG'] = '0'

# Now safe to import cv2
import cv2
cv2.setUseOptimized(False)
cv2.setNumThreads(0)

import numpy as np
import base64
from io import BytesIO
import logging
from typing import Tuple, Dict
import asyncio
from concurrent.futures import ThreadPoolExecutor
import ssl
import warnings

from app.config import settings

logger = logging.getLogger(__name__)

# Thread pool for CPU-intensive ML operations
executor = ThreadPoolExecutor(max_workers=4)

# SSL bypass for HSEmotion model downloads
ssl._create_default_https_context = ssl._create_unverified_context
warnings.filterwarnings("ignore")

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
    """Emotion detection from facial expressions using HSEmotion (pretrained on AffectNet)"""
    
    # HSEmotion class order
    HS_CLASSES = ['Anger', 'Contempt', 'Disgust', 'Fear', 'Happiness', 'Neutral', 'Sadness', 'Surprise']
    
    # Emotion labels mapping
    EMOTION_LABELS = {
        "happy":   "Happy 😊",
        "neutral": "Neutral 😐",
        "sad":     "Sad 😢",
        "angry":   "Angry 😠",
        "bravery": "Bravery 💪",
    }
    
    # Sensitivity multipliers
    SENSITIVITY = {
        "happy": 1.8,
        "sad":   1.0,
        "angry": 1.0,
        "fear":  1.0,
    }
    
    BRAVERY_THRESHOLD = 50
    
    def __init__(self):
        """Initialize emotion detection model"""
        self.model_type = getattr(settings, 'EMOTION_MODEL', 'hsemotion')
        self.recognizer = None
        self.face_cascade = None
        self.face_cascade_alt = None
        self._init_model()
    
    def _init_model(self):
        """Initialize the emotion detection model - preferring HSEmotion"""
        try:
            # Try HSEmotion first (better quality, pretrained on AffectNet)
            try:
                logger.info("[Emotion] Attempting to initialize HSEmotion model...")
                from hsemotion.facial_emotions import HSEmotionRecognizer
                
                self.recognizer = HSEmotionRecognizer(
                    model_name='enet_b0_8_best_afew',
                    device='cpu'
                )
                
                # Load face cascades
                self.face_cascade = cv2.CascadeClassifier(
                    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
                )
                self.face_cascade_alt = cv2.CascadeClassifier(
                    cv2.data.haarcascades + "haarcascade_frontalface_alt2.xml"
                )
                
                self.model_type = 'hsemotion'
                logger.info("[Emotion] HSEmotion model initialized successfully")
                return
                
            except Exception as hs_err:
                logger.warning(f"[Emotion] HSEmotion failed: {hs_err}, trying FER...")
            
            # Fallback to FER
            try:
                from fer import FER
                self.detector = FER(emotion_model_path=None)
                self.model_type = 'fer'
                logger.info("[Emotion] FER model initialized successfully")
                return
                
            except Exception as fer_err:
                logger.warning(f"[Emotion] FER failed: {fer_err}, trying DeepFace...")
            
            # Fallback to DeepFace
            try:
                import deepface
                self.detector = deepface
                self.model_type = 'deepface'
                logger.info("[Emotion] DeepFace model initialized successfully")
                return
                
            except Exception as df_err:
                logger.error(f"[Emotion] All emotion models failed: {df_err}")
                logger.warning("[Emotion] Emotion detection will fallback to Neutral")
                self.detector = None
                
        except Exception as e:
            logger.error(f"[Emotion] Unexpected error during model initialization: {e}")
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
            emotion, confidence, emotion_dict = await asyncio.get_event_loop().run_in_executor(
                executor,
                self._detect_emotion_sync,
                image_array
            )
            
            logger.info(f"[Emotion] Detected emotion: {emotion} (confidence: {confidence:.2f})")
            return emotion, confidence
            
        except Exception as e:
            logger.error(f"[Emotion] Emotion detection failed: {e}")
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
    
    def _detect_emotion_sync(self, image: np.ndarray) -> Tuple[str, float, Dict]:
        """
        Synchronous emotion detection (runs in thread pool)
        
        Args:
            image: OpenCV image (BGR format)
        
        Returns:
            Tuple of (emotion_label, confidence, emotion_dict)
        """
        try:
            if self.model_type == 'hsemotion' and self.recognizer:
                # HSEmotion model - highest quality
                return self._detect_hsemotion(image)
            
            elif self.model_type == 'fer' and self.detector:
                # FER library
                result = self.detector.top_emotion(image)
                if result:
                    emotion_label, confidence = result
                    emotion_label = emotion_label.lower()
                    if emotion_label in EMOTION_MAPPING:
                        return EMOTION_MAPPING[emotion_label], confidence, {}
            
            elif self.model_type == 'deepface' and self.detector:
                # DeepFace
                try:
                    analysis = self.detector.analyze(image, actions=['emotion'], enforce_detection=False)
                    if analysis and len(analysis) > 0:
                        emotion_dict = analysis[0]['emotion']
                        top_emotion = max(emotion_dict, key=emotion_dict.get)
                        confidence = emotion_dict[top_emotion] / 100.0
                        if top_emotion in EMOTION_MAPPING:
                            return EMOTION_MAPPING[top_emotion], confidence, emotion_dict
                except Exception as e:
                    logger.warning(f"DeepFace analysis failed: {e}")
            
            # Fallback
            return 'Neutral', 0.5, {}
            
        except Exception as e:
            logger.error(f"[Emotion] Emotion detection sync failed: {e}")
            return 'Neutral', 0.5, {}
    
    def _detect_hsemotion(self, frame: np.ndarray) -> Tuple[str, float, Dict]:
        """
        Detect emotion using HSEmotion model (best quality)
        
        Args:
            frame: OpenCV image (BGR format)
        
        Returns:
            Tuple of (emotion_label, confidence, emotion_dict)
        """
        try:
            # Detect face
            face_box = self._detect_face(frame)
            if face_box is None:
                logger.warning("[Emotion] No face detected")
                return 'Neutral', 0.5, {}
            
            x, y, w, h = face_box
            
            # Crop face with padding
            pad = int(0.15 * min(w, h))
            x1 = max(0, x - pad)
            y1 = max(0, y - pad)
            x2 = min(frame.shape[1], x + w + pad)
            y2 = min(frame.shape[0], y + h + pad)
            face_crop = frame[y1:y2, x1:x2]
            
            if face_crop.size == 0:
                return 'Neutral', 0.5, {}
            
            # Predict emotions
            emotion_label, scores = self.recognizer.predict_emotions(face_crop, logits=False)
            raw = {self.HS_CLASSES[i].lower(): float(scores[i]) for i in range(len(self.HS_CLASSES))}
            
            # Extract scores
            happy   = raw.get("happiness", 0.0) * 100
            sad     = raw.get("sadness",   0.0) * 100
            angry   = raw.get("anger",     0.0) * 100
            neutral = raw.get("neutral",   0.0) * 100
            fear    = raw.get("fear",      0.0) * 100
            
            # Apply sensitivity
            happy = happy * self.SENSITIVITY["happy"]
            sad   = sad   * self.SENSITIVITY["sad"]
            angry = angry * self.SENSITIVITY["angry"]
            
            # Normalize INCLUDING neutral
            base = happy + sad + angry + neutral or 1.0
            
            happy   = round(happy   / base * 100, 1)
            sad     = round(sad     / base * 100, 1)
            angry   = round(angry   / base * 100, 1)
            neutral = round(neutral / base * 100, 1)
            
            # Improved bravery calculation
            bravery = 0.6 * happy + 0.4 * neutral - 0.7 * fear
            bravery = round(max(0.0, min(100.0, bravery)), 1)
            
            emotions = {
                "happy": happy,
                "neutral": neutral,
                "sad": sad,
                "angry": angry,
                "bravery": bravery
            }
            
            # Determine dominant emotion
            dominant_raw = max(
                ["happy", "neutral", "sad", "angry"],
                key=lambda k: emotions[k]
            )
            
            # Stabilize neutral detection
            if neutral > 50:
                dominant_raw = "neutral"
            
            # Map to standard emotion labels
            emotion_mapping_hsemotion = {
                "happy": "Happy",
                "neutral": "Neutral",
                "sad": "Sad",
                "angry": "Angry"
            }
            
            emotion_label = emotion_mapping_hsemotion.get(dominant_raw, "Neutral")
            confidence = emotions[dominant_raw] / 100.0
            
            logger.info(f"[Emotion] HSEmotion detected: {emotion_label} (confidence: {confidence:.2f})")
            
            return emotion_label, confidence, emotions
            
        except Exception as e:
            logger.error(f"[Emotion] HSEmotion detection failed: {e}")
            return 'Neutral', 0.5, {}
    
    def _detect_face(self, frame):
        """Detect face in frame using cascades"""
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.equalizeHist(gray)
            
            for cascade in [self.face_cascade, self.face_cascade_alt]:
                if cascade is not None and not cascade.empty():
                    faces = cascade.detectMultiScale(
                        gray,
                        scaleFactor=1.05,
                        minNeighbors=4,
                        minSize=(50, 50),
                        flags=cv2.CASCADE_SCALE_IMAGE
                    )
                    if len(faces) > 0:
                        # Return largest face
                        return tuple(max(faces, key=lambda f: f[2] * f[3]))
            
            return None
            
        except Exception as e:
            logger.warning(f"[Emotion] Face detection failed: {e}")
            return None
    
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
