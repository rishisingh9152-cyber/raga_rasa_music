#!/usr/bin/env python3
"""Display updated emotion-to-rasa mapping"""

from app.services.recommendation import EMOTION_TO_RASA

print("Updated Emotion-to-Rasa Mapping for Music Therapy")
print("=" * 60)
print()

for emotion, ragas in EMOTION_TO_RASA.items():
    if isinstance(ragas, list):
        rasa_str = ', '.join(ragas)
    else:
        rasa_str = ragas
    print(f"  {emotion:15} -> {rasa_str}")

print()
print("=" * 60)
print("\nTherapeutic Rationale:")
print("  - Happy/Surprised    : Shringar (romantic, joyful)")
print("  - Sad                : Shaant + Shringar (calming + uplifting)")
print("  - Angry              : Shaant (peaceful, pacifying)")
print("  - Fearful/Disgusted  : Veer (heroic, strengthening)")
print("  - Neutral            : Shaant (peaceful, meditative)")
