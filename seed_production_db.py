#!/usr/bin/env python3
"""
Production seed script - populate MongoDB with songs from Cloudinary
This script is designed to work with the production MongoDB Atlas database
"""

import asyncio
import json
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

# Production MongoDB connection
MONGODB_URI = "mongodb+srv://Rishi123:Rishi_123@majorproject.lpwzhzc.mongodb.net/?appName=MajorProject"
DATABASE_NAME = "raga_rasa"

# Cloudinary configuration
CLOUDINARY_BASE_URL = "https://res.cloudinary.com/dlx3ufj3t/video/upload"
CLOUDINARY_FOLDER = "raga-rasa/songs"

# Song data structure - based on the folder structure
SONGS_DATA = {
    "Shaant": [
        {"title": "Raga Ahir Bhairav", "duration": 180},
        {"title": "Raga Bageshri", "duration": 240},
        {"title": "Raga Darbari", "duration": 300},
        {"title": "Raga Jaunpuri", "duration": 220},
        {"title": "Raga Patdeep", "duration": 200},
        {"title": "Raga Sarang", "duration": 250},
        {"title": "Raga Tilang", "duration": 210},
        {"title": "Raga Yaman", "duration": 260},
        # Add more songs based on your actual Cloudinary uploads
    ],
    "Shok": [
        {"title": "Raga Bihag", "duration": 280},
        {"title": "Raga Jaijaiwanti", "duration": 290},
        {"title": "Raga Malhar", "duration": 320},
        {"title": "Raga Multani", "duration": 270},
        {"title": "Raga Pilu", "duration": 250},
        # Add more songs
    ],
    "Shringar": [
        {"title": "Raga Bhimpalasi", "duration": 300},
        {"title": "Raga Khadaj", "duration": 280},
        {"title": "Raga Mishra Kafi", "duration": 260},
        # Add more songs
    ],
    "Veer": [
        {"title": "Raga Bhairav", "duration": 310},
        {"title": "Raga Brindabani Sarang", "duration": 290},
        {"title": "Raga Hansdhwani", "duration": 270},
        # Add more songs
    ]
}


async def seed_production_database():
    """Seed production MongoDB with songs"""
    
    client = None
    try:
        print("=" * 70)
        print("RagaRasa Music Therapy - Production Database Seeding")
        print("=" * 70)
        
        # Connect to production MongoDB
        print(f"\nConnecting to MongoDB Atlas...")
        client = AsyncIOMotorClient(MONGODB_URI)
        
        # Verify connection
        await client.admin.command('ping')
        db = client[DATABASE_NAME]
        print("[OK] Connected to MongoDB Atlas successfully")
        
        # Clear existing songs (optional - set to False to keep existing data)
        CLEAR_EXISTING = True
        if CLEAR_EXISTING:
            existing_count = await db.songs.count_documents({})
            if existing_count > 0:
                print(f"\nClearing {existing_count} existing songs...")
                await db.songs.delete_many({})
                print("[OK] Cleared existing songs")
        
        # Prepare songs data
        print(f"\nPreparing songs data...")
        total_songs = 0
        songs_to_insert = []
        
        for rasa, songs in SONGS_DATA.items():
            for i, song_data in enumerate(songs, 1):
                # Create song document
                song_doc = {
                    "_id": f"{rasa.lower()}_{i}",  # Unique ID
                    "song_id": f"{rasa.lower()}_{i}",
                    "song_name": song_data["title"],
                    "title": song_data["title"],
                    "rasa": rasa,
                    "duration": song_data.get("duration", 300),
                    "avg_rating": 0.0,
                    "num_users": 0,
                    "created_at": datetime.utcnow().isoformat(),
                    "streaming_url": f"{CLOUDINARY_BASE_URL}/{CLOUDINARY_FOLDER}/{rasa}/{rasa.lower()}_{i}.mp3",
                    "cloudinary_url": f"{CLOUDINARY_BASE_URL}/{CLOUDINARY_FOLDER}/{rasa}/{rasa.lower()}_{i}.mp3",
                    "audio_url": f"{CLOUDINARY_BASE_URL}/{CLOUDINARY_FOLDER}/{rasa}/{rasa.lower()}_{i}.mp3",
                }
                songs_to_insert.append(song_doc)
                total_songs += 1
        
        print("[OK] Prepared {} songs".format(total_songs))
        
        # Insert songs
        print(f"\nInserting songs into MongoDB...")
        if songs_to_insert:
            result = await db.songs.insert_many(songs_to_insert)
            print("[OK] Inserted {} songs".format(len(result.inserted_ids)))
        
        # Verify insertion
        print(f"\nVerifying insertion...")
        for rasa in SONGS_DATA.keys():
            count = await db.songs.count_documents({"rasa": rasa})
            print(f"  {rasa}: {count} songs")
        
        total_count = await db.songs.count_documents({})
        print(f"  Total: {total_count} songs in database")
        
        # Show sample song
        sample = await db.songs.find_one()
        if sample:
            print(f"\nSample song structure:")
            print(json.dumps({k: v for k, v in sample.items() if k != "_id"}, indent=2))
        
        print("\n" + "=" * 70)
        print("Database seeding completed successfully!")
        print("=" * 70)
        
    except Exception as e:
        print("\n[ERROR] Error: {}".format(e))
        import traceback
        traceback.print_exc()
        return False
    finally:
        if client:
            client.close()
    
    return True


if __name__ == "__main__":
    success = asyncio.run(seed_production_database())
    exit(0 if success else 1)
