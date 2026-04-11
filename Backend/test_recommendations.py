#!/usr/bin/env python3
"""Test recommendation endpoint"""

import asyncio
import httpx
import json

async def test_recommendations():
    # Start a session first
    print("Testing Recommendation Flow")
    print("=" * 80)
    
    async with httpx.AsyncClient() as client:
        # Step 1: Start session
        print("\n1. Starting session...")
        response = await client.post("http://localhost:8000/api/session/start")
        print(f"   Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"   Error: {response.text}")
            return
        
        session_data = response.json()
        session_id = session_data.get("session_id")
        print(f"   Session ID: {session_id}")
        
        # Step 2: Get recommendations
        print("\n2. Requesting recommendations...")
        request_body = {
            "emotion": "Happy",
            "session_id": session_id,
            "cognitive_data": {
                "memory_score": 4,
                "reaction_time": 300,
                "accuracy_score": 85
            }
        }
        
        response = await client.post(
            "http://localhost:8000/api/recommend/live",
            json=request_body
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"   Error: {response.text}")
            return
        
        recommendations = response.json()
        print(f"   Recommendations count: {len(recommendations)}")
        
        if recommendations:
            print("\n   First 3 recommendations:")
            for i, song in enumerate(recommendations[:3], 1):
                print(f"\n   Song {i}:")
                print(f"     ID: {song.get('song_id')}")
                print(f"     Title: {song.get('title')}")
                print(f"     Audio URL: {song.get('audio_url')}")
                print(f"     Rasa: {song.get('rasa')}")
                print(f"     Confidence: {song.get('confidence')}")
        else:
            print("   No recommendations returned!")

asyncio.run(test_recommendations())
