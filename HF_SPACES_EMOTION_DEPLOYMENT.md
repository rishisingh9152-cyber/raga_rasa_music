# HUGGING FACE SPACES EMOTION DEPLOYMENT GUIDE

## Overview

This guide walks through deploying the Emotion Recognition Service to Hugging Face Spaces.

**Estimated Deployment Time**: 10 minutes
**Cost Estimate**: Free tier (with GPU support available)

---

## Prerequisites

Before starting:

1. **Hugging Face Account**
   - Sign up at https://huggingface.co
   - Free tier with GPU options

2. **Emotion Service Files**
   - `emotion_recognition/api.py`
   - `emotion_recognition/emotion_detector.py`
   - `emotion_recognition/requirements.txt`

3. **Git Installed**
   - For pushing to HF Spaces repository

---

## Step 1: Create Hugging Face Space

### 1.1 Create New Space
```bash
# Go to https://huggingface.co/spaces

# Click "Create new Space"
# Fill in:
# - Space name: raga-rasa-emotion
# - License: MIT
# - Space SDK: Docker
# - Visibility: Public
# - Create Space
```

### 1.2 Get Space Repository URL
```bash
# Space URL:
# https://huggingface.co/spaces/rishi22652/emotion_recognition

# Clone the space repo
git clone https://huggingface.co/spaces/rishi22652/emotion_recognition
cd emotion_recognition
```

---

## Step 2: Prepare Emotion Service Files

### 2.1 Copy Files to Space Directory
```bash
# Copy from main project
cp ../emotion_recognition/api.py ./
cp ../emotion_recognition/emotion_detector.py ./
cp ../emotion_recognition/requirements.txt ./

# Or create them directly in space directory
```

### 2.2 Update api.py for HF Spaces

```python
# emotion_recognition/api.py
import os
import base64
import json
from io import BytesIO

import cv2
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS

# Import emotion detector
from emotion_detector import EmotionDetector

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Initialize emotion detector
detector = EmotionDetector()

# Get port from HF Spaces environment
PORT = int(os.getenv("PORT", "7860"))
DEBUG = os.getenv("DEBUG", "false").lower() == "true"


@app.route("/", methods=["GET"])
def home():
    """Health check and info endpoint"""
    return jsonify({
        "service": "raga-rasa-emotion",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "/health": "Health check",
            "/detect": "Detect emotion from image",
            "/detect/batch": "Detect emotions from multiple images"
        }
    }), 200


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "emotion-detection",
        "model": "fer2013",
    }), 200


@app.route("/detect", methods=["POST"])
def detect_emotion():
    """
    Detect emotion from base64 image.
    
    Expected JSON:
    {
        "image": "base64_encoded_image"
    }
    
    Returns:
    {
        "emotion": "happy",
        "confidence": 0.95,
        "emotions": {
            "angry": 0.01,
            "disgust": 0.02,
            "fear": 0.01,
            "happy": 0.95,
            "sad": 0.01,
            "surprise": 0.00,
            "neutral": 0.00
        }
    }
    """
    try:
        data = request.get_json()
        if not data or "image" not in data:
            return jsonify({"error": "Missing image field"}), 400
        
        # Decode base64 image
        image_data = base64.b64decode(data["image"])
        nparr = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            return jsonify({"error": "Invalid image data"}), 400
        
        # Detect emotion
        result = detector.detect(image)
        
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({
            "error": str(e),
            "message": "Error detecting emotion"
        }), 500


@app.route("/detect/batch", methods=["POST"])
def detect_emotions_batch():
    """
    Detect emotions from multiple base64 images.
    
    Expected JSON:
    {
        "images": [
            "base64_image_1",
            "base64_image_2"
        ]
    }
    
    Returns:
    {
        "results": [
            {"emotion": "happy", "confidence": 0.95, ...},
            {"emotion": "sad", "confidence": 0.87, ...}
        ]
    }
    """
    try:
        data = request.get_json()
        if not data or "images" not in data:
            return jsonify({"error": "Missing images field"}), 400
        
        results = []
        for image_data_b64 in data["images"]:
            try:
                # Decode base64 image
                image_data = base64.b64decode(image_data_b64)
                nparr = np.frombuffer(image_data, np.uint8)
                image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                if image is not None:
                    result = detector.detect(image)
                    results.append(result)
                else:
                    results.append({"error": "Invalid image"})
            except Exception as e:
                results.append({"error": str(e)})
        
        return jsonify({"results": results}), 200
    
    except Exception as e:
        return jsonify({
            "error": str(e),
            "message": "Error processing batch"
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=DEBUG)
```

### 2.3 Update requirements.txt

```
# emotion_recognition/requirements.txt
flask==2.3.3
flask-cors==4.0.0
opencv-python==4.8.0.76
numpy==1.24.3
pillow==10.0.0
fer==25.10.3
tensorflow==2.13.0
scikit-learn==1.3.0
gunicorn==21.2.0
```

---

## Step 3: Create Dockerfile for HF Spaces

### 3.1 Create Dockerfile
```dockerfile
# Dockerfile for HF Spaces
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for OpenCV
RUN apt-get update && apt-get install -y \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY api.py .
COPY emotion_detector.py .

# Set environment variables
ENV PORT=7860
ENV FLASK_APP=api.py
ENV PYTHONUNBUFFERED=1

# Expose port (HF Spaces uses 7860)
EXPOSE 7860

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:7860/health || exit 1

# Run application
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "--workers", "1", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "api:app"]
```

### 3.2 Verify Dockerfile Syntax
```bash
# HF Spaces will use dockerfile_path if specified
# Default is ./Dockerfile
```

---

## Step 4: Configure Space Settings

### 4.1 Create app_config.yaml (Optional)
```yaml
# app_config.yaml (optional for advanced config)
title: "RagaRasa Emotion Recognition"
description: "AI-powered emotion detection from facial images"
sdk: docker
docker:
  dockerfile: ./Dockerfile
  port: 7860
  resources:
    - gpu
persistent_storage_path: /data
```

### 4.2 Create README.md
```markdown
# RagaRasa Emotion Recognition Service

Emotion detection API using deep learning (FER2013 + TensorFlow).

## Endpoints

- `GET /` - Service info
- `GET /health` - Health check
- `POST /detect` - Detect emotion from base64 image
- `POST /detect/batch` - Batch emotion detection

## Usage

```python
import requests
import base64

# Read image
with open("photo.jpg", "rb") as f:
    image_b64 = base64.b64encode(f.read()).decode()

# Call API
response = requests.post(
    "https://your-space-url/detect",
    json={"image": image_b64}
)

print(response.json())
# {
#     "emotion": "happy",
#     "confidence": 0.95,
#     "emotions": {...}
# }
```

## Emotions Detected

- angry
- disgust
- fear
- happy
- neutral
- sad
- surprise

## Performance

- Model: FER2013 trained on 35,887 images
- Accuracy: ~65% on test set
- Inference Time: 50-100ms per image
```

---

## Step 5: Push to Hugging Face Spaces

### 5.1 Configure Git
```bash
# In the space directory
git config user.email "your-email@example.com"
git config user.name "Your Name"

# Add HF credentials (if needed)
git lfs install
```

### 5.2 Push Files
```bash
# Add all files
git add .

# Commit
git commit -m "Deploy emotion service: FER2013 model with Flask API"

# Push to HF Spaces
# Replace YOUR_USERNAME with your HF username
git push origin main
```

### 5.3 Monitor Build
```bash
# HF Spaces will automatically:
# 1. Detect Dockerfile
# 2. Build Docker image
# 3. Deploy to servers
# 4. Allocate GPU (if requested)

# Watch progress in HF Spaces dashboard
# Build typically takes 5-10 minutes
```

---

## Step 6: Configure GPU (Optional)

### 6.1 Request GPU Resources
In HF Spaces Settings:

```
1. Go to Space Settings
2. Under "Hardware", select:
   - T4 (Recommended for this service)
   - A10G (Higher performance)
   - H100 (Max performance)
3. Save and rebuild
```

### 6.2 Update Requirements for GPU
```bash
# For GPU acceleration, use GPU-optimized packages
# requirements.txt additions:
tensorflow-gpu==2.13.0  # Instead of tensorflow
torch==2.0.0+cu118     # For GPU support
```

---

## Step 7: Verify Deployment

### 7.1 Get Space URL
```bash
# After successful build:
# https://huggingface.co/spaces/rishi22652/emotion_recognition

# Direct API URL:
# https://rishi22652-emotion-recognition.hf.space
```

### 7.2 Test Health Endpoint
```bash
curl https://rishi22652-emotion-recognition.hf.space/health

# Expected response:
# {
#   "status": "healthy",
#   "service": "emotion-detection",
#   "model": "fer2013"
# }
```

### 7.3 Test Emotion Detection
```bash
# Create test image and convert to base64
python3 << 'EOF'
import base64
import requests

# Read and encode image
with open("test_image.jpg", "rb") as f:
    image_b64 = base64.b64encode(f.read()).decode()

# Call API
response = requests.post(
    "https://rishi22652-emotion-recognition.hf.space/detect",
    json={"image": image_b64}
)

print(response.json())
EOF
```

---

## Step 8: Update Backend Configuration

### 8.1 Update Backend Environment
```bash
# In Backend deployment (GCP/Render), update:
EMOTION_SERVICE_URL=https://rishi22652-emotion-recognition.hf.space
USE_EXTERNAL_EMOTION_SERVICE=true
EMOTION_SERVICE_ENDPOINT=/detect
```

### 8.2 Restart Backend Service
```bash
# For Google Cloud Run
gcloud run services update raga-rasa-backend \
  --region=us-central1 \
  --update-env-vars=\
"EMOTION_SERVICE_URL=https://rishi22652-emotion-recognition.hf.space"
```

---

## Step 9: Monitoring and Logging

### 9.1 View Logs
In HF Spaces Dashboard:
```
1. Go to your space
2. Click "Logs" tab
3. View build and runtime logs
```

### 9.2 Monitor Performance
```bash
# Check space statistics
# - Number of requests
# - GPU usage
# - Build status
# - Storage usage
```

---

## Step 10: Production Checklist

Before integrating with production backend:

- [ ] Service deployed to HF Spaces
- [ ] Health check endpoint responding
- [ ] Emotion detection working
- [ ] Batch detection functional
- [ ] CORS headers correct
- [ ] Error handling in place
- [ ] Logs accessible
- [ ] Monitoring active
- [ ] Backend environment variables updated
- [ ] Full integration tested

---

## Common Issues and Solutions

### Issue: Build Fails with Module Not Found
```
ModuleNotFoundError: No module named 'tensorflow'
```

**Solution**:
1. Check requirements.txt spelling
2. Ensure all dependencies listed
3. Run locally to test:
```bash
pip install -r requirements.txt
```

### Issue: Space Crashes After Startup
**Solution**:
1. Check logs in HF Spaces dashboard
2. Verify PORT=7860 is set
3. Test locally:
```bash
gunicorn --bind 0.0.0.0:7860 api:app
```

### Issue: Model Download Times Out
**Solution**:
1. Pre-download models in Dockerfile:
```dockerfile
RUN python -m nltk.downloader punkt
```
2. Or use local model paths

### Issue: GPU Memory Exceeded
**Solution**:
1. Reduce model batch size
2. Upgrade GPU tier (T4 → A10G)
3. Implement memory optimization

### Issue: Slow API Response
**Solution**:
1. Enable GPU acceleration
2. Cache model in memory
3. Implement request batching
4. Add response caching

---

## Cost Analysis

### HF Spaces Free Tier
- **CPU**: Free, shared CPU
- **Storage**: 50GB
- **Bandwidth**: Unlimited
- **Cost**: $0/month

### HF Spaces Paid Tiers
- **T4 GPU**: $4.50/month (recommended)
- **A10G GPU**: $15/month
- **A100 GPU**: $60/month

**Recommended**: T4 for balanced cost/performance

---

## Advanced Configuration

### 10.1 Custom Model
```python
# Load custom model instead of FER2013
from tensorflow.keras.models import load_model

# In emotion_detector.py:
class EmotionDetector:
    def __init__(self, model_path="model.h5"):
        self.model = load_model(model_path)
```

### 10.2 Caching Results
```python
from functools import lru_cache

class EmotionDetector:
    @lru_cache(maxsize=1000)
    def detect(self, image_hash):
        # Cache results based on image hash
        pass
```

### 10.3 Rate Limiting
```python
from flask_limiter import Limiter

limiter = Limiter(
    app=app,
    key_func=lambda: request.remote_addr
)

@app.route("/detect", methods=["POST"])
@limiter.limit("10/minute")
def detect_emotion():
    # Rate limited to 10 requests per minute
    pass
```

---

## Next Steps

1. Monitor emotion detection accuracy in production
2. Collect feedback on emotion predictions
3. Fine-tune model with real-world data
4. Implement caching for frequently processed images
5. Add support for real-time video emotion detection

---

## Useful Links

- HF Spaces Docs: https://huggingface.co/docs/hub/spaces
- FER2013 Dataset: https://www.kaggle.com/datasets/msambare/fer2013
- TensorFlow Docs: https://www.tensorflow.org/guide
- Flask Docs: https://flask.palletsprojects.com

**Last Updated**: April 2026
**Version**: 1.0
