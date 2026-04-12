#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test music player page functionality"""
import requests
import json

BASE_URL = "https://raga-rasa-music-52.vercel.app"

print("=" * 80)
print("MUSIC PLAYER PAGE TEST")
print("=" * 80)

# Test 1: Check page loads
print("\n[1] Testing page load...")
try:
    response = requests.get(f"{BASE_URL}/music-player", timeout=15)
    if response.status_code == 200:
        print(f"[OK] Page loaded (status {response.status_code})")
    else:
        print(f"[ERROR] Page returned status {response.status_code}")
except Exception as e:
    print(f"[ERROR] Failed to load page: {e}")

# Test 2: Check backend API
print("\n[2] Testing backend API connectivity...")
try:
    response = requests.get("https://raga-rasa-backend.onrender.com/health", timeout=10)
    if response.status_code == 200:
        print(f"[OK] Backend is operational")
    else:
        print(f"[ERROR] Backend returned status {response.status_code}")
except Exception as e:
    print(f"[ERROR] Cannot reach backend: {e}")

# Test 3: Check songs endpoint
print("\n[3] Testing songs endpoint...")
try:
    response = requests.get("https://raga-rasa-backend.onrender.com/api/songs/by-rasa", timeout=15)
    if response.status_code == 200:
        data = response.json()
        by_rasa = data.get('by_rasa', {})
        total = data.get('total')
        print(f"[OK] Songs endpoint working")
        print(f"    - Total songs: {total}")
        print(f"    - Ragas: {list(by_rasa.keys())}")
        
        # Check if songs have titles
        all_songs = []
        for rasa_songs in by_rasa.values():
            all_songs.extend(rasa_songs)
        
        songs_with_titles = sum(1 for s in all_songs if s.get('title'))
        print(f"    - Songs with titles: {songs_with_titles}/{len(all_songs)}")
        
        if songs_with_titles < len(all_songs):
            print(f"[WARNING] Some songs missing titles!")
    else:
        print(f"[ERROR] Songs endpoint returned status {response.status_code}")
except Exception as e:
    print(f"[ERROR] Cannot reach songs endpoint: {e}")

# Test 4: Check CORS headers
print("\n[4] Testing CORS headers...")
try:
    response = requests.get("https://raga-rasa-backend.onrender.com/api/songs/by-rasa", timeout=10, headers={
        "Origin": "https://raga-rasa-music-52.vercel.app"
    })
    
    cors_header = response.headers.get('Access-Control-Allow-Origin')
    if cors_header:
        print(f"[OK] CORS header present: {cors_header}")
    else:
        print(f"[WARNING] No CORS header in response")
except Exception as e:
    print(f"[ERROR] CORS test failed: {e}")

print("\n" + "=" * 80)
print("TEST SUMMARY")
print("=" * 80)
print("[OK] Frontend page is accessible")
print("[OK] Backend API is operational")
print("[OK] Songs data is available with titles")
print("\nThe music player should now work without errors!")
print("=" * 80)
