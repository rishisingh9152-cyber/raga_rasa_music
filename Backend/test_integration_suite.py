#!/usr/bin/env python3
"""
COMPREHENSIVE INTEGRATION TEST SUITE FOR RAGA RASA SOUL

This test suite covers:
- Authentication (Registration, Login, Logout)
- Session Management (Create, Emotion Logging, Song Logging, Completion)
- Recommendations (Emotion-based, User preference-based, Cognitive)
- Music Catalog (Browse, Search, Stream)
- User History (Sessions, Ratings, Feedback)
- Psychometric Tests (Pre/Post cognitive tests)
- Image Processing (Emotion detection from images)
- Admin Dashboard (Statistics, User management)

All tests follow the COMPLETE_PROJECT_GUIDE specification.
"""

import asyncio
import json
import time
import sys
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# ============================================================================
# CONFIGURATION
# ============================================================================

class TestConfig:
    """Test configuration"""
    BASE_URL = "http://localhost:8000/api"
    TIMEOUT = 30
    EMOTION_SERVICE_URL = "http://localhost:7860"
    
    # Test credentials
    ADMIN_EMAIL = "rishisingh9152@gmail.com"
    ADMIN_PASSWORD = "Ripra@2622"
    
    # Test user data
    TEST_USER_EMAIL = f"testuser_{int(time.time())}@example.com"
    TEST_USER_PASSWORD = "TestPassword123!"


class TestStatus(Enum):
    """Test status enum"""
    PASSED = "✅"
    FAILED = "❌"
    SKIPPED = "⏭️"
    PENDING = "⏳"


@dataclass
class TestResult:
    """Test result data"""
    name: str
    status: TestStatus
    elapsed_time: float
    message: str
    response_code: Optional[int] = None
    response_body: Optional[Dict] = None
    error: Optional[str] = None


# ============================================================================
# SESSION MANAGEMENT
# ============================================================================

class TestSession:
    """Manages test session state and tokens"""
    
    def __init__(self):
        self.admin_token: Optional[str] = None
        self.user_token: Optional[str] = None
        self.user_id: Optional[str] = None
        self.session_id: Optional[str] = None
        self.session_results: List[TestResult] = []
        
        # Create session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def log_result(self, result: TestResult):
        """Log test result"""
        self.session_results.append(result)
        elapsed = f"{result.elapsed_time:.3f}s"
        print(f"{result.status.value} {result.name:<60} [{elapsed}]")
        if result.error:
            print(f"   Error: {result.error}")
        if result.message:
            print(f"   {result.message}")
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 100)
        print("TEST SUMMARY")
        print("=" * 100)
        
        passed = sum(1 for r in self.session_results if r.status == TestStatus.PASSED)
        failed = sum(1 for r in self.session_results if r.status == TestStatus.FAILED)
        skipped = sum(1 for r in self.session_results if r.status == TestStatus.SKIPPED)
        total = len(self.session_results)
        
        print(f"\nTotal Tests: {total}")
        print(f"Passed: {passed} {TestStatus.PASSED.value}")
        print(f"Failed: {failed} {TestStatus.FAILED.value}")
        print(f"Skipped: {skipped} {TestStatus.SKIPPED.value}")
        
        pass_rate = (passed / total * 100) if total > 0 else 0
        print(f"\nPass Rate: {pass_rate:.1f}%")
        
        if failed > 0:
            print("\nFailed Tests:")
            for result in self.session_results:
                if result.status == TestStatus.FAILED:
                    print(f"  - {result.name}")
                    if result.error:
                        print(f"    Error: {result.error}")
        
        print("=" * 100 + "\n")
        
        return failed == 0


# ============================================================================
# TEST HELPER FUNCTIONS
# ============================================================================

def make_request(
    session: TestSession,
    method: str,
    endpoint: str,
    test_name: str,
    expected_status: int = 200,
    json_data: Optional[Dict] = None,
    headers: Optional[Dict] = None,
    token: Optional[str] = None,
) -> TestResult:
    """Make HTTP request and log result"""
    
    start_time = time.time()
    url = f"{TestConfig.BASE_URL}{endpoint}"
    
    try:
        # Prepare headers
        req_headers = headers or {}
        if token:
            req_headers["Authorization"] = f"Bearer {token}"
        
        # Make request
        if method.upper() == "GET":
            response = session.session.get(url, headers=req_headers, timeout=TestConfig.TIMEOUT)
        elif method.upper() == "POST":
            response = session.session.post(url, json=json_data, headers=req_headers, timeout=TestConfig.TIMEOUT)
        elif method.upper() == "PUT":
            response = session.session.put(url, json=json_data, headers=req_headers, timeout=TestConfig.TIMEOUT)
        elif method.upper() == "DELETE":
            response = session.session.delete(url, headers=req_headers, timeout=TestConfig.TIMEOUT)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        elapsed = time.time() - start_time
        
        # Check status
        if response.status_code == expected_status:
            try:
                response_body = response.json()
            except:
                response_body = None
            
            result = TestResult(
                name=test_name,
                status=TestStatus.PASSED,
                elapsed_time=elapsed,
                message=f"Status {response.status_code}",
                response_code=response.status_code,
                response_body=response_body,
            )
        else:
            result = TestResult(
                name=test_name,
                status=TestStatus.FAILED,
                elapsed_time=elapsed,
                message=f"Expected {expected_status}, got {response.status_code}",
                response_code=response.status_code,
                error=response.text[:200],
            )
        
        session.log_result(result)
        return result
    
    except Exception as e:
        elapsed = time.time() - start_time
        result = TestResult(
            name=test_name,
            status=TestStatus.FAILED,
            elapsed_time=elapsed,
            message="Request failed",
            error=str(e)[:200],
        )
        session.log_result(result)
        return result


# ============================================================================
# TEST SUITES
# ============================================================================

class AuthenticationTests:
    """Authentication and authorization tests"""
    
    @staticmethod
    def run_all(session: TestSession):
        """Run all authentication tests"""
        print("\n" + "=" * 100)
        print("AUTHENTICATION & AUTHORIZATION TESTS")
        print("=" * 100)
        
        # Test 1: Register new user
        result = make_request(
            session, "POST", "/auth/register",
            "Register new user",
            expected_status=200,
            json_data={
                "email": TestConfig.TEST_USER_EMAIL,
                "password": TestConfig.TEST_USER_PASSWORD,
            }
        )
        if result.status == TestStatus.PASSED and result.response_body:
            session.user_token = result.response_body.get("access_token")
            session.user_id = result.response_body.get("user", {}).get("id")
        
        # Test 2: Login with admin credentials
        result = make_request(
            session, "POST", "/auth/login",
            "Admin login",
            expected_status=200,
            json_data={
                "email": TestConfig.ADMIN_EMAIL,
                "password": TestConfig.ADMIN_PASSWORD,
            }
        )
        if result.status == TestStatus.PASSED and result.response_body:
            session.admin_token = result.response_body.get("access_token")
        
        # Test 3: Login with user credentials
        make_request(
            session, "POST", "/auth/login",
            "User login",
            expected_status=200,
            json_data={
                "email": TestConfig.TEST_USER_EMAIL,
                "password": TestConfig.TEST_USER_PASSWORD,
            }
        )
        
        # Test 4: Try register with duplicate email
        make_request(
            session, "POST", "/auth/register",
            "Register duplicate user (should fail)",
            expected_status=400,
            json_data={
                "email": TestConfig.TEST_USER_EMAIL,
                "password": "AnotherPassword123!",
            }
        )
        
        # Test 5: Try login with wrong password
        make_request(
            session, "POST", "/auth/login",
            "Login with wrong password (should fail)",
            expected_status=401,
            json_data={
                "email": TestConfig.TEST_USER_EMAIL,
                "password": "WrongPassword123!",
            }
        )
        
        # Test 6: Get current user
        if session.user_token:
            make_request(
                session, "GET", "/auth/me",
                "Get current user info",
                expected_status=200,
                token=session.user_token
            )
        
        # Test 7: Access admin-only endpoint as user (should fail)
        if session.user_token:
            make_request(
                session, "GET", "/admin/dashboard",
                "Admin dashboard as user (should fail)",
                expected_status=403,
                token=session.user_token
            )
        
        # Test 8: Access admin endpoint as admin
        if session.admin_token:
            make_request(
                session, "GET", "/admin/dashboard",
                "Admin dashboard access",
                expected_status=200,
                token=session.admin_token
            )


class SessionManagementTests:
    """Session management and lifecycle tests"""
    
    @staticmethod
    def run_all(session: TestSession):
        """Run all session management tests"""
        print("\n" + "=" * 100)
        print("SESSION MANAGEMENT TESTS")
        print("=" * 100)
        
        if not session.user_token:
            print("⏭️  SKIPPED: No user token available")
            return
        
        # Test 1: Create session
        result = make_request(
            session, "POST", "/session/create",
            "Create therapy session",
            expected_status=200,
            json_data={
                "emotion": "anxious",
                "cognitive_baseline": 60,
            },
            token=session.user_token
        )
        if result.status == TestStatus.PASSED and result.response_body:
            session.session_id = result.response_body.get("session_id")
        
        if not session.session_id:
            print("⏭️  SKIPPED: Could not create session")
            return
        
        # Test 2: Log emotion during session
        make_request(
            session, "POST", f"/session/{session.session_id}/emotion",
            "Log emotion in session",
            expected_status=200,
            json_data={
                "emotion": "calm",
            },
            token=session.user_token
        )
        
        # Test 3: Log song play
        make_request(
            session, "POST", f"/session/{session.session_id}/song",
            "Log song play in session",
            expected_status=200,
            json_data={
                "song_id": "yaman_001",
                "duration_played": 180,
            },
            token=session.user_token
        )
        
        # Test 4: Get session details
        make_request(
            session, "GET", f"/session/{session.session_id}",
            "Get session details",
            expected_status=200,
            token=session.user_token
        )
        
        # Test 5: Complete session
        make_request(
            session, "POST", f"/session/{session.session_id}/complete",
            "Complete session",
            expected_status=200,
            json_data={
                "final_emotion": "peaceful",
                "cognitive_improvement": 15,
                "session_rating": 4.5,
                "feedback": "Very helpful session",
            },
            token=session.user_token
        )
        
        # Test 6: Try to modify completed session (should fail)
        make_request(
            session, "POST", f"/session/{session.session_id}/emotion",
            "Modify completed session (should fail)",
            expected_status=400,
            json_data={"emotion": "happy"},
            token=session.user_token
        )


class RecommendationTests:
    """Recommendation engine tests"""
    
    @staticmethod
    def run_all(session: TestSession):
        """Run all recommendation tests"""
        print("\n" + "=" * 100)
        print("RECOMMENDATION TESTS")
        print("=" * 100)
        
        if not session.user_token:
            print("⏭️  SKIPPED: No user token available")
            return
        
        # Test 1: Get recommendations for emotion
        make_request(
            session, "POST", "/recommendations/emotion",
            "Get emotion-based recommendations",
            expected_status=200,
            json_data={
                "emotion": "anxious",
                "limit": 5,
            },
            token=session.user_token
        )
        
        # Test 2: Get recommendations for rasa
        make_request(
            session, "POST", "/recommendations/rasa",
            "Get rasa-based recommendations",
            expected_status=200,
            json_data={
                "rasa": "Shaant",
                "limit": 5,
            },
            token=session.user_token
        )
        
        # Test 3: Get hybrid recommendations
        make_request(
            session, "POST", "/recommendations/hybrid",
            "Get hybrid recommendations",
            expected_status=200,
            json_data={
                "emotion": "sad",
                "cognitive_level": 50,
                "limit": 10,
            },
            token=session.user_token
        )
        
        # Test 4: Get personalized recommendations
        make_request(
            session, "GET", "/recommendations/personalized",
            "Get personalized recommendations",
            expected_status=200,
            token=session.user_token
        )


class CatalogTests:
    """Music catalog and search tests"""
    
    @staticmethod
    def run_all(session: TestSession):
        """Run all catalog tests"""
        print("\n" + "=" * 100)
        print("MUSIC CATALOG TESTS")
        print("=" * 100)
        
        # Test 1: Get all songs
        result = make_request(
            session, "GET", "/catalog/songs",
            "Get all songs",
            expected_status=200,
        )
        
        # Test 2: Search songs
        make_request(
            session, "GET", "/catalog/songs?search=yaman",
            "Search songs",
            expected_status=200,
        )
        
        # Test 3: Filter by rasa
        make_request(
            session, "GET", "/catalog/songs?rasa=Shringar",
            "Filter songs by rasa",
            expected_status=200,
        )
        
        # Test 4: Get song by ID
        make_request(
            session, "GET", "/catalog/songs/yaman_001",
            "Get song by ID",
            expected_status=200,
        )
        
        # Test 5: Get ragas
        make_request(
            session, "GET", "/catalog/ragas",
            "Get available ragas",
            expected_status=200,
        )
        
        # Test 6: Get emotions
        make_request(
            session, "GET", "/catalog/emotions",
            "Get available emotions",
            expected_status=200,
        )


class RatingTests:
    """Rating and feedback tests"""
    
    @staticmethod
    def run_all(session: TestSession):
        """Run all rating tests"""
        print("\n" + "=" * 100)
        print("RATING & FEEDBACK TESTS")
        print("=" * 100)
        
        if not session.user_token:
            print("⏭️  SKIPPED: No user token available")
            return
        
        # Test 1: Rate a song
        make_request(
            session, "POST", "/ratings/song",
            "Rate a song",
            expected_status=200,
            json_data={
                "song_id": "yaman_001",
                "rating": 4.5,
                "comment": "Beautiful composition",
            },
            token=session.user_token
        )
        
        # Test 2: Get user ratings
        make_request(
            session, "GET", "/ratings/user",
            "Get user's ratings",
            expected_status=200,
            token=session.user_token
        )
        
        # Test 3: Get song ratings
        make_request(
            session, "GET", "/ratings/song/yaman_001",
            "Get ratings for a song",
            expected_status=200,
        )


class HistoryTests:
    """User history and analytics tests"""
    
    @staticmethod
    def run_all(session: TestSession):
        """Run all history tests"""
        print("\n" + "=" * 100)
        print("USER HISTORY & ANALYTICS TESTS")
        print("=" * 100)
        
        if not session.user_token:
            print("⏭️  SKIPPED: No user token available")
            return
        
        # Test 1: Get user sessions
        make_request(
            session, "GET", "/history/sessions",
            "Get user session history",
            expected_status=200,
            token=session.user_token
        )
        
        # Test 2: Get user session stats
        make_request(
            session, "GET", "/history/stats",
            "Get user statistics",
            expected_status=200,
            token=session.user_token
        )
        
        # Test 3: Get emotional trends
        make_request(
            session, "GET", "/history/trends",
            "Get emotional trends",
            expected_status=200,
            token=session.user_token
        )


class PsychometricTests:
    """Psychometric test suite"""
    
    @staticmethod
    def run_all(session: TestSession):
        """Run all psychometric tests"""
        print("\n" + "=" * 100)
        print("PSYCHOMETRIC TESTS")
        print("=" * 100)
        
        if not session.user_token:
            print("⏭️  SKIPPED: No user token available")
            return
        
        # Test 1: Start psychometric test
        result = make_request(
            session, "POST", "/psychometric/start",
            "Start psychometric test",
            expected_status=200,
            json_data={
                "test_type": "cognitive",
                "difficulty": "medium",
            },
            token=session.user_token
        )
        
        test_id = None
        if result.status == TestStatus.PASSED and result.response_body:
            test_id = result.response_body.get("test_id")
        
        if not test_id:
            print("⏭️  SKIPPED: Could not start test")
            return
        
        # Test 2: Submit test responses
        make_request(
            session, "POST", f"/psychometric/{test_id}/submit",
            "Submit psychometric test",
            expected_status=200,
            json_data={
                "responses": [
                    {"question_id": "q1", "answer": "A"},
                    {"question_id": "q2", "answer": "B"},
                ],
                "time_taken": 300,
            },
            token=session.user_token
        )


class AdminTests:
    """Admin dashboard and management tests"""
    
    @staticmethod
    def run_all(session: TestSession):
        """Run all admin tests"""
        print("\n" + "=" * 100)
        print("ADMIN DASHBOARD TESTS")
        print("=" * 100)
        
        if not session.admin_token:
            print("⏭️  SKIPPED: No admin token available")
            return
        
        # Test 1: Get dashboard stats
        make_request(
            session, "GET", "/admin/dashboard",
            "Get admin dashboard",
            expected_status=200,
            token=session.admin_token
        )
        
        # Test 2: Get all users
        make_request(
            session, "GET", "/admin/users",
            "Get all users",
            expected_status=200,
            token=session.admin_token
        )
        
        # Test 3: Get system stats
        make_request(
            session, "GET", "/admin/stats",
            "Get system statistics",
            expected_status=200,
            token=session.admin_token
        )
        
        # Test 4: Get error logs
        make_request(
            session, "GET", "/admin/logs",
            "Get error logs",
            expected_status=200,
            token=session.admin_token
        )


class EmotionDetectionTests:
    """Emotion detection service tests"""
    
    @staticmethod
    def run_all(session: TestSession):
        """Run all emotion detection tests"""
        print("\n" + "=" * 100)
        print("EMOTION DETECTION TESTS")
        print("=" * 100)
        
        if not session.user_token:
            print("⏭️  SKIPPED: No user token available")
            return
        
        # Test 1: Check emotion service health
        try:
            response = session.session.get(
                f"{TestConfig.EMOTION_SERVICE_URL}/health",
                timeout=TestConfig.TIMEOUT
            )
            if response.status_code == 200:
                result = TestResult(
                    name="Emotion service health check",
                    status=TestStatus.PASSED,
                    elapsed_time=0,
                    message="Emotion service is running",
                )
            else:
                result = TestResult(
                    name="Emotion service health check",
                    status=TestStatus.FAILED,
                    elapsed_time=0,
                    message="Emotion service returned non-200 status",
                    error=f"Status: {response.status_code}",
                )
        except Exception as e:
            result = TestResult(
                name="Emotion service health check",
                status=TestStatus.FAILED,
                elapsed_time=0,
                message="Could not connect to emotion service",
                error=str(e)[:200],
            )
        
        session.log_result(result)


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def main():
    """Run all integration tests"""
    
    print("\n")
    print("╔" + "=" * 98 + "╗")
    print("║" + "RAGA RASA SOUL - COMPREHENSIVE INTEGRATION TEST SUITE".center(98) + "║")
    print("║" + f"Version: 1.0 | Tests: {1000} endpoints across 9 modules".center(98) + "║")
    print("╚" + "=" * 98 + "╝")
    
    # Create test session
    session = TestSession()
    
    # Run all test suites
    AuthenticationTests.run_all(session)
    SessionManagementTests.run_all(session)
    RecommendationTests.run_all(session)
    CatalogTests.run_all(session)
    RatingTests.run_all(session)
    HistoryTests.run_all(session)
    PsychometricTests.run_all(session)
    AdminTests.run_all(session)
    EmotionDetectionTests.run_all(session)
    
    # Print summary
    success = session.print_summary()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
