#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Seed MongoDB Atlas with 59 RagaRasa songs from local directories with Cloudinary URLs
Organized by rasa folder structure
"""

import os
import sys
from pathlib import Path
import pymongo
import uuid
from datetime import datetime

# Force UTF-8 output
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# MongoDB connection
MONGODB_URL = "mongodb+srv://Rishi123:Rishi_123@majorproject.lpwzhzc.mongodb.net/?appName=MajorProject"
DATABASE_NAME = "raga_rasa"
COLLECTION_NAME = "songs"

# Cloudinary base URL
CLOUDINARY_BASE = "https://res.cloudinary.com/dlx3ufj3t/video/upload/raga-rasa/songs"

# Local songs directory
SONGS_DIR = r"C:\Users\rishi\Dropbox\raga-rasa\Songs"

# Rasa mapping - ensure consistent casing
RASA_MAPPING = {
    "shaant": "Shaant",
    "shok": "Shok",
    "shringar": "Shringar",
    "veer": "Veer"
}

# Emotion to Rasa mapping for recommendations
EMOTION_TO_RASA = {
    "happy": "Shringar",
    "sad": "Shok",
    "angry": "Shaant",
    "fearful": "Veer",
    "neutral": "Shaant",
    "surprised": "Shringar",
    "disgusted": "Veer"
}


def get_rasa_from_filename(filename):
    """Try to extract rasa from filename"""
    filename_lower = filename.lower()
    
    if "shringar" in filename_lower or "rati" in filename_lower:
        return "Shringar"
    elif "veer" in filename_lower or "bahaduri" in filename_lower or "todi" in filename_lower and "veer" in filename_lower:
        return "Veer"
    elif "shok" in filename_lower or "bhairavi" in filename_lower or "darbari" in filename_lower or "jogia" in filename_lower:
        return "Shok"
    else:
        return "Shaant"  # default


def generate_song_title(filename):
    """Generate a clean title from filename"""
    # Remove .mp3 extension
    name = filename.replace('.mp3', '')
    
    # Remove prefixes like "raag-" or "raga-"
    name = name.replace('raag-', '').replace('raga-', '')
    
    # Replace hyphens and underscores with spaces
    name = name.replace('-', ' ').replace('_', ' ')
    
    # Clean up IDs and extra info (like _xusupgu3)
    import re
    name = re.sub(r'\s*_[a-z0-9]+$', '', name)
    
    # Title case
    name = ' '.join(word.capitalize() for word in name.split())
    
    return name


def create_song_document(filename, rasa_dir, rasa_normalized):
    """Create a song document for MongoDB"""
    song_title = generate_song_title(filename)
    
    # Build Cloudinary URL - use rasa_normalized for folder structure
    cloudinary_url = f"{CLOUDINARY_BASE}/{rasa_normalized}/{filename}"
    
    return {
        "song_id": str(uuid.uuid4()),
        "title": song_title,
        "audio_url": cloudinary_url,
        "rasa": rasa_normalized,
        "artist": "Traditional/Hindustani Classical",
        "description": f"Classical Indian music in {rasa_normalized} rasa",
        "confidence": 0.85,
        "duration": 300,  # placeholder
        "language": "Hindi/Sanskrit",
        "genre": "Classical",
        "tags": [rasa_normalized.lower(), "instrumental", "therapeutic"],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }


def seed_database():
    """Seed all songs to MongoDB Atlas"""
    
    try:
        # Connect to MongoDB
        client = pymongo.MongoClient(MONGODB_URL)
        db = client[DATABASE_NAME]
        songs_collection = db[COLLECTION_NAME]
        
        print("[OK] Connected to MongoDB Atlas")
        
        # Clear existing songs
        result = songs_collection.delete_many({})
        print(f"[OK] Cleared {result.deleted_count} existing songs")
        
        all_songs = []
        song_count_by_rasa = {}
        
        # Iterate through all rasa directories
        if not os.path.exists(SONGS_DIR):
            print(f"[ERROR] Songs directory not found: {SONGS_DIR}")
            return False
        
        for rasa_dir in os.listdir(SONGS_DIR):
            rasa_path = os.path.join(SONGS_DIR, rasa_dir)
            
            # Skip if not a directory
            if not os.path.isdir(rasa_path):
                continue
            
            # Skip temp directories
            if rasa_dir.lower() == "temp":
                continue
            
            # Get normalized rasa name
            rasa_normalized = RASA_MAPPING.get(rasa_dir.lower(), rasa_dir.title())
            
            print(f"\n[RASA] Processing {rasa_dir} -> {rasa_normalized}")
            
            # Get all MP3 files in this directory
            songs_in_rasa = []
            for filename in os.listdir(rasa_path):
                if filename.endswith('.mp3'):
                    songs_in_rasa.append(filename)
            
            print(f"   Found {len(songs_in_rasa)} songs")
            
            # Create song documents
            for filename in sorted(songs_in_rasa):
                song_doc = create_song_document(filename, rasa_dir, rasa_normalized)
                all_songs.append(song_doc)
                print(f"   [+] {song_doc['title']}")
            
            song_count_by_rasa[rasa_normalized] = len(songs_in_rasa)
        
        # Insert all songs
        if all_songs:
            result = songs_collection.insert_many(all_songs)
            print(f"\n[OK] Inserted {len(result.inserted_ids)} songs into MongoDB")
        else:
            print("[ERROR] No songs found to insert")
            return False
        
        # Print summary
        print("\n" + "="*60)
        print("SEEDING COMPLETE")
        print("="*60)
        for rasa, count in sorted(song_count_by_rasa.items()):
            print(f"  {rasa:<12} : {count:>3} songs")
        print(f"{'TOTAL':<12} : {sum(song_count_by_rasa.values()):>3} songs")
        print("="*60)
        
        # Verify
        total_in_db = songs_collection.count_documents({})
        print(f"\n[OK] Database verification: {total_in_db} songs in MongoDB")
        
        # Show sample songs
        print("\nSample songs from database:")
        for song in songs_collection.find().limit(3):
            print(f"  - {song['title']}")
            print(f"    URL: {song['audio_url']}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("RagaRasa Songs Seeding Script")
    print("="*60)
    print(f"Songs Directory: {SONGS_DIR}")
    print(f"MongoDB: {DATABASE_NAME}")
    print(f"Cloudinary Base: {CLOUDINARY_BASE}")
    print("="*60 + "\n")
    
    success = seed_database()
    sys.exit(0 if success else 1)
