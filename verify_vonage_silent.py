#!/usr/bin/env python
"""
Silent Vonage Verification - No Output
Just returns exit code
"""

import os
import sys
from decouple import config

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

try:
    from vonage import Auth, Vonage
    
    # Load config
    api_key = config('VONAGE_API_KEY')
    api_secret = config('VONAGE_API_SECRET')
    phone = config('VONAGE_PHONE_NUMBER')
    provider = config('VOICE_PROVIDER')
    
    # Test 1: Check provider
    if provider != 'vonage':
        sys.exit(1)
    
    # Test 2: Init client
    vonage_auth = Auth(api_key=api_key, api_secret=api_secret)
    vonage_client = Vonage(vonage_auth)
    
    # Test 3: Check voice API
    if not hasattr(vonage_client, 'voice'):
        sys.exit(1)
    
    # Test 4: Check create_call method
    if not hasattr(vonage_client.voice, 'create_call'):
        sys.exit(1)
    
    # Test 5: Check database
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
    
    # All tests passed
    sys.exit(0)
    
except Exception as e:
    sys.exit(1)
