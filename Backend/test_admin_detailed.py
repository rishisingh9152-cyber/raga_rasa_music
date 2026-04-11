#!/usr/bin/env python3
"""
Test setup-admin with detailed error reporting
"""

import requests
import json

API = "http://localhost:8000/api"

print("Testing /api/setup-admin endpoint...")
print("-" * 50)

try:
    response = requests.post(
        f"{API}/setup-admin",
        json={
            "email": "rishisingh9152@gmail.com",
            "password": "Ripra@2622"
        },
        timeout=5
    )
    
    print(f"HTTP Status: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    print(f"Body: {response.text[:500]}")
    
    if response.status_code == 200:
        data = response.json()
        print("\nSUCCESS - Admin created!")
        print(f"User ID: {data['user']['user_id']}")
        print(f"Email: {data['user']['email']}")
        print(f"Role: {data['user']['role']}")
    elif response.status_code == 403:
        print("\nINFO - Admin already exists")
    elif response.status_code == 400:
        print("\nINFO - Email already registered")
    else:
        print(f"\nERROR - {response.status_code}")
        try:
            error_data = response.json()
            print(f"Error detail: {error_data}")
        except:
            print(f"Response text: {response.text}")
            
except requests.exceptions.ConnectionError as e:
    print(f"Connection error: {e}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
