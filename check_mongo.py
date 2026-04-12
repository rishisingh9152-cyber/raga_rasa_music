#!/usr/bin/env python3
"""Quick MongoDB connection test"""

from pymongo import MongoClient

uri = 'mongodb+srv://Rishi123:Rishi_123@majorproject.lpwzhzc.mongodb.net/?appName=MajorProject'

try:
    print("[Connecting to MongoDB...]")
    client = MongoClient(uri)
    db = client['raga_rasa']
    collection = db['songs']
    
    # Test connection
    client.admin.command('ping')
    print("[SUCCESS] Connected to MongoDB Atlas")
    
    # Count songs
    count = collection.count_documents({})
    print(f"[INFO] Total songs in database: {count}")
    
    # Get sample
    sample = collection.find_one()
    if sample:
        print(f"[INFO] Sample song: {sample.get('title')} - {sample.get('artist')}")
        print(f"[INFO] Rasa: {sample.get('rasa')}")
        print(f"[INFO] URL: {sample.get('url', 'N/A')[:60]}...")
    
    # Check distribution by rasa
    ragas = collection.distinct('rasa')
    print(f"[INFO] Ragas in database: {ragas}")
    
    for rasa in ragas:
        count = collection.count_documents({'rasa': rasa})
        print(f"  - {rasa}: {count} songs")
    
    client.close()
    
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
