#!/usr/bin/env python3
"""
Create mock song data in MongoDB for testing recommendations
Uses public Cloudinary URLs for demonstration
"""

import pymongo
from datetime import datetime

def populate_mock_songs():
    print("\n" + "="*60)
    print("MOCK SONG DATA GENERATOR")
    print("="*60)
    
    try:
        # Connect to MongoDB
        print("[INFO] Connecting to MongoDB Atlas...")
        
        client = pymongo.MongoClient(
            "mongodb+srv://Rishi123:Rishi_123@majorproject.lpwzhzc.mongodb.net/raga_rasa_db"
        )
        
        db = client["raga_rasa_db"]
        db.command("ping")
        print("[OK] Connected to MongoDB Atlas")
        
        # Clear existing songs (optional)
        print("[INFO] Clearing existing songs...")
        result = db.songs.delete_many({})
        print(f"  Deleted {result.deleted_count} existing songs")
        
        # Create mock songs data
        # Using sample URLs and rasa categorization
        mock_songs = [
            # Shringar (Happy, Romantic) - 8 songs
            {
                "_id": "shringar_001_raag_yaman",
                "title": "Raag Yaman - Happy Melody",
                "rasa": "Shringar",
                "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
                "duration": "4:38",
                "storage_metadata": {
                    "storage_type": "cloud",
                    "cloud_provider": "demo",
                    "cloud_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"
                },
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "_id": "shringar_002_raag_bhairav",
                "title": "Raag Bhairav - Morning Joy",
                "rasa": "Shringar",
                "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3",
                "duration": "5:12",
                "storage_metadata": {
                    "storage_type": "cloud",
                    "cloud_provider": "demo",
                    "cloud_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3"
                },
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "_id": "shringar_003_raag_ahir_bhairav",
                "title": "Raag Ahir Bhairav - Romantic",
                "rasa": "Shringar",
                "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3",
                "duration": "4:45",
                "storage_metadata": {
                    "storage_type": "cloud",
                    "cloud_provider": "demo",
                    "cloud_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3"
                },
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "_id": "shringar_004_raag_khamaaj",
                "title": "Raag Khamaaj - Blissful",
                "rasa": "Shringar",
                "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-4.mp3",
                "duration": "5:30",
                "storage_metadata": {
                    "storage_type": "cloud",
                    "cloud_provider": "demo",
                    "cloud_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-4.mp3"
                },
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "_id": "shringar_005_raag_malhar",
                "title": "Raag Malhar - Festive",
                "rasa": "Shringar",
                "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-5.mp3",
                "duration": "6:00",
                "storage_metadata": {
                    "storage_type": "cloud",
                    "cloud_provider": "demo",
                    "cloud_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-5.mp3"
                },
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            
            # Shaant (Peaceful, Calm) - 10 songs
            {
                "_id": "shaant_001_raag_bhairav_thaat",
                "title": "Raag Bhairav Thaat - Peaceful",
                "rasa": "Shaant",
                "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-6.mp3",
                "duration": "7:15",
                "storage_metadata": {
                    "storage_type": "cloud",
                    "cloud_provider": "demo",
                    "cloud_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-6.mp3"
                },
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "_id": "shaant_002_raag_sarang",
                "title": "Raag Sarang - Serenity",
                "rasa": "Shaant",
                "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-7.mp3",
                "duration": "6:45",
                "storage_metadata": {
                    "storage_type": "cloud",
                    "cloud_provider": "demo",
                    "cloud_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-7.mp3"
                },
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "_id": "shaant_003_raag_darbari",
                "title": "Raag Darbari - Meditative",
                "rasa": "Shaant",
                "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-8.mp3",
                "duration": "8:30",
                "storage_metadata": {
                    "storage_type": "cloud",
                    "cloud_provider": "demo",
                    "cloud_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-8.mp3"
                },
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "_id": "shaant_004_raag_jor",
                "title": "Raag Jor - Calm Flow",
                "rasa": "Shaant",
                "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-9.mp3",
                "duration": "7:00",
                "storage_metadata": {
                    "storage_type": "cloud",
                    "cloud_provider": "demo",
                    "cloud_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-9.mp3"
                },
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            
            # Veer (Courageous, Bold) - 5 songs
            {
                "_id": "veer_001_raag_bhairav_raudra",
                "title": "Raag Bhairav Raudra - Bold",
                "rasa": "Veer",
                "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-10.mp3",
                "duration": "5:30",
                "storage_metadata": {
                    "storage_type": "cloud",
                    "cloud_provider": "demo",
                    "cloud_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-10.mp3"
                },
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "_id": "veer_002_raag_marwa",
                "title": "Raag Marwa - Energetic",
                "rasa": "Veer",
                "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-11.mp3",
                "duration": "6:15",
                "storage_metadata": {
                    "storage_type": "cloud",
                    "cloud_provider": "demo",
                    "cloud_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-11.mp3"
                },
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "_id": "veer_003_raag_kafi",
                "title": "Raag Kafi - Courageous",
                "rasa": "Veer",
                "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-12.mp3",
                "duration": "5:45",
                "storage_metadata": {
                    "storage_type": "cloud",
                    "cloud_provider": "demo",
                    "cloud_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-12.mp3"
                },
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            
            # Shok (Sad, Melancholic) - 7 songs
            {
                "_id": "shok_001_raag_yaman_kalyan",
                "title": "Raag Yaman Kalyan - Melancholy",
                "rasa": "Shok",
                "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-13.mp3",
                "duration": "6:30",
                "storage_metadata": {
                    "storage_type": "cloud",
                    "cloud_provider": "demo",
                    "cloud_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-13.mp3"
                },
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "_id": "shok_002_raag_bhopali",
                "title": "Raag Bhopali - Sorrowful",
                "rasa": "Shok",
                "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-14.mp3",
                "duration": "5:50",
                "storage_metadata": {
                    "storage_type": "cloud",
                    "cloud_provider": "demo",
                    "cloud_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-14.mp3"
                },
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "_id": "shok_003_raag_asavari",
                "title": "Raag Asavari - Pathos",
                "rasa": "Shok",
                "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-15.mp3",
                "duration": "7:20",
                "storage_metadata": {
                    "storage_type": "cloud",
                    "cloud_provider": "demo",
                    "cloud_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-15.mp3"
                },
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
        ]
        
        # Insert songs into database
        print("\n[INFO] Inserting mock songs...")
        
        result = db.songs.insert_many(mock_songs)
        print(f"[OK] Inserted {len(result.inserted_ids)} songs")
        
        # Verify
        print("\n[INFO] Verifying data...")
        all_songs = list(db.songs.find({}))
        print(f"[OK] Total songs in database: {len(all_songs)}")
        
        # Group by rasa
        rasa_counts = {}
        for song in all_songs:
            rasa = song.get("rasa", "Unknown")
            rasa_counts[rasa] = rasa_counts.get(rasa, 0) + 1
        
        print("\nSongs by Rasa:")
        for rasa in ["Shringar", "Shaant", "Veer", "Shok"]:
            count = rasa_counts.get(rasa, 0)
            print(f"  {rasa}: {count}")
            
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    populate_mock_songs()
