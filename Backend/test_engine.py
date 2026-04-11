#!/usr/bin/env python3
"""Test recommendation engine directly"""

import asyncio
from app.services.recommendation import get_recommendation_engine
from app.database import init_db

async def test_engine():
    print("Testing Recommendation Engine")
    print("=" * 80)
    
    # Initialize database
    try:
        await init_db()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Failed to initialize database: {e}")
        return
    
    # Get engine
    engine = get_recommendation_engine()
    print(f"Engine initialized: {engine}")
    
    # Test recommendation
    print("\nTesting recommendation for Happy emotion...")
    cognitive_data = {
        "memory_score": 4,
        "reaction_time": 300,
        "accuracy_score": 85
    }
    
    try:
        recommendations = await engine.get_recommendations(
            emotion="Happy",
            cognitive_data=cognitive_data,
            user_id=None,
            session_id="test_session"
        )
        
        print(f"Got {len(recommendations)} recommendations")
        
        if recommendations:
            print("\nFirst 3 songs:")
            for i, song in enumerate(recommendations[:3], 1):
                print(f"\n{i}. {song.title}")
                print(f"   ID: {song.song_id}")
                print(f"   URL: {song.audio_url}")
                print(f"   Rasa: {song.rasa}")
                print(f"   Confidence: {song.confidence}")
        else:
            print("No recommendations found!")
            
    except Exception as e:
        print(f"Engine error: {e}")
        import traceback
        traceback.print_exc()

asyncio.run(test_engine())
