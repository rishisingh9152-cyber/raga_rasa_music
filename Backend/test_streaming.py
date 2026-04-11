#!/usr/bin/env python3
"""Test audio streaming endpoint"""

import asyncio
import httpx
from pathlib import Path

async def test_streaming():
    print("Testing Audio Streaming Endpoint")
    print("=" * 80)
    
    # Song ID format from database
    song_id = "shringar/bageshwari_shringar"
    
    print(f"\nTesting stream for song: {song_id}")
    print(f"Expected file: C:\\Major Project\\Songs\\shringar\\bageshwari_shringar.wav")
    print(f"File exists: {Path('C:/Major Project/Songs/shringar/bageshwari_shringar.wav').exists()}")
    
    async with httpx.AsyncClient() as client:
        # Test the streaming endpoint
        url = f"http://localhost:8000/api/songs/stream/{song_id}"
        print(f"\nTesting URL: {url}")
        
        try:
            response = await client.get(url, follow_redirects=True)
            print(f"Status: {response.status_code}")
            print(f"Content-Type: {response.headers.get('content-type')}")
            print(f"Content-Length: {response.headers.get('content-length')}")
            
            if response.status_code == 200:
                print(f"Response size: {len(response.content)} bytes")
                print("SUCCESS: Audio file streamed successfully!")
            else:
                print(f"Error: {response.text[:200]}")
                
        except Exception as e:
            print(f"Request failed: {e}")

asyncio.run(test_streaming())
