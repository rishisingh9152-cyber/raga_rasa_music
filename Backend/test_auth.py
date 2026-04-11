#!/usr/bin/env python3
"""
Quick test script to verify authentication system works correctly
"""

import asyncio
import httpx
import json

API_BASE_URL = "http://localhost:8000/api"


async def test_auth_flow():
    """Test the complete authentication flow"""
    
    async with httpx.AsyncClient() as client:
        print("=" * 60)
        print("TESTING RAGA RASA SOUL AUTHENTICATION SYSTEM")
        print("=" * 60)
        
        # Test 1: Create first admin
        print("\n[1] Creating first admin via /setup-admin endpoint...")
        try:
            response = await client.post(
                f"{API_BASE_URL}/setup-admin",
                json={
                    "email": "admin@test.com",
                    "password": "SecurePassword123!"
                }
            )
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                admin_token = data['access_token']
                print(f"✓ Admin created successfully")
                print(f"  Token: {admin_token[:50]}...")
                print(f"  Role: {data['user']['role']}")
            else:
                print(f"✗ Failed: {response.text}")
                return
        except Exception as e:
            print(f"✗ Error: {str(e)}")
            return
        
        # Test 2: Try to create another admin (should fail)
        print("\n[2] Attempting to create second admin (should fail)...")
        try:
            response = await client.post(
                f"{API_BASE_URL}/setup-admin",
                json={
                    "email": "admin2@test.com",
                    "password": "SecurePassword123!"
                }
            )
            print(f"Status: {response.status_code}")
            if response.status_code == 403:
                print(f"✓ Correctly blocked: {response.json()['detail']}")
            else:
                print(f"✗ Unexpected response: {response.text}")
        except Exception as e:
            print(f"✗ Error: {str(e)}")
        
        # Test 3: Register a regular user
        print("\n[3] Registering a regular user...")
        try:
            response = await client.post(
                f"{API_BASE_URL}/auth/register",
                json={
                    "email": "user@test.com",
                    "password": "UserPassword123!"
                }
            )
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                user_token = data['access_token']
                print(f"✓ User registered successfully")
                print(f"  Token: {user_token[:50]}...")
                print(f"  Role: {data['user']['role']}")
            else:
                print(f"✗ Failed: {response.text}")
        except Exception as e:
            print(f"✗ Error: {str(e)}")
        
        # Test 4: Try to register duplicate email
        print("\n[4] Attempting to register duplicate email (should fail)...")
        try:
            response = await client.post(
                f"{API_BASE_URL}/auth/register",
                json={
                    "email": "user@test.com",
                    "password": "AnotherPassword123!"
                }
            )
            print(f"Status: {response.status_code}")
            if response.status_code == 400:
                print(f"✓ Correctly rejected: {response.json()['detail']}")
            else:
                print(f"✗ Unexpected response: {response.text}")
        except Exception as e:
            print(f"✗ Error: {str(e)}")
        
        # Test 5: Login with correct credentials
        print("\n[5] Login with correct credentials...")
        try:
            response = await client.post(
                f"{API_BASE_URL}/auth/login",
                json={
                    "email": "admin@test.com",
                    "password": "SecurePassword123!"
                }
            )
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Login successful")
                print(f"  User: {data['user']['email']}")
                print(f"  Role: {data['user']['role']}")
            else:
                print(f"✗ Failed: {response.text}")
        except Exception as e:
            print(f"✗ Error: {str(e)}")
        
        # Test 6: Login with wrong password
        print("\n[6] Login with wrong password (should fail)...")
        try:
            response = await client.post(
                f"{API_BASE_URL}/auth/login",
                json={
                    "email": "admin@test.com",
                    "password": "WrongPassword123!"
                }
            )
            print(f"Status: {response.status_code}")
            if response.status_code == 401:
                print(f"✓ Correctly rejected: {response.json()['detail']}")
            else:
                print(f"✗ Unexpected response: {response.text}")
        except Exception as e:
            print(f"✗ Error: {str(e)}")
        
        # Test 7: Access admin endpoint with admin token
        print("\n[7] Accessing /admin/dashboard with admin token...")
        try:
            response = await client.get(
                f"{API_BASE_URL}/admin/dashboard",
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Dashboard accessed successfully")
                print(f"  Total users: {data['total_users']}")
                print(f"  Total songs: {data['total_songs']}")
                print(f"  Total sessions: {data['total_sessions']}")
            else:
                print(f"✗ Failed: {response.text}")
        except Exception as e:
            print(f"✗ Error: {str(e)}")
        
        # Test 8: Access admin endpoint with user token (should fail)
        print("\n[8] Accessing /admin/dashboard with user token (should fail)...")
        try:
            response = await client.get(
                f"{API_BASE_URL}/admin/dashboard",
                headers={"Authorization": f"Bearer {user_token}"}
            )
            print(f"Status: {response.status_code}")
            if response.status_code == 403:
                print(f"✓ Correctly denied: {response.json()['detail']}")
            else:
                print(f"✗ Unexpected response: {response.text}")
        except Exception as e:
            print(f"✗ Error: {str(e)}")
        
        print("\n" + "=" * 60)
        print("AUTHENTICATION TESTS COMPLETE")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_auth_flow())
