#!/usr/bin/env python
"""Test Vonage Auth with API credentials from .env"""

from vonage import Auth, Vonage
from decouple import config

VONAGE_API_KEY = config('VONAGE_API_KEY', default='')
VONAGE_API_SECRET = config('VONAGE_API_SECRET', default='')

print(f"Testing Vonage Auth:")
print(f"  API_KEY: {VONAGE_API_KEY}")
print(f"  API_SECRET: {VONAGE_API_SECRET}")
print()

try:
    print("Attempting Auth initialization...")
    auth = Auth(api_key=VONAGE_API_KEY, api_secret=VONAGE_API_SECRET)
    print("✅ Auth object created successfully")
    
    print("Attempting Vonage client initialization...")
    client = Vonage(auth)
    print("✅ Vonage client initialized successfully!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print(f"   Type: {type(e).__name__}")
    import traceback
    traceback.print_exc()
