import os
import cv2
import numpy as np
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import matplotlib.pyplot as plt

from emotion_detector import EmotionDetector

# =========================
# CONFIG
# =========================
DATASET_PATH = "dataset/test"  
# structure:
# dataset/test/happy/*.jpg
# dataset/test/sad/*.jpg
# dataset/test/angry/*.jpg
# dataset/test/neutral/*.jpg

CLASSES = ["happy", "neutral", "sad", "angry"]

# =========================
# INIT MODEL
# =========================
detector = EmotionDetector()

y_true = []
y_pred = []

# =========================
# LOOP DATASET
# =========================
for label in CLASSES:
    folder = os.path.join(DATASET_PATH, label)

    for img_name in os.listdir(folder):
        img_path = os.path.join(folder, img_name)

        frame = cv2.imread(img_path)
        if frame is None:
            continue

        result = detector.detect_from_frame(frame)

        pred = result["raw_dominant"]

        # skip no-face cases
        if pred is None or pred == "No Face Detected":
            continue

        y_true.append(label)
        y_pred.append(pred)

# =========================
# CONFUSION MATRIX
# =========================
cm = confusion_matrix(y_true, y_pred, labels=CLASSES)

print("\nConfusion Matrix:\n", cm)

# =========================
# PLOT
# =========================
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=CLASSES)
disp.plot(cmap="Blues")
plt.title("Emotion Detection Confusion Matrix")
plt.show()