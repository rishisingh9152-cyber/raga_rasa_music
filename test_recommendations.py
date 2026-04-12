#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test recommendation endpoint with proper session setup"""
import requests
import json
import uuid

BASE_URL = "https://raga-rasa-backend.onrender.com"

def test_recommendation_with_session():
    """Test recommendation with proper session creation"""
    
    print("=" * 80)
    print("TESTING RECOMMENDATION WITH SESSION")
    print("=" * 80)
    
    # Generate a session ID
    session_id = str(uuid.uuid4())
    print(f"\nGenerated session_id: {session_id}")
    
    # Prepare cognitive data (with default values)
    cognitive_data = {
        "attention_span": 0.7,
        "emotional_regulation": 0.6,
        "stress_level": 0.5,
        "anxiety_level": 0.4,
        "mood": 0.7,
        "musical_affinity": 0.8,
        "relaxation_score": 0.5
    }
    
    # Test recommendations for different emotions
    emotions = ["happy", "sad", "neutral", "angry", "fearful"]
    
    for emotion in emotions:
        print(f"\n{'-' * 80}")
        print(f"Testing: {emotion.upper()} emotion")
        print(f"{'-' * 80}")
        
        payload = {
            "emotion": emotion,
            "session_id": session_id,
            "cognitive_data": cognitive_data
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/recommend/live",
                json=payload,
                timeout=15
            )
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                songs = response.json()
                print(f"[SUCCESS] Returned {len(songs)} songs")
                
                if songs:
                    print(f"\nFirst 3 recommendations:")
                    for i, song in enumerate(songs[:3], 1):
                        title = song.get('title', 'Unknown')
                        rasa = song.get('rasa', 'Unknown')
                        confidence = song.get('confidence', 0)
                        print(f"  {i}. {title} ({rasa}) - confidence: {confidence:.2f}")
                else:
                    print("No songs returned (empty list)")
            else:
                error_data = response.json()
                print(f"[ERROR] Status {response.status_code}")
                if isinstance(error_data, dict) and 'detail' in error_data:
                    print(f"Details: {error_data['detail'][:200]}")
                else:
                    print(f"Response: {str(error_data)[:200]}")
        
        except requests.exceptions.Timeout:
            print("[TIMEOUT] Request timed out after 15 seconds")
        except Exception as e:
            print(f"[EXCEPTION] {type(e).__name__}: {e}")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    test_recommendation_with_session()
