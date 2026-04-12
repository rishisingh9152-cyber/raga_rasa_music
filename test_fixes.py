import requests
import json

# Test emotion service
print('TEST 1: Emotion Service')
resp = requests.get('https://raga-rasa-music.onrender.com/health', timeout=10)
print(f'  Status: {resp.status_code}')
data = resp.json()
detector_init = data.get('detector_initialized')
print(f'  Detector initialized: {detector_init}')
print()

# Test recommendation with lowercase emotion
print('TEST 2: Recommendation Engine (with lowercase emotion)')
payload = {
    'emotion': 'happy',
    'session_id': 'test_123',
    'cognitive_data': {}
}
resp = requests.post('https://raga-rasa-backend.onrender.com/api/recommend/live', json=payload, timeout=30)
print(f'  Status: {resp.status_code}')
if resp.status_code == 200:
    data = resp.json()
    count = len(data) if isinstance(data, list) else 0
    print(f'  Songs returned: {count}')
    if count > 0:
        first_song = data[0]
        print(f'  First song: {first_song.get("title")} ({first_song.get("rasa")})')
else:
    print(f'  Error: {resp.text[:150]}')
print()

# Test songs by rasa
print('TEST 3: Songs by Rasa')
resp = requests.get('https://raga-rasa-backend.onrender.com/api/songs/by-rasa?rasa=Shringar', timeout=30)
print(f'  Status: {resp.status_code}')
if resp.status_code == 200:
    data = resp.json()
    total = data.get('total', 0)
    print(f'  Total songs: {total}')
    if total > 0:
        first = data.get('songs', [{}])[0]
        print(f'  First song: {first.get("title")}')
else:
    print(f'  Error: {resp.text[:150]}')
