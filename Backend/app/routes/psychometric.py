"""Psychometric test endpoints"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
import logging
from datetime import datetime
from typing import Optional
from uuid import uuid4

from app.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter()


class PsychometricTestDataRequest(BaseModel):
    """Test data"""
    memory_score: int = Field(..., ge=0, le=6)
    reaction_time: int = Field(..., ge=0)
    accuracy_score: float = Field(..., ge=0, le=100)


class PsychometricTestRequest(BaseModel):
    """Psychometric test request"""
    session_id: str
    user_id: Optional[str] = None
    test_type: str = Field(..., description="pre_test or post_test")
    data: PsychometricTestDataRequest
    notes: Optional[str] = None


class PsychometricTestResponse(BaseModel):
    """Psychometric test response"""
    test_id: str
    session_id: str
    user_id: Optional[str]
    test_type: str
    timestamp: datetime
    data: PsychometricTestDataRequest
    notes: Optional[str]
    created_at: datetime


@router.post("/psychometric-test")
async def create_psychometric_test(request: PsychometricTestRequest):
    """
    Create a psychometric test record
    
    Args:
        session_id: Associated session ID
        user_id: Associated user ID (optional)
        test_type: "pre_test" or "post_test"
        data: Test data (memory, reaction time, accuracy)
        notes: Optional notes
    
    Returns:
        Created test document
    """
    try:
        if request.test_type not in ["pre_test", "post_test"]:
            raise HTTPException(status_code=400, detail="test_type must be 'pre_test' or 'post_test'")
        
        db = get_db()
        
        test_id = f"test_{uuid4().hex[:12]}"
        
        test_doc = {
            "_id": test_id,
            "test_id": test_id,
            "session_id": request.session_id,
            "user_id": request.user_id,
            "test_type": request.test_type,
            "timestamp": datetime.utcnow(),
            "data": request.data.model_dump(),
            "notes": request.notes,
            "created_at": datetime.utcnow()
        }
        
        result = await db.psychometric_tests.insert_one(test_doc)
        
        # Add test ID to session
        await db.sessions.update_one(
            {"_id": request.session_id},
            {
                "$addToSet": {"psychometric_tests": test_id},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        logger.info(f"Created {request.test_type} for session {request.session_id}")
        
        return {
            "status": "success",
            "test_id": test_id,
            "message": f"{request.test_type} created successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create psychometric test: {e}")
        raise HTTPException(status_code=500, detail="Failed to create psychometric test")


@router.get("/psychometric-test/{test_id}")
async def get_psychometric_test(test_id: str):
    """
    Get a specific psychometric test
    
    Args:
        test_id: Test ID
    
    Returns:
        Test document
    """
    try:
        db = get_db()
        
        test = await db.psychometric_tests.find_one({"_id": test_id})
        
        if not test:
            raise HTTPException(status_code=404, detail=f"Test {test_id} not found")
        
        return test
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get psychometric test: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve test")


@router.get("/psychometric-tests")
async def list_psychometric_tests(
    session_id: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None),
    test_type: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=500),
    skip: int = Query(0, ge=0)
):
    """
    List psychometric tests with optional filters
    
    Args:
        session_id: Filter by session ID
        user_id: Filter by user ID
        test_type: Filter by test type (pre_test or post_test)
        limit: Number of results
        skip: Number of results to skip
    
    Returns:
        List of tests
    """
    try:
        db = get_db()
        
        query = {}
        if session_id:
            query["session_id"] = session_id
        if user_id:
            query["user_id"] = user_id
        if test_type:
            query["test_type"] = test_type
        
        total = await db.psychometric_tests.count_documents(query)
        
        tests = await db.psychometric_tests.find(query).sort("timestamp", -1).skip(skip).limit(limit).to_list(None)
        
        logger.info(f"Listed psychometric tests: {len(tests)} of {total} total")
        
        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "count": len(tests),
            "tests": tests
        }
        
    except Exception as e:
        logger.error(f"Failed to list psychometric tests: {e}")
        raise HTTPException(status_code=500, detail="Failed to list tests")


@router.get("/session/{session_id}/psychometric-comparison")
async def get_psychometric_comparison(session_id: str):
    """
    Get pre and post test comparison for a session
    
    Args:
        session_id: Session ID
    
    Returns:
        Pre-test, post-test, and improvement data
    """
    try:
        db = get_db()
        
        tests = await db.psychometric_tests.find({"session_id": session_id}).to_list(None)
        
        pre_test = next((t for t in tests if t.get("test_type") == "pre_test"), None)
        post_test = next((t for t in tests if t.get("test_type") == "post_test"), None)
        
        if not pre_test or not post_test:
            raise HTTPException(status_code=404, detail="Pre-test or post-test not found for this session")
        
        # Calculate improvements
        pre_data = pre_test.get("data", {})
        post_data = post_test.get("data", {})
        
        memory_improvement = post_data.get("memory_score", 0) - pre_data.get("memory_score", 0)
        reaction_time_improvement = pre_data.get("reaction_time", 0) - post_data.get("reaction_time", 0)  # Lower is better
        accuracy_improvement = post_data.get("accuracy_score", 0) - pre_data.get("accuracy_score", 0)
        
        comparison = {
            "session_id": session_id,
            "pre_test": pre_test,
            "post_test": post_test,
            "improvements": {
                "memory_score_change": memory_improvement,
                "reaction_time_improvement_ms": reaction_time_improvement,
                "accuracy_improvement_percent": round(accuracy_improvement, 2),
                "overall_improvement_percent": round(
                    (memory_improvement / 6 * 20 + reaction_time_improvement / 400 * 20 + accuracy_improvement * 0.6) / 10,
                    2
                )
            }
        }
        
        logger.info(f"Retrieved psychometric comparison for session {session_id}")
        
        return comparison
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get psychometric comparison: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve comparison")
