# Model Storage Directory Structure

Please upload your model files here:

## Directory Structure Created:

```
C:\Major Project\backend\models\
├── emotion_recognition/
│   └── [Your external emotion service files here]
└── rasa_classification/
    ├── model.h5              ← Upload your Keras/TensorFlow model here
    ├── model.pkl             ← OR upload your pickle model here
    ├── metadata.json         ← Model metadata (optional)
    └── README.md             ← Model documentation
```

## How to Upload Models:

### 1. Rasa Classification Model

**Upload location:** `C:\Major Project\backend\models\rasa_classification\`

**Supported formats:**
- `model.h5` - Keras/TensorFlow SavedModel format
- `model.pkl` - scikit-learn or pickle format
- `model.joblib` - joblib format

**Steps:**
1. Copy your rasa classification model file to: 
   `C:\Major Project\backend\models\rasa_classification\`
2. Name it as `model.h5`, `model.pkl`, or `model.joblib`
3. (Optional) Create `metadata.json` with model info

### 2. Emotion Recognition Service

**For your external emotion recognition project:**

1. **If it's running on a different port:** Update `.env` with:
   ```
   EMOTION_SERVICE_URL=http://localhost:[your_port]
   EMOTION_SERVICE_ENDPOINT=/path/to/emotion/endpoint
   ```

2. **If you want to include it in this backend:** 
   - Provide the file path and we'll integrate it

## Next Steps:

1. **Tell me:**
   - File path to your emotion recognition project
   - Port it runs on (or if it should run on same backend)
   - API endpoint path (e.g., `/predict`, `/emotion`, etc.)
   - Input/output format of your emotion service

2. **Upload:**
   - Rasa classification model (model.h5 or model.pkl)
   - Any model metadata files needed

3. **I'll:**
   - Create model loaders for your rasa model
   - Set up service integration for emotion recognition
   - Update configuration and documentation
   - Test the integration

---

**Model directories are ready!**

Next: Provide the details and file paths.
