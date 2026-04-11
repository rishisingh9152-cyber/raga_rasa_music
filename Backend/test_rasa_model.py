#!/usr/bin/env python3
"""Test rasa model loading and classification"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.rasa_model import get_rasa_model, is_rasa_model_available

def main():
    print("\n=== Testing Rasa Model Loading ===\n")
    
    # Check if model is available
    print("Loading rasa model...")
    model = get_rasa_model()
    
    if is_rasa_model_available():
        print("✅ Rasa model loaded successfully!")
        print(f"Model type: {model.model_type}")
        print(f"Model path: {model.model if hasattr(model, 'model_path') else 'Loaded'}")
    else:
        print("⚠️  Rasa model not loaded, will use fallback mapping")
    
    # Test emotion to rasa mapping
    test_emotions = ["Happy", "Sad", "Angry", "Neutral", "Fearful", "Surprised", "Disgusted"]
    
    print("\n=== Testing Emotion to Rasa Mapping ===\n")
    print(f"{'Emotion':<15} | {'Rasa':<10} | {'Confidence':<12} | {'Method':<15}")
    print("-" * 60)
    
    for emotion in test_emotions:
        result = model.predict_rasa(emotion)
        method = result.get("method", "model")
        print(f"{emotion:<15} | {result['rasa']:<10} | {result['confidence']:<12.2%} | {method:<15}")
    
    print("\n✅ Rasa model testing complete!")

if __name__ == "__main__":
    main()
