#!/usr/bin/env python3
"""Test script to verify MongoDB Atlas connection and get sample songs"""

import asyncio
import json
from motor.motor_asyncio import AsyncIOMotorClient

async def test_mongodb_and_get_songs():
    """Connect to MongoDB Atlas and retrieve sample songs"""
    
    # MongoDB Atlas connection string
    mongo_url = "mongodb+srv://Rishi123:Rishi_123@majorproject.lpwzhzc.mongodb.net/?appName=MajorProject"
    
    client = AsyncIOMotorClient(mongo_url, serverSelectionTimeoutMS=15000)
    db = client["raga_rasa"]
    
    try:
        # Test connection with ping
        await client.admin.command('ping')
        
        # Count total songs
        total_songs = await db.songs.count_documents({})
        
        # Get all songs
        songs = await db.songs.find(
            {},
            {
                'title': 1,
                'audio_url': 1,
                'rasa': 1,
                'raag': 1,
                '_id': 1
            }
        ).to_list(None)
        
        return total_songs, songs
        
    except Exception as e:
        print(f"Error: {e}")
        return 0, None
        
    finally:
        client.close()

if __name__ == "__main__":
    total, songs = asyncio.run(test_mongodb_and_get_songs())
    
    if songs:
        # Save to JSON file
        output = {
            "total_songs": total,
            "sample_songs": []
        }
        
        for song in songs:
            output["sample_songs"].append({
                "title": song.get("title", "Unknown"),
                "rasa": song.get("rasa", "Unknown"),
                "raag": song.get("raag", "Unknown"),
                "audio_url": song.get("audio_url", ""),
                "_id": str(song.get("_id", ""))
            })
        
        # Write to file
        with open("mongodb_songs.json", "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"[OK] MongoDB Atlas connection verified!")
        print(f"[OK] Total songs in database: {total}")
        print(f"[OK] Songs saved to mongodb_songs.json")
