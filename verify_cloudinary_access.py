#!/usr/bin/env python3
"""
Verify Cloudinary access and find all uploaded files
"""

import requests
import json

def verify_cloudinary():
    print("\n" + "="*60)
    print("CLOUDINARY ACCESS VERIFICATION")
    print("="*60)
    
    # Cloudinary config
    cloud_name = "dlx3ufj3t"
    api_key = "255318353319693"
    api_secret = "MKFvdiyfmNpzxbaGKBMFM6SlT2c"
    
    # Test 1: Check account with ping
    print("\n[TEST 1] Account verification...")
    url = f"https://api.cloudinary.com/v1_1/{cloud_name}/usage"
    
    try:
        response = requests.get(url, auth=(api_key, api_secret), timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] Cloudinary account is accessible")
            print(f"  Account status: {data}")
        else:
            print(f"[FAIL] HTTP {response.status_code}")
            print(f"  Response: {response.text}")
    except Exception as e:
        print(f"[ERROR] {e}")
    
    # Test 2: List resources with different parameters
    print("\n[TEST 2] Listing all resources...")
    url = f"https://api.cloudinary.com/v1_1/{cloud_name}/resources"
    
    params = {
        "type": "upload",
        "max_results": 500,
        "resource_type": "video"  # Songs are audio/video
    }
    
    try:
        response = requests.get(url, params=params, auth=(api_key, api_secret), timeout=10)
        if response.status_code == 200:
            data = response.json()
            resources = data.get("resources", [])
            print(f"[OK] Found {len(resources)} video resources")
            if resources:
                for r in resources[:3]:
                    print(f"  - {r.get('public_id')}")
        else:
            print(f"[FAIL] HTTP {response.status_code}")
    except Exception as e:
        print(f"[ERROR] {e}")
    
    # Test 3: Try image resource type
    print("\n[TEST 3] Checking image resources...")
    params = {
        "type": "upload",
        "max_results": 100,
        "resource_type": "image"
    }
    
    try:
        response = requests.get(url, params=params, auth=(api_key, api_secret), timeout=10)
        if response.status_code == 200:
            data = response.json()
            resources = data.get("resources", [])
            print(f"[OK] Found {len(resources)} image resources")
    except Exception as e:
        print(f"[ERROR] {e}")
    
    # Test 4: List all files (no resource type filter)
    print("\n[TEST 4] Listing all files (any type)...")
    params = {
        "max_results": 100
    }
    
    try:
        response = requests.get(url, params=params, auth=(api_key, api_secret), timeout=10)
        if response.status_code == 200:
            data = response.json()
            resources = data.get("resources", [])
            print(f"[OK] Found {len(resources)} total resources")
            if resources:
                print(f"\n  File listing:")
                for i, r in enumerate(resources[:10]):
                    print(f"    [{i+1}] {r.get('public_id')} (type: {r.get('resource_type')})")
        else:
            print(f"[FAIL] HTTP {response.status_code}")
            print(f"  Response: {response.text[:500]}")
    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    verify_cloudinary()
