#!/usr/bin/env python3
"""
Upload songs from laptop to Cloudinary and store metadata in MongoDB
"""

import os
import sys
from pathlib import Path
import requests
import pymongo
from datetime import datetime
import logging
import io

# Fix Unicode on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Cloudinary config
CLOUDINARY_CLOUD_NAME = "dlx3ufj3t"
CLOUDINARY_API_KEY = "255318353319693"
CLOUDINARY_API_SECRET = "MKFvdiyfmNpzxbaGKBMFM6SlT2c"

# MongoDB config
MONGODB_URI = "mongodb+srv://Rishi123:Rishi_123@majorproject.lpwzhzc.mongodb.net/raga_rasa_db"

# Local songs path
SONGS_BASE_PATH = Path("C:/Major Project/Songs")

# Map folder names to rasa types
RASA_MAPPING = {
    "shaant": "Shaant",
    "shok": "Shok",
    "shringar": "Shringar",
    "veer": "Veer"
}

class CloudinaryUploader:
    """Upload songs to Cloudinary"""
    
    def __init__(self):
        self.upload_url = f"https://api.cloudinary.com/v1_1/{CLOUDINARY_CLOUD_NAME}/video/upload"
        self.auth = (CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET)
    
    def upload_file(self, file_path: Path, rasa: str, title: str) -> dict:
        """
        Upload a single file to Cloudinary
        
        Returns:
            dict with upload result (public_id, secure_url, etc.)
        """
        try:
            # Prepare public_id - don't include folder in public_id since we're setting folder separately
            # Use a sanitized version of the title
            safe_title = title.replace(" ", "_").replace("[", "").replace("]", "").replace("&", "and")[:50]
            public_id = f"{rasa.lower()}_{safe_title}"
            
            with open(file_path, 'rb') as f:
                files = {'file': f}
                data = {
                    'public_id': public_id,  # Just the filename, folder is set separately
                    'resource_type': 'video',  # Use video for audio files
                    'folder': f'raga-rasa/songs/{rasa}'  # Set folder separately
                }
                
                logger.info(f"Uploading: {file_path.name}")
                
                response = requests.post(
                    self.upload_url,
                    files=files,
                    data=data,
                    auth=self.auth,
                    timeout=120
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"  [OK] Uploaded successfully")
                    return {
                        'success': True,
                        'public_id': result.get('public_id'),
                        'secure_url': result.get('secure_url'),
                        'duration': result.get('duration'),
                        'file_size': result.get('bytes')
                    }
                else:
                    logger.warning(f"  [FAIL] HTTP {response.status_code}: {response.text[:100]}")
                    return {'success': False, 'error': response.text}
                    
        except Exception as e:
            logger.error(f"  [ERROR] Upload failed: {e}")
            return {'success': False, 'error': str(e)}

def get_all_songs_from_laptop():
    """Get all song files from local laptop"""
    
    songs = []
    
    for rasa_folder in SONGS_BASE_PATH.iterdir():
        if not rasa_folder.is_dir():
            continue
        
        rasa_name = rasa_folder.name.lower()
        if rasa_name not in RASA_MAPPING:
            continue
        
        rasa = RASA_MAPPING[rasa_name]
        
        for mp3_file in rasa_folder.glob("*.mp3"):
            # Extract title from filename
            title = mp3_file.stem
            
            songs.append({
                'file_path': mp3_file,
                'rasa': rasa,
                'title': title,
                'filename': mp3_file.name
            })
    
    return songs

def upload_all_songs_to_cloudinary(max_uploads=None):
    """Upload all songs to Cloudinary"""
    
    print("\n" + "="*70)
    print("CLOUDINARY SONG UPLOADER")
    print("="*70)
    
    # Get all songs
    songs = get_all_songs_from_laptop()
    total_songs = len(songs)
    
    print(f"\n[INFO] Found {total_songs} songs to upload")
    print("\nSongs by Rasa:")
    rasa_counts = {}
    for song in songs:
        rasa = song['rasa']
        rasa_counts[rasa] = rasa_counts.get(rasa, 0) + 1
    
    for rasa in ["Shringar", "Shaant", "Veer", "Shok"]:
        count = rasa_counts.get(rasa, 0)
        if count > 0:
            print(f"  {rasa}: {count} songs")
    
    if max_uploads:
        print(f"\n[INFO] Limiting uploads to {max_uploads} songs for testing")
        songs = songs[:max_uploads]
    
    # Create uploader
    uploader = CloudinaryUploader()
    
    # Upload each song
    print("\n" + "-"*70)
    print("UPLOADING SONGS...")
    print("-"*70)
    
    uploaded_songs = []
    failed_uploads = []
    
    for idx, song in enumerate(songs, 1):
        try:
            title_display = song['title'][:40]  # Truncate for display
            print(f"\n[{idx}/{len(songs)}] {title_display} ({song['rasa']})")
        except:
            print(f"\n[{idx}/{len(songs)}] (title encoding issue) ({song['rasa']})")
        
        result = uploader.upload_file(
            song['file_path'],
            song['rasa'],
            song['title']
        )
        
        if result['success']:
            song['cloudinary_result'] = result
            uploaded_songs.append(song)
        else:
            failed_uploads.append(song)
            print(f"      Error: {result.get('error')}")
    
    print("\n" + "="*70)
    print(f"UPLOAD COMPLETE: {len(uploaded_songs)} uploaded, {len(failed_uploads)} failed")
    print("="*70)
    
    return uploaded_songs, failed_uploads

def save_to_mongodb(uploaded_songs):
    """Save uploaded song metadata to MongoDB"""
    
    print("\n" + "-"*70)
    print("SAVING TO MONGODB...")
    print("-"*70)
    
    try:
        client = pymongo.MongoClient(MONGODB_URI)
        db = client["raga_rasa_db"]
        db.command("ping")
        print("[OK] Connected to MongoDB")
        
        # Prepare documents
        song_docs = []
        for song in uploaded_songs:
            result = song['cloudinary_result']
            
            doc = {
                "_id": result['public_id'].replace("/", "_"),
                "title": song['title'],
                "rasa": song['rasa'],
                "audio_url": result['secure_url'],
                "duration": result.get('duration'),
                "file_size": result.get('file_size'),
                "storage_metadata": {
                    "storage_type": "cloud",
                    "cloud_provider": "cloudinary",
                    "cloudinary_public_id": result['public_id'],
                    "cloud_url": result['secure_url']
                },
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            song_docs.append(doc)
        
        # Insert with upsert
        print(f"\n[INFO] Inserting {len(song_docs)} songs into MongoDB (with upsert)...")
        
        # Use upsert to handle duplicates
        inserted = 0
        for doc in song_docs:
            try:
                result = db.songs.update_one(
                    {"_id": doc["_id"]},
                    {"$set": doc},
                    upsert=True
                )
                inserted += 1
            except Exception as e:
                print(f"[WARN] Failed to insert {doc['title']}: {e}")
        
        print(f"[OK] Inserted/updated {inserted} songs")
        
        # Verify
        print("\n[INFO] Verifying data in MongoDB...")
        all_songs = list(db.songs.find({}))
        print(f"[OK] Total songs in database: {len(all_songs)}")
        
        # Group by rasa
        rasa_counts = {}
        for song in all_songs:
            rasa = song.get("rasa", "Unknown")
            rasa_counts[rasa] = rasa_counts.get(rasa, 0) + 1
        
        print("\nSongs by Rasa in MongoDB:")
        for rasa in ["Shringar", "Shaant", "Veer", "Shok"]:
            count = rasa_counts.get(rasa, 0)
            if count > 0:
                print(f"  {rasa}: {count}")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] MongoDB error: {e}")
        return False

def main():
    print("\n" + "="*70)
    print("RAGARASA SONG UPLOAD & DATABASE INTEGRATION")
    print("="*70)
    
    # Step 1: Upload to Cloudinary
    uploaded_songs, failed_uploads = upload_all_songs_to_cloudinary()
    
    if not uploaded_songs:
        print("\n[FAIL] No songs were uploaded. Aborting.")
        return
    
    # Step 2: Save to MongoDB
    if save_to_mongodb(uploaded_songs):
        print("\n" + "="*70)
        print("[SUCCESS] All songs uploaded and database updated!")
        print("="*70)
    else:
        print("\n[FAIL] Failed to save to MongoDB")

if __name__ == "__main__":
    main()
