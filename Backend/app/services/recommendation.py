"""Recommendation engine combining content-based and collaborative filtering"""

import numpy as np
from typing import List, Dict, Optional
import logging
from datetime import datetime

from app.models import SongSchema
from app.database import get_db

logger = logging.getLogger(__name__)

# Rasa mapping for emotion-based filtering
# Note: Some emotions map to multiple ragas for better therapeutic outcomes
EMOTION_TO_RASA = {
    'Happy': 'Shringar',
    'Surprised': 'Shringar',
    'Sad': ['Shaant', 'Shringar'],  # Both calming and uplifting for sadness
    'Angry': 'Shaant',
    'Fearful': 'Veer',
    'Disgusted': 'Veer',
    'Neutral': 'Shaant',
}


class RecommendationEngine:
    """Hybrid recommendation system using content + collaborative filtering"""
    
    def __init__(self):
        self.db = get_db()
        self.max_recommendations = 5
    
    async def get_recommendations(
        self,
        emotion: str,
        cognitive_data: Dict,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> List[SongSchema]:
        """
        Get personalized song recommendations
        
        Args:
            emotion: Detected emotion
            cognitive_data: User's cognitive metrics
            user_id: User identifier (optional, for collaborative filtering)
            session_id: Session identifier
        
        Returns:
            List of recommended songs
        """
        try:
            # Step 1: Get target rasa(s) based on emotion
            target_ragas = EMOTION_TO_RASA.get(emotion, 'Shaant')
            # Handle both single rasa string and multiple ragas list
            if isinstance(target_ragas, str):
                target_ragas = [target_ragas]
            
            # Step 2: Get songs matching the rasa(s)
            matching_songs = []
            for rasa in target_ragas:
                rasa_songs = await self._get_songs_by_rasa(rasa)
                matching_songs.extend(rasa_songs)
            
            if not matching_songs:
                logger.warning(f"No songs found for ragas: {target_ragas}")
                matching_songs = await self._get_all_songs()
            
            # Step 3: Score songs based on multiple factors
            scored_songs = await self._score_songs(
                matching_songs,
                cognitive_data,
                user_id,
                emotion
            )
            
            # Step 4: Rank and return top N
            ranked_songs = sorted(scored_songs, key=lambda x: x['score'], reverse=True)
            return [self._to_song_schema(song) for song in ranked_songs[:self.max_recommendations]]
            
        except Exception as e:
            logger.error(f"Recommendation error: {e}")
            return []
    
    async def _get_songs_by_rasa(self, rasa: str) -> List[Dict]:
        """Get all songs matching a specific rasa"""
        try:
            songs = await self.db.songs.find({"rasa": rasa}).to_list(None)
            return songs or []
        except Exception as e:
            logger.error(f"Failed to fetch songs by rasa: {e}")
            return []
    
    async def _get_all_songs(self) -> List[Dict]:
        """Get all available songs"""
        try:
            songs = await self.db.songs.find({}).to_list(None)
            return songs or []
        except Exception as e:
            logger.error(f"Failed to fetch all songs: {e}")
            return []
    
    async def _score_songs(
        self,
        songs: List[Dict],
        cognitive_data: Dict,
        user_id: Optional[str],
        emotion: str
    ) -> List[Dict]:
        """
        Score songs based on multiple factors
        
        Scoring formula:
        score = 0.5 * content_similarity
              + 0.3 * user_preference
              + 0.2 * freshness
        """
        scored_songs = []
        
        for song in songs:
            song_copy = song.copy()
            
            # Content-based similarity (quality + audio features)
            content_score = self._compute_content_similarity(song, cognitive_data)
            
            # User preference (collaborative filtering)
            user_score = await self._compute_user_preference(song['_id'], user_id) if user_id else 0.5
            
            # Freshness (newer songs get slight boost)
            freshness_score = self._compute_freshness(song)
            
            # Combined score
            final_score = (0.5 * content_score) + (0.3 * user_score) + (0.2 * freshness_score)
            
            song_copy['score'] = final_score
            song_copy['content_score'] = content_score
            song_copy['user_score'] = user_score
            song_copy['freshness_score'] = freshness_score
            
            scored_songs.append(song_copy)
        
        return scored_songs
    
    def _compute_content_similarity(self, song: Dict, cognitive_data: Dict) -> float:
        """
        Compute content-based similarity score based on cognitive metrics
        
        - Low memory_score → prefer calming/simple compositions
        - High reaction_time → prefer stimulating (Veer ragas)
        - Low accuracy_score → prefer uplifting (Shringar ragas)
        """
        base_score = 0.7  # Base similarity
        
        memory_score = cognitive_data.get('memory_score', 3)
        reaction_time = cognitive_data.get('reaction_time', 300)
        accuracy_score = cognitive_data.get('accuracy_score', 50)
        
        # If low memory, prefer calming (Shaant/Shok)
        if memory_score < 2:
            if song.get('rasa') in ['Shaant', 'Shok']:
                base_score += 0.15
        
        # If high reaction time (slow), prefer stimulating (Veer)
        if reaction_time > 400:
            if song.get('rasa') == 'Veer':
                base_score += 0.1
        
        # If low accuracy, prefer uplifting (Shringar)
        if accuracy_score < 40:
            if song.get('rasa') == 'Shringar':
                base_score += 0.15
        
        # Audio features compatibility (if available)
        features = song.get('audio_features', {})
        if features:
            energy = features.get('energy', 0.5)
            if memory_score < 2 and energy < 0.5:  # Match low energy
                base_score += 0.1
        
        return min(base_score, 1.0)
    
    async def _compute_user_preference(self, song_id: str, user_id: str) -> float:
        """
        Compute user preference score from past ratings
        Uses collaborative filtering - similar users' ratings
        """
        try:
            # Get this user's average rating for this song
            user_rating = await self.db.ratings.find_one({
                "user_id": user_id,
                "song_id": song_id
            })
            
            if user_rating:
                # Normalize rating to 0-1 scale
                return user_rating.get('rating', 3) / 5.0
            
            # Get average rating from all users for this song
            pipeline = [
                {"$match": {"song_id": song_id}},
                {"$group": {"_id": None, "avg_rating": {"$avg": "$rating"}}}
            ]
            result = await self.db.ratings.aggregate(pipeline).to_list(1)
            
            if result and len(result) > 0:
                avg_rating = result[0].get('avg_rating', 3)
                return avg_rating / 5.0
            
            # Default score for new songs
            return 0.5
            
        except Exception as e:
            logger.error(f"Failed to compute user preference: {e}")
            return 0.5
    
    def _compute_freshness(self, song: Dict) -> float:
        """
        Compute freshness score - newer songs get slight preference
        """
        try:
            created_at = song.get('created_at')
            if not created_at:
                return 0.5
            
            # Calculate days since creation
            days_old = (datetime.utcnow() - created_at).days
            
            # Exponential decay: newer is better, but not overwhelming factor
            # Max boost at 0 days, decays to 0.5 over time
            freshness = 1.0 - (days_old / 365.0) * 0.5  # Decay over 1 year
            return max(0.5, min(1.0, freshness))
            
        except Exception as e:
            logger.warning(f"Failed to compute freshness: {e}")
            return 0.5
    
    def _to_song_schema(self, song: Dict) -> SongSchema:
        """Convert song document to API schema"""
        return SongSchema(
            song_id=song.get('_id', ''),
            title=song.get('title', ''),
            audio_url=song.get('audio_url', ''),
            rasa=song.get('rasa', 'Shaant'),
            confidence=song.get('score', 0.5),  # Use computed score as confidence
            duration=song.get('duration', None)
        )


# Global recommendation engine instance
_engine: RecommendationEngine = None


def get_recommendation_engine() -> RecommendationEngine:
    """Get or create recommendation engine instance"""
    global _engine
    if _engine is None:
        _engine = RecommendationEngine()
    return _engine
