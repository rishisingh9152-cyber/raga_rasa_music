import requests
import re

# Get the HTML to find the JS bundle name
r = requests.get('https://raga-rasa-music-52.vercel.app/music-player', timeout=15)
html = r.text

# Look for the index JS file
matches = re.findall(r'<script[^>]*src="([^"]*index[^"]*\.js)', html)
if matches:
    print(f'Found {len(matches)} index JS files:')
    for match in matches[:3]:
        print(f'  {match}')
        
        # Try to fetch the file to see if it has our changes
        if match.startswith('/'):
            url = 'https://raga-rasa-music-52.vercel.app' + match
        else:
            url = 'https://raga-rasa-music-52.vercel.app/' + match
        
        try:
            js_r = requests.get(url, timeout=10)
            # Look for our new code
            if 'Filtered out' in js_r.text or 'validSongs' in js_r.text:
                print(f'    ✓ NEW CODE found in {match}')
            elif 'getSongsByRasa' in js_r.text:
                if 'by_rasa' in js_r.text:
                    print(f'    ✓ Updated API extraction found in {match}')
                else:
                    print(f'    ✗ OLD CODE (no by_rasa extraction) in {match}')
            else:
                print(f'    ? Cannot verify {match}')
        except Exception as e:
            print(f'    Error fetching {match}: {e}')
else:
    print('Could not find index JS file in HTML')
