#!/usr/bin/env python3
"""
Debug script to test recommendation engine locally
"""

import asyncio
import sys
sys.path.insert(0, r'C:\Users\rishi\raga_rasa_music\Backend')

from app.database import init_db, get_db
from app.services.recommendation import get_recommendation_engine
from app.config import settings
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def test_recommendations():
    print("\n" + "="*70)
    print("RECOMMENDATION ENGINE DEBUG TEST")
    print("="*70)
    
    # Initialize database
    print("\n[1] Initializing database...")
    await init_db()
    
    db = get_db()
    if db is None:
        print("[FAIL] Database not initialized")
        return
    
    # Check songs in database
    print("\n[2] Checking songs in database...")
    songs_count = await db.songs.count_documents({})
    print(f"[OK] Total songs in database: {songs_count}")
    
    # Check by rasa
    for rasa in ["Shringar", "Shaant", "Veer", "Shok"]:
        count = await db.songs.count_documents({"rasa": rasa})
        print(f"  {rasa}: {count} songs")
    
    # Sample song
    print("\n[3] Checking sample song structure...")
    sample = await db.songs.find_one()
    if sample:
        print(f"[OK] Sample song found:")
        print(f"  ID: {sample.get('_id')[:50]}...")
        print(f"  Title: {sample.get('title')}")
        print(f"  Rasa: {sample.get('rasa')}")
        print(f"  URL: {sample.get('audio_url')[:60]}...")
    
    # Test recommendation engine
    print("\n[4] Testing recommendation engine...")
    engine = get_recommendation_engine()
    
    # Test emotion mapping
    emotions_to_test = ["Happy", "Sad", "Neutral", "Fearful"]
    
    for emotion in emotions_to_test:
        print(f"\n  Testing emotion: {emotion}")
        
        cognitive_data = {
            "memory_score": 4,
            "reaction_time": 250,
            "accuracy_score": 85
        }
        
        try:
            recommendations = await engine.get_recommendations(
                emotion=emotion,
                cognitive_data=cognitive_data,
                session_id="test-session-001"
            )
            
            print(f"    Returned {len(recommendations)} songs")
            
            if recommendations:
                for i, song in enumerate(recommendations[:3], 1):
                    print(f"      [{i}] {song.title} ({song.rasa}) - {song.confidence:.2f}")
            else:
                print(f"    [WARN] No recommendations returned")
                
                # Debug: Check if we can manually query
                print(f"    Debug: Manually querying database for emotion...")
                from app.services.recommendation import EMOTION_TO_RASA
                target_rasa = EMOTION_TO_RASA.get(emotion, "Shaant")
                if isinstance(target_rasa, list):
                    target_rasa = target_rasa[0]
                
                manual_songs = await db.songs.find({"rasa": target_rasa}).to_list(5)
                print(f"    Manual query for {target_rasa}: {len(manual_songs)} songs")
                
        except Exception as e:
            print(f"    [ERROR] {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*70)
    print("DEBUG TEST COMPLETE")
    print("="*70)

if __name__ == "__main__":
    asyncio.run(test_recommendations())
