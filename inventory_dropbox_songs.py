#!/usr/bin/env python3
"""
Inventory songs from Dropbox folder and generate streaming URLs
Since we can't directly query Dropbox without API token, we'll create a manual mapping
based on the folder structure you provided.
"""

import json
import os
from pathlib import Path
from typing import Dict, List

# Dropbox folder structure based on your shared folder
# Format: rasa_folder / song_files.mp3

# Since accessing Dropbox folder contents requires API, we'll use a two-step approach:
# 1. User manually lists files from their Dropbox folder
# 2. We create the inventory with proper streaming URLs

DROPBOX_FOLDER_SHARE_LINK = "https://www.dropbox.com/scl/fo/2je1qltlw5zuhosbd96zf/AHQqoCAInjkdN7eNRykcuvo"

def generate_dropbox_streaming_url(file_path: str, folder_id: str = "2je1qltlw5zuhosbd96zf", resource_key: str = "AHQqoCAInjkdN7eNRykcuvo") -> str:
    """
    Generate Dropbox direct streaming URL from file path
    
    Format: https://dl.dropboxusercontent.com/scl/fi/{file_id}/{filename}?rlkey={resource_key}&dl=1
    
    For now, we'll construct URLs based on folder structure
    """
    # This is a placeholder - actual implementation needs file IDs from Dropbox
    # We'll need to manually get these from the Dropbox folder
    return f"https://dl.dropboxusercontent.com/scl/fi/{folder_id}/{file_path}?rlkey={resource_key}&dl=1"

def create_songs_inventory() -> Dict:
    """
    Create inventory of songs from Dropbox
    
    Since we need actual file structure from your Dropbox, this creates a template
    that will be populated with actual songs
    """
    
    # Based on previous session: 68 songs organized by rasa
    # Shringar: 7 songs
    # Shaant: 32 songs
    # Veer: 8 songs
    # Shok: 21 songs
    
    # Template structure - actual songs will be loaded/populated
    songs_inventory = {
        "metadata": {
            "total_songs": 68,
            "source": "Dropbox",
            "folder_link": DROPBOX_FOLDER_SHARE_LINK,
            "last_updated": "2026-04-12",
            "note": "Songs organized by rasa folders in Dropbox"
        },
        "songs": {}
    }
    
    return songs_inventory

def main():
    """Main inventory creation"""
    print("=" * 70)
    print("DROPBOX SONGS INVENTORY GENERATOR")
    print("=" * 70)
    print("\nSince we need to access your Dropbox folder contents,")
    print("please follow these steps:")
    print("\n1. Open your Dropbox folder: " + DROPBOX_FOLDER_SHARE_LINK)
    print("2. Note the folder structure (Shringar, Shaant, Veer, Shok)")
    print("3. For each song file, we need:")
    print("   - File name")
    print("   - Rasa folder it's in")
    print("   - Dropbox file ID (hover over file, copy link)")
    print("\nAlternatively, you can use the Dropbox desktop app to sync")
    print("the folder, and we can scan the local sync folder.")
    print("\n" + "=" * 70)
    
    # For now, create a template that will be populated
    inventory = create_songs_inventory()
    
    # Save template
    output_path = Path("Backend/data/songs_inventory.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(inventory, f, indent=2)
    
    print(f"\nTemplate created: {output_path}")
    print("\nNext steps:")
    print("1. Check your Dropbox folder structure")
    print("2. We'll need to add actual songs with their Dropbox file IDs")
    print("3. Then update MongoDB with these streaming URLs")

if __name__ == "__main__":
    main()
