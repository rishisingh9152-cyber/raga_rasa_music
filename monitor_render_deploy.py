#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Monitor Render backend for successful redeploy of fixes"""
import requests
import time
import json
from datetime import datetime

BASE_URL = "https://raga-rasa-backend.onrender.com"

def test_db_test():
    """Test if /db-test endpoint works (no longer returns 405)"""
    try:
        response = requests.get(f"{BASE_URL}/db-test", timeout=10)
        return response.status_code, response.json() if response.status_code == 200 else response.text
    except Exception as e:
        return None, str(e)

def test_songs_by_rasa():
    """Test if /api/songs/by-rasa endpoint works"""
    try:
        response = requests.get(f"{BASE_URL}/api/songs/by-rasa", timeout=10)
        if response.status_code == 200:
            data = response.json()
            return 200, f"Total songs: {data.get('total', 0)}, by_rasa keys: {list(data.get('by_rasa', {}).keys())}"
        return response.status_code, response.text[:200]
    except Exception as e:
        return None, str(e)

def test_recommendation():
    """Test if recommendation endpoint works"""
    try:
        # Test with happy emotion
        response = requests.post(
            f"{BASE_URL}/api/recommend/live",
            json={"emotion": "happy", "rasa_preference": None},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            song_count = len(data.get('songs', []))
            return 200, f"Returned {song_count} songs"
        return response.status_code, response.text[:200]
    except Exception as e:
        return None, str(e)

def main():
    """Monitor endpoints for successful redeploy"""
    print("=" * 70)
    print("RagaRasa Backend Redeploy Monitor")
    print("=" * 70)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Monitoring: {BASE_URL}\n")
    
    tests = [
        ("DB Test", test_db_test),
        ("Songs by Rasa", test_songs_by_rasa),
        ("Recommendation", test_recommendation),
    ]
    
    attempts = 0
    max_attempts = 40  # Check for up to 20 minutes (30 sec intervals)
    
    while attempts < max_attempts:
        attempts += 1
        print(f"\n--- Attempt {attempts}/{max_attempts} at {datetime.now().strftime('%H:%M:%S')} ---")
        
        all_success = True
        for test_name, test_func in tests:
            status, data = test_func()
            
            if status == 200:
                print(f"[OK] {test_name}: {data}")
            elif status == 405:
                print(f"[OLD CODE] {test_name}: Still running old code (405)")
                all_success = False
            elif status == 500:
                print(f"[SERVER ERROR] {test_name}: 500 error")
                all_success = False
            else:
                print(f"[ERROR] {test_name}: Status {status}")
                all_success = False
        
        if all_success and attempts > 2:  # Give it a couple checks
            print("\n" + "=" * 70)
            print("SUCCESS! All endpoints responding correctly!")
            print("=" * 70)
            return True
        
        if attempts < max_attempts:
            print("Waiting 30 seconds before next check...")
            time.sleep(30)
    
    print("\n" + "=" * 70)
    print("TIMEOUT: Render redeploy did not complete within 20 minutes")
    print("Manual action may be needed at https://dashboard.render.com")
    print("=" * 70)
    return False

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
