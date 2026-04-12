#!/usr/bin/env python
"""Test bcrypt verification with the new password hash"""

import bcrypt
from pymongo import MongoClient

MONGODB_URL = "mongodb+srv://Rishi123:Rishi_123@majorproject.lpwzhzc.mongodb.net/raga_rasa_db?retryWrites=true&w=majority"

try:
    print("[*] Testing bcrypt password verification...")
    
    client = MongoClient(MONGODB_URL)
    db = client["raga_rasa_db"]
    
    user = db.users.find_one({"email": "rishisingh9152@gmail.com"})
    
    if user:
        hashed_password = user.get("password", "")
        plain_password = "rishisingh"
        
        print(f"[*] Hash from DB: {hashed_password[:50]}...")
        print(f"[*] Testing with plain password: {plain_password}")
        print()
        
        # Test 1: Direct bcrypt check
        try:
            result = bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
            print(f"[Test 1] bcrypt.checkpw result: {result}")
        except Exception as e:
            print(f"[Test 1] Error: {e}")
        
        # Test 2: Try with bytes instead of string
        try:
            result = bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
            print(f"[Test 2] bcrypt.checkpw (bytes) result: {result}")
        except Exception as e:
            print(f"[Test 2] Error: {e}")
        
        # Test 3: Try using passlib
        try:
            from passlib.context import CryptContext
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            result = pwd_context.verify(plain_password, hashed_password)
            print(f"[Test 3] passlib verify result: {result}")
        except Exception as e:
            print(f"[Test 3] Error: {e}")
        
        print()
        print("[*] Checking hash format...")
        print(f"    Hash starts with: {hashed_password[:10]}")
        print(f"    Hash length: {len(hashed_password)}")
        
        if hashed_password.startswith('$2b$'):
            print("    ✓ Valid bcrypt hash format")
        else:
            print("    ✗ Invalid hash format!")
    else:
        print("[ERROR] User not found!")
    
    client.close()
    
except Exception as e:
    print(f"[ERROR] {str(e)}")
    import traceback
    traceback.print_exc()
