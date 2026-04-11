# RagaRasa Music Therapy - Complete API Reference

## Database Status: ✅ FULLY OPERATIONAL

**Total Documents: 598** across 7 collections with complete data relationships

---

## 📊 Quick Statistics

| Metric | Count |
|--------|-------|
| **Songs** | 68 |
| **Users** | 5 |
| **Sessions** | 40 |
| **Ratings** | 140 |
| **Session Images** | 245 |
| **Psychometric Tests** | 80 |
| **Context Scores** | 20 |
| **Total Relationships** | 598+ |

---

## 🎵 Songs Collection

**68 Therapeutic Songs by Rasa:**
- Shaant (Peaceful): 32 songs
- Shok (Sorrowful): 21 songs  
- Shringar (Romantic): 7 songs
- Veer (Heroic): 8 songs

**With Complete Metadata:**
- Title, artist, duration
- Audio features (energy, valence, tempo)
- Streaming URLs
- Play counts and ratings
- File paths and sizes

---

## 👥 Users Collection

**5 Sample Users:**
- Unique user_id for each
- Email and preferences
- Favorite ragas
- Session tracking
- Total listening time

---

## 📅 Sessions Collection - Complete Structure

Each session includes:

**Timing**
- created_at, started_at, ended_at
- Duration in minutes

**Emotion Analysis**
- Detected emotion (happy, sad, calm, energetic, etc.)
- Assigned rasa (Shringar, Shaant, Veer, Shok)
- Confidence score (0-1)

**Music Recommendations**
- Array of recommended_songs
- Array of played_songs

**User Engagement**
- Ratings linked by rating_ids
- Songs rated during session

**Session Captures**
- Images array (245 images total)
- Pre/post psychometric tests

**Cognitive Data**
```json
{
  "pre_test": {
    "memory_score": 0-6,
    "reaction_time": milliseconds,
    "accuracy_score": 0-100
  },
  "post_test": {
    "memory_score": 0-6,
    "reaction_time": milliseconds,
    "accuracy_score": 0-100
  }
}
```

**User Feedback**
- Mood after session
- Session rating (1-5 stars)
- Comments and recommendations

---

## ⭐ Ratings Collection

**140 Complete Ratings:**
- Each links: user → song → session
- Tracks emotion before/after
- Includes feedback text
- 1-5 star ratings
- Timestamps for all actions

**Enables:**
- Average song ratings
- User rating history
- Emotional impact tracking
- Satisfaction metrics

---

## 📸 Images Collection

**245 Session Captures:**
- Organized by session
- Emotion detection per frame
- Confidence scores
- Facial expression intensity
- Gaze direction tracking

**Enables:**
- Emotion timeline visualization
- Session playback
- Emotional journey tracking

---

## 🧠 Psychometric Tests Collection

**80 Cognitive Assessments:**
- 40 pre-tests (before sessions)
- 40 post-tests (after sessions)

**Metrics Tracked:**
- Memory score (0-6)
- Reaction time (milliseconds)
- Accuracy percentage (0-100)

**Enables:**
- Cognitive improvement tracking
- Therapy effectiveness measurement
- Progress analytics

---

## 📈 Context Scores Collection

**20 Wellness Analytics:**
- Wellness score (0-100)
- Engagement score (0-100)
- Emotional stability (0-100)
- Cognitive improvement percentage
- Overall therapy effectiveness

---

## 🔌 API Endpoint Categories

### Session Management (7 endpoints)
```
✓ Create sessions
✓ Update emotions/ragas
✓ Add songs to session
✓ Complete sessions
✓ Get session summaries
✓ List sessions
✓ Track session details
```

### Rating System (7 endpoints)
```
✓ Create ratings
✓ List ratings
✓ Update ratings
✓ Delete ratings
✓ Get song ratings
✓ User rating history
✓ Session ratings
```

### Psychometric Testing (4 endpoints)
```
✓ Create test records
✓ Get test details
✓ List tests
✓ Pre/post comparison
✓ Improvement calculation
```

### Image Management (6 endpoints)
```
✓ Capture images
✓ Get image metadata
✓ Session image timeline
✓ Emotion timeline
✓ Facial analysis
✓ Delete images
```

### Song Catalog (4 endpoints)
```
✓ List songs
✓ Get song details
✓ Stream audio
✓ Song ratings
```

---

## 🗄️ Database Relationships

```
User
  ↓
  └→ Sessions (1:many)
       ↓
       ├→ Ratings (1:many) ←→ Songs
       ├→ Images (1:many)
       ├→ Psychometric Tests (1:2)
       └→ Context Scores (1:1)
```

---

## 📝 Data Flow Example

1. **User starts session**
   - POST /api/session/start
   - Returns: session_id

2. **Emotion detected**
   - PUT /api/session/{session_id}/update-emotion
   - Stores: emotion, rasa, confidence

3. **Recommendations made**
   - Songs fetched for assigned rasa
   - PUT /api/session/{session_id}/add-song (type=recommended)

4. **User plays song**
   - GET /api/songs/stream/{song_id}
   - PUT /api/session/{session_id}/add-song (type=played)

5. **User rates song**
   - POST /api/rate-song
   - Creates rating linked to session

6. **Images captured**
   - POST /api/image/capture
   - Stores frame with emotion detection

7. **Tests administered**
   - POST /api/psychometric-test (type=pre_test, post_test)
   - Tracks cognitive changes

8. **Session completed**
   - PUT /api/session/{session_id}/complete
   - Calculates duration and generates summary

---

## 🎯 Key Features

✅ **Complete Session Tracking**
- From start to finish with all data

✅ **Emotion-Music Mapping**
- 68 songs organized by 4 therapeutic ragas

✅ **User Engagement**
- Ratings, feedback, preferences

✅ **Cognitive Analytics**
- Pre/post testing with improvement metrics

✅ **Session Recording**
- Images, timestamps, facial analysis

✅ **Therapeutic Tracking**
- Wellness scores and effectiveness metrics

✅ **Recommendation Engine**
- Emotion-based song suggestions

---

## 📱 Frontend Integration Ready

All endpoints are:
- ✅ Documented
- ✅ Tested with sample data
- ✅ Properly indexed
- ✅ Error handled
- ✅ CORS enabled

---

## 🚀 Getting Started

1. **Verify Database**
   ```bash
   python verify_db.py
   ```

2. **Start Backend**
   ```bash
   python main.py
   ```

3. **Access API Docs**
   ```
   http://localhost:8000/docs
   ```

4. **View Database**
   ```
   MongoDB: localhost:27017
   Database: raga_rasa
   ```

---

**Database Implementation: 100% Complete** ✅
