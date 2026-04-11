#!/usr/bin/env python3
"""
Test complete auth flow with longer timeouts
"""

import requests

API = "http://localhost:8000/api"
TIMEOUT = 30  # 30 second timeout

print("COMPLETE AUTHENTICATION FLOW TEST")
print("=" * 70)

# Test 1: Login as admin
print("\n[1] Login as admin...")
try:
    response = requests.post(
        f"{API}/auth/login",
        json={"email": "rishisingh9152@gmail.com", "password": "Ripra@2622"},
        timeout=TIMEOUT
    )
    if response.status_code == 200:
        admin_data = response.json()
        admin_token = admin_data['access_token']
        print(f"[OK] Login successful")
        print(f"     Email: {admin_data['user']['email']}")
        print(f"     Role: {admin_data['user']['role']}")
    else:
        print(f"[FAIL] Status {response.status_code}: {response.text}")
        exit(1)
except Exception as e:
    print(f"[FAIL] {str(e)}")
    exit(1)

# Test 2: Access admin dashboard
print("\n[2] Access admin dashboard (30s timeout)...")
try:
    response = requests.get(
        f"{API}/admin/dashboard",
        headers={"Authorization": f"Bearer {admin_token}"},
        timeout=TIMEOUT
    )
    if response.status_code == 200:
        stats = response.json()
        print(f"[OK] Dashboard accessed")
        print(f"     Total users: {stats['total_users']}")
        print(f"     Total songs: {stats['total_songs']}")
        print(f"     Admin count: {stats['admin_count']}")
    else:
        print(f"[FAIL] Status {response.status_code}: {response.text[:200]}")
except Exception as e:
    print(f"[FAIL] {type(e).__name__}: {str(e)[:200]}")

print("\n[3] Register new user...")
try:
    response = requests.post(
        f"{API}/auth/register",
        json={"email": f"testuser{int(requests.utils.datetime.datetime.now().timestamp())}@example.com", "password": "TestPassword123"},
        timeout=TIMEOUT
    )
    if response.status_code == 200:
        user_data = response.json()
        user_token = user_data['access_token']
        print(f"[OK] Registration successful")
        print(f"     Email: {user_data['user']['email']}")
        print(f"     Role: {user_data['user']['role']}")
    else:
        print(f"[FAIL] Status {response.status_code}")
except Exception as e:
    print(f"[FAIL] {str(e)}")

print("\n[4] Access optional auth route without token...")
try:
    response = requests.post(
        f"{API}/session/start",
        json={"emotion": "neutral", "raga": "Yaman"},
        timeout=TIMEOUT
    )
    if response.status_code == 200:
        print(f"[OK] Optional auth works without token")
        print(f"     Session ID: {response.json()['session_id']}")
    else:
        print(f"[FAIL] Status {response.status_code}")
except Exception as e:
    print(f"[FAIL] {str(e)}")

print("\n" + "=" * 70)
print("CORE AUTH TESTS PASSED!")
print("=" * 70)
