#!/usr/bin/env python3
"""
Test script to verify RagaRasa backend deployment on Render
"""

import requests
import json
import sys

BASE_URL = "https://raga-rasa-backend.onrender.com"
TIMEOUT = 10

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=TIMEOUT)
        print(f"  Status: {response.status_code}")
        print(f"  Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"  Error: {e}")
        return False

def test_recommendations():
    """Test recommendations endpoint"""
    print("\nTesting recommendations endpoint...")
    try:
        # Try to get recommendations for a happy emotion
        payload = {
            "emotion": "happy",
            "session_id": "test-session",
            "cognitive_data": {
                "memory_score": 4,
                "reaction_time": 250,
                "accuracy_score": 85
            }
        }
        response = requests.post(
            f"{BASE_URL}/api/recommend/live",
            json=payload,
            timeout=TIMEOUT
        )
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  Returned {len(data)} recommendations")
            if data:
                first = data[0]
                print(f"  First song: {first.get('song_name', 'N/A')}")
                print(f"  Has streaming_url: {'streaming_url' in first}")
                return True
        else:
            print(f"  Response: {response.text}")
        return False
    except Exception as e:
        print(f"  Error: {e}")
        return False

def test_songs():
    """Test songs endpoint"""
    print("\nTesting songs endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/catalog/ragas/list", timeout=TIMEOUT)
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            num_songs = len(data)
            print(f"  Returned {num_songs} ragas/songs")
            if num_songs > 0:
                first = data[0]
                print(f"  First song: {first.get('song_name', 'N/A')}")
                print(f"  Has streaming_url: {'streaming_url' in first}")
            return num_songs > 0
        else:
            print(f"  Response: {response.text}")
        return False
    except Exception as e:
        print(f"  Error: {e}")
        return False

def main():
    print(f"Testing RagaRasa Backend: {BASE_URL}")
    print("=" * 60)
    
    results = {
        "Health": test_health(),
        "Recommendations": test_recommendations(),
        "Songs": test_songs()
    }
    
    print("\n" + "=" * 60)
    print("SUMMARY:")
    for test_name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] - {test_name}")
    
    all_passed = all(results.values())
    print("\n" + ("All tests passed!" if all_passed else "Some tests failed"))
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
