"""Test script to verify emotion detection service connectivity"""

import requests
import base64
import json
from pathlib import Path

# Test paths
TEST_IMAGE_PATH = Path("C:/Major Project/backend/tests/sample_emotion.jpg")
EMOTION_SERVICE_URL = "http://localhost:5000"
BACKEND_API_URL = "http://localhost:8000/api"

def test_emotion_service_health():
    """Test if emotion service is reachable"""
    print("=" * 60)
    print("Testing Emotion Service Health...")
    print("=" * 60)
    
    try:
        response = requests.get(f"{EMOTION_SERVICE_URL}/health", timeout=5)
        print(f"✓ Emotion Service Status: {response.status_code}")
        print(f"  Response: {response.json()}")
        return True
    except Exception as e:
        print(f"✗ Emotion Service Connection Failed: {e}")
        return False

def test_backend_health():
    """Test if backend is reachable"""
    print("\n" + "=" * 60)
    print("Testing Backend Health...")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BACKEND_API_URL.replace('/api', '')}/health", timeout=5)
        print(f"✓ Backend Status: {response.status_code}")
        print(f"  Response: {response.json()}")
        return True
    except Exception as e:
        print(f"✗ Backend Connection Failed: {e}")
        return False

def test_emotion_service_detection():
    """Test emotion detection directly from emotion service"""
    print("\n" + "=" * 60)
    print("Testing Emotion Service Detection...")
    print("=" * 60)
    
    # Create a simple test image (1x1 pixel red)
    try:
        import cv2
        import numpy as np
        
        # Create a simple test image
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        img[:, :] = [100, 150, 200]  # BGR color
        
        # Encode to base64
        _, buffer = cv2.imencode('.jpg', img)
        image_base64 = base64.b64encode(buffer).decode('utf-8')
        
        # Send to emotion service
        payload = {"image": image_base64}
        response = requests.post(
            f"{EMOTION_SERVICE_URL}/detect",
            json=payload,
            timeout=30
        )
        
        print(f"✓ Emotion Detection Response: {response.status_code}")
        result = response.json()
        print(f"  Emotions: {result.get('emotions', {})}")
        print(f"  Dominant: {result.get('raw_dominant')}")
        return True
        
    except ImportError:
        print("⚠ OpenCV not available, skipping image test")
        return False
    except Exception as e:
        print(f"✗ Emotion Detection Failed: {e}")
        return False

def test_backend_emotion_health():
    """Test backend emotion service health endpoint"""
    print("\n" + "=" * 60)
    print("Testing Backend Emotion Service Health...")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BACKEND_API_URL}/emotion-service/health", timeout=5)
        print(f"✓ Backend Emotion Health Status: {response.status_code}")
        print(f"  Response: {response.json()}")
        return True
    except Exception as e:
        print(f"✗ Backend Emotion Health Check Failed: {e}")
        return False

def main():
    """Run all tests"""
    print("\n")
    print("█" * 60)
    print("  RAGA RASA - EMOTION DETECTION SERVICE TEST")
    print("█" * 60)
    
    # Run tests
    emotion_health = test_emotion_service_health()
    backend_health = test_backend_health()
    emotion_backend_health = test_backend_emotion_health()
    emotion_detection = test_emotion_service_detection()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Emotion Service Health:    {'✓ PASS' if emotion_health else '✗ FAIL'}")
    print(f"Backend Health:            {'✓ PASS' if backend_health else '✗ FAIL'}")
    print(f"Backend Emotion Health:    {'✓ PASS' if emotion_backend_health else '✗ FAIL'}")
    print(f"Emotion Detection:         {'✓ PASS' if emotion_detection else '✗ FAIL'}")
    
    all_pass = all([emotion_health, backend_health, emotion_backend_health, emotion_detection])
    
    if all_pass:
        print("\n✓ All tests passed! System is ready.")
    else:
        print("\n✗ Some tests failed. Check the errors above.")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
