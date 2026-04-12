#!/usr/bin/env python
"""Test password verification with the newly hashed password"""

import bcrypt
from pymongo import MongoClient

MONGODB_URL = "mongodb+srv://Rishi123:Rishi_123@majorproject.lpwzhzc.mongodb.net/raga_rasa_db?retryWrites=true&w=majority"

client = MongoClient(MONGODB_URL)
db = client["raga_rasa_db"]

user = db.users.find_one({"email": "rishisingh9152@gmail.com"})

if user:
    hashed_from_db = user.get("password")
    plain_password = "rishisingh"
    
    print(f"[*] Hash from DB: {hashed_from_db}")
    print(f"[*] Plain password: {plain_password}")
    print()
    
    try:
        result = bcrypt.checkpw(plain_password.encode('utf-8'), hashed_from_db.encode('utf-8'))
        print(f"[OK] Bcrypt verification: {result}")
        if result:
            print("[OK] Password is correct!")
        else:
            print("[ERROR] Password is incorrect!")
    except Exception as e:
        print(f"[ERROR] Verification failed: {e}")
else:
    print("[ERROR] User not found!")

client.close()
