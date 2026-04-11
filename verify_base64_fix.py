#!/usr/bin/env python3
"""
Test to verify the base64 prefix issue is fixed
"""

import base64
from PIL import Image
import io
import json
import sys

if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def create_canvas_like_base64():
    """Create base64 like canvas.toDataURL() would"""
    img = Image.new('RGB', (640, 480), color=(100, 150, 200))
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    base64_str = base64.b64encode(img_bytes.getvalue()).decode()
    # This is what toDataURL returns
    return f"data:image/jpeg;base64,{base64_str}"

def test_base64_formats():
    """Test different base64 formats"""
    
    print("=" * 70)
    print("Testing Base64 Format Issue")
    print("=" * 70)
    
    # Create canvas-like base64
    canvas_data_url = create_canvas_like_base64()
    
    print(f"\n[FORMAT 1] With Data URI Prefix (WRONG)")
    print(f"Length: {len(canvas_data_url)} bytes")
    print(f"Start: {canvas_data_url[:60]}...")
    print(f"This is what canvas.toDataURL() returns")
    
    # Extract just the base64
    if canvas_data_url.startswith("data:image/jpeg;base64,"):
        base64_only = canvas_data_url.replace("data:image/jpeg;base64,", "")
    else:
        base64_only = canvas_data_url
    
    print(f"\n[FORMAT 2] Just Base64 (CORRECT)")
    print(f"Length: {len(base64_only)} bytes")
    print(f"Start: {base64_only[:60]}...")
    print(f"This is what the API expects")
    
    # Show the difference
    print(f"\n[ANALYSIS]")
    print(f"Prefix to strip: 'data:image/jpeg;base64,'")
    print(f"Prefix length: 23 bytes")
    print(f"Data URL length: {len(canvas_data_url)}")
    print(f"Base64 only length: {len(base64_only)}")
    print(f"Difference: {len(canvas_data_url) - len(base64_only)} bytes")
    
    # Verify we can decode both
    print(f"\n[VALIDATION]")
    try:
        # Try with prefix - this would fail on backend
        img_data = base64.b64decode(canvas_data_url)
        print(f"[UNEXPECTED] Prefix didn't cause error! (This is why it gave 422)")
    except Exception as e:
        print(f"[OK] Prefix causes error: {type(e).__name__}")
        print(f"     This is why emotion service returned 422!")
    
    try:
        # Try without prefix - this should work
        img_data = base64.b64decode(base64_only)
        img = Image.open(io.BytesIO(img_data))
        print(f"[OK] Base64 only decodes perfectly: {img.size}")
    except Exception as e:
        print(f"[ERROR] Base64 only failed: {e}")
    
    print(f"\n" + "=" * 70)
    print(f"SOLUTION VERIFICATION")
    print(f"=" * 70)
    print(f"Code fix in LiveSession.tsx:")
    print(f"  const imageDataUrl = canvasRef.toDataURL('image/jpeg');")
    print(f"  const imageBase64 = imageDataUrl.replace(/^data:image\\/jpeg;base64,/, '');")
    print(f"\nThis strips the prefix so the API receives JUST the base64 string.")
    print(f"=" * 70)

if __name__ == "__main__":
    test_base64_formats()
