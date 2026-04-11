#!/usr/bin/env python3
"""Test the actual streaming endpoint"""

import asyncio
import requests
from motor.motor_asyncio import AsyncIOMotorClient
from urllib.parse import quote

async def main():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['raga_rasa']
    
    # Get first song
    song = await db.songs.find_one({})
    song_id = song.get('_id')
    file_path = song.get('file_path')
    
    print(f"Testing song: {song_id}")
    print(f"File exists: {__import__('pathlib').Path(file_path).exists()}")
    print()
    
    # Test different endpoint variations
    test_urls = [
        f"http://localhost:8000/api/songs/stream/{song_id}",
        f"http://localhost:8000/songs/stream/{song_id}",
        f"http://localhost:8000/api/songs/stream/{quote(song_id, safe='')}",
    ]
    
    for url in test_urls:
        try:
            print(f"Testing: {url}")
            resp = requests.get(url, timeout=5)
            print(f"  Status: {resp.status_code}")
            if resp.status_code == 200:
                content_length = resp.headers.get('Content-Length', 'unknown')
                print(f"  Content-Length: {content_length}")
            else:
                print(f"  Error: {resp.text[:100]}")
            print()
        except Exception as e:
            print(f"  Exception: {e}")
            print()
    
    client.close()

asyncio.run(main())
