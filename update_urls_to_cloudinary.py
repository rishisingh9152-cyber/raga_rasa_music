#!/usr/bin/env python3
"""Update MongoDB to use Cloudinary URLs instead of relative paths"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def update_urls_to_cloudinary():
    """
    Update all song audio_url fields to use Cloudinary format
    Based on the pattern from upload_songs_to_cloudinary.py, URLs should be:
    https://res.cloudinary.com/dlx3ufj3t/video/upload/raga-rasa/songs/{rasa}/{filename}
    """
    
    cloud_name = "dlx3ufj3t"
    
    # Connect to MongoDB Atlas
    print("Connecting to MongoDB Atlas...")
    atlas_url = "mongodb+srv://Rishi123:Rishi_123@majorproject.lpwzhzc.mongodb.net/?appName=MajorProject"
    atlas_client = AsyncIOMotorClient(atlas_url)
    atlas_db = atlas_client["raga_rasa"]
    
    try:
        # Get all songs
        print("\nFetching all songs from MongoDB Atlas...")
        songs = await atlas_db.songs.find({}).to_list(None)
        print(f"Found {len(songs)} songs")
        
        updated_count = 0
        
        for song in songs:
            # Get the song's rasa and ID
            rasa = song.get('rasa', 'Shaant')
            song_id = song.get('_id', '')
            current_url = song.get('audio_url', '')
            
            # Construct Cloudinary URL
            # The public_id from the upload script is: f"{rasa.lower()}_{safe_title}"
            # And it's stored in folder: f'raga-rasa/songs/{rasa}'
            # So the full URL should be: https://res.cloudinary.com/dlx3ufj3t/video/upload/raga-rasa/songs/{rasa}/{filename}
            
            # Extract filename from the song_id which might be like "shok/Desh_amjadalikhan_hasya_shant"
            # or could be the public_id
            
            # Build URL based on rasa and song_id
            cloudinary_url = f"https://res.cloudinary.com/{cloud_name}/video/upload/raga-rasa/songs/{rasa}/{song_id}"
            
            # Update the document
            result = await atlas_db.songs.update_one(
                {"_id": song['_id']},
                {"$set": {"audio_url": cloudinary_url}}
            )
            
            if result.modified_count > 0:
                updated_count += 1
                print(f"Updated: {song.get('title', 'Unknown')} -> {cloudinary_url}")
        
        print(f"\nSuccessfully updated {updated_count} songs")
        
        # Verify
        print("\nVerifying URLs...")
        sample = await atlas_db.songs.find_one()
        if sample:
            print(f"Sample song URL: {sample.get('audio_url')}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        atlas_client.close()

if __name__ == "__main__":
    asyncio.run(update_urls_to_cloudinary())
