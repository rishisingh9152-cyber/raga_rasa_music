#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete re-upload of all songs to Cloudinary with proper URL tracking
"""

import os
import sys
from pathlib import Path
import cloudinary
import cloudinary.uploader
import pymongo
import time

# Force UTF-8 output
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Cloudinary configuration
cloudinary.config(
    cloud_name="dlx3ufj3t",
    api_key="255318353319693",
    api_secret="MKFvdiyfmNpzxbaGKBMFM6SlT2c"
)

# MongoDB connection
MONGODB_URL = "mongodb+srv://Rishi123:Rishi_123@majorproject.lpwzhzc.mongodb.net/?appName=MajorProject"
DATABASE_NAME = "raga_rasa"
COLLECTION_NAME = "songs"

# Local songs directory
SONGS_DIR = r"C:\Users\rishi\Dropbox\raga-rasa\Songs"

# Rasa mapping
RASA_MAPPING = {
    "shaant": "Shaant",
    "shok": "Shok",
    "shringar": "Shringar",
    "veer": "Veer"
}


def sanitize_filename(filename):
    """Sanitize filename for Cloudinary"""
    return filename.replace('&', 'and').replace('.mp3', '')


def main():
    """Main function"""
    
    print("Complete Cloudinary Upload with MongoDB Update")
    print("="*70)
    
    try:
        # Connect to MongoDB
        client = pymongo.MongoClient(MONGODB_URL)
        db = client[DATABASE_NAME]
        songs_collection = db[COLLECTION_NAME]
        
        print("[OK] Connected to MongoDB Atlas\n")
        
        # Get all songs from database, indexed by rasa and filename-ish title
        all_songs = list(songs_collection.find())
        print(f"[OK] Found {len(all_songs)} songs in database\n")
        
        # Build a simple map: rasa -> list of songs
        songs_by_rasa = {}
        for song in all_songs:
            rasa = song.get("rasa")
            if rasa not in songs_by_rasa:
                songs_by_rasa[rasa] = []
            songs_by_rasa[rasa].append(song)
        
        # Counter for updates
        total_uploaded = 0
        url_updates = {}  # song_id -> new_url
        
        # Process each rasa folder
        for rasa_dir in sorted(os.listdir(SONGS_DIR)):
            rasa_path = os.path.join(SONGS_DIR, rasa_dir)
            
            if not os.path.isdir(rasa_path) or rasa_dir.lower() == "temp":
                continue
            
            rasa_normalized = RASA_MAPPING.get(rasa_dir.lower(), rasa_dir.title())
            
            print(f"[RASA] {rasa_normalized}")
            print("-" * 70)
            
            # Get list of songs in this rasa directory
            mp3_files = sorted([f for f in os.listdir(rasa_path) if f.endswith('.mp3')])
            songs_in_rasa_db = songs_by_rasa.get(rasa_normalized, [])
            
            print(f"   Files on disk: {len(mp3_files)}")
            print(f"   Songs in DB:   {len(songs_in_rasa_db)}\n")
            
            # Upload each file
            for idx, filename in enumerate(mp3_files):
                file_path = os.path.join(rasa_path, filename)
                
                # Get corresponding song from DB (in order)
                if idx < len(songs_in_rasa_db):
                    song_doc = songs_in_rasa_db[idx]
                    song_id = song_doc["song_id"]
                else:
                    print(f"   [WARN] No matching DB song for: {filename}")
                    continue
                
                try:
                    # Upload to Cloudinary
                    public_id = f"raga-rasa/songs/{rasa_normalized}/{sanitize_filename(filename)}"
                    
                    print(f"   [{idx+1}/{len(mp3_files)}] {filename}")
                    
                    result = cloudinary.uploader.upload_large(
                        file_path,
                        public_id=public_id,
                        resource_type="video",
                        timeout=300
                    )
                    
                    url = result.get("secure_url")
                    if url:
                        url_updates[song_id] = url
                        print(f"        OK: {url}")
                        total_uploaded += 1
                    else:
                        print(f"        [ERROR] No URL returned")
                    
                    # Small delay to avoid rate limiting
                    time.sleep(0.5)
                    
                except Exception as e:
                    print(f"        [ERROR] {str(e)}")
            
            print()
        
        # Update all songs in MongoDB
        print("="*70)
        print("Updating MongoDB with Cloudinary URLs...")
        print("="*70 + "\n")
        
        updated_count = 0
        for song_id, url in url_updates.items():
            result = songs_collection.update_one(
                {"song_id": song_id},
                {"$set": {"audio_url": url}}
            )
            if result.modified_count > 0:
                updated_count += 1
                print(f"[OK] Updated song: {song_id}")
        
        print(f"\n[OK] Updated {updated_count} songs in MongoDB\n")
        
        # Verify
        print("="*70)
        print("VERIFICATION - Sample Songs")
        print("="*70 + "\n")
        
        for song in songs_collection.find().limit(5):
            print(f"Title: {song['title']}")
            print(f"Rasa:  {song['rasa']}")
            print(f"URL:   {song['audio_url']}")
            print()
        
        return True
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
