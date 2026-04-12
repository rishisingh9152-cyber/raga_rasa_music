#!/usr/bin/env python
"""Test password verification methods"""

from pymongo import MongoClient

MONGODB_URL = "mongodb+srv://Rishi123:Rishi_123@majorproject.lpwzhzc.mongodb.net/raga_rasa_db?retryWrites=true&w=majority"

client = MongoClient(MONGODB_URL)
db = client["raga_rasa_db"]

user = db.users.find_one({"email": "rishisingh9152@gmail.com"})

if user:
    plain_password = "rishisingh"
    stored_password = user.get("password")
    
    print(f"[*] Testing password verification...")
    print(f"    Plain password:   '{plain_password}'")
    print(f"    Stored password:  '{stored_password}'")
    print(f"    Match: {plain_password == stored_password}")
    print()
    
    # Test all methods
    print("[*] Method 1: Plain text comparison")
    result = plain_password == stored_password
    print(f"    Result: {result}")
    
    print()
    print("[*] Method 2: Try passlib")
    try:
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        result = pwd_context.verify(plain_password, stored_password)
        print(f"    Result: {result}")
    except Exception as e:
        print(f"    Error: {e}")
    
    print()
    print("[*] Method 3: Try bcrypt")
    try:
        import bcrypt
        result = bcrypt.checkpw(plain_password.encode('utf-8'), stored_password.encode('utf-8'))
        print(f"    Result: {result}")
    except Exception as e:
        print(f"    Error: {e}")
        
else:
    print("[ERROR] User not found!")

client.close()
