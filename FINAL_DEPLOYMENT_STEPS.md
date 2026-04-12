# RagaRasa Production Deployment - Final Steps

## Issue Identified
The Render backend is deployed but returns 0 recommendations because the MongoDB environment variable is not set correctly.

## Solution: Set Environment Variables on Render Dashboard

1. **Go to Render Dashboard**
   - Navigate to https://dashboard.render.com
   - Select your `raga-rasa-backend` service

2. **Go to Settings → Environment**

3. **Add These Variables** (if not already present):
   ```
   MONGODB_URL=mongodb+srv://Rishi123:Rishi_123@majorproject.lpwzhzc.mongodb.net/?appName=MajorProject
   DATABASE_NAME=raga_rasa
   PYTHON_VERSION=3.10.15
   PYTHONPATH=.
   ```

4. **Save Changes** - The service will auto-redeploy

5. **Wait for deployment to complete** (check the logs)

## Verify the Fix

Once the environment variables are set and the service redeployed:

```bash
# Test if recommendations now work
curl -X POST https://raga-rasa-backend.onrender.com/api/recommend/live \
  -H "Content-Type: application/json" \
  -d '{
    "emotion": "happy",
    "session_id": "test-123",
    "cognitive_data": {
      "memory_score": 4,
      "reaction_time": 250,
      "accuracy_score": 85
    }
  }'
```

You should get a response with 5 song recommendations.

## Frontend Configuration

The frontend is already configured correctly:
- `.env` file has: `VITE_API_BASE_URL=https://raga-rasa-backend.onrender.com/api`
- API service calls the correct endpoints

## Database Status

✓ MongoDB has been seeded with 19 songs (4 ragas)
- 8 Shaant songs
- 5 Shok songs  
- 3 Shringar songs
- 3 Veer songs

All songs have Cloudinary streaming URLs configured.

## Next Steps

1. Set MONGODB_URL on Render
2. Wait for redeploy
3. Test recommendations endpoint
4. Test frontend with deployed backend
5. Test emotion recognition service if needed
