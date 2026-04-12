#!/usr/bin/env python3
"""
End-to-end test for RagaRasa Music Therapy System
Tests the complete flow: image -> emotion -> rasa -> song recommendations
"""

import requests
import json
import base64
import cv2
import numpy as np
from pathlib import Path

# Configuration
BACKEND_URL = "https://raga-rasa-backend.onrender.com"
EMOTION_URL = "https://raga-rasa-music.onrender.com"
FRONTEND_URL = "https://raga-rasa-music-52.vercel.app"

# Colors for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"

def print_header(text):
    print(f"\n{CYAN}{'='*60}{RESET}")
    print(f"{CYAN}{text.center(60)}{RESET}")
    print(f"{CYAN}{'='*60}{RESET}\n")

def print_test(test_name):
    print(f"{YELLOW}[TEST] {test_name}{RESET}")

def print_pass(msg):
    print(f"{GREEN}[PASS] {msg}{RESET}")

def print_fail(msg):
    print(f"{RED}[FAIL] {msg}{RESET}")

def test_backend_health():
    """Test backend is alive"""
    print_test("Backend Health Check")
    try:
        resp = requests.get(f"{BACKEND_URL}/", timeout=10)
        print_pass(f"Backend online (status: {resp.status_code})")
        data = resp.json()
        print(f"  Version: {data.get('version')}")
        print(f"  Message: {data.get('message')}")
        return True
    except Exception as e:
        print_fail(f"Backend check failed: {e}")
        return False

def test_emotion_service_health():
    """Test emotion service is alive"""
    print_test("Emotion Service Health Check")
    try:
        resp = requests.get(f"{EMOTION_URL}/health", timeout=10)
        print_pass(f"Emotion service online (status: {resp.status_code})")
        data = resp.json()
        print(f"  Service: {data.get('service')}")
        print(f"  Detector initialized: {data.get('detector_initialized')}")
        return resp.status_code == 200
    except Exception as e:
        print_fail(f"Emotion service check failed: {e}")
        return False

def test_get_songs():
    """Test getting songs from catalog"""
    print_test("Get Songs from Catalog")
    try:
        resp = requests.get(f"{BACKEND_URL}/api/ragas/list", timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            count = len(data)
            print_pass(f"Successfully retrieved {count} songs")
            if count > 0:
                song = data[0]
                print(f"  Sample: {song.get('title')} - {song.get('artist')}")
                print(f"  Rasa: {song.get('rasa')}")
                print(f"  URL: {song.get('url', 'N/A')[:50]}...")
            return True
        else:
            print_fail(f"Failed to get songs (status: {resp.status_code})")
            return False
    except Exception as e:
        print_fail(f"Get songs failed: {e}")
        return False

def test_emotion_detection_flow():
    """Test emotion detection with a synthetic image"""
    print_test("Emotion Detection Flow (with synthetic image)")
    try:
        # Create a simple test image (1x1 white image)
        img = np.ones((100, 100, 3), dtype=np.uint8) * 255  # White image
        
        # Encode to base64
        _, buffer = cv2.imencode('.jpg', img)
        image_base64 = base64.b64encode(buffer).decode('utf-8')
        
        # Send to backend emotion endpoint
        payload = {
            "image_base64": image_base64,
            "session_id": "test_session_123"
        }
        
        resp = requests.post(
            f"{BACKEND_URL}/api/detect-emotion",
            json=payload,
            timeout=30
        )
        
        if resp.status_code == 200:
            data = resp.json()
            emotion = data.get('emotion', 'N/A')
            confidence = data.get('confidence', 0)
            print_pass(f"Emotion detected: {emotion} (confidence: {confidence:.2f})")
            return True
        else:
            print_fail(f"Emotion detection failed (status: {resp.status_code})")
            print(f"  Response: {resp.text[:200]}")
            return False
    except Exception as e:
        print_fail(f"Emotion detection flow failed: {e}")
        return False

def test_get_recommendations():
    """Test getting song recommendations for an emotion"""
    print_test("Get Song Recommendations")
    try:
        payload = {
            "emotion": "happy",
            "limit": 5
        }
        
        resp = requests.post(
            f"{BACKEND_URL}/api/recommend/live",
            json=payload,
            timeout=10
        )
        
        if resp.status_code == 200:
            data = resp.json()
            recommendations = data.get('recommendations', [])
            print_pass(f"Retrieved {len(recommendations)} recommendations for 'happy'")
            if recommendations:
                song = recommendations[0]
                print(f"  Top: {song.get('title')} - {song.get('artist')}")
                print(f"  Rasa: {song.get('rasa')}")
            return True
        else:
            print_fail(f"Failed to get recommendations (status: {resp.status_code})")
            print(f"  Response: {resp.text[:200]}")
            return False
    except Exception as e:
        print_fail(f"Get recommendations failed: {e}")
        return False

def test_frontend_accessibility():
    """Test frontend is accessible"""
    print_test("Frontend Accessibility Check")
    try:
        resp = requests.head(f"{FRONTEND_URL}/", timeout=10, allow_redirects=True)
        if 200 <= resp.status_code < 400:
            print_pass(f"Frontend online (status: {resp.status_code})")
            return True
        else:
            print_fail(f"Frontend returned status: {resp.status_code}")
            return False
    except Exception as e:
        print_fail(f"Frontend check failed: {e}")
        return False

def main():
    print_header("RagaRasa End-to-End Test Suite")
    
    results = {}
    
    # Run tests
    results['backend_health'] = test_backend_health()
    results['emotion_service'] = test_emotion_service_health()
    results['get_songs'] = test_get_songs()
    results['emotion_detection'] = test_emotion_detection_flow()
    results['recommendations'] = test_get_recommendations()
    results['frontend'] = test_frontend_accessibility()
    
    # Summary
    print_header("Test Summary")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = f"{GREEN}PASS{RESET}" if result else f"{RED}FAIL{RESET}"
        print(f"  {test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\n{CYAN}{'='*60}{RESET}")
    if passed == total:
        print(f"{GREEN}[SUCCESS] All tests passed! ({passed}/{total}){RESET}")
    else:
        print(f"{YELLOW}[WARNING] Some tests failed: {passed}/{total} passed{RESET}")
    print(f"{CYAN}{'='*60}{RESET}\n")
    
    return passed == total

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
