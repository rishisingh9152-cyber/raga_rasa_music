# Recommendation Engine - Quick Reference Card

## 🎯 The 4-Step Process

```
┌─────────────────────────────────────────────────────────────────┐
│ INPUT: emotion + cognitive_data + user_id                      │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ STEP 1: Emotion → Rasa(s)                                       │
│ "Sad" → ["Shaant", "Shringar"]                                 │
│ Uses EMOTION_TO_RASA dictionary                                │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ STEP 2: Fetch Songs                                             │
│ Query MongoDB for all songs matching those ragas               │
│ Result: List of 7-32+ songs depending on emotion              │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ STEP 3: Score Each Song (THE CORE)                              │
│                                                                  │
│ For each song calculate:                                        │
│   • CONTENT_SCORE (50 weight) ← User's mental state           │
│   • USER_SCORE (30 weight) ← Previous/Community ratings       │
│   • FRESHNESS_SCORE (20 weight) ← Age of song                │
│                                                                  │
│ FINAL = 0.5*C + 0.3*U + 0.2*F                                 │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ STEP 4: Sort & Return Top 5                                     │
│ Songs ranked by final score (highest first)                    │
│ OUTPUT: [Song1, Song2, Song3, Song4, Song5]                   │
└──────────────────────────────────────────────────────────────────┘
```

---

## 📊 Scoring Breakdown

### Content Score (50% weight) - User's Mental State Match

**Base:** 0.7 for all songs

**Bonuses:**
```
IF Low Memory (< 2)           & Song is [Shaant, Shok]  → +0.15
IF Slow Reaction (> 400ms)    & Song is Veer           → +0.10
IF Low Accuracy (< 40)        & Song is Shringar       → +0.15
IF Low Memory                 & Song has low energy    → +0.10
```

**Range:** 0.7 to 0.95

---

### User Score (30% weight) - Community Wisdom

**Priority order:**
1. User's own past rating (if exists) → rating/5.0
2. Community average rating → avg/5.0
3. New song, no ratings → 0.5 (neutral default)

**Range:** 0.0 to 1.0

---

### Freshness Score (20% weight) - Recency

**Formula:** `1.0 - (days_old / 365) × 0.5`

**Range:** 0.5 to 1.0 (clamped at 0.5 minimum)

```
TODAY:      1.0 (maximum)
6 months:   0.75
1 year:     0.5 (minimum)
2+ years:   0.5 (still minimum)
```

---

## 🎵 Emotion-Rasa Mapping

```
Happy       → Shringar
Surprised   → Shringar
Sad         → Shaant + Shringar  ← TWO ragas!
Angry       → Shaant
Fearful     → Veer
Disgusted   → Veer
Neutral     → Shaant
```

**Key:** Sad gets TWO ragas for balanced therapy (calm + uplifting)

---

## 📈 Complete Scoring Example

**User State:** Sad, low memory (1), slow reactions (450ms), low accuracy (35)

**Algorithm Processing:**

```
1. Emotion "Sad" → ["Shaant", "Shringar"]

2. Fetch songs:
   - Shaant: 32 songs
   - Shringar: 7 songs
   - Total: 39 songs to score

3. For example Song A (Raga Yaman, Shaant):
   
   Content:  0.7 (base) + 0.15 (matches low memory) = 0.85
   User:     0.8 (they rated it 4/5 before)
   Fresh:    0.75 (6 months old)
   
   FINAL = (0.5 × 0.85) + (0.3 × 0.8) + (0.2 × 0.75)
        = 0.425 + 0.24 + 0.15
        = 0.815  ← 81.5% confidence

4. For example Song B (Raga Bhairav, Shringar):
   
   Content:  0.7 (base) + 0.15 (matches low accuracy) = 0.85
   User:     0.9 (community average 4.5/5)
   Fresh:    1.0 (added today!)
   
   FINAL = (0.5 × 0.85) + (0.3 × 0.9) + (0.2 × 1.0)
        = 0.425 + 0.27 + 0.2
        = 0.895  ← 89.5% confidence ⭐ BETTER!

5. Sort all 39 songs by score, return top 5
```

---

## 🔧 Content Score Logic (Most Complex)

```python
def get_content_bonus(user_state, song_rasa):
    bonus = 0
    
    # Check memory
    if user_state['memory'] < 2:
        if song_rasa in ['Shaant', 'Shok']:
            bonus += 0.15  # Match calm music
    
    # Check reaction time
    if user_state['reaction_time'] > 400:
        if song_rasa == 'Veer':
            bonus += 0.10  # Match vigorous music
    
    # Check accuracy
    if user_state['accuracy'] < 40:
        if song_rasa == 'Shringar':
            bonus += 0.15  # Match uplifting music
    
    # Double bonus for perfect match
    if user_state['memory'] < 2 and song_features['energy'] < 0.5:
        bonus += 0.10  # Calm user + calm song
    
    return min(0.7 + bonus, 1.0)  # Cap at 1.0
```

---

## 💡 Design Philosophy

**Why these weights (50-30-20)?**
- **50% Content:** Current mental state is most important
- **30% Collaborative:** Historical wisdom helps personalize
- **20% Freshness:** Small variety factor, not overwhelming

**Why base score 0.7?**
- All songs in matching rasa are relevant
- Bonuses (0.1-0.15) fine-tune from there
- Never goes below 0 or above 1.0

**Why multiple ragas for Sad?**
- Sadness is complex emotion
- Shaant helps with pain/grief (calming)
- Shringar helps with mood (uplifting)
- More diverse recommendations

**Why freshness minimum 0.5?**
- Classic songs should still get played
- New songs get slight boost, not dominant
- Decays over 1 year for gradual preference shift

---

## 📍 Code Locations

| What | File | Lines |
|------|------|-------|
| Main flow | `recommendation.py` | 33-83 |
| Emotion mapping | `recommendation.py` | 15-23 |
| Content score | `recommendation.py` | 144-180 |
| User score | `recommendation.py` | 182-214 |
| Freshness score | `recommendation.py` | 216-235 |
| Score combination | `recommendation.py` | 103-142 |
| Database queries | `recommendation.py` | 85-101 |

---

## 🚀 Performance

```
Time Complexity: O(n log n) where n = songs in matching ragas
Space Complexity: O(n) for storing song scores

Typical Performance:
  • 7-32 songs per rasa
  • ~39 total songs for Sad emotion
  • Scoring 39 songs: ~5ms
  • Database query: ~1-5ms
  • Sorting: ~1ms
  • Total: 10-50ms response time
```

---

## 🎓 Learning Path

1. **Start here:** Understand Emotion → Rasa mapping
2. **Then:** Learn the 4-step process flow
3. **Deep dive:** Study content, user, and freshness scoring
4. **Advanced:** Understand why each weight is 50-30-20
5. **Expert:** Modify bonuses for different user populations

See `RECOMMENDATION_ENGINE_EXPLAINED.md` for full details!
