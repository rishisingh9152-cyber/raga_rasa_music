#!/usr/bin/env python3
"""
Test existing session endpoint
"""

import requests

API = "http://localhost:8000/api"

print("Testing /api/session/start endpoint...")
print("-" * 50)

try:
    response = requests.post(
        f"{API}/session/start",
        json={
            "emotion": "sadness",
            "raga": "Yaman"
        },
        timeout=5
    )
    
    print(f"HTTP Status: {response.status_code}")
    print(f"Response: {response.text[:300]}")
    
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
