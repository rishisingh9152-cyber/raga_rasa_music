#!/usr/bin/env python
"""Create a test user with simple password"""

from pymongo import MongoClient
from datetime import datetime

MONGODB_URL = "mongodb+srv://Rishi123:Rishi_123@majorproject.lpwzhzc.mongodb.net/raga_rasa_db?retryWrites=true&w=majority"

client = MongoClient(MONGODB_URL)
db = client["raga_rasa_db"]

test_user = {
    "user_id": "test_user_001",
    "email": "test@raga.com",
    "password": "test123",
    "role": "admin",
    "created_at": datetime.utcnow().isoformat(),
    "updated_at": datetime.utcnow().isoformat()
}

result = db.users.insert_one(test_user)
print(f"[OK] Test user created!")
print(f"    Email: test@raga.com")
print(f"    Password: test123")

client.close()
