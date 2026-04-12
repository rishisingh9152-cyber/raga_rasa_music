#!/usr/bin/env python
"""Check admin user and create properly hashed password"""

from pymongo import MongoClient
import bcrypt

MONGODB_URL = "mongodb+srv://Rishi123:Rishi_123@majorproject.lpwzhzc.mongodb.net/raga_rasa_db?retryWrites=true&w=majority"

client = MongoClient(MONGODB_URL)
db = client["raga_rasa_db"]

# Get admin user
user = db.users.find_one({"email": "rishisingh9152@gmail.com"})
if user:
    print("[*] Admin user found!")
    pwd = user.get("password")
    print(f"Current password: {pwd}")
    
    # Test if plain text
    if pwd == "rishisingh":
        print("[OK] Password is plain text")
        
        # Now hash it with bcrypt
        hashed = bcrypt.hashpw(b"rishisingh", bcrypt.gensalt()).decode()
        print(f"[*] Hashed password: {hashed}")
        
        # Update in database
        db.users.update_one(
            {"email": "rishisingh9152@gmail.com"},
            {"$set": {"password": hashed}}
        )
        print("[OK] Updated password in database!")
        
        # Verify it works
        if bcrypt.checkpw(b"rishisingh", hashed.encode()):
            print("[OK] Verification successful!")
    else:
        print(f"[*] Password is: {pwd}")
else:
    print("[ERROR] Admin user not found!")

client.close()
