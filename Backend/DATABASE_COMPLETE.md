# RagaRasa Music Therapy Platform - Complete Database Setup

## ✅ COMPLETE SETUP STATUS

All database collections have been successfully created, indexed, and populated with comprehensive sample data demonstrating complete relationships between all entities.

---

## 📊 Database Overview

### Total Documents: **598**

| Collection | Count | Purpose |
|------------|-------|---------|
| **songs** | 68 | All therapy music with metadata |
| **users** | 5 | User profiles with preferences |
| **sessions** | 40 | Therapy sessions with all details |
| **ratings** | 140 | User ratings linked to sessions and songs |
| **images** | 245 | Session images with emotion detection |
| **psychometric_tests** | 80 | Pre/post cognitive assessments (2 per session) |
| **context_scores** | 20 | Wellness analytics and improvement metrics |
| **TOTAL** | **598** | Complete interconnected data |

---

## 🎵 Songs Collection (68 documents)

### Structure
```json
{
  "_id": "shok/Desh_amjadalikhan_hasya_shant",
  "title": "Desh amjadalikhan hasya shant",
  "artist": "Amjad Ali Khan",
  "rasa": "Shok",
  "audio_url": "/api/songs/stream/shok/Desh_amjadalikhan_hasya_shant",
  "file_path": "C:\\Major Project\\Songs\\shok\\Desh_amjadalikhan_hasya_shant.mp3",
  "duration": "14:25",
  "file_size": 41,547,392,
  "file_size_mb": 39.61,
  "audio_features": {
    "energy": 0.4,
    "valence": 0.3,
    "tempo": 90,
    "bitrate": "192 kbps"
  },
  "play_count": 15,
  "average_rating": 4.2,
  "rating_count": 8,
  "created_at": "2026-04-09T14:55:14.152000",
  "updated_at": "2026-04-09T14:55:14.152000"
}
```

### Breakdown by Rasa
- **Shaant (Peaceful)**: 32 songs
- **Shok (Sorrowful)**: 21 songs
- **Shringar (Romantic)**: 7 songs
- **Veer (Heroic)**: 8 songs

### Indexes
- `rasa` - Filter songs by emotional type
- `title` - Search songs by name
- `artist` - Filter by artist
- `created_at` - Sort by upload date

---

## 👥 Users Collection (5 documents)

### Structure
```json
{
  "_id": "user_1aef41cb",
  "user_id": "user_1aef41cb",
  "email": "user1@ragarasa.com",
  "name": "User 1",
  "created_at": "2026-04-09T14:55:14.192000",
  "preferences": {
    "favorite_ragas": ["Shaant", "Shringar"],
    "preferred_time_of_day": "morning",
    "listening_frequency": "daily"
  },
  "total_sessions": 8,
  "total_time_minutes": 320
}
```

### Indexes
- `user_id` (unique) - User identification
- `created_at` - Registration date sorting

---

## 📅 Sessions Collection (40 documents)

### Complete Session Structure
```json
{
  "_id": "session_a817601f1609",
  "session_id": "session_a817601f1609",
  "user_id": "user_1aef41cb",
  "created_at": "2026-03-30T12:45:00",
  "started_at": "2026-03-30T12:50:00",
  "ended_at": "2026-03-30T13:35:00",
  "emotion": "energetic",
  "rasa": "Veer",
  "confidence": 0.876,
  "duration_minutes": 45.0,
  "status": "completed",
  "cognitive_data": {
    "pre_test": {
      "memory_score": 4,
      "reaction_time": 450,
      "accuracy_score": 78.5
    },
    "post_test": {
      "memory_score": 5,
      "reaction_time": 380,
      "accuracy_score": 85.2
    }
  },
  "recommended_songs": ["veer/bhimpalasi_veer", "veer/adana_nikhilbanerjee_veer"],
  "played_songs": ["veer/bhimpalasi_veer"],
  "ratings": ["rating_abc123def456", "rating_xyz789"],
  "images": ["image_img001", "image_img002", "image_img003"],
  "psychometric_tests": ["test_pre001", "test_post001"],
  "feedback": {
    "mood_after": "much better",
    "session_rating": 5,
    "comment": "Great therapeutic experience",
    "would_recommend": true,
    "energy_level_after": 4
  },
  "updated_at": "2026-03-30T13:35:01"
}
```

### Session Relationships
Each session contains arrays of:
- **recommended_songs** - Songs suggested by recommendation engine
- **played_songs** - Songs actually played during session
- **ratings** - User ratings for each song (array of rating_ids)
- **images** - Frames captured during session (array of image_ids)
- **psychometric_tests** - Cognitive assessments (pre_test and post_test)

### Indexes
- `user_id` - Filter sessions by user
- `created_at` - Sort by date
- `status` - Filter by session status
- `emotion` - Filter by detected emotion
- `rasa` - Filter by assigned rasa

---

## ⭐ Ratings Collection (140 documents)

### Structure
```json
{
  "_id": "rating_abc123def456",
  "rating_id": "rating_abc123def456",
  "session_id": "session_a817601f1609",
  "user_id": "user_1aef41cb",
  "song_id": "veer/bhimpalasi_veer",
  "song_title": "Bhimpalasi Veer",
  "rasa": "Veer",
  "rating": 5,
  "feedback_text": "Loved the energetic music!",
  "emotion_before": "sad",
  "emotion_after": "happy",
  "timestamp": "2026-03-30T13:20:00",
  "created_at": "2026-03-30T13:20:00",
  "updated_at": "2026-03-30T13:20:00"
}
```

### Key Features
- **Bidirectional Linking**: Links users, sessions, and songs
- **Emotion Tracking**: Records emotional state before and after
- **Feedback**: Captures user sentiment about the song
- **Average Rating**: Each song has `average_rating` calculated from all ratings

### Indexes
- `(user_id, song_id)` - User's rating for specific song
- `session_id` - All ratings in a session
- `song_id` - All ratings for a song
- `created_at` - Chronological sorting

### Query Examples
```
GET /api/ratings?session_id=session_a817601f1609
GET /api/song/{song_id}/ratings
GET /api/ratings?user_id=user_1aef41cb
```

---

## 📸 Images Collection (245 documents)

### Structure
```json
{
  "_id": "image_img001",
  "image_id": "image_img001",
  "session_id": "session_a817601f1609",
  "timestamp": "2026-03-30T12:55:30",
  "image_path": "C:\\RagaRasa\\Sessions\\session_a817601f1609\\frame_0001.jpg",
  "emotion_detected": "energetic",
  "confidence": 0.876,
  "facial_features": {
    "face_detected": true,
    "expression_intensity": 0.85,
    "gaze_direction": "forward"
  },
  "created_at": "2026-03-30T12:55:30"
}
```

### Features
- **Session-Specific Storage**: Images organized by session directory
- **Emotion Timeline**: Track emotional changes during session
- **Facial Analysis**: Expression intensity and gaze tracking
- **Multiple Frames**: Average 6 images per session

### Indexes
- `session_id` - All images in a session
- `timestamp` - Chronological order

### Query Examples
```
GET /api/session/{session_id}/images
GET /api/session/{session_id}/emotion-timeline
```

---

## 🧠 Psychometric Tests Collection (80 documents)

### Structure
```json
{
  "_id": "test_pre001",
  "test_id": "test_pre001",
  "session_id": "session_a817601f1609",
  "user_id": "user_1aef41cb",
  "test_type": "pre_test",
  "timestamp": "2026-03-30T12:48:00",
  "data": {
    "memory_score": 4,
    "reaction_time": 450,
    "accuracy_score": 78.5
  },
  "notes": "Pre-session cognitive assessment",
  "created_at": "2026-03-30T12:48:00"
}
```

### Two Tests Per Session
- **Pre-Test**: Before therapy session starts
- **Post-Test**: After therapy session ends

### Cognitive Metrics
- **Memory Score**: 0-6 scale
- **Reaction Time**: Milliseconds (lower is better)
- **Accuracy Score**: 0-100 percentage

### Indexes
- `session_id` - Both tests for a session
- `user_id` - User's test history
- `test_type` - Filter pre/post tests

### Query Examples
```
GET /api/session/{session_id}/psychometric-comparison
```

---

## 📈 Context Scores Collection (20 documents)

### Structure
```json
{
  "_id": "score_score001",
  "score_id": "score_score001",
  "user_id": "user_1aef41cb",
  "session_id": "session_a817601f1609",
  "timestamp": "2026-03-30T13:35:01",
  "wellness_score": 85.2,
  "engagement_score": 92.5,
  "emotional_stability": 78.5,
  "cognitive_improvement": 28.5,
  "overall_therapy_effectiveness": 84.3
}
```

### Analytics Metrics
- **Wellness Score**: 0-100 overall well-being
- **Engagement Score**: 0-100 user engagement level
- **Emotional Stability**: 0-100 emotional consistency
- **Cognitive Improvement**: Percentage improvement in pre/post tests
- **Overall Effectiveness**: Combined therapy effectiveness score

### Indexes
- `user_id` - User's wellness history
- `session_id` - Scores for specific session

---

## 🔗 Data Relationships

### Session ↔ Ratings
```
Session contains array of rating_ids
Rating contains session_id reference
Each rating links user, song, and session
```

### Session ↔ Images
```
Session contains array of image_ids
Image contains session_id reference
Enables emotion timeline visualization
```

### Session ↔ Psychometric Tests
```
Session contains array of test_ids
Tests contain session_id reference
Exactly 2 tests per session (pre and post)
```

### Song ↔ Ratings
```
Each song has average_rating and rating_count
Multiple ratings per song across all sessions
Rating contains song_id reference
```

### User ↔ Sessions
```
User has total_sessions and total_time_minutes
Session contains user_id reference
Multiple sessions per user
```

---

## 📡 API Endpoints

### Sessions
```
POST   /api/session/start                          - Create new session
GET    /api/session/{session_id}                   - Get session details
GET    /api/sessions                               - List all sessions
PUT    /api/session/{session_id}/update-emotion    - Update emotion/rasa
PUT    /api/session/{session_id}/add-song          - Add song to session
PUT    /api/session/{session_id}/complete          - Mark session complete
GET    /api/session/{session_id}/summary           - Get session summary
```

### Ratings
```
POST   /api/rate                                   - Create detailed rating
POST   /api/rate-song                              - Simple song rating
GET    /api/rating/{rating_id}                     - Get specific rating
GET    /api/ratings                                - List ratings
GET    /api/song/{song_id}/ratings                 - Get song ratings
PUT    /api/rating/{rating_id}                     - Update rating
DELETE /api/rating/{rating_id}                     - Delete rating
```

### Psychometric Tests
```
POST   /api/psychometric-test                      - Create test
GET    /api/psychometric-test/{test_id}            - Get test details
GET    /api/psychometric-tests                     - List tests
GET    /api/session/{session_id}/psychometric-comparison - Compare pre/post
```

### Images
```
POST   /api/image/capture                          - Capture session image
GET    /api/image/{image_id}                       - Get image metadata
GET    /api/images                                 - List images
GET    /api/session/{session_id}/images            - Get session images
GET    /api/session/{session_id}/emotion-timeline  - Get emotion changes
DELETE /api/image/{image_id}                       - Delete image
```

### Songs
```
GET    /api/ragas/list                             - List all songs
GET    /api/ragas/{raga_id}                        - Get song details
GET    /api/songs/{song_id}                        - Get song with metadata
GET    /api/songs/stream/{song_id}                 - Stream audio file
```

---

## 🏗️ Database Indexes

### Performance Optimization
All collections have been indexed for efficient queries:

**Songs**
- `rasa` - Filter by emotional type
- `title` - Search by name
- `artist` - Filter by artist
- `created_at` - Sort by date

**Sessions**
- `user_id` - User's sessions
- `created_at` - Date sorting
- `status` - Filter by status
- `emotion` - Filter by emotion
- `rasa` - Filter by rasa

**Ratings**
- `(user_id, song_id)` - User's rating for song
- `session_id` - Ratings in session
- `song_id` - Ratings for song
- `created_at` - Date sorting

**Psychometric Tests**
- `session_id` - Tests in session
- `user_id` - User's test history
- `test_type` - Filter pre/post

**Images**
- `session_id` - Images in session
- `timestamp` - Time order

**Context Scores**
- `session_id` - Scores for session
- `user_id` - User's scores

---

## 📥 Running the Seed Script

To repopulate the database with fresh demo data:

```bash
cd C:\Major Project\backend
python seed_all_data.py
```

This creates:
- 68 songs (all from C:\Major Project\Songs)
- 5 sample users
- 40 complete sessions
- 140 ratings (linked to sessions)
- 245 images (linked to sessions)
- 80 psychometric tests (2 per session)
- 20 context scores

---

## 🔍 Data Verification

Check current database status:

```bash
python verify_db.py
```

Output shows:
- Total document count per collection
- Sample data from each collection
- Relationship validation

---

## 🎯 Next Steps for Frontend

The backend is now ready to serve:

1. **Session Management**: Start/complete sessions with emotions
2. **Song Streaming**: Get recommendations and stream audio
3. **Rating System**: Record user ratings and feedback
4. **Image Capture**: Save session frames for analysis
5. **Analytics**: Track cognitive improvements and wellness

All endpoints are documented at: `http://localhost:8000/docs`

---

## 📋 Collection Schema Summary

```
songs
├── _id, title, artist, rasa
├── audio_url, file_path, duration
├── file_size, audio_features
└── play_count, average_rating, rating_count

users
├── _id, user_id, email, name
├── preferences (favorite_ragas, preferred_time)
└── total_sessions, total_time_minutes

sessions
├── _id, session_id, user_id
├── created_at, started_at, ended_at
├── emotion, rasa, confidence, duration_minutes
├── cognitive_data (pre/post tests)
├── recommended_songs [], played_songs []
├── ratings [], images [], psychometric_tests []
├── feedback, status
└── updated_at

ratings
├── _id, rating_id
├── session_id, user_id, song_id, song_title, rasa
├── rating (1-5), feedback_text
├── emotion_before, emotion_after
└── timestamp, created_at, updated_at

images
├── _id, image_id, session_id
├── timestamp, image_path
├── emotion_detected, confidence
├── facial_features (expression, gaze)
└── created_at

psychometric_tests
├── _id, test_id, session_id, user_id
├── test_type (pre_test/post_test)
├── timestamp, data (memory, reaction_time, accuracy)
├── notes, improvement_percentage
└── created_at

context_scores
├── _id, score_id, user_id, session_id
├── timestamp, wellness_score, engagement_score
├── emotional_stability, cognitive_improvement
└── overall_therapy_effectiveness
```

---

**Database Setup Complete! 🎉**

All collections are indexed, populated with sample data, and ready for full production use.
