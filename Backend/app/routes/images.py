"""Session image capture endpoints"""

from fastapi import APIRouter, HTTPException, Query, File, UploadFile
import logging
from datetime import datetime
from typing import Optional
from uuid import uuid4
from pathlib import Path

from app.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter()

# Session images storage directory
IMAGES_BASE_DIR = Path("C:/RagaRasa/Sessions")


@router.post("/image/capture")
async def capture_session_image(
    session_id: str,
    emotion_detected: Optional[str] = None,
    confidence: Optional[float] = None,
    file: Optional[UploadFile] = File(None)
):
    """
    Record a captured image during a session
    
    Args:
        session_id: Session ID
        emotion_detected: Detected emotion from image
        confidence: Confidence score
        file: Optional image file
    
    Returns:
        Created image record
    """
    try:
        if confidence is not None and (confidence < 0 or confidence > 1):
            raise HTTPException(status_code=400, detail="Confidence must be between 0 and 1")
        
        db = get_db()
        
        image_id = f"image_{uuid4().hex[:12]}"
        
        # Save file if provided
        image_path = None
        if file:
            try:
                # Create session directory
                session_dir = IMAGES_BASE_DIR / session_id
                session_dir.mkdir(parents=True, exist_ok=True)
                
                # Save file
                timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
                file_path = session_dir / f"{timestamp}_{file.filename}"
                
                contents = await file.read()
                with open(file_path, "wb") as f:
                    f.write(contents)
                
                image_path = str(file_path)
                logger.info(f"Saved image to {image_path}")
                
            except Exception as e:
                logger.warning(f"Could not save image file: {e}")
                # Continue anyway - we can still record the image metadata
        
        # Create image document
        image_doc = {
            "_id": image_id,
            "image_id": image_id,
            "session_id": session_id,
            "timestamp": datetime.utcnow(),
            "image_path": image_path,
            "emotion_detected": emotion_detected,
            "confidence": confidence or 0.0,
            "created_at": datetime.utcnow()
        }
        
        result = await db.images.insert_one(image_doc)
        
        # Add image ID to session
        await db.sessions.update_one(
            {"_id": session_id},
            {
                "$addToSet": {"images": image_id},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        logger.info(f"Created image record {image_id} for session {session_id}")
        
        return {
            "status": "success",
            "image_id": image_id,
            "message": "Image captured successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to capture image: {e}")
        raise HTTPException(status_code=500, detail="Failed to capture image")


@router.get("/image/{image_id}")
async def get_image_metadata(image_id: str):
    """
    Get image metadata
    
    Args:
        image_id: Image ID
    
    Returns:
        Image metadata
    """
    try:
        db = get_db()
        
        image = await db.images.find_one({"_id": image_id})
        
        if not image:
            raise HTTPException(status_code=404, detail=f"Image {image_id} not found")
        
        return image
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get image: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve image")


@router.get("/images")
async def list_images(
    session_id: Optional[str] = Query(None),
    emotion_detected: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    skip: int = Query(0, ge=0)
):
    """
    List images with optional filters
    
    Args:
        session_id: Filter by session ID
        emotion_detected: Filter by detected emotion
        limit: Number of results
        skip: Number of results to skip
    
    Returns:
        List of images
    """
    try:
        db = get_db()
        
        query = {}
        if session_id:
            query["session_id"] = session_id
        if emotion_detected:
            query["emotion_detected"] = emotion_detected
        
        total = await db.images.count_documents(query)
        
        images = await db.images.find(query).sort("timestamp", -1).skip(skip).limit(limit).to_list(None)
        
        logger.info(f"Listed images: {len(images)} of {total} total")
        
        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "count": len(images),
            "images": images
        }
        
    except Exception as e:
        logger.error(f"Failed to list images: {e}")
        raise HTTPException(status_code=500, detail="Failed to list images")


@router.get("/session/{session_id}/images")
async def get_session_images(session_id: str, limit: int = Query(100, ge=1, le=500)):
    """
    Get all images for a session
    
    Args:
        session_id: Session ID
        limit: Maximum number of images to return
    
    Returns:
        List of images for the session
    """
    try:
        db = get_db()
        
        images = await db.images.find({"session_id": session_id}).sort("timestamp", 1).limit(limit).to_list(None)
        
        logger.info(f"Retrieved {len(images)} images for session {session_id}")
        
        return {
            "session_id": session_id,
            "image_count": len(images),
            "images": images
        }
        
    except Exception as e:
        logger.error(f"Failed to get session images: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve session images")


@router.delete("/image/{image_id}")
async def delete_image(image_id: str):
    """
    Delete an image record and file
    
    Args:
        image_id: Image ID to delete
    
    Returns:
        Deletion status
    """
    try:
        db = get_db()
        
        # Get image record
        image = await db.images.find_one({"_id": image_id})
        
        if not image:
            raise HTTPException(status_code=404, detail=f"Image {image_id} not found")
        
        # Delete file if it exists
        if image.get("image_path"):
            try:
                file_path = Path(image["image_path"])
                if file_path.exists():
                    file_path.unlink()
                    logger.info(f"Deleted image file: {image['image_path']}")
            except Exception as e:
                logger.warning(f"Could not delete image file: {e}")
        
        # Delete from database
        await db.images.delete_one({"_id": image_id})
        
        # Remove from session
        if image.get("session_id"):
            await db.sessions.update_one(
                {"_id": image["session_id"]},
                {"$pull": {"images": image_id}}
            )
        
        logger.info(f"Deleted image {image_id}")
        
        return {"status": "success", "message": f"Image {image_id} deleted"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete image: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete image")


@router.get("/session/{session_id}/emotion-timeline")
async def get_emotion_timeline(session_id: str):
    """
    Get emotion detection timeline for a session
    
    Args:
        session_id: Session ID
    
    Returns:
        Timeline of emotion detections from images
    """
    try:
        db = get_db()
        
        images = await db.images.find({"session_id": session_id}).sort("timestamp", 1).to_list(None)
        
        # Extract emotion timeline
        timeline = [
            {
                "timestamp": img.get("timestamp"),
                "emotion": img.get("emotion_detected"),
                "confidence": img.get("confidence"),
                "image_id": img.get("_id")
            }
            for img in images if img.get("emotion_detected")
        ]
        
        logger.info(f"Retrieved emotion timeline for session {session_id}: {len(timeline)} entries")
        
        return {
            "session_id": session_id,
            "total_images": len(images),
            "emotion_detections": len(timeline),
            "timeline": timeline
        }
        
    except Exception as e:
        logger.error(f"Failed to get emotion timeline: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve emotion timeline")
