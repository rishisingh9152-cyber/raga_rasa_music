#!/usr/bin/env python3
"""Test all emotions on deployed backend"""

import requests
import json

BASE_URL = 'https://raga-rasa-backend.onrender.com'

emotions_to_test = ["Happy", "Sad", "Angry", "Fearful", "Neutral"]

print("=" * 70)
print("TESTING DEPLOYED BACKEND - ALL EMOTIONS")
print("=" * 70)

# Create a session first
print('\nCreating session...')
session_resp = requests.post(f'{BASE_URL}/api/session/start', json={})

if session_resp.status_code != 200:
    print(f'Error creating session: {session_resp.text}')
    exit(1)

session_id = session_resp.json().get('session_id')
print(f'Session ID: {session_id}')

print("\nTesting emotions:")
print("-" * 70)

for emotion in emotions_to_test:
    print(f'\nEmotion: {emotion}')
    
    rec_resp = requests.post(
        f'{BASE_URL}/api/recommend/live',
        json={
            'emotion': emotion,
            'session_id': session_id,
            'cognitive_data': {
                'memory_score': 4,
                'reaction_time': 250,
                'accuracy_score': 85
            }
        },
        timeout=10
    )
    
    if rec_resp.status_code == 200:
        recs = rec_resp.json()
        num_recs = len(recs) if isinstance(recs, list) else len(recs.get('recommendations', []))
        print(f'  Status: OK')
        print(f'  Recommendations: {num_recs}')
        
        if isinstance(recs, list) and recs:
            for i, song in enumerate(recs[:3], 1):
                title = song.get('title', 'Unknown')
                rasa = song.get('rasa', 'Unknown')
                confidence = song.get('confidence', 0)
                print(f'    [{i}] {title} ({rasa}) - {confidence:.2f}')
        elif isinstance(recs, dict) and recs.get('recommendations'):
            for i, song in enumerate(recs['recommendations'][:3], 1):
                title = song.get('title', 'Unknown')
                rasa = song.get('rasa', 'Unknown')
                confidence = song.get('confidence', 0)
                print(f'    [{i}] {title} ({rasa}) - {confidence:.2f}')
    else:
        print(f'  Status: ERROR {rec_resp.status_code}')
        print(f'  Response: {rec_resp.text[:200]}')

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)
