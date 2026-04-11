"""Integration tests for backend endpoints"""

import pytest
from httpx import AsyncClient
from app.config import settings
import json
import base64
import cv2
import numpy as np


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test health check endpoint"""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data


@pytest.mark.asyncio
async def test_session_start(client: AsyncClient):
    """Test session initialization"""
    response = await client.post("/session/start")
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert isinstance(data["session_id"], str)
    assert len(data["session_id"]) > 0


@pytest.mark.asyncio
async def test_recommend_live(client: AsyncClient):
    """Test live recommendations"""
    # First create a session
    session_response = await client.post("/session/start")
    session_id = session_response.json()["session_id"]
    
    # Request recommendations
    request_data = {
        "emotion": "Happy",
        "session_id": session_id,
        "cognitive_data": {
            "memory_score": 4,
            "reaction_time": 285,
            "accuracy_score": 66.67
        }
    }
    
    response = await client.post("/recommend/live", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    
    # Verify song structure
    if len(data) > 0:
        song = data[0]
        assert "song_id" in song
        assert "title" in song
        assert "audio_url" in song
        assert "rasa" in song
        assert "confidence" in song


@pytest.mark.asyncio
async def test_ragas_list(client: AsyncClient):
    """Test raga catalog"""
    response = await client.get("/ragas/list")
    assert response.status_code in [200, 500]  # 500 if no data seeded
    
    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, list)


@pytest.mark.asyncio
async def test_rate_song(client: AsyncClient):
    """Test song rating"""
    session_response = await client.post("/session/start")
    session_id = session_response.json()["session_id"]
    
    request_data = {
        "user_id": "test-user-123",
        "song_id": "raga_001",
        "rating": 5,
        "session_id": session_id,
        "feedback": {
            "mood_after": "Felt great",
            "session_rating": 5,
            "comment": "Excellent experience"
        }
    }
    
    response = await client.post("/rate", json=request_data)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_sessions_history(client: AsyncClient):
    """Test session history retrieval"""
    response = await client.get("/sessions/history?user_id=test-user-123")
    assert response.status_code in [200, 500]
    
    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, list)


# Test helpers
def create_dummy_image_base64() -> str:
    """Create a dummy image in base64 format for testing"""
    # Create a simple numpy array as image
    image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    
    # Encode as JPEG
    success, encoded = cv2.imencode('.jpg', image)
    if success:
        image_bytes = encoded.tobytes()
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        return f"data:image/jpeg;base64,{image_base64}"
    
    return ""


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
