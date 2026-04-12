#!/usr/bin/env python3
"""
End-to-end test for RagaRasa Music Therapy flow:
1. Start session
2. Detect emotion
3. Get recommendations
4. Verify song URLs work
"""

import requests
import json
import time
import base64
from pathlib import Path
import sys
import io

# Fix Unicode on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Configuration
BACKEND_BASE_URL = "https://raga-rasa-backend.onrender.com"
EMOTION_SERVICE_BASE_URL = "https://raga-rasa-music.onrender.com"

def test_health_checks():
    """Test if services are running"""
    print("\n" + "="*60)
    print("HEALTH CHECKS")
    print("="*60)
    
    # Backend health
    try:
        response = requests.get(f"{BACKEND_BASE_URL}/health", timeout=10)
        print(f"[OK] Backend health: {response.status_code}")
        print(f"  Response: {response.json()}")
    except Exception as e:
        print(f"[FAIL] Backend health check failed: {e}")
    
    # Emotion service health
    try:
        response = requests.get(f"{BACKEND_BASE_URL}/api/emotion-service/health", timeout=10)
        print(f"[OK] Emotion service health: {response.status_code}")
        print(f"  Response: {response.json()}")
    except Exception as e:
        print(f"[FAIL] Emotion service health check failed: {e}")

def test_session_creation():
    """Test session creation"""
    print("\n" + "="*60)
    print("TEST 1: SESSION CREATION")
    print("="*60)
    
    try:
        response = requests.post(
            f"{BACKEND_BASE_URL}/api/session/start",
            json={},
            timeout=10
        )
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        
        if "session_id" in data:
            session_id = data["session_id"]
            print(f"\n[OK] Session created successfully!")
            print(f"  Session ID: {session_id}")
            return session_id
        else:
            print(f"[FAIL] No session_id in response")
            return None
            
    except Exception as e:
        print(f"[FAIL] Session creation failed: {e}")
        return None

def create_test_image():
    """Create a simple test image (1x1 white JPEG)"""
    # This is a minimal valid JPEG (1x1 pixel white)
    jpeg_base64 = "/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/2wBDAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8VAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCwAA8A/9k="
    return jpeg_base64

def test_emotion_detection(session_id):
    """Test emotion detection with a dummy image"""
    print("\n" + "="*60)
    print("TEST 2: EMOTION DETECTION")
    print("="*60)
    
    if not session_id:
        print("[FAIL] No session ID available")
        return None
    
    try:
        image_base64 = create_test_image()
        
        response = requests.post(
            f"{BACKEND_BASE_URL}/api/detect-emotion",
            json={
                "image_base64": image_base64,
                "session_id": session_id
            },
            timeout=30
        )
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        
        if "emotion" in data:
            emotion = data["emotion"]
            print(f"\n[OK] Emotion detected successfully!")
            print(f"  Emotion: {emotion}")
            print(f"  Confidence: {data.get('confidence', 'N/A')}")
            return emotion
        else:
            print(f"[FAIL] No emotion in response")
            return None
            
    except Exception as e:
        print(f"[FAIL] Emotion detection failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_recommendations(session_id, emotion):
    """Test song recommendations"""
    print("\n" + "="*60)
    print("TEST 3: RECOMMENDATIONS")
    print("="*60)
    
    if not session_id or not emotion:
        print("[FAIL] Missing session ID or emotion")
        return None
    
    # Mock cognitive data (from pre-test)
    cognitive_data = {
        "memory_score": 4,
        "reaction_time": 250,
        "accuracy_score": 85
    }
    
    try:
        response = requests.post(
            f"{BACKEND_BASE_URL}/api/recommend/live",
            json={
                "emotion": emotion,
                "session_id": session_id,
                "cognitive_data": cognitive_data
            },
            timeout=30
        )
        print(f"Status: {response.status_code}")
        data = response.json()
        
        if isinstance(data, list):
            print(f"\n[OK] Recommendations retrieved successfully!")
            print(f"  Total songs: {len(data)}")
            
            if len(data) > 0:
                print(f"\n  First 3 recommendations:")
                for i, song in enumerate(data[:3]):
                    print(f"\n  [{i+1}] {song.get('title', 'Unknown')}")
                    print(f"      Rasa: {song.get('rasa', 'N/A')}")
                    print(f"      Confidence: {song.get('confidence', 0):.2f}")
                    print(f"      URL: {song.get('audio_url', 'N/A')[:100]}...")
            else:
                print("[FAIL] No songs returned")
            
            return data
        else:
            print(f"[FAIL] Unexpected response format: {type(data)}")
            print(f"  Response: {json.dumps(data, indent=2)}")
            return None
            
    except Exception as e:
        print(f"[FAIL] Recommendation failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_song_urls(songs):
    """Test if song URLs are accessible"""
    print("\n" + "="*60)
    print("TEST 4: SONG URL ACCESSIBILITY")
    print("="*60)
    
    if not songs or len(songs) == 0:
        print("[FAIL] No songs to test")
        return
    
    for i, song in enumerate(songs[:3]):
        url = song.get("audio_url")
        title = song.get("title", "Unknown")
        
        if not url:
            print(f"[FAIL] Song {i+1} ({title}): No URL provided")
            continue
        
        try:
            # Head request to check if URL exists
            response = requests.head(url, timeout=10, allow_redirects=True)
            if response.status_code == 200:
                print(f"[OK] Song {i+1} ({title}): URL accessible (HTTP {response.status_code})")
            else:
                print(f"[WARN] Song {i+1} ({title}): URL returned {response.status_code}")
        except Exception as e:
            print(f"[FAIL] Song {i+1} ({title}): URL test failed - {e}")

def main():
    print("\n" + "="*60)
    print("RAGARASA MUSIC THERAPY - END-TO-END TEST")
    print("="*60)
    
    # Step 1: Health checks
    test_health_checks()
    
    # Step 2: Create session
    session_id = test_session_creation()
    
    if not session_id:
        print("\n[FAIL] Test failed: Could not create session")
        return
    
    # Step 3: Detect emotion
    emotion = test_emotion_detection(session_id)
    
    if not emotion:
        print("\n[FAIL] Test failed: Could not detect emotion")
        return
    
    # Step 4: Get recommendations
    songs = test_recommendations(session_id, emotion)
    
    if not songs:
        print("\n[FAIL] Test failed: Could not get recommendations")
        return
    
    # Step 5: Test song URLs
    test_song_urls(songs)
    
    print("\n" + "="*60)
    print("[OK] END-TO-END TEST COMPLETE")
    print("="*60)

if __name__ == "__main__":
    main()
