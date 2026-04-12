"""Dropbox streaming service for managing song URLs"""

import json
import logging
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class DropboxService:
    """Service for managing Dropbox streaming URLs for songs"""
    
    def __init__(self, mapping_file_path: str = "data/dropbox_songs_mapping.json"):
        """
        Initialize Dropbox service with song mappings
        
        Args:
            mapping_file_path: Path to dropbox_songs_mapping.json
        """
        self.mapping_file = Path(mapping_file_path)
        self.songs_mapping: Dict = {}
        self._load_mapping()
    
    def _load_mapping(self):
        """Load song mappings from JSON file"""
        try:
            if self.mapping_file.exists():
                with open(self.mapping_file, 'r') as f:
                    self.songs_mapping = json.load(f)
                logger.info(f"Loaded {len(self.songs_mapping)} songs from Dropbox mapping")
            else:
                logger.warning(f"Mapping file not found: {self.mapping_file}")
        except Exception as e:
            logger.error(f"Failed to load Dropbox mapping: {e}")
            self.songs_mapping = {}
    
    def get_streaming_url(self, song_id: str) -> Optional[Dict]:
        """
        Get streaming URL for a song
        
        Args:
            song_id: Song identifier (e.g., "shringar/bageshwari_shringar")
        
        Returns:
            Dict with song_id, dropbox_url, title, rasa
            or None if song not found
        """
        if song_id in self.songs_mapping:
            song_data = self.songs_mapping[song_id].copy()
            song_data['song_id'] = song_id
            return song_data
        
        logger.warning(f"Song not found in mapping: {song_id}")
        return None
    
    def get_all_songs_by_rasa(self, rasa: str) -> list:
        """
        Get all songs for a given rasa
        
        Args:
            rasa: Rasa name (Shringar, Shaant, Veer, Shok)
        
        Returns:
            List of songs matching the rasa
        """
        songs = []
        for song_id, song_data in self.songs_mapping.items():
            if song_data.get('rasa') == rasa:
                song_with_id = song_data.copy()
                song_with_id['song_id'] = song_id
                songs.append(song_with_id)
        return songs
    
    def reload_mapping(self):
        """Reload mapping from file (useful if file changes)"""
        self._load_mapping()
    
    def get_mapping_stats(self) -> Dict:
        """Get statistics about loaded mappings"""
        stats_by_rasa = {}
        for song_data in self.songs_mapping.values():
            rasa = song_data.get('rasa', 'Unknown')
            stats_by_rasa[rasa] = stats_by_rasa.get(rasa, 0) + 1
        
        return {
            'total_songs': len(self.songs_mapping),
            'by_rasa': stats_by_rasa
        }


# Global instance
_dropbox_service: Optional[DropboxService] = None


def init_dropbox_service(mapping_file_path: str = "data/dropbox_songs_mapping.json") -> DropboxService:
    """Initialize global Dropbox service"""
    global _dropbox_service
    _dropbox_service = DropboxService(mapping_file_path)
    return _dropbox_service


def get_dropbox_service() -> DropboxService:
    """Get global Dropbox service instance"""
    global _dropbox_service
    if _dropbox_service is None:
        _dropbox_service = DropboxService()
    return _dropbox_service
