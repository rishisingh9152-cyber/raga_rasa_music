"""Initialize MongoDB collections and create admin user"""
import asyncio
from pymongo import MongoClient
from pymongo.errors import CollectionInvalid
from datetime import datetime

# MongoDB connection
MONGODB_URI = "mongodb+srv://Rishi123:Rishi_123@majorproject.lpwzhzc.mongodb.net/raga_rasa_db?retryWrites=true&w=majority"
DATABASE_NAME = "raga_rasa_db"

def create_admin_user(db):
    """Create admin user in MongoDB"""
    try:
        users_collection = db['users']
        
        admin_data = {
            "email": "rishisingh9152@gmail.com",
            "password": "rishisingh",
            "role": "admin",
            "created_at": datetime.utcnow(),
            "is_active": True
        }
        
        # Check if user already exists
        existing = users_collection.find_one({"email": admin_data["email"]})
        if existing:
            print(f"[OK] Admin user already exists: {admin_data['email']}")
            return existing
        
        # Insert new admin user
        result = users_collection.insert_one(admin_data)
        print(f"[OK] Admin user created successfully!")
        print(f"   Email: {admin_data['email']}")
        print(f"   Password: {admin_data['password']}")
        print(f"   Role: {admin_data['role']}")
        print(f"   ID: {result.inserted_id}")
        return admin_data
        
    except Exception as e:
        print(f"[ERROR] Failed to create admin user: {str(e)}")
        return None

def create_collections(db):
    """Create required collections"""
    try:
        required_collections = [
            'songs',
            'sessions',
            'ratings',
            'psychometric_tests',
            'images',
            'users',
            'context_scores'
        ]
        
        existing_collections = db.list_collection_names()
        print(f"Existing collections: {existing_collections}")
        print()
        
        for collection_name in required_collections:
            if collection_name not in existing_collections:
                try:
                    db.create_collection(collection_name)
                    print(f"[OK] Created collection: {collection_name}")
                except CollectionInvalid:
                    print(f"[INFO] Collection already exists: {collection_name}")
            else:
                print(f"[INFO] Collection already exists: {collection_name}")
        
        print()
        print(f"All required collections are ready!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to create collections: {str(e)}")
        return False

def main():
    """Main initialization function"""
    try:
        print("=" * 60)
        print("MongoDB Initialization & Admin Setup")
        print("=" * 60)
        print()
        
        print(f"Connecting to MongoDB Atlas...")
        print(f"URI: {MONGODB_URI[:50]}...")
        print()
        
        # Connect to MongoDB
        client = MongoClient(MONGODB_URI)
        db = client[DATABASE_NAME]
        
        # Test connection
        try:
            client.admin.command('ping')
            print(f"[OK] Connected to MongoDB Atlas successfully!")
            print()
        except Exception as e:
            print(f"[ERROR] Failed to connect: {str(e)}")
            return False
        
        # Create collections
        print("Creating required collections...")
        print("-" * 60)
        if not create_collections(db):
            return False
        
        print()
        print("Creating admin user...")
        print("-" * 60)
        create_admin_user(db)
        
        print()
        print("=" * 60)
        print("[OK] Initialization Complete!")
        print("=" * 60)
        print()
        print("You can now:")
        print("1. Login with email: rishisingh9152@gmail.com")
        print("2. Password: rishi_123")
        print("3. All collections are ready in MongoDB Atlas (MajorProject)")
        print()
        
        # Close connection
        client.close()
        return True
        
    except Exception as e:
        print(f"[ERROR] Initialization failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
