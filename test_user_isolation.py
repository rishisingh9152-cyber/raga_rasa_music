#!/usr/bin/env python3
"""
Test script to verify user_id filtering in session endpoints
Tests that users only see their own sessions and not other users' sessions
"""

import requests
import json
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8080/api"
TEST_USER_1_EMAIL = "test_user_1@example.com"
TEST_USER_1_PASSWORD = "TestPass123!"
TEST_USER_2_EMAIL = "test_user_2@example.com"
TEST_USER_2_PASSWORD = "TestPass456!"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def register_user(email, password):
    """Register a new user"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/register",
            json={"email": email, "password": password}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] Registered {email}")
            print(f"   User ID: {data['user']['user_id']}")
            return data['access_token'], data['user']['user_id']
        elif response.status_code == 409:
            print(f"[WARN] User {email} already exists, logging in...")
            return login_user(email, password)
        else:
            print(f"[FAIL] Failed to register {email}: {response.status_code}")
            print(f"   Response: {response.text}")
            return None, None
    except Exception as e:
        print(f"[FAIL] Error registering {email}: {e}")
        return None, None

def login_user(email, password):
    """Login a user"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/login",
            json={"email": email, "password": password}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] Logged in {email}")
            print(f"   User ID: {data['user']['user_id']}")
            return data['access_token'], data['user']['user_id']
        else:
            print(f"[FAIL] Failed to login {email}: {response.status_code}")
            print(f"   Response: {response.text}")
            return None, None
    except Exception as e:
        print(f"[FAIL] Error logging in {email}: {e}")
        return None, None

def start_session(token, user_id):
    """Start a new session"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(
            f"{API_BASE_URL}/session/start",
            json={},
            headers=headers
        )
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] Started session for user {user_id}")
            print(f"   Session ID: {data['session_id']}")
            return data['session_id']
        else:
            print(f"[FAIL] Failed to start session: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"[FAIL] Error starting session: {e}")
        return None

def get_user_sessions(token, user_id):
    """Get all sessions for a user"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{API_BASE_URL}/sessions",
            headers=headers
        )
        if response.status_code == 200:
            data = response.json()
            sessions = data.get('sessions', [])
            print(f"[OK] Retrieved {len(sessions)} sessions for user {user_id}")
            return sessions
        else:
            print(f"[FAIL] Failed to get sessions: {response.status_code}")
            print(f"   Response: {response.text}")
            return []
    except Exception as e:
        print(f"[FAIL] Error getting sessions: {e}")
        return []

def test_session_isolation():
    """Test that users only see their own sessions"""
    print_section("TEST: User Session Isolation")
    
    # Register/Login two users
    print("\n[Step 1] Setting up test users...")
    token1, user1_id = register_user(TEST_USER_1_EMAIL, TEST_USER_1_PASSWORD)
    if not token1:
        print("[FAIL] Failed to setup user 1")
        return False
    
    token2, user2_id = register_user(TEST_USER_2_EMAIL, TEST_USER_2_PASSWORD)
    if not token2:
        print("[FAIL] Failed to setup user 2")
        return False
    
    print(f"\n[OK] Test users created:")
    print(f"   User 1: {user1_id} ({TEST_USER_1_EMAIL})")
    print(f"   User 2: {user2_id} ({TEST_USER_2_EMAIL})")
    
    # User 1 creates 2 sessions
    print("\n[Step 2] User 1 creating sessions...")
    user1_session1 = start_session(token1, user1_id)
    user1_session2 = start_session(token1, user1_id)
    if not user1_session1 or not user1_session2:
        print("[FAIL] Failed to create user 1 sessions")
        return False
    
    # User 2 creates 1 session
    print("\n[Step 3] User 2 creating session...")
    user2_session1 = start_session(token2, user2_id)
    if not user2_session1:
        print("[FAIL] Failed to create user 2 session")
        return False
    
    # User 1 retrieves their sessions
    print("\n[Step 4] User 1 retrieving their sessions...")
    user1_sessions = get_user_sessions(token1, user1_id)
    
    # User 2 retrieves their sessions
    print("\n[Step 5] User 2 retrieving their sessions...")
    user2_sessions = get_user_sessions(token2, user2_id)
    
    # Verify isolation
    print("\n[Step 6] Verifying session isolation...")
    isolation_ok = True
    
    # Check user 1 only sees their sessions
    user1_session_ids = [s['session_id'] for s in user1_sessions if s.get('session_id')]
    if user1_session1 not in user1_session_ids:
        print(f"[FAIL] User 1 cannot see their own session {user1_session1}")
        isolation_ok = False
    if user1_session2 not in user1_session_ids:
        print(f"[FAIL] User 1 cannot see their own session {user1_session2}")
        isolation_ok = False
    if user2_session1 in user1_session_ids:
        print(f"[FAIL] SECURITY BREACH: User 1 can see User 2's session {user2_session1}")
        isolation_ok = False
    
    # Check user 2 only sees their sessions
    user2_session_ids = [s['session_id'] for s in user2_sessions if s.get('session_id')]
    if user2_session1 not in user2_session_ids:
        print(f"[FAIL] User 2 cannot see their own session {user2_session1}")
        isolation_ok = False
    if user1_session1 in user2_session_ids:
        print(f"[FAIL] SECURITY BREACH: User 2 can see User 1's session {user1_session1}")
        isolation_ok = False
    if user1_session2 in user2_session_ids:
        print(f"[FAIL] SECURITY BREACH: User 2 can see User 1's session {user1_session2}")
        isolation_ok = False
    
    if isolation_ok:
        print("[OK] Session isolation verified:")
        print(f"   User 1 sees {len(user1_sessions)} sessions (expected >= 2)")
        print(f"   User 2 sees {len(user2_sessions)} sessions (expected >= 1)")
        print(f"   No cross-contamination detected")
    else:
        print("[FAIL] Session isolation test FAILED")
    
    return isolation_ok

def test_session_ownership():
    """Test that users cannot access other users' sessions by ID"""
    print_section("TEST: Session Ownership Verification")
    
    # Setup users
    print("\n[Step 1] Setting up test users...")
    token1, user1_id = register_user(f"owner_user_{datetime.now().timestamp()}@example.com", "TestPass123!")
    if not token1:
        print("[FAIL] Failed to setup user 1")
        return False
    
    token2, user2_id = register_user(f"intruder_user_{datetime.now().timestamp()}@example.com", "TestPass456!")
    if not token2:
        print("[FAIL] Failed to setup user 2")
        return False
    
    # User 1 creates a session
    print("\n[Step 2] User 1 creating a session...")
    session_id = start_session(token1, user1_id)
    if not session_id:
        print("[FAIL] Failed to create session")
        return False
    
    # User 1 should be able to access their session
    print("\n[Step 3] User 1 accessing their own session...")
    try:
        headers1 = {"Authorization": f"Bearer {token1}"}
        response = requests.get(f"{API_BASE_URL}/session/{session_id}", headers=headers1)
        if response.status_code == 200:
            print(f"[OK] User 1 can access their own session")
            user1_can_access = True
        else:
            print(f"[FAIL] User 1 cannot access their own session: {response.status_code}")
            user1_can_access = False
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        user1_can_access = False
    
    # User 2 should NOT be able to access User 1's session
    print("\n[Step 4] User 2 trying to access User 1's session...")
    try:
        headers2 = {"Authorization": f"Bearer {token2}"}
        response = requests.get(f"{API_BASE_URL}/session/{session_id}", headers=headers2)
        if response.status_code == 403:
            print(f"[OK] User 2 correctly denied access (403 Forbidden)")
            user2_denied = True
        elif response.status_code == 200:
            print(f"[FAIL] SECURITY BREACH: User 2 can access User 1's session!")
            user2_denied = False
        else:
            print(f"[WARN]  Unexpected status code: {response.status_code}")
            user2_denied = False
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        user2_denied = False
    
    ownership_ok = user1_can_access and user2_denied
    if ownership_ok:
        print("\n[OK] Session ownership verification passed")
    else:
        print("\n[FAIL] Session ownership test FAILED")
    
    return ownership_ok

def main():
    print("\n" + "="*60)
    print("  USER DATA ISOLATION TEST SUITE")
    print("  Testing that users only see their own session data")
    print("="*60)
    
    print("\n[INFO] Make sure MongoDB is running and the backend is accessible at:")
    print(f"   {API_BASE_URL}")
    
    results = []
    
    # Run tests
    test1 = test_session_isolation()
    results.append(("Session Isolation", test1))
    
    test2 = test_session_ownership()
    results.append(("Session Ownership", test2))
    
    # Summary
    print_section("TEST SUMMARY")
    for test_name, result in results:
        status = "[OK] PASS" if result else "[FAIL] FAIL"
        print(f"{test_name}: {status}")
    
    all_passed = all(r for _, r in results)
    print("\n" + "="*60)
    if all_passed:
        print("  [SUCCESS] ALL TESTS PASSED - User data isolation is working!")
    else:
        print("  [FAIL] SOME TESTS FAILED - Please review the output above")
    print("="*60 + "\n")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
