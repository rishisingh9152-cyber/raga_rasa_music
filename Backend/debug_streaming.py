#!/usr/bin/env python3
"""Debug script for streaming endpoint"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from pathlib import Path

async def main():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['raga_rasa']
    
    # Get a song
    song = await db.songs.find_one({})
    
    if song:
        print("Sample song from DB:")
        print(f"  _id: {song.get('_id')}")
        print(f"  file_path: {song.get('file_path')}")
        print(f"  audio_url: {song.get('audio_url')}")
        
        # Test file path
        fp = Path(song.get('file_path'))
        print(f"  Path exists: {fp.exists()}")
        print(f"  Path: {fp}")
        
        # Now test the streaming endpoint
        print("\nTesting streaming with song_id:")
        song_id = song.get('_id')
        
        # Try to find by ID like the endpoint does
        found = await db.songs.find_one({"_id": song_id})
        print(f"  Found by _id: {found is not None}")
        if found:
            print(f"    file_path: {found.get('file_path')}")
    
    client.close()

asyncio.run(main())
