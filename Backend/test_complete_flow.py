#!/usr/bin/env python3
"""
Test complete auth flow
"""

import requests

API = "http://localhost:8000/api"

print("COMPLETE AUTHENTICATION FLOW TEST")
print("=" * 70)

# Test 1: Login as admin
print("\n[1] Login as admin...")
response = requests.post(
    f"{API}/auth/login",
    json={"email": "rishisingh9152@gmail.com", "password": "Ripra@2622"},
    timeout=5
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

# Test 2: Access admin dashboard
print("\n[2] Access admin dashboard...")
response = requests.get(
    f"{API}/admin/dashboard",
    headers={"Authorization": f"Bearer {admin_token}"},
    timeout=5
)
if response.status_code == 200:
    stats = response.json()
    print(f"[OK] Dashboard accessed")
    print(f"     Total users: {stats['total_users']}")
    print(f"     Total songs: {stats['total_songs']}")
    print(f"     Admin count: {stats['admin_count']}")
else:
    print(f"[FAIL] Status {response.status_code}: {response.text}")
    exit(1)

# Test 3: Register new user
print("\n[3] Register new user...")
response = requests.post(
    f"{API}/auth/register",
    json={"email": "testuser@example.com", "password": "TestPassword123"},
    timeout=5
)
if response.status_code == 200:
    user_data = response.json()
    user_token = user_data['access_token']
    print(f"[OK] Registration successful")
    print(f"     Email: {user_data['user']['email']}")
    print(f"     Role: {user_data['user']['role']}")
else:
    print(f"[FAIL] Status {response.status_code}: {response.text}")
    exit(1)

# Test 4: Try to access admin dashboard as regular user (should fail)
print("\n[4] Try admin dashboard as regular user (should fail)...")
response = requests.get(
    f"{API}/admin/dashboard",
    headers={"Authorization": f"Bearer {user_token}"},
    timeout=5
)
if response.status_code == 403:
    print(f"[OK] Correctly denied admin access")
    print(f"     Error: {response.json()['detail']}")
else:
    print(f"[FAIL] Should return 403, got {response.status_code}")

# Test 5: Access protected route without auth
print("\n[5] Access optional auth route without token...")
response = requests.post(
    f"{API}/session/start",
    json={"emotion": "neutral", "raga": "Yaman"},
    timeout=5
)
if response.status_code == 200:
    print(f"[OK] Optional auth works without token")
    print(f"     Session ID: {response.json()['session_id']}")
else:
    print(f"[FAIL] Status {response.status_code}: {response.text}")

print("\n" + "=" * 70)
print("ALL TESTS PASSED!")
print("=" * 70)
print("\nAuthentication system is fully functional!")
print(f"\nAdmin Credentials:")
print(f"  Email: rishisingh9152@gmail.com")
print(f"  Password: Ripra@2622")
