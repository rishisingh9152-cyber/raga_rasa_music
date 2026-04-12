# Music Player Analysis & Integration Issues

## Current Architecture

### AudioPlayer Component (`src/components/AudioPlayer.tsx`)
- **Status**: ✅ Well-designed
- **Features**: Play/Pause, Volume control, Progress bar, Skip buttons, Rating
- **Issues**: None - component is solid

### MusicPlayer Page (`src/pages/MusicPlayer.tsx`)
- **Status**: ⚠️ Multiple integration issues
- **Current Behavior**: Fetches songs from `/api/songs/by-rasa`
- **Issues Identified**:

#### 1. **CRITICAL: Wrong API Base URL**
   - Line 49: `const response = await fetch("/api/songs/by-rasa");`
   - **Problem**: Uses relative path, assumes backend on localhost
   - **Fix**: Should use `${API_BASE_URL}/songs/by-rasa`
   - **Current Deployment**: Backend is at `https://raga-rasa-backend.onrender.com/api`

#### 2. **Song Interface Mismatch**
   - Line 6-12: Defines Song interface with `_id`, `filename`, `duration`
   - **Problem**: MongoDB schema has `song_id`, not `_id` - though MongoDB auto-generates `_id`
   - **Actual DB Schema**:
     ```javascript
     {
       _id: ObjectId,           // MongoDB auto-generated
       song_id: string,         // Our UUID
       title: string,
       audio_url: string,       // Cloudinary URL ✅
       rasa: string,
       artist: string,
       confidence: number,
       duration: number,        // in seconds, not string
       ...
     }
     ```
   - **Fix**: Update interface to match actual DB

#### 3. **Rating Endpoint Issues**
   - Line 180: `const response = await fetch("/api/rate-song", {`
   - **Problems**:
     - Uses relative path (localhost assumption)
     - Backend has `/api/rate` endpoint (different path)
     - Doesn't include session_id
   
#### 4. **Missing API Integration Layer**
   - Song fetching logic inline in component
   - No error handling for failed playback
   - No integration with emotion-based recommendations
   - Should use `src/services/api.ts` service layer

#### 5. **Audio URL Handling**
   - Line 102-104: Sets `audio.src = currentSong.audio_url`
   - **Current**: Should work with Cloudinary URLs now ✅
   - **But**: No CORS headers configuration

#### 6. **No Skip/Previous Song Confirmation**
   - Lines 161-173: `navigate()` function
   - **Issue**: Should verify Cloudinary URLs are accessible before switching
   - **Current**: Will silently fail if URL is inaccessible

## Issues to Fix (Priority Order)

### 🔴 CRITICAL
1. ✅ API Base URL - use production Render URL
2. ✅ Song interface - match MongoDB schema
3. ✅ Rating endpoint - use correct path
4. ✅ Error handling for Cloudinary playback

### 🟡 IMPORTANT  
5. ✅ Integrate with recommendations from LiveSession
6. ✅ Verify skip/next functionality works with 59 songs
7. ✅ Audio file loading detection

### 🟢 NICE-TO-HAVE
8. Add song analytics tracking
9. Persist playback position
10. Create song queue management

## Solution Plan

### Step 1: Update API Service Layer (`src/services/api.ts`)
- Add function to fetch songs by rasa
- Add function to submit song rating
- Ensure all endpoints use production URLs

### Step 2: Update Song Interface
- Match MongoDB schema exactly
- Handle both `_id` and `song_id`

### Step 3: Refactor MusicPlayer Component
- Use API service layer instead of direct fetch
- Add proper error handling
- Integrate with SessionContext for recommendations

### Step 4: Update AudioPlayer Integration
- Ensure skip/previous works with full song list
- Add audio loading error detection
- Verify Cloudinary URL accessibility

### Step 5: Testing
- Test with all 59 songs
- Test skip/previous across rasas
- Test rating submission
- Test emotion-based recommendations

## Current Music Database

**Total Songs**: 59
- Shaant (Peaceful): 32 songs ✅
- Shok (Melancholic): 18 songs ✅
- Shringar (Romantic): 3 songs ✅
- Veer (Courageous): 6 songs ✅

**All songs have**:
- ✅ Cloudinary URLs (real streaming links)
- ✅ Proper rasa classification
- ✅ Metadata in MongoDB

## Backend API Ready

| Endpoint | Method | Status |
|----------|--------|--------|
| `/api/songs/by-rasa` | GET | ✅ Needs verification |
| `/api/rate` | POST | ✅ Needs URL update |
| `/api/recommend/live` | POST | ✅ For emotion-based |

---

**Next**: Implement fixes in order of priority
