"""User rating endpoints"""

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import uuid4

from app.database import get_db
from app.models import FeedbackSchema
from app.dependencies.auth import get_current_user_optional

logger = logging.getLogger(__name__)

router = APIRouter()


class RateSongRequest(BaseModel):
    """Song rating request"""
    user_id: Optional[str] = None  # Optional - will use JWT if available
    song_id: str
    rating: int = Field(..., ge=1, le=5, description="Rating 1-5 stars")
    session_id: str
    feedback: Optional[FeedbackSchema] = None


class SimpleSongRatingRequest(BaseModel):
    """Simple song rating request for music player"""
    song_id: str
    song_title: str
    rasa: str
    rating: int = Field(..., ge=1, le=5, description="Rating 1-5 stars")
    session_id: Optional[str] = None
    feedback_text: Optional[str] = None
    emotion_before: Optional[str] = None
    emotion_after: Optional[str] = None
    user_id: Optional[str] = None  # Optional - will use session or generated ID if not provided


@router.post("/rate")
async def rate_song_detailed(
    request: RateSongRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional)
):
    """
    Store detailed user's song rating and feedback
    
    Args:
        user_id: User identifier (optional - uses JWT if available)
        song_id: Song identifier
        rating: Rating 1-5 stars
        session_id: Session identifier
        feedback: User feedback
    
    Returns:
        Created rating document
    """
    try:
        db = get_db()
        
        # Use JWT user_id if available, otherwise use provided user_id
        user_id = current_user.get("user_id") if current_user else request.user_id
        
        rating_id = f"rating_{uuid4().hex[:12]}"
        
        # Create rating document
        rating_doc = {
            "_id": rating_id,
            "rating_id": rating_id,
            "user_id": user_id,
            "song_id": request.song_id,
            "rating": request.rating,
            "session_id": request.session_id,
            "feedback": request.feedback.model_dump() if request.feedback else None,
            "timestamp": datetime.utcnow(),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Insert rating
        result = await db.ratings.insert_one(rating_doc)
        
        # Add rating ID to session
        await db.sessions.update_one(
            {"_id": request.session_id},
            {
                "$addToSet": {"ratings": rating_id},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        logger.info(f"Rating saved: user={user_id}, song={request.song_id}, rating={request.rating}, session={request.session_id}")
        
        return {
            "status": "success",
            "rating_id": rating_id,
            "message": "Rating saved successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to save rating: {e}")
        raise HTTPException(status_code=500, detail="Failed to save rating")


@router.post("/rate-song")
async def rate_song_simple(
    request: SimpleSongRatingRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional)
):
    """
    Simple song rating endpoint for music player
    
    Args:
        song_id: Song identifier
        song_title: Song title
        rasa: Rasa classification
        rating: Rating 1-5 stars
        session_id: Optional session ID
        feedback_text: Optional user comments
        emotion_before: Emotion before listening
        emotion_after: Emotion after listening
        user_id: Optional user identifier (uses JWT if available, generates anonymous ID if not)
    
    Returns:
        Success response with rating data
    """
    try:
        db = get_db()
        
        # Use JWT user_id if available, otherwise use provided user_id or generate anonymous one
        if current_user:
            user_id = current_user.get("user_id")
        else:
            user_id = request.user_id or f"anon_{uuid4().hex[:8]}"
        
        rating_id = f"rating_{uuid4().hex[:12]}"
        
        # Create rating document
        rating_doc = {
            "_id": rating_id,
            "rating_id": rating_id,
            "user_id": user_id,
            "song_id": request.song_id,
            "song_title": request.song_title,
            "rasa": request.rasa,
            "rating": request.rating,
            "session_id": request.session_id,
            "feedback_text": request.feedback_text or "",
            "emotion_before": request.emotion_before,
            "emotion_after": request.emotion_after,
            "timestamp": datetime.utcnow(),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Insert rating
        result = await db.ratings.insert_one(rating_doc)
        
        # Add rating to session if session_id provided
        if request.session_id:
            await db.sessions.update_one(
                {"_id": request.session_id},
                {
                    "$addToSet": {"ratings": rating_id},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
        
        logger.info(f"Song rated: user={user_id}, song={request.song_id}, rating={request.rating}")
        
        return {
            "status": "success",
            "message": "Rating saved successfully",
            "rating_id": rating_id,
            "rating": request.rating
        }
        
    except Exception as e:
        logger.error(f"Failed to save song rating: {e}")
        raise HTTPException(status_code=500, detail="Failed to save rating")


@router.get("/song/{song_id}/ratings")
async def get_song_ratings(song_id: str):
    """
    Get all ratings for a specific song
    
    Args:
        song_id: Song identifier
    
    Returns:
        List of ratings and average rating
    """
    try:
        db = get_db()
        
        # Find all ratings for this song
        ratings = await db.ratings.find({"song_id": song_id}).to_list(None)
        
        if not ratings:
            return {
                "song_id": song_id,
                "average_rating": 0,
                "total_ratings": 0,
                "ratings": []
            }
        
        # Calculate average rating
        total_rating = sum(r.get("rating", 0) for r in ratings)
        average_rating = total_rating / len(ratings) if ratings else 0
        
        logger.info(f"Retrieved {len(ratings)} ratings for song {song_id}")
        
        return {
            "song_id": song_id,
            "average_rating": round(average_rating, 2),
            "total_ratings": len(ratings),
            "ratings": ratings
        }
        
    except Exception as e:
        logger.error(f"Failed to get song ratings: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve ratings")


@router.get("/rating/{rating_id}")
async def get_rating(rating_id: str):
    """
    Get a specific rating by ID
    
    Args:
        rating_id: Rating ID
    
    Returns:
        Rating document
    """
    try:
        db = get_db()
        
        rating = await db.ratings.find_one({"_id": rating_id})
        
        if not rating:
            raise HTTPException(status_code=404, detail=f"Rating {rating_id} not found")
        
        return rating
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get rating: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve rating")


@router.get("/ratings")
async def list_ratings(
    user_id: Optional[str] = Query(None),
    session_id: Optional[str] = Query(None),
    song_id: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=500),
    skip: int = Query(0, ge=0)
):
    """
    List ratings with optional filters
    
    Args:
        user_id: Filter by user ID
        session_id: Filter by session ID
        song_id: Filter by song ID
        limit: Number of results
        skip: Number of results to skip
    
    Returns:
        List of ratings with metadata
    """
    try:
        db = get_db()
        
        # Build query
        query = {}
        if user_id:
            query["user_id"] = user_id
        if session_id:
            query["session_id"] = session_id
        if song_id:
            query["song_id"] = song_id
        
        # Get total count
        total = await db.ratings.count_documents(query)
        
        # Get paginated results
        ratings = await db.ratings.find(query).sort("timestamp", -1).skip(skip).limit(limit).to_list(None)
        
        logger.info(f"Listed ratings: {len(ratings)} of {total} total")
        
        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "count": len(ratings),
            "ratings": ratings
        }
        
    except Exception as e:
        logger.error(f"Failed to list ratings: {e}")
        raise HTTPException(status_code=500, detail="Failed to list ratings")


@router.put("/rating/{rating_id}")
async def update_rating(rating_id: str, rating: int = Query(..., ge=1, le=5), feedback_text: Optional[str] = None):
    """
    Update a rating
    
    Args:
        rating_id: Rating ID
        rating: New rating value (1-5)
        feedback_text: Optional new feedback
    
    Returns:
        Updated rating document
    """
    try:
        db = get_db()
        
        update_data = {
            "rating": rating,
            "updated_at": datetime.utcnow()
        }
        
        if feedback_text is not None:
            update_data["feedback_text"] = feedback_text
        
        result = await db.ratings.update_one(
            {"_id": rating_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail=f"Rating {rating_id} not found")
        
        updated_rating = await db.ratings.find_one({"_id": rating_id})
        logger.info(f"Updated rating {rating_id}")
        
        return updated_rating
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update rating: {e}")
        raise HTTPException(status_code=500, detail="Failed to update rating")


@router.delete("/rating/{rating_id}")
async def delete_rating(rating_id: str):
    """
    Delete a rating
    
    Args:
        rating_id: Rating ID to delete
    
    Returns:
        Deletion status
    """
    try:
        db = get_db()
        
        # First get the rating to find session_id
        rating = await db.ratings.find_one({"_id": rating_id})
        
        if not rating:
            raise HTTPException(status_code=404, detail=f"Rating {rating_id} not found")
        
        # Delete the rating
        result = await db.ratings.delete_one({"_id": rating_id})
        
        # Remove from session
        if rating.get("session_id"):
            await db.sessions.update_one(
                {"_id": rating["session_id"]},
                {"$pull": {"ratings": rating_id}}
            )
        
        logger.info(f"Deleted rating {rating_id}")
        
        return {"status": "success", "message": f"Rating {rating_id} deleted"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete rating: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete rating")
