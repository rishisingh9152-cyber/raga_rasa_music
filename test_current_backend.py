#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test the current Render backend deployment"""
import requests
import time
import sys
import os

# Force UTF-8 output on Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "https://raga-rasa-backend.onrender.com"
ENDPOINTS = [
    "/health",
    "/db-test",
    "/api/test/db-status",
    "/api/test/songs-count",
    "/api/ragas/simple",
    "/api/songs/by-rasa"
]

def test_endpoint(url, retries=3, initial_wait=5):
    """Test an endpoint with retries"""
    print(f"\nTesting {url}...")
    
    # Wait before first attempt
    print(f"Waiting {initial_wait}s for Render service...")
    time.sleep(initial_wait)
    
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=10)
            print(f"[OK] Status: {response.status_code}")
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"  Response: {data}")
                except:
                    print(f"  Response: {response.text[:200]}")
            return response.status_code
        except requests.exceptions.Timeout:
            print(f"[TIMEOUT] Timeout (attempt {attempt+1}/{retries})")
            if attempt < retries - 1:
                time.sleep(5)
        except requests.exceptions.ConnectionError as e:
            print(f"[ERROR] Connection error: {e} (attempt {attempt+1}/{retries})")
            if attempt < retries - 1:
                time.sleep(5)
        except Exception as e:
            print(f"[ERROR] Error: {e}")
            return None
    
    return None

if __name__ == "__main__":
    print("=" * 60)
    print("Testing Render Backend Deployment")
    print(f"Base URL: {BASE_URL}")
    print("=" * 60)
    
    results = {}
    for endpoint in ENDPOINTS:
        url = BASE_URL + endpoint
        status = test_endpoint(url, retries=2, initial_wait=0)
        results[endpoint] = status
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for endpoint, status in results.items():
        symbol = "[OK]" if status == 200 else "[FAIL]"
        print(f"{symbol} {endpoint}: {status}")
    
    # Check if any 200 responses
    success_count = sum(1 for s in results.values() if s == 200)
    print(f"\nSuccessful endpoints: {success_count}/{len(ENDPOINTS)}")
    
    sys.exit(0 if success_count > 0 else 1)
