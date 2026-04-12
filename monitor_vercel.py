#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Monitor Vercel frontend deployment"""
import requests
import time
from datetime import datetime

BASE_URL = "https://raga-rasa-music-52.vercel.app"

def test_music_player():
    """Test if music player page loads without errors"""
    try:
        response = requests.get(f"{BASE_URL}/music-player", timeout=15)
        
        if response.status_code == 200:
            # Check for error indicators in HTML
            content = response.text
            
            # Look for the error message
            if "Cannot read properties of undefined" in content:
                return False, "Error still present in page"
            if "localeCompare" in content:
                return False, "Error code still present"
            
            # Check for music player content
            if "Music Player" in content or "music-player" in content.lower():
                return True, "Music player page loaded successfully"
            
            return True, f"Page loaded (status {response.status_code})"
        else:
            return False, f"HTTP {response.status_code}"
    except Exception as e:
        return False, str(e)

def main():
    print("=" * 70)
    print("Vercel Frontend Deployment Monitor")
    print(f"URL: {BASE_URL}/music-player")
    print("=" * 70)
    
    max_attempts = 30
    attempt = 0
    
    while attempt < max_attempts:
        attempt += 1
        print(f"\n[{attempt}/{max_attempts}] {datetime.now().strftime('%H:%M:%S')}")
        
        success, message = test_music_player()
        
        if success:
            print(f"[SUCCESS] {message}")
            print("\n" + "=" * 70)
            print("VERCEL DEPLOYMENT SUCCESSFUL!")
            print("=" * 70)
            return True
        else:
            print(f"[CHECKING] {message}")
        
        if attempt < max_attempts:
            print("Waiting 10 seconds...")
            time.sleep(10)
    
    print("\n" + "=" * 70)
    print("TIMEOUT: Vercel deployment did not complete within 5 minutes")
    print("=" * 70)
    return False

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
