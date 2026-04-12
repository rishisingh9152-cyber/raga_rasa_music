#!/usr/bin/env python
"""Create admin user with plain text password for testing"""

from pymongo import MongoClient
from datetime import datetime

MONGODB_URL = "mongodb+srv://Rishi123:Rishi_123@majorproject.lpwzhzc.mongodb.net/raga_rasa_db?retryWrites=true&w=majority"

try:
    print("[*] Connecting to MongoDB Atlas...")
    client = MongoClient(MONGODB_URL)
    db = client["raga_rasa_db"]
    
    # Delete existing admin user
    print("[*] Deleting existing admin user...")
    result = db.users.delete_one({"email": "rishisingh9152@gmail.com"})
    print(f"    Deleted: {result.deleted_count}")
    
    # Create new admin user with PLAIN TEXT password (for testing)
    print("[*] Creating admin user with plain text password...")
    admin_user = {
        "user_id": "admin_001",
        "email": "rishisingh9152@gmail.com",
        "password": "rishisingh",  # Plain text password
        "first_name": "Rishi",
        "last_name": "Singh",
        "role": "admin",
        "is_active": True,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    
    result = db.users.insert_one(admin_user)
    print(f"[OK] Admin user created!")
    print(f"    Email: rishisingh9152@gmail.com")
    print(f"    Password: rishisingh (PLAIN TEXT - for testing only)")
    print(f"    ID: {result.inserted_id}")
    
    client.close()
    print("[OK] Done!")
    
except Exception as e:
    print(f"[ERROR] {str(e)}")
    import traceback
    traceback.print_exc()
