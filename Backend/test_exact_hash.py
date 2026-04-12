#!/usr/bin/env python
"""Test with the exact password hash from database"""

import bcrypt

# The exact hash from the database
hashed_password = "$2b$12$geMzTThT17BkD0VzZmErI.ndKJofiNHie/gpikMC8BZOUoMMntq7S"
plain_password = "rishisingh"

print("[*] Testing exact password from database...")
print(f"    Hash: {hashed_password}")
print(f"    Password: {plain_password}")
print()

try:
    result = bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    print(f"[RESULT] bcrypt.checkpw: {result}")
    
    if result:
        print("[OK] Password verification SUCCESS!")
    else:
        print("[ERROR] Password verification FAILED!")
except Exception as e:
    print(f"[ERROR] Exception: {e}")
    import traceback
    traceback.print_exc()
