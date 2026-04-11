"""
emotion_detector.py
--------------------
Uses HSEmotion — pretrained on AffectNet.
Detects: Happy, Neutral, Sad, Angry, Bravery (derived)
"""

import cv2
import numpy as np
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

from hsemotion.facial_emotions import HSEmotionRecognizer
import warnings
warnings.filterwarnings("ignore")

BRAVERY_THRESHOLD = 50

# HSEmotion class order
HS_CLASSES = ['Anger', 'Contempt', 'Disgust', 'Fear', 'Happiness', 'Neutral', 'Sadness', 'Surprise']

EMOTION_LABELS = {
    "happy":   "Happy 😊",
    "neutral": "Neutral 😐",
    "sad":     "Sad 😢",
    "angry":   "Angry 😠",
    "bravery": "Bravery 💪",
}

# Sensitivity multipliers
SENSITIVITY = {
    "happy": 1.8,
    "sad":   1.0,
    "angry": 1.0,
    "fear":  1.0,
}


class EmotionDetector:
    def __init__(self):
        print("[Loading] Downloading/loading pretrained model (first run may take a moment)...")

        self.recognizer = HSEmotionRecognizer(
            model_name='enet_b0_8_best_afew',
            device='cpu'
        )

        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        self.face_cascade_alt = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_alt2.xml"
        )

        print("[Ready] Model loaded successfully!\n")

    def detect_from_frame(self, frame: np.ndarray) -> dict:
        empty = {
            "emotions": {
                "happy": 0.0,
                "neutral": 0.0,
                "sad": 0.0,
                "angry": 0.0,
                "bravery": 0.0
            },
            "dominant": "No Face Detected",
            "raw_dominant": None,
            "is_brave": None,
            "face_box": None,
        }

        face_box = self._detect_face(frame)
        if face_box is None:
            return empty

        x, y, w, h = face_box

        # Crop face with padding
        pad = int(0.15 * min(w, h))
        x1 = max(0, x - pad)
        y1 = max(0, y - pad)
        x2 = min(frame.shape[1], x + w + pad)
        y2 = min(frame.shape[0], y + h + pad)
        face_crop = frame[y1:y2, x1:x2]

        if face_crop.size == 0:
            return empty

        try:
            emotion_label, scores = self.recognizer.predict_emotions(face_crop, logits=False)
            raw = {HS_CLASSES[i].lower(): float(scores[i]) for i in range(len(HS_CLASSES))}
        except Exception as e:
            print(f"[Predict error] {e}")
            return empty

        # Extract scores
        happy   = raw.get("happiness", 0.0) * 100
        sad     = raw.get("sadness",   0.0) * 100
        angry   = raw.get("anger",     0.0) * 100
        neutral = raw.get("neutral",   0.0) * 100
        fear    = raw.get("fear",      0.0) * 100

        # Apply sensitivity
        happy = happy * SENSITIVITY["happy"]
        sad   = sad   * SENSITIVITY["sad"]
        angry = angry * SENSITIVITY["angry"]

        # Normalize INCLUDING neutral
        base = happy + sad + angry + neutral or 1.0

        happy   = round(happy   / base * 100, 1)
        sad     = round(sad     / base * 100, 1)
        angry   = round(angry   / base * 100, 1)
        neutral = round(neutral / base * 100, 1)

        # Improved bravery calculation (more stable)
        bravery = 0.6 * happy + 0.4 * neutral - 0.7 * fear
        bravery = round(max(0.0, min(100.0, bravery)), 1)

        emotions = {
            "happy": happy,
            "neutral": neutral,
            "sad": sad,
            "angry": angry,
            "bravery": bravery
        }

        # Determine dominant emotion
        dominant_raw = max(
            ["happy", "neutral", "sad", "angry"],
            key=lambda k: emotions[k]
        )

        # Stabilize neutral detection
        if neutral > 50:
            dominant_raw = "neutral"

        return {
            "emotions": emotions,
            "dominant": EMOTION_LABELS[dominant_raw],
            "raw_dominant": dominant_raw,
            "is_brave": bravery >= BRAVERY_THRESHOLD,
            "face_box": (x1, y1, x2 - x1, y2 - y1),
        }

    def _detect_face(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)

        for cascade in [self.face_cascade, self.face_cascade_alt]:
            faces = cascade.detectMultiScale(
                gray,
                scaleFactor=1.05,
                minNeighbors=4,
                minSize=(50, 50),
                flags=cv2.CASCADE_SCALE_IMAGE
            )
            if len(faces) > 0:
                return tuple(max(faces, key=lambda f: f[2] * f[3]))

        return None
