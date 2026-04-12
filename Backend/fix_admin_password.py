#!/usr/bin/env python
"""Fix admin user password - hash it properly"""

from pymongo import MongoClient
from datetime import datetime
import hashlib
import hmac

def hash_password(password: str) -> str:
    """Simple SHA256 hash for password"""
    # Use PBKDF2 style hashing
    salt = b'raga_rasa_salt'
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    return f"pbkdf2:sha256:100000${salt.hex()}${pwd_hash.hex()}"

MONGODB_URL = "mongodb+srv://Rishi123:Rishi_123@majorproject.lpwzhzc.mongodb.net/raga_rasa_db?retryWrites=true&w=majority"

try:
    client = MongoClient(MONGODB_URL)
    db = client["raga_rasa_db"]
    
    # Test connection
    client.admin.command('ping')
    print("[OK] Connected to MongoDB Atlas")
    
    # Hash the password
    hashed_pwd = hash_password("rishisingh")
    print(f"[OK] Password hashed successfully")
    
    # Update the admin user with hashed password
    result = db.users.update_one(
        {"email": "rishisingh9152@gmail.com"},
        {
            "$set": {
                "password": hashed_pwd,
                "updated_at": datetime.utcnow(),
                "first_name": "Rishi",
                "last_name": "Singh",
                "user_id": "admin_user_001"
            }
        }
    )
    
    if result.matched_count > 0:
        print(f"[OK] Admin user password has been updated!")
        print(f"    Modified: {result.modified_count} document(s)")
        print(f"    Email: rishisingh9152@gmail.com")
        print(f"    Password: rishisingh")
    else:
        print("[ERROR] Admin user not found!")
    
    client.close()
    print("[OK] Done!")
    
except Exception as e:
    print(f"[ERROR] {str(e)}")
    import traceback
    traceback.print_exc()
