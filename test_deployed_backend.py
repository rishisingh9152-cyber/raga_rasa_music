#!/usr/bin/env python3
"""Test deployed backend recommendations"""

import requests
import json

BASE_URL = 'https://raga-rasa-backend.onrender.com'

# Create a session first
print('Creating session...')
session_resp = requests.post(f'{BASE_URL}/api/session/start', json={})
print(f'Session response: {session_resp.status_code}')

if session_resp.status_code == 200:
    session_id = session_resp.json().get('session_id')
    print(f'Session ID: {session_id}')
    
    # Try to get recommendations
    print(f'\nGetting recommendations for emotion: Happy')
    rec_resp = requests.post(
        f'{BASE_URL}/api/recommend/live',
        json={
            'emotion': 'Happy',
            'session_id': session_id,
            'cognitive_data': {
                'memory_score': 4,
                'reaction_time': 250,
                'accuracy_score': 85
            }
        },
        timeout=10
    )
    print(f'Recommendation response: {rec_resp.status_code}')
    if rec_resp.status_code == 200:
        recs = rec_resp.json()
        print(f'Response type: {type(recs)}')
        print(f'Response: {json.dumps(recs, indent=2)[:500]}')
        
        # Handle both dict and list responses
        if isinstance(recs, list):
            num_recs = len(recs)
            recs_list = recs
        else:
            num_recs = len(recs.get('recommendations', []))
            recs_list = recs.get('recommendations', [])
        
        print(f'Number of recommendations: {num_recs}')
        if recs_list:
            for i, song in enumerate(recs_list[:3], 1):
                print(f'  [{i}] {song.get("title") if isinstance(song, dict) else song} - {song.get("rasa") if isinstance(song, dict) else "N/A"}')
        else:
            print('No recommendations returned!')
    else:
        print(f'Error: {rec_resp.text}')
else:
    print(f'Error: {session_resp.text}')
