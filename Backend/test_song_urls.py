#!/usr/bin/env python3
"""Test script to check song audio URLs and file paths"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from pathlib import Path

async def check_song_details():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['raga_rasa']
    
    # Get first 5 songs
    songs = await db.songs.find({}).to_list(5)
    
    print("Song Details Test")
    print("=" * 80)
    print(f"Total songs in database: {await db.songs.count_documents({})}\n")
    
    for i, song in enumerate(songs, 1):
        print(f"Song {i}:")
        print(f"  ID: {song.get('_id', 'MISSING')}")
        print(f"  Title: {song.get('title', 'MISSING')}")
        print(f"  Audio URL: {song.get('audio_url', 'MISSING')}")
        print(f"  File Path: {song.get('file_path', 'MISSING')}")
        
        # Check if file exists
        file_path = song.get('file_path')
        if file_path:
            exists = Path(file_path).exists()
            print(f"  File Exists: {'YES' if exists else 'NO'}")
        print()

asyncio.run(check_song_details())
