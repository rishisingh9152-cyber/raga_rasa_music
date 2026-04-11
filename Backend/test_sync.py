#!/usr/bin/env python3
"""
Simple synchronous test script to create admin user and test auth flow
"""

import requests
import json
import time

API_BASE = "http://localhost:8000/api"

def test_setup_admin():
    """Test creating first admin user"""
    print("=" * 70)
    print("TESTING SETUP ADMIN")
    print("=" * 70)
    
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
        if response.status_code == 200:
            data = response.json()
            print("[OK] Admin created successfully!")
            print(f"Token: {data['access_token'][:50]}...")
            print(f"Role: {data['user']['role']}")
            return data['access_token']
        else:
            print(f"[ERROR] {response.text}")
            return None
    except Exception as e:
        print(f"[ERROR] Failed to connect: {str(e)}")
        print("Waiting a moment for server to be fully ready...")
        time.sleep(2)
        # Retry once
        try:
            response = requests.post(
                f"{API_BASE}/setup-admin",
                json={
                    "email": "rishisingh9152@gmail.com",
                    "password": "Ripra@2622"
                },
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                print("[OK] Admin created successfully (on retry)!")
                return data['access_token']
            else:
                print(f"[ERROR] {response.text}")
                return None
        except:
            print("[ERROR] Server is not ready yet. Please ensure backend is running on port 8000")
            return None

def test_register_user(token=None):
    """Test user registration"""
    print("\n" + "=" * 70)
    print("TESTING USER REGISTRATION")
    print("=" * 70)
    
    try:
        response = requests.post(
            f"{API_BASE}/auth/register",
            json={
                "email": "testuser@example.com",
                "password": "TestPassword123!"
            },
            timeout=5
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("[OK] User registered successfully!")
            print(f"Email: {data['user']['email']}")
            print(f"Role: {data['user']['role']}")
            return data['access_token']
        else:
            print(f"[ERROR] {response.text}")
            return None
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return None

def test_login(email, password):
    """Test user login"""
    print("\n" + "=" * 70)
    print("TESTING USER LOGIN")
    print("=" * 70)
    
    try:
        response = requests.post(
            f"{API_BASE}/auth/login",
            json={
                "email": email,
                "password": password
            },
            timeout=5
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("[OK] Login successful!")
            print(f"Email: {data['user']['email']}")
            print(f"Role: {data['user']['role']}")
            return data['access_token']
        else:
            print(f"[ERROR] {response.text}")
            return None
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return None

def test_admin_dashboard(token):
    """Test admin dashboard access"""
    print("\n" + "=" * 70)
    print("TESTING ADMIN DASHBOARD")
    print("=" * 70)
    
    try:
        response = requests.get(
            f"{API_BASE}/admin/dashboard",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("[OK] Dashboard accessed!")
            print(f"Total Users: {data['total_users']}")
            print(f"Total Songs: {data['total_songs']}")
            print(f"Total Sessions: {data['total_sessions']}")
            print(f"Completed Sessions: {data['completed_sessions']}")
            print(f"Average Rating: {data['avg_rating']}")
            print(f"Admin Count: {data['admin_count']}")
        else:
            print(f"[ERROR] {response.text}")
    except Exception as e:
        print(f"[ERROR] {str(e)}")

if __name__ == "__main__":
    print("\n")
    print("RAGA RASA SOUL - AUTHENTICATION SYSTEM TEST")
    print("=" * 70)
    
    # Test 1: Setup admin
    admin_token = test_setup_admin()
    
    if admin_token:
        # Test 2: Access admin dashboard
        test_admin_dashboard(admin_token)
        
        # Test 3: Register user
        user_token = test_register_user(admin_token)
        
        # Test 4: Login
        if user_token:
            login_token = test_login("testuser@example.com", "TestPassword123!")
    
    print("\n" + "=" * 70)
    print("AUTHENTICATION TESTS COMPLETE")
    print("=" * 70)
    print("\nAdmin credentials created:")
    print(f"  Email: rishisingh9152@gmail.com")
    print(f"  Password: Ripra@2622")
    print("\nYou can now:")
    print("  1. Login to the application at http://localhost:5173/login")
    print("  2. Access the admin dashboard at http://localhost:5173/admin")
    print("\n")
