"""Session history endpoints (for Profile page)"""

from fastapi import APIRouter, HTTPException, Query
from typing import List
import logging

from app.database import get_db
from app.models import SessionHistorySchema
from app.services.cache import cache_get, cache_set
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/sessions/history", response_model=List[SessionHistorySchema])
async def get_sessions_history(user_id: str = Query(...)):
    """
    Get user's session history for Profile analytics page
    
    Args:
        user_id: User identifier
    
    Returns:
        List of session history records
    """
    try:
        # Check cache
        cache_key = f"history:{user_id}"
        cached = await cache_get(cache_key)
        if cached:
            logger.info(f"Session history retrieved from cache")
            return [SessionHistorySchema(**item) for item in cached]
        
        db = get_db()
        
        # Fetch sessions for this user
        # Note: This is a simplified implementation
        # In production, you'd need to track user_id in sessions during /session/start
        sessions = await db.sessions.find({
            "user_id": user_id
        }).sort("created_at", -1).to_list(50)
        
        if not sessions:
            logger.warning(f"No sessions found for user {user_id}")
            return []
        
        # Build response
        history = []
        for session in sessions:
            try:
                # Get the top raga recommendation
                top_raga = "Raga Darbari"
                if session.get("recommended_songs") and len(session["recommended_songs"]) > 0:
                    top_raga = session["recommended_songs"][0].get("title", "Raga Darbari")
                
                # Extract feedback data
                feedback = session.get("feedback", {})
                rating = feedback.get("session_rating", 0)
                
                # Get cognitive data for mood before
                cognitive_data = session.get("cognitive_data", {})
                # For now, use moodLevel from frontend if available
                mood_before = 5  # Default
                mood_after = feedback.get("mood_after", "No comment").count("relax") > 0 and 7 or 5
                
                history_item = SessionHistorySchema(
                    session_id=session.get("_id", ""),
                    date=session.get("created_at", datetime.utcnow()).strftime("%b %d, %Y"),
                    emotion=session.get("emotion", "Neutral"),
                    top_raga=top_raga,
                    rating=rating,
                    mood_before=mood_before,
                    mood_after=mood_after
                )
                history.append(history_item)
                
            except Exception as e:
                logger.warning(f"Failed to process session {session.get('_id')}: {e}")
                continue
        
        # Cache results
        cached_data = [item.model_dump() for item in history]
        await cache_set(cache_key, cached_data, expiry=3600)  # Cache for 1 hour
        
        logger.info(f"Retrieved {len(history)} sessions for user {user_id}")
        return history
        
    except Exception as e:
        logger.error(f"Failed to fetch session history: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch session history")
