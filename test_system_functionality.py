#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test key system functionality after redeploy"""
import requests
import json

BASE_URL = "https://raga-rasa-backend.onrender.com"

print("=" * 70)
print("RagaRasa Backend Functionality Test")
print("=" * 70)

# Test 1: Health
print("\n[1] Testing /health endpoint...")
try:
    r = requests.get(f"{BASE_URL}/health", timeout=10)
    print(f"    Status: {r.status_code}")
    if r.status_code == 200:
        print(f"    Data: {r.json()}")
except Exception as e:
    print(f"    ERROR: {e}")

# Test 2: Database initialization
print("\n[2] Testing /db-test endpoint...")
try:
    r = requests.get(f"{BASE_URL}/db-test", timeout=10)
    print(f"    Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"    Data: {data}")
        if data.get("status") == "success" and data.get("total_songs") == 59:
            print("    ✓ Database initialized correctly!")
        else:
            print(f"    ✗ Unexpected response")
except Exception as e:
    print(f"    ERROR: {e}")

# Test 3: Songs by rasa
print("\n[3] Testing /api/songs/by-rasa endpoint...")
try:
    r = requests.get(f"{BASE_URL}/api/songs/by-rasa", timeout=10)
    print(f"    Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"    Total songs: {data.get('total')}")
        by_rasa = data.get('by_rasa', {})
        print(f"    By rasa: {[(k, len(v)) for k, v in by_rasa.items()]}")
        if data.get("total") == 59:
            print("    ✓ All songs retrieved!")
        else:
            print(f"    ✗ Expected 59 songs, got {data.get('total')}")
except Exception as e:
    print(f"    ERROR: {e}")

# Test 4: Recommendation endpoint
print("\n[4] Testing /api/recommend/live endpoint...")
try:
    r = requests.post(
        f"{BASE_URL}/api/recommend/live",
        json={"emotion": "happy", "rasa_preference": None},
        timeout=10
    )
    print(f"    Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        songs = data.get('songs', [])
        print(f"    Returned {len(songs)} songs for 'happy' emotion")
        if songs:
            print(f"    First song: {songs[0].get('title')}")
            print("    ✓ Recommendations working!")
        else:
            print("    ✗ No songs returned")
    else:
        print(f"    Response: {r.text[:200]}")
except Exception as e:
    print(f"    ERROR: {e}")

# Test 5: Songs by rasa filter
print("\n[5] Testing /api/songs/by-rasa?rasa=Shaant...")
try:
    r = requests.get(f"{BASE_URL}/api/songs/by-rasa?rasa=Shaant", timeout=10)
    print(f"    Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        total = data.get('total')
        print(f"    Shaant songs: {total}")
        if total > 0:
            print("    ✓ Rasa filter working!")
        else:
            print("    ✗ Filter not working")
except Exception as e:
    print(f"    ERROR: {e}")

print("\n" + "=" * 70)
print("Test completed!")
print("=" * 70)
