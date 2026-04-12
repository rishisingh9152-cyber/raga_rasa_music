#!/usr/bin/env python3
"""Check what's in Cloudinary"""

import cloudinary
import cloudinary.api

cloudinary.config(
    cloud_name='dlx3ufj3t',
    api_key='255318353319693',
    api_secret='MKFvdiyfmNpzxbaGKBMFM6SlT2c'
)

try:
    # List resources in the raga-rasa/songs folder
    result = cloudinary.api.resources(prefix='raga-rasa/songs', max_results=10)
    resources = result.get('resources', [])
    print(f'Found {len(resources)} resources in Cloudinary:')
    for res in resources[:5]:
        public_id = res.get('public_id')
        secure_url = res.get('secure_url')
        print(f'  - {public_id}')
        print(f'    URL: {secure_url}')
    
    print(f'\nTotal in folder: {result.get("total_count", "unknown")}')
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
