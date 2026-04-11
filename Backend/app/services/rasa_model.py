"""
Rasa Classification Model Loader

Loads and uses the rasa classification model to map emotions to Indian classical music ragas.
Supports both Keras (H5) and scikit-learn (pickle) models.
"""

import os
import logging
from typing import Optional, Dict
import numpy as np
from pathlib import Path

logger = logging.getLogger(__name__)

# Model paths
MODELS_DIR = Path(__file__).parent.parent.parent / "models" / "rasa_classification"
MODEL_H5_PATH = MODELS_DIR / "model.h5"
MODEL_PKL_PATH = MODELS_DIR / "model.pkl"
MODEL_JOBLIB_PATH = MODELS_DIR / "model.joblib"


class RasaClassificationModel:
    """Rasa classification model wrapper"""
    
    def __init__(self):
        """Initialize rasa model"""
        self.model = None
        self.model_type = None
        self.emotion_labels = [
            "Angry", "Disgusted", "Fearful", "Happy", 
            "Neutral", "Sad", "Surprised"
        ]
        self._load_model()
    
    def _load_model(self):
        """Load model from disk"""
        try:
            # Try loading Keras model first
            if MODEL_H5_PATH.exists():
                logger.info(f"Found model.h5 at {MODEL_H5_PATH}, attempting to load...")
                self._load_keras_model()
                return
            
            # Try loading pickle model
            if MODEL_PKL_PATH.exists():
                logger.info(f"Found model.pkl at {MODEL_PKL_PATH}, attempting to load...")
                self._load_pickle_model()
                return
            
            # Try loading joblib model
            if MODEL_JOBLIB_PATH.exists():
                logger.info(f"Found model.joblib at {MODEL_JOBLIB_PATH}, attempting to load...")
                self._load_joblib_model()
                return
            
            logger.warning(f"No rasa model found in {MODELS_DIR}")
            logger.warning("Rasa classification will be disabled until model is uploaded")
            self.model = None
            
        except Exception as e:
            logger.error(f"Failed to load rasa model: {e}")
            logger.error("Will fall back to rule-based emotion->rasa mapping")
            self.model = None
    
    def _load_keras_model(self):
        """Load Keras H5 model"""
        try:
            import tensorflow as tf
            self.model = tf.keras.models.load_model(str(MODEL_H5_PATH))
            self.model_type = "keras"
            logger.info(f"Loaded Keras rasa model from {MODEL_H5_PATH}")
        except ImportError:
            logger.error("TensorFlow not installed. Cannot load H5 model.")
            raise
        except Exception as e:
            logger.error(f"Failed to load Keras model: {e}")
            raise
    
    def _load_pickle_model(self):
        """Load scikit-learn pickle model"""
        try:
            import pickle
            with open(MODEL_PKL_PATH, 'rb') as f:
                self.model = pickle.load(f)
            self.model_type = "sklearn"
            logger.info(f"Loaded scikit-learn rasa model from {MODEL_PKL_PATH}")
        except Exception as e:
            logger.error(f"Failed to load pickle model: {e}")
            raise
    
    def _load_joblib_model(self):
        """Load joblib model"""
        try:
            import joblib
            self.model = joblib.load(str(MODEL_JOBLIB_PATH))
            self.model_type = "sklearn"
            logger.info(f"Loaded joblib rasa model from {MODEL_JOBLIB_PATH}")
        except ImportError:
            logger.error("joblib not installed. Cannot load joblib model.")
            raise
        except Exception as e:
            logger.error(f"Failed to load joblib model: {e}")
            raise
    
    def predict_rasa_from_audio(self, audio_file_path: str) -> Dict[str, any]:
        """
        Predict rasa directly from audio file by extracting spectrogram
        
        Args:
            audio_file_path: Path to audio file (MP3, WAV, etc.)
        
        Returns:
            Dict with rasa prediction and confidence
        """
        if self.model is None:
            logger.warning(f"Model not loaded, using fallback mapping for audio file")
            return self._fallback_emotion_to_rasa("Neutral")
        
        try:
            import librosa
            
            logger.info(f"Extracting spectrogram from audio file: {audio_file_path}")
            
            # Load audio file
            y, sr = librosa.load(audio_file_path, sr=22050, duration=5)
            logger.info(f"Loaded audio: duration={len(y)/sr:.2f}s, sample_rate={sr}Hz")
            
            # Extract mel-spectrogram
            mel_spec = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128)
            logger.debug(f"Mel-spectrogram shape: {mel_spec.shape}")
            
            # Convert to dB scale and normalize
            mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
            logger.debug(f"Mel-spectrogram DB range: [{mel_spec_db.min():.2f}, {mel_spec_db.max():.2f}]")
            
            # Resize to (128, 128) if needed
            if mel_spec_db.shape != (128, 128):
                from scipy import ndimage
                # Calculate zoom factors
                zoom_factors = (128 / mel_spec_db.shape[0], 128 / mel_spec_db.shape[1])
                mel_spec_resized = ndimage.zoom(mel_spec_db, zoom_factors, order=1)
                logger.info(f"Resized spectrogram to (128, 128) from {mel_spec_db.shape}")
            else:
                mel_spec_resized = mel_spec_db
            
            # Normalize to [0, 1] range
            mel_spec_normalized = (mel_spec_resized - mel_spec_resized.min()) / (mel_spec_resized.max() - mel_spec_resized.min() + 1e-8)
            
            # Add channel dimension for model input: (128, 128, 1)
            mel_spec_input = np.expand_dims(mel_spec_normalized, axis=-1)
            mel_spec_batch = np.expand_dims(mel_spec_input, axis=0)  # Add batch dimension
            logger.info(f"Model input shape: {mel_spec_batch.shape}")
            
            # Make prediction
            if self.model_type == "keras":
                prediction = self.model.predict(mel_spec_batch, verbose=0)
                logger.debug(f"Raw model output: {prediction}")
                logger.debug(f"Output shape: {prediction.shape}")
                
                # prediction shape should be (1, 4) for 4 rasa classes
                rasa_idx = np.argmax(prediction[0])
                confidence = float(prediction[0][rasa_idx])
                logger.info(f"Keras model: rasa_idx={rasa_idx}, confidence={confidence:.4f}")
            else:  # sklearn
                prediction = self.model.predict(mel_spec_batch.reshape(1, -1))
                probabilities = self.model.predict_proba(mel_spec_batch.reshape(1, -1))
                rasa_idx = prediction[0]
                confidence = float(np.max(probabilities[0]))
                logger.info(f"Sklearn model: rasa_idx={rasa_idx}, confidence={confidence:.4f}")
            
            rasas = ["Shringar", "Shaant", "Veer", "Shok"]
            rasa = rasas[int(rasa_idx)] if int(rasa_idx) < len(rasas) else "Shaant"
            logger.info(f"Predicted rasa: {rasa} (confidence: {confidence:.4f})")
            
            return {
                "rasa": rasa,
                "confidence": float(confidence),
                "method": "spectrogram"
            }
            
        except Exception as e:
            logger.error(f"Rasa prediction from audio failed: {e}", exc_info=True)
            logger.error("Falling back to rule-based mapping")
            return self._fallback_emotion_to_rasa("Neutral")
    
    def predict_rasa(self, emotion: str) -> Dict[str, any]:
        """
        Predict rasa for given emotion (fallback if audio file not available)
        
        Args:
            emotion: Emotion label (e.g., "Happy", "happy", "Sad")
        
        Returns:
            Dict with rasa prediction and confidence
        """
        # This now just uses the fallback mapping directly
        logger.info(f"Using emotion-based fallback mapping for emotion: {emotion}")
        return self._fallback_emotion_to_rasa(emotion)
    
    def _emotion_to_vector(self, emotion: str) -> list:
        """Convert emotion label to feature vector (one-hot encoding)"""
        vector = [0] * len(self.emotion_labels)
        if emotion in self.emotion_labels:
            idx = self.emotion_labels.index(emotion)
            vector[idx] = 1
        else:
            # If emotion not found, use neutral
            vector[self.emotion_labels.index("Neutral")] = 1
        return vector
    
    @staticmethod
    def _fallback_emotion_to_rasa(emotion: str) -> Dict[str, any]:
        """
        Fallback mapping when model is not available
        
        Maps emotions directly to ragas without ML model
        Handles both uppercase and lowercase emotion labels
        """
        # Normalize to title case
        emotion_normalized = emotion.title() if emotion else "Neutral"
        
        mapping = {
            'Happy': 'Shringar',      # Romantic/Aesthetic
            'Surprised': 'Shringar',  # Surprise can be pleasant
            'Sad': 'Shok',            # Sorrowful
            'Angry': 'Veer',          # Heroic/Energetic
            'Fearful': 'Veer',        # Fearful → Stimulating
            'Disgusted': 'Veer',      # Disgust → Stimulating
            'Neutral': 'Shaant',      # Peaceful/Calm
        }
        
        rasa = mapping.get(emotion_normalized, 'Shaant')
        return {
            "emotion": emotion_normalized,
            "rasa": rasa,
            "confidence": 0.8,
            "method": "fallback"
        }


# Global model instance
_rasa_model: Optional[RasaClassificationModel] = None


def get_rasa_model() -> RasaClassificationModel:
    """Get or create rasa classification model"""
    global _rasa_model
    if _rasa_model is None:
        _rasa_model = RasaClassificationModel()
    return _rasa_model


def is_rasa_model_available() -> bool:
    """Check if rasa model is loaded"""
    model = get_rasa_model()
    return model.model is not None
