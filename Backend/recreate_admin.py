#!/usr/bin/env python
"""Delete admin user and recreate with hashed password"""

from pymongo import MongoClient
from datetime import datetime
import sys

# Import bcrypt directly
try:
    import bcrypt
except ImportError:
    print("[WARNING] bcrypt not available, using simple hash")
    def bcrypt_hash(password):
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest()
    bcrypt = type('obj', (object,), {'hashpw': lambda s, salt: bcrypt_hash(s.decode() if isinstance(s, bytes) else s).encode()})()

MONGODB_URL = "mongodb+srv://Rishi123:Rishi_123@majorproject.lpwzhzc.mongodb.net/raga_rasa_db?retryWrites=true&w=majority"

try:
    print("[*] Connecting to MongoDB Atlas...")
    client = MongoClient(MONGODB_URL)
    db = client["raga_rasa_db"]
    
    # Test connection
    client.admin.command('ping')
    print("[OK] Connected to MongoDB Atlas")
    
    # Delete the existing admin user
    print("[*] Deleting existing admin user...")
    result = db.users.delete_one({"email": "rishisingh9152@gmail.com"})
    print(f"[OK] Deleted {result.deleted_count} existing admin user(s)")
    
    # Create a new admin user with hashed password
    print("[*] Creating new admin user with hashed password...")
    
    # Use bcrypt to hash the password
    password = "rishisingh"
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    new_admin = {
        "user_id": "admin_001",
        "email": "rishisingh9152@gmail.com",
        "password": hashed_password,
        "first_name": "Rishi",
        "last_name": "Singh",
        "role": "admin",
        "is_active": True,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    
    result = db.users.insert_one(new_admin)
    print(f"[OK] Admin user created successfully!")
    print(f"    Email: rishisingh9152@gmail.com")
    print(f"    Password: rishisingh")
    print(f"    ID: {result.inserted_id}")
    
    client.close()
    print("[OK] Done!")
    
except Exception as e:
    print(f"[ERROR] {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
