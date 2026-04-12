#!/usr/bin/env python3
"""Test database and songs endpoints"""
import requests

BASE_URL = 'https://raga-rasa-backend.onrender.com'

# Test 1: DB test
print('Testing /db-test...')
try:
    r = requests.get(f'{BASE_URL}/db-test', timeout=30)
    print(f'Status: {r.status_code}')
    if r.status_code == 200:
        data = r.json()
        status = data.get("status")
        total = data.get("total_songs")
        initialized = data.get("initialized")
        print(f'Response: status={status}, total_songs={total}, initialized={initialized}')
        if status == "success" and total == 59:
            print('[SUCCESS] Database initialized correctly!')
    else:
        print(f'Error: Got status {r.status_code}')
except Exception as e:
    print(f'Exception: {e}')

# Test 2: Songs by rasa
print('\nTesting /api/songs/by-rasa...')
try:
    r = requests.get(f'{BASE_URL}/api/songs/by-rasa', timeout=30)
    print(f'Status: {r.status_code}')
    if r.status_code == 200:
        data = r.json()
        total = data.get("total")
        print(f'Total songs: {total}')
        by_rasa = data.get('by_rasa', {})
        for rasa in sorted(by_rasa.keys()):
            count = len(by_rasa[rasa])
            print(f'  {rasa}: {count} songs')
        print(f'[SUCCESS] Retrieved all {total} songs!')
    else:
        print(f'Error: Got status {r.status_code}')
except Exception as e:
    print(f'Exception: {e}')
