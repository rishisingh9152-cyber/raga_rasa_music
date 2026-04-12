import requests
import json

r = requests.get("https://raga-rasa-backend.onrender.com/api/songs/by-rasa", timeout=10)
data = r.json()

print("Response structure:")
print(json.dumps({k: type(v).__name__ for k, v in data.items()}, indent=2))

print("\nby_rasa structure:")
by_rasa = data.get('by_rasa', {})
for rasa, songs in by_rasa.items():
    print(f"\n{rasa}: {len(songs)} songs")
    if songs:
        song = songs[0]
        print(f"  Keys: {list(song.keys())}")
        
        # Check all songs in this rasa for missing titles
        missing_titles = [s for s in songs if not s.get('title')]
        if missing_titles:
            print(f"  WARNING: {len(missing_titles)} songs without titles!")
            print(f"  Example: {missing_titles[0]}")
        else:
            print(f"  All {len(songs)} songs have titles")
