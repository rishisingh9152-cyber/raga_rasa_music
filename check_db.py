#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pymongo

client = pymongo.MongoClient('mongodb+srv://Rishi123:Rishi_123@majorproject.lpwzhzc.mongodb.net/?appName=MajorProject')
db = client['raga_rasa']
songs = list(db.songs.find().limit(10))

print("Current songs in MongoDB:")
for song in songs:
    song_id = song["song_id"]
    title = song["title"]
    rasa = song["rasa"]
    url = song["audio_url"]
    print(f"\nID: {song_id}")
    print(f"Title: {title}")
    print(f"Rasa: {rasa}")
    print(f"URL: {url}")
    print("---")
