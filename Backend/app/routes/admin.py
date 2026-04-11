"""Admin routes for system management"""

from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime
import logging
from typing import Dict, Any, List

from app.database import get_db
from app.dependencies.auth import require_admin
from app.services.cloud_storage import get_storage_provider

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/admin/dashboard", dependencies=[Depends(require_admin)])
async def get_dashboard(current_user: Dict[str, Any] = Depends(require_admin)):
    """
    Get admin dashboard statistics.
    
    Returns:
    - total_users: Total number of registered users
    - total_songs: Total number of songs in catalog
    - total_sessions: Total therapy sessions completed
    - avg_rating: Average song rating across all ratings
    - admin_count: Number of admins in system
    """
    db = get_db()
    
    try:
        # Get user statistics
        total_users = await db.users.count_documents({})
        admin_count = await db.users.count_documents({"role": "admin"})
        
        # Get song statistics
        total_songs = await db.songs.count_documents({})
        
        # Get session statistics
        total_sessions = await db.sessions.count_documents({})
        completed_sessions = await db.sessions.count_documents({"status": "completed"})
        
        # Get average rating
        ratings = await db.ratings.find({}).to_list(None)
        avg_rating = sum(r.get("rating", 0) for r in ratings) / len(ratings) if ratings else 0
        
        logger.info(f"Admin {current_user.get('user_id')} accessed dashboard")
        
        return {
            "total_users": total_users,
            "admin_count": admin_count,
            "total_songs": total_songs,
            "total_sessions": total_sessions,
            "completed_sessions": completed_sessions,
            "avg_rating": round(avg_rating, 2)
        }
        
    except Exception as e:
        logger.error(f"Error fetching dashboard stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch dashboard statistics"
        )


@router.get("/admin/users", dependencies=[Depends(require_admin)])
async def list_users(current_user: Dict[str, Any] = Depends(require_admin), skip: int = 0, limit: int = 100):
    """
    List all users in the system.
    
    Query Parameters:
    - skip: Number of users to skip (default: 0)
    - limit: Maximum number of users to return (default: 100)
    """
    db = get_db()
    
    try:
        users = await db.users.find({}).skip(skip).limit(limit).to_list(limit)
        
        # Remove sensitive data
        for user in users:
            if "_id" in user:
                del user["_id"]
            if "password" in user:
                del user["password"]
        
        total_count = await db.users.count_documents({})
        
        return {
            "users": users,
            "total": total_count,
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        logger.error(f"Error listing users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch users"
        )


@router.post("/admin/promote", dependencies=[Depends(require_admin)])
async def promote_user(user_id: str, current_user: Dict[str, Any] = Depends(require_admin)):
    """
    Promote a regular user to admin.
    
    Query Parameters:
    - user_id: The ID of the user to promote
    """
    db = get_db()
    
    try:
        # Ensure user exists
        user = await db.users.find_one({"user_id": user_id})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Promote user
        result = await db.users.update_one(
            {"user_id": user_id},
            {"$set": {"role": "admin"}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to promote user"
            )
        
        logger.info(f"Admin {current_user.get('user_id')} promoted user {user_id} to admin")
        
        return {
            "message": f"User {user_id} promoted to admin",
            "user_id": user_id,
            "role": "admin"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error promoting user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to promote user"
        )


@router.post("/admin/demote", dependencies=[Depends(require_admin)])
async def demote_admin(user_id: str, current_user: Dict[str, Any] = Depends(require_admin)):
    """
    Demote an admin back to regular user.
    
    Query Parameters:
    - user_id: The ID of the admin to demote
    """
    db = get_db()
    
    try:
        # Prevent demoting the only admin
        admin_count = await db.users.count_documents({"role": "admin"})
        if admin_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot demote the only admin in the system"
            )
        
        # Ensure user exists
        user = await db.users.find_one({"user_id": user_id})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Demote user
        result = await db.users.update_one(
            {"user_id": user_id},
            {"$set": {"role": "user"}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to demote admin"
            )
        
        logger.info(f"Admin {current_user.get('user_id')} demoted admin {user_id} to user")
        
        return {
            "message": f"Admin {user_id} demoted to user",
            "user_id": user_id,
            "role": "user"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error demoting admin: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to demote admin"
        )


@router.delete("/admin/song/{song_id}", dependencies=[Depends(require_admin)])
async def delete_song(song_id: str, current_user: Dict[str, Any] = Depends(require_admin)):
    """
    Delete a song from the catalog.
    
    Path Parameters:
    - song_id: The ID of the song to delete
    """
    db = get_db()
    
    try:
        # Check if song exists
        song = await db.songs.find_one({"song_id": song_id})
        if not song:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Song not found"
            )
        
        # Delete song
        await db.songs.delete_one({"song_id": song_id})
        
        # Also delete associated ratings
        await db.ratings.delete_many({"song_id": song_id})
        
        logger.info(f"Admin {current_user.get('user_id')} deleted song {song_id}")
        
        return {
            "message": f"Song {song_id} deleted successfully",
            "song_id": song_id,
            "title": song.get("title", "Unknown")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting song: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete song"
        )


@router.get("/admin/songs", dependencies=[Depends(require_admin)])
async def list_songs(current_user: Dict[str, Any] = Depends(require_admin), skip: int = 0, limit: int = 100):
    """
    List all songs in the catalog.
    
    Query Parameters:
    - skip: Number of songs to skip (default: 0)
    - limit: Maximum number of songs to return (default: 100)
    """
    db = get_db()
    
    try:
        songs = await db.songs.find({}).skip(skip).limit(limit).to_list(limit)
        
        # Remove MongoDB ObjectId
        for song in songs:
            if "_id" in song:
                del song["_id"]
        
        total_count = await db.songs.count_documents({})
        
        return {
            "songs": songs,
            "total": total_count,
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        logger.error(f"Error listing songs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch songs"
        )


@router.get("/admin/stats", dependencies=[Depends(require_admin)])
async def get_detailed_stats(current_user: Dict[str, Any] = Depends(require_admin)):
    """
    Get detailed system statistics.
    
    Returns comprehensive stats including:
    - User distribution by role
    - Session statistics by status
    - Songs by Rasa category
    - Top rated songs
    - Average session metrics
    """
    db = get_db()
    
    try:
        # User statistics
        total_users = await db.users.count_documents({})
        admin_users = await db.users.count_documents({"role": "admin"})
        regular_users = total_users - admin_users
        
        # Session statistics
        total_sessions = await db.sessions.count_documents({})
        active_sessions = await db.sessions.count_documents({"status": "active"})
        completed_sessions = await db.sessions.count_documents({"status": "completed"})
        
        # Songs by Rasa
        ragas = ["Shringar", "Shaant", "Veer", "Shok"]
        songs_by_rasa = {}
        for rasa in ragas:
            songs_by_rasa[rasa] = await db.songs.count_documents({"rasa": rasa})
        
        # Top rated songs
        ratings_pipeline = [
            {
                "$group": {
                    "_id": "$song_id",
                    "avg_rating": {"$avg": "$rating"},
                    "count": {"$sum": 1}
                }
            },
            {
                "$sort": {"avg_rating": -1}
            },
            {
                "$limit": 10
            }
        ]
        
        top_ratings = await db.ratings.aggregate(ratings_pipeline).to_list(None)
        
        logger.info(f"Admin {current_user.get('user_id')} accessed detailed stats")
        
        return {
            "users": {
                "total": total_users,
                "admins": admin_users,
                "regular": regular_users
            },
            "sessions": {
                "total": total_sessions,
                "active": active_sessions,
                "completed": completed_sessions
            },
            "songs_by_rasa": songs_by_rasa,
            "top_rated_songs": top_ratings
        }
        
    except Exception as e:
        logger.error(f"Error fetching detailed stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch statistics"
        )


# ==================== Storage Configuration Endpoints ====================

@router.get("/admin/storage/config", dependencies=[Depends(require_admin)])
async def get_storage_config(current_user: Dict[str, Any] = Depends(require_admin)):
    """
    Get current storage configuration.
    
    Returns:
    - provider: Current storage provider (local, google_drive, aws_s3, azure_blob)
    - configuration: Provider-specific configuration
    """
    db = get_db()
    
    try:
        # Get storage config from database
        config = await db.storage_config.find_one({})
        
        if not config:
            # Return default local storage config
            return {
                "provider": "local",
                "configuration": {
                    "base_path": "./Songs/",
                    "description": "Local file system storage"
                }
            }
        
        # Remove sensitive data
        if "_id" in config:
            del config["_id"]
        if "google_drive_api_key" in config:
            config["google_drive_api_key"] = "***REDACTED***"
        
        logger.info(f"Admin {current_user.get('user_id')} fetched storage config")
        return config
        
    except Exception as e:
        logger.error(f"Error fetching storage config: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch storage configuration"
        )


@router.post("/admin/storage/config", dependencies=[Depends(require_admin)])
async def update_storage_config(
    config: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(require_admin)
):
    """
    Update storage configuration.
    
    Body:
    - provider: Storage provider type
    - configuration: Provider-specific settings
    
    Validates the configuration before saving.
    """
    db = get_db()
    
    try:
        provider = config.get("provider", "local").lower()
        
        # Validate provider type
        valid_providers = ["local", "google_drive", "aws_s3", "azure_blob"]
        if provider not in valid_providers:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid provider. Must be one of: {valid_providers}"
            )
        
        # Validate required fields for each provider
        if provider == "google_drive":
            if not config.get("google_drive_folder_id") or not config.get("google_drive_api_key"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Google Drive requires: google_drive_folder_id and google_drive_api_key"
                )
        elif provider == "aws_s3":
            if not config.get("aws_s3_bucket") or not config.get("aws_s3_region"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="AWS S3 requires: aws_s3_bucket and aws_s3_region"
                )
        elif provider == "azure_blob":
            if not config.get("azure_blob_container") or not config.get("azure_storage_account"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Azure Blob requires: azure_blob_container and azure_storage_account"
                )
        
        # Update or create storage config
        storage_config = {
            "provider": provider,
            **config,
            "updated_at": datetime.utcnow(),
            "updated_by": current_user.get("user_id")
        }
        
        await db.storage_config.update_one({}, {"$set": storage_config}, upsert=True)
        
        logger.info(f"Admin {current_user.get('user_id')} updated storage config to {provider}")
        
        return {
            "message": f"Storage configuration updated to {provider}",
            "provider": provider
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating storage config: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update storage configuration"
        )


@router.get("/admin/storage/migrations", dependencies=[Depends(require_admin)])
async def list_migrations(current_user: Dict[str, Any] = Depends(require_admin)):
    """
    List all storage migration operations.
    
    Returns list of migration statuses.
    """
    db = get_db()
    
    try:
        migrations = await db.storage_migrations.find({}).to_list(None)
        
        # Remove internal IDs
        for migration in migrations:
            if "_id" in migration:
                del migration["_id"]
        
        logger.info(f"Admin {current_user.get('user_id')} listed migrations")
        
        return {
            "migrations": migrations,
            "total": len(migrations)
        }
        
    except Exception as e:
        logger.error(f"Error listing migrations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list migrations"
        )


@router.post("/admin/storage/migrate", dependencies=[Depends(require_admin)])
async def start_migration(
    target_provider: str,
    current_user: Dict[str, Any] = Depends(require_admin)
):
    """
    Start a migration to a new storage provider.
    
    Query Parameters:
    - target_provider: Target storage provider (google_drive, aws_s3, azure_blob)
    
    This endpoint initiates an async migration. Check /admin/storage/migrations for status.
    """
    db = get_db()
    
    try:
        # Validate target provider
        valid_providers = ["google_drive", "aws_s3", "azure_blob"]
        if target_provider not in valid_providers:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid target provider. Must be one of: {valid_providers}"
            )
        
        # Get current storage config
        current_config = await db.storage_config.find_one({})
        current_provider = current_config.get("provider", "local") if current_config else "local"
        
        # Get all songs to migrate
        songs = await db.songs.find({}).to_list(None)
        
        # Create migration record
        import uuid
        migration_id = str(uuid.uuid4())
        migration_record = {
            "migration_id": migration_id,
            "status": "pending",
            "source_provider": current_provider,
            "target_provider": target_provider,
            "songs_total": len(songs),
            "songs_migrated": 0,
            "songs_failed": 0,
            "error_message": None,
            "started_at": datetime.utcnow(),
            "completed_at": None,
            "created_by": current_user.get("user_id")
        }
        
        await db.storage_migrations.insert_one(migration_record)
        
        logger.info(f"Migration {migration_id} started by admin {current_user.get('user_id')}")
        
        return {
            "message": f"Migration to {target_provider} initiated",
            "migration_id": migration_id,
            "status": "pending",
            "songs_to_migrate": len(songs)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting migration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start migration"
        )

