import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def check_db():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['raga_rasa']
    
    # Check all songs in database
    songs = await db.songs.find().to_list(None)
    print(f'Total songs in DB: {len(songs)}')
    
    # Count by rasa
    for rasa in ['Shaant', 'Shringar', 'Veer', 'Shok']:
        count = await db.songs.count_documents({'rasa': rasa})
        print(f'{rasa}: {count}')
        
        # Show first 3 songs
        songs_list = await db.songs.find({'rasa': rasa}).to_list(3)
        for song in songs_list:
            print(f'  - {song.get("title", "No title")}')
    
    client.close()

asyncio.run(check_db())
