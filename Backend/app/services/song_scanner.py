"""Service to scan and manage music files from folder structure"""

import os
import logging
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import subprocess
import json

logger = logging.getLogger(__name__)

# Base path for songs
SONGS_BASE_PATH = Path("C:/Major Project/Songs")

# Map folder names to rasa types
RASA_MAPPING = {
    "shaant": "Shaant",
    "shok": "Shok",
    "shringar": "Shringar",
    "veer": "Veer"
}

class SongScanner:
    """Scans song folders and provides song catalog"""
    
    def __init__(self, base_path: Optional[Path] = None):
        """Initialize scanner with base path"""
        self.base_path = base_path or SONGS_BASE_PATH
        self.supported_formats = {'.mp3', '.wav', '.flac', '.m4a', '.ogg'}
    
    def get_all_songs(self, rasa_filter: Optional[str] = None) -> List[Dict]:
        """
        Scan all songs from folder structure
        
        Args:
            rasa_filter: Optional filter by rasa (shaant, shok, shringar, veer)
        
        Returns:
            List of song dictionaries with metadata
        """
        songs = []
        
        try:
            if not self.base_path.exists():
                logger.warning(f"Songs path does not exist: {self.base_path}")
                return songs
            
            # If filter specified, only scan that rasa folder
            if rasa_filter:
                rasa_lower = rasa_filter.lower()
                rasa_folder = self.base_path / rasa_lower
                if rasa_folder.exists():
                    songs.extend(self._scan_rasa_folder(rasa_folder, rasa_filter))
            else:
                # Scan all rasa folders
                for rasa_folder in self.base_path.iterdir():
                    if rasa_folder.is_dir() and rasa_folder.name in RASA_MAPPING:
                        rasa_type = RASA_MAPPING[rasa_folder.name]
                        songs.extend(self._scan_rasa_folder(rasa_folder, rasa_type))
            
            logger.info(f"Scanned {len(songs)} songs from folders")
            return sorted(songs, key=lambda x: x['title'])
            
        except Exception as e:
            logger.error(f"Error scanning songs: {e}")
            return songs
    
    def _scan_rasa_folder(self, rasa_folder: Path, rasa_type: str) -> List[Dict]:
        """Scan a single rasa folder for audio files"""
        songs = []
        
        try:
            for file_path in rasa_folder.rglob("*"):
                if file_path.is_file() and file_path.suffix.lower() in self.supported_formats:
                    try:
                        song_dict = self._create_song_entry(file_path, rasa_type)
                        songs.append(song_dict)
                    except Exception as e:
                        logger.warning(f"Failed to process file {file_path}: {e}")
                        continue
        except Exception as e:
            logger.error(f"Error scanning folder {rasa_folder}: {e}")
        
        return songs
    
    def _create_song_entry(self, file_path: Path, rasa_type: str) -> Dict:
        """Create song entry dictionary from file"""
        file_size = file_path.stat().st_size
        
        # Create unique ID from relative path
        relative_path = file_path.relative_to(self.base_path)
        song_id = str(relative_path).replace('\\', '/').replace('.mp3', '').replace('.wav', '').replace('.flac', '').replace('.m4a', '').replace('.ogg', '')
        
        # Extract title from filename (remove file extension and special characters)
        title = file_path.stem.replace('_', ' ').replace('-', ' ')
        
        # Try to extract actual duration using ffmpeg/ffprobe
        duration_str = self._get_audio_duration(file_path)
        
        # Create URL path (relative to serve directory)
        audio_url = f"/api/songs/stream/{song_id}"
        
        return {
            "_id": song_id,
            "title": title,
            "rasa": rasa_type,
            "audio_url": audio_url,
            "duration": duration_str,
            "file_path": str(file_path),
            "file_size": file_size,
            "file_size_mb": file_size / (1024 * 1024),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    
    def _get_audio_duration(self, file_path: Path) -> str:
        """
        Extract audio duration using ffprobe
        Falls back to estimation if ffprobe is not available
        
        Args:
            file_path: Path to audio file
        
        Returns:
            Duration as formatted string (MM:SS)
        """
        try:
            # Try using ffprobe if available
            result = subprocess.run(
                ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', 
                 '-of', 'default=noprint_wrappers=1:nokey=1:noprint_wrappers=1', 
                 str(file_path)],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0 and result.stdout.strip():
                duration_seconds = int(float(result.stdout.strip()))
                minutes = duration_seconds // 60
                seconds = duration_seconds % 60
                return f"{minutes}:{seconds:02d}"
        except (FileNotFoundError, subprocess.TimeoutExpired, Exception) as e:
            logger.debug(f"Could not extract duration with ffprobe for {file_path.name}: {e}")
        
        # Fallback: Estimate duration (rough estimate: ~50KB per second for MP3)
        try:
            file_size = file_path.stat().st_size
            estimated_duration_seconds = max(1, file_size // 50000)
            return f"{estimated_duration_seconds // 60}:{estimated_duration_seconds % 60:02d}"
        except Exception as e:
            logger.warning(f"Could not estimate duration for {file_path.name}: {e}")
            return "0:00"
    
    def get_song_file_path(self, song_id: str) -> Optional[Path]:
        """Get file path for a song ID"""
        try:
            for rasa_folder in self.base_path.iterdir():
                if rasa_folder.is_dir():
                    for file_path in rasa_folder.rglob("*"):
                        if file_path.is_file() and file_path.suffix.lower() in self.supported_formats:
                            relative_path = file_path.relative_to(self.base_path)
                            file_song_id = str(relative_path).replace('\\', '/').replace('.mp3', '').replace('.wav', '').replace('.flac', '').replace('.m4a', '').replace('.ogg', '')
                            if file_song_id == song_id:
                                return file_path
        except Exception as e:
            logger.error(f"Error finding song file: {e}")
        
        return None


# Singleton instance
_scanner = None

def get_song_scanner() -> SongScanner:
    """Get or create song scanner instance"""
    global _scanner
    if _scanner is None:
        _scanner = SongScanner()
    return _scanner
