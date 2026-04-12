#!/usr/bin/env python3
"""Monitor Vercel deployment for new JS bundle"""
import requests
import time
import re

BASE_URL = "https://raga-rasa-music-52.vercel.app"

def get_js_filename():
    """Get the current JS bundle filename"""
    try:
        r = requests.get(f"{BASE_URL}/music-player", timeout=10)
        matches = re.findall(r'src="(/assets/index-[^"]*\.js)"', r.text)
        if matches:
            return matches[0].split('/')[-1]
    except:
        pass
    return None

print("=" * 70)
print("Vercel Frontend Deployment Monitor")
print("=" * 70)

initial_js = get_js_filename()
print(f"\nInitial JS file: {initial_js}")

print("\nWaiting for new build...")
for attempt in range(1, 31):
    time.sleep(10)
    current_js = get_js_filename()
    
    print(f"[{attempt:2d}] {current_js}", end="")
    
    if current_js and current_js != initial_js:
        print(" <- NEW BUILD DETECTED!")
        print("\n" + "=" * 70)
        print("SUCCESS: Vercel has rebuilt with new code!")
        print("=" * 70)
        break
    else:
        print()

if attempt == 30:
    print("\nTimeout: Vercel rebuild took longer than expected")
    print("Please manually check: https://raga-rasa-music-52.vercel.app/music-player")
