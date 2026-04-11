# Recommendation Engine Workings - Detailed Explanation

## Overview
The recommendation engine is a **hybrid system** that combines:
1. **Content-Based Filtering** - matches user's cognitive state with song characteristics
2. **Collaborative Filtering** - uses community ratings to personalize recommendations
3. **Emotion-Rasa Mapping** - maps detected emotions to Indian classical music ragas

---

## Step-by-Step Flow

### STEP 1: Emotion to Rasa Mapping
**Input:** Detected emotion (e.g., "Sad")
**Output:** Target rasa(s) to search for

```
User Emotion → EMOTION_TO_RASA Mapping → Rasa(s)

Example:
  Sad → ['Shaant', 'Shringar']  # Both calming AND uplifting
  Happy → 'Shringar'             # Romantic, joyful
  Angry → 'Shaant'               # Peaceful, pacifying
  Neutral → 'Shaant'             # Meditative
```

**Code Location:** Lines 15-23, 53-57

---

### STEP 2: Fetch Songs by Rasa
**Input:** Target rasa(s)
**Output:** List of all songs matching those ragas

```
Database Query:
  db.songs.find({"rasa": "Shaant"})  → Returns all Shaant raga songs
  db.songs.find({"rasa": "Shringar"}) → Returns all Shringar raga songs
  
Combined Result: Merged list of all matching songs
```

**Code Location:** Lines 59-67, 85-92

---

### STEP 3: Score Each Song
**This is the CORE of the recommendation engine**

Each song gets scored using a weighted formula:

```
FINAL SCORE = (0.5 × CONTENT_SCORE) + (0.3 × USER_SCORE) + (0.2 × FRESHNESS_SCORE)

                ↓                           ↓                      ↓
            50% Weight            30% Weight                20% Weight
          (Most Important)   (User's taste)           (Newer songs boost)
```

**Code Location:** Lines 103-142

---

## A. Content Similarity Score (50% weight)

**Purpose:** Match the song with user's cognitive state

Base Score: **0.7** (all songs start with 0.7)

**Bonuses Applied Based on Cognitive Metrics:**

```
IF memory_score < 2 (low memory):
  → User has trouble remembering things
  → ADD +0.15 if song is Shaant or Shok (calming, simple)
  → Final boost: 0.85/1.0
  
IF reaction_time > 400ms (slow reaction):
  → User is sluggish/slow
  → ADD +0.1 if song is Veer (vigorous, stimulating)
  → Final score: 0.8/1.0
  
IF accuracy_score < 40 (low accuracy):
  → User made mistakes, low confidence
  → ADD +0.15 if song is Shringar (uplifting, happy)
  → Final score: 0.85/1.0
  
IF low memory AND song has low energy:
  → Double match: user is mentally tired AND song is calm
  → ADD +0.1 extra bonus
  → Final score: 0.95/1.0
```

**Example Calculation:**
```
User: memory_score=1, reaction_time=250, accuracy_score=35
Song: Rasa=Shringar

Starting base: 0.7
+ Low memory (1 < 2) & Shringar? NO (Shringar not in Shaant/Shok)
+ Low accuracy (35 < 40) & Shringar? YES → +0.15
= 0.85
```

**Code Location:** Lines 144-180

---

## B. User Preference Score (30% weight)

**Purpose:** Leverage what other users liked

```
Step 1: Check if THIS USER rated this song before
  → If yes: Use their previous rating (0-1 scale)
  → Example: They rated it 4/5 → Score = 4/5 = 0.8

Step 2: If no personal rating, check COMMUNITY average
  → MongoDB aggregation: Average all user ratings
  → Example: Average across all users = 3.5/5 → Score = 3.5/5 = 0.7

Step 3: If no ratings exist (new song)
  → Use default score: 0.5
```

**Scoring Examples:**
```
User personally rated song 5/5 → Score = 1.0 (highest)
User personally rated song 2/5 → Score = 0.4 (avoid it)
Community average is 4.5/5 → Score = 0.9
Community average is 2/5 → Score = 0.4
Brand new song, no ratings → Score = 0.5 (neutral)
```

**Code Location:** Lines 182-214

---

## C. Freshness Score (20% weight)

**Purpose:** Slightly prefer newer songs (variety)

```
Exponential Decay Formula:
  freshness = 1.0 - (days_old / 365) × 0.5

Examples:
  Song added TODAY:
    days_old = 0
    freshness = 1.0 - (0/365) × 0.5 = 1.0 (maximum)

  Song added 6 months ago:
    days_old = 180
    freshness = 1.0 - (180/365) × 0.5 = 0.75

  Song added 1 year ago:
    days_old = 365
    freshness = 1.0 - (365/365) × 0.5 = 0.5 (minimum)

  Song added 2 years ago:
    days_old = 730
    freshness = 1.0 - (730/365) × 0.5 = 0.0 → BUT clamped to 0.5
```

**Code Location:** Lines 216-235

---

## STEP 4: Rank & Return Top 5

```
All scored songs are sorted by final_score (highest first)

Top 5 are returned to the user

FINAL RECOMMENDATION = Song with highest combined score
```

**Code Location:** Lines 77-79

---

## COMPLETE EXAMPLE WALKTHROUGH

**Scenario:** User is SAD with low cognitive performance

```
INPUT:
  emotion = "Sad"
  cognitive_data = {
    memory_score: 1,        # Low memory
    reaction_time: 450,     # Slow
    accuracy_score: 35      # Low accuracy
  }
  user_id = "user_123"

═══════════════════════════════════════════════════════════════

STEP 1: EMOTION TO RASA MAPPING
  Sad → ['Shaant', 'Shringar']
  
═══════════════════════════════════════════════════════════════

STEP 2: FETCH SONGS
  Query 1: db.songs.find({"rasa": "Shaant"}) → 32 songs
  Query 2: db.songs.find({"rasa": "Shringar"}) → 7 songs
  Combined: 39 songs total

═══════════════════════════════════════════════════════════════

STEP 3: SCORE EACH SONG

Song A: "Raga Yaman" (Shaant)
  Content Score:
    Base: 0.7
    + memory < 2 && Shaant? YES → +0.15 = 0.85
    + accuracy < 40 && Shringar? NO
    = 0.85
    
  User Score:
    User previously rated it 4/5 → 0.8
    
  Freshness Score:
    Created 6 months ago → 0.75
    
  FINAL = (0.5 × 0.85) + (0.3 × 0.8) + (0.2 × 0.75)
        = 0.425 + 0.24 + 0.15
        = 0.815 ⭐ Confidence: 81.5%

───────────────────────────────────────────────────────────────

Song B: "Raga Bhairav" (Shringar)
  Content Score:
    Base: 0.7
    + memory < 2 && Shaant? NO
    + accuracy < 40 && Shringar? YES → +0.15 = 0.85
    = 0.85
    
  User Score:
    Never rated before, community avg 4/5 → 0.8
    
  Freshness Score:
    Created today → 1.0
    
  FINAL = (0.5 × 0.85) + (0.3 × 0.8) + (0.2 × 1.0)
        = 0.425 + 0.24 + 0.2
        = 0.865 ⭐ Confidence: 86.5%

───────────────────────────────────────────────────────────────

Song C: "Raga Malkauns" (Shaant)
  Content Score:
    Base: 0.7
    + memory < 2 && Shaant? YES → +0.15 = 0.85
    = 0.85
    
  User Score:
    User rated it poorly before 2/5 → 0.4
    
  Freshness Score:
    Very old (2 years) → 0.5
    
  FINAL = (0.5 × 0.85) + (0.3 × 0.4) + (0.2 × 0.5)
        = 0.425 + 0.12 + 0.1
        = 0.645 ⭐ Confidence: 64.5%

═══════════════════════════════════════════════════════════════

STEP 4: RANK & RETURN TOP 5

Ranking by final score (highest first):
  1. Song B (0.865) ← BEST MATCH
  2. Song A (0.815)
  3. Song C (0.645)
  ... (36 more songs)

OUTPUT TO USER:
  [
    {
      title: "Raga Bhairav",
      rasa: "Shringar",
      audio_url: "/api/songs/stream/shringar/bhairav",
      confidence: 0.865  ← Shows user how confident we are
    },
    {
      title: "Raga Yaman",
      rasa: "Shaant",
      audio_url: "/api/songs/stream/shaant/yaman",
      confidence: 0.815
    },
    ... (top 5 songs)
  ]
```

---

## Key Design Insights

**Why 50-30-20 weighting?**
- **50% Content:** User's current state is most important
- **30% Collaborative:** Community wisdom helps personalization
- **20% Freshness:** Small factor for variety, not overwhelming

**Why multiple ragas for Sad?**
- Sadness needs both calming (Shaant) AND uplifting (Shringar)
- Allows more diverse recommendations

**Why base score of 0.7?**
- All songs are somewhat relevant (they're in the right rasa)
- Bonuses (+0.10-0.15) refine further based on user state

**Why Freshness with exponential decay?**
- Doesn't overly favor new songs
- Minimum 0.5 ensures old classics still get played
- Decays over 1 year for balance

---

## Files & Locations

| Component | File | Lines |
|-----------|------|-------|
| Emotion Mapping | `recommendation.py` | 15-23 |
| Main Flow | `recommendation.py` | 33-83 |
| Content Scoring | `recommendation.py` | 144-180 |
| User Preference | `recommendation.py` | 182-214 |
| Freshness Scoring | `recommendation.py` | 216-235 |
| API Endpoint | `routes/recommendation.py` | - |

