"""In-process emotion recognition module adapted from local project code."""

import base64
import ssl
import warnings
from typing import Any, Dict, Optional, Tuple

import cv2
import numpy as np
from hsemotion.facial_emotions import HSEmotionRecognizer

ssl._create_default_https_context = ssl._create_unverified_context
warnings.filterwarnings("ignore")

BRAVERY_THRESHOLD = 50
HS_CLASSES = [
    "Anger",
    "Contempt",
    "Disgust",
    "Fear",
    "Happiness",
    "Neutral",
    "Sadness",
    "Surprise",
]


class EmotionRecognitionLocal:
    def __init__(self):
        self.recognizer = HSEmotionRecognizer(model_name="enet_b0_8_best_afew", device="cpu")
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        self.face_cascade_alt = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_alt2.xml"
        )

    def detect_from_base64(self, image_base64: str) -> Tuple[str, float, Dict[str, Any]]:
        if image_base64.startswith("data:"):
            image_base64 = image_base64.split(",", 1)[1]

        image_bytes = base64.b64decode(image_base64)
        nparr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if frame is None:
            return "neutral", 0.5, {"raw_dominant": "neutral", "emotions": {"neutral": 50.0}}

        result = self.detect_from_frame(frame)
        dominant_raw = result.get("raw_dominant") or "neutral"
        emotions = result.get("emotions") or {}
        confidence = float(emotions.get(dominant_raw, 50.0))
        if confidence > 1.0:
            confidence = confidence / 100.0
        return str(dominant_raw), confidence, result

    def detect_from_frame(self, frame: np.ndarray) -> Dict[str, Any]:
        empty = {
            "emotions": {"happy": 0.0, "neutral": 0.0, "sad": 0.0, "angry": 0.0, "bravery": 0.0},
            "dominant": "No Face Detected",
            "raw_dominant": None,
            "is_brave": None,
            "face_box": None,
        }

        face_box = self._detect_face(frame)
        if face_box is None:
            return empty

        x, y, w, h = face_box
        pad = int(0.15 * min(w, h))
        x1 = max(0, x - pad)
        y1 = max(0, y - pad)
        x2 = min(frame.shape[1], x + w + pad)
        y2 = min(frame.shape[0], y + h + pad)
        face_crop = frame[y1:y2, x1:x2]
        if face_crop.size == 0:
            return empty

        try:
            _, scores = self.recognizer.predict_emotions(face_crop, logits=False)
            raw = {HS_CLASSES[i].lower(): float(scores[i]) for i in range(len(HS_CLASSES))}
        except Exception:
            return empty

        happy = raw.get("happiness", 0.0) * 100 * 1.8
        sad = raw.get("sadness", 0.0) * 100
        angry = raw.get("anger", 0.0) * 100
        neutral = raw.get("neutral", 0.0) * 100
        fear = raw.get("fear", 0.0) * 100

        base = happy + sad + angry + neutral or 1.0
        happy = round(happy / base * 100, 1)
        sad = round(sad / base * 100, 1)
        angry = round(angry / base * 100, 1)
        neutral = round(neutral / base * 100, 1)
        bravery = round(max(0.0, min(100.0, 0.6 * happy + 0.4 * neutral - 0.7 * fear)), 1)

        emotions = {
            "happy": happy,
            "neutral": neutral,
            "sad": sad,
            "angry": angry,
            "bravery": bravery,
        }
        dominant_raw = max(["happy", "neutral", "sad", "angry"], key=lambda k: emotions[k])
        if neutral > 50:
            dominant_raw = "neutral"

        return {
            "emotions": emotions,
            "dominant": dominant_raw.title(),
            "raw_dominant": dominant_raw,
            "is_brave": bravery >= BRAVERY_THRESHOLD,
            "face_box": (x1, y1, x2 - x1, y2 - y1),
        }

    def _detect_face(self, frame: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)
        for cascade in [self.face_cascade, self.face_cascade_alt]:
            faces = cascade.detectMultiScale(
                gray,
                scaleFactor=1.05,
                minNeighbors=4,
                minSize=(50, 50),
                flags=cv2.CASCADE_SCALE_IMAGE,
            )
            if len(faces) > 0:
                return tuple(max(faces, key=lambda f: f[2] * f[3]))
        return None


_local_detector: Optional[EmotionRecognitionLocal] = None


def get_local_emotion_detector() -> EmotionRecognitionLocal:
    global _local_detector
    if _local_detector is None:
        _local_detector = EmotionRecognitionLocal()
    return _local_detector
