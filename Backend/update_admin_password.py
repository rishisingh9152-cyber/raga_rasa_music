#!/usr/bin/env python
"""Change admin password to 'rishisingh' in MongoDB"""

from pymongo import MongoClient
from datetime import datetime
import bcrypt

MONGODB_URL = "mongodb+srv://Rishi123:Rishi_123@majorproject.lpwzhzc.mongodb.net/raga_rasa_db?retryWrites=true&w=majority"

try:
    print("[*] Connecting to MongoDB Atlas...")
    client = MongoClient(MONGODB_URL)
    db = client["raga_rasa_db"]
    
    # Test connection
    client.admin.command('ping')
    print("[OK] Connected to MongoDB Atlas")
    
    # Hash the password 'rishisingh'
    password = "rishisingh"
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    print(f"[*] Password hashed: {hashed_password[:50]}...")
    
    # Update the admin user password
    print("[*] Updating admin user password...")
    result = db.users.update_one(
        {"email": "rishisingh9152@gmail.com"},
        {
            "$set": {
                "password": hashed_password,
                "updated_at": datetime.utcnow().isoformat()
            }
        }
    )
    
    if result.matched_count > 0:
        print(f"[OK] Admin user password updated!")
        print(f"    Email: rishisingh9152@gmail.com")
        print(f"    Password: rishisingh")
        print(f"    Modified documents: {result.modified_count}")
    else:
        print("[ERROR] Admin user not found!")
    
    client.close()
    print("[OK] Done!")
    
except Exception as e:
    print(f"[ERROR] {str(e)}")
    import traceback
    traceback.print_exc()
