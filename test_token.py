#!/usr/bin/env python3
"""Test script to decode JWT token and check its validity"""
import sys
from jose import jwt, JWTError

if len(sys.argv) < 2:
    print("Usage: python test_token.py <token>")
    sys.exit(1)

token = sys.argv[1]
secret_key = "your-jwt-secret-key-change-in-production"  # From .env
algorithm = "HS256"

try:
    payload = jwt.decode(token, secret_key, algorithms=[algorithm])
    print("Token decoded successfully!")
    print(f"Payload: {payload}")
    print(f"\nChecks:")
    print(f"  - Type: {payload.get('type')}")
    print(f"  - User ID (sub): {payload.get('sub')}")
    print(f"  - Is Admin: {payload.get('is_admin')}")
    print(f"  - Expiration: {payload.get('exp')}")

    from datetime import datetime
    exp_timestamp = payload.get('exp')
    if exp_timestamp:
        exp_datetime = datetime.fromtimestamp(exp_timestamp)
        print(f"  - Expires at: {exp_datetime}")
        print(f"  - Is expired: {datetime.utcnow() > exp_datetime}")
except JWTError as e:
    print(f"Token decode failed: {e}")
    sys.exit(1)
