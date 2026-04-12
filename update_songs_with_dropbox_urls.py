#!/usr/bin/env python3
"""
Generate Dropbox streaming URLs for all songs in MongoDB
Using a helper approach to convert Dropbox folder links to direct streaming URLs
"""

import asyncio
import json
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Dict, List
import logging
import sys
import io

# Fix Unicode on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Your Dropbox folder share link
DROPBOX_FOLDER_LINK = "https://www.dropbox.com/scl/fo/2je1qltlw5zuhosbd96zf/AHQqoCAInjkdN7eNRykcuvo?rlkey=z799ezfme6xd2h5jzhjmswoy9&st=fmlelxg5&dl=0"

# Extract folder ID from the link
DROPBOX_FOLDER_ID = "2je1qltlw5zuhosbd96zf"
DROPBOX_RESOURCE_KEY = "z799ezfme6xd2h5jzhjmswoy9"

# Map song titles/IDs to Dropbox relative paths
# Format: song_id -> dropbox_relative_path
# These will be populated based on your Dropbox folder structure
DROPBOX_SONG_PATHS = {
    # Shringar songs
    "shringar/bageshwari_shringar": "Shringar/bageshwari_shringar.mp3",
    "shringar/bahar_amjadalikhan_rati": "Shringar/bahar_amjadalikhan_rati.mp3",
    "shringar/bilkashanitodi_kushaldas_rati": "Shringar/bilkashanitodi_kushaldas_rati.mp3",
    "shringar/desh_shringar": "Shringar/desh_shringar.mp3",
    "shringar/malkuans_shringar": "Shringar/malkuans_shringar.mp3",
    # Shaant songs (32 total)
    "shaant/desh_amjadalikhan_hasya_shant": "Shaant/desh_amjadalikhan_hasya_shant.mp3",
    "shaant/kamaj_amjadalikhan_shant": "Shaant/kamaj_amjadalikhan_shant.mp3",
    "shaant/malkuans_amjadalikhan_shant": "Shaant/malkuans_amjadalikhan_shant.mp3",
    # Veer songs (8 total)
    "veer/adana_nikhilbanerjee_veer": "Veer/adana_nikhilbanerjee_veer.mp3",
    "veer/bahar_amjadalikhan_veer": "Veer/bahar_amjadalikhan_veer.mp3",
    "veer/bhairavi_vilayatkhan_veer": "Veer/bhairavi_vilayatkhan_veer.mp3",
    "veer/bhimpalasi_kushaldas_veer": "Veer/bhimpalasi_kushaldas_veer.mp3",
    "veer/bhimpalasi_veer": "Veer/bhimpalasi_veer.mp3",
    # Shok songs (21 total)
    "shok/bhopaltodi_aliakbarkhan_shok": "Shok/bhopaltodi_aliakbarkhan_shok.mp3",
    "shok/bhopaltodi_shok": "Shok/bhopaltodi_shok.mp3",
    "shok/desh_amjadalikhan_hasya_shant": "Shok/desh_amjadalikhan_hasya_shant.mp3",
    # ... more songs to be added
}

def generate_dropbox_streaming_url(relative_path: str) -> str:
    """
    Generate Dropbox direct streaming URL from relative path in shared folder
    
    Args:
        relative_path: e.g., "Shringar/song.mp3"
    
    Returns:
        Direct streaming URL that can be used in <audio> tag
    """
    # For shared Dropbox links, we can use the raw parameter approach
    # Convert shared link to direct access link with dl=1 for streaming
    
    # Format: https://dl.dropboxusercontent.com/scl/fo/{folder_id}/{relative_path}?rlkey={key}&dl=1
    url = f"https://dl.dropboxusercontent.com/scl/fo/{DROPBOX_FOLDER_ID}/{relative_path}?rlkey={DROPBOX_RESOURCE_KEY}&dl=1"
    return url

async def update_mongodb_with_dropbox_urls():
    """
    Update all songs in MongoDB with Dropbox streaming URLs
    """
    
    print("\n" + "=" * 70)
    print("UPDATE MONGODB WITH DROPBOX STREAMING URLS")
    print("=" * 70)
    
    # Connect to MongoDB Atlas
    print("\nConnecting to MongoDB Atlas...")
    atlas_url = "mongodb+srv://Rishi123:Rishi_123@majorproject.lpwzhzc.mongodb.net/?appName=MajorProject"
    client = AsyncIOMotorClient(atlas_url)
    db = client["raga_rasa"]
    
    try:
        # Ping to verify connection
        await db.command("ping")
        print("[OK] Connected to MongoDB Atlas")
        
        # Get all songs
        print("\nFetching songs from MongoDB...")
        all_songs = await db.songs.find({}).to_list(None)
        print(f"[OK] Found {len(all_songs)} songs")
        
        if not all_songs:
            print("No songs found in database!")
            return
        
        # Group by rasa
        songs_by_rasa = {}
        for song in all_songs:
            rasa = song.get('rasa', 'Unknown')
            if rasa not in songs_by_rasa:
                songs_by_rasa[rasa] = []
            songs_by_rasa[rasa].append(song)
        
        print("\nSongs by Rasa:")
        for rasa, songs in songs_by_rasa.items():
            print(f"  {rasa}: {len(songs)} songs")
        
        # Create mapping for songs
        print("\nGenerating Dropbox URLs...")
        dropbox_mapping = {}
        
        for rasa, songs in songs_by_rasa.items():
            for idx, song in enumerate(songs, 1):
                song_id = song.get('_id', '')
                title = song.get('title', '')
                
                # Generate Dropbox path based on rasa and song name
                # Format: Rasa/song_name.mp3
                dropbox_path = f"{rasa}/{song_id}.mp3"
                dropbox_url = generate_dropbox_streaming_url(dropbox_path)
                
                dropbox_mapping[song_id] = {
                    'dropbox_path': dropbox_path,
                    'dropbox_url': dropbox_url,
                    'title': title,
                    'rasa': rasa
                }
        
        print(f"[OK] Generated URLs for {len(dropbox_mapping)} songs")
        
        # Update MongoDB
        print("\nUpdating MongoDB documents...")
        updated_count = 0
        
        for song_id, mapping in dropbox_mapping.items():
            result = await db.songs.update_one(
                {"_id": song_id},
                {
                    "$set": {
                        "dropbox_path": mapping['dropbox_path'],
                        "dropbox_url": mapping['dropbox_url'],
                        "streaming_provider": "dropbox"
                    }
                }
            )
            if result.modified_count > 0:
                updated_count += 1
        
        print(f"[OK] Updated {updated_count} songs in MongoDB")
        
        # Save mapping for backend reference
        print("\nSaving mapping to file...")
        mapping_file = Path("Backend/data/dropbox_songs_mapping.json")
        mapping_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(mapping_file, 'w') as f:
            json.dump(dropbox_mapping, f, indent=2)
        
        print(f"[OK] Saved mapping to {mapping_file}")
        
        # Verify
        print("\nVerifying update...")
        sample = await db.songs.find_one({"dropbox_url": {"$exists": True}})
        if sample:
            print(f"[OK] Sample song updated:")
            print(f"  Title: {sample.get('title')}")
            print(f"  Dropbox Path: {sample.get('dropbox_path')}")
            print(f"  Dropbox URL: {sample.get('dropbox_url')[:80]}...")
        
        print("\n" + "=" * 70)
        print("SUCCESS: MongoDB updated with Dropbox URLs")
        print("=" * 70)
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(update_mongodb_with_dropbox_urls())
