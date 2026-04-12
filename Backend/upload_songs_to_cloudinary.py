#!/usr/bin/env python
"""Upload songs to Cloudinary organized by Rasa"""

import os
import cloudinary
import cloudinary.uploader
from pathlib import Path

# Cloudinary config
cloudinary.config(
    cloud_name="dlx3ufj3t",
    api_key="255318353319693",
    api_secret="MKFvdiyfmNpzxbaGKBMFM6SlT2c"
)

# Base directory with songs
SONGS_DIR = r"C:\Users\rishi\OneDrive\Desktop\raas"

# Rasas and their properties
RASAS = {
    "Shringar": {"count": 8, "emotion": "happy, romantic"},
    "Veer": {"count": 8, "emotion": "courageous, bold"},
    "Shaant": {"count": 30, "emotion": "peaceful, calm"},
    "Shok": {"count": 22, "emotion": "sad, melancholic"}
}

def upload_songs():
    """Upload all songs to Cloudinary"""
    total_uploaded = 0
    
    for rasa, info in RASAS.items():
        rasa_dir = os.path.join(SONGS_DIR, rasa)
        
        if not os.path.exists(rasa_dir):
            print(f"[SKIP] Directory not found: {rasa_dir}")
            continue
        
        # Get all music files
        music_files = []
        for ext in ['*.mp3', '*.wav', '*.m4a', '*.flac']:
            music_files.extend(Path(rasa_dir).glob(ext))
        
        print(f"\n[*] Processing {rasa} ({len(music_files)} files)")
        print(f"    Emotion: {info['emotion']}")
        
        for file_path in music_files:
            try:
                filename = file_path.name
                cloudinary_path = f"raga-rasa/songs/{rasa}/{filename}"
                
                print(f"    Uploading: {filename}...", end=" ")
                
                response = cloudinary.uploader.upload(
                    str(file_path),
                    resource_type="auto",
                    public_id=cloudinary_path.replace(".mp3", "").replace(".wav", "").replace(".m4a", "").replace(".flac", ""),
                    folder=f"raga-rasa/songs/{rasa}",
                    overwrite=False
                )
                
                print(f"✓ ({response['public_id']})")
                total_uploaded += 1
                
            except Exception as e:
                print(f"✗ Error: {str(e)}")
    
    print(f"\n[OK] Total uploaded: {total_uploaded}/68 songs")
    return total_uploaded

if __name__ == "__main__":
    print("=" * 60)
    print("RagaRasa Music Therapy - Song Upload to Cloudinary")
    print("=" * 60)
    
    uploaded = upload_songs()
    
    print("\n[OK] Upload complete!")
    print(f"Total songs uploaded: {uploaded}")
