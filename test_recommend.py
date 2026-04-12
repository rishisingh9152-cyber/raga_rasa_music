import requests

payload = {
    'emotion': 'happy',
    'session_id': 'test_123',
    'cognitive_data': {}
}
resp = requests.post('https://raga-rasa-backend.onrender.com/api/recommend/live', json=payload, timeout=15)
print('Status:', resp.status_code)
content = resp.text
if resp.status_code == 200:
    print('Success! Got recommendations')
    data = resp.json()
    if 'recommendations' in data:
        recs_count = len(data['recommendations'])
        print(f'Recommendations count: {recs_count}')
        if recs_count > 0:
            print(f'First rec: {data["recommendations"][0]}')
else:
    print('Error:', content[:300])
