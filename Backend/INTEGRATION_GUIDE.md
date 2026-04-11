# 🎵 Integration Guide: External Emotion Recognition Service + Rasa Model

This guide explains how to integrate your **external face emotion recognition service** and **rasa classification model** with the RagaRasa backend.

---

## 📋 What You Need

### 1. Face Emotion Recognition Service
- **Status**: Separate project running as a service
- **Task**: Detect emotions from images (Happy, Sad, Angry, etc.)
- **Input**: Base64 encoded JPEG image
- **Output**: Emotion label + confidence score

### 2. Rasa Classification Model
- **Format**: model.h5 (Keras) OR model.pkl (scikit-learn) OR model.joblib
- **Task**: Map emotion → Indian classical music rasa (Shringar, Shaant, Veer, Shok)
- **Input**: Emotion label
- **Output**: Rasa classification + confidence

---

## 🎯 STEP-BY-STEP SETUP

### STEP 1: Upload Your Rasa Classification Model

**Location**: `C:\Major Project\backend\models\rasa_classification\`

**Supported formats**:
- `model.h5` - Keras/TensorFlow SavedModel
- `model.pkl` - scikit-learn pickle model
- `model.joblib` - joblib format

**How to upload**:
1. Copy your model file to: `C:\Major Project\backend\models\rasa_classification\`
2. Name it one of: `model.h5`, `model.pkl`, or `model.joblib`
3. (Optional) Add `metadata.json` with model info

**Example structure**:
```
C:\Major Project\backend\models\rasa_classification\
├── model.h5                    ← Your trained model here
├── metadata.json               ← (optional) Model info
└── README.md                   ← This file
```

### STEP 2: Configure External Emotion Service

Edit `.env` file with your emotion service details:

```env
# External Emotion Recognition Service Configuration

# Set to True to use your external service
USE_EXTERNAL_EMOTION_SERVICE=True

# Your emotion service URL and port
EMOTION_SERVICE_URL=http://localhost:5000

# The API endpoint path on your service
# Examples: /predict, /emotion, /api/detect, etc.
EMOTION_SERVICE_ENDPOINT=/predict

# Minimum confidence threshold (0.0 - 1.0)
# If emotion confidence below this, will default to "Neutral"
EMOTION_CONFIDENCE_THRESHOLD=0.3

# Enable rasa classification model
USE_RASA_MODEL=True
```

### STEP 3: Customize External Service API

If your emotion service has a different API format, edit:
**File**: `C:\Major Project\backend\app\services\external_emotion.py`

**Method to customize**: `predict_emotion()`

**Example - if your service expects different request/response**:

```python
# Current (modify if different):
request_payload = {
    "image": image_base64,
    "format": "base64"
}

# If your service expects different format:
request_payload = {
    "base64_image": image_base64  # Different key name
}

# Parse response based on your format:
emotion = result.get("detected_emotion")  # If different key
confidence = result.get("probability")    # If different key
```

---

## 🔧 YOUR EMOTION SERVICE API

**Tell me the following and I'll update the integration**:

### 1. Service Details
- [ ] **URL**: `http://localhost:____` (what port?)
- [ ] **Endpoint path**: `/predict` or something else?
- [ ] **Method**: POST (or something else?)

### 2. Request Format
What does your service expect?

```python
# Example:
POST http://localhost:5000/predict

Request:
{
    "image_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
    "format": "base64"
}
```

### 3. Response Format
What does your service return?

```python
# Example:
Response:
{
    "emotion": "Happy",
    "confidence": 0.95,
    "timestamp": "2025-03-15T10:00:00Z"
}
```

---

## 🎓 RASA MODEL DETAILS

### Model Training

Your rasa model should:
1. **Input**: One-hot encoded emotion vector or emotion label
   - [1, 0, 0, 0, 0, 0, 0] → Angry
   - [0, 1, 0, 0, 0, 0, 0] → Disgusted
   - [0, 0, 1, 0, 0, 0, 0] → Fearful
   - [0, 0, 0, 1, 0, 0, 0] → Happy
   - [0, 0, 0, 0, 1, 0, 0] → Neutral
   - [0, 0, 0, 0, 0, 1, 0] → Sad
   - [0, 0, 0, 0, 0, 0, 1] → Surprised

2. **Output**: Rasa classification
   - 0 → Shringar (Romantic/Aesthetic)
   - 1 → Shaant (Peaceful/Calm)
   - 2 → Veer (Heroic/Energetic)
   - 3 → Shok (Sorrowful)

3. **Output format**: Single class index or one-hot encoded

### Supported Model Types

**Keras/TensorFlow (H5 format)**:
```python
import tensorflow as tf
model = tf.keras.models.load_model('model.h5')
prediction = model.predict(emotion_vector)
```

**scikit-learn (pickle format)**:
```python
import pickle
model = pickle.load(open('model.pkl', 'rb'))
prediction = model.predict([emotion_vector])
probabilities = model.predict_proba([emotion_vector])
```

**scikit-learn (joblib format)**:
```python
import joblib
model = joblib.load('model.joblib')
prediction = model.predict([emotion_vector])
```

---

## 📊 DATA FLOW

```
Frontend
  ↓
POST /detect-emotion {image_base64, session_id}
  ↓
Backend (C:\Major Project\backend)
  ├─ Call External Emotion Service
  │  └─ POST http://your-service:port/endpoint {image}
  │     ↓
  │  Your Emotion Service (separate project)
  │     ↓
  │  Returns: {emotion, confidence}
  │
  ├─ Load Rasa Model (model.h5/pkl)
  │  └─ Predict: emotion → rasa
  │     ↓
  │  Rasa Classification Model
  │     ↓
  │  Returns: {rasa, confidence}
  │
  ├─ Store in MongoDB
  └─ Return to Frontend: {emotion}
```

---

## ✅ CHECKLIST

### Before Starting Backend

- [ ] Upload rasa model to: `C:\Major Project\backend\models\rasa_classification\`
  - [ ] Named as: `model.h5` or `model.pkl` or `model.joblib`
  - [ ] Supports emotion → rasa mapping

- [ ] Configure `.env` file
  - [ ] Set `EMOTION_SERVICE_URL` = your service URL
  - [ ] Set `EMOTION_SERVICE_ENDPOINT` = your endpoint path
  - [ ] Set `USE_EXTERNAL_EMOTION_SERVICE=True`
  - [ ] Set `USE_RASA_MODEL=True`

- [ ] (Optional) Customize `external_emotion.py`
  - [ ] If your service uses different request/response format
  - [ ] Update `predict_emotion()` method

### On Startup

1. Backend will try to load rasa model from models directory
2. Backend will ping your emotion service for health check
3. If either fails, you'll see warnings in logs but system continues
4. (Fallback mappings available if models unavailable)

---

## 🚀 QUICK START

### 1. Upload Model

```bash
# Copy your model to:
C:\Major Project\backend\models\rasa_classification\model.h5
# or
C:\Major Project\backend\models\rasa_classification\model.pkl
```

### 2. Update .env

```bash
cd C:\Major Project\backend
```

Edit `.env`:
```env
USE_EXTERNAL_EMOTION_SERVICE=True
EMOTION_SERVICE_URL=http://localhost:5000
EMOTION_SERVICE_ENDPOINT=/predict
USE_RASA_MODEL=True
```

### 3. Start Your Emotion Service

```bash
# In separate terminal, start your emotion recognition service
# Example (adjust for your project):
cd /path/to/your/emotion/project
python app.py  # or however you start it
# Should be running on http://localhost:5000
```

### 4. Start Backend

```bash
cd C:\Major Project\backend
docker-compose up
```

### 5. Verify Services

```bash
# Check emotion service health
curl http://localhost:5000/health

# Check backend
curl http://localhost:8000/health

# Check emotion service integration
curl http://localhost:8000/emotion-service/health
```

### 6. Start Frontend

```bash
cd "C:\Major Project\raga-rasa-soul-main"
npm run dev
```

---

## 🧪 TESTING

### Test Emotion Detection with Real Image

```bash
# 1. Get a base64 encoded image
# You can use an online tool or Python:

python << 'EOF'
import base64
with open('test_image.jpg', 'rb') as f:
    image_base64 = base64.b64encode(f.read()).decode('utf-8')
    print(f"data:image/jpeg;base64,{image_base64}")
EOF

# 2. Test the endpoint
curl -X POST http://localhost:8000/detect-emotion \
  -H "Content-Type: application/json" \
  -d '{
    "image_base64": "data:image/jpeg;base64,YOUR_BASE64_HERE",
    "session_id": "test-session-123"
  }'
```

### View Logs

```bash
# Backend logs
docker-compose logs -f backend

# Your emotion service logs
# (Check your project's logging)
```

---

## 🔍 TROUBLESHOOTING

### Backend Can't Connect to Emotion Service

**Error**: `Connection refused` or `Connection timeout`

**Solution**:
1. Check if your emotion service is running
2. Verify the port in `.env` matches your service
3. Check firewall isn't blocking the port
4. Test manually: `curl http://localhost:YOUR_PORT/`

### Rasa Model Not Loading

**Error**: `No rasa model found in C:\Major Project\backend\models\rasa_classification`

**Solution**:
1. Upload your model file to that directory
2. Name it exactly as: `model.h5`, `model.pkl`, or `model.joblib`
3. Restart backend: `docker-compose restart backend`

### Model Has Different Input Format

**Error**: `Rasa prediction failed` or wrong outputs

**Solution**:
1. Check your model's expected input format
2. Edit `app/services/rasa_model.py`
3. Update `_emotion_to_vector()` method
4. Modify the prediction logic in `predict_rasa()`

### External Service Returns Different Format

**Error**: `KeyError` on response parsing

**Solution**:
1. Check your service's actual response format
2. Edit `app/services/external_emotion.py`
3. Update the response parsing in `predict_emotion()`:
   ```python
   emotion = result.get("your_emotion_key")
   confidence = result.get("your_confidence_key")
   ```

---

## 📝 LOGS & DEBUGGING

### Enable Debug Logging

Edit `.env`:
```env
DEBUG=True
```

### View Backend Logs

```bash
docker-compose logs -f backend

# Look for lines like:
# "Emotion detected: Happy (confidence: 0.95)"
# "Rasa prediction: Shringar"
```

---

## 🎯 WHAT HAPPENS AFTER EMOTION DETECTION

### Flow in Backend

```
1. Receive base64 image from frontend
   ↓
2. Call external emotion service
   ↓
3. Get emotion + confidence
   ↓
4. Load rasa model
   ↓
5. Predict rasa for emotion
   ↓
6. Store both in MongoDB:
   {
     emotion: "Happy",
     rasa: "Shringar",
     emotion_confidence: 0.95,
     rasa_confidence: 0.89
   }
   ↓
7. Return emotion to frontend
   ↓
8. Frontend uses emotion for recommendations
```

### Recommendation Flow

```
emotion = "Happy"
  ↓
rasa = "Shringar" (from model)
  ↓
Filter songs by rasa="Shringar"
  ↓
Score songs using:
  • Cognitive metrics (memory, reaction, accuracy)
  • User preferences (past ratings)
  • Freshness (newer songs)
  ↓
Return top 5 recommended songs
```

---

## 📞 NEXT STEPS

### To Complete Integration

1. **Tell me** (reply with):
   - [ ] File path to your emotion recognition project
   - [ ] Port your emotion service runs on
   - [ ] Exact API endpoint path
   - [ ] Example request/response format

2. **Upload**:
   - [ ] Your rasa classification model (model.h5 or model.pkl)
   - [ ] Location: `C:\Major Project\backend\models\rasa_classification\`

3. **I'll**:
   - [ ] Create custom integration code if needed
   - [ ] Update configuration
   - [ ] Test and verify everything works

---

## 🔗 REFERENCE

### Files to Modify

- `.env` - Configuration (emotion service URL, model paths)
- `app/services/external_emotion.py` - Emotion service client (if API format different)
- `app/services/rasa_model.py` - Rasa model loader (if model format different)
- `app/routes/emotion.py` - Main emotion detection endpoint

### Model Directory

```
C:\Major Project\backend\models\rasa_classification\
├── model.h5 or model.pkl    ← Upload here
├── metadata.json            ← (optional)
└── README.md
```

### Configuration Variables

```env
# Emotion Service
EMOTION_SERVICE_URL=http://localhost:5000
EMOTION_SERVICE_ENDPOINT=/predict
EMOTION_CONFIDENCE_THRESHOLD=0.3

# Rasa Model
RASA_MODEL_PATH=./models/rasa_classification/
USE_RASA_MODEL=True
```

---

**Ready to integrate?**

**Next: Provide your emotion service details and upload the rasa model! 🚀**
