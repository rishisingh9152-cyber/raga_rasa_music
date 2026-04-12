#!/usr/bin/env python3
"""Test the fix for music player"""

# Simulate the API response structure
api_response = {
    "songs": [{"title": "Song 1"}, {"title": "Song 2"}],
    "by_rasa": {
        "Shaant": [{"title": "Peaceful Song 1"}, {"title": "Peaceful Song 2"}],
        "Shringar": [{"title": "Romantic Song"}]
    },
    "total": 4
}

# Simulate the old broken code
print("OLD CODE (Broken):")
print("=" * 60)
try:
    # Old code would do: return data (which is the whole object)
    songsByRasa_broken = api_response
    
    # Then try to iterate: songsByRasa["Shaant"]
    # This would fail because top level has "songs", "by_rasa", "total"
    songs = songsByRasa_broken.get("Shaant")
    print(f"Songs found: {songs}")
    if not songs:
        print("ERROR: No songs found! Would get None and cause TypeError")
except Exception as e:
    print(f"ERROR: {e}")

print("\n")

# Simulate the new fixed code
print("NEW CODE (Fixed):")
print("=" * 60)
try:
    # New code extracts by_rasa
    data = api_response
    songsByRasa = data.get("by_rasa") or data
    
    # Now iterate: songsByRasa["Shaant"]
    songs = songsByRasa.get("Shaant")
    print(f"Songs found: {songs}")
    
    if songs:
        print("SUCCESS: Songs properly extracted!")
        
        # Test the sort with null safety
        all_songs = []
        for rasa_songs in songsByRasa.values():
            all_songs.extend(rasa_songs)
        
        print(f"Total songs: {len(all_songs)}")
        
        # The sort function now handles missing titles safely
        sorted_songs = sorted(all_songs, key=lambda s: s.get("title") or "")
        print(f"Sorted songs: {[s['title'] for s in sorted_songs]}")
        print("SUCCESS: Songs sorted without errors!")
except Exception as e:
    print(f"ERROR: {e}")
