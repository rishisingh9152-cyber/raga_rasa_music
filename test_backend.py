#!/usr/bin/env python3
"""Quick backend test script"""

import subprocess
import time
import sys
import requests

def test_backend():
    print("Testing Backend Server...")
    print("=" * 60)
    
    # Try to import the app
    print("[1/3] Testing imports...")
    try:
        from Backend.main import app
        print("    ✓ Backend imports successfully")
    except Exception as e:
        print(f"    ✗ Backend import failed: {e}")
        return False
    
    # Test database connection
    print("[2/3] Testing database...")
    try:
        from Backend.app.database import get_db
        db = get_db()
        
        # Check collections
        collections = db.list_collection_names()
        expected_collections = ['songs', 'sessions', 'ratings', 'users', 'images', 'psychometric_tests', 'context_scores']
        missing = [c for c in expected_collections if c not in collections]
        
        if missing:
            print(f"    ✗ Missing collections: {missing}")
            return False
        
        # Count documents in key collections
        songs_count = db['songs'].count_documents({})
        sessions_count = db['sessions'].count_documents({})
        
        print(f"    ✓ Database connected (Songs: {songs_count}, Sessions: {sessions_count})")
        
        if songs_count == 0:
            print("    ⚠ No songs in database - you may need to run seed scripts")
            
    except Exception as e:
        print(f"    ✗ Database test failed: {e}")
        return False
    
    # Test API schema
    print("[3/3] Testing API schema...")
    try:
        from Backend.app.models import (
            SessionCreateSchema, SessionSchema, CognitiveDataSchema,
            EmotionDetectSchema, FeedbackSchema, SongSchema, RatingSchema,
            PsychometricTestSchema
        )
        print("    ✓ All Pydantic models load successfully")
    except Exception as e:
        print(f"    ✗ Schema test failed: {e}")
        return False
    
    print("=" * 60)
    print("✓ All backend tests passed!")
    print("\nYou can now start the backend server with:")
    print("  cd Backend && python main.py")
    print("\nOr start the frontend with:")
    print("  cd raga-rasa-soul-main && npm run dev")
    
    return True

if __name__ == "__main__":
    success = test_backend()
    sys.exit(0 if success else 1)
