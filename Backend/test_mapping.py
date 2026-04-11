#!/usr/bin/env python3
"""Test updated emotion-to-rasa mapping"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.services.recommendation import RecommendationEngine, EMOTION_TO_RASA

async def main():
    print("Emotion-to-Rasa Mapping")
    print("=" * 50)
    for emotion, ragas in EMOTION_TO_RASA.items():
        if isinstance(ragas, list):
            print(f"{emotion:15} -> {', '.join(ragas)}")
        else:
            print(f"{emotion:15} -> {ragas}")
    
    print("\n" + "=" * 50)
    print("Testing Recommendations for Different Emotions")
    print("=" * 50)
    
    engine = RecommendationEngine()
    
    test_emotions = ['Happy', 'Sad', 'Angry', 'Neutral']
    
    for emotion in test_emotions:
        print(f"\nEmotion: {emotion}")
        recommendations = await engine.get_recommendations(
            emotion=emotion,
            cognitive_data={'memory_score': 3, 'reaction_time': 300, 'accuracy_score': 50},
            user_id=None,
            session_id=None
        )
        
        if recommendations:
            print(f"  Got {len(recommendations)} recommendations:")
            for i, song in enumerate(recommendations[:3], 1):
                print(f"    {i}. {song.title} (Rasa: {song.rasa})")
        else:
            print("  No recommendations found")

asyncio.run(main())
