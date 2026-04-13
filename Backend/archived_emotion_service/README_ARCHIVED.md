# Archived Emotion Recognition Service

## ⚠️ This Folder is Archived - DO NOT USE FOR DEPLOYMENT

The emotion recognition functionality has been **integrated directly into the FastAPI backend** as of recent updates.

### What Was Here
This folder originally contained a separate Flask microservice for emotion detection:
- Used HSEmotion model (pretrained on AffectNet)
- Ran as a separate service on Hugging Face Spaces or Render
- Backend called this service via HTTP

### Why It's Now Archived
✅ **Emotion detection is now integrated into the backend**
- HSEmotion model loaded directly in `Backend/app/services/emotion.py`
- Endpoint: `POST /api/detect-emotion` (in main backend)
- No separate service needed
- Faster (no inter-service network calls)
- Simpler deployment (1 service instead of 2)

### What to Do
1. **Do NOT deploy this folder** - It's kept for reference only
2. **Use the integrated backend** - Deploy `Backend/` instead
3. **Delete this folder** - Optional cleanup (can keep for reference)

### If You Need Reference
Look at:
- `Backend/app/services/emotion.py` - Current integrated implementation
- `emotion_detector.py` - Original HSEmotion model code (for reference)

### Key Files in This Archive
- `emotion_detector.py` - HSEmotion model wrapper (now in Backend/app/services/)
- `api.py` - Original Flask API (no longer needed)
- `requirements.txt` - Original dependencies (merged into Backend/requirements.txt)
- `Dockerfile` - Original container (no longer needed)

---

**Status**: Archived (kept for historical reference)
**Last Updated**: April 13, 2026
**Integration Date**: April 13, 2026

See: `INTEGRATED_EMOTION_SERVICE.md` for details on the integration.
