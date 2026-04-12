#!/usr/bin/env python3
from pymongo import MongoClient
import asyncio

uri = 'mongodb+srv://Rishi123:Rishi_123@majorproject.lpwzhzc.mongodb.net/?appName=MajorProject'

# Test 1: Direct MongoDB query
client = MongoClient(uri)
db = client['raga_rasa']
songs_collection = db['songs']

print("TEST 1: Direct MongoDB Query")
all_songs = list(songs_collection.find({}))
print(f"  Total songs in DB: {len(all_songs)}")

print("\nTEST 2: Query by Shringar rasa")
shringar_songs = list(songs_collection.find({"rasa": "Shringar"}))
print(f"  Shringar songs: {len(shringar_songs)}")
if shringar_songs:
    print(f"  First: {shringar_songs[0].get('title')}")

print("\nTEST 3: Query by Shaant rasa")
shaant_songs = list(songs_collection.find({"rasa": "Shaant"}))
print(f"  Shaant songs: {len(shaant_songs)}")

print("\nTEST 4: Check field names in first document")
sample = songs_collection.find_one()
if sample:
    print("  Fields in document:")
    for key in sample.keys():
        print(f"    - {key}")

client.close()
