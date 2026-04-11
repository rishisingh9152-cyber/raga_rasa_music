#!/usr/bin/env python3
"""
Setup admin user with your credentials
"""

import asyncio
import httpx
from datetime import datetime

API_BASE_URL = "http://localhost:8080/api"


async def setup_admin():
    """Create admin user"""
    
    email = "rishisingh9152@gmail.com"
    password = "Ripra@2622"
    
    print("=" * 70)
    print("SETTING UP ADMIN USER")
    print("=" * 70)
    print(f"\nEmail: {email}")
    print(f"Password: {'*' * len(password)}")
    print(f"Timestamp: {datetime.now().isoformat()}\n")
    
    async with httpx.AsyncClient() as client:
        try:
            print("Attempting to create admin...")
            response = await client.post(
                f"{API_BASE_URL}/setup-admin",
                json={
                    "email": email,
                    "password": password
                },
                timeout=10.0
            )
            
            print(f"\nResponse Status: {response.status_code}")
            print("-" * 70)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ SUCCESS - Admin user created!")
                print("\nDetails:")
                print(f"  User ID: {data['user']['user_id']}")
                print(f"  Email: {data['user']['email']}")
                print(f"  Role: {data['user']['role']}")
                print(f"  Token Type: {data['token_type']}")
                print(f"\nToken (first 50 chars): {data['access_token'][:50]}...")
                print("\n" + "=" * 70)
                print("🎉 YOU ARE NOW AN ADMIN!")
                print("=" * 70)
                print("\nYou can now:")
                print("  1. Login at http://localhost:5173/login")
                print("  2. Access admin dashboard at http://localhost:5173/admin")
                print("  3. Manage users and songs")
                print("  4. View system statistics")
                print("\n" + "=" * 70)
                return True
                
            elif response.status_code == 403:
                data = response.json()
                print("⚠️  Admin already exists!")
                print(f"Error: {data['detail']}")
                print("\nTo login as admin, use:")
                print(f"  Email: {email}")
                print(f"  Password: {'*' * len(password)}")
                print("\nGo to: http://localhost:5173/login")
                return False
                
            elif response.status_code == 400:
                data = response.json()
                print("❌ ERROR - Bad Request")
                print(f"Error: {data['detail']}")
                return False
                
            else:
                print(f"❌ ERROR - Unexpected status code")
                print(f"Response: {response.text}")
                return False
                
        except httpx.ConnectError:
            print("❌ ERROR - Cannot connect to backend")
            print("\nMake sure backend is running:")
            print("  cd Backend")
            print("  python main.py")
            print("\nOr with uvicorn:")
            print("  uvicorn main:app --host 0.0.0.0 --port 8080")
            return False
            
        except httpx.TimeoutException:
            print("❌ ERROR - Request timeout")
            print("Backend is not responding. Check if it's running.")
            return False
            
        except Exception as e:
            print(f"❌ ERROR - {str(e)}")
            return False


if __name__ == "__main__":
    success = asyncio.run(setup_admin())
    exit(0 if success else 1)
