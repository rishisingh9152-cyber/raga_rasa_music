"""Seed initial raga data into MongoDB"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initial raga data
INITIAL_RAGAS = [
    {
        "_id": "raga_001",
        "title": "Raga Yaman",
        "rasa": "Shringar",  # Romantic/Aesthetic
        "audio_url": "http://localhost:8000/audio/raga-yaman.mp3",
        "duration": "8:45",
        "audio_features": {
            "energy": 0.6,
            "valence": 0.7,
            "tempo": 120
        }
    },
    {
        "_id": "raga_002",
        "title": "Raga Darbari",
        "rasa": "Shok",  # Sorrowful
        "audio_url": "http://localhost:8000/audio/raga-darbari.mp3",
        "duration": "9:12",
        "audio_features": {
            "energy": 0.4,
            "valence": 0.3,
            "tempo": 90
        }
    },
    {
        "_id": "raga_003",
        "title": "Raga Bhairav",
        "rasa": "Veer",  # Heroic/Energetic
        "audio_url": "http://localhost:8000/audio/raga-bhairav.mp3",
        "duration": "7:30",
        "audio_features": {
            "energy": 0.8,
            "valence": 0.6,
            "tempo": 140
        }
    },
    {
        "_id": "raga_004",
        "title": "Raga Bhairav Thaat",
        "rasa": "Veer",  # Heroic
        "audio_url": "http://localhost:8000/audio/raga-bhairav-thaat.mp3",
        "duration": "6:45",
        "audio_features": {
            "energy": 0.75,
            "valence": 0.65,
            "tempo": 130
        }
    },
    {
        "_id": "raga_005",
        "title": "Raga Bageshree",
        "rasa": "Shaant",  # Peaceful/Calm
        "audio_url": "http://localhost:8000/audio/raga-bageshree.mp3",
        "duration": "10:15",
        "audio_features": {
            "energy": 0.3,
            "valence": 0.5,
            "tempo": 80
        }
    },
    {
        "_id": "raga_006",
        "title": "Raga Ahir Bhairav",
        "rasa": "Shringar",  # Romantic
        "audio_url": "http://localhost:8000/audio/raga-ahir-bhairav.mp3",
        "duration": "8:20",
        "audio_features": {
            "energy": 0.55,
            "valence": 0.65,
            "tempo": 110
        }
    },
    {
        "_id": "raga_007",
        "title": "Raga Marwa",
        "rasa": "Veer",  # Energetic
        "audio_url": "http://localhost:8000/audio/raga-marwa.mp3",
        "duration": "7:50",
        "audio_features": {
            "energy": 0.85,
            "valence": 0.7,
            "tempo": 150
        }
    },
    {
        "_id": "raga_008",
        "title": "Raga Yaman Kalyan",
        "rasa": "Shringar",  # Romantic
        "audio_url": "http://localhost:8000/audio/raga-yaman-kalyan.mp3",
        "duration": "9:00",
        "audio_features": {
            "energy": 0.6,
            "valence": 0.75,
            "tempo": 120
        }
    },
    {
        "_id": "raga_009",
        "title": "Raga Jaunpuri",
        "rasa": "Shok",  # Sorrowful
        "audio_url": "http://localhost:8000/audio/raga-jaunpuri.mp3",
        "duration": "8:35",
        "audio_features": {
            "energy": 0.35,
            "valence": 0.25,
            "tempo": 85
        }
    },
    {
        "_id": "raga_010",
        "title": "Raga Malkauns",
        "rasa": "Shaant",  # Peaceful
        "audio_url": "http://localhost:8000/audio/raga-malkauns.mp3",
        "duration": "9:45",
        "audio_features": {
            "energy": 0.25,
            "valence": 0.4,
            "tempo": 75
        }
    },
]


async def seed_data():
    """Seed initial raga data"""
    try:
        client = AsyncIOMotorClient(settings.MONGODB_URL)
        db = client[settings.DATABASE_NAME]
        
        # Check if data already exists
        count = await db.songs.count_documents({})
        if count > 0:
            logger.info(f"Database already contains {count} songs. Skipping seed.")
            return
        
        # Try to load songs from C:\Major Project\Songs folder
        songs_dir = Path("C:/Major Project/Songs")
        songs_from_disk = load_songs_from_disk(songs_dir)
        
        if songs_from_disk:
            logger.info(f"Found {len(songs_from_disk)} songs on disk")
            result = await db.songs.insert_many(songs_from_disk)
            logger.info(f"Seeded {len(result.inserted_ids)} songs from disk")
        else:
            logger.info("No songs found on disk, using initial hardcoded data")
            # Insert initial ragas
            result = await db.songs.insert_many(INITIAL_RAGAS)
            logger.info(f"Seeded {len(result.inserted_ids)} ragas")
        
        # Create indexes
        await db.songs.create_index("song_id", unique=True)
        await db.songs.create_index("rasa")
        logger.info("Indexes created successfully")
        
        client.close()
        
    except Exception as e:
        logger.error(f"Seeding failed: {e}")
        raise


def load_songs_from_disk(songs_dir: Path) -> list:
    """
    Load songs from disk organized by rasa folders
    
    Args:
        songs_dir: Base directory containing rasa folders
    
    Returns:
        List of song documents ready for database insertion
    """
    songs = []
    rasa_mapping = {
        "shringar": "Shringar",
        "shaant": "Shaant",
        "veer": "Veer",
        "shok": "Shok"
    }
    
    try:
        if not songs_dir.exists():
            logger.warning(f"Songs directory not found: {songs_dir}")
            return songs
        
        for rasa_folder_name, rasa_name in rasa_mapping.items():
            rasa_folder = songs_dir / rasa_folder_name
            
            if not rasa_folder.exists():
                logger.info(f"Rasa folder not found: {rasa_folder}")
                continue
            
            # Find all MP3 files in this rasa folder
            mp3_files = list(rasa_folder.glob("*.mp3"))
            logger.info(f"Found {len(mp3_files)} songs in {rasa_folder_name}")
            
            for idx, mp3_file in enumerate(mp3_files):
                # Use actual filename as title (without .mp3)
                # Just clean up underscores to spaces
                title = mp3_file.stem.replace('_', ' ')
                
                song_doc = {
                    "_id": f"{rasa_name.lower()}_{idx}_{mp3_file.stem}",
                    "title": title,
                    "rasa": rasa_name,
                    "audio_url": f"/api/songs/stream/{mp3_file.name}",
                    "file_path": str(mp3_file),
                    "duration": "0:00",  # Can be extracted with audio processing
                    "audio_features": {
                        "energy": 0.5,
                        "valence": 0.5,
                        "tempo": 100
                    },
                    "created_at": mp3_file.stat().st_ctime
                }
                songs.append(song_doc)
                logger.info(f"  Added: {title} ({rasa_name})")
        
        logger.info(f"Total songs loaded from disk: {len(songs)}")
        return songs
        
    except Exception as e:
        logger.error(f"Failed to load songs from disk: {e}")
        return songs


if __name__ == "__main__":
    asyncio.run(seed_data())
