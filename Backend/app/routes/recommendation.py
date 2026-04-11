"""Music recommendation endpoints"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import logging
import traceback

from app.database import get_db
from app.services.recommendation import get_recommendation_engine
from app.models import SongSchema, CognitiveDataSchema, FeedbackSchema
from app.services.cache import cache_get, cache_set

logger = logging.getLogger(__name__)

router = APIRouter()


class RecommendLiveRequest(BaseModel):
    """Live session recommendation request"""
    emotion: str
    session_id: str
    cognitive_data: CognitiveDataSchema


class RecommendFinalRequest(BaseModel):
    """Final session recommendation request"""
    emotion: str
    session_id: str
    cognitive_data: CognitiveDataSchema
    feedback: FeedbackSchema


@router.post("/recommend/live", response_model=List[SongSchema])
async def recommend_live(request: RecommendLiveRequest):
    """
    Get song recommendations for live session
    
    Args:
        emotion: Detected emotion
        session_id: Session identifier
        cognitive_data: User's cognitive metrics from PreTest
    
    Returns:
        List of recommended songs
    """
    try:
        logger.info(f"[Recommend] Getting recommendations for session {request.session_id}, emotion: {request.emotion}")
        
        # Check cache
        cache_key = f"recommend:live:{request.session_id}:{request.emotion}"
        cached = await cache_get(cache_key)
        if cached:
            logger.info(f"[Recommend] Recommendations retrieved from cache")
            return [SongSchema(**song) for song in cached]
        
        # Get recommendations
        logger.info(f"[Recommend] Calling recommendation engine...")
        engine = get_recommendation_engine()
        cognitive_dict = request.cognitive_data.model_dump()
        
        try:
            recommendations = await engine.get_recommendations(
                emotion=request.emotion,
                cognitive_data=cognitive_dict,
                user_id=None,
                session_id=request.session_id
            )
            logger.info(f"[Recommend] Engine returned {len(recommendations)} recommendations")
        except Exception as engine_err:
            logger.error(f"[Recommend] Recommendation engine failed: {str(engine_err)}")
            logger.error(f"[Recommend] Traceback: {traceback.format_exc()}")
            logger.info(f"[Recommend] Returning empty list as fallback")
            recommendations = []
        
        if not recommendations:
            logger.warning(f"[Recommend] No recommendations generated, returning empty list")
            return []
        
        # Cache results
        cached_data = [song.model_dump() for song in recommendations]
        await cache_set(cache_key, cached_data, expiry=600)  # Cache for 10 minutes
        
        # Update session
        db = get_db()
        await db.sessions.update_one(
            {"_id": request.session_id},
            {
                "$set": {
                    "recommended_songs": cached_data,
                    "cognitive_data": cognitive_dict
                }
            }
        )
        
        logger.info(f"[Recommend] Generated {len(recommendations)} recommendations for session {request.session_id}")
        return recommendations
        
    except Exception as e:
        logger.error(f"[Recommend] Unexpected error in recommendation: {str(e)}")
        logger.error(f"[Recommend] Traceback: {traceback.format_exc()}")
        logger.info(f"[Recommend] Returning empty list as fallback")
        # Return empty list instead of error - at least the user sees no songs but no crash
        return []


@router.post("/recommend/final", response_model=List[SongSchema])
async def recommend_final(request: RecommendFinalRequest):
    """
    Get final recommendations after PostTest
    
    Args:
        emotion: Detected emotion
        session_id: Session identifier
        cognitive_data: Updated cognitive metrics from PostTest
        feedback: User feedback and session rating
    
    Returns:
        List of recommended songs based on session outcome
    """
    try:
        # Get recommendations with updated cognitive data
        engine = get_recommendation_engine()
        cognitive_dict = request.cognitive_data.model_dump()
        feedback_dict = request.feedback.model_dump()
        
        recommendations = await engine.get_recommendations(
            emotion=request.emotion,
            cognitive_data=cognitive_dict,
            user_id=None,
            session_id=request.session_id
        )
        
        # Update session with final recommendations and feedback
        db = get_db()
        recommendations_data = [song.model_dump() for song in recommendations]
        await db.sessions.update_one(
            {"_id": request.session_id},
            {
                "$set": {
                    "final_recommended_songs": recommendations_data,
                    "final_cognitive_data": cognitive_dict,
                    "feedback": feedback_dict
                }
            }
        )
        
        logger.info(f"Generated {len(recommendations)} final recommendations for session {request.session_id}")
        return recommendations
        
    except Exception as e:
        logger.error(f"Final recommendation error: {e}")
        raise HTTPException(status_code=500, detail="Final recommendation generation failed")
