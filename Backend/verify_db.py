import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

async def main():
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]
    
    collections = {
        'songs': 0,
        'users': 0,
        'sessions': 0,
        'ratings': 0,
        'images': 0,
        'psychometric_tests': 0,
        'context_scores': 0
    }
    
    print('Database Summary:')
    print('=' * 60)
    for collection_name in collections.keys():
        count = await db[collection_name].count_documents({})
        collections[collection_name] = count
        print(f'{collection_name}............ {count} documents')
    
    print('=' * 60)
    total = sum(collections.values())
    print(f'TOTAL............................. {total} documents')
    
    # Sample data from each collection
    print('\nSample Data:')
    print('=' * 60)
    
    # Sample Song
    song = await db.songs.find_one({})
    if song:
        title = song.get("title", "Unknown")
        rasa = song.get("rasa", "Unknown")
        print(f'Song: {title} ({rasa})')
    
    # Sample User
    user = await db.users.find_one({})
    if user:
        name = user.get("name", "Unknown")
        user_id = user.get("user_id", "Unknown")
        print(f'User: {name} ({user_id})')
    
    # Sample Session
    session = await db.sessions.find_one({})
    if session:
        session_id = session.get("session_id", "Unknown")
        emotion = session.get("emotion", "Unknown")
        rasa = session.get("rasa", "Unknown")
        duration = session.get("duration_minutes", 0)
        played = len(session.get("played_songs", []))
        ratings_count = len(session.get("ratings", []))
        images_count = len(session.get("images", []))
        tests = len(session.get("psychometric_tests", []))
        print(f'Session: {session_id}')
        print(f'  - Emotion: {emotion}, Rasa: {rasa}')
        print(f'  - Duration: {duration} minutes')
        print(f'  - Songs Played: {played}')
        print(f'  - Ratings: {ratings_count}')
        print(f'  - Images: {images_count}')
        print(f'  - Tests: {tests}')
    
    client.close()

asyncio.run(main())
