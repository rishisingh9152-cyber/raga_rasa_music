#!/usr/bin/env python3
"""
Test registration endpoint
"""

import requests

API = "http://localhost:8000/api"

print("Testing /api/auth/register endpoint...")
print("-" * 50)

try:
    response = requests.post(
        f"{API}/auth/register",
        json={
            "email": "testuser123@example.com",
            "password": "TestPassword123"
        },
        timeout=5
    )
    
    print(f"HTTP Status: {response.status_code}")
    print(f"Body: {response.text[:500]}")
    
    if response.status_code == 200:
        data = response.json()
        print("\nSUCCESS - User registered!")
        print(f"Email: {data['user']['email']}")
        print(f"Role: {data['user']['role']}")
    else:
        print(f"\nStatus: {response.status_code}")
            
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
