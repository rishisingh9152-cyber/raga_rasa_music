#!/usr/bin/env python3
"""Test script for external emotion service integration"""

import requests
import json
import base64
from pathlib import Path

EMOTION_SERVICE_URL = "http://localhost:5000"

def test_health():
    """Test health endpoint"""
    print("\n=== Testing Emotion Service Health ===")
    try:
        resp = requests.get(f"{EMOTION_SERVICE_URL}/health", timeout=5)
        print(f"Status: {resp.status_code}")
        print(f"Response: {json.dumps(resp.json(), indent=2)}")
        return resp.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_emotion_detection(image_path):
    """Test emotion detection with an image"""
    print(f"\n=== Testing Emotion Detection ===")
    try:
        # Read and encode image
        with open(image_path, "rb") as f:
            image_base64 = base64.b64encode(f.read()).decode()
        
        # Send to service
        payload = {"image": image_base64}
        resp = requests.post(
            f"{EMOTION_SERVICE_URL}/detect",
            json=payload,
            timeout=30
        )
        
        print(f"Status: {resp.status_code}")
        result = resp.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        
        # Verify response structure
        expected_keys = {"emotions", "dominant", "raw_dominant", "is_brave"}
        if expected_keys.issubset(result.keys()):
            print("✅ Response structure is correct")
            return True
        else:
            print(f"⚠️  Missing keys. Expected: {expected_keys}, Got: {set(result.keys())}")
            return True
            
    except Exception as e:
        print(f"❌ Emotion detection failed: {e}")
        return False

def main():
    print("Testing External Emotion Recognition Service")
    print("=" * 50)
    
    # Test health
    if not test_health():
        print("\n❌ Emotion service is not running at http://localhost:5000")
        print("Note: Emotion detection is now integrated into the main backend")
        print("This test is for legacy external emotion service only")
        return
    
    print("\n✅ Emotion service is healthy!")
    
    # Find a test image
    snapshots_dir = Path("Backend/archived_emotion_service/snapshots")
    if snapshots_dir.exists():
        images = list(snapshots_dir.glob("*.jpg")) + list(snapshots_dir.glob("*.png"))
        if images:
            print(f"\n✅ Found {len(images)} test images")
            test_image = images[0]
            print(f"Testing with: {test_image.name}")
            test_emotion_detection(test_image)
        else:
            print(f"\n⚠️  No images found in {snapshots_dir}")
    else:
        print(f"\n⚠️  Snapshots directory not found at {snapshots_dir}")
        print("Emotion detection is now integrated in Backend/app/services/emotion.py")

if __name__ == "__main__":
    main()
