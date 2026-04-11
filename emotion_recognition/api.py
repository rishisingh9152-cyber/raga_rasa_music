
import cv2, base64, numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
from emotion_detector import EmotionDetector

app = Flask(__name__)
CORS(app)
detector = EmotionDetector()

@app.route("/health")
def health():
    return jsonify({"status": "ok", "model": "HSEmotion enet_b0_8_best_afew"})

@app.route("/detect", methods=["POST"])
def detect():
    data = request.get_json(force=True)
    if not data or "image" not in data:
        return jsonify({"error": "Send JSON with 'image' key (base64 JPEG)"}), 400
    try:
        frame = cv2.imdecode(np.frombuffer(base64.b64decode(data["image"]), np.uint8), cv2.IMREAD_COLOR)
        if frame is None:
            raise ValueError("Could not decode image")
    except Exception as e:
        return jsonify({"error": str(e)}), 422

    result = detector.detect_from_frame(frame)
    result.pop("face_box", None)
    return jsonify(result)

if __name__ == "__main__":
    print("\n[API] http://localhost:5000\n")
    app.run(host="0.0.0.0", port=5000, debug=False)
