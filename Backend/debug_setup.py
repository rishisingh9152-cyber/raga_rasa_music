#!/usr/bin/env python3
"""
Debug script to test setup-admin endpoint
"""

import requests
import json

API_BASE = "http://localhost:8000/api"

try:
    response = requests.post(
        f"{API_BASE}/setup-admin",
        json={
            "email": "rishisingh9152@gmail.com",
            "password": "Ripra@2622"
        },
        timeout=5
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("\n✓ Success!")
    elif response.status_code == 403:
        print("\n✓ Admin already exists (expected if already created)")
    elif response.status_code == 400:
        print("\n✓ Email already registered")
    else:
        print(f"\n✗ Error: {response.status_code}")
        print("Trying to get more details...")
        try:
            print(json.dumps(response.json(), indent=2))
        except:
            print(response.text)
            
except Exception as e:
    print(f"Failed to connect: {str(e)}")
