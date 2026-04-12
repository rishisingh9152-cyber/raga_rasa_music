#!/usr/bin/env python3
"""
Script to scan Cloudinary for uploaded songs and populate MongoDB database
Uses REST API instead of SDK
"""

import requests
import pymongo
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def scan_and_populate_songs():
    """Scan Cloudinary and populate MongoDB with song metadata"""
    
    print("\n" + "="*60)
    print("CLOUDINARY SONG SCANNER (REST API)")
    print("="*60)
    
    try:
        # Connect to MongoDB
        print("[INFO] Connecting to MongoDB Atlas...")
        
        client = pymongo.MongoClient(
            "mongodb+srv://Rishi123:Rishi_123@majorproject.lpwzhzc.mongodb.net/raga_rasa_db"
        )
        
        db = client["raga_rasa_db"]
        
        # Test connection
        db.command("ping")
        print("[OK] Connected to MongoDB Atlas")
        
        # Cloudinary config
        cloud_name = "dlx3ufj3t"
        api_key = "255318353319693"
        api_secret = "MKFvdiyfmNpzxbaGKBMFM6SlT2c"
        
        print("[INFO] Querying Cloudinary API...")
        
        # Use Cloudinary REST API to list resources
        # https://cloudinary.com/documentation/admin_api#get_resources
        
        url = f"https://api.cloudinary.com/v1_1/{cloud_name}/resources"
        params = {
            "type": "upload",
            "prefix": "raga-rasa/songs",
            "max_results": "500"
        }
        
        # Basic auth with API key and secret
        response = requests.get(url, params=params, auth=(api_key, api_secret), timeout=30)
        
        if response.status_code != 200:
            print(f"[FAIL] Cloudinary API error: {response.status_code}")
            print(f"Response: {response.text}")
            return
        
        data = response.json()
        all_resources = data.get("resources", [])
        
        print(f"[OK] Found {len(all_resources)} resources in Cloudinary")
        
        # Process resources and group by rasa
        songs_by_rasa = {
            "Shringar": [],
            "Shaant": [],
            "Veer": [],
            "Shok": []
        }
        
        for resource in all_resources:
            public_id = resource.get("public_id", "")
            filename = resource.get("filename", "")
            
            # Extract rasa from path (raga-rasa/songs/Rasa/filename)
            parts = public_id.split("/")
            if len(parts) >= 3:
                rasa_name = parts[2]  # Get rasa from path
                
                # Map to valid rasa names
                rasa_map = {
                    "shringar": "Shringar",
                    "shaant": "Shaant",
                    "veer": "Veer",
                    "shok": "Shok",
                    "Shringar": "Shringar",
                    "Shaant": "Shaant",
                    "Veer": "Veer",
                    "Shok": "Shok"
                }
                
                rasa = rasa_map.get(rasa_name, "Shaant")
                
                # Get Cloudinary URL
                secure_url = resource.get("secure_url", "")
                
                # Extract title from filename
                title = filename.replace(".mp3", "").replace("_", " ").replace("-", " ")
                
                # Get duration (in seconds)
                duration = resource.get("duration", 0)
                duration_str = f"{int(duration)//60}:{int(duration)%60:02d}" if duration else "0:00"
                
                song_doc = {
                    "_id": public_id.replace("/", "_"),  # Use public_id as unique key
                    "title": title,
                    "rasa": rasa,
                    "audio_url": secure_url,
                    "duration": duration_str,
                    "storage_metadata": {
                        "storage_type": "cloud",
                        "cloud_provider": "cloudinary",
                        "cloudinary_public_id": public_id,
                        "cloud_url": secure_url
                    },
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                
                songs_by_rasa[rasa].append(song_doc)
                print(f"  Found: {title} (Rasa: {rasa})")
        
        # Insert into database
        print("\n[INFO] Inserting songs into MongoDB...")
        
        total_inserted = 0
        for rasa, songs in songs_by_rasa.items():
            if songs:
                # Use upsert to avoid duplicates
                for song in songs:
                    try:
                        result = db.songs.update_one(
                            {"_id": song["_id"]},
                            {"$set": song},
                            upsert=True
                        )
                        total_inserted += 1
                    except Exception as e:
                        print(f"  [WARN] Failed to insert {song['title']}: {e}")
                
                print(f"  {rasa}: {len(songs)} songs")
        
        print(f"\n[OK] Inserted {total_inserted} songs into database")
        
        # Verify insertion
        print("\n[INFO] Verifying database contents...")
        all_songs = list(db.songs.find({}))
        print(f"[OK] Total songs in database: {len(all_songs)}")
        
        # Group by rasa
        rasa_counts = {}
        for song in all_songs:
            rasa = song.get("rasa", "Unknown")
            rasa_counts[rasa] = rasa_counts.get(rasa, 0) + 1
        
        print("\nSongs by Rasa:")
        for rasa, count in sorted(rasa_counts.items()):
            print(f"  {rasa}: {count}")
            
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    scan_and_populate_songs()
