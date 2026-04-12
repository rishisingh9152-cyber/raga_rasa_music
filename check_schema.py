#!/usr/bin/env python3
from pymongo import MongoClient

uri = 'mongodb+srv://Rishi123:Rishi_123@majorproject.lpwzhzc.mongodb.net/?appName=MajorProject'
client = MongoClient(uri)
db = client['raga_rasa']
collection = db['songs']

sample = collection.find_one()

# Check the structure that RagaSchema expects
print("RagaSchema expects:")
print("  - song_id: str")
print("  - title: str")
print("  - rasa: str")
print("  - audio_url: str")
print("  - duration: str")
print("  - storage_metadata: Optional[...]")

print("\nSample document from DB:")
print(f"  _id: {sample.get('_id')}")
print(f"  title: {sample.get('title')}")
print(f"  rasa: {sample.get('rasa')}")
print(f"  audio_url: {sample.get('audio_url', 'MISSING')}")
print(f"  duration: {sample.get('duration')} (type: {type(sample.get('duration')).__name__})")
print(f"  storage_metadata: {sample.get('storage_metadata', 'MISSING')}")

print("\nAll fields:")
for key, value in sample.items():
    if key not in ['_id', 'title', 'rasa', 'audio_url', 'duration', 'storage_metadata']:
        print(f"  {key}: {type(value).__name__}")

# Check if audio_url is complete
print(f"\nAudio URL details:")
url = sample.get('audio_url', '')
if url:
    print(f"  Starts with: {url[:50]}")
    print(f"  Length: {len(url)}")
    print(f"  Ends with: {url[-50:]}")
else:
    print("  URL is empty or missing!")

client.close()
