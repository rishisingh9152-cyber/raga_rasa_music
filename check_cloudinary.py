#!/usr/bin/env python3
"""
Check what resources are actually in Cloudinary
"""

import requests

def check_cloudinary_resources():
    print("\n" + "="*60)
    print("CLOUDINARY RESOURCE CHECKER")
    print("="*60)
    
    # Cloudinary config
    cloud_name = "dlx3ufj3t"
    api_key = "255318353319693"
    api_secret = "MKFvdiyfmNpzxbaGKBMFM6SlT2c"
    
    url = f"https://api.cloudinary.com/v1_1/{cloud_name}/resources"
    
    # Try different prefixes
    prefixes_to_try = [
        "raga-rasa/songs",
        "raga-rasa",
        "songs",
        ""  # Get all
    ]
    
    for prefix in prefixes_to_try:
        print(f"\n[INFO] Checking prefix: '{prefix}'")
        
        params = {
            "type": "upload",
            "max_results": "500"
        }
        
        if prefix:
            params["prefix"] = prefix
        
        try:
            response = requests.get(url, params=params, auth=(api_key, api_secret), timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                resources = data.get("resources", [])
                print(f"[OK] Found {len(resources)} resources")
                
                if resources:
                    print(f"  First 5:")
                    for i, r in enumerate(resources[:5]):
                        print(f"    [{i+1}] {r.get('public_id')}")
            else:
                print(f"[FAIL] HTTP {response.status_code}: {response.text[:100]}")
                
        except Exception as e:
            print(f"[ERROR] {e}")

if __name__ == "__main__":
    check_cloudinary_resources()
