# Recommendation Engine - Visual Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     RECOMMENDATION REQUEST FLOW                             │
└─────────────────────────────────────────────────────────────────────────────┘

INPUT
  ↓
  ├─ emotion: "Sad"
  ├─ cognitive_data: {memory: 1, reaction_time: 450, accuracy: 35}
  ├─ user_id: "user_123" (optional)
  └─ session_id: "session_456" (optional)

════════════════════════════════════════════════════════════════════════════════

STEP 1: EMOTION → RASA MAPPING
┌──────────────────────────────────────────────────────────────────┐
│ EMOTION_TO_RASA = {                                              │
│   'Happy': 'Shringar',                                            │
│   'Sad': ['Shaant', 'Shringar'],  ← SAD maps to BOTH!           │
│   'Angry': 'Shaant',                                              │
│   'Fearful': 'Veer',                                              │
│   'Disgusted': 'Veer',                                            │
│   'Neutral': 'Shaant'                                             │
│ }                                                                 │
└──────────────────────────────────────────────────────────────────┘
  ↓
  Sad → ['Shaant', 'Shringar']  (Two ragas for balanced therapy)

════════════════════════════════════════════════════════════════════════════════

STEP 2: FETCH MATCHING SONGS
┌─────────────────────────────────────────────────────────────────┐
│ MongoDB Queries:                                                │
│ ┌─────────────────────────────────────────────────────────┐   │
│ │ db.songs.find({"rasa": "Shaant"})  → 32 songs        │   │
│ └─────────────────────────────────────────────────────────┘   │
│ ┌─────────────────────────────────────────────────────────┐   │
│ │ db.songs.find({"rasa": "Shringar"}) → 7 songs        │   │
│ └─────────────────────────────────────────────────────────┘   │
│ ────────────────────────────────────────────────────────────── │
│ Total: 39 songs to score                                       │
└─────────────────────────────────────────────────────────────────┘

════════════════════════════════════════════════════════════════════════════════

STEP 3: SCORE EACH SONG (The Core Algorithm)
┌──────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│  FOR EACH OF 39 SONGS:                                                      │
│                                                                              │
│  ┌─ Calculate CONTENT SCORE (0-1.0)                                        │
│  │   ├─ Base: 0.7                                                          │
│  │   ├─ Check: memory < 2? (user can't remember things)                   │
│  │   │         → Song in [Shaant, Shok]? → +0.15                         │
│  │   ├─ Check: reaction_time > 400ms? (user is slow)                     │
│  │   │         → Song is Veer? → +0.10                                    │
│  │   ├─ Check: accuracy < 40? (user made mistakes)                       │
│  │   │         → Song is Shringar? → +0.15                               │
│  │   └─ Check: Low memory + Low energy song? → +0.10                     │
│  │                                                                         │
│  ├─ Calculate USER PREFERENCE SCORE (0-1.0)                               │
│  │   ├─ Check: Did THIS USER rate this song?                             │
│  │   │         → YES: Use their rating / 5.0                             │
│  │   │         → NO: Check community average                              │
│  │   ├─ If community has ratings: avg_rating / 5.0                       │
│  │   └─ If no ratings: Use default 0.5                                   │
│  │                                                                         │
│  └─ Calculate FRESHNESS SCORE (0-1.0)                                      │
│      └─ Formula: freshness = 1.0 - (days_old / 365) × 0.5                │
│          (Newer songs get slightly higher scores)                          │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │ COMBINE SCORES WITH WEIGHTS:                                       │  │
│  │                                                                    │  │
│  │  FINAL_SCORE = (0.5 × CONTENT_SCORE)                             │  │
│  │              + (0.3 × USER_PREFERENCE_SCORE)                      │  │
│  │              + (0.2 × FRESHNESS_SCORE)                            │  │
│  │                                                                    │  │
│  │  Why this weighting?                                              │  │
│  │  • 50% CONTENT: User's mental state is paramount                 │  │
│  │  • 30% PREFERENCE: Community wisdom personalizes                 │  │
│  │  • 20% FRESHNESS: Slight variety, not overwhelming               │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

════════════════════════════════════════════════════════════════════════════════

STEP 4: RANK SONGS
┌──────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│ All 39 songs now have scores. Sort by FINAL_SCORE (highest first):        │
│                                                                              │
│ Rank  Song Title              Rasa      Score   Confidence                 │
│ ──────────────────────────────────────────────────────────────────────    │
│  1.   Raga Bhairav           Shringar   0.865   ██████████░ 86.5%  ⭐     │
│  2.   Raga Yaman             Shaant     0.815   ██████████░ 81.5%         │
│  3.   Raga Malkauns          Shaant     0.645   ████████░░░ 64.5%         │
│  4.   Raga Darbari           Shaant     0.612   ███████░░░░ 61.2%         │
│  5.   Raga Kharaharapriya    Shringar   0.598   ███████░░░░ 59.8%         │
│        (34 more songs...)                                                   │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

════════════════════════════════════════════════════════════════════════════════

OUTPUT (Top 5 songs returned)
┌──────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│  [                                                                          │
│    {                                                                        │
│      "song_id": "shringar/bhairav",                                       │
│      "title": "Raga Bhairav",                                              │
│      "rasa": "Shringar",                                                   │
│      "audio_url": "/api/songs/stream/shringar/bhairav",                  │
│      "confidence": 0.865,  ← User sees how confident we are              │
│      "duration": 480                                                       │
│    },                                                                       │
│    {                                                                        │
│      "song_id": "shaant/yaman",                                           │
│      "title": "Raga Yaman",                                               │
│      "rasa": "Shaant",                                                    │
│      "audio_url": "/api/songs/stream/shaant/yaman",                      │
│      "confidence": 0.815                                                  │
│    },                                                                       │
│    ... (3 more songs)                                                      │
│  ]                                                                          │
│                                                                              │
│  Frontend displays these 5 songs with play buttons for user to try         │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## Scoring Bonus Reference Sheet

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                    CONTENT SCORE BONUSES                                     │
└──────────────────────────────────────────────────────────────────────────────┘

COGNITIVE STATE    CONDITION          PREFERRED RAGA    BONUS
──────────────────────────────────────────────────────────────────────────────
Low Memory         memory < 2         Shaant, Shok      +0.15
                   (can't focus)      (calming, simple)

Slow Reaction      reaction_time>400  Veer              +0.10
                   (sluggish, tired)  (vigorous, energy)

Low Accuracy       accuracy < 40      Shringar          +0.15
                   (mistakes, sad)    (happy, uplifting)

Low Memory +       Both conditions    Low-energy songs  +0.10
Low Energy Song    match              (double bonus)
──────────────────────────────────────────────────────────────────────────────

FRESHNESS DECAY OVER TIME
──────────────────────────────────────────────────────────────────────────────
Days Old     Freshness Score    How it feels
────────────────────────────────────────────
0 days       1.0                BRAND NEW - Maximum freshness
30 days      0.96               Very fresh
90 days      0.88               Relatively recent
180 days     0.75               6 months old
365 days     0.5                1 year old - MINIMUM
730 days     0.5                Very old - Still minimum (clamped)
────────────────────────────────────────────

Note: Score is CLAMPED between 0.5-1.0, so very old classics
      still get 0.5 (not penalized below that)
```

---

## Example: How Content Score Works

```
Scenario: User with low memory asking for recommendations

User Profile:
  memory_score = 1       (very low)
  reaction_time = 250    (normal)
  accuracy_score = 50    (okay)

Song 1: Raga Yaman (Shaant - peaceful, simple)
  Base Score: 0.7
  + memory < 2 AND Rasa in [Shaant, Shok]? YES → +0.15
  = 0.85  ← Gets BOOSTED because song matches user's state

Song 2: Raga Marwa (Shringar - complex, emotional)
  Base Score: 0.7
  + memory < 2 AND Rasa in [Shaant, Shok]? NO
  = 0.7  ← No boost, song is complex (not ideal for low memory)

Song 3: Raga Darbari (Shaant - peaceful, mellow)
  Base Score: 0.7
  + memory < 2 AND Rasa in [Shaant, Shok]? YES → +0.15
  + accuracy < 40? NO
  = 0.85  ← Same boost as Song 1

RESULT: Peaceful ragas (Shaant) score higher for users with low memory
        because the music is simpler and easier to process
```

---

## Algorithm Time Complexity

```
Operation: Recommend(emotion, cognitive_data, user_id)
────────────────────────────────────────────────────────

Step 1 (Emotion mapping):     O(1) - Dict lookup
Step 2 (Fetch songs):         O(n) - Database query, n = songs in rasa
Step 3 (Score each song):     O(n × m) - n songs, m operations per song
                                (but m is constant: 3 scoring functions)
Step 4 (Sort & return top 5): O(n log n) - Sort all songs

OVERALL: O(n log n) where n = number of songs in matching ragas

Performance:
  • With 68 total songs, ~7-32 per rasa
  • Scoring 39 songs takes milliseconds
  • Database query takes 1-5ms
  • Total response time: typically 10-50ms
```
