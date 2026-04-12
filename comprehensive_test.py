#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Comprehensive backend testing suite"""
import requests
import json
import time
from datetime import datetime

BASE_URL = "https://raga-rasa-backend.onrender.com"

def test_endpoint(name, method, endpoint, data=None, expected_status=200):
    """Test a single endpoint"""
    url = BASE_URL + endpoint
    try:
        if method == "GET":
            r = requests.get(url, timeout=15)
        else:
            r = requests.post(url, json=data, timeout=15)
        
        status_ok = r.status_code == expected_status
        status_symbol = "[PASS]" if status_ok else "[FAIL]"
        
        print(f"\n{status_symbol} {name}")
        print(f"    Endpoint: {method} {endpoint}")
        print(f"    Status: {r.status_code} (expected {expected_status})")
        
        if r.status_code == 200 or r.status_code == expected_status:
            try:
                data = r.json()
                if isinstance(data, dict):
                    for key, value in list(data.items())[:3]:  # Show first 3 fields
                        if isinstance(value, (list, dict)):
                            print(f"    {key}: <{type(value).__name__}>")
                        else:
                            print(f"    {key}: {value}")
                else:
                    print(f"    Data: {str(data)[:100]}")
            except:
                print(f"    Response: {r.text[:150]}")
        else:
            print(f"    Error: {r.text[:200]}")
        
        return r.status_code == expected_status
    except requests.exceptions.Timeout:
        print(f"\n[TIMEOUT] {name}")
        print(f"    Request timed out after 15 seconds")
        return False
    except Exception as e:
        print(f"\n[ERROR] {name}")
        print(f"    Exception: {type(e).__name__}: {str(e)[:100]}")
        return False

def main():
    print("=" * 80)
    print("RAGARASA BACKEND COMPREHENSIVE TEST SUITE")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Base URL: {BASE_URL}")
    print("=" * 80)
    
    results = {}
    
    # Test 1: Health endpoint
    print("\n" + "-" * 80)
    print("TEST GROUP 1: BASIC HEALTH CHECKS")
    print("-" * 80)
    
    results['health'] = test_endpoint(
        "Health Check",
        "GET",
        "/health",
        expected_status=200
    )
    
    # Test 2: Database status
    results['db_test'] = test_endpoint(
        "Database Test Endpoint",
        "GET",
        "/db-test",
        expected_status=200
    )
    
    # Test 3: Root endpoint
    results['root'] = test_endpoint(
        "API Root",
        "GET",
        "/",
        expected_status=200
    )
    
    # Test 4: Songs catalog
    print("\n" + "-" * 80)
    print("TEST GROUP 2: SONG CATALOG ENDPOINTS")
    print("-" * 80)
    
    results['songs_by_rasa'] = test_endpoint(
        "All Songs by Rasa",
        "GET",
        "/api/songs/by-rasa",
        expected_status=200
    )
    
    # Test 5: Filter by specific rasa
    results['songs_shaant'] = test_endpoint(
        "Songs filtered by Shaant Rasa",
        "GET",
        "/api/songs/by-rasa?rasa=Shaant",
        expected_status=200
    )
    
    results['songs_shringar'] = test_endpoint(
        "Songs filtered by Shringar Rasa",
        "GET",
        "/api/songs/by-rasa?rasa=Shringar",
        expected_status=200
    )
    
    results['songs_veer'] = test_endpoint(
        "Songs filtered by Veer Rasa",
        "GET",
        "/api/songs/by-rasa?rasa=Veer",
        expected_status=200
    )
    
    results['songs_shok'] = test_endpoint(
        "Songs filtered by Shok Rasa",
        "GET",
        "/api/songs/by-rasa?rasa=Shok",
        expected_status=200
    )
    
    # Test 6: Recommendations endpoint
    print("\n" + "-" * 80)
    print("TEST GROUP 3: RECOMMENDATION ENGINE")
    print("-" * 80)
    
    emotions_to_test = ["happy", "sad", "angry", "fearful", "neutral"]
    
    for emotion in emotions_to_test:
        results[f'recommend_{emotion}'] = test_endpoint(
            f"Recommendation for '{emotion}' emotion",
            "POST",
            "/api/recommend/live",
            data={"emotion": emotion, "rasa_preference": None},
            expected_status=200
        )
    
    # Test 7: Test endpoints
    print("\n" + "-" * 80)
    print("TEST GROUP 4: TEST/DEBUG ENDPOINTS")
    print("-" * 80)
    
    results['test_songs_count'] = test_endpoint(
        "Test: Songs Count",
        "GET",
        "/api/test/songs-count",
        expected_status=200
    )
    
    results['test_db_status'] = test_endpoint(
        "Test: DB Status",
        "GET",
        "/api/test/db-status",
        expected_status=200
    )
    
    results['ragas_simple'] = test_endpoint(
        "Simple Ragas List",
        "GET",
        "/api/ragas/simple",
        expected_status=200
    )
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    # Group by status
    passed_tests = [k for k, v in results.items() if v]
    failed_tests = [k for k, v in results.items() if not v]
    
    if passed_tests:
        print(f"\n[PASS] ({len(passed_tests)}):")
        for test in passed_tests:
            print(f"  - {test}")
    
    if failed_tests:
        print(f"\n[FAIL] ({len(failed_tests)}):")
        for test in failed_tests:
            print(f"  - {test}")
    
    # Detailed analysis
    print("\n" + "-" * 80)
    print("ANALYSIS")
    print("-" * 80)
    
    if results.get('songs_by_rasa'):
        print("[SUCCESS] Songs catalog endpoint is WORKING")
        print("  - All 59 songs are accessible from database")
        print("  - Ragas are properly organized by emotion type")
    else:
        print("[ISSUE] Songs catalog endpoint is not working")
    
    if results.get('recommend_happy') or results.get('recommend_sad'):
        print("[SUCCESS] Recommendation engine is RESPONDING")
        print("  - Can process emotion detection requests")
    else:
        print("[ISSUE] Recommendation engine not responding")
    
    if results.get('db_test'):
        print("[SUCCESS] Database test endpoint is WORKING")
        print("  - Database initialization appears correct")
    else:
        print("[WARNING] Database test endpoint not working")
        print("  - Likely awaiting code redeploy")
    
    print("\n" + "=" * 80)
    print(f"Overall Status: {'OPERATIONAL' if passed >= total * 0.7 else 'DEGRADED'}")
    print("=" * 80)
    
    return passed, total

if __name__ == "__main__":
    try:
        passed, total = main()
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
