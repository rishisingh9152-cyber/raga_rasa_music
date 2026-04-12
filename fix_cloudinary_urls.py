#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix MongoDB URLs - Update all songs with actual Cloudinary URLs by re-uploading and matching
"""

import os
import sys
from pathlib import Path
import cloudinary
import cloudinary.uploader
import pymongo
from datetime import datetime

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


def sanitize_public_id(filename):
    """Sanitize filename for Cloudinary public_id (remove special chars like &)"""
    # Replace & with and
    name = filename.replace('.mp3', '').replace('&', 'and')
    return name


def upload_and_get_url(file_path, rasa_folder, filename):
    """Upload to Cloudinary and return the secure URL"""
    try:
        public_id = f"raga-rasa/songs/{rasa_folder}/{sanitize_public_id(filename)}"
        
        result = cloudinary.uploader.upload_large(
            file_path,
            public_id=public_id,
            resource_type="video",
            timeout=300
        )
        
        return result.get("secure_url")
        
    except Exception as e:
        print(f"   [ERROR] Upload failed: {e}")
        return None


def main():
    """Main function"""
    
    print("Updating MongoDB with Cloudinary URLs")
    print("="*60)
    
    try:
        # Connect to MongoDB
        client = pymongo.MongoClient(MONGODB_URL)
        db = client[DATABASE_NAME]
        songs_collection = db[COLLECTION_NAME]
        
        print("[OK] Connected to MongoDB\n")
        
        # Build a map of rasa + filename -> song_id
        songs_by_location = {}
        for song in songs_collection.find():
            rasa = song.get("rasa")
            title = song.get("title", "")
            song_id = song.get("song_id")
            
            if rasa and song_id:
                songs_by_location[(rasa, title)] = song_id
        
        print(f"[OK] Found {len(songs_by_location)} songs in database\n")
        
        updated_count = 0
        failed_files = []
        
        # Iterate through rasa directories
        for rasa_dir in sorted(os.listdir(SONGS_DIR)):
            rasa_path = os.path.join(SONGS_DIR, rasa_dir)
            
            if not os.path.isdir(rasa_path) or rasa_dir.lower() == "temp":
                continue
            
            rasa_normalized = RASA_MAPPING.get(rasa_dir.lower(), rasa_dir.title())
            
            print(f"[RASA] {rasa_normalized}")
            print("-" * 60)
            
            for filename in sorted(os.listdir(rasa_path)):
                if not filename.endswith('.mp3'):
                    continue
                
                file_path = os.path.join(rasa_path, filename)
                
                # Try to find matching song in DB
                # Match by rasa folder
                matching_songs = [(k, v) for k, v in songs_by_location.items() if k[0] == rasa_normalized]
                
                if not matching_songs:
                    failed_files.append((rasa_normalized, filename))
                    continue
                
                # Get first matching song (will update in order)
                location_key, song_id = matching_songs[0]
                
                # Upload to Cloudinary
                print(f"   Uploading: {filename}")
                url = upload_and_get_url(file_path, rasa_normalized, filename)
                
                if url:
                    # Update MongoDB
                    result = songs_collection.update_one(
                        {"song_id": song_id},
                        {"$set": {"audio_url": url}}
                    )
                    
                    if result.modified_count > 0:
                        print(f"   [OK] Updated: {url}")
                        updated_count += 1
                        # Remove from mapping to avoid duplicate
                        del songs_by_location[location_key]
                    else:
                        print(f"   [WARN] Failed to update song_id: {song_id}")
                else:
                    failed_files.append((rasa_normalized, filename))
        
        print("\n" + "="*60)
        print(f"UPDATE COMPLETE")
        print("="*60)
        print(f"  Updated: {updated_count}")
        print(f"  Failed:  {len(failed_files)}")
        print("="*60)
        
        # Show sample results
        print("\nSample songs in database:")
        for song in songs_collection.find().limit(5):
            print(f"\n  {song['title']}")
            print(f"  URL: {song['audio_url']}")
        
        # Verify total
        total_in_db = songs_collection.count_documents({})
        print(f"\n[OK] Total songs in database: {total_in_db}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
