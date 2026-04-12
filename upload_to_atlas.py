#!/usr/bin/env python3
"""
Upload songs from local database to MongoDB Atlas (deployed database)
"""

import asyncio
import sys
sys.path.insert(0, r'C:\Users\rishi\raga_rasa_music\Backend')

from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def upload_songs_to_atlas():
    """
    Copy songs from local MongoDB to MongoDB Atlas
    """
    
    # Connect to local MongoDB
    print("Connecting to local MongoDB...")
    local_client = AsyncIOMotorClient("mongodb://localhost:27017")
    local_db = local_client["raga_rasa"]
    
    # Connect to MongoDB Atlas (deployed)
    print("Connecting to MongoDB Atlas...")
    atlas_url = "mongodb+srv://Rishi123:Rishi_123@majorproject.lpwzhzc.mongodb.net/?appName=MajorProject"
    atlas_client = AsyncIOMotorClient(atlas_url)
    atlas_db = atlas_client["raga_rasa"]
    
    try:
        # Get all songs from local database
        print("\nFetching songs from local MongoDB...")
        local_songs = await local_db.songs.find({}).to_list(None)
        print(f"Found {len(local_songs)} songs in local database")
        
        # Get count by rasa
        print("\nBreakdown by rasa:")
        for rasa in ["Shringar", "Shaant", "Veer", "Shok"]:
            count = await local_db.songs.count_documents({"rasa": rasa})
            print(f"  {rasa}: {count} songs")
        
        if len(local_songs) == 0:
            print("No songs found in local database!")
            return
        
        # Insert into MongoDB Atlas
        print(f"\nInserting {len(local_songs)} songs into MongoDB Atlas...")
        try:
            result = await atlas_db.songs.insert_many(local_songs, ordered=False)
            print(f"Successfully inserted {len(result.inserted_ids)} songs")
        except Exception as e:
            if "duplicate key" in str(e):
                print(f"Some songs already exist (duplicate key error), continuing...")
                # Delete existing songs and try again
                print("Deleting existing songs in Atlas...")
                await atlas_db.songs.delete_many({})
                
                result = await atlas_db.songs.insert_many(local_songs)
                print(f"Successfully inserted {len(result.inserted_ids)} songs after clearing")
            else:
                raise
        
        # Verify upload
        print("\nVerifying upload...")
        atlas_count = await atlas_db.songs.count_documents({})
        print(f"Total songs in MongoDB Atlas: {atlas_count}")
        
        print("\nBreakdown by rasa in Atlas:")
        for rasa in ["Shringar", "Shaant", "Veer", "Shok"]:
            count = await atlas_db.songs.count_documents({"rasa": rasa})
            print(f"  {rasa}: {count} songs")
        
        # Test sample song
        sample = await atlas_db.songs.find_one()
        if sample:
            print(f"\nSample song in Atlas:")
            print(f"  Title: {sample.get('title')}")
            print(f"  Rasa: {sample.get('rasa')}")
            print(f"  URL: {sample.get('audio_url')[:80]}...")
        
        print("\n✅ Songs successfully uploaded to MongoDB Atlas!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        local_client.close()
        atlas_client.close()

if __name__ == "__main__":
    asyncio.run(upload_songs_to_atlas())
