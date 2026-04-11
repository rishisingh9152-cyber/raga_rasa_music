"""
Song upload and classification service with cloud storage support
Supports hybrid local and cloud storage for migration flexibility
"""

import os
import shutil
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import hashlib

from app.services.cloud_storage import get_storage_provider
from app.config import settings

logger = logging.getLogger(__name__)

# Local fallback directories
SONGS_BASE_DIR = Path(settings.STORAGE_BASE_PATH)
TEMP_DIR = SONGS_BASE_DIR / "temp"
RASA_FOLDERS = {
    "Shringar": SONGS_BASE_DIR / "shringar",
    "Shaant": SONGS_BASE_DIR / "shaant",
    "Veer": SONGS_BASE_DIR / "veer",
    "Shok": SONGS_BASE_DIR / "shok",
}


def initialize_directories():
    """Create necessary local directories if they don't exist"""
    try:
        TEMP_DIR.mkdir(parents=True, exist_ok=True)
        for rasa_dir in RASA_FOLDERS.values():
            rasa_dir.mkdir(parents=True, exist_ok=True)
        logger.info("Song directories initialized")
    except Exception as e:
        logger.error(f"Failed to initialize directories: {e}")
        raise


async def save_uploaded_song(file_content: bytes, filename: str) -> Dict[str, str]:
    """
    Save uploaded song file to temp directory or cloud temp storage
    
    Args:
        file_content: Binary content of the uploaded file
        filename: Original filename
    
    Returns:
        Dict with temp file path and filename
    """
    try:
        # For now, always save to local temp directory for validation
        TEMP_DIR.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename to avoid conflicts
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{filename}"
        temp_file_path = TEMP_DIR / safe_filename
        
        # Write file to temp directory
        with open(temp_file_path, 'wb') as f:
            f.write(file_content)
        
        # Calculate file hash
        file_hash = hashlib.sha256(file_content).hexdigest()
        
        logger.info(f"Song saved to temp: {temp_file_path}")
        
        return {
            "temp_path": str(temp_file_path),
            "filename": safe_filename,
            "original_name": filename,
            "file_hash": file_hash,
            "file_size": len(file_content)
        }
    except Exception as e:
        logger.error(f"Failed to save uploaded song: {e}")
        raise


async def move_song_to_rasa_folder(
    temp_path: str, 
    rasa: str, 
    song_title: str,
    use_cloud: bool = False
) -> Dict[str, str]:
    """
    Move song from temp directory to appropriate rasa folder (local or cloud)
    
    Args:
        temp_path: Path to temp song file
        rasa: Rasa classification (Shringar, Shaant, Veer, Shok)
        song_title: Title of the song
        use_cloud: Whether to use cloud storage or local filesystem
    
    Returns:
        Dict with final file path and song info
    """
    try:
        temp_file = Path(temp_path)
        
        # Validate temp file exists
        if not temp_file.exists():
            raise FileNotFoundError(f"Temp file not found: {temp_path}")
        
        # Validate rasa
        if rasa not in RASA_FOLDERS:
            raise ValueError(f"Invalid rasa: {rasa}. Must be one of {list(RASA_FOLDERS.keys())}")
        
        # Read file content for cloud upload
        with open(temp_file, 'rb') as f:
            file_content = f.read()
        
        # Calculate file hash
        file_hash = hashlib.sha256(file_content).hexdigest()
        
        # Create final filename based on song title and rasa
        safe_title = song_title.lower().replace(" ", "-")
        final_filename = f"raag-{rasa.lower()}-{safe_title}.mp3"
        
        if use_cloud:
            # Upload to cloud storage
            storage_provider = get_storage_provider()
            cloud_path = f"{rasa.lower()}/{final_filename}"
            
            upload_result = await storage_provider.upload_file(
                cloud_path,
                file_content,
                metadata={
                    "rasa": rasa,
                    "title": song_title,
                    "hash": file_hash
                }
            )
            
            # Get cloud URL
            cloud_url = await storage_provider.get_download_url(cloud_path)
            
            logger.info(f"Song uploaded to cloud: {cloud_path}")
            
            # Clean up temp file
            try:
                temp_file.unlink()
            except:
                pass
            
            return {
                "final_path": cloud_path,
                "filename": final_filename,
                "rasa_folder": rasa,
                "song_title": song_title,
                "storage_type": settings.STORAGE_PROVIDER,
                "cloud_url": cloud_url,
                "file_hash": file_hash,
                "file_size": len(file_content)
            }
        else:
            # Keep using local storage
            dest_folder = RASA_FOLDERS[rasa]
            dest_folder.mkdir(parents=True, exist_ok=True)
            
            final_path = dest_folder / final_filename
            
            # Handle duplicate filenames
            counter = 1
            while final_path.exists():
                name_parts = final_filename.rsplit('.', 1)
                final_filename = f"{name_parts[0]}-{counter}.{name_parts[1]}"
                final_path = dest_folder / final_filename
                counter += 1
            
            # Move file from temp to destination
            shutil.move(str(temp_file), str(final_path))
            
            logger.info(f"Song moved to local {rasa} folder: {final_path}")
            
            return {
                "final_path": str(final_path),
                "filename": final_filename,
                "rasa_folder": rasa,
                "song_title": song_title,
                "storage_type": "local",
                "local_path": str(final_path),
                "file_hash": file_hash,
                "file_size": len(file_content)
            }
            
    except Exception as e:
        logger.error(f"Failed to move song to rasa folder: {e}")
        # Clean up temp file if it exists
        try:
            if temp_file.exists():
                temp_file.unlink()
        except:
            pass
        raise


async def cleanup_temp_files():
    """Clean up old temporary files"""
    try:
        if not TEMP_DIR.exists():
            return
        
        for file in TEMP_DIR.glob("*"):
            if file.is_file():
                file.unlink()
        
        logger.info("Temp files cleaned up")
    except Exception as e:
        logger.error(f"Failed to cleanup temp files: {e}")


def get_all_songs_by_rasa(rasa: Optional[str] = None) -> Dict[str, list]:
    """
    Get all songs organized by rasa (local storage only)
    
    Args:
        rasa: Optional filter by specific rasa
    
    Returns:
        Dict mapping rasa to list of songs
    """
    try:
        result = {}
        folders_to_scan = {rasa: RASA_FOLDERS[rasa]} if rasa else RASA_FOLDERS
        
        for rasa_name, folder_path in folders_to_scan.items():
            songs = []
            if folder_path.exists():
                for mp3_file in folder_path.glob("*.mp3"):
                    songs.append({
                        "filename": mp3_file.name,
                        "path": str(mp3_file),
                        "size_mb": mp3_file.stat().st_size / (1024 * 1024),
                        "created_at": datetime.fromtimestamp(mp3_file.stat().st_ctime).isoformat()
                    })
            result[rasa_name] = songs
        
        return result
    except Exception as e:
        logger.error(f"Failed to get songs by rasa: {e}")
        return {}


async def get_song_from_storage(song_path: str) -> bytes:
    """
    Get song file from storage (cloud or local)
    
    Args:
        song_path: Path to the song file
    
    Returns:
        Binary content of the song
    """
    try:
        storage_provider = get_storage_provider()
        return await storage_provider.download_file(song_path)
    except Exception as e:
        logger.error(f"Failed to get song from storage: {e}")
        raise


# Initialize directories on module load
initialize_directories()
