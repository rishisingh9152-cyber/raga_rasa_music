"""Frontend-Backend Connection Test"""

import requests
import json
import time

# URLs
BACKEND_URL = "http://localhost:8000"
API_BASE = f"{BACKEND_URL}/api"
FRONTEND_URL = "http://localhost:8081"

def test_backend_health():
    """Test if backend is healthy"""
    print("=" * 70)
    print("1. Testing Backend Health")
    print("=" * 70)
    
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        print(f"✓ Status: {response.status_code}")
        print(f"  Response: {json.dumps(response.json(), indent=2)}")
        return True
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False

def test_session_creation():
    """Test session/start endpoint"""
    print("\n" + "=" * 70)
    print("2. Testing Session Creation (/api/session/start)")
    print("=" * 70)
    
    try:
        response = requests.post(
            f"{API_BASE}/session/start",
            headers={"Content-Type": "application/json"},
            json={},
            timeout=10
        )
        print(f"✓ Status: {response.status_code}")
        result = response.json()
        print(f"  Response: {json.dumps(result, indent=2)}")
        
        if "session_id" in result:
            print(f"✓ Session ID: {result['session_id']}")
            return result['session_id']
        else:
            print("✗ No session_id in response")
            return None
            
    except Exception as e:
        print(f"✗ Failed: {e}")
        return None

def test_emotion_service_health():
    """Test emotion service health through backend"""
    print("\n" + "=" * 70)
    print("3. Testing Emotion Service Health (/api/emotion-service/health)")
    print("=" * 70)
    
    try:
        response = requests.get(
            f"{API_BASE}/emotion-service/health",
            timeout=10
        )
        print(f"✓ Status: {response.status_code}")
        print(f"  Response: {json.dumps(response.json(), indent=2)}")
        return True
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False

def test_cors():
    """Test CORS headers"""
    print("\n" + "=" * 70)
    print("4. Testing CORS Configuration")
    print("=" * 70)
    
    try:
        response = requests.options(
            f"{API_BASE}/session/start",
            headers={
                "Origin": "http://localhost:8081",
                "Access-Control-Request-Method": "POST"
            },
            timeout=5
        )
        
        cors_headers = {
            "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
            "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
            "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers"),
        }
        
        print(f"✓ CORS Headers:")
        for key, value in cors_headers.items():
            print(f"  {key}: {value}")
        
        if cors_headers["Access-Control-Allow-Origin"]:
            return True
        else:
            print("⚠ CORS not properly configured")
            return False
            
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False

def test_all_endpoints():
    """Test all available endpoints"""
    print("\n" + "=" * 70)
    print("5. Testing All Available Endpoints")
    print("=" * 70)
    
    endpoints = [
        ("GET", "/catalog/ragas/list", None),
        ("GET", "/emotion-service/health", None),
        ("GET", "/history/sessions", None),
    ]
    
    for method, endpoint, payload in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{API_BASE}{endpoint}", timeout=5)
            else:
                response = requests.post(f"{API_BASE}{endpoint}", json=payload, timeout=5)
            
            print(f"✓ {method} {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"✗ {method} {endpoint}: {e}")

def main():
    print("\n")
    print("█" * 70)
    print("  FRONTEND-BACKEND CONNECTION TEST")
    print("█" * 70)
    
    print(f"\nBackend URL: {BACKEND_URL}")
    print(f"API Base: {API_BASE}")
    print(f"Frontend URL: {FRONTEND_URL}")
    
    # Run tests
    health = test_backend_health()
    session = test_session_creation()
    emotion = test_emotion_service_health()
    cors = test_cors()
    
    test_all_endpoints()
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    print(f"Backend Health:          {'✓ PASS' if health else '✗ FAIL'}")
    print(f"Session Creation:        {'✓ PASS' if session else '✗ FAIL'}")
    print(f"Emotion Service Health:  {'✓ PASS' if emotion else '✗ FAIL'}")
    print(f"CORS Configuration:      {'✓ PASS' if cors else '✗ FAIL'}")
    
    if all([health, session, emotion, cors]):
        print("\n✓ All tests passed! Frontend-Backend connection is working.")
    else:
        print("\n✗ Some tests failed. Check the errors above.")
    
    print("=" * 70)
    
    # Instructions
    print("\nNext Steps:")
    print("1. Open browser: http://localhost:8081")
    print("2. Go to Session page")
    print("3. Allow camera access")
    print("4. Click 'Capture Emotion'")
    print("5. Check if emotion is detected")

if __name__ == "__main__":
    main()
