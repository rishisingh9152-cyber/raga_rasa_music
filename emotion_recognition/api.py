import os
import base64
import numpy as np
import cv2
from flask import Flask, request, jsonify
from flask_cors import CORS
from emotion_detector import EmotionDetector
import logging

app = Flask(__name__)
CORS(app)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize emotion detector (loads model on startup)
logger.info("Initializing EmotionDetector...")
try:
    detector = EmotionDetector()
    logger.info("EmotionDetector initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize EmotionDetector: {e}")
    detector = None

@app.route('/')
def home():
    return jsonify({
        "service": "Emotion Recognition API",
        "status": "running",
        "version": "1.0.0",
        "model": "HSEmotion (pretrained on AffectNet)",
        "endpoints": {
            "GET /": "Service info",
            "GET /health": "Health check",
            "POST /detect": "Detect emotion from base64 image"
        }
    })

@app.route('/health')
def health():
    return jsonify({
        "status": "ok" if detector else "error",
        "service": "emotion-recognition",
        "detector_initialized": detector is not None
    })

@app.route('/detect', methods=['POST'])
def detect():
    """Detect emotion from base64 image"""
    return _detect_emotion()

@app.route('/emotion/detect', methods=['POST'])
def emotion_detect():
    """Alias endpoint: /emotion/detect (for compatibility)"""
    return _detect_emotion()

def _detect_emotion():
    """Core emotion detection logic"""
    try:
        if not detector:
            return jsonify({"error": "Emotion detector not initialized"}), 503
        
        data = request.get_json()
        
        if not data or 'image' not in data:
            return jsonify({"error": "Missing 'image' field in request"}), 400
        
        # Decode base64 image
        image_data = data['image']
        if isinstance(image_data, str):
            # Remove data URI prefix if present (e.g., "data:image/jpeg;base64,...")
            if image_data.startswith('data:'):
                image_data = image_data.split(',')[1]
            
            try:
                image_bytes = base64.b64decode(image_data)
            except Exception as e:
                logger.error(f"Failed to decode base64: {e}")
                return jsonify({"error": "Invalid base64 image"}), 400
        else:
            image_bytes = image_data
        
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            return jsonify({"error": "Failed to decode image"}), 400
        
        # Detect emotion
        logger.info("Detecting emotion from image...")
        result = detector.detect_from_frame(frame)
        
        # Extract dominant emotion
        dominant_raw = result.get('raw_dominant', 'neutral')
        emotions = result.get('emotions', {})
        confidence = max(emotions.values()) / 100.0 if emotions else 0.0
        
        response = {
            "emotion": dominant_raw,
            "confidence": round(confidence, 3),
            "dominant": result.get('dominant', 'Neutral'),
            "raw_dominant": dominant_raw,
            "emotions": emotions,
            "is_brave": result.get('is_brave', False)
        }
        
        logger.info(f"Emotion detected: {dominant_raw} (confidence: {confidence:.3f})")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Emotion detection error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False') == 'True'
    app.run(host='0.0.0.0', port=port, debug=debug)
