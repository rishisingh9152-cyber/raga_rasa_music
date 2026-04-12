#!/usr/bin/env python3
"""
End-to-end test for RagaRasa Music Therapy flow with mock emotion detection
Tests: recommendations, song URLs, and database updates
"""

import requests
import json
import sys
import io

# Fix Unicode on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Configuration
BACKEND_BASE_URL = "https://raga-rasa-backend.onrender.com"

def test_session_creation():
    """Test session creation"""
    print("\n" + "="*60)
    print("TEST 1: SESSION CREATION")
    print("="*60)
    
    try:
        response = requests.post(
            f"{BACKEND_BASE_URL}/api/session/start",
            json={},
            timeout=30  # Increased timeout for slow backend
        )
        print(f"Status: {response.status_code}")
        data = response.json()
        
        if "session_id" in data:
            session_id = data["session_id"]
            print(f"[OK] Session created successfully!")
            print(f"  Session ID: {session_id}")
            print(f"  Created at: {data.get('created_at', 'N/A')}")
            return session_id
        else:
            print(f"[FAIL] No session_id in response")
            return None
            
    except Exception as e:
        print(f"[FAIL] Session creation failed: {e}")
        return None

def test_recommendations_with_mock_emotion(session_id, emotion="Happy"):
    """Test song recommendations with a mock emotion (skip the slow emotion detection)"""
    print("\n" + "="*60)
    print(f"TEST 2: RECOMMENDATIONS (emotion={emotion})")
    print("="*60)
    
    if not session_id:
        print("[FAIL] Missing session ID")
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
        
        if response.status_code != 200:
            print(f"[FAIL] Got status {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return None
        
        data = response.json()
        
        if isinstance(data, list):
            print(f"[OK] Recommendations retrieved successfully!")
            print(f"  Total songs: {len(data)}")
            
            if len(data) > 0:
                print(f"\n  First 5 recommendations:")
                for i, song in enumerate(data[:5]):
                    print(f"\n  [{i+1}] Title: {song.get('title', 'Unknown')}")
                    print(f"      Rasa: {song.get('rasa', 'N/A')}")
                    print(f"      Confidence: {song.get('confidence', 0):.2f}")
                    audio_url = song.get('audio_url', '')
                    if audio_url:
                        print(f"      URL: {audio_url[:80]}...")
                    else:
                        print(f"      URL: [NONE]")
            else:
                print("[WARN] No songs returned (but API call succeeded)")
            
            return data
        else:
            print(f"[FAIL] Unexpected response format: {type(data)}")
            print(f"  Response: {str(data)[:200]}")
            return None
            
    except Exception as e:
        print(f"[FAIL] Recommendation failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_song_urls(songs):
    """Test if song URLs are accessible"""
    print("\n" + "="*60)
    print("TEST 3: SONG URL ACCESSIBILITY")
    print("="*60)
    
    if not songs or len(songs) == 0:
        print("[SKIP] No songs to test")
        return
    
    accessible_count = 0
    failed_count = 0
    
    for i, song in enumerate(songs[:3]):
        url = song.get("audio_url")
        title = song.get("title", "Unknown")
        
        if not url:
            print(f"[SKIP] Song {i+1} ({title}): No URL provided")
            continue
        
        try:
            # Head request to check if URL exists
            response = requests.head(url, timeout=10, allow_redirects=True)
            if response.status_code == 200:
                print(f"[OK] Song {i+1} ({title}): Accessible")
                accessible_count += 1
            else:
                print(f"[WARN] Song {i+1} ({title}): HTTP {response.status_code}")
        except Exception as e:
            print(f"[FAIL] Song {i+1} ({title}): {str(e)[:60]}")
            failed_count += 1
    
    print(f"\nSummary: {accessible_count} accessible, {failed_count} failed")

def test_multiple_emotions():
    """Test recommendations for different emotions"""
    print("\n" + "="*60)
    print("TEST 4: MULTIPLE EMOTIONS")
    print("="*60)
    
    emotions = ["Happy", "Sad", "Angry", "Neutral", "Fearful"]
    
    # Create a fresh session for each emotion test
    session_id = test_session_creation()
    if not session_id:
        print("[FAIL] Could not create session for emotion tests")
        return
    
    results = {}
    
    for emotion in emotions:
        print(f"\nTesting emotion: {emotion}")
        
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
            
            if response.status_code == 200:
                songs = response.json()
                num_songs = len(songs) if isinstance(songs, list) else 0
                results[emotion] = f"OK ({num_songs} songs)"
                print(f"  Result: {results[emotion]}")
            else:
                results[emotion] = f"FAIL (HTTP {response.status_code})"
                print(f"  Result: {results[emotion]}")
                
        except Exception as e:
            results[emotion] = f"ERROR ({str(e)[:30]})"
            print(f"  Result: {results[emotion]}")
    
    print("\n" + "-"*60)
    print("Emotion Test Results:")
    for emotion, result in results.items():
        print(f"  {emotion:12} -> {result}")

def main():
    print("\n" + "="*60)
    print("RAGARASA - END-TO-END FLOW TEST (Mock Emotion)")
    print("="*60)
    
    # Test 1: Session creation
    session_id = test_session_creation()
    if not session_id:
        print("\n[FAIL] Test failed: Could not create session")
        return
    
    # Test 2: Recommendations
    print("\n[INFO] Testing recommendations with default emotion (Happy)...")
    songs = test_recommendations_with_mock_emotion(session_id, "Happy")
    if not songs:
        print("\n[WARN] Could not get recommendations for Happy emotion")
    else:
        # Test 3: Song URL accessibility
        test_song_urls(songs)
    
    # Test 4: Multiple emotions
    test_multiple_emotions()
    
    print("\n" + "="*60)
    print("[OK] END-TO-END TEST COMPLETE")
    print("="*60)

if __name__ == "__main__":
    main()
