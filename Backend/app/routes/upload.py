"""Song upload and management endpoints with cloud storage support"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Body, Path as PathParam, Depends
from fastapi.responses import FileResponse, StreamingResponse
from typing import List, Optional, Dict, Any
import logging
from pathlib import Path
from pydantic import BaseModel
import uuid

from app.database import get_db
from app.models import SongSchema
from app.services.song_upload import (
    save_uploaded_song,
    move_song_to_rasa_folder,
    get_all_songs_by_rasa,
    get_song_from_storage,
    RASA_FOLDERS
)
from app.services.rasa_model import get_rasa_model
from app.services.cloud_storage import get_storage_provider
from app.config import settings
from app.dependencies.auth import require_admin

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# Pydantic Models
# ============================================================================

class ConfirmUploadRequest(BaseModel):
    """Request model for confirming song upload"""
    temp_path: str
    title: str
    artist: Optional[str] = None
    rasa: str = "Shaant"
    rasa_confidence: Optional[float] = None


@router.post("/songs/upload")
async def upload_song(
    title: str = Form(...),
    artist: Optional[str] = Form(None),
    emotion: str = Form("Neutral"),
    file: UploadFile = File(...),
    current_user: Dict[str, Any] = Depends(require_admin)
):
    """
    Upload a new song for automatic rasa classification
    
    **Admin only endpoint**
    
    The song is:
    1. Saved to temp storage
    2. Analyzed using the Rasa ML model
    3. Returns classification results for admin review
    
    Args:
        title: Song title
        artist: Artist name (optional)
        emotion: User's current emotion (used for fallback classification)
        file: Audio file (MP3)
    
    Returns:
        Upload status with automatic Rasa classification
    """
    try:
        # Validate file type
        if not file.filename.endswith('.mp3'):
            raise HTTPException(status_code=400, detail="Only MP3 files are supported")
        
        # Validate file size (max 50MB)
        content = await file.read()
        file_size_mb = len(content) / (1024 * 1024)
        if file_size_mb > 50:
            raise HTTPException(status_code=413, detail="File size exceeds 50MB limit")
        
        logger.info(f"Admin {current_user.get('user_id')} uploading song: {file.filename}, size: {file_size_mb:.2f}MB")
        
        # Step 1: Save to temp directory
        temp_info = await save_uploaded_song(content, file.filename)
        logger.info(f"Saved to temp: {temp_info['temp_path']}")
        
        # Step 2: Classify using rasa model based on audio spectrogram
        try:
            rasa_model = get_rasa_model()
            classification_result = rasa_model.predict_rasa_from_audio(temp_info['temp_path'])
            logger.info(f"Classified rasa from audio: {classification_result['rasa']} (confidence: {classification_result['confidence']:.4f})")
        except Exception as e:
            logger.warning(f"Rasa classification failed, using fallback: {e}")
            # Fallback classification based on emotion
            emotion_to_rasa = {
                "Happy": "Shringar",
                "Sad": "Shok",
                "Calm": "Shaant",
                "Energetic": "Veer",
                "Neutral": "Shaant"
            }
            rasa = emotion_to_rasa.get(emotion, "Shaant")
            classification_result = {
                "rasa": rasa,
                "confidence": 0.5,
                "method": "emotion_fallback"
            }
        
        return {
            "status": "success",
            "temp_path": temp_info['temp_path'],
            "filename": temp_info['filename'],
            "title": title,
            "artist": artist,
            "file_size_mb": file_size_mb,
            "classification": classification_result,
            "next_step": "Call /api/songs/confirm-upload to finalize"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/songs/confirm-upload")
async def confirm_upload(
    request: ConfirmUploadRequest,
    current_user: Dict[str, Any] = Depends(require_admin)
):
    """
    Confirm song upload and move to storage (cloud or local)
    
    **Admin only endpoint**
    
    Args:
        request: ConfirmUploadRequest with temp_path, title, artist, rasa
    
    Returns:
        Confirmation with final file path and database info
    """
    try:
        # Extract data from request
        temp_path = request.temp_path
        title = request.title
        artist = request.artist
        rasa = request.rasa
        rasa_confidence = request.rasa_confidence or 1.0
        
        # Validate rasa
        valid_rasas = ["Shringar", "Shaant", "Veer", "Shok"]
        if rasa not in valid_rasas:
            raise HTTPException(status_code=400, detail=f"Invalid rasa. Must be one of {valid_rasas}")
        
        # Determine if we should use cloud storage
        use_cloud = settings.STORAGE_PROVIDER != "local"
        
        # Step 1: Move file to storage (cloud or local)
        move_result = await move_song_to_rasa_folder(temp_path, rasa, title, use_cloud=use_cloud)
        logger.info(f"Admin {current_user.get('user_id')} confirmed song upload to {move_result.get('storage_type', 'local')}: {move_result.get('final_path')}")
        
        # Step 2: Store in database with metadata
        db = get_db()
        
        # Create storage metadata
        storage_metadata = {
            "storage_type": move_result.get("storage_type", "local"),
            "file_hash": move_result.get("file_hash"),
            "file_size": move_result.get("file_size", 0)
        }
        
        if move_result.get("storage_type") == "local":
            storage_metadata["local_path"] = move_result.get("final_path")
        else:
            storage_metadata["cloud_bucket"] = move_result.get("cloud_bucket")
            storage_metadata["cloud_object_key"] = move_result.get("final_path")
            storage_metadata["cloud_url"] = move_result.get("cloud_url")
        
        song_data = {
            "_id": f"song_{title.lower().replace(' ', '_')}_{rasa}_{str(uuid.uuid4())[:8]}",
            "title": title,
            "artist": artist or "Unknown",
            "rasa": rasa,
            "rasa_confidence": rasa_confidence,
            "audio_url": move_result.get("cloud_url") or f"/api/songs/stream/{move_result['filename']}",
            "file_path": move_result.get("final_path"),
            "storage_metadata": storage_metadata,
            "duration": "0:00",  # Can be extracted from audio
            "audio_features": {
                "energy": 0.5,
                "valence": 0.5,
                "tempo": 100
            },
            "created_at": datetime.utcnow() if 'datetime' in dir() else __import__('datetime').datetime.utcnow(),
            "uploaded_by": current_user.get("user_id")
        }
        
        # Insert into database
        result = await db.songs.insert_one(song_data)
        
        logger.info(f"Song stored in database: {result.inserted_id}")
        
        return {
            "status": "success",
            "message": "Song uploaded and stored successfully",
            "song_id": str(result.inserted_id),
            "title": title,
            "artist": artist,
            "rasa": rasa,
            "rasa_confidence": rasa_confidence,
            "storage_type": move_result.get("storage_type", "local"),
            "audio_url": song_data['audio_url']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Confirm upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Confirm upload failed: {str(e)}")


@router.get("/songs/confirm-upload")
async def confirm_upload_get():
    """
    Fallback GET handler to provide helpful error message
    """
    raise HTTPException(
        status_code=405,
        detail="This endpoint only accepts POST requests. Use fetch() with method: 'POST' and a JSON body with temp_path, title, artist, and rasa."
    )


@router.get("/songs/library")
async def get_songs_library(rasa: Optional[str] = None) -> dict:
    """
    Get all uploaded songs organized by rasa
    
    Args:
        rasa: Optional filter by specific rasa
    
    Returns:
        Songs organized by rasa folder
    """
    try:
        db = get_db()
        
        # Get songs from database instead of filesystem
        query = {} if not rasa else {"rasa": rasa}
        songs = await db.songs.find(query).to_list(None)
        
        # Organize by rasa
        songs_by_rasa = {
            "Shringar": [],
            "Shaant": [],
            "Veer": [],
            "Shok": []
        }
        
        for song in songs:
            if "_id" in song:
                del song["_id"]
            rasa_key = song.get("rasa", "Shaant")
            if rasa_key in songs_by_rasa:
                songs_by_rasa[rasa_key].append(song)
        
        return {
            "status": "success",
            "songs": songs_by_rasa
        }
    except Exception as e:
        logger.error(f"Failed to get songs library: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve songs library")


@router.get("/songs/stream/{song_id_or_filename:path}")
async def stream_song(song_id_or_filename: str = PathParam(...)):
    """
    Stream a song file by ID or filename
    Supports both local and cloud-hosted songs
    
    Args:
        song_id_or_filename: Song ID or filename to stream
    
    Returns:
        Audio file stream
    """
    try:
        from app.services.song_scanner import get_song_scanner
        from datetime import datetime as dt
        
        # First try to find by song_id in database
        db = get_db()
        song = await db.songs.find_one({"_id": song_id_or_filename})
        
        if song:
            storage_metadata = song.get("storage_metadata", {})
            storage_type = storage_metadata.get("storage_type", "local")
            
            if storage_type == "local":
                # Local storage
                file_path = Path(song.get("file_path"))
                if file_path.exists():
                    logger.info(f"Streaming song from local storage: {song.get('title')}")
                    return FileResponse(
                        file_path,
                        media_type="audio/mpeg",
                        headers={"Content-Disposition": f"inline; filename={file_path.name}"}
                    )
            else:
                # Cloud storage
                try:
                    storage_provider = get_storage_provider()
                    cloud_path = storage_metadata.get("cloud_object_key")
                    
                    if cloud_path:
                        file_content = await storage_provider.download_file(cloud_path)
                        logger.info(f"Streaming song from cloud storage: {song.get('title')}")
                        
                        return StreamingResponse(
                            iter([file_content]),
                            media_type="audio/mpeg",
                            headers={"Content-Disposition": f"inline; filename={song.get('title', 'song')}.mp3"}
                        )
                except Exception as e:
                    logger.warning(f"Failed to stream from cloud: {e}")
        
        # Try to find in filesystem by filename
        for rasa_folder in RASA_FOLDERS.values():
            file_path = rasa_folder / song_id_or_filename
            if file_path.exists():
                logger.info(f"Streaming song by filename: {song_id_or_filename}")
                return FileResponse(
                    file_path,
                    media_type="audio/mpeg",
                    headers={"Content-Disposition": f"inline; filename={song_id_or_filename}"}
                )
        
        logger.warning(f"Song file not found: {song_id_or_filename}")
        raise HTTPException(status_code=404, detail="Song file not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Stream failed: {e}")
        raise HTTPException(status_code=500, detail=f"Stream failed: {str(e)}")


# Import datetime for song_data
from datetime import datetime
