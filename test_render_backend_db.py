#!/usr/bin/env python3
"""Test if the Render backend can access MongoDB"""

import requests
import json

BASE_URL = "https://raga-rasa-backend.onrender.com"

# Test 1: Health check
print("Test 1: Health Check")
response = requests.get(f"{BASE_URL}/health")
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}\n")

# Test 2: Get ragas/songs list
print("Test 2: Get Ragas List")
response = requests.get(f"{BASE_URL}/api/catalog/ragas/list")
print(f"Status: {response.status_code}")
if response.status_code == 200:
    songs = response.json()
    print(f"Number of songs: {len(songs)}")
    if songs:
        print(f"First song: {json.dumps(songs[0], indent=2)[:300]}")
else:
    print(f"Error: {response.text}")

print("\n")

# Test 3: Try recommendations with proper format
print("Test 3: Recommendations")
payload = {
    "emotion": "happy",
    "session_id": "test-session-123",
    "cognitive_data": {
        "memory_score": 4,
        "reaction_time": 250,
        "accuracy_score": 85
    }
}
response = requests.post(f"{BASE_URL}/api/recommend/live", json=payload)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    recs = response.json()
    print(f"Number of recommendations: {len(recs) if isinstance(recs, list) else 0}")
    if isinstance(recs, list) and recs:
        print(f"First recommendation: {json.dumps(recs[0], indent=2)[:300]}")
else:
    print(f"Error: {response.text}")
