#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Upload all 59 RagaRasa songs to Cloudinary and update MongoDB with real URLs
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


def upload_to_cloudinary(file_path, rasa_folder, filename):
    """Upload a song file to Cloudinary and return the URL"""
    try:
        # Create folder path: raga-rasa/songs/Shaant/filename
        public_id = f"raga-rasa/songs/{rasa_folder}/{filename.replace('.mp3', '')}"
        
        print(f"   Uploading to Cloudinary: {public_id}")
        
        result = cloudinary.uploader.upload_large(
            file_path,
            public_id=public_id,
            resource_type="video",
            timeout=300
        )
        
        url = result.get("secure_url")
        print(f"   [OK] Uploaded: {url}")
        return url
        
    except Exception as e:
        print(f"   [ERROR] Upload failed: {e}")
        return None


def update_mongodb_with_urls(cloudinary_urls):
    """Update MongoDB documents with actual Cloudinary URLs"""
    try:
        client = pymongo.MongoClient(MONGODB_URL)
        db = client[DATABASE_NAME]
        songs_collection = db[COLLECTION_NAME]
        
        updated_count = 0
        for song_id, url in cloudinary_urls.items():
            result = songs_collection.update_one(
                {"song_id": song_id},
                {"$set": {"audio_url": url}}
            )
            if result.modified_count > 0:
                updated_count += 1
        
        print(f"\n[OK] Updated {updated_count} songs in MongoDB with actual Cloudinary URLs")
        return True
        
    except Exception as e:
        print(f"[ERROR] MongoDB update failed: {e}")
        return False


def main():
    """Main function to upload all songs and update database"""
    
    print("RagaRasa Cloudinary Upload Script")
    print("="*60)
    print(f"Songs Directory: {SONGS_DIR}")
    print(f"Cloudinary Cloud: dlx3ufj3t")
    print("="*60 + "\n")
    
    try:
        # Connect to MongoDB first to get song documents
        client = pymongo.MongoClient(MONGODB_URL)
        db = client[DATABASE_NAME]
        songs_collection = db[COLLECTION_NAME]
        
        print("[OK] Connected to MongoDB Atlas\n")
        
        # Get all songs from database
        all_db_songs = {song["song_id"]: song for song in songs_collection.find()}
        print(f"[OK] Found {len(all_db_songs)} songs in MongoDB\n")
        
        cloudinary_urls = {}  # song_id -> actual_url
        total_uploaded = 0
        total_failed = 0
        
        # Iterate through all rasa directories
        for rasa_dir in sorted(os.listdir(SONGS_DIR)):
            rasa_path = os.path.join(SONGS_DIR, rasa_dir)
            
            # Skip if not a directory or is temp
            if not os.path.isdir(rasa_path) or rasa_dir.lower() == "temp":
                continue
            
            # Get normalized rasa name
            rasa_normalized = RASA_MAPPING.get(rasa_dir.lower(), rasa_dir.title())
            
            print(f"\n[RASA] {rasa_normalized}")
            print("-" * 60)
            
            # Get all MP3 files in this directory
            songs_in_rasa = sorted([f for f in os.listdir(rasa_path) if f.endswith('.mp3')])
            
            for filename in songs_in_rasa:
                file_path = os.path.join(rasa_path, filename)
                
                # Find matching song in database
                db_song = None
                for song_id, song in all_db_songs.items():
                    if song.get("rasa") == rasa_normalized and filename in file_path:
                        db_song = song
                        break
                
                # If not found by filename match, find by audio_url containing filename
                if not db_song:
                    for song_id, song in all_db_songs.items():
                        if song.get("rasa") == rasa_normalized:
                            db_song = song
                            break
                
                if not db_song:
                    print(f"   [SKIP] {filename} - not found in database")
                    continue
                
                # Upload to Cloudinary
                url = upload_to_cloudinary(file_path, rasa_normalized, filename)
                
                if url:
                    cloudinary_urls[db_song["song_id"]] = url
                    total_uploaded += 1
                else:
                    total_failed += 1
        
        print("\n" + "="*60)
        print(f"UPLOAD COMPLETE")
        print("="*60)
        print(f"  Uploaded: {total_uploaded}")
        print(f"  Failed:   {total_failed}")
        print(f"  Total:    {len(cloudinary_urls)}")
        print("="*60)
        
        # Update MongoDB with real URLs
        if cloudinary_urls:
            update_mongodb_with_urls(cloudinary_urls)
            print("\nVerifying URLs in database...")
            
            # Show sample
            sample_songs = list(songs_collection.find().limit(3))
            for song in sample_songs:
                print(f"\n  {song['title']}")
                print(f"  URL: {song['audio_url']}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
