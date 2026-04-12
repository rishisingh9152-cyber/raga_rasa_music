"""Music catalog endpoints with cloud storage support"""

from fastapi import APIRouter, HTTPException
from typing import List, Optional, Dict
import logging
from pathlib import Path

from app.database import get_db
from app.models import RagaSchema, SongSchema
from app.services.cache import cache_get, cache_set
from app.services.song_scanner import get_song_scanner
from app.services.cloud_storage import get_storage_provider
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

# Songs directory path (fallback for local storage)
SONGS_BASE_DIR = Path(settings.STORAGE_BASE_PATH)


@router.get("/test/songs-count")
async def test_songs_count():
    """Test endpoint to check if database is accessible"""
    try:
        db = get_db()
        if not db:
            return {"status": "error", "message": "Database not initialized"}
        
        collection = db.songs
        count = await collection.count_documents({})
        return {"status": "success", "total_songs": count}
    except Exception as e:
        return {"status": "error", "message": str(e), "exc_info": str(e.__class__.__name__)}


@router.get("/ragas/simple")
async def get_ragas_simple():
    """Simple endpoint to test database access - returns raw dict"""
    try:
        db = get_db()
        if not db:
            return {"error": "Database not initialized", "status": "db_init_failed"}
        
        ragas = await db.songs.find({}).to_list(5)
        
        # Convert ObjectIds to strings for JSON serialization
        result = []
        for raga in ragas:
            result.append({
                "title": raga.get("title"),
                "rasa": raga.get("rasa"),
                "duration": raga.get("duration"),
                "audio_url": raga.get("audio_url", "no_url")[:50] + "..."
            })
        
        return {"status": "success", "count": len(result), "samples": result}
        
    except Exception as e:
        logger.error(f"Simple test failed: {e}", exc_info=True)
        return {"error": str(e), "status": "error"}


@router.get("/ragas/list", response_model=List[SongSchema])
async def get_ragas_list(rasa: Optional[str] = None):
    """
    Get list of available ragas for music player
    
    Args:
        rasa: Optional filter by rasa (Shringar, Shaant, Veer, Shok)
    
    Returns:
        List of available ragas with proper URLs (local or cloud)
    """
    try:
        db = get_db()
        logger.info(f"[Catalog] Database connection: {db}")
        
        # Build query
        query = {}
        if rasa:
            query["rasa"] = rasa
        
        logger.info(f"[Catalog] Querying songs with filter: {query}")
        # Fetch ragas from database
        ragas = await db.songs.find(query).to_list(None)
        logger.info(f"[Catalog] Found {len(ragas)} ragas")
        
        if not ragas:
            logger.warning(f"No ragas found with filter: {rasa}")
            return []
        
        # Convert to response schema with proper URLs
        raga_list = []
        for idx, raga in enumerate(ragas):
            try:
                # Generate proper URL based on storage type
                audio_url = raga.get("audio_url")
                
                # Convert duration to string if it's an int
                duration = raga.get("duration", None)
                if isinstance(duration, int):
                    # Convert seconds to "mm:ss" format
                    mins = duration // 60
                    secs = duration % 60
                    duration = f"{mins}:{secs:02d}"
                
                song_id_val = raga.get("song_id", str(raga.get("_id", f"unknown_{idx}")))
                logger.debug(f"[Catalog] Processing song {idx}: {raga.get('title')} (id: {song_id_val})")
                
                raga_item = SongSchema(
                    song_id=song_id_val,
                    title=raga.get("title", ""),
                    audio_url=audio_url or "/api/songs/stream/unknown",
                    rasa=raga.get("rasa", "Shaant"),
                    confidence=raga.get("confidence", 1.0),
                    duration=duration,
                    rasa_confidence=raga.get("rasa_confidence", 1.0),
                    storage_metadata=None
                )
                raga_list.append(raga_item)
            except Exception as e:
                logger.warning(f"Failed to convert raga {raga.get('title')}: {e}", exc_info=True)
                continue
        
        logger.info(f"[Catalog] Retrieved {len(raga_list)} ragas with filter: {rasa}")
        return raga_list
        
    except Exception as e:
        logger.error(f"[Catalog] Failed to fetch ragas list: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch ragas list: {str(e)}")


@router.get("/ragas/{raga_id}", response_model=RagaSchema)
async def get_raga_details(raga_id: str):
    """
    Get details for a specific raga with cloud-aware URLs
    
    Args:
        raga_id: Raga/Song ID
    
    Returns:
        Raga details with proper streaming URL
    """
    try:
        # Check cache
        cache_key = f"raga:{raga_id}"
        cached = await cache_get(cache_key)
        if cached:
            return RagaSchema(**cached)
        
        db = get_db()
        raga = await db.songs.find_one({"_id": raga_id})
        
        if not raga:
            raise HTTPException(status_code=404, detail="Raga not found")
        
         # Generate proper URL based on storage type
         audio_url = await _get_song_url(raga)
         
         # Convert duration to string if it's an int
         duration = raga.get("duration", "0:00")
         if isinstance(duration, int):
             # Convert seconds to "mm:ss" format
             mins = duration // 60
             secs = duration % 60
             duration = f"{mins}:{secs:02d}"
         
         raga_item = RagaSchema(
             song_id=raga.get("song_id", str(raga.get("_id", ""))),
             title=raga.get("title", ""),
             rasa=raga.get("rasa", "Shaant"),
             audio_url=audio_url,
             duration=str(duration),
             storage_metadata=raga.get("storage_metadata")
         )
        
        # Cache result
        await cache_set(cache_key, raga_item.model_dump(), expiry=3600)
        
        return raga_item
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch raga details: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch raga details")


@router.get("/songs/by-rasa")
async def get_songs_by_rasa(rasa: Optional[str] = None) -> Dict:
    """
    Get all songs organized by rasa with cloud-aware URLs
    
    Args:
        rasa: Optional filter by specific rasa
    
    Returns:
        Dictionary with songs organized by rasa
    """
    try:
        db = get_db()
        
        # Build query
        query = {}
        if rasa:
            query["rasa"] = rasa
        
        # Get songs from database
        songs = await db.songs.find(query).to_list(None)
        
        # Organize by rasa
        songs_data = {
            "Shringar": [],
            "Shaant": [],
            "Veer": [],
            "Shok": []
        }
        
        for song in songs:
            rasa_key = song.get("rasa", "Shaant")
            
            # Generate proper URL
            audio_url = await _get_song_url(song)
            
            song_doc = {
                "_id": song.get("_id", ""),
                "title": song.get("title", ""),
                "artist": song.get("artist", "Unknown"),
                "rasa": rasa_key,
                "audio_url": audio_url,
                "duration": song.get("duration", "0:00"),
                "rasa_confidence": song.get("rasa_confidence", 1.0),
                "storage_metadata": song.get("storage_metadata")
            }
            
            if rasa_key in songs_data:
                songs_data[rasa_key].append(song_doc)
        
        logger.info(f"Returning {sum(len(v) for v in songs_data.values())} songs organized by rasa")
        return songs_data
        
    except Exception as e:
        logger.error(f"Failed to get songs by rasa: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve songs")


@router.get("/songs/{song_id}", response_model=RagaSchema)
async def get_song_by_id(song_id: str):
    """
    Get details for a specific song by ID with cloud-aware URL
    
    Args:
        song_id: Song ID to retrieve
    
    Returns:
        Song details with proper streaming URL
    """
    try:
        db = get_db()
        
        # Try to find song in database first
        song = await db.songs.find_one({"_id": song_id})
        
         if song:
             audio_url = await _get_song_url(song)
             
             # Convert duration to string if it's an int
             duration = song.get("duration", "0:00")
             if isinstance(duration, int):
                 # Convert seconds to "mm:ss" format
                 mins = duration // 60
                 secs = duration % 60
                 duration = f"{mins}:{secs:02d}"
             
             raga_item = RagaSchema(
                 song_id=song.get("song_id", str(song.get("_id", ""))),
                 title=song.get("title", ""),
                 rasa=song.get("rasa", "Shaant"),
                 audio_url=audio_url,
                 duration=str(duration),
                 storage_metadata=song.get("storage_metadata")
            )
            logger.info(f"Retrieved song from database: {raga_item.title}")
            return raga_item
        
        # If not in database, try filesystem
        logger.warning(f"Song {song_id} not found in database, checking filesystem...")
        scanner = get_song_scanner()
        file_path = scanner.get_song_file_path(song_id)
        
        if file_path and file_path.exists():
            # Reconstruct song data from file
            relative_path = file_path.relative_to(SONGS_BASE_DIR)
            rasa_folder = relative_path.parts[0]
            
            rasa_mapping = {
                "shringar": "Shringar",
                "shaant": "Shaant",
                "veer": "Veer",
                "shok": "Shok"
            }
            rasa = rasa_mapping.get(rasa_folder.lower(), "Shaant")
            title = file_path.stem.replace('_', ' ').replace('-', ' ')
            
            raga_item = RagaSchema(
                song_id=song_id,
                title=title,
                rasa=rasa,
                audio_url=f"/api/songs/stream/{file_path.name}",
                duration="0:00"
            )
            logger.info(f"Retrieved song from filesystem: {title}")
            return raga_item
        
        raise HTTPException(status_code=404, detail=f"Song {song_id} not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch song details: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch song details")


# ==================== Helper Functions ====================

async def _get_song_url(song: Dict) -> str:
    """
    Get the proper audio URL for a song based on storage type
    
    Args:
        song: Song document from database
    
    Returns:
        Proper streaming URL (local or cloud)
    """
    try:
        storage_metadata = song.get("storage_metadata", {})
        storage_type = storage_metadata.get("storage_type", "local")
        
        if storage_type == "cloud":
            # Use cloud URL if available
            cloud_url = storage_metadata.get("cloud_url")
            if cloud_url:
                return cloud_url
        elif storage_type == "local":
            # Use local streaming endpoint
            filename = song.get("filename")
            if filename:
                return f"/api/songs/stream/{filename}"
        
        # Fallback to database audio_url
        return song.get("audio_url", f"/api/songs/stream/{song.get('_id', '')}")
        
    except Exception as e:
        logger.warning(f"Error generating song URL: {e}")
        return song.get("audio_url", "")


def _load_ragas_from_filesystem(rasa_filter: Optional[str] = None) -> List[Dict]:
    """
    Load ragas from filesystem organized in rasa folders
    
    Args:
        rasa_filter: Optional filter by specific rasa
    
    Returns:
        List of raga documents
    """
    ragas = []
    
    if not SONGS_BASE_DIR.exists():
        logger.warning(f"Songs directory not found: {SONGS_BASE_DIR}")
        return ragas
    
    rasa_mapping = {
        "shaant": "Shaant",
        "shringar": "Shringar",
        "veer": "Veer",
        "shok": "Shok"
    }
    
    for folder_name, rasa_name in rasa_mapping.items():
        # Skip if filtered by different rasa
        if rasa_filter and rasa_filter.lower() != folder_name and rasa_filter != rasa_name:
            continue
        
        rasa_folder = SONGS_BASE_DIR / folder_name
        
        if not rasa_folder.exists():
            continue
        
        # Get all MP3 files in this rasa folder
        for idx, mp3_file in enumerate(rasa_folder.glob("*.mp3")):
            # Use the actual filename as the title (without .mp3)
            title = mp3_file.stem.replace('_', ' ')
            
            raga_doc = {
                "_id": f"{rasa_name.lower()}_{idx}_{mp3_file.stem}",
                "title": title,
                "rasa": rasa_name,
                "audio_url": f"/api/songs/stream/{mp3_file.name}",
                "filename": mp3_file.name,
                "file_path": str(mp3_file),
                "duration": "0:00",
                "storage_metadata": {
                    "storage_type": "local",
                    "local_path": str(mp3_file)
                }
            }
            ragas.append(raga_doc)
    
    logger.info(f"Loaded {len(ragas)} ragas from filesystem")
    return ragas


def _get_all_songs_by_rasa(rasa_filter: Optional[str] = None) -> Dict:
    """
    Get all songs organized by rasa from filesystem
    
    Args:
        rasa_filter: Optional filter by specific rasa
    
    Returns:
        Dictionary with songs organized by rasa
    """
    result = {}
    
    if not SONGS_BASE_DIR.exists():
        return result
    
    rasa_mapping = {
        "shaant": "Shaant",
        "shringar": "Shringar",
        "veer": "Veer",
        "shok": "Shok"
    }
    
    for folder_name, rasa_name in rasa_mapping.items():
        # Skip if filtered by different rasa
        if rasa_filter and rasa_filter.lower() != folder_name and rasa_filter != rasa_name:
            continue
        
        rasa_folder = SONGS_BASE_DIR / folder_name
        songs = []
        
        if rasa_folder.exists():
            for mp3_file in rasa_folder.glob("*.mp3"):
                title = mp3_file.stem.replace('_', ' ')
                
                song_doc = {
                    "_id": f"{rasa_name.lower()}_{mp3_file.stem}",
                    "title": title,
                    "filename": mp3_file.name,
                    "audio_url": f"/api/songs/stream/{mp3_file.name}",
                    "duration": "0:00",
                    "rasa": rasa_name
                }
                songs.append(song_doc)
        
        result[rasa_name] = songs
    
    return result
