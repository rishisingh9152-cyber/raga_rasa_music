"""Database connection and initialization"""

from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
import logging
import traceback

from app.config import settings

logger = logging.getLogger(__name__)

# Global database instance and client
_client: Optional[AsyncIOMotorClient] = None
_db = None


async def init_db():
    """Initialize MongoDB connection"""
    global _client, _db
    try:
        logger.info(f"[Database] Connecting to MongoDB at {settings.MONGODB_URL}")
        _client = AsyncIOMotorClient(settings.MONGODB_URL, serverSelectionTimeoutMS=5000)
        
        # Verify connection with ping
        logger.info(f"[Database] Pinging MongoDB server...")
        await _client.admin.command('ping')
        logger.info(f"[Database] MongoDB ping successful")
        
        # Get database instance
        _db = _client[settings.DATABASE_NAME]
        logger.info(f"[Database] Connected to database: {settings.DATABASE_NAME}")
        
        # Initialize collections and indexes
        await _create_collections()
        await _create_indexes()
        logger.info(f"[Database] Database initialization complete")
        
    except Exception as e:
        logger.error(f"[Database] Failed to connect to MongoDB: {str(e)}")
        logger.error(f"[Database] Traceback: {traceback.format_exc()}")
        raise


async def _create_collections():
    """Create collections if they don't exist"""
    try:
        db = get_db()
        
        # Get existing collections
        existing_collections = await db.list_collection_names()
        logger.info(f"[Database] Existing collections: {existing_collections}")
        
        # Define required collections
        required_collections = [
            'songs',
            'sessions',
            'ratings',
            'psychometric_tests',
            'images',
            'users',
            'context_scores'
        ]
        
        for collection_name in required_collections:
            if collection_name not in existing_collections:
                await db.create_collection(collection_name)
                logger.info(f"[Database] Created collection: {collection_name}")
            else:
                logger.info(f"[Database] Collection already exists: {collection_name}")
                
    except Exception as e:
        logger.error(f"[Database] Failed to create collections: {str(e)}")


async def _create_indexes():
    """Create database indexes for efficient queries"""
    try:
        db = get_db()
        
        logger.info(f"[Database] Creating indexes...")
        
        # Songs collection indexes
        logger.debug(f"[Database] Creating songs indexes...")
        await db.songs.create_index("rasa")
        await db.songs.create_index("title")
        await db.songs.create_index("artist")
        await db.songs.create_index("created_at")
        
        # Sessions collection indexes
        logger.debug(f"[Database] Creating sessions indexes...")
        await db.sessions.create_index("user_id")
        await db.sessions.create_index("created_at")
        await db.sessions.create_index("status")
        await db.sessions.create_index("emotion")
        await db.sessions.create_index("rasa")
        
        # Ratings collection indexes
        logger.debug(f"[Database] Creating ratings indexes...")
        await db.ratings.create_index([("user_id", 1), ("song_id", 1)])
        await db.ratings.create_index("session_id")
        await db.ratings.create_index("song_id")
        await db.ratings.create_index("created_at")
        
        # Psychometric tests collection indexes
        logger.debug(f"[Database] Creating psychometric_tests indexes...")
        await db.psychometric_tests.create_index("session_id")
        await db.psychometric_tests.create_index("user_id")
        await db.psychometric_tests.create_index("test_type")
        await db.psychometric_tests.create_index("created_at")
        
        # Images collection indexes
        logger.debug(f"[Database] Creating images indexes...")
        await db.images.create_index("session_id")
        await db.images.create_index("timestamp")
        
        # Users collection indexes
        logger.debug(f"[Database] Creating users indexes...")
        await db.users.create_index("user_id", unique=True)
        await db.users.create_index("created_at")
        
        # Context scores indexes
        logger.debug(f"[Database] Creating context_scores indexes...")
        await db.context_scores.create_index("session_id")
        await db.context_scores.create_index("user_id")
        
        logger.info(f"[Database] All indexes created successfully")
    except Exception as e:
        logger.error(f"[Database] Failed to create indexes: {str(e)}")
        # Don't raise - indexes might already exist
        logger.info(f"[Database] Continuing despite index creation error")


async def close_db():
    """Close MongoDB connection"""
    global _client
    if _client:
        logger.info("[Database] Closing MongoDB connection...")
        _client.close()
        logger.info("[Database] MongoDB connection closed")


def get_db():
    """Get database instance"""
    if _db is None:
        raise RuntimeError(
            "Database not initialized. "
            "Call init_db() during application startup. "
            "Ensure MongoDB is running on localhost:27017"
        )
    return _db

