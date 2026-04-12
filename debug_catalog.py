#!/usr/bin/env python3
"""Direct test of the catalog endpoint issue"""

import requests
import json

BACKEND_URL = "https://raga-rasa-backend.onrender.com"

# Test 1: Get ragas list
print("[TEST] GET /api/ragas/list")
try:
    resp = requests.get(f"{BACKEND_URL}/api/ragas/list", timeout=15)
    print(f"Status: {resp.status_code}")
    
    if resp.status_code == 200:
        data = resp.json()
        print(f"Success! Got {len(data)} songs")
        if data:
            print(f"First song: {data[0]}")
    else:
        print(f"Error response:")
        print(resp.text[:500])
except requests.Timeout:
    print("Request timed out")
except Exception as e:
    print(f"Exception: {e}")

print("\n" + "="*60 + "\n")

# Test 2: Check if the backend schema is wrong
print("[TEST] Check backend models")
try:
    resp = requests.get(f"{BACKEND_URL}/docs", timeout=10)
    if resp.status_code == 200:
        print("Swagger docs are accessible - check the /docs endpoint for schema info")
    else:
        print(f"Docs endpoint returned: {resp.status_code}")
except Exception as e:
    print(f"Error accessing docs: {e}")

print("\n" + "="*60 + "\n")

# Test 3: Direct backend info
print("[TEST] Backend root endpoint")
try:
    resp = requests.get(f"{BACKEND_URL}/", timeout=10)
    data = resp.json()
    print(json.dumps(data, indent=2))
except Exception as e:
    print(f"Error: {e}")
