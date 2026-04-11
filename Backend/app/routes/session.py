"""Session management endpoints"""

from fastapi import APIRouter, HTTPException, Query, Depends
from uuid import uuid4
from datetime import datetime
import logging
import traceback
from typing import List, Optional, Dict, Any

from app.database import get_db
from app.models import SessionCreateSchema, SessionSchema, CognitiveDataSchema
from app.dependencies.auth import get_current_user_optional, get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/session/start", response_model=SessionCreateSchema)
async def start_session(current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional)):
    """
    Initialize a new therapy session
    
    Requires: JWT token (optional, but recommended)
    
    Returns:
        Session ID for tracking throughout the session
    """
    session_id = str(uuid4())
    
    try:
        logger.info(f"[Session Start] Initiating session creation: {session_id}")
        
        # Get database instance
        try:
            db = get_db()
            logger.info(f"[Session Start] Database instance obtained")
        except RuntimeError as db_err:
            logger.error(f"[Session Start] Database not initialized: {db_err}")
            raise HTTPException(
                status_code=503,
                detail="Database service unavailable. Please ensure MongoDB is running."
            )
        
        # Create comprehensive session document
        session_doc = {
            "_id": session_id,
            "session_id": session_id,
            "user_id": current_user.get("user_id") if current_user else None,
            "created_at": datetime.utcnow(),
            "started_at": None,
            "ended_at": None,
            "emotion": None,
            "rasa": None,
            "confidence": 0.0,
            "cognitive_data": None,
            "feedback": None,
            "recommended_songs": [],
            "played_songs": [],
            "ratings": [],
            "images": [],
            "psychometric_tests": [],
            "status": "active",
            "duration_minutes": 0,
            "updated_at": datetime.utcnow()
        }
        
        logger.info(f"[Session Start] Inserting session document into database")
        
        # Insert into database
        result = await db.sessions.insert_one(session_doc)
        logger.info(f"[Session Start] Session created successfully: {session_id}, inserted_id: {result.inserted_id}")
        
        return SessionCreateSchema(
            session_id=session_id,
            created_at=session_doc["created_at"],
            message="Session initialized"
        )
        
    except HTTPException:
        # Re-raise HTTPException (already has proper status code and message)
        raise
    except Exception as e:
        logger.error(f"[Session Start] Unexpected error creating session {session_id}: {str(e)}")
        logger.error(f"[Session Start] Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create session: {str(e)}"
        )


@router.get("/session/{session_id}")
async def get_session(session_id: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Retrieve complete session details
    
    Args:
        session_id: Session ID
    
    Returns:
        Complete session document with all relationships
    """
    try:
        db = get_db()
        
        session = await db.sessions.find_one({"_id": session_id})
        
        if not session:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
        # Verify user owns this session
        if session.get("user_id") != current_user.get("user_id"):
            raise HTTPException(status_code=403, detail="Not authorized to access this session")
        
        logger.info(f"Retrieved session: {session_id}")
        return session
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get session {session_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve session")


@router.get("/sessions")
async def list_sessions(
    current_user: Dict[str, Any] = Depends(get_current_user),
    status: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=500),
    skip: int = Query(0, ge=0)
):
    """
    List sessions for the authenticated user with optional filters
    
    Args:
        status: Filter by status (active, completed, cancelled)
        limit: Number of results
        skip: Number of results to skip
    
    Returns:
        List of sessions for authenticated user only
    """
    try:
        db = get_db()
        
        # Always filter by current user's ID
        query = {"user_id": current_user.get("user_id")}
        if status:
            query["status"] = status
        
        # Get total count
        total = await db.sessions.count_documents(query)
        
        # Get paginated results
        sessions = await db.sessions.find(query).sort("created_at", -1).skip(skip).limit(limit).to_list(None)
        
        logger.info(f"Listed sessions for user {current_user.get('user_id')}: {len(sessions)} of {total} total")
        
        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "count": len(sessions),
            "sessions": sessions
        }
        
    except Exception as e:
        logger.error(f"Failed to list sessions: {e}")
        raise HTTPException(status_code=500, detail="Failed to list sessions")


@router.put("/session/{session_id}/update-emotion")
async def update_session_emotion(session_id: str, emotion: str, rasa: str, confidence: float = 0.9, current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Update session with detected emotion and assigned rasa
    
    Args:
        session_id: Session ID
        emotion: Detected emotion
        rasa: Assigned rasa
        confidence: Confidence score (0-1)
    
    Returns:
        Updated session
    """
    try:
        if confidence < 0 or confidence > 1:
            raise HTTPException(status_code=400, detail="Confidence must be between 0 and 1")
        
        db = get_db()
        
        # Verify session exists and user owns it
        session = await db.sessions.find_one({"_id": session_id})
        if not session:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
        if session.get("user_id") != current_user.get("user_id"):
            raise HTTPException(status_code=403, detail="Not authorized to modify this session")
        
        result = await db.sessions.update_one(
            {"_id": session_id},
            {
                "$set": {
                    "emotion": emotion,
                    "rasa": rasa,
                    "confidence": confidence,
                    "started_at": datetime.utcnow(),
                    "status": "active",
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
        session = await db.sessions.find_one({"_id": session_id})
        logger.info(f"Updated session {session_id} emotion: {emotion}, rasa: {rasa}")
        
        return session
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update session emotion: {e}")
        raise HTTPException(status_code=500, detail="Failed to update session")


@router.put("/session/{session_id}/add-song")
async def add_song_to_session(session_id: str, song_id: str, song_type: str = "played", current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Add a song to session's played or recommended list
    
    Args:
        session_id: Session ID
        song_id: Song ID to add
        song_type: "played" or "recommended"
    
    Returns:
        Updated session
    """
    try:
        if song_type not in ["played", "recommended"]:
            raise HTTPException(status_code=400, detail="song_type must be 'played' or 'recommended'")
        
        db = get_db()
        
        # Verify session exists and user owns it
        session = await db.sessions.find_one({"_id": session_id})
        if not session:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
        if session.get("user_id") != current_user.get("user_id"):
            raise HTTPException(status_code=403, detail="Not authorized to modify this session")
        
        field = "played_songs" if song_type == "played" else "recommended_songs"
        
        result = await db.sessions.update_one(
            {"_id": session_id},
            {
                "$addToSet": {field: song_id},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
        session = await db.sessions.find_one({"_id": session_id})
        logger.info(f"Added {song_type} song {song_id} to session {session_id}")
        
        return session
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to add song to session: {e}")
        raise HTTPException(status_code=500, detail="Failed to add song")


@router.put("/session/{session_id}/complete")
async def complete_session(session_id: str, feedback: Optional[dict] = None, current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Mark session as completed
    
    Args:
        session_id: Session ID
        feedback: Optional feedback dictionary
    
    Returns:
        Completed session
    """
    try:
        db = get_db()
        
        # Verify session exists and user owns it
        session = await db.sessions.find_one({"_id": session_id})
        if not session:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
        if session.get("user_id") != current_user.get("user_id"):
            raise HTTPException(status_code=403, detail="Not authorized to modify this session")
        
        end_time = datetime.utcnow()
        
        result = await db.sessions.update_one(
            {"_id": session_id},
            {
                "$set": {
                    "ended_at": end_time,
                    "status": "completed",
                    "feedback": feedback,
                    "updated_at": end_time
                }
            }
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
        session = await db.sessions.find_one({"_id": session_id})
        
        # Calculate duration
        if session.get("started_at"):
            duration = (end_time - session["started_at"]).total_seconds() / 60
            await db.sessions.update_one(
                {"_id": session_id},
                {"$set": {"duration_minutes": round(duration, 2)}}
            )
            session["duration_minutes"] = round(duration, 2)
        
        logger.info(f"Completed session {session_id}")
        
        return session
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to complete session: {e}")
        raise HTTPException(status_code=500, detail="Failed to complete session")


@router.get("/session/{session_id}/summary")
async def get_session_summary(session_id: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get a summary of session activities
    
    Args:
        session_id: Session ID
    
    Returns:
        Session summary with statistics
    """
    try:
        db = get_db()
        
        session = await db.sessions.find_one({"_id": session_id})
        
        if not session:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
        # Verify user owns this session
        if session.get("user_id") != current_user.get("user_id"):
            raise HTTPException(status_code=403, detail="Not authorized to access this session")
        
        # Get additional statistics - filter by both session_id AND user_id
        ratings = await db.ratings.find({"session_id": session_id, "user_id": current_user.get("user_id")}).to_list(None)
        images = await db.images.find({"session_id": session_id}).to_list(None)
        tests = await db.psychometric_tests.find({"session_id": session_id, "user_id": current_user.get("user_id")}).to_list(None)
        
        avg_rating = sum(r.get("rating", 0) for r in ratings) / len(ratings) if ratings else 0
        
        summary = {
            "session_id": session_id,
            "emotion": session.get("emotion"),
            "rasa": session.get("rasa"),
            "duration_minutes": session.get("duration_minutes", 0),
            "status": session.get("status"),
            "songs_played": len(session.get("played_songs", [])),
            "songs_rated": len(ratings),
            "average_rating": round(avg_rating, 2),
            "images_captured": len(images),
            "tests_completed": len(tests),
            "created_at": session.get("created_at"),
            "ended_at": session.get("ended_at"),
            "feedback": session.get("feedback")
        }
        
        logger.info(f"Generated session summary for {session_id}")
        
        return summary
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get session summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to get session summary")
