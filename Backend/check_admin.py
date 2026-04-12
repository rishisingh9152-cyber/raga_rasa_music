#!/usr/bin/env python
"""Check admin user in MongoDB"""

from pymongo import MongoClient

MONGODB_URL = "mongodb+srv://Rishi123:Rishi_123@majorproject.lpwzhzc.mongodb.net/raga_rasa_db?retryWrites=true&w=majority"

try:
    client = MongoClient(MONGODB_URL)
    db = client["raga_rasa_db"]
    
    user = db.users.find_one({"email": "rishisingh9152@gmail.com"})
    
    if user:
        print("[OK] User found!")
        print(f"    user_id: {user.get('user_id')}")
        print(f"    email: {user.get('email')}")
        print(f"    role: {user.get('role')}")
        print(f"    password hash length: {len(user.get('password', ''))}")
        print(f"    password (first 50 chars): {user.get('password', '')[:50]}")
    else:
        print("[ERROR] User not found!")
    
    client.close()
except Exception as e:
    print(f"[ERROR] {str(e)}")
    import traceback
    traceback.print_exc()
