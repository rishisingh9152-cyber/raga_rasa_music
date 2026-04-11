"""
External Emotion Recognition Service Client

This module handles communication with an external face emotion recognition service.
Update the configuration based on your service details.
"""

import httpx
import logging
from typing import Optional, Tuple
import base64
from app.config import settings

logger = logging.getLogger(__name__)


class ExternalEmotionServiceClient:
    """Client for communicating with external emotion recognition service"""
    
    def __init__(
        self,
        service_url: str = None,
        endpoint: str = None,
        timeout: int = 60
    ):
        """
        Initialize emotion service client
        
        Args:
            service_url: Base URL of emotion recognition service
                        (e.g., http://localhost:5000)
            endpoint: API endpoint path (e.g., /detect, /predict)
            timeout: Request timeout in seconds (default 60s as emotion detection can be slow)
        """
        self.service_url = service_url or getattr(settings, 'EMOTION_SERVICE_URL', 'http://localhost:5000')
        self.endpoint = endpoint or getattr(settings, 'EMOTION_SERVICE_ENDPOINT', '/detect')
        self.timeout = timeout
        self.full_url = f"{self.service_url}{self.endpoint}"
        
        logger.info(f"Emotion Service Client initialized: {self.full_url}")
    
    async def predict_emotion(self, image_base64: str) -> Tuple[str, float]:
        """
        Send image to external emotion recognition service
        
        Uses HSEmotion API format with emotional scores
        Returns the most confident emotion detected
        
        Args:
            image_base64: Base64 encoded image
        
        Returns:
            Tuple of (emotion_label, confidence_score)
        """
        try:
            # HSEmotion service format
            request_payload = {
                "image": image_base64
            }
            
            logger.info(f"Sending emotion detection request to {self.full_url}")
            logger.info(f"Image size: {len(image_base64)} bytes")
            logger.debug(f"Payload keys: {request_payload.keys()}")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.full_url,
                    json=request_payload
                )
                
                logger.info(f"Emotion service response: {response.status_code}")
                
                # Handle different error codes gracefully
                if response.status_code == 422:
                    error_detail = response.text[:500]
                    logger.error(f"Emotion service returned 422 (Unprocessable Entity)")
                    logger.error(f"Service URL: {self.full_url}")
                    logger.error(f"Response: {error_detail}")
                    logger.error(f"This might mean the service expects a different field name or format")
                    return "neutral", 0.5
                
                response.raise_for_status()
                result = response.json()
                
                # Parse HSEmotion response format
                # The service returns: emotions dict, dominant emotion, raw_dominant, is_brave
                raw_dominant = result.get("raw_dominant") or "neutral"
                
                # Handle "No Face Detected" case
                if raw_dominant is None or raw_dominant == "No Face Detected":
                    logger.warning(f"No face detected in image, defaulting to neutral")
                    return "neutral", 0.3
                
                # Get confidence from emotions dict
                emotions = result.get("emotions", {})
                
                # Find the confidence for the detected emotion
                if raw_dominant in emotions:
                    confidence = emotions[raw_dominant]
                    # Normalize to 0-1 scale if it's 0-100
                    if confidence > 1.0:
                        confidence = confidence / 100.0
                else:
                    confidence = max(emotions.values()) if emotions else 0.5
                    if confidence > 1.0:
                        confidence = confidence / 100.0
                
                # Normalize emotion name to lowercase
                emotion_label = raw_dominant.lower()
                
                logger.info(f"Emotion detected: {emotion_label} (confidence: {confidence:.2f})")
                return emotion_label, confidence
                
        except httpx.RequestError as e:
            logger.error(f"Request to emotion service failed: {e}")
            return "neutral", 0.5
        except Exception as e:
            logger.error(f"Emotion service error: {e}")
            return "neutral", 0.5
    
    async def health_check(self) -> bool:
        """Check if emotion service is available"""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{self.service_url}/health")
                return response.status_code == 200
        except Exception as e:
            logger.warning(f"Emotion service health check failed: {e}")
            return False


# Global client instance
_emotion_client: Optional[ExternalEmotionServiceClient] = None


def get_emotion_service_client() -> ExternalEmotionServiceClient:
    """Get or create emotion service client"""
    global _emotion_client
    if _emotion_client is None:
        _emotion_client = ExternalEmotionServiceClient()
    return _emotion_client


async def check_emotion_service() -> bool:
    """Check if emotion service is running"""
    client = get_emotion_service_client()
    return await client.health_check()
