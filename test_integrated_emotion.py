"""
Test the integrated emotion detection service
"""

import asyncio
import base64
import sys
import os

# Add Backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Backend'))

from app.services.emotion import get_emotion_detector


async def test_emotion_detector():
    """Test emotion detector initialization and basic functionality"""
    
    print("[Test] Initializing emotion detector...")
    detector = get_emotion_detector()
    
    print(f"[Test] Model type: {detector.model_type}")
    print(f"[Test] HSEmotion recognizer: {detector.recognizer is not None}")
    print(f"[Test] Fallback detector: {detector.detector is not None}")
    
    if detector.recognizer is None and detector.detector is None:
        print("[ERROR] No emotion model could be initialized!")
        return False
    
    print("[Test] Emotion detector initialized successfully!")
    print(f"[Test] Using model: {detector.model_type}")
    
    # Create a simple test image (small gray image)
    import numpy as np
    import cv2
    
    # Create a 100x100 gray image
    test_image = np.ones((100, 100, 3), dtype=np.uint8) * 128
    
    # Encode to base64
    _, buffer = cv2.imencode('.jpg', test_image)
    test_base64 = base64.b64encode(buffer).decode('utf-8')
    
    print("[Test] Testing emotion detection with sample image...")
    try:
        emotion, confidence = await detector.detect_from_base64(test_base64)
        print(f"[Test] ✓ Emotion detection works!")
        print(f"[Test] Detected emotion: {emotion}")
        print(f"[Test] Confidence: {confidence:.2f}")
        return True
    except Exception as e:
        print(f"[ERROR] Emotion detection failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Integrated Emotion Detector Test")
    print("=" * 60)
    
    success = asyncio.run(test_emotion_detector())
    
    if success:
        print("\n✓ All tests passed!")
        sys.exit(0)
    else:
        print("\n✗ Tests failed!")
        sys.exit(1)
