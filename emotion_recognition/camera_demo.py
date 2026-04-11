"""
camera_demo.py
--------------
Live webcam emotion detection. Clean layout, no overlapping text.
Press Q to quit, S to save snapshot.
"""

import cv2
import time
import os
import numpy as np
from collections import deque
from emotion_detector import EmotionDetector

COLOURS = {
    "happy":   (0,  200, 255),
    "sad":     (200, 70,  20),
    "angry":   (20,  20, 220),
    "bravery": (20, 200,  60),
}
ORDER = ["happy", "sad", "angry", "bravery"]
SMOOTH_N = 6
_history = {k: deque([0.0] * SMOOTH_N, maxlen=SMOOTH_N) for k in ORDER}


def smooth(emotions):
    for k in ORDER:
        _history[k].append(emotions.get(k, 0.0))
    return {k: round(sum(_history[k]) / len(_history[k]), 1) for k in ORDER}


def draw_ui(frame, result, emotions, fps):
    h_f, w_f = frame.shape[:2]

    # ── 1. Emotion bar panel (top-left) ───────────────────────────────
    panel_x, panel_y = 10, 10
    bar_w, bar_h, row_gap = 155, 20, 32
    label_offset = bar_w + 10
    panel_w = bar_w + 125
    panel_h = len(ORDER) * row_gap + 16

    ov = frame.copy()
    cv2.rectangle(ov, (panel_x - 6, panel_y - 6),
                  (panel_x + panel_w, panel_y + panel_h), (10, 10, 10), -1)
    cv2.addWeighted(ov, 0.7, frame, 0.3, 0, frame)

    for i, key in enumerate(ORDER):
        score = emotions.get(key, 0.0)
        y = panel_y + 10 + i * row_gap
        col = COLOURS[key]

        # Track
        cv2.rectangle(frame, (panel_x, y), (panel_x + bar_w, y + bar_h), (55, 55, 55), -1)
        # Fill
        fill = int(bar_w * min(score, 100) / 100)
        if fill > 0:
            cv2.rectangle(frame, (panel_x, y), (panel_x + fill, y + bar_h), col, -1)
        # Text
        cv2.putText(frame, f"{key.capitalize():<8} {score:5.1f}%",
                    (panel_x + label_offset, y + 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.54, (235, 235, 235), 1, cv2.LINE_AA)

    # ── 2. Face box (no text on top of bars) ──────────────────────────
    box = result.get("face_box")
    raw = result.get("raw_dominant", "happy")
    col = COLOURS.get(raw, (100, 255, 100))

    if box:
        x, y, w, h = box
        cv2.rectangle(frame, (x, y), (x + w, y + h), col, 2, cv2.LINE_AA)

        dominant = result.get("dominant", "")
        # Put label BELOW the face box — avoids top overlap
        label_y = min(y + h + 28, h_f - 10)
        cv2.putText(frame, dominant, (x + 2, label_y + 1),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.85, (0, 0, 0), 3, cv2.LINE_AA)
        cv2.putText(frame, dominant, (x, label_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.85, col, 2, cv2.LINE_AA)

    # ── 3. Brave badge (top-right) ────────────────────────────────────
    is_brave = result.get("is_brave")
    if is_brave is not None:
        bval  = emotions.get("bravery", 0.0)
        badge = "BRAVE" if is_brave else "FEARFUL"
        bcol  = (20, 220, 60) if is_brave else (30, 30, 210)
        txt   = f"{badge}  {bval:.0f}%"
        (tw, th), _ = cv2.getTextSize(txt, cv2.FONT_HERSHEY_SIMPLEX, 0.72, 2)
        bx, by = w_f - tw - 18, 34
        cv2.rectangle(frame, (bx - 8, by - th - 7), (bx + tw + 8, by + 7), (10, 10, 10), -1)
        cv2.rectangle(frame, (bx - 8, by - th - 7), (bx + tw + 8, by + 7), bcol, 1)
        cv2.putText(frame, txt, (bx, by), cv2.FONT_HERSHEY_SIMPLEX, 0.72, bcol, 2, cv2.LINE_AA)

    # ── 4. FPS (bottom-right) ─────────────────────────────────────────
    cv2.putText(frame, f"FPS {fps:.1f}", (w_f - 85, h_f - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 255, 100), 1, cv2.LINE_AA)


def run(camera_index=0):
    print("\n" + "=" * 50)
    print("   Emotion Detector  —  Capture Mode")
    print("=" * 50)

    detector = EmotionDetector()

    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print("[Error] Camera not found.")
        return

    print("\nPress C = Capture | Q = Quit\n")

    captured_result = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        display = frame.copy()

        # Show result if already captured
        if captured_result:
            emotions = captured_result["emotions"]
            dominant = captured_result["dominant"]

            cv2.putText(display, f"Result: {dominant}",
                        (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1, (0, 255, 0), 2)

            y = 80
            for k, v in emotions.items():
                cv2.putText(display, f"{k}: {v:.1f}%",
                            (20, y),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.6, (255, 255, 255), 1)
                y += 25

        cv2.imshow("Emotion Capture", display)

        key = cv2.waitKey(1) & 0xFF

        # 🔥 Capture image
        if key == ord("c"):
            print("[Captured] Processing emotion...")

            captured_result = detector.detect_from_frame(frame)

        elif key == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    run(camera_index=0)
