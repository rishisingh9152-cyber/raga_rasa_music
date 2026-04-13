"""
Image preprocessing utilities for emotion detection
"""

import base64
import io
import cv2
import numpy as np
from typing import Tuple, Optional
from PIL import Image
import logging

logger = logging.getLogger(__name__)


class ImageProcessor:
    """Handles image preprocessing and validation"""

    MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB max
    ALLOWED_FORMATS = ["jpeg", "jpg", "png", "bmp"]

    @staticmethod
    def validate_image_size(image_bytes: bytes) -> bool:
        """
        Validate that image size is within acceptable limits.

        Args:
            image_bytes: Raw image bytes

        Returns:
            True if image size is valid, False otherwise
        """
        return len(image_bytes) <= ImageProcessor.MAX_IMAGE_SIZE

    @staticmethod
    def validate_image_format(image: Image.Image) -> bool:
        """
        Validate image format.

        Args:
            image: PIL Image object

        Returns:
            True if format is allowed, False otherwise
        """
        return image.format.lower() in ImageProcessor.ALLOWED_FORMATS

    @staticmethod
    def base64_to_cv2(base64_string: str) -> Optional[np.ndarray]:
        """
        Convert base64-encoded image string to OpenCV format.

        Args:
            base64_string: Base64-encoded image string

        Returns:
            OpenCV image (BGR numpy array) or None if conversion fails
        """
        try:
            # Remove data URI prefix if present
            if "," in base64_string:
                base64_string = base64_string.split(",")[1]

            # Decode base64
            image_bytes = base64.b64decode(base64_string)

            # Validate size
            if not ImageProcessor.validate_image_size(image_bytes):
                raise ValueError(
                    f"Image size exceeds maximum limit of {ImageProcessor.MAX_IMAGE_SIZE} bytes"
                )

            # Convert bytes to image
            image_array = np.frombuffer(image_bytes, dtype=np.uint8)
            frame = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

            if frame is None:
                raise ValueError("Failed to decode image data")

            return frame

        except Exception as e:
            logger.error(f"[ImageProcessor] Error converting base64 to image: {str(e)}")
            raise ValueError(f"Error converting base64 to image: {str(e)}")

    @staticmethod
    def file_to_cv2(file_bytes: bytes) -> Optional[np.ndarray]:
        """
        Convert file bytes to OpenCV format.

        Args:
            file_bytes: Raw file bytes

        Returns:
            OpenCV image (BGR numpy array) or None if conversion fails
        """
        try:
            if not ImageProcessor.validate_image_size(file_bytes):
                raise ValueError(
                    f"Image size exceeds maximum limit of {ImageProcessor.MAX_IMAGE_SIZE} bytes"
                )

            image_array = np.frombuffer(file_bytes, dtype=np.uint8)
            frame = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

            if frame is None:
                raise ValueError("Failed to decode image file")

            return frame

        except Exception as e:
            logger.error(f"[ImageProcessor] Error converting file to image: {str(e)}")
            raise ValueError(f"Error converting file to image: {str(e)}")

    @staticmethod
    def crop_face(
        frame: np.ndarray, face_box: Tuple[int, int, int, int], padding: float = 0.15
    ) -> Optional[np.ndarray]:
        """
        Crop face region from frame with padding.

        Args:
            frame: Input image (OpenCV format)
            face_box: Tuple of (x, y, w, h) for face location
            padding: Padding factor relative to face size

        Returns:
            Cropped face image or None if crop fails
        """
        try:
            x, y, w, h = face_box
            pad = int(padding * min(w, h))

            # Apply padding with boundary checks
            x1 = max(0, x - pad)
            y1 = max(0, y - pad)
            x2 = min(frame.shape[1], x + w + pad)
            y2 = min(frame.shape[0], y + h + pad)

            face_crop = frame[y1:y2, x1:x2]

            if face_crop.size == 0:
                raise ValueError("Cropped face region is empty")

            return face_crop

        except Exception as e:
            logger.error(f"[ImageProcessor] Error cropping face: {str(e)}")
            raise ValueError(f"Error cropping face: {str(e)}")

    @staticmethod
    def normalize_frame(frame: np.ndarray) -> np.ndarray:
        """
        Normalize frame for better processing.

        Args:
            frame: Input image

        Returns:
            Normalized image
        """
        try:
            # Ensure frame is 3-channel BGR
            if len(frame.shape) == 2:
                frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
            elif frame.shape[2] == 4:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

            return frame
        except Exception as e:
            logger.error(f"[ImageProcessor] Error normalizing frame: {str(e)}")
            return frame
