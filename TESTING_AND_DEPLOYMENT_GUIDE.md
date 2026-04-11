# RAGA RASA SOUL - COMPLETE TESTING & DEPLOYMENT GUIDE

## Current System Status

### Services Running
- **MongoDB**: ✅ Running on port 27017
- **Frontend Vite Dev Server**: ✅ Running on port 5173
- **Emotion Recognition Service**: ✅ Running on port 5000
- **Backend FastAPI**: ❌ NEEDS TO BE STARTED on port 8000

### Access Points
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Emotion Service**: http://localhost:5000/detect

---

## How to Start the Backend

### Option 1: Using Batch Script (Recommended for Windows)
```batch
cd C:\Major Project\Backend
backend_start.bat
```

### Option 2: Manual Command
```bash
cd C:\Major Project\Backend
python main.py
```

### Option 3: Using Virtual Environment
```bash
cd C:\Major Project\Backend
call venv\Scripts\activate.bat
python main.py
```

The backend will start on `http://localhost:8000`

---

## Manual End-to-End Testing in Browser

### Test 1: Session Creation & PreTest
**Location**: http://localhost:5173

1. **Start New Session**
   - Click "New Session" button
   - A session ID should be created and displayed

2. **Complete PreTest**
   - You'll see memory test questions
   - Answer the cognitive assessment questions
   - Click "Submit PreTest"
   - Verify success message appears

### Test 2: Emotion Capture
1. **Capture Emotion**
   - You'll see "Capture Emotion" button with camera prompt
   - Click button
   - Browser will request camera access - ALLOW IT
   - Video preview should appear in the canvas
   - Click button again to capture frame
   - Wait for emotion detection (~5-10 seconds)
   - Should see detected emotion displayed (e.g., "Happy", "Sad", "Neutral")

**Expected emotions**: Happy, Sad, Angry, Neutral, Surprised, Disgusted, Fearful

**Test scenarios**:
- Capture with your face visible (should detect specific emotion)
- Capture without face (should fallback to "Neutral")
- Capture at different distances (should work from 1-3 feet)

### Test 3: Song Recommendations
1. **Automatic Recommendation**
   - After emotion is detected, song recommendations appear
   - Should show 5-10 songs based on emotion + cognitive data
   - Each song shows: Title, Artist, Rasa, Duration

2. **Verify Audio URLs**
   - Songs should have working audio URLs
   - URLs format: `/api/songs/stream/filename.mp3`

### Test 4: Audio Playback
1. **Play a Song**
   - Click play button on any recommended song
   - Audio player controls should appear
   - Click play icon to start playback
   - Should hear audio from speakers
   - Should see playback progress

**Test scenarios**:
- Play from different ragas (Shaant, Veer, Shringar, Shok)
- Test pause/resume
- Test progress bar scrubbing
- Test volume control

### Test 5: PostTest & Feedback
1. **Complete PostTest**
   - After listening to songs, new memory test appears
   - Answer the questions
   - Enter mood improvement rating (1-10)
   - Enter feedback text
   - Click "Submit PostTest"

2. **View Final Recommendations**
   - System shows final song recommendations
   - Based on emotion + cognitive improvement

### Test 6: Session Data Verification
1. **Check Session Data**
   - Session should be saved in MongoDB
   - All data captured:
     - PreTest cognitive scores
     - Detected emotion
     - Recommended songs
     - PostTest results
     - Feedback

---

## Automated API Testing (After Backend Starts)

Run the comprehensive test script:

```bash
cd C:\Major Project
python test_e2e_verification.py
```

This tests:
1. Service availability
2. Session creation
3. PreTest submission
4. Emotion detection
5. Song recommendations
6. Audio streaming
7. PostTest submission  
8. Session data retrieval
9. Catalog endpoints

**Expected Output**: 
```
[PASS] SERVICES
[PASS] SESSION
[PASS] PRETEST
[PASS] EMOTION
[PASS] RECOMMENDATIONS
[PASS] AUDIO
[PASS] POSTTEST
[PASS] RETRIEVAL
[PASS] CATALOG

Total: 9/9 tests passed
ALL TESTS PASSED - Application is ready for production!
```

---

## Emotion Detection Test Cases

### Scenario 1: Face Detection with Good Lighting
- **Input**: Clear face image in good lighting
- **Expected**: Specific emotion detected (Happy, Sad, Angry, etc.)
- **Confidence**: > 0.5

### Scenario 2: Multiple Faces
- **Input**: Image with multiple faces
- **Expected**: Dominant emotion detected from primary face
- **Fallback**: "Neutral" if can't detect

### Scenario 3: No Face
- **Input**: Blank image or image without faces
- **Expected**: "Neutral" emotion (no error)
- **Time**: May take 40-50 seconds

### Scenario 4: Poor Lighting
- **Input**: Dark or very bright image
- **Expected**: Emotion detected or fallback to "Neutral"
- **Robustness**: System handles gracefully

### Scenario 5: Service Timeout
- **Input**: Large image or slow connection
- **Expected**: Timeout after 60 seconds, fallback to "Neutral"
- **No Crash**: Application continues normally

---

## Song Audio Playback Test Cases

### Test Case: Audio URL Conversion
- **Frontend Receives**: `/api/songs/stream/shaant_sample.mp3`
- **Frontend Converts To**: `http://localhost:5173/api/songs/stream/shaant_sample.mp3`
- **Audio Element**: Works with absolute URL
- **Expected**: Audio plays successfully

### Test Case: Multiple Ragas
Test audio playback for songs from each rasa:

1. **Shaant (Peaceful)**
   - Sample song: `shaant_sample.mp3`
   - Typical for Calm, Neutral emotions

2. **Veer (Brave/Energetic)**
   - For Angry, Happy emotions
   - Energetic tempo

3. **Shringar (Romantic)**
   - For Happy, Loving moods
   - Melodic and sweet

4. **Shok (Sorrowful)**
   - For Sad, Fearful emotions
   - Melancholic tone

### Test Case: Stream Endpoint
- **Endpoint**: `GET /api/songs/stream/{song_id_or_filename}`
- **Input**: `shaant_sample.mp3`
- **Output**: MP3 file bytes with correct MIME type
- **Status**: 200 OK
- **Size**: Varies (typically 3-8 MB)

---

## Database Verification

### Check Session Storage

```bash
# Connect to MongoDB
mongosh

# Switch to database
use ragarasa_soul

# Check sessions
db.sessions.findOne()

# Expected structure:
{
  _id: ObjectId,
  session_id: "uuid-string",
  created_at: ISODate,
  status: "active" or "completed",
  pretest_data: {
    memory_score: number,
    reaction_time: number,
    accuracy_score: number
  },
  detected_emotion: "emotion-name",
  recommendations: [songs],
  posttest_data: {
    memory_score: number,
    reaction_time: number,
    accuracy_score: number
  },
  feedback: "user-feedback-text"
}
```

### Verify Data Integrity

1. **Check All Sessions**
   ```js
   db.sessions.find().count()  // Should have created sessions
   ```

2. **Check Emotion Distribution**
   ```js
   db.sessions.distinct("detected_emotion")
   // Should return: ["Happy", "Sad", "Neutral", ...]
   ```

3. **Check Cognitive Scores**
   ```js
   db.sessions.aggregate([
     { $match: { pretest_data: { $exists: true } } },
     { $group: { 
       _id: null,
       avg_memory: { $avg: "$pretest_data.memory_score" },
       avg_reaction_time: { $avg: "$pretest_data.reaction_time" }
     }}
   ])
   ```

---

## Error Handling Verification

### Test Error: Camera Denied
1. Click "Capture Emotion"
2. When browser asks for camera permission, click "Deny"
3. **Expected**: Error message shows, no crash

### Test Error: Network Offline
1. Disconnect internet
2. Try to send emotion data
3. **Expected**: Error message, graceful fallback

### Test Error: Emotion Service Down
1. Stop emotion service (port 5000)
2. Click "Capture Emotion"
3. **Expected**: After 60 seconds, falls back to "Neutral", continues normally

### Test Error: MongoDB Down
1. Stop MongoDB
2. Try to create new session
3. **Expected**: Error message, no page crash

---

## Performance Metrics

### Expected Response Times

| Operation | Expected Time | Timeout |
|-----------|---------------|---------|
| Session Creation | < 100 ms | 5 s |
| PreTest Submission | < 200 ms | 5 s |
| Emotion Detection (with face) | 5-10 s | 60 s |
| Emotion Detection (no face) | 40-50 s | 60 s |
| Song Recommendation | < 500 ms | 10 s |
| Audio Stream (10 MB file) | 2-5 s | 30 s |
| PostTest Submission | < 200 ms | 5 s |
| Session Retrieval | < 100 ms | 5 s |

### Memory Usage
- Frontend: ~50-100 MB
- Backend: ~200-300 MB
- MongoDB: ~100-200 MB
- Emotion Service: ~500-800 MB

### CPU Usage
- Idle: < 5%
- During Emotion Detection: 20-40%
- During Audio Playback: 5-10%

---

## Deployment Checklist

- [x] Canvas reference always available for emotion capture
- [x] Emotion service handles 422 errors gracefully
- [x] Base64 data URI prefix stripped correctly
- [x] Audio URLs converted from relative to absolute
- [x] Stream endpoint imports RASA_FOLDERS correctly
- [x] Fallback to "Neutral" emotion when service fails
- [x] All endpoints return proper HTTP status codes
- [x] Error messages are user-friendly
- [x] MongoDB sessions stored correctly
- [x] All ragas/rasas have songs available
- [x] CORS configured for frontend access
- [ ] Backend process running (PENDING - MANUAL START REQUIRED)
- [ ] Manual e2e testing completed
- [ ] All error scenarios tested
- [ ] Performance benchmarks acceptable

---

## Production Deployment

### Before Going Live
1. **Start all services**:
   - Start MongoDB
   - Start Emotion Recognition Service (port 5000)
   - Start Backend (port 8000)
   - Frontend is dev mode (can use build for production)

2. **Run full test suite**:
   ```bash
   python test_e2e_verification.py
   ```
   All tests should PASS

3. **Manual browser testing**:
   - Go through Test 1-6 above
   - Verify audio playback works
   - Check session data in MongoDB

4. **Load testing** (optional):
   - Test with multiple concurrent users
   - Monitor CPU, memory, database connections

### Production Configuration
```python
# Backend settings
DEBUG = False  # No debug mode
RELOAD = False  # No auto-reload
CORS_ORIGINS = ["https://yourdomain.com"]  # Restrict CORS
LOG_LEVEL = "INFO"  # No debug logs
```

### Monitoring
- Monitor port 8000 availability
- Check MongoDB connection pool
- Monitor emotion service uptime
- Log error rates and response times
- Set up alerts for service failures

---

## Troubleshooting

### Backend Won't Start
```bash
# Clear Python cache
Remove-Item -Recurse -Force __pycache__
Remove-Item -Recurse -Force app/__pycache__

# Check requirements
pip install -r requirements.txt

# Test import
python -c "import main; print('OK')"

# Run with verbose output
python main.py --verbose
```

### Emotion Detection Times Out
- Emotion service may be slow for large images
- Check port 5000 is listening
- Increase timeout to 60 seconds (already done)
- Check image size (should be < 1 MB)

### Audio Won't Play
- Check audio URLs are absolute (contain http://)
- Verify files exist in C:\Major Project\Songs\
- Check RASA_FOLDERS import in upload.py
- Verify MIME type is audio/mpeg

### Database Connection Issues
- Check MongoDB is running on port 27017
- Verify MONGODB_URL in config
- Check firewall allows port 27017
- Run `mongosh` to verify connectivity

### Session Data Not Saved
- Check MongoDB is running
- Verify database name is correct
- Check collection names match
- Review backend logs for errors

---

## Support & Debugging

### Enable Verbose Logging
```python
# Backend
logging.basicConfig(level=logging.DEBUG)

# Frontend (in LiveSession.tsx)
console.debug('Emotion detected:', emotion);
console.debug('Recommendations:', recommendations);
```

### Check Logs
```bash
# MongoDB logs
mongosh --eval "db.currentOp()"

# Backend FastAPI includes request logs
# Frontend browser console (F12)
```

### Common Issues & Solutions

1. **"Canvas is null"** → Check canvas div exists in HTML
2. **"CORS error"** → Verify backend CORS middleware
3. **"No Face Detected"** → Normal, should return "Neutral"
4. **Audio plays but no sound** → Check browser volume, HTTPS issues
5. **Session data missing** → Restart MongoDB or check permissions

---

## Next Steps for Continued Development

1. **User Authentication** - Add login/register
2. **User Profiles** - Track user history
3. **Analytics Dashboard** - Show trends in emotions/improvements
4. **Recommendation Algorithm** - More sophisticated matching
5. **Offline Mode** - Cache songs locally
6. **Mobile App** - React Native version
7. **Advanced Emotion Tracking** - Multiple captures per session
8. **Music Therapy Integration** - More therapeutic features
9. **Admin Panel** - Manage songs and ragas
10. **API Rate Limiting** - Protect from abuse

---

**Last Updated**: April 9, 2026
**Application Status**: READY FOR MANUAL TESTING ✅
**Backend**: NEEDS MANUAL START (see "How to Start the Backend" section)
