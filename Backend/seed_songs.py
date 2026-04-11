"""Comprehensive seed script to scan and upload all songs from folders to MongoDB"""

import asyncio
import logging
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
from app.services.song_scanner import SongScanner

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def seed_songs_from_disk():
    """
    Scan all songs from C:\Major Project\Songs and upload to MongoDB
    """
    try:
        # Initialize scanner
        scanner = SongScanner()
        logger.info("Initialized SongScanner")
        
        # Scan all songs from disk
        all_songs = scanner.get_all_songs()
        
        if not all_songs:
            logger.warning("No songs found on disk. Check that Songs folder exists.")
            return
        
        logger.info(f"Scanned {len(all_songs)} total songs from disk")
        
        # Log breakdown by rasa
        rasa_counts = {}
        for song in all_songs:
            rasa = song.get('rasa', 'Unknown')
            rasa_counts[rasa] = rasa_counts.get(rasa, 0) + 1
        
        logger.info("Songs by Rasa:")
        for rasa, count in sorted(rasa_counts.items()):
            logger.info(f"  {rasa}: {count} songs")
        
        # Connect to MongoDB
        logger.info(f"Connecting to MongoDB at {settings.MONGODB_URL}")
        client = AsyncIOMotorClient(settings.MONGODB_URL)
        db = client[settings.DATABASE_NAME]
        
        # Verify connection
        await client.admin.command('ping')
        logger.info("MongoDB connection successful")
        
        # Clear existing songs collection (optional - comment out if you want to keep existing data)
        existing_count = await db.songs.count_documents({})
        if existing_count > 0:
            logger.warning(f"Found {existing_count} existing songs in database, clearing them...")
            await db.songs.delete_many({})
            logger.info("Cleared existing songs")
        
        # Upload songs to database
        logger.info("Uploading songs to MongoDB...")
        inserted_count = 0
        skipped_count = 0
        
        for i, song in enumerate(all_songs, 1):
            song_id = song['_id']
            
            try:
                # Check if song already exists
                existing = await db.songs.find_one({"_id": song_id})
                if existing:
                    logger.debug(f"  Skipping existing song: {song['title']}")
                    skipped_count += 1
                    continue
                
                # Insert song
                result = await db.songs.insert_one(song)
                inserted_count += 1
                logger.info(f"  [{i}/{len(all_songs)}] Inserted: {song['title']} ({song['rasa']}) - {song['duration']}")
                
            except Exception as e:
                logger.error(f"  Failed to insert song {song['title']}: {e}")
        
        logger.info(f"\nSeed complete!")
        logger.info(f"  Inserted: {inserted_count} new songs")
        logger.info(f"  Skipped: {skipped_count} existing songs")
        
        # Create indexes
        logger.info("Creating database indexes...")
        await db.songs.create_index("rasa")
        await db.songs.create_index("title")
        await db.songs.create_index("created_at")
        logger.info("Indexes created successfully")
        
        # Verify final count
        final_count = await db.songs.count_documents({})
        logger.info(f"Total songs in database: {final_count}")
        
        client.close()
        
    except Exception as e:
        logger.error(f"Seed failed with error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(seed_songs_from_disk())
