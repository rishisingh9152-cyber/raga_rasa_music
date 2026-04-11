#!/usr/bin/env python3
"""
Test register function directly
"""

import asyncio
from app.models import RegisterSchema
from app.dependencies.auth import get_password_hash, create_access_token
from app.database import get_db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_register():
    print("Testing register logic...")
    
    # Step 1: Hash password
    print("1. Testing password hash...")
    hashed = get_password_hash("TestPassword123")
    print(f"   [OK] Password hashed: {hashed[:30]}...")
    
    # Step 2: Create token
    print("2. Testing token creation...")
    token = create_access_token("user-123", "test@example.com", "user")
    print(f"   [OK] Token created: {token[:50]}...")
    
    # Step 3: Create register schema
    print("3. Testing RegisterSchema...")
    schema = RegisterSchema(email="test@example.com", password="TestPassword123")
    print(f"   [OK] Schema created")
    
    # Step 4: Get database
    print("4. Testing database...")
    db = get_db()
    print(f"   [OK] Database connection: {type(db)}")
    
    # Step 5: Try inserting a test document
    print("5. Testing database insert...")
    try:
        test_doc = {
            "email": "direct-test@example.com",
            "test": True
        }
        result = await db.users.insert_one(test_doc)
        print(f"   [OK] Insert successful: {result.inserted_id}")
        
        # Clean up
        await db.users.delete_one({"_id": result.inserted_id})
        print(f"   [OK] Cleanup successful")
    except Exception as e:
        print(f"   [FAIL] Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_register())
