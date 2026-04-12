#!/usr/bin/env python
"""Check admin user data types in MongoDB"""

from pymongo import MongoClient

MONGODB_URL = "mongodb+srv://Rishi123:Rishi_123@majorproject.lpwzhzc.mongodb.net/raga_rasa_db?retryWrites=true&w=majority"

try:
    client = MongoClient(MONGODB_URL)
    db = client["raga_rasa_db"]
    
    user = db.users.find_one({"email": "rishisingh9152@gmail.com"})
    
    if user:
        print("[*] Admin user data:")
        for key, value in user.items():
            if key == "password":
                print(f"    {key}:")
                print(f"        Type: {type(value)}")
                print(f"        Value: {value}")
                print(f"        Length: {len(value)}")
                print(f"        Repr: {repr(value)}")
            else:
                print(f"    {key}: {value} (type: {type(value).__name__})")
    else:
        print("[ERROR] User not found!")
    
    client.close()
except Exception as e:
    print(f"[ERROR] {str(e)}")
    import traceback
    traceback.print_exc()
