#!/usr/bin/env python3
"""Check /db-test error message"""
import requests
import json

BASE_URL = 'https://raga-rasa-backend.onrender.com'

r = requests.get(f'{BASE_URL}/db-test', timeout=30)
print(f'Status: {r.status_code}')
data = r.json()
print(json.dumps(data, indent=2))
