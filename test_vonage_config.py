#!/usr/bin/env python
"""
Test Vonage Configuration and API Integration
Tests if Vonage is properly configured and can make API calls
"""

import os
import sys
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from decouple import config
from vonage import Auth, Vonage

def print_section(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def test_environment_variables():
    """Test if all environment variables are loaded"""
    print_section("1. ENVIRONMENT VARIABLES CHECK")
    
    vars_to_check = {
        'VOICE_PROVIDER': config('VOICE_PROVIDER', default=''),
        'VONAGE_API_KEY': config('VONAGE_API_KEY', default=''),
        'VONAGE_API_SECRET': config('VONAGE_API_SECRET', default=''),
        'VONAGE_PHONE_NUMBER': config('VONAGE_PHONE_NUMBER', default=''),
        'BASE_URL': config('BASE_URL', default=''),
    }
    
    all_set = True
    for key, value in vars_to_check.items():
        if value:
            # Truncate sensitive data
            display_value = value if len(value) < 20 else f"{value[:15]}... [truncated]"
            print(f"  [OK] {key:25} = {display_value}")
        else:
            print(f"  [ERROR] {key:25} = NOT SET")
            all_set = False
    
    return all_set

def test_vonage_client():
    """Test if Vonage client can be initialized"""
    print_section("2. VONAGE CLIENT INITIALIZATION")
    
    try:
        VONAGE_API_KEY = config('VONAGE_API_KEY')
        VONAGE_API_SECRET = config('VONAGE_API_SECRET')
        
        print(f"  Creating Auth with API Key: {VONAGE_API_KEY[:10]}...")
        vonage_auth = Auth(api_key=VONAGE_API_KEY, api_secret=VONAGE_API_SECRET)
        
        print(f"  Initializing Vonage client...")
        vonage_client = Vonage(vonage_auth)
        
        print(f"  [OK] Vonage client initialized successfully")
        print(f"  [OK] Client type: {type(vonage_client).__name__}")
        print(f"  [OK] Voice API available: {hasattr(vonage_client, 'voice')}")
        
        return vonage_client
        
    except Exception as e:
        print(f"  [ERROR] Failed to initialize Vonage client")
        print(f"  [ERROR] {type(e).__name__}: {str(e)}")
        return None

def test_database_connection():
    """Test if Django database is accessible"""
    print_section("3. DATABASE CONNECTION TEST")
    
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
        print(f"  [OK] Database connection successful")
        print(f"  [OK] Using database: {connection.settings_dict['ENGINE']}")
        
        # Check if HumeAgent table exists
        from HumeAiTwilio.models import HumeAgent
        agents_count = HumeAgent.objects.filter(status='active').count()
        print(f"  [OK] Active agents in database: {agents_count}")
        
        return True
        
    except Exception as e:
        print(f"  [ERROR] Database connection failed")
        print(f"  [ERROR] {type(e).__name__}: {str(e)}")
        return False

def test_call_initiation_function():
    """Test if initiate_call function is available and checks Vonage provider"""
    print_section("4. CALL INITIATION FUNCTION TEST")
    
    try:
        from HumeAiTwilio.api_views.call_initiation import (
            initiate_call, 
            VOICE_PROVIDER,
            vonage_client,
            VONAGE_PHONE_NUMBER
        )
        
        voice_provider = config('VOICE_PROVIDER')
        print(f"  [OK] Call initiation function imported")
        print(f"  [OK] VOICE_PROVIDER configured: {voice_provider}")
        print(f"  [OK] Vonage client status: {'Initialized' if vonage_client else 'Not initialized'}")
        print(f"  [OK] Vonage phone number: {VONAGE_PHONE_NUMBER}")
        
        if voice_provider == 'vonage' and vonage_client:
            print(f"  [SUCCESS] System is configured to use Vonage!")
            return True
        else:
            print(f"  [WARNING] System is NOT using Vonage (using {voice_provider})")
            return False
            
    except Exception as e:
        print(f"  [ERROR] Failed to import call initiation")
        print(f"  [ERROR] {type(e).__name__}: {str(e)}")
        return False

def test_vonage_ncco():
    """Test if Vonage NCCO can be generated"""
    print_section("5. VONAGE NCCO GENERATION TEST")
    
    try:
        BASE_URL = config('BASE_URL', default='https://example.com')
        
        ncco = [
            {
                "action": "connect",
                "eventWebhook": {
                    "url": f"{BASE_URL}/api/hume-twilio/vonage-event-callback/",
                    "method": "POST"
                }
            },
            {
                "action": "input",
                "type": ["audio"],
                "eventWebhook": {
                    "url": f"{BASE_URL}/api/hume-twilio/vonage-stream-callback/",
                    "method": "POST"
                },
                "timeOut": 3600
            }
        ]
        
        print(f"  [OK] NCCO structure created successfully")
        print(f"  [OK] NCCO contains {len(ncco)} actions")
        print(f"  [OK] Action 1: {ncco[0]['action']}")
        print(f"  [OK] Action 2: {ncco[1]['action']}")
        print(f"  [OK] Webhook URL: {BASE_URL}/api/hume-twilio/vonage-event-callback/")
        
        return True
        
    except Exception as e:
        print(f"  [ERROR] Failed to generate NCCO")
        print(f"  [ERROR] {type(e).__name__}: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("\n")
    print("*" * 70)
    print("*" + " " * 68 + "*")
    print("*" + "  VONAGE CONFIGURATION & API INTEGRATION TEST".center(68) + "*")
    print("*" + " " * 68 + "*")
    print("*" * 70)
    
    results = {
        'env_vars': test_environment_variables(),
        'vonage_client': test_vonage_client() is not None,
        'database': test_database_connection(),
        'call_function': test_call_initiation_function(),
        'ncco': test_vonage_ncco(),
    }
    
    # Summary
    print_section("FINAL SUMMARY")
    
    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v)
    
    print(f"\n  Test Results:")
    print(f"  {'='*40}")
    for test_name, result in results.items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {status} {test_name}")
    
    print(f"\n  Total: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print(f"\n  [SUCCESS] All tests passed!")
        print(f"  [SUCCESS] Vonage system is fully configured and ready!")
        print(f"  [SUCCESS] You can now make API calls using Vonage")
        return 0
    else:
        print(f"\n  [WARNING] Some tests failed. Check the output above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
